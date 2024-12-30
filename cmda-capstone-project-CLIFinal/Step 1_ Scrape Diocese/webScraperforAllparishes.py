import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import csv

parish_results = []  

def format_parish_url(base_url, parish_name):
    # Format the parish name into a slug for the URL
    slug = parish_name.lower().replace(" ", "-")
    return f"{base_url}{slug}/"

def scrape_indianapolis_parishes(page, listing_url):
    page.goto(listing_url)
    page.wait_for_timeout(2000)
    listing_content = page.content()
    soup = BeautifulSoup(listing_content, 'html.parser')

    parish_links = []
    for link in soup.select('ul li a'):
        parish_name = link.text.strip()
        parish_url = "https://www.archindy.org/parishes/" + link['href']
        parish_links.append((parish_name, parish_url))

    # Define the last valid parish name to stop further scraping
    stop_parish_name = "St. Vincent de Paul, Shelby County"

    for parish_name, parish_url in parish_links:
        # Stop if we've reached the last valid parish name
        if parish_name == stop_parish_name:
            page.goto(parish_url)
            page.wait_for_timeout(2000)

            parish_content = page.content()
            parish_soup = BeautifulSoup(parish_content, 'html.parser')

            website_link = 'Not Found'
            for li in parish_soup.find_all("li"):
                if "Web site:" in li.get_text():
                    a_tags = li.find_all("a", href=True)
                    for a_tag in a_tags:
                        if a_tag["href"].startswith("http://") or a_tag["href"].startswith("https://"):
                            website_link = a_tag["href"]
                            break
                    break

            parish_results.append([parish_name, website_link])
            break  # Stop after adding the last valid parish entry

        # Continue scraping for other parishes
        page.goto(parish_url)
        page.wait_for_timeout(2000)

        parish_content = page.content()
        parish_soup = BeautifulSoup(parish_content, 'html.parser')

        website_link = 'Not Found'
        for li in parish_soup.find_all("li"):
            if "Web site:" in li.get_text():
                a_tags = li.find_all("a", href=True)
                for a_tag in a_tags:
                    if a_tag["href"].startswith("http://") or a_tag["href"].startswith("https://"):
                        website_link = a_tag["href"]
                        break
                break

        parish_results.append([parish_name, website_link])


def scrape_atlanta_parishes(page, listing_url):
    page.goto(listing_url)
    page.select_option("select[name='table_1_length']", value="-1")
    page.wait_for_timeout(2000)
    page_content = page.content()
    soup = BeautifulSoup(page_content, "html.parser")

    parish_rows = soup.find_all("tr", id=lambda x: x and x.startswith("table_"))
    for row in parish_rows:
        name = row.find('td', class_='column-name').text.strip() if row.find('td', class_='column-name') else 'Not Found'
        website_link = row.find('td', class_='column-web').find('a')['href'] if row.find('td', class_='column-web') and row.find('td', class_='column-web').find('a') else 'Not Found'

        # Append the results to parish_results
        parish_results.append([name, website_link])


def scrape_louisville_parishes(page, listing_url, base_parish_url):
    page.goto(listing_url)
    page.wait_for_timeout(2000)
    content = page.content()
    soup = BeautifulSoup(content, 'html.parser')

    parish_rows = soup.find('tbody', class_='row-hover').find_all('tr')
    parish_urls = []

    for row in parish_rows:
        name_tag = row.find('td', class_='column-1').find('a', href=True)
        if name_tag:
            parish_name = name_tag.text.strip()
            parish_url = format_parish_url(base_parish_url, parish_name)
            parish_urls.append((parish_name, parish_url))

    for parish_name, parish_url in parish_urls:
        page.goto(parish_url)
        page.wait_for_timeout(2000)

        parish_content = page.content()
        parish_soup = BeautifulSoup(parish_content, 'html.parser')

        website_link = "Not Found"
        parish_info = parish_soup.find('h3', string=re.compile(r'Parish Information'))
        if parish_info:
            p_tag = parish_info.find_next('p')
            if p_tag:
                for line in p_tag.stripped_strings:
                    if "Website:" in line:
                        link_tag = p_tag.find('a', href=True, string=re.compile(r'http'))
                        if link_tag:
                            website_link = link_tag['href']
                            break

        # Append the results to parish_results
        parish_results.append([parish_name, website_link])


def scrape_boston_parishes(page, base_url):
    page.goto(base_url)
    page.wait_for_timeout(2000)

    parish_data = []

    while True:
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')

        table = soup.find('table', class_='listing_table')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                name_tag = row.find('a')
                if name_tag:
                    parish_name = name_tag.text.strip()
                    parish_link = base_url.rsplit("/", 1)[0] + "/" + name_tag['href']
                    parish_data.append((parish_name, parish_link))

        next_button = page.locator("a", has_text="Next »")
        if next_button.count() > 0:
            next_button.first.click()
            page.wait_for_timeout(2000)
        else:
            break

    for parish_name, parish_url in parish_data:
        page.goto(parish_url)
        page.wait_for_timeout(2000)

        parish_content = page.content()
        parish_soup = BeautifulSoup(parish_content, 'html.parser')

        website_link = "Not Found"
        nav_menu = parish_soup.find('nav', {'id': 'main-menu'})
        if nav_menu:
            links = nav_menu.find_all('a', href=True)
            for link in links:
                if "Official Parish Web site" in link.text or "official" in link.get('href', '').lower():
                    website_link = link['href']
                    break

        # Append the results to parish_results
        parish_results.append([parish_name, website_link])

def scrape_stlouis_parishes_all_pages(page, base_url):
    page.goto(base_url)
    page.wait_for_timeout(2000)

    while True:
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')

        parish_list = soup.find_all('div', class_='archstl-listing archstl-parish-listing')
        for parish in parish_list:
            name_tag = parish.find('h2', class_='wp-block-heading')
            parish_name = name_tag.text.strip() if name_tag else "Not Found"

            website_tag = parish.find('a', href=True, string="Visit Website")
            website_link = website_tag['href'] if website_tag else "Not Found"

            # Append results to parish_results
            parish_results.append([parish_name, website_link])

        next_button = soup.find('a', class_='wp-block-query-pagination-next')
        if next_button:
            next_page_url = next_button['href']
            full_next_page_url = f"https://www.archstl.org{next_page_url}"
            page.goto(full_next_page_url)
            page.wait_for_timeout(2000)
        else:
            break

def scrape_archny_all_pages(page):
    url = "https://archny.org/parish-finder/"
    page.goto(url)
    page.wait_for_timeout(3000)  # Wait for dynamic content to load

    while True:
        # Extract page content
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Locate parish information on the current page
        parish_entries = soup.find_all('div', class_='fc-item-box')
        for parish in parish_entries:
            # Extract parish name
            name_tag = parish.find('div', class_='fc-item-title')
            parish_name = name_tag.text.strip() if name_tag else 'Not Found'

            # Extract website link
            website_tag = parish.find('a', title="Website")
            website = website_tag['href'] if website_tag else 'Not Found'

            # Append results to parish_results
            parish_results.append([parish_name, website])

        # Check for the "Next" button
        next_button = page.locator("div.location_pagination1 a.next")
        if next_button.count() > 0:
            next_button.click()
            page.wait_for_timeout(3000)
        else:
            break

def scrape_archokc_parishes(page):
    url = "https://archokc.org/parishfinder"
    page.goto(url)
    page.wait_for_timeout(3000)  

    # Extract page content
    content = page.content()
    soup = BeautifulSoup(content, 'html.parser')

    # Locate parish entries
    parish_entries = soup.find_all('li', class_='site')
    for parish in parish_entries:
        # Extract parish name
        name_tag = parish.find('div', class_='name')
        parish_name = name_tag.text.strip() if name_tag else 'Not Found'

        # Extract website link
        link_container = parish.find('div', class_='linkContainer')
        website_tag = link_container.find('a', class_='urlLink') if link_container else None
        website = website_tag['href'] if website_tag else 'Not Found'

        # Append the results to parish_results
        parish_results.append([parish_name, website])

def scrape_archdpdx(page):
    url = "https://www.archdpdx.org/parishfinder"
    page.goto(url)
    
    # Wait for the network to be idle and ensure dynamic content is loaded
    page.wait_for_load_state("networkidle", timeout=15000)

    # Extract page content
    content = page.content()
    soup = BeautifulSoup(content, 'html.parser')

    # Locate parish entries
    parish_entries = soup.find_all('li', class_='site')
    if not parish_entries:
        return

    for parish in parish_entries:
        # Extract parish name
        name_tag = parish.find('div', class_='name')
        parish_name = name_tag.text.strip() if name_tag else 'Not Found'

        # Extract website link
        link_container = parish.find('div', class_='linkContainer')
        website_tag = link_container.find('a', class_='urlLink') if link_container else None
        website = website_tag['href'] if website_tag else 'Not Found'

        # Append the results to parish_results
        parish_results.append([parish_name, website])

def scrape_archphila_parishes(page):
    base_url = "https://archphila.org/parish/"

    while True:
        # Wait for the page content to load
        page.wait_for_load_state("networkidle", timeout=10000)

        # Extract page content
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Locate parish entries that are not closed
        parish_entries = soup.find_all('p', class_=lambda x: x != 'closedparish')

        # Extract names and second-page links of open parishes
        for parish in parish_entries:
            link = parish.find('a', href=True)
            if link and '/parish/' in link['href']:
                parish_name = link.text.strip()
                second_page_url = link['href']

                page.goto(second_page_url)
                page.wait_for_load_state("networkidle", timeout=10000)

                # Extract content from the parish's second page
                second_page_content = page.content()
                second_page_soup = BeautifulSoup(second_page_content, 'html.parser')

                # Find the "Web Site:" section
                website_link = 'Not Found'
                website_div = second_page_soup.find('div', string=lambda x: x and "Web Site:" in x)
                if website_div:
                    website_tag = website_div.find_next('a', href=True)
                    website_link = website_tag['href'] if website_tag else 'Not Found'

                # Append the result to parish_results
                parish_results.append([parish_name, website_link])

        # Find the "Next" button in pagination
        next_button = soup.find('a', class_='next page-numbers')
        if next_button:
            next_page_url = next_button['href']
            page.goto(next_page_url)
        else:
            break

def scrape_archgh_all_pages(page):
    url = "https://www.archgh.org/parishes/parish-search/"
    scraped_parishes = set()  # Track parish names to avoid duplicates
    total_parishes = 62  # Adjust based on the total number of expected parishes

    # Navigate to the parish search page
    page.goto(url)

    while len(scraped_parishes) < total_parishes:
        # Wait for the table rows to be present in the DOM
        page.wait_for_selector('table tr h3.h6 a', timeout=30000)

        # Extract the rendered page content
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Locate parish entries
        parish_rows = soup.select('tr[ng-repeat]')
        if not parish_rows:
            break

        for row in parish_rows:
            # Extract parish name
            name_tag = row.select_one('h3.h6 a')
            website_tag = row.select_one('td a[href^="//"]')

            parish_name = name_tag.text.strip() if name_tag else "Not Found"
            website = "https:" + website_tag['href'] if website_tag else "Not Found"

            # Avoid duplicates
            if parish_name in scraped_parishes:
                continue

            scraped_parishes.add(parish_name)

            # Append results to parish_results
            parish_results.append([parish_name, website])

        # Stop if all expected parishes are scraped
        if len(scraped_parishes) >= total_parishes:
            break

        # Check if the "Next" button is available and visible
        next_button = page.locator('li > a[aria-label="Next"]').first
        if next_button.is_visible():
            next_button.click()
            page.wait_for_load_state("networkidle", timeout=10000)  # Wait for the next page to load
        else:
            break

def scrape_archsa_parishes(page):
    url = "https://archsa.org/parishes/?name_contains=&pastors=&typeOfService=&zip=Select&startTime=Select&endTime=Select&city=Select&serviceDay=Select&language=Select&search=Search"

    # Navigate to the page
    page.goto(url, wait_until="domcontentloaded")  # Skip waiting for all network requests

    # Wait for parish entries to load
    try:
        page.wait_for_selector("div.arch-result", timeout=60000)  # Adjust timeout as needed
    except Exception:
        return

    # Extract the page content
    content = page.content()
    soup = BeautifulSoup(content, 'html.parser')

    # Locate all parish entries
    parish_entries = soup.find_all("div", class_="arch-result")
    if not parish_entries:
        return

    for entry in parish_entries:
        # Extract parish name
        name_tag = entry.find("h3").find("a")
        parish_name = name_tag.text.strip() if name_tag else "Not Found"

        # Extract parish website
        website_tag = entry.find("a", class_="website")
        website_link = website_tag['href'] if website_tag else "Not Found"

        # Append results to parish_results
        parish_results.append([parish_name, website_link])

def scrape_seattle_parishes(page):
    base_url = "https://archseattle.org/finder/?mode=Parish"

    # Navigate to the main parish finder page
    page.goto(base_url, wait_until="domcontentloaded")

    # Wait for parish rows to load
    try:
        page.wait_for_selector("tr.ParishRow", timeout=30000)
    except Exception:
        return

    # Extract the page content
    content = page.content()
    soup = BeautifulSoup(content, 'html.parser')

    # Locate all parish rows
    parish_rows = soup.find_all("tr", class_="ParishRow")
    if not parish_rows:
        return

    for row in parish_rows:
        # Extract parish name and link to the second page
        name_tag = row.find("a")
        parish_name = name_tag.text.strip() if name_tag else "Not Found"
        second_page_link = "https://archseattle.org" + name_tag['href'] if name_tag and name_tag['href'] else "Not Found"

        # Navigate to the second page
        page.goto(second_page_link, wait_until="domcontentloaded")

        # Extract the content of the second page
        second_page_content = page.content()
        second_page_soup = BeautifulSoup(second_page_content, 'html.parser')

        # Locate the parish website link
        website_tag = second_page_soup.find("div", class_="page-header").find("a", href=True)
        parish_website = website_tag['href'] if website_tag else "Not Found"

        # Append results to parish_results
        parish_results.append([parish_name, parish_website])

def scrape_adw_parishes(page):
    base_url = "https://adw.org/parishes-masses/parish-mass-finder/"
    parish_data = []

    # Step 1: Navigate to the main page and click the "List" button
    page.goto(base_url, wait_until="domcontentloaded")

    # Click the "List" button to show the parish list
    list_button = page.locator('a[data-show="listing"]')
    list_button.click()
    page.wait_for_selector("div.parish-listing__school", timeout=15000)

    # Extract parish names and second-page links
    content = page.content()
    soup = BeautifulSoup(content, 'html.parser')
    parish_entries = soup.find_all("div", class_="parish-listing__school")

    if not parish_entries:
        return

    for entry in parish_entries:
        name_tag = entry.find("h4", class_="parish-listing__school-title").find("a")
        parish_name = name_tag.text.strip() if name_tag else "Not Found"
        second_page_link = name_tag["href"] if name_tag else "Not Found"

        parish_data.append({"name": parish_name, "second_page_link": second_page_link})

    # Step 2: Visit each second-page link and extract parish website
    for parish in parish_data:
        second_page_link = parish["second_page_link"]

        if second_page_link == "Not Found":
            parish_results.append([parish["name"], "Not Found"])
            continue

        try:
            page.goto(second_page_link, wait_until="domcontentloaded")
            page.wait_for_selector("div.info-box", timeout=15000)  # Ensure the info-box loads

            second_page_content = page.content()
            second_page_soup = BeautifulSoup(second_page_content, 'html.parser')

            # Find the website link in the second page
            website_tag = second_page_soup.select_one("li i.fas.fa-laptop + a")
            parish_website = website_tag["href"] if website_tag else "Not Found"

            parish_results.append([parish["name"], parish_website])

        except Exception:
            parish_results.append([parish["name"], "Error"])

def scrape_milwaukee_parishes(page):
    base_url = "https://www.archmil.org"
    listing_url = f"{base_url}/Parishes/Alpha-Listing.htm"
    parishes = []

    # Navigate to the main alpha listing page
    page.goto(listing_url, wait_until="domcontentloaded")

    # Wait for the parish links to load
    try:
        page.wait_for_selector("div.attCol1 h4 a", timeout=30000)
    except Exception:
        return

    # Extract the main page content
    content = page.content()
    soup = BeautifulSoup(content, 'html.parser')

    # Locate all parish entries
    parish_entries = soup.select("div.attCol1 h4 a")
    if not parish_entries:
        return

    for entry in parish_entries:
        parish_name = entry.text.strip()
        second_page_link = base_url + entry['href'] if entry['href'] else "Not Found"
        parishes.append({"name": parish_name, "second_page_link": second_page_link})

    # Visit each second-page link to extract the parish website link
    for parish in parishes:
        second_page_link = parish["second_page_link"]
        if second_page_link == "Not Found":
            parish_results.append([parish["name"], "Not Found"])
            continue

        try:
            page.goto(second_page_link, wait_until="domcontentloaded")

            # Wait for the website link to load
            page.wait_for_selector("div.website a", timeout=15000)

            # Extract content from the second page
            second_page_content = page.content()
            second_page_soup = BeautifulSoup(second_page_content, 'html.parser')

            # Locate the website link
            website_tag = second_page_soup.select_one("div.website a[href^='http']")
            parish_website = website_tag['href'] if website_tag else "Not Found"

            parish_results.append([parish["name"], parish_website])

        except Exception:
            parish_results.append([parish["name"], "Error"])

def scrape_hartford_parishes(page):
    # Scraping Archdiocese of Hartford
    url = "https://archdioceseofhartford.org/parish-search-results/?wpv_view_count=5752&wpv-parish-name=0&wpv-church-name=0&wpv-location-city=0&wpv_filter_submit=Submit"

    # Navigate to the Hartford parish page
    page.goto(url, wait_until="domcontentloaded")

    # Wait for parish entries to load
    page.wait_for_timeout(5000)

    # Use Playwright to locate parish entries directly
    parish_elements = page.locator("div.row.full-box")

    if parish_elements.count() == 0:
        return

    for i in range(parish_elements.count()):
        # Extract parish name
        parish_name = parish_elements.nth(i).locator("h1[data-fontsize='26']").text_content().strip()

        # Extract parish website
        contact_info_element = parish_elements.nth(i).locator("div.col-sm-4.mass-box-top")
        website = "Not Found"

        if contact_info_element.count() > 0:
            # Get the full text content of the contact info section
            contact_info_text = contact_info_element.first.text_content()

            # Extract the website text following "Website"
            lines = contact_info_text.split("\n")
            for line in lines:
                if "Website" in line:
                    website = line.replace("Website", "").strip()
                    break

        # Add to the global results
        parish_results.append([parish_name, website])

def scrape_archdiocese_anchorage_juneau(page):
    # Scraping Archdiocese of Anchorage-Juneau
    url = "https://www.aoaj.org/parishfinder"

    # Navigate to the page
    page.goto(url, wait_until="domcontentloaded")

    # Wait for the page to fully load
    page.wait_for_timeout(5000)

    # Click all dropdowns to expand
    dropdowns = page.locator("div.categoryName")
    for i in range(dropdowns.count()):
        dropdowns.nth(i).click()
        page.wait_for_timeout(500)  # Small delay for UI interaction

    # Locate all parish entries
    parish_elements = page.locator("li.site")

    # Loop through all parish entries and extract data
    for i in range(parish_elements.count()):
        parish_name = parish_elements.nth(i).locator("div.name").first.text_content().strip()

        # Extract website link
        link_element = parish_elements.nth(i).locator("a.urlLink")
        website = link_element.get_attribute("href") if link_element.count() > 0 else "Not Found"

        # Add to the global results
        parish_results.append([parish_name, website])




def scrape_denver_parishes(page):
    url = "https://archden.org/parish-locator"
    visited_parishes = set()  # To track already scraped parish names

    # Navigate to the page
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # Click the "Show All" button
    show_all_button = page.locator("a#filterShowAll")
    if show_all_button.count() > 0 and show_all_button.is_enabled():
        show_all_button.click()
        page.wait_for_timeout(5000)  # Wait for all entries to load

    # Locate all parish entries
    parish_entries = page.locator("div.store-locator__infobox")

    # Iterate over all parish entries
    for i in range(parish_entries.count()):
        # Extract parish name
        name_locator = parish_entries.nth(i).locator("div.infobox__row.store-location")
        parish_name = name_locator.text_content().strip() if name_locator.count() > 0 else "Not Found"

        # Skip placeholder or invalid names and check if already visited
        if parish_name.lower() == "placeholder store name" or parish_name in visited_parishes:
            continue

        # Extract parish website
        website_locator = parish_entries.nth(i).locator("div.infobox__row.store-website a")
        website_link = (
            website_locator.get_attribute("href").strip()
            if website_locator.count() > 0
            else "Website Not Found"
        )
        parish_results.append([parish_name, website_link])
        visited_parishes.add(parish_name)

def scrape_newark_parishes(page):
    url = "https://rcan.org/parishes/"

    # Navigate to the page
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)  

    # Locate all parish entries using Playwright selectors
    parish_entries = page.locator("div.info.parish-info")

    # Iterate over each parish entry
    for i in range(parish_entries.count()):
        # Extract parish name
        name_locator = parish_entries.nth(i).locator("div.header div.name h4")
        parish_name = name_locator.text_content().strip() if name_locator.count() > 0 else "Not Found"

        # Extract website URL
        website_locator = parish_entries.nth(i).locator("div.website a.button")
        website_url = website_locator.get_attribute("href") if website_locator.count() > 0 else "Website Not Found"

        # Append the result to the global list
        parish_results.append([parish_name, website_url])
    

def scrape_las_vegas_parishes(page):
    url = "https://lvcatholic.org/parishfinder"
    
    # Navigate to the page
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle", timeout=30000)  # Wait for network activity to idle

    # Wait for parish entries to load
    try:
        page.wait_for_selector("li.site", timeout=30000)  # Increase timeout
    except Exception as e:
        return

    # Locate all parish entries
    parish_entries = page.locator("li.site")
    total_entries = parish_entries.count()

    if total_entries == 0:
        return

    # Iterate over each parish entry
    for i in range(total_entries):
        # Extract parish name
        name_locator = parish_entries.nth(i).locator(":scope > div.name")
        parish_name = name_locator.text_content().strip() if name_locator.count() > 0 else "Name Not Found"

        # Extract website URL
        website_locator = parish_entries.nth(i).locator(":scope a.urlLink")
        website_url = website_locator.get_attribute("href") if website_locator.count() > 0 else "Website Not Found"

        # Append the result to the global list
        parish_results.append([parish_name, website_url])


def save_to_csv():
    filename = "parish_results.csv"
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Parish Name", "Website"])  
        writer.writerows(parish_results)
    print(f"Results saved to {filename}")


def scrape_parishes():
    start_time = time.time()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        # Call all scraper functions
        scrape_newark_parishes(page)  #works 
        scrape_indianapolis_parishes(page, "https://www.archindy.org/parishes/alphalist.html")
        scrape_atlanta_parishes(page, "https://archatl.com/parishes/parish-directory/")
        scrape_louisville_parishes(page, "https://www.archlou.org/parishes/find-a-parish/", "https://www.archlou.org/parishes/")
        scrape_boston_parishes(page, "https://thebostonpilot.com/bcd/ParishSearch.asp")
        scrape_stlouis_parishes_all_pages(page, "https://www.archstl.org/join-us/parish-directory/?cst")
        scrape_archny_all_pages(page)
        scrape_archokc_parishes(page)
        scrape_archdpdx(page)
        scrape_archphila_parishes(page)
        scrape_archgh_all_pages(page)
        scrape_archsa_parishes(page)
        scrape_seattle_parishes(page)
        scrape_adw_parishes(page)
        scrape_milwaukee_parishes(page)
        scrape_hartford_parishes(page)
        scrape_archdiocese_anchorage_juneau(page)
        scrape_denver_parishes(page)
        scrape_las_vegas_parishes(page)  

        browser.close()

    save_to_csv()

    end_time = time.time()
    print(f"\nTotal Execution Time: {end_time - start_time:.2f} seconds")

# Run the combined scraper
scrape_parishes()