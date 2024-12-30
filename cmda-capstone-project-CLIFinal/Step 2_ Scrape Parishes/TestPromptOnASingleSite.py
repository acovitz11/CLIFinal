# Single site scraping version of ScrapeGraphMultiAtlantaTest2.py for testing purposes bbut without redundant displays of data
from scrapegraphai.graphs import SmartScraperGraph, SmartScraperMultiGraph
from dotenv import main
import os
import json

# Load environment variables and set up API key
main.load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

graph_config = {
    "llm": {
        "api_key": api_key,
        "model": "openai/gpt-4o-mini",  # Use specified model name
    }
}

parish_link = "https://www.hsccatl.com"

# Step 1: Retrieve sublinks for this parish
sublink_prompt = (
    f"List all relevant links from {parish_link} that might contain information about mass times, sacraments, confession, reconciliation, adoration, and contact details. "
    "Do not retrieve or collect any detailed information like mass times, sacrament schedules, confession details, reconciliation details, adoration details, or contact details at this stage."
)
sublink_graph = SmartScraperGraph(
    prompt=sublink_prompt,
    source=parish_link,
    config=graph_config
)
sublink_result = sublink_graph.run()

print("Keys in directory_result:", sublink_result.keys())  # Debugging to check available keys
# Extract sublinks
try:
    sublinks = sublink_result.get("relevant_links", [])
    parish_sublinks = {parish_link: sublinks}
    print(f"Retrieved relevant sublinks for {parish_link}: {json.dumps(parish_sublinks, indent=4)}")
except Exception as e:
    print(f"Error retrieving sublinks for {parish_link}: {e}")
    sublinks = []

# Convert relative sublinks to absolute URLs
sublinks = [f"{parish_link.rstrip('/')}{sublink}" for sublink in sublinks]

# Step 2: Scrape detailed information from sublinks
parish_details = []
#Possible alternate prompt
'''
try:
    detail_prompt = (
        "You will be given instructions and specification below on what information to find from what source. Follow these instructions and specifications to collect information about this Parish. "
        "Instuctiion 1) Collect the Parish's: Name, Address, Phone Number, and Email Address. "
        "Instruction 2) From the section containing information on mass times, collect the 'Mass Times' and group them by each day of the week. (If a mass times section isn't found, or if no information about mass times is found in the mass times section, then and only then can you search other sections for information about mass times.) "
        "Instruction 3) From the section containing information on either confession or reconciliation times, collect all the details about 'Confession/Reconciliation Times', such as the day of the week or month when it is held. (If a confession or reconciliation times section isn't found, or if no information about confession or reconciliation times is found in the confession or reconciliation times section, then and only then can you search other sections for information about confession and reconciliation times.) "
        "Instruction 4) From the section containing information on adoration times, collect all the details about the 'Adoration Times', such as the day of the week or month when it is held. (If an adoration times section isn't found, or if no information about adoration times is found in the adoration times section, then and only then can you search other sections for information about adoration times.) "
        "Specification 1) Ensure the data is structured clearly, includes all available information, and formats times as HH:MM AM/PM."
        "Specification 2) If in Instruction 2, Instruction 3, or Instruction 4, you had to search other sections for the relevant information, make sure you are absolutely certain that the information you find is correct and relevant before collecting it. "
    )
    '''
try:
    detail_prompt = (
        "Collect the Parish's Name, Address, Phone, Email, Mass Times (grouped by day), Confession/Reconciliation Times, and Adoration Times. Ensure data is structured clearly and times are in HH:MM AM/PM. If specific sections for Mass, Confession, or Adoration are missing, validate data from other sections before collecting."
    )

    detail_graph = SmartScraperMultiGraph(
        prompt=detail_prompt,
        source=[parish_link] + sublinks,
        config=graph_config
    )

    detail_result = detail_graph.run()
    print(f"Scraped data for {parish_link}: {json.dumps(detail_result, indent=4)}")

    parish_details.append({
        "parish_link": parish_link,
        "details": detail_result
    })
except Exception as e:
    print(f"Error scraping details for {parish_link}: {e}")
    parish_details.append({
        "parish_link": parish_link,
        "details": {}
    })

# Final output
print(f"Final Parish Details: {json.dumps(parish_details, indent=4)}")
