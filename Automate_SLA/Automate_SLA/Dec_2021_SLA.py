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
    EXCEL_TRACKER = r"/Users/calvindechicago/Desktop/Community Board 3/SLA/SLA_tracker_template.xlsx"

elif sys.platform == "win32" or sys.platform == "win64":
    # Windows...
    agenda = r"C:\Users\MN03\Desktop\Current Items\SLA_Agenda\Dec_2021\dec_agenda.txt"
    filepath = r"C:\Users\MN03\Desktop\Current Items\SLA_Agenda\Dec_2021\SLA_OUTPUT"
    EXCEL_TEMPLATE = r"C:\Users\MN03\Desktop\Current Items\SLA_Agenda\Tracker_Template\Tracker_Template.xlsx"
    EXCEL_TRACKER = r"C:\Users\MN03\Desktop\Current Items\SLA_Agenda\SLA_Tracker_DEC.xlsx"
else:
    print(" One or more filepaths is not defined")
#==========================================================================================



#=======================================================
agenda_table = make_sla_dataframe(agenda)
#=======================================================
# make_sla_folders(agenda_table, filepath)
#=======================================================
# create_sla_tracker(agenda_table, EXCEL_TEMPLATE)
#=======================================================


#=======================================================
stip_emails(EXCEL_TRACKER, filepath, due_date="Friday, December 17 at 3:00 pm")
#=======================================================
# reso_text_output(agenda_table, filepath)
#=======================================================
# Run add_reps once reps have been added manually to tracker.
# add_reps(agenda_table)