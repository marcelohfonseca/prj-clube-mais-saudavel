from playwright.sync_api import sync_playwright
from time import sleep

from get_utils import get_week, get_msg_log, parse_time, parse_datetime

import re
import pandas as pd
import numpy as np
import logging


logging.basicConfig(
    filename="scraping.log",  # Nome do arquivo de log
    level=logging.INFO,  # Define o nível mínimo de log
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato da mensagem
)
logger = logging.getLogger(__name__)  # Cria um logger específico para este módulo


class StravaScraper:
    URL = "https://www.strava.com"

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def start_browser(
        self,
        headless=False,
        session_file: str = "user_data",
        view_port: dict = {"width": 1920, "height": 1080},
    ):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir=session_file,
            headless=headless,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        self.page = self.browser.new_page()
        self.page.set_viewport_size(view_port)

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
        logger.info(get_msg_log("login", "info", self.email))
        if self.page.url.startswith(self.URL + "/login"):
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
            print("Login realizado com sucesso!")

    def get_club_members(self, club_url: str):
        self.page.goto(club_url + "/members")
        self.login_if_needed()

        atletas = self.page.query_selector_all("ul.list-athletes li")
        data = []

        for atleta in atletas:
            nome = atleta.query_selector(".text-headline a").inner_text()
            link = atleta.query_selector(".text-headline a").get_attribute("href")
            athlete_id = link.split("/")[-1]
            data.append(
                {
                    "athlete_id": athlete_id,
                    "athlete_name": nome,
                    "link": self.URL + link,
                }
            )
        return pd.DataFrame(data)

    def get_athlete_activities(self, athlete_id: int, weeks: int = 1):
        week_list = get_week(weeks)
        atividades = []

        for week in week_list:
            base_url = f"{self.URL}/athletes/{athlete_id}#interval?"
            params = f"interval={week}&interval_type=week&chart_type=miles&year_offset=0"

            self.page.goto(base_url + params)
            sleep(3)

            elementos = self.page.query_selector_all(
                '//a[@data-testid="activity_name"]'
            )

            for el in elementos:
                href = el.get_attribute("href")
                match = re.search(r"/activities/(\d+)", href)
                if match:
                    atividades.append(match.group(1))
        return dict({"athlete_id": athlete_id, "activities": atividades})

    def activity_data(self, athlete_id: int, activity_id: int):
        self.page.goto(f"{self.URL}/activities/{activity_id}")
        sleep(3)

        data = {
            "athlete_id": athlete_id,
            "activity_id": activity_id,
            "athlete_name": None,
            "activity_type": None,
            "time": None,
            "location": None,
            "activity_name": None,
            "moving_time": None,
            "elapsed_time": None,
            "duration": None,
            "calories": None,
            "distance": None,
            "pace": None,
            "elevation": None,
        }

        # nome do atleta
        try:
            element = '//span[@class="title"]/a[@class="minimal"]'
            if self.element_exists(element):
                content = self.page.locator(element).first
                data["athlete_name"] = (
                    content.text_content().strip()
                    if content.text_content()
                    else "Unnamed"
                )
            else:
                data["athlete_name"] = "Not Found"
        except Exception as e:
            pass

        # tipo de atividade
        try:
            element = '//span[@class="title"]'
            if self.page.locator(element).count() > 0:
                self.page.wait_for_selector(element, timeout=3000)
                content = self.page.locator(element).first
                data["activity_type"] = content.text_content()
            else:
                data["activity_type"] = "Not Found"
        except Exception as e:
            pass

        # data e hora da atividade
        try:
            activity_time = self.page.locator(
                '//div[@class="details"]/time'
            ).text_content()
            data["time"] = parse_datetime(activity_time)
        except Exception as e:
            print("Erro ao coletar a data e hora da atividade:", e)

        # nome da atividade
        try:
            data["activity_name"] = self.page.locator(
                '//div[@class="details"]/h1[@class="text-title1 marginless activity-name"]'
            ).text_content()
        except Exception as e:
            print("Erro ao coletar o nome da atividade:", e)

        # localização da atividade
        try:
            element = '//div[@class="details"]/span[@class="location"]'
            if self.page.locator(element).count() > 0:
                self.page.wait_for_selector(element, timeout=3000)
                content = self.page.locator(element).first
                data["location"] = content.text_content()
            else:
                data["location"] = "Not Found"
        except Exception as e:
            print("Erro ao coletar a localização da atividade:", e)
            data["location"] = "Erro"

        # tempo de movimento
        try:
            moving_time_str = (
                self.page.locator('//ul[@class="inline-stats section"]//li//strong')
                .nth(1)
                .text_content()
            )
            data["moving_time"] = parse_time(moving_time_str)
        except Exception as e:
            print("Erro ao coletar tempo de movimento:", e)

        # distância, pace e elevação (se for corrida ou caminhada)
        if data["activity_type"].lower() in [
            "run",
            "long run",
            "walk",
            "workout",
            "treadmill workout",
        ]:
            try:
                distance_str = (
                    self.page.locator('//ul[@class="inline-stats section"]//li//strong')
                    .nth(0)
                    .text_content()
                )
                data["distance"] = re.sub(r" km", "", distance_str).strip()
            except Exception as e:
                print("Erro ao coletar a distância:", e)

            try:
                pace_str = (
                    self.page.locator('//ul[@class="inline-stats section"]//li//strong')
                    .nth(2)
                    .text_content()
                )
                data["pace"] = re.match(r"(\d{1,2}:\d{2})", pace_str).group(1)
            except Exception as e:
                print("Erro ao coletar o ritmo:", e)

            try:
                elevation_str = (
                    self.page.locator(
                        '//div[contains(@class, "section more-stats")]//div[contains(text(), "Elevation")]/following-sibling::div//strong[abbr[@class="unit" and @title="meters"]]'
                    )
                    .text_content()
                    .strip()
                )
                data["elevation"] = re.sub(r" m", "", elevation_str).strip()
            except Exception as e:
                print("Erro ao coletar a elevação:", e)

        # tempo decorrido
        try:
            elapsed_time_str = self.page.locator(
                '//div[contains(@class, "section more-stats")]//span[@data-glossary-term="definition-elapsed-time"]/parent::div/following-sibling::div//strong'
            ).text_content()
            data["elapsed_time"] = parse_time(elapsed_time_str)
        except Exception as e:
            print("Erro ao coletar o tempo decorrido:", e)

        # calorias
        try:
            data["calories"] = self.page.locator(
                '//div[contains(@class, "section more-stats")]//div[contains(text(), "Calories")]/following-sibling::div//strong'
            ).text_content()
        except Exception as e:
            print("Erro ao coletar as calorias:", e)

        # duração da atividade (não está disponível para todas as atividades)
        try:
            duration_str = self.page.locator('//*[@id="heading"]/div/div/div[2]').text_content().strip()
            data["duration"] = parse_time(duration_str)
        except Exception as e:
            print("Erro ao coletar a duração:", e)

        return pd.DataFrame([data])


if __name__ == "__main__":
    EMAIL = "fonmarcelo@gmail.com"
    PASSWORD = "p[>Yzk@V91ZL2+vcbiXX"
    CLUB_URL = "https://www.strava.com/clubs/1337810"

    scraper = StravaScraper(EMAIL, PASSWORD)
    scraper.start_browser()

    try:
        atv = scraper.activity_data(3580656, 13633978177)
        print(atv)
    finally:
        scraper.close_browser()

    '''try:
        members_df = scraper.get_club_members(CLUB_URL)
        members_df.to_parquet("data/members.parquet")

        if not members_df.empty:
            all_activities = pd.DataFrame()

            for _, row in members_df.iterrows():  # Itera sobre todos os atletas
                athlete_id = row["athlete_id"]
                activities = scraper.get_athlete_activities(athlete_id, weeks=7)
                print(f"Atividades do atleta {athlete_id}: {activities}")

                for activity_id in activities["activities"]:
                    activity_data = scraper.activity_data(athlete_id, activity_id)
                    all_activities = pd.concat([all_activities, activity_data])

            print(all_activities)
            all_activities.to_parquet("data/activities.parquet")
    finally:
        scraper.close_browser()'''
