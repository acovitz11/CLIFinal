#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import ast
from datetime import datetime
import re

#replace the following with actual path
mass_times = pd.read_csv("C:/Users/ashco/Downloads/MassTimesTableByDay.csv") 
adoration = pd.read_csv("C:/Users/ashco/Downloads/AdorationTable3.csv")
confession = pd.read_csv("C:/Users/ashco/Downloads/ReconciliationTimesTableByDay.csv") 
parishes = pd.read_csv("C:/Users/ashco/Downloads/ParishTable3.csv") 


# In[2]:


# process mass times from both strings and dictionaries
def extract_mass_times(value, day):
    # If the value is a string and looks like a dictionary, try to evaluate it
    if isinstance(value, str):
        try:
            # Attempt to safely evaluate the string as a Python literal (dictionary)
            value = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            # If it fails, it means it's a normal string (e.g., '12:00 PM')
            return value
    
    # If the value is a dictionary, expand it for the specific day
    if isinstance(value, dict):
        # If the dictionary contains the 'day' we are interested in, return its times
        if day in value:
            times = value[day]
            if isinstance(times, list):
                # If times are in a list, return them as a comma-separated string
                return ", ".join(times)
            return times  # If it's a single string, return it
    # If value is neither a string nor dictionary, just return it
    return value

days_of_week = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
mass_times_cleaned = mass_times.copy()  # Create a copy to modify

for day in days_of_week:
    mass_times_cleaned[day] = mass_times_cleaned.apply(lambda row: extract_mass_times(row[day], day), axis=1)


# In[3]:


#DETECT LANGUAGES MASS IS OFFERED TO

def detect_languages(row):
    # Define a list of possible languageS
    language_keywords = ['English', 'Spanish', 'French', 'Italian', 'Latin', 'Portuguese', 'German',
                        'Korean', 'Chinese']
    
    # Create an empty list to store detected languages
    detected_languages = set()
    detected_languages.add('English') #default English
    
    # Iterate through each column, splitting by commas and checking for language keywords
    for col in row:
        if isinstance(col, str) and pd.notna(col):  # Ensure the column is a string and not missing
            for keyword in language_keywords:
                # If the language keyword is found in the mass time text, add it to the detected list
                if keyword.lower() in col.lower():
                    detected_languages.add(keyword)
                    
    return ', '.join(sorted(detected_languages))

# Add column to dataframe
mass_times_cleaned['Language'] = mass_times_cleaned.apply(detect_languages, axis=1)


# In[4]:


# MASS TIMES CLEAN

def mass_clean(value):
    # Check if the value is a dictionary
    if isinstance(value, dict):
        # Iterate through dictionary values and clean them
        cleaned_times = []
        for key, time in value.items():
            # Check if the value in dictionary is a list
            if isinstance(time, list):
                # If it's a list, clean each item in the list
                cleaned_times.extend([clean_time(t) for t in time if clean_time(t) is not None])
            else:
                # Clean the time value and filter out None
                cleaned_time = clean_time(time)
                if cleaned_time is not None:
                    cleaned_times.append(cleaned_time)
        return ', '.join(cleaned_times)
    
    # If value is not a dictionary, process it as a single string
    elif isinstance(value, list):
        # If it's a list of times, clean each item in the list and filter out None
        cleaned_times = [clean_time(item) for item in value if clean_time(item) is not None]
        return ', '.join(cleaned_times)
    
    # Otherwise, clean the value directly (assuming it's a string)
    else:
        cleaned_time = clean_time(value)
        return cleaned_time if cleaned_time is not None else ""

def clean_time(time_value):
    # Ensure it's a string before proceeding
    if not time_value:  # checks for empty, 'NA', or only spaces
        return None
    
    # Handle cases like ' NA' or NaN values
    if not isinstance(time_value, str):
        return None  # Return None if it's not a valid string

    # Ensure AM/PM format is consistent
    time_value = re.sub(r'\s?a\.m\.', ' AM', time_value, flags=re.IGNORECASE)
    time_value = re.sub(r'\s?p\.m\.', ' PM', time_value, flags=re.IGNORECASE)

    # Convert lowercase am/pm (e.g., am, pm) to uppercase AM/PM
    time_value = re.sub(r'(\d{1,2}:\d{2})([aApPmM]{2})', r'\1 \2', time_value)
    time_value = re.sub(r'\bam\b', 'AM', time_value, flags=re.IGNORECASE)
    time_value = re.sub(r'\bpm\b', 'PM', time_value, flags=re.IGNORECASE)
    
    # Use regex to extract times in the proper format
    times = re.findall(r'(\d{1,2}:\d{2}\s?[APM]{2})', time_value)

    # Clean each time and remove extra spaces
    cleaned_times = [time.strip() for time in times]
    
    # Return the cleaned times, or None if no valid times were found
    return ', '.join(cleaned_times) if cleaned_times else None


# In[5]:


for col in mass_times.columns[1:8]:  # Skip the ParishID column, end before language
    mass_times_cleaned[col] = mass_times_cleaned[col].apply(mass_clean)
    
#mass_times_cleaned.head()


# In[6]:


# ADORATION AND CONFESSION CLEANING

def sacrement_time_clean(value):
    if pd.isna(value) or value == ' NA':
        return None  # Return None for empty or NA values
    
    if isinstance(value, str):
        # Remove any unnecessary text like 'Time:' and extra spaces
        value = value.replace('Time:', '').strip()
        
        # Standardize p.m. -> PM and a.m. -> AM
        value = re.sub(r'\s?p\.m\.', ' PM', value, flags=re.IGNORECASE)
        value = re.sub(r'\s?a\.m\.', ' AM', value, flags=re.IGNORECASE)
        
        # Regular expression to match time (like 4:00 PM or 6 p.m.)
        time_pattern = r'(\d{1,2}[:]\d{2}\s?[APM]{2}|\d{1,2}\s?[APM]{2})'  # For matching time like '4:00 PM' or '6 p.m.'
        
        time_matches = re.findall(time_pattern, value)
        
        # If a time range exists, we return both start and end times
        if '–' in value or '-' in value:
            time_range = value.split('–') if '–' in value else value.split('-')
            start_time = re.findall(time_pattern, time_range[0].strip())
            end_time = re.findall(time_pattern, time_range[1].strip())
            return f'{start_time[0]} - {end_time[0]}'
        
        # Return the first matched time if no range is found
        return time_matches[0] if time_matches else None
    return None
    


# In[7]:


def sacrement_time_clean(value):
    if pd.isna(value) or value == ' NA':
        return None  # Return None for empty or NA values
    
    if isinstance(value, str):
        # Remove unnecessary parts like 'Time:', extra spaces, or 'or by appointment'
        value = value.replace('Time:', '').strip()
        value = re.sub(r'\s?or\s+by\s+appointment', '', value, flags=re.IGNORECASE).strip()
        
        # Standardize p.m. -> PM and a.m. -> AM
        value = re.sub(r'\s?p\.m\.', ' PM', value, flags=re.IGNORECASE)
        value = re.sub(r'\s?a\.m\.', ' AM', value, flags=re.IGNORECASE)
        
        # Normalize "to" in time ranges to "-" (e.g., "12:00 PM to 1:00 PM" -> "12:00 PM - 1:00 PM")
        value = re.sub(r'\s?to\s?', ' - ', value)

        # Regular expression to match time (like 4:00 PM or 6 p.m.)
        time_pattern = r'(\d{1,2}[:]\d{2}\s?[APM]{2}|\d{1,2}\s?[APM]{2})'  # For matching time like '4:00 PM' or '6 p.m.'
        
        time_matches = re.findall(time_pattern, value)
        
        # If a time range exists, we return both start and end times
        if '–' in value or '-' in value:
            time_range = value.split('–') if '–' in value else value.split('-')
            start_time = re.findall(time_pattern, time_range[0].strip())
            end_time = re.findall(time_pattern, time_range[1].strip())
            if start_time and end_time:
                return f'{start_time[0]} - {end_time[0]}'
        
        # Return the first matched time if no range is found
        return time_matches[0] if time_matches else None
    return None

# Apply this function to a DataFrame for each day's column
def clean_sacrement_times(df):
    # Iterate over each day of the week columns
    days_of_week = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    for day in days_of_week:
        df[day] = df[day].apply(sacrement_time_clean)
    return df


# In[8]:


clean_confession = clean_sacrement_times(confession)
#clean_confession.head()


# In[9]:


#adoration.head()


# In[10]:


copy_adoration = adoration.copy()

def split_by_day(row):
    # Start with an empty dictionary for the days of the week
    adoration_days = {day: "NA" for day in days_of_week}

    # Check if the adoration time is a dictionary or string
    if isinstance(row, dict):
        # If it's a dictionary, map the days in the dictionary to the DataFrame columns
        for day, times in row.items():
            adoration_days[day] = times
    elif isinstance(row, str):
        # If it's a string, try to extract times by day
        for day in days_of_week:
            if day in row:
                adoration_days[day] = row
    return adoration_days

# Apply the function to split times and add new columns for each day
adoration_columns = copy_adoration['Adoration_Times'].apply(lambda x: split_by_day(x) if x != 'NA' else {day: 'NA' for day in days_of_week})

# Convert the results back into a DataFrame
adoration_df = pd.DataFrame(adoration_columns.tolist())

# Merge the new columns with the original ParishID column
clean_adoration = pd.concat([adoration, adoration_df], axis=1)


# In[11]:


clean_adoration = clean_sacrement_times(clean_adoration)
#clean_adoration.head()


# In[12]:


# CLEAN PHONE NUMBERS

def clean_phone_number(phone_number):
    if pd.isna(phone_number) or phone_number == 'NA':  # Handle missing values
        return None
    
    # Remove all non-numeric characters
    cleaned_number = re.sub(r'\D', '', phone_number)
    
    # If the length is correct (10 digits for a standard phone number), format it
    if len(cleaned_number) == 10:
        formatted_number = f"({cleaned_number[:3]}) {cleaned_number[3:6]}-{cleaned_number[6:]}"
        return formatted_number
    else:
        return None 

# Apply the function to clean phone numbers
parishes['PhoneNumber'] = parishes['PhoneNumber'].apply(clean_phone_number)

#parishes.head()


# In[13]:


# Save the DataFrames to CSV files
parishes.to_csv('FinalParishData.csv', index=False)
clean_adoration.to_csv('FinalAdorationData.csv', index=False)
mass_times_cleaned.to_csv('FinalMassTimesData.csv', index=False)
clean_confession.to_csv('FinalConfessionData.csv', index=False)

