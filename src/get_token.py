import json
import requests

client_id = "9957"
client_secret = "bcb7634eef1e2c2a2a67de2693c7b9ba374a6df5"
redirect_uri = "http://localhost/"

request_url = (
    f"http://www.strava.com/oauth/authorize?client_id={client_id}"
    f"&response_type=code&redirect_uri={redirect_uri}"
    f"&approval_prompt=force"
    f"&scope=profile:read_all,activity:read_all"
)

print("Click here:", request_url)
code = input("Insert the code from the url: ")

token = requests.post(
    url="https://www.strava.com/api/v3/oauth/token",
    data={
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
    },
)

strava_token = token.json()

with open("strava_token.json", "w") as outfile:
    json.dump(strava_token, outfile)


'''with open("strava_token.json", "r") as token:
    data = json.load(token)

if data["expires_at"] < time.time():
    token = requests.post(
        url="https://www.strava.com/api/v3/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": data["refresh_token"],
        },
    )

    # Let's save the new token
    strava_token = token.json()

with open("strava_token.json", "w") as outfile:
    json.dump(strava_token, outfile)
'''
