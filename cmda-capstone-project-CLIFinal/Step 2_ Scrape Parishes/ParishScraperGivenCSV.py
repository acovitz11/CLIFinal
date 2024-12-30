from scrapegraphai.graphs import SmartScraperGraph, SmartScraperMultiGraph
from dotenv import main
import os
import json
import json5  # For forgiving JSON parsing
import pandas as pd
import time  # Ensure time is imported for delays

# Load environment variables and set up API key
main.load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

graph_config = {
    "llm": {
        "api_key": api_key,
        "model": "openai/gpt-4o-mini",  # Use specified model name
    }
}

# Step 1: Collect the list of parish websites from the csv file
csv_file = "cleaned_urls.csv"  # Path to the cleaned CSV file
parish_links = pd.read_csv(csv_file)['Website'].tolist()  # Load the 'Website' column as a list

# Select a specific range of websites
start_index = 0  # Starting row index
end_index = len(parish_links)    # Ending row index (exclusive)
sample_of_parish_links = parish_links[start_index:end_index]

# Print the selected range of websites for confirmation
print(f"Selected websites from row {start_index} to {end_index}:")
print(sample_of_parish_links)

# Step 2: Retrieve sublinks for each parish in batches
batch_size = 5  # Number of parishes to process per batch
batches = [sample_of_parish_links[i:i + batch_size] for i in range(0, len(sample_of_parish_links), batch_size)]

parish_sublinks = {}

for batch_index, batch in enumerate(batches):
    print(f"Processing batch {batch_index + 1}/{len(batches)}")
    for parish_link in batch:
        try:
            sublink_prompt = (
                f"List all relevant links from {parish_link} that might contain information about mass times, sacraments, confession, reconciliation, adoration, and contact details. "
                "Do not say the title or description of the links. Do not retrieve or collect any detailed information like mass times, sacrament schedules, confession details, reconciliation details, adoration details, or contact details at this stage."
            )
            sublink_graph = SmartScraperGraph(
                prompt=sublink_prompt,
                source=parish_link,
                config=graph_config
            )
            
            # Run the graph to retrieve sublinks for this parish
            sublink_result = sublink_graph.run()
            print(f"Keys in sublink_result for {parish_link}: {sublink_result.keys()}")  # Debugging
            
            first_key = list(sublink_result.keys())[0]  # Get the first key dynamically
            sublinks = sublink_result.get(first_key, [])
            parish_sublinks[parish_link] = sublinks
        except Exception as e:
            print(f"Error processing sublinks for {parish_link}: {e}")
            parish_sublinks[parish_link] = []
    time.sleep(2)  # Add a 2-second delay between batches

print(f"Retrieved sublinks for {len(parish_sublinks)} parishes.")

# Step 3: Scrape detailed information from sublinks
parish_details = []

for parish_link, sublinks in parish_sublinks.items():
    try:
        # Ensure all sublinks are strings before appending to `source`
        links = [parish_link] + [
            sublink['url'] if isinstance(sublink, dict) and 'url' in sublink else str(sublink)
            for sublink in (sublinks if isinstance(sublinks, list) else [sublinks])
        ]

        detail_prompt = (
            "Collect the Parish's Name, Address, Phone, Email, Mass Times (grouped by day), Confession/Reconciliation Times, and Adoration Times. Ensure data is structured clearly and times are in HH:MM AM/PM. If specific sections for Mass, Confession, or Adoration are missing, validate data from other sections before collecting."
        )
        
        detail_graph = SmartScraperMultiGraph(
            prompt=detail_prompt,
            source=links,  # Updated `source` includes properly formatted `links`
            config=graph_config
        )
        
        # Debugging: Verify the source URLs
        print(f"List of URLs for {parish_link}: {links}")
        
        # Run the graph to get parish details
        detail_result = detail_graph.run()
        print(f"Keys in detail_result for {parish_link}: {detail_result.keys()}")  # Debugging
        
        # Create a dictionary to store parish details
        parish_data = {}

        # Iterate over all keys dynamically and store the data
        for key, value in detail_result.items():
            try:
                # Attempt to parse the JSON using json5 for more forgiving parsing
                parsed_value = json5.loads(json.dumps(value))  # json.dumps ensures it's treated as a string
                print(f"{key} : {json.dumps(parsed_value, indent=4)}")  # Print parsed data
                parish_data[key] = parsed_value  # Store the parsed data
            except Exception as e:
                # Handle invalid JSON gracefully
                print(f"Invalid JSON for key '{key}' in {parish_link}: {e}")
                # Optionally log or keep the raw data as fallback
                parish_data[key] = value  # Retain the raw value for inspection
                with open("invalid_json_log.txt", "a") as log_file:
                    log_file.write(f"Invalid JSON for {key} in {parish_link}: {value}\n")

        # Append the full parish data to parish_details
        parish_details.append({
            "parish_link": parish_link,
            "details": parish_data
        })

    except Exception as e:
        print(f"Error processing details for {parish_link}: {e}")
        parish_details.append({
            "parish_link": parish_link,
            "details": {}
        })

# Flatten the details for CSV output
flattened_details = []

for parish in parish_details:
    parish_link = parish["parish_link"]
    details = parish["details"]
    
    # Flatten the dictionary into a row format
    if isinstance(details, dict):
        flattened_details.append({
            "parish_link": parish_link,
            **{key: json.dumps(value) for key, value in details.items()}  # Dynamically flatten all details
        })

# Convert to a DataFrame and save to CSV
df = pd.DataFrame(flattened_details)
csv_filename = f"RawScrapedParishData.csv"
df.to_csv(csv_filename, index=False)

print(f"Parish details saved to {csv_filename}")
