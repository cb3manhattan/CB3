"""
Automatically Create November SLA
"""

from Automate_SLA import make_sla_dataframe, make_sla_folders, create_sla_tracker, reso_text_output, stip_emails
import sys
from sys import platform


#==========================================================================================
# Set Text File. The Agenda will be read from here.
if sys.platform == "darwin":
    # On Mac
    agenda = r"/Users/calvindechicago/Documents/GitHub/CB3/sample_agenda/sample_agenda.txt"
    filepath = r"/Users/calvindechicago/Desktop/Community Board 3/SLA"
    EXCEL_TEMPLATE = r"/Users/calvindechicago/Desktop/Community Board 3/SLA/SLA_tracker_template.xlsx"

elif sys.platform == "win32" or sys.platform == "win64":
    # Windows...
    agenda = r"C:\Users\MN03\Desktop\Current Items\SLA_Agenda\sla_app_type\SLA_Agenda_Example.txt"
    filepath = r"C:\Users\MN03\Desktop\Current Items\SLA_Agenda\SLA_AUTO_OUTPUT"
    EXCEL_TEMPLATE = r"C:\Users\MN03\Desktop\Current Items\SLA_Agenda\Tracker_Template\Tracker_Template.xlsx"

else:
    print("Excel Template filepath not defined")
#==========================================================================================

#==========================================================================================
# SET EXCEL Tracker FILEPATH
if sys.platform == "darwin":
    # On Mac
    EXCEL_TRACKER = r"/Users/calvindechicago/Desktop/Community Board 3/SLA/SLA_tracker_template.xlsx"

elif sys.platform == "win32" or sys.platform == "win64":
    # On PC
    EXCEL_TRACKER = r"C:\Users\MN03\Desktop\Current Items\SLA_Agenda\SLA_Tracker_Nov.xlsx"
    print("EXCEL TRACKER Filepath is: " + EXCEL_TRACKER)
else:
    print("Excel Tracker filepath not defined")
#==========================================================================================


agenda_table = make_sla_dataframe(agenda)

make_sla_folders(agenda_table, filepath)

create_sla_tracker(agenda_table, EXCEL_TEMPLATE)




due_date = "Friday, November 19"
stip_emails(EXCEL_TRACKER, filepath, due_date="Friday, November 19")

reso_text_output(agenda_table, filepath)

# Run add_reps once reps have been added manually to tracker.
# add_reps(agenda_table)