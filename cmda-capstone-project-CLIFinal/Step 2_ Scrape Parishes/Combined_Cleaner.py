import csv
import re
import os

# Define allowed characters and allowed words
allowed_characters = {',', '"', "'", '{', '}', ' ', '~', ':', '[', ']', '(', ')'}
allowed_words = {
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", 
    "NA", "Name", "Address", "Phone", "Email", "Mass_Times", "Reconciliation_Times", "Adoration_Times"
}

def process_csv(input_file):
    # Update the input file directly
    temp_file = input_file + ".temp"

    with open(input_file, 'r') as infile, open(temp_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Process each row in the CSV
        for index, row in enumerate(reader):
            if index == 0:  # Write the header row as is
                writer.writerow(row)
                continue

            if row and row[0]:  # Ensure the row and the first cell are not empty
                if row[0].startswith("http://www."):
                    row[0] = row[0].replace("http://www.", "https://www.")
                elif row[0].startswith("http://"):
                    row[0] = row[0].replace("http://", "https://www.")
                elif row[0].startswith("https://") and not row[0].startswith("https://www."):
                    row[0] = row[0].replace("https://", "https://www.")
                elif not row[0].startswith("https://"):
                    row[0] = "https://www." + row[0]

            writer.writerow(row)

    # Replace the original file with the updated temp file
    os.replace(temp_file, input_file)

def apply_replacements(input_file, output_file):
    # Define replacement rules
    replacements = {
        r"(?i)confession/reconciliationtimes": "Reconciliation_Times",
        r"(?i)confession/reconciliation times": "Reconciliation_Times",
        r"(?i)confessionreconciliationtimes": "Reconciliation_Times",
        r"(?i)confession_reconciliation_times": "Reconciliation_Times",
        r"(?i)confessiontimes": "Reconciliation_Times",
        r"(?i)confession_times": "Reconciliation_Times",
        r"(?i)confession times": "Reconciliation_Times",
        r"(?i)reconciliationtimes": "Reconciliation_Times",
        r"(?i)reconciliation_times": "Reconciliation_Times",
        r"(?i)reconciliation times": "Reconciliation_Times",
        r"(?i)masstimes": "Mass_Times",
        r"(?i)mass_times": "Mass_Times",
        r"(?i)mass times": "Mass_Times",
        r"(?i)adorationtimes": "Adoration_Times",
        r"(?i)adoration times": "Adoration_Times",
        r"(?i)adoration_times": "Adoration_Times",
        r'(?i)"phone"': '"Phone"',
        r'(?i)"email"': '"Email"',
        r'(?i)"address"': '"Address"',
        r'(?i)"name"': '"Name"',
    }

    # Read the entire file as plain text
    with open(input_file, 'r') as file:
        file_content = file.read()

    # Perform regex replacements
    for pattern, replacement in replacements.items():
        file_content = re.sub(pattern, replacement, file_content)

    # Write the updated content back to a new file
    with open(output_file, 'w') as file:
        file.write(file_content)

def capitalize_whole_words(input_file, output_file):
    # Define replacement rules for whole words
    replacements = {
        r"(?i)\bconfession\b": "Confession",  # Matches whole word "confession" (case-insensitive)
        r"(?i)\badoration\b": "Adoration",  # Matches whole word "adoration" (case-insensitive)
        r"(?i)\breconciliation\b": "Reconciliation",  # Matches whole word "reconciliation" (case-insensitive)
        r"(?i)\bmass\b": "Mass",  # Matches whole word "mass" (case-insensitive)
    }

    # Read the entire file as plain text
    with open(input_file, 'r') as file:
        file_content = file.read()

    # Perform regex replacements for whole words
    for pattern, replacement in replacements.items():
        file_content = re.sub(pattern, replacement, file_content)

    # Write the updated content back to a new file
    with open(output_file, 'w') as file:
        file.write(file_content)

def is_scrapable(line):
    # Split the line at the first comma
    parts = line.split(",", 1)
    if len(parts) < 2:
        return True  # Scrapable if there's no content after the first comma

    # Process only the part after the first comma
    content = parts[1]
    index = 0
    word_buffer = ""  # Temporary storage for building words
    line_length = len(content)

    while index < line_length:
        char = content[index]

        # Check if the character is an allowed character
        if char in allowed_characters:
            if word_buffer:
                # Check if the buffered word is in allowed words
                if word_buffer not in allowed_words:
                    return True  # Scrapable if the word is not allowed
                word_buffer = ""  # Reset the buffer
            index += 1
            continue

        # Build words from characters not in allowed characters
        if char.isalnum() or char == "_":  # Include underscores for multi-word terms
            word_buffer += char
        else:
            # If we encounter a non-alphanumeric character, check the buffer
            if word_buffer and word_buffer not in allowed_words:
                return True  # Scrapable if the word is not allowed
            word_buffer = ""  # Reset the buffer

        index += 1

    # Final check for the last word in the buffer
    if word_buffer and word_buffer not in allowed_words:
        return True  # Scrapable if the last word is not allowed

    return False  # Line is not scrapable

def clean_csv_file(lines, output_file):
    with open(output_file, "w", encoding="utf-8") as outfile:
        for line in lines:
            # Replace """ with ""
            line = line.replace('"""', '""')

            # Replace multiple commas with a single comma
            while ',,' in line:  # Ensure all consecutive commas are reduced
                line = line.replace(',,', ',')

            # Remove the last character if it is a comma
            if line.endswith(',\n'):
                line = line[:-2] + '\n'  # Remove the last comma and preserve the newline
            elif line.endswith(','):
                line = line[:-1]  # Remove the last comma if there's no newline

            # Add '"{' before the first "" after the first comma and '}"' at the end of the line
            first_comma_index = line.find(',')
            if first_comma_index != -1 and line[first_comma_index + 1:first_comma_index + 3] == '""':
                line = (
                    line[:first_comma_index + 1]
                    + '"{'  # Add '"{' after the first comma
                    + line[first_comma_index + 1:]  # Keep the rest of the line
                ).rstrip() + '}"\n'  # Add '}"' at the end of the line

            # Add specific keys if "Name" is not in the line
            if '"Name"' not in line and '{' in line:
                # Locate the start of the JSON block
                start_index = line.find('{') + 1

                # Split the JSON-like structure into its parts using `,` as a delimiter
                parts = line[start_index:].split('","')

                # Map keys to corresponding parts
                if len(parts) >= 6:
                    parts[0] = '""Name"": ' + parts[0] + '"'  # Add "Name"
                    if "{" in parts[1]:  # Check if "Address" is a JSON block
                        parts[1] = '""Address"": ' + parts[1]  # Add "Address"
                    else:
                        parts[1] = '""Address"": "' + parts[1] + '"'  # Add "Address"
                    parts[2] = '""Phone"": "' + parts[2] + '"'  # Add "Phone"
                    parts[3] = '""Email"": "' + parts[3] + '"'  # Add "Email"
                    parts[4] = '""Mass_Times"": ' + parts[4]  # Add "Mass_Times" (keep it JSON)
                    if "{" in parts[5]:  # Check if "Reconciliation_Times" is a JSON block
                        parts[5] = '""Reconciliation_Times"": ' + parts[5]  # Add "Reconciliation_Times"
                    else:
                        parts[5] = '""Reconciliation_Times"": "' + parts[5] + '"'  # Add "Reconciliation_Times"
                    if "{" in parts[6]:  # Check if "Adoration_Times" is a JSON block
                        parts[6] = '""Adoration_Times"": ' + parts[6]  # Add "Adoration_Times"
                    else:
                        parts[6] = '""Adoration_Times"": "' + parts[6]  # Add "Adoration_Times"
                # Reassemble the parts into a valid JSON-like structure
                line = line[:start_index] + ', '.join(parts)

            # Ensure lines ending with '}"}"' are fixed to '}}"'
            if line.endswith('}"}"\n') or line.endswith('}"}"'):
                line = line.rstrip('\n').replace('}"}"', '}}"') + '\n'

            # Write the processed line to the output file
            outfile.write(line)

# Usage
input_csv = 'RawScrapedParishData.csv'  # Replace with the path to your input CSV file
removed_csv = 'CouldNotScrape.csv'  # Replace with the path to your removed file
final_json_csv = 'JSON-like_Final_File.csv'

# Process and update the input CSV directly
process_csv(input_csv)

# Apply text replacements and save to an intermediate output file
apply_replacements(input_csv, removed_csv)

# Apply whole-word capitalization and save to the final output file
capitalize_whole_words(removed_csv, removed_csv)

# Separate rows into scrapable and not scrapable
with open(removed_csv, 'r') as file:
    lines = file.readlines()

scrapable_rows = []
not_scrapable_rows = []

for line in lines:
    if is_scrapable(line.strip()):  # Strip to remove trailing newlines/spaces
        scrapable_rows.append(line)
    else:
        not_scrapable_rows.append(line)

# Write the not scrapable rows to the removed file
with open(removed_csv, 'w') as file:
    file.writelines(not_scrapable_rows)

# Process scrapable rows for JSON-like formatting
clean_csv_file(scrapable_rows, final_json_csv)

print(f"Invalid rows saved to {removed_csv}")
print(f"Processed file saved as {final_json_csv}.")
