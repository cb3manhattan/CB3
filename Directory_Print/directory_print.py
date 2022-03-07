"""
This script iterates through Shared Drive and prints names of files, directories and subdirectories.

"""

import pandas as pd
import datetime as dt
from datetime import datetime
import openpyxl
import os
import csv
from os import listdir
from os.path import isfile, join


# THIS IS THE DIRECTORY WHERE FILE NAMES WILL BE PULLED FROM
files_folder = r'Y:\public'


# Create list of filenames in Root directory only
def all_files(files_folder):
        onlyfiles = [f for f in listdir(files_folder) if isfile(join(files_folder, f))]
        print(onlyfiles)
        print('\n ----------------------------------------------------------')

        # Create list of all filenames in directory, including file extensions
        for (root,dirs,files) in os.walk(files_folder):
                print('\n')
                print (root)
                print (dirs)

def only_dirs(files_folder):
        for item in os.listdir(files_folder):
                if os.path.isdir(os.path.join(files_folder, item)):
                        print(item)

def only_files(files_folder):
        for file in os.listdir(files_folder):
                if os.path.isfile(os.path.join(files_folder, file)):
                        print(file)


##
##  RUN FUNCTIONS
##


#all_files(files_folder)

#only_dirs(files_folder)

only_files(files_folder)

