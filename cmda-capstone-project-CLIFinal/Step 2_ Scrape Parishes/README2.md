# Setup 
Step 1: Create virtual environment (how to do this varies based on the system you are using)

Step 2: Create a file called .env to store your OPEN AI API Key, put the following line in the file, replacing the word yourapikey with your API key:
OPENAI_API_KEY = "yourapikey"

Step 3: Add the virtual environmment and the .env file to the .gitignore file

Step 4: Activate the virtual environment (how to do this varies based on the system you are using)

Step 5: In the virtual environment, install packages SgrapeGraphAI, pandas, json5, and dotenv (Must be using python 3.9 or higher, I recommend python 3.12 as thats what worked for me)

Step 6: If you encounter an error while running the code that says "AttributeError: 'FetchNode' object has no attribute 'update_state'", go to your virtual environment where scrapegraphai was downloaded, go to lib/python(yourversion)/site-packages, go to scrapegraphai, go to nodes, then open "fetch_node.py". Conrtol F to find the two occurances of the line "return self.update_state(state, compressed_document)", and replace both of them with the following two lines:
        state.update({self.output[0]: compressed_document})
        return state
(If this does not solve the problem, then uninstall ScrapeGraphAI from your virtual environment, and install scrapegraphai version 1.20.1 and then repeat the above step 6)

# Order of Files 
Step 1: Take the output file "parish_results.csv" from webScraperforAllParishes.py and pass it to parish_results_cleaner.py to return the output file "cleaned_urls.csv".

Step 2: Pass "cleaned_urls.csv" to ParishScraperGivenCSV.py to run the code for all the parish links you currently have which outputs "RawScrapedParishData.csv". (or pass a single parish link to TestPromptOnASingleSite.py if you want to test out a new prompt)

Step 3: Pass "RawScrapedParishData.csv" to Combined_Cleaner.py to return "CouldNotScrape.csv" (which contains a list of the parish links that couldn't be scraped), and "JSON-like_Final_File.csv" which contains all the cleaned parish data

Step 4: Pass "JSON-like_Final_File.csv" to "ConvertCsvTo6CsvTables.py" to split that large table into the smaller tables that will be passed on to the dashboard creation part