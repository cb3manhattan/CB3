# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.12.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# """
# # Automating SLA Document Creation
#
# ## The purpose of this script is to automate SLA tasks. This includes the following:
# - Creating a table with each component of the application (i.e. address, tradename, etc.)
# - Creating folders for each establishment for archiving
# - Creating emails, letters, etc. 
#
#
# ## Process:
# 1. Copy list of items from online agenda into text doc as shown below
# 2. Quickly remove unwanted text from file. Useful text includes Application Type headings and SLA application agenda items.  
# 3. Various functions should be designed to have the following outputs:
#     - A table of the applications with each element parsed out into different columns. One table output should feed
#     directly into the tracking sheet I have.
#     - Template text with address block, email subject, and text
#
# ---------------------------------------------------------------------------------
#
# ## TO DO
#  - Start scripting work to input values into template letters
#  - Create output for excel, which can serve a number of functions:
#      - a place to input additional info like lawyers name
#      - track other SLA items
#  - Create similar script that takes as an input an excel file instead of a text file.
#  - Create script that inputs area code based on address.
#  - Other info from agenda might be useful: License type, app type (method of operation change, etc)
#
#
# """
#
#

import pandas as pd
import datetime as dt
from datetime import datetime
import requests
import openpyxl
import os
import csv
import sys

# Print Conda Env info running in Jupyter Notebook 
# #!conda info
print(sys.executable)

# Set Text File. The Agenda will be read from here. 
agenda = r"C:\Users\MN03\Desktop\Current Items\SLA_Agenda\sla_app_type\SLA_Agenda_Example.txt"


# Function to create Agenda Dataframe / Table
def make_sla_dataframe(agenda):
    # Open the text file
    #r+ = read/write access mode
    agenda = open(agenda, 'r+')
    #Readlines creates a list, where each index contains a line of text, which in this case is a single establishment. 
    contents = agenda.readlines()
    
    # Close the text file
    agenda.close()
    
    # This creates a dataframe where each row is a line from the agenda pull
    agenda_df = pd.DataFrame(contents, columns=['line'])
    
    #Remove illegal character (apostrophe) from each string, and replace 'B'way' with 'Broadway'
    agenda_df = agenda_df.apply(lambda x: x.str.replace("B'way", "Broadway"))
    agenda_df = agenda_df.apply(lambda x: x.str.replace("'", ""))
    
    # Create new column with agenda number only for each row
    agenda_df['agenda_number'] = agenda_df.loc[:,'line'].str.split(pat=".").str[0]
    
    # Create column with all agenda item info except for the agenda item number
    agenda_df['agenda_info_no_number'] = agenda_df.loc[:,'line'].str.split(pat=".").str[1]
    
    # This partitions the string into:
    # 1: business name
    # 2: comma
    # 3: address, and license type and notes
    # Once partitioned the 1st and 3rd columns are output. 
    agenda_df['b_name'] = agenda_df.loc[:,'agenda_info_no_number'].str.partition(sep=",", expand=True)[0]
    agenda_df['address'] = agenda_df.loc[:,'agenda_info_no_number'].str.partition(sep=",", expand=True)[2]
    
    # This creates a column showing the text in the first parentheses. The second set is not important because these will always be
    # notes on the liquor licence, which aren't important for this exercise. 
    agenda_df['address_sup'] = agenda_df['address'].str.extract('\(([^)]+)')

    # The first set of parentheses contains either an address supplement, such as 'basement',
    # or information about the liquor license. 
    # Strings containing 'op' or 'wb' are filtered out in the code below so that only address supplementary info remains. 
    agenda_df['address_sup3'] = agenda_df['address_sup'].str.contains('op|wb', na=True)
    
    # Replace all values in the address supplement column identified above as having 'op' or 'wb' with an empty string.
    agenda_df['address_sup'] = agenda_df['address_sup'].mask(agenda_df['address_sup3'], "")
    
    # This line splits out the address and creates a new string with everything to the left of the first 
    # opening parenthesis, which is the primary address. 
    agenda_df['prim_address'] = agenda_df['address'].str.split(pat="(").str[0]
    
    # This line removes '\n' characters from each row
    #df = df.replace('\n','', regex=True)
    agenda_df['prim_address'] = agenda_df['prim_address'].replace('\n','', regex=True)
    
    # This line splits out the business name and creates a new string with everything to the left of the first 
    # opening parenthesis, which is the business trade name.
    agenda_df['b_tradename'] = agenda_df['b_name'].str.split(pat="(").str[0]
    
    # This creates a column showing the text in the first parentheses. The second set is not important because these will always be
    # notes on the liquor licence, which aren't important for this exercise. 
    agenda_df['b_llc_name'] = agenda_df['b_name'].str.extract('\(([^)]+)')
    
    # This replaces NAN with empty string
    agenda_df['b_llc_name'] =agenda_df['b_llc_name'].fillna('')
    
    # Where LLC name is blank, set to value of b_tradename, which erroneously contains the llc names 

    def set_b_name(x):
        if x['b_llc_name'] == '':
            return x['b_tradename']
        else:    
            return x['b_llc_name'];

    agenda_df['b_llc_name'] = agenda_df.apply(lambda x: set_b_name(x), axis=1)


    # Where tradename and LLC name are the same, set tradename to empty string
    agenda_df.loc[agenda_df['b_tradename'] == agenda_df['b_llc_name'], 'b_tradename'] ='' 

    
    # Clean agenda type header rows
    agenda_df.loc[agenda_df.line.str.contains("Alterations"), 'line']='Alteration' 

    agenda_df.loc[agenda_df.line.str.contains("Items not heard at Committee"), 'line']='Item not heard at Committee' 

    agenda_df.loc[agenda_df.line.str.contains("	Expansion onto Municipal Property"), 'line']='Expansion onto Municipal Property' 
    
    
    # Create Column showing Application Type for each Establishment
    
    #initialize app_type column to blank string
    agenda_df['app_type'] = ''

    for index, row in agenda_df.iterrows():
        if row.line[0].isdigit() is False:
            a_type = row.line
            agenda_df.at[index, 'app_type'] = ''

        else:
            agenda_df.at[index, 'app_type'] = a_type

    # Strip whitespace and newline characters from beginning and end of strings
    agenda_df['app_type'] = agenda_df['app_type'].str.strip()
    
    
    # This line creates new column that contains a bool series with 'True' for every line that starts with a a digit
    # Lines that do not contain a digit (agenda number) will be removed.
    agenda_df['entry_row']= agenda_df['line'].str[0].str.isdigit()
    
    # Filters out rows that do not contain an agenda item (start with a digit). 
    # Because the entry_row column is boolean, just calling it as as a filter will remove False entries.  
    agenda_df = agenda_df[agenda_df.entry_row]
    
    return agenda_df;

agenda_table = make_sla_dataframe(agenda)

agenda_table

# +
"""
This function creates folders for archiving Executed Stips and Resolutions
param: agenda_table - This is an automatically produced dataframe using the make_sla_function
param: Filepath - This is the filepath where the folders will be created, and it should be noted that each folder will be
       created in a top level folder containing the month. This parameter be created by user and provided as an argument. 

"""

def make_sla_folders(agenda_table, filepath):
    
    # Current month (number and name) and year. This will be used to create top level folder. 
    month_name = str(datetime.now().strftime("%B"))
    month_num = str(datetime.now().month)
    year = str(datetime.now().year)

    # This line creates the top level directory with the month, year, and 'SLA'
    month_dir = month_num + '-' + month_name + ' ' + year + ' SLA'
    
    filepath = os.path.join(filepath, month_dir)
    

    # Strip whitespace from left and right of column. Consider doing this for other columns     
    agenda_table['b_tradename'] = agenda_table.b_tradename.str.strip() 
    agenda_table['b_llc_name'] = agenda_table['b_llc_name'].str.strip()
    agenda_table['prim_address'] = agenda_table['prim_address'].str.strip()
    
    
    # 1 Make new folder path for each establishment
    # 2 This will be the primary address followed by a dash followed by the trade name if it exists, else the LLC name
    #      These will follow this pattern: '45 Avenue B - Lamias Fish Market'
    #
    for index, row in agenda_table.iterrows():
        est_filepath = ''
        if row.b_tradename != '':
            est_filepath = row.prim_address + ' - ' + row.b_tradename
        else:
            est_filepath = row.prim_address + ' - ' + row.b_llc_name

        fin_filepath = os.path.join(filepath, est_filepath)
        
        try:
            os.makedirs(fin_filepath)
            
    
        except Exception as e: print(e)
# -


filepath = r"C:\Users\MN03\Desktop\Current Items\SLA_Agenda\SLA_AUTO_OUTPUT"

make_sla_folders(agenda_table, filepath)

# +
# Append automated output to Standard SLA Tracking Template
# https://stackoverflow.com/questions/57314254/pandas-df-write-to-excel-template-with-prepared-styles

TEMPLATE_PATH = r"C:\Users\MN03\Desktop\Calvin Docs\SLA\Automation Work\SLA_Tracker_Template.xlsx"

# +
# Create new text file for emails to sla:
desktop = os.path.expanduser("~/Desktop")
top_folder = 'SLA_AUTO_OUTPUT'
filepath = os.path.join(desktop,'Current Items','SLA_Agenda')

sla_emails_text = os.path.join(filepath, 'sla_email_text.txt')

# In cases where the 'b_llc_name' column does not have a value, The b_tradename also contains the LLC name. 
# This should be fixed in the future, but for now the work around is to identify rows where both columns have values
# to identify where the 'b_tradename' column is truly a tradename. 

for index, row in agenda_df.iterrows():
    if (row.b_tradename != '' and row.b_llc_name != ''):
        with open(sla_emails_text, "a") as file:
            file.write("\n" + "\n" + "\n" + "CB3 Resolution re: " + row.b_tradename + " - " + row.prim_address + "\n"
                       "Re:    " + row.b_llc_name + "\n" + "       " + "d/b/a " + row.b_tradename + "\n" + "       " +
                       row.prim_address + "\n" + "       " + "New York, NY" + "\n")
            file.close() 
        
    else:
        with open(sla_emails_text, "a") as file:
            file.write("\n" + "\n" + "\n" + "CB3 Resolution re: " + row.b_tradename + " - " + row.prim_address +
                       "\n" + "Re:    " + row.b_tradename + "\n" + "       " +  row.prim_address + "\n" + "       " + 
                       "New York, NY" + "\n" )
            file.close() 
# +
# Create new text file for EMAILS for admin approvals to sla:
desktop = os.path.expanduser("~/Desktop")
top_folder = 'SLA_AUTO_OUTPUT'
filepath = os.path.join(desktop,'Current Items','SLA_Agenda')

sla_emails_text = os.path.join(filepath, 'sla_email_text_admin_approvals.txt')

for index, row in agenda_df.iterrows():
        with open(sla_emails_text, "a") as file:
            file.write("\n \n \n" + "CB 3 No Objection To (New Application, Municipal Expansion, Alteration, Corporation Change) with stipulations, stipulations attached – " + row.prim_address + "\n \n" + """Please see the attached letter from CB 3 Manhattan stating no objection to the wine, beer,and cider application for """
                       + row.b_tradename + " located at " + row.prim_address + """, so long as the attached stipulations are included in the license agreement.""")
            file.close() 

# -
# SLA APPLICATION TYPE OUTPUT
Nov_Path= r"C:\Users\MN03\Desktop\Current Items\SLA_Agenda\sla_app_type\sla_app_type.txt"


agenda_df = make_sla_folders(Nov_Path)

# +
agenda_df

# Open the text file
#r+ = read/write access mode
agenda = open(Nov_Path, 'r+')
    
#Readlines creates a list, where each index contains a line of text, which in this case is a single establishment. 
contents = agenda.readlines()

# Close the text file
agenda.close()

print(contents)
# -

  # This creates a dataframe where each row is a line from the agenda pull
agenda_df = pd.DataFrame(contents, columns=['line'])
    
    #Remove illegal character (apostrophe) from each string, and replace 'B'way' with 'Broadway'
agenda_df = agenda_df.apply(lambda x: x.str.replace("B'way", "Broadway"))
agenda_df = agenda_df.apply(lambda x: x.str.replace("'", ""))
    
    # This line creates new column that contains a bool series with 'True' for every line that starts with a a digit
    # Lines that do not contain a digit (agenda number) will be removed.
agenda_df['entry_row']= agenda_df['line'].str[0].str.isdigit()

# +
agenda_df


# IDENTIFY SUBSTRINGS
# df[df['A'].str.contains("hello")]


# df.loc[(df.Event == 'Dance'),'Event']='Hip-Hop'

agenda_df.loc[agenda_df.line.str.contains("Alterations"), 'line']='Alteration' 

agenda_df.loc[agenda_df.line.str.contains("Items not heard at Committee"), 'line']='Item not heard at Committee' 

agenda_df.loc[agenda_df.line.str.contains("	Expansion onto Municipal Property"), 'line']='Expansion onto Municipal Property' 




# +
# Iterate through every row. 
# If line does not start with a digit, take 'line' value and assign it to every row until there is another row without a digit. 
# see is_digit code above
# might also 

    # This line creates new column that contains a bool series with 'True' for every line that starts with a a digit
    # Lines that do not contain a digit (agenda number) will be removed.
   # agenda_df['entry_row']= agenda_df['line'].str[0].str.isdigit()

#initialize app_type column to blank string
agenda_df['app_type'] = ''

for index, row in agenda_df.iterrows():
    if row.line[0].isdigit() is False:
        a_type = row.line
        agenda_df.at[index, 'app_type'] = ''

    else:
        agenda_df.at[index, 'app_type'] = a_type
        
# Strip whitespace and newline characters from beginning and end of strings

agenda_df['app_type'] = agenda_df['app_type'].str.strip()


# -

agenda_df



# +
def set_app_type(x):
    
    if x[0][0].isdigit() is False:
        index_dict.update({x.name: x.line})
        index_list.append(x.name)
        app_type = x.line
        print(app_type)
#         print(index_dict)
#         print("index list: " + str(index_list))
        
    else: 
        print(app_type)
        
    
    
    
    
# -

agenda_df["app_type"] = agenda_df.apply(lambda x: 'False' if x.line[0].isdigit() is False else 'True', axis=1)

# +
# new_df = df[df.apply(lambda x : bool_provider(x['Rev_M'],x['Year']),axis=1)]

# +
# Test pull changes from calvinbrown32 to cb3manhattan
# -



# +
# Pull Sample Agenda from personal github repo
url = "https://calvinbrown32.github.io/external_files/sample_agenda.txt"
agenda_sample = requests.get(url).content

# This returns text (above returns raw bytes)
# -

# Create Directory. This script creates a directory 
def create_sla_dir():
    # Current month (number and name) and year. This will be used to create top level folder. 
    month_name = str(datetime.now().strftime("%B"))
    month_num = str(datetime.now().month)
    year = str(datetime.now().year)

    # This line creates the top level directory with the month, year, and 'SLA'
    month_dir = month_num + '-' + month_name + ' ' + year + ' SLA'

    #Print message that script is running
    print("Making SLA folders at following location:")

    # FIND DESKTOP PATH and create a folder structure below it. 
    desktop = os.path.expanduser("~/Desktop")
    top_folder = 'SLA_AUTO_OUTPUT'
    filepath = os.path.join(desktop,'Current Items', 'SLA_Agenda', top_folder, month_dir)
    try:
        os.makedirs(filepath)
        print(filepath)
    except Exception as e: print(e)
        
    return filepath;
