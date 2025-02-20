import os

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

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
        all_activity_df = pd.DataFrame()

        for _, row in tqdm(
            members_df.iterrows(),
            total=len(members_df),
            desc='Coletando atividades dos atletas',
        ):
            athlete_id = row['athlete_id']
            activities = scraper.get_athlete_activities(athlete_id, weeks=2)

            for activity_id in tqdm(
                activities['activities'],
                desc=f'Coletando dados de atividades de {athlete_id}',
                leave=False,
            ):
                activity_df = scraper.activity_df(athlete_id, activity_id)
                all_activity_df = pd.concat([all_activity_df, activity_df])

        all_activity_df['week'] = all_activity_df['time'].dt.strftime('%Y%U')

        for week in tqdm(
            all_activity_df['week'].unique(), desc='Salvando arquivos semanais'
        ):
            week_activity_df = all_activity_df[all_activity_df['week'] == week]
            week_activity_df.to_parquet(PATH_TO_DATA + f'activity_week_{week}.parquet')
finally:
    scraper.close_browser()
