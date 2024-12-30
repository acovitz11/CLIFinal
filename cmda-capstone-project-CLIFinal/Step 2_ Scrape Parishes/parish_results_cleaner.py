import pandas as pd

# Load the CSV file
file_path = 'parish_results.csv'  # Replace with the path to your CSV file
df = pd.read_csv(file_path)

# Clean the data: Filter out rows where the Website column contains "Not Found", "Error", or is NaN
valid_urls = df.loc[
    ~df['Website'].isin(["Not Found", "Error", "Website Not Found"]) & df['Website'].notna(), 'Website'
].tolist()

# Print or save the cleaned list of URLs
print(valid_urls)

# Optional: Save the cleaned list to a new CSV file
cleaned_df = pd.DataFrame(valid_urls, columns=["Website"])
cleaned_df.to_csv('cleaned_urls.csv', index=False)
