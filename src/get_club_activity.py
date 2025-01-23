import json
import requests
import pandas as pd

CLUB_ID = "1337810"

with open("strava_token.json", "r") as token:
    data = json.load(token)

token = data["access_token"]

url = 'https://www.strava.com/api/v3/clubs'
activities_url = url + f"/{CLUB_ID}/activities?access_token={token}"

response = requests.get(activities_url)
activity = response.json()

df = pd.DataFrame(activity)
print(df.head())
