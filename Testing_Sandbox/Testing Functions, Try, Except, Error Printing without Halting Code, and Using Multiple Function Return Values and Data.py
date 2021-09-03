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

# """
# ## BELOW: TESTING TRY and EXCEPT. 
# ####    I want to learn how to use this feature in my code
# ####    I want to print the error but not halt the code. 
# ####    This will be designed to alert if directory already exists
#     
# ####    OTHER ITEMS to learn: Returning multiple items from function. 
# """

import pandas as pd
import datetime as dt
from datetime import datetime
import openpyxl
import os
import csv

agenda_pull = r"C:\Users\MN03\Desktop\Calvin Docs\SLA\Automation Work\Example_Agenda_Pull.txt"


def test_try_except(agenda_pull):
    
    # Open the text file
    #r+ = read/write access mode
    agenda = open(agenda_pull, 'r+')
    
    #Readlines creates a list, where each index contains a line of text, which in this case is a single establishment. 
    contents = agenda.readlines()
    
    # Close the text file
    agenda.close()
    
    # This creates a dataframe where each row is a line from the agenda pull
    agenda_df = pd.DataFrame(contents, columns=['line'])
    
    
    desktop = os.path.expanduser("~/Desktop")
    top_folder = 'Test_try_except'
    filepath = os.path.join(desktop, top_folder)
    try:
        os.makedirs(filepath)
    except Exception as e: 
        print(e)
        pass
    
    return 0, 'a function can return numerous values and data', ['hello', 'why','a function can return numerous values and data'], agenda_df; 

mac_agenda = r'/Users/calvindechicago/Desktop/SLA_test.txt'

test_try_except(mac_agenda)[3]


test_try_except(mac_agenda)[3]




