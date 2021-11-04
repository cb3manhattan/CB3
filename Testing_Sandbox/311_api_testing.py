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
## BELOW: TESTING Socrata NY Open Data API. 
####    Using request library to pull 311 data for Community Board

#### To DO 
1. Create Javascript that takes value of community board dropdown and passes it to query builder
2. Create Date reader. 

"""

import pandas as pd
import geopandas as gpd
import datetime as dt
from datetime import datetime
import openpyxl
import os
import csv
import requests 
import folium
import matplotlib
import numpy as np


# +
# Geojson Endpoint for NYC Open Data - 311 2010 - Present
# https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9

ENDPOINT = "https://data.cityofnewyork.us/resource/erm2-nwe9.geojson"
QUERY_SYMBOL = '?'
COMMUNITY_BOARD = 'community_board'
CB = "03 MANHATTAN"
base_url = ENDPOINT + QUERY_SYMBOL + COMMUNITY_BOARD + '=' + CB

# +
# Create secondary query to test date function. 
# Documentation here: https://dev.socrata.com/foundry/data.cityofnewyork.us/erm2-nwe9

ENDPOINT = "https://data.cityofnewyork.us/resource/erm2-nwe9.geojson"
QUERY_SYMBOL = '?'
WHERE = "$where="
date = "2021-09-01T00:00:00.000"
date_operator = " > "
date_query = f"created_date{date_operator}'{date}'"
base_url = ENDPOINT + QUERY_SYMBOL + WHERE + date_query
# -

# Current Time in floating timestamp data type, which is what Socrata uses. 
now = datetime.now()
dt_2 = now.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-4]

print(dt_2)

# See base url assembled from pieces above
base_url

# Blank Space in url works with Socrata, but not geopandas, so replacing space with html hexadecimal space. 
base_url = base_url.replace(' ','%20')

cb3_complaints = requests.get(base_url)

# Get html response code
cb3_complaints

# +
# Read in geojson data from socrata url created above 

cb3_complaints_geo = gpd.read_file(base_url)
# -

# Make sure geodataframe was created
type(cb3_complaints_geo)

cb3_complaints_geo.crs

# +
# Total bounds is returning null array. This is probably because there are null values in geometry column. 
# Follow Steps 1 and 2 to correct:

# 1 Create new geodataframe of rows with null geometry so that data is not lost
complaints_null_geo = cb3_complaints_geo[cb3_complaints_geo['geometry'].isna()]

# 2 Remove all rows with null geometry from original geodataframe 
cb3_complaints_geo = cb3_complaints_geo[cb3_complaints_geo['geometry'].notna()]
# -


bounds = cb3_complaints_geo.total_bounds
a = np.mean(bounds[0:3:2]).round(3)
b = np.mean(bounds[1:4:2]).round(3)
data_centroid = [b,a]
print(data_centroid)

cb3_complaints = cb3_complaints_geo.to_json()

type(cb3_complaints)

filepath_cb_complaints = r"/Users/calvindechicago/Desktop"

# +
#cb3_complaints_geo.to_file(filepath_cb_complaints, driver="GeoJSON")  
# -

print(cb3_complaints)

# +



cb3_complaints_geo = cb3_complaints_geo[cb3_complaints_geo['geometry'].notna()]



# -
cb3_complaints_geo.total_bounds


# +
# Get sorted unique community board values in data pull 

cbs = cb3_complaints_geo.loc[:,'community_board'].sort_values().unique()
# -

cbs

# +
# Create drop down selection html for each community board 

for i in cbs:
    i=f"""<option value="{i}">{i}</option>"""
    print(i)


# -

mapcomplaints = folium.Map(location=data_centroid, tiles = 'cartodbpositron', zoom_start=10, control_scale=True)


folium.features.GeoJson(cb3_complaints_geo,                                                                          
                       ).add_to(mapcomplaints)


# Creates Folium map
mapcomplaints

# +
# Create a Map instance
m = folium.Map(location=data_centroid, tiles = 'cartodbpositron', zoom_start=10, control_scale=True)

#Plot a choropleth map
#Notice: 'geoid' column that we created earlier needs to be assigned always as the first column
folium.Choropleth(
    geo_data=choropleth_data,
    name='Percentage of Cyclists',
    data=choropleth_data,
    columns=['geoid', 'pct_bike'],
    key_on='feature.id',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    line_color='white',
    line_weight=0,
    highlight=False,
    smooth_factor=1.0,
    #threshold_scale=[1, 2, 3, 4, 5],
    legend_name= 'Percentage of workers that bike to work').add_to(m)
# -


