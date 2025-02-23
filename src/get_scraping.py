import logging
import re
from datetime import datetime
from time import sleep

import numpy as np
import pandas as pd
from playwright.sync_api import sync_playwright

from src.get_utils import get_msg_log, get_week, parse_datetime, parse_time


logging.basicConfig(
    filename='scraping.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class StravaScraper:
    URL = 'https://www.strava.com'

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def start_browser(
        self,
        headless=False,
        session_file: str = 'user_data',
        view_port: dict = {'width': 1920, 'height': 1080},
    ):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir=session_file,
            headless=headless,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        )
        self.page = self.browser.new_page()
        self.page.set_viewport_size(view_port)
        logger.info(get_msg_log('start', 'info', self.email))

    def close_browser(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def element_exists(self, element: str, timeout: int = 3000) -> bool:
        try:
            return self.page.locator(element).first.is_visible(timeout=timeout)
        except Exception:
            return False

    def login_if_needed(self):
        logger.info(get_msg_log('login', 'info', self.email))
        if self.page.url.startswith(self.URL + '/login'):
            self.page.locator('//*[@id="desktop-email"]').click()
            self.page.locator('//*[@id="desktop-email"]').fill(self.email)
            self.page.locator('//*[@id="desktop-login-button"]').click()
            sleep(2)

            self.page.locator(
                '//*[@id="__next"]/div/div[2]/div[2]/div/div/form/div[1]/div[2]/div/input'
            ).fill(self.password)

            self.page.locator(
                '//*[@id="__next"]/div/div[2]/div[2]/div/div/form/div[2]/button'
            ).click()

    def get_club_members(self, club_id: str):
        self.page.goto(f'{self.URL}/clubs/{club_id}/members')
        self.login_if_needed()

        try:
            atletas = self.page.query_selector_all('ul.list-athletes li')
            data = []

            for atleta in atletas:
                nome = atleta.query_selector('.text-headline a').inner_text()
                link = atleta.query_selector('.text-headline a').get_attribute('href')
                athlete_id = link.split("/")[-1]
                data.append(
                    {
                        'athlete_id': athlete_id,
                        'athlete_name': nome,
                        'link': self.URL + link,
                        'updated_at': datetime.now(),
                    }
                )
            logger.info(get_msg_log('members', 'info', club_id))
        except Exception as e:
            logger.error(get_msg_log('members', 'error', club_id))
            return pd.DataFrame
        return pd.DataFrame(data)

    def get_athlete_activities(self, athlete_id: int, weeks: int = 1):
        week_list = get_week(weeks)
        atividades = []

        try:
            for week in week_list:
                base_url = f'{self.URL}/athletes/{athlete_id}#interval?'
                params = (
                    f'interval={week}&interval_type=week&chart_type=miles&year_offset=0'
                )

                self.page.goto(base_url + params)
                sleep(3)

                elementos = self.page.query_selector_all(
                    '//a[@data-testid="activity_name"]'
                )

                for el in elementos:
                    href = el.get_attribute('href')
                    match = re.search(r'/activities/(\d+)', href)
                    if match:
                        atividades.append(match.group(1))

            logger.info(get_msg_log('activities', 'info', athlete_id))
            return dict({'athlete_id': athlete_id, 'activities': atividades})
        except Exception as e:
            logger.error(get_msg_log('activities', 'error', athlete_id))
            return dict({'athlete_id': athlete_id, 'activities': []})

    def activity_data(self, athlete_id: int, activity_id: int):
        self.page.goto(f'{self.URL}/activities/{activity_id}/overview')
        sleep(3)

        logger.info(get_msg_log('activity', 'info', f'{athlete_id}: {activity_id}'))

        data = {
            'athlete_id': athlete_id,
            'activity_id': activity_id,
            'athlete_name': 'Unnamed',
            'activity_type': 'Unnamed',
            'date': None,
            'date_time': None,
            'location': 'Unnamed',
            'activity_name': 'Unnamed',
            'moving_time': np.nan,
            'elapsed_time': np.nan,
            'duration': np.nan,
            'calories': np.nan,
            'distance': np.nan,
            'pace': np.nan,
            'elevation': np.nan,
            'link': f'{self.URL}/activities/{activity_id}',
            'updated_at': datetime.now(),
            'week': None,
        }

        # nome do atleta
        try:
            element = '//span[@class="title"]/a[@class="minimal"]'
            if self.element_exists(element):
                content = self.page.locator(element).first.text_content()
                data['athlete_name'] = content.strip() if content else 'Unnamed'
            else:
                data['athlete_name'] = 'Not Found'
        except Exception as e:
            logger.error(
                get_msg_log('activity', 'error', f'{athlete_id}: {activity_id} - {e}')
            )

        # tipo de atividade
        try:
            element = '//*[@id="heading"]/header/h2/span'
            if self.element_exists(element):
                content = self.page.locator(element).text_content().strip()

                if content:
                    content = content.replace('–', '-').replace('—', '-')
                    parts = content.split('-')
                    data['activity_type'] = (
                        parts[-1].strip() if len(parts) > 1 else 'Unnamed'
                    )
                else:
                    data['activity_type'] = 'Unnamed'
            else:
                data['activity_type'] = 'Not Found'
        except Exception as e:
            logger.error(
                get_msg_log('activity', 'error', f'{athlete_id}: {activity_id} - {e}')
            )

        # data e hora da atividade
        try:
            element = '//div[@class="details"]/time'
            if self.element_exists(element):
                content = self.page.locator(element).text_content()
                data['date_time'] = parse_datetime(content) if content else np.nan
        except Exception as e:
            logger.error(
                get_msg_log('activity', 'error', f'{athlete_id}: {activity_id} - {e}')
            )

        # nome da atividade
        try:
            element = '//div[@class="details"]/h1[@class="text-title1 marginless activity-name"]'
            if self.element_exists(element):
                content = self.page.locator(element).text_content().strip()
                data['activity_name'] = content if content else 'Unnamed'
            else:
                data['activity_name'] = 'Not Found'
        except Exception as e:
            logger.error(
                get_msg_log('activity', 'error', f'{athlete_id}: {activity_id} - {e}')
            )

        # localização da atividade
        try:
            element = '//div[@class="details"]/span[@class="location"]'
            if self.element_exists(element):
                content = self.page.locator(element).text_content().strip()
                data['location'] = content if content else 'Unnamed'
            else:
                data['location'] = 'Not Found'
        except Exception as e:
            logger.error(
                get_msg_log('activity', 'error', f'{athlete_id}: {activity_id} - {e}')
            )

        # tempo de movimento
        try:
            element = '//ul[@class="inline-stats section"]//li//strong'
            if self.element_exists(element):
                content = self.page.locator(element).nth(1).text_content().strip()
                data['moving_time'] = parse_time(content) if content else np.nan
            else:
                data['moving_time'] = np.nan
        except Exception as e:
            logger.error(
                get_msg_log('activity', 'error', f'{athlete_id}: {activity_id} - {e}')
            )

        # distância, pace e elevação (se for corrida ou caminhada)
        # https://support.strava.com/hc/en-us/articles/216919407-Supported-Sport-Types-on-Strava
        if data['activity_type'].lower() in [
            'walk',
            'run',
            'long run',
            'virtual run',
            'treadmill workout',
            'hike',
            'workout',
            'ride',
            'mountain bike ride',
            'gravel ride',
            'e-bike ride',
            'e-mountain bike ride',
            'velomobile',
            'virtual ride',
        ]:
            try:
                element = '//*[@id="heading"]/div/div/div[2]/ul/li[div[text()="Distance"]]/strong'
                if self.element_exists(element):
                    content = self.page.locator(element).nth(0).text_content().strip()
                    data['distance'] = (
                        re.sub(r' km', '', content) if content else np.nan
                    )
                else:
                    data['distance'] = np.nan
            except Exception as e:
                logger.error(
                    get_msg_log(
                        'activity', 'error', f'{athlete_id}: {activity_id} - {e}'
                    )
                )

        try:
            possible_elements = [
                '//div[contains(@class, "section more-stats")]//div[contains(text(), "Elevation")]/following-sibling::div//strong[abbr[@class="unit" and @title="meters"]]',
                '//*[@id="heading"]/div/div/div[2]/ul/li[div[text()="Elevation"]]/strong',
            ]

            show_more_button = '//*[@id="heading"]/div/div/div[2]/div[1]/div[1]/button'
            if self.element_exists(show_more_button):
                self.page.locator(show_more_button).click()

            elevation = None
            for element in possible_elements:
                if self.element_exists(element):
                    content = self.page.locator(element).text_content().strip()
                    if content:
                        elevation = re.sub(r'[^\d]', '', content)
                        break
                else:
                    elevation = np.nan
            data['elevation'] = elevation if elevation else np.nan
        except Exception as e:
            logger.error(
                get_msg_log('activity', 'error', f'{athlete_id}: {activity_id} - {e}')
            )

        if data['activity_type'].lower() in [
            'walk',
            'run',
            'long run',
            'virtual run',
            'treadmill workout',
            'hike',
            'workout',
        ]:
            try:
                element = '//ul[@class="inline-stats section"]//li//strong'
                if self.element_exists(element):
                    content = self.page.locator(element).nth(2).text_content().strip()
                    data['pace'] = (
                        re.match(r'(\d{1,2}:\d{2})', content).group(1)
                        if content
                        else np.nan
                    )
                else:
                    data['pace'] = np.nan
            except Exception as e:
                logger.error(
                    get_msg_log(
                        'activity', 'error', f'{athlete_id}: {activity_id} - {e}'
                    )
                )

        # tempo decorrido
        try:
            possible_elements = [
                '//div[contains(@class, "section more-stats")]//span[@data-glossary-term="definition-elapsed-time"]/parent::div/following-sibling::div//strong',
                '//table[@class="unstyled"]//tr[th/span[contains(text(), "Elapsed Time")]]/td',
            ]

            show_more_button = '//*[@id="heading"]/div/div/div[2]/div[1]/div[1]/button'
            if self.element_exists(show_more_button):
                self.page.locator(show_more_button).click()

            elapsed_time = None
            for element in possible_elements:
                if self.element_exists(element):
                    content = self.page.locator(element).text_content().strip()
                    if content:
                        elapsed_time = parse_time(content)
                        break
                else:
                    elapsed_time = np.nan
            data['elapsed_time'] = elapsed_time if elapsed_time else np.nan
        except Exception as e:
            logger.error(
                get_msg_log('activity', 'error', f'{athlete_id}: {activity_id} - {e}')
            )

        # duração da atividade (não está disponível para todas as atividades)
        try:
            element = '//*[@id="heading"]/div/div/div[2]/ul/li/strong'
            if self.element_exists(element):
                content = self.page.locator(element).text_content().strip()
                data['duration'] = parse_time(content) if content else np.nan
            else:
                data['duration'] = np.nan
        except Exception as e:
            logger.error(
                get_msg_log('activity', 'error', f'{athlete_id}: {activity_id} - {e}')
            )

        # calorias
        try:
            possible_elements = [
                '//div[contains(@class, "section more-stats")]//div[contains(text(), "Calories")]/following-sibling::div//strong',
                '//div[@class="section more-stats"]//table//tr[th[text()="Calories"]]/td[1]',
            ]

            show_more_button = '//*[@id="heading"]/div/div/div[2]/div[1]/div[1]/button'
            if self.element_exists(show_more_button):
                self.page.locator(show_more_button).click()

            calories = np.nan
            for element in possible_elements:
                if self.element_exists(element):
                    content = self.page.locator(element).text_content().strip()
                    if content:
                        calories = content.replace(',', '.')
                        break
            data['calories'] = calories if calories else np.nan
        except Exception as e:
            logger.error(
                get_msg_log('activity', 'error', f'{athlete_id}: {activity_id} - {e}')
            )

        dataset = pd.DataFrame([data])        
        dataset = dataset.astype(
            {
                'athlete_id': 'int',
                'activity_id': 'int',
                'athlete_name': 'string',
                'activity_type': 'category',
                'date_time': 'datetime64[ns]',
                'date': 'datetime64[ns]',
                'location': 'string',
                'activity_name': 'string',
                'moving_time': 'timedelta64[ns]',
                'elapsed_time': 'timedelta64[ns]',
                'duration': 'timedelta64[ns]',
                'calories': 'float',
                'distance': 'float',
                'pace': 'string',
                'elevation': 'float',
                'link': 'string',
                'updated_at': 'datetime64[ns]',
                'week': 'string',
            }
        )
        dataset['date'] = dataset['date_time'].dt.date
        dataset['week'] = dataset['date_time'].dt.strftime('%Y%U')

        return dataset
