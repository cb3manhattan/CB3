# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

"""
The purpose of this script is to automate SLA tasks. This includes creating folders for each month and establishment,
creating emails and letters from templates, and more. 


Process:
1) Copy list of items from online agenda into text doc as shown below
2) I will likely want to quickly remove certain text from this, such as section descriptions like 'New Liquor License Applications,' or other info that will not go into the final outputs like the description of the license type. 
3) The most important thing will likely be keeping each entry to one line in the input file as I will likely use line breaks to parse each item. 
4) If this doesn't work, another option might be the period (.) followed by blank spaces. 
5) DBA format seems to be in parentheses after the name. 
6) I will have to manually add lawyers names.
7) Agenda number is the number in the list itself. 

----------------------------------------------------------------------------
1 - Open and read lines of text file
    - https://www.geeksforgeeks.org/reading-writing-text-files-python/
2 - Iterate through each line and build a dataframe / table from the relevant contents
3 - Filter out rows that begin with numeric. These should be the agenda items. 
4 - split at period and get first item, which is the numeric agenda item number. 
5 - split again and get the business name
6 - split again and get the address

---------------------------------------------------------------------------------

TO DO
 - Create code to remove illegal characters from strings ('B'way' and apostrophes have been replaced)
 - Start scripting work to input values into template letters
 - Create output for excel, which can serve a number of functions:
     - a place to input additional info like lawyers name
     - track other SLA items
 - Create similar script that takes as an input an excel file instead of a text file. 


"""

import pandas as pd
import datetime as dt
from datetime import datetime
import openpyxl
import os
import csv

agenda_pull = r"C:\Users\MN03\Desktop\Calvin Docs\SLA\Automation Work\Example_Agenda_Pull.txt"


def make_sla_folders(agenda_pull):
    
    # Open the text file
    #r+ = read/write access mode
    agenda = open(agenda_pull, 'r+')
    
    #Readlines creates a list, where each index contains a line of text, which in this case is a single establishment. 
    contents = agenda.readlines()
    
    # Close the text file
    agenda.close()
    
    # This creates a dataframe where each row is a line from the agenda pull
    agenda_df = pd.DataFrame(contents, columns=['line'])
    
    #Remove illegal character (apostrophe) from each string, and replace 'B'way' with 'Broadway'
    agenda_df = agenda_df.apply(lambda x: x.str.replace("B'way", "Broadway"))
    agenda_df = agenda_df.apply(lambda x: x.str.replace("'", ""))
    
    # This line creates new column that contains a bool series with 'True' for every line that starts with a a digit
    # Lines that do not contain a digit (agenda number) will be removed.
    agenda_df['entry_row']= agenda_df['line'].str[0].str.isdigit()
    
    # Filters out rows that do not contain an agenda item (start with a digit). 
    # Because the entry_row column is boolean, just calling it as as a filter will remove False entries.  
    agenda_df = agenda_df[agenda_df.entry_row]
    
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
    filepath = os.path.join(desktop, top_folder, month_dir)
    os.makedirs(filepath)
    print(filepath) 
    
    # Strip whitespace from left and right of column. Consider doing this for other columns     
    agenda_df['b_tradename'] = agenda_df.b_tradename.str.strip() 
    agenda_df['b_llc_name'] = agenda_df['b_llc_name'].str.strip()
    agenda_df['prim_address'] = agenda_df['prim_address'].str.strip()
    
    
    # 1 Make new folder path for each establishment
    # 2 This will be the primary address followed by a dash followed by the trade name if it exists, else the LLC name
    #      These will follow this pattern: '45 Avenue B - Lamias Fish Market'
    #
    for index, row in agenda_df.iterrows():
        est_filepath = ''
        if row.b_tradename != '':
            est_filepath = row.prim_address + ' - ' + row.b_tradename
        else:
            est_filepath = row.prim_address + ' - ' + row.b_llc_name

        fin_filepath = os.path.join(desktop, top_folder, month_dir, est_filepath)
        os.makedirs(fin_filepath)
        
    return agenda_df;
    

september_pull =  r"C:\Users\MN03\Desktop\Calvin Docs\SLA\Automation Work\September_Agenda_Pull.txt"

make_sla_folders(agenda_pull)

agenda_df = make_sla_folders(agenda_pull)

"""
MAKE SLA TRACKING SHEET
- Every month a new tracking sheet needs to be created. 
- Use code above to pull information from the agenda and append it to columns in an excel template.
- The following columns are created:
    Agenda Number
    Business name
    DBA
    Address
    Address Supplement
    Rep Name 
    Rep Email
    Rep Phone
    Sent Date
    Received 
"""

agenda_df

"""
BELOW: TESTING TRY and EXCEPT. 
    I want to learn how to use this feature in my code
    I want to print the error but not halt the code. 
    This will be designed to alert if directory already exists
    
    OTHER ITEMS to learn: Returning multiple items from function. 
"""


def test_try_except():
    desktop = os.path.expanduser("~/Desktop")
    top_folder = 'Test_try_except'
    filepath = os.path.join(desktop, top_folder)
    try:
        os.makedirs(filepath)
    except Exception as e: 
        print(e)
        pass
    return 0; 


test_try_except()

# +
# USE THIS BRANCH
