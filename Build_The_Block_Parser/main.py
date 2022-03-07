import requests
import pandas as pd

#These are all of the main variables used to build a call url to the the census api website

HOST = "https://www1.nyc.gov/assets/nypd/js/"
MEETINGS_JS = "meetings.js"
base_url = "/".join([HOST, MEETINGS_JS])


Meeting_Request = requests.get(base_url)

Meetings = Meeting_Request.content

#Setting up AGE data frame, getting rid of first header row
#Meetings_pd = pd.DataFrame(data=Meeting_Request.json()[1:])

print(Meeting_Request)