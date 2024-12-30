import csv
import pandas as pd
import re
import json

# Define input and output filenames dynamically
n = "3"

# Input and output CSV files
input_csv = 'JSON-like_Final_File1.csv'
parish_table_csv = f'ParishTable{n}.csv'
mass_times_table_csv = f'MassTimesTable{n}.csv'
sacraments_table_csv = f'SacramentsTable{n}.csv'
adoration_table_csv = f'AdorationTable{n}.csv'
confession_table_csv = f'ConfessionTable{n}.csv'
archdiocese_table_csv = f'ArchdioceseTable{n}.csv'
reconciliation_output_csv = "ReconciliationTimesTableByDay.csv"
mass_times_output_csv = "MassTimesTableByDay.csv"

# Initialize data structures
parish_data = []
mass_times_data = []
sacraments_data = []
adoration_data = []
confession_data = []
archdiocese_data = [{"pkArchdiocese": 0, "Archdiocese": "Atlanta"}]
reconciliation_rows = []
mass_times_rows = []

# Helper function to normalize the JSON-like string
def normalize_json_like_string(data):
    return data.replace('""', '"').replace('" ,', '",').replace(', "', ',"')

# Helper function to extract key-value pairs, including nested dictionaries and lists
def extract_nested_value(data, key):
    normalized_data = normalize_json_like_string(data)
    match = re.search(rf'"{key}"\s*:\s*({{.*?}}|\[.*?\]|".*?"|[^,]*)(,|}})', normalized_data)
    if not match:
        return "NA"
    
    value = match.group(1).strip()
    if value.startswith("{") or value.startswith("["):
        # Match the entire nested structure
        brace_count = 0
        bracket_count = 0
        start_index = normalized_data.find(value)
        for i, char in enumerate(normalized_data[start_index:], start=start_index):
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
            elif char == "[":
                bracket_count += 1
            elif char == "]":
                bracket_count -= 1
            if brace_count == 0 and bracket_count == 0:
                return normalized_data[start_index:i + 1]
    return value.strip('"')

# Helper function to process Reconciliation_Times
def process_reconciliation_times(parish_id, reconciliation_times):
    # Initialize the row with ParishID and empty slots for each day
    columns = ["ParishID", "Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    row = {day: "NA" for day in columns}
    row["ParishID"] = parish_id

    # Handle cases where reconciliation_times is not a valid JSON dictionary
    if not reconciliation_times.startswith("{"):
        row["Saturday"] = reconciliation_times
        return row

    try:
        # Attempt to load as JSON
        reconciliation_data = json.loads(reconciliation_times)
    except json.JSONDecodeError:
        row["Saturday"] = reconciliation_times
        return row

    # If reconciliation_data is a dictionary, process normally
    if isinstance(reconciliation_data, dict):
        for key, value in reconciliation_data.items():
            if key in columns:
                if isinstance(value, list):
                    # Convert lists containing dictionaries or non-string values to strings
                    row[key] = ", ".join(
                        json.dumps(v) if isinstance(v, dict) else str(v) for v in value
                    )
                else:
                    # Handle string or simple values
                    row[key] = value
            elif key == "Weekdays":
                # Copy the value to Monday through Friday
                for weekday in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                    row[weekday] = value

    return row

# Helper function to process Mass_Times
def process_mass_times(parish_id, mass_times):
    # Initialize the row with ParishID and empty slots for each day
    columns = ["ParishID", "Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    row = {day: "NA" for day in columns}
    row["ParishID"] = parish_id

    # Parse the Mass_Times JSON string
    try:
        mass_dict = json.loads(mass_times)
    except json.JSONDecodeError:
        row["Saturday"] = mass_times
        return row

    # Fill the columns based on the keys in the dictionary
    for key, value in mass_dict.items():
        if key in columns:
            if isinstance(value, list):
                # Convert lists containing dictionaries or non-string values to strings
                row[key] = ", ".join(
                    json.dumps(v) if isinstance(v, dict) else str(v) for v in value
                )
            else:
                # Handle string or simple values
                row[key] = value
        elif key == "Weekdays":
            # Copy the value to Monday through Friday
            for weekday in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                row[weekday] = value

    return row

# Read the CSV file
with open(input_csv, 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    for idx, row in enumerate(reader):
        # Skip rows with insufficient data
        if not row or len(row) < 2:
            print(f"Skipping malformed or empty row at index {idx}: {row}")
            continue

        # Extract the URL and parish information
        url = row[0].strip()
        parish_raw = row[1]

        # Normalize and extract values using the key-based approach
        name = extract_nested_value(parish_raw, "Name")
        address = extract_nested_value(parish_raw, "Address")
        phone = extract_nested_value(parish_raw, "Phone")
        email = extract_nested_value(parish_raw, "Email")
        mass_times = extract_nested_value(parish_raw, "Mass_Times")
        reconciliation_times = extract_nested_value(parish_raw, "Reconciliation_Times")
        adoration_times = extract_nested_value(parish_raw, "Adoration_Times")

        # Populate Parish Table
        parish_data.append({
            "pkParish": idx,
            "Parish": name,
            "Website": url,
            "Address": address,
            "Email": email,
            "PhoneNumber": phone,
            "ArchdioceseID": 0
        })

        # Populate Mass Times Table
        mass_times_data.append({
            "ParishID": idx,
            "Mass_Times": mass_times
        })

        # Populate Confession Times Table
        confession_data.append({
            "ParishID": idx,
            "Reconciliation_Times": reconciliation_times
        })

        # Populate Adoration Times Table
        adoration_data.append({
            "ParishID": idx,
            "Adoration_Times": adoration_times
        })

        # Populate Sacraments Table
        sacraments_data.append({
            "ParishID": idx,
            "Adoration": "Yes" if adoration_times != "NA" else "No",
            "Confession": "Yes" if reconciliation_times != "NA" else "No"
        })

        # Populate Reconciliation Times by Day
        reconciliation_rows.append(process_reconciliation_times(idx, reconciliation_times))

        # Populate Mass Times by Day
        mass_times_rows.append(process_mass_times(idx, mass_times))

# Function to save a table with spaces after separators
def save_table_with_spaces(data, file_name):
    df = pd.DataFrame(data)
    df.to_csv(file_name, index=False, encoding='utf-8')

# Save each table
save_table_with_spaces(parish_data, parish_table_csv)
save_table_with_spaces(mass_times_data, mass_times_table_csv)
save_table_with_spaces(sacraments_data, sacraments_table_csv)
save_table_with_spaces(adoration_data, adoration_table_csv)
save_table_with_spaces(confession_data, confession_table_csv)
save_table_with_spaces(archdiocese_data, archdiocese_table_csv)
save_table_with_spaces(reconciliation_rows, reconciliation_output_csv)
save_table_with_spaces(mass_times_rows, mass_times_output_csv)

print("CSV files created successfully with cleaned data and formatted times.")
