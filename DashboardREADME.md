# Power BI Dashboard
## Pre-Cleaning 
### Cleaning CSV files
Needed CSVs for input into FinalCleaningCSVNotebook.ipynb (change input file paths)
MassTimesTableByDay
AdorationTable3
ReconciliationTimesTableByDay
ParishTable3

The notebook will complete the following cleaning tasks:
Extract mass times and standardize
Detect the languages that mass is offered in
Split the adoration file returned string by day
Clean and standardize format of phone numbers
Extract the zip code from address for processing to get states
Output the cleaned data files as “Finals”

### Power BI Input Data
The data from the Final CSV files is inputted into the dashboard. These file paths will need to be changed to where the files will be held.
ParishTable
MassTimesTable
ConfessionTable
AdorationTable

These datatables are referenced from the other files. As long as the original 4 hold the same structure, these should automatically update as well. These group the data by week to three columns (by ParishID, Days, and Times). They are not used in the dashboard but an additional column is added called “Sacrament” for each and then they are combined into the “SacrementsByDay” dataset which is used in the dashboard.
DaysAdoration
DaysConfession
DaysMass

The datasets Days and Sacraments are used for general categorization and formatting for the dashboard as an overarching category for filtering. CLI_Data is the information for parish survey response scores that was provided. The dataset Diocese Locations takes the diocese column endings and attached state locations for use in dashboard mapping.

OverlappedParishes is the dataset that merges CLI_Data and ParishTable to get parishes that are scrapped by VT and scored by CLI. ActivityRankings references SacrementsByDay and groups by ParishID and sacramental frequencies.

## Power BI Dashboard
### Dashboard Data
The data that is used in the dashboard comes from ActivityRankings, CLI_Data, OverlappedParishes, ParishTable, and SacrementsByDay datasets. A few extra calculated columns are added:
ParishTable and OverlappedParishes have a column called ParishUnique which combines the parish name and VT scrapped ID so we have unique parish names. This is to differentiate between parishes with the same name (e.x. St. Mary’s in IN vs St. Mary’s in KY).
ActivityRankings has the following calculations:
Sacramental Importance which weighs each sacrament relatively (right now, Mass as 3, Confession as 2, Adoration as 1). This will need to be changed for adjusting the weights of each sacrament with more data available.
CombinedScore which takes the frequencies of each sacrament by parish and multiplies it by sacramental importance score.
NormalizedCombinedScore which takes the same formula as combinedSore but normalized.
Average Activity Score which does the same thing as NormalizedCombinedScore but in a calculated column for visualization.

### Dashboard Breakdown
The dashboard consists of 7 pages: the first three containing information only on the scrapped parishes by VT, the fourth only with CLI information, and the last three related to the overlapping parishes where we have information from both sources.

Page 1: VT Overview
Overview of the scrapped parish data split by state with the map, top states, and numerical total cards
Page 2: VT Sacrament
Initial glance into sacramental frequencies for each parish. Split by averages for each sacrament as well as averages of each sacrament for each state.
Page 3: VT Face Cards
For scrapped parishes, face cards are developed so that contact information as well as sacramental frequencies and times are available at a quick glance.
Page 4: CLI Overview
Similar to VT Overview but only for CLI data. Shows split by dioceses as well as top states.
Page 5: CLI/VT Scoring State
Parish response scores in each category for the overlapping parishes (currently 70 between both sources). Average CLI scores overall and average CLI scores by state included.
Page 6: CLI/VT Face Cards
Very similar to the VT Face Cards page with contact and sacramental information but also includes CLI Scores for each parish as well as the VT Activity Score (from AverageActivityScore calculated column).
Page 7: CLI/VT Scoring Comparison
Table contains overlapping parishes sacramental frequencies for each category and scatter plots show Parish Health Score vs Activity Score and Individual Engagement with Activity Score.

## Limitations/Future Work
The biggest thing I would suggest would be looking into the sacramental importance weights and finding the best relative scores for each of those. In the scatter plots of Page 7, there is a lot of clustering between 0.3 and 0.5 for the VT Activity Score which I believe is caused by the weighing of mass so high compared to the other two. Adjusting to find a better weight would be a good indicator for finding that analysis with overall parish health and individual engagement.

The parishes were merged (CLI and VT) on the parish name and location, so there may be some duplicates that you should be aware of (i.e. if two St. Mary’s exist in KY). Additionally, zip codes were filled down for missing zip codes (as the assumption was that parishes were scrapped from one diocese at a time and would be in the same location), but this could be inaccurate for a few.

Some Python scripts were run within the PowerBI dashboard Queries in ParishTable. The first finds the state abbreviation from the extracted zipcode from Address. The second compares the state abbreviation to get the full state name. The first is run using libraries pyzipcode and ZipCodeDatabase, which may need to be installed in the Python environment being used. Additionally, you may need to enable Python scripts (in Power BI settings).

PowerBI privacy settings make it difficult to share the dashboard with those outside your organization. To share with those outside the organization, it is possible to be published to the web (the ArcGIS maps have a bug that the new update caused, but will hopefully be fixed soon). I would recommend creating a new PowerBI workspace and sharing the dashboard that way within CLI for members to collaborate and see filters, etc.

Thank you for allowing us to work on this project and please do not hesitate to reach out with any questions.
