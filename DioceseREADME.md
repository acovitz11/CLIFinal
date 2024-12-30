# Diocesan and Parish Web Scraper

## Overview
This First step of the CLI WebScraper project automates the collection of parish information, specifically parish names and website URLs, from diocesan directories across the United States. The scraper is built to handle diverse website structures and dynamic content, ensuring scalability and adaptability. The resulting dataset is exported as a structured CSV file for further analysis and integration into additional tools.

The scraper leverages Playwright for web automation and dynamic content handling, and BeautifulSoup for parsing HTML content. This tool forms the foundation for advanced data collection methods such as AI-driven scraping.

---

## Features
- Multi-Diocesan Support: Scrapes data from multiple diocesan websites, including but not limited to:
  - Archdiocese of Indianapolis
  - Archdiocese of Atlanta
  - Archdiocese of Boston
  - Archdiocese of St. Louis
  - Archdiocese of New York
  - Archdiocese of Denver
  - Archdiocese of Seattle
  - ...and many more.
- Dynamic Content Handling: Handles JavaScript-heavy and dynamically loaded content using Playwright.
- Automated Pagination: Efficiently navigates through paginated directories to extract all available data.
- Scalable Architecture: Modular design makes it easy to add support for new diocesan websites.
- Structured Output: Data is exported as a CSV file with two columns: Parish Name and Website URL.

---

## Setup and Prerequisites

### Requirements
- Python 3.8 or later
- Dependencies:
  - `playwright`
  - `beautifulsoup4`
  - `re`
  - `csv`

### Installation
1. Clone or download the repository.
2. Run the script using the following command:
   ```bash
   pip install playwright beautifulsoup4
   playwright install
3. Ensure you have a stable internet connection as the scraper interacts with live web pages.

### Usage
1. Save the script as script_name.py
2. Run the script using the following command:
   python parish_scraper.py

### Output
1. The scraper generates a CSV file named parish_results.csv in the working directory.
2. The CSV contains the following columns:
    Parish Name: Name of the parish.
    Website URL: URL of the parish's website or "Not Found" if no website is listed.

## Key Functionalities

### 1. Handling Dynamic Content
- JavaScript Rendering: Playwright ensures JavaScript-heavy websites are fully rendered before scraping.
- Pagination and AJAX: Dynamic pagination and AJAX-based content are handled seamlessly, ensuring no data is missed.

### 2. Data Structuring
- Global Data Storage: Parish data is stored in a global list during the scraping process.
- CSV Export: At the end of execution, all data is exported into a clean, structured CSV file for easy use.

---

## Challenges and Solutions

### Inconsistent HTML Structures
- Challenge: Each diocese has its own unique HTML structure, requiring customized scraping logic.
- Solution: Modular functions were designed to handle these variations efficiently.

### Dynamic Content
- Challenge: Many diocesan websites use JavaScript for content rendering, which traditional HTML parsers cannot handle.
- Solution: This was addressed using Playwright's headless browser automation to fully render pages before scraping.

### Execution Time
- Challenge: The scraper processes large datasets, which may take time.
- Solution: Future enhancements will focus on multi-threading or asynchronous scraping to improve performance.

---

## Adding Support for New Dioceses
1. Write a New Function: Create a new scraping function based on the structure of the target diocesan website.
2. Add the Function to the Main Workflow: Add the new function call to the `scrape_parishes()` method.
3. Test and Validate: Run the script and validate the output in the `parish_results.csv` file.

---

## Future Enhancements
1. Error Handling: Implement error handling to retry failed requests automatically.
2. Multi-Threading: Add support for multi-threading to reduce execution time and improve efficiency.
