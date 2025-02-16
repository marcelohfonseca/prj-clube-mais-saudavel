import os

import pandas as pd
from dotenv import load_dotenv

from src.get_scraping import StravaScraper


load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
CLUB_ID = 1337810
PATH_TO_DATA = 'data/'

scraper = StravaScraper(EMAIL, PASSWORD)
scraper.start_browser()

try:
    members_df = scraper.get_club_members(CLUB_ID)
    members_df.to_parquet(PATH_TO_DATA + 'members.parquet')

    if not members_df.empty:
        all_activities = pd.DataFrame()

        for _, row in members_df.iterrows():
            athlete_id = row['athlete_id']
            activities = scraper.get_athlete_activities(athlete_id, weeks=7)

            for activity_id in activities['activities']:
                activity_data = scraper.activity_data(athlete_id, activity_id)
                all_activities = pd.concat([all_activities, activity_data])

        for week in all_activities['week'].unique():
            week_activities = all_activities[all_activities['week'] == week]
            week_activities.to_parquet(PATH_TO_DATA + f'week_{week}.parquet')
finally:
    scraper.close_browser()
