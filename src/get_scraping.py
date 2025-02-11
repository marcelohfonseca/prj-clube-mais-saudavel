from playwright.sync_api import sync_playwright
from time import sleep
from datetime import datetime

import re
import pandas as pd

EMAIL = 'fonmarcelo@gmail.com'
PASSWORD = 'p[>Yzk@V91ZL2+vcbiXX'
SESSION_FILE = 'state.json'

columns = [
    'athlete_id', 'athlete_name', 'activity_id', 'activity_type', 'time', 'location', 'activity_name', 'moving_time', 'distance', 'pace'
]
activities_df = pd.DataFrame()


def format_time(time_str):
    # Verifica se o formato tem ":", separando por ":", que deve gerar uma lista de [horas, minutos, segundos]
    time_parts = time_str.split(":")

    if len(time_parts) == 2:  # Caso de "MM:SS"
        hours = 0
        minutes = int(time_parts[0])
        seconds = int(time_parts[1])
    elif len(time_parts) == 3:  # Caso de "HH:MM:SS"
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = int(time_parts[2])
    else:
        raise ValueError("Formato de tempo inválido")

    return f"{hours:02}:{minutes:02}:{seconds:02}"


def login_if_needed(page):
    """Faz login apenas se necessário."""
    if page.url.startswith("https://www.strava.com/login"):
        print("Realizando login...")
        page.locator('//*[@id="desktop-email"]').click()
        page.locator('//*[@id="desktop-email"]').fill(EMAIL)
        page.locator('//*[@id="desktop-login-button"]').click()
        sleep(2)

        page.locator(
            '//*[@id="__next"]/div/div[2]/div[2]/div/div/form/div[1]/div[2]/div/input'
        ).click()
        page.locator(
            '//*[@id="__next"]/div/div[2]/div[2]/div/div/form/div[1]/div[2]/div/input'
        ).fill(PASSWORD)
        page.locator(
            '//*[@id="__next"]/div/div[2]/div[2]/div/div/form/div[2]/button'
        ).click()

        sleep(5)
        print("Login realizado com sucesso!")


def scrape_activity(url):
    activity_df = pd.DataFrame(columns=columns)
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir='user_data', 
            headless=False, 
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.set_viewport_size({"width": 1980, "height": 1080})

        page.goto(url + "/members")
        login_if_needed(page)

        sleep(3)

        athlete_id = "3580656"
        page.goto(
            "https://www.strava.com/athletes/3580656#interval?interval=202506&interval_type=week&chart_type=miles&year_offset=0"
        )
        sleep(3)

        # Coleta todos os links de atividades
        elementos = page.locator(
            '//*[@id="main"]/div//a[contains(@href, "/activities/")]'
        )

        # Extrai os códigos das atividades
        atividades = []
        for el in elementos.all():
            href = el.get_attribute("href")
            match = re.search(r"/activities/(\d+)", href)
            if match:
                atividades.append(match.group(1))

        print("Códigos das atividades:", atividades)

        activity_id = '13583503049'
        page.goto("https://www.strava.com/activities/13583503049")
        sleep(3)

        data = {
            'athlete_id': athlete_id,
            'activity_id': activity_id,
            'athlete_name': None,
            'activity_type': None,
            'time': None,
            'location': None,
            'activity_name': None,
            'moving_time': None,
            'elapsed_time': None,
            'calories': None,
            'distance': None,
            'pace': None,
            'elevation': None,
        }

        # Coleta nome do atleta e tipo de atividade
        try:
            data["athlete_name"] = page.locator(
                '//span[@class="title"]/a[@class="minimal"]'
            ).text_content()

            data["activity_type"] = (
                page.locator('//span[@class="title"]')
                .first.text_content()
                .split("–")[-1]
                .strip()
            )
        except Exception as e:
            print("Erro ao coletar os dados de atleta e tipo de atividade:", e)

        # Coleta detalhes da atividade
        try:
            activity_time = page.locator('//div[@class="details"]/time').text_content()
            data["time"] = datetime.strptime(
                activity_time.strip(), "%I:%M %p on %A, %B %d, %Y"
            )

            data["location"] = page.locator(
                '//div[@class="details"]/span[@class="location"]'
            ).text_content()
            data["activity_name"] = page.locator(
                '//div[@class="details"]/h1[@class="text-title1 marginless activity-name"]'
            ).text_content()
        except Exception as e:
            print("Erro ao coletar os detalhes da atividade:", e)

        # Coleta tempo de movimento
        try:
            element = '//ul[@class="inline-stats section"]//li//strong'
            moving_time_str = page.locator(element).nth(1).text_content()
            data["moving_time"] = format_time(moving_time_str)

            if data["activity_type"].lower() == "run":
                distance_str = page.locator(element).nth(0).text_content()
                data["distance"] = re.sub(r" km", "", distance_str).strip()

                pace_str = page.locator(element).nth(2).text_content()
                data["pace"] = re.match(r"(\d{1,2}:\d{2})", pace_str).group(1)
        except Exception as e:
            print("Erro ao coletar os detalhes de tempo da atividade:", e)

        try:
            elapsed_time_str = page.locator(
                '//div[contains(@class, "section more-stats")]//span[@data-glossary-term="definition-elapsed-time"]/parent::div/following-sibling::div//strong'
            ).text_content()
            data["elapsed_time"] = format_time(elapsed_time_str)

            data["calories"] = page.locator(
                '//div[contains(@class, "section more-stats")]//div[contains(text(), "Calories")]/following-sibling::div//strong'
            ).text_content()

            if data["activity_type"].lower() == "run":
                elevation_str = (
                    page.locator(
                        '//div[contains(@class, "section more-stats")]//div[contains(text(), "Elevation")]/following-sibling::div//strong[abbr[@class="unit" and @title="meters"]]'
                    )
                    .text_content()
                    .strip()
                )
                data["elevation"] = re.sub(r" m", "", elevation_str).strip()
        except Exception as e:
            print("Erro ao coletar Elapsed Time e Calories:", e)

        activity_df = pd.DataFrame([data])

        print('Dados:')
        print(activity_df.head())  # Verifica se os dados foram coletados corretamente
        context.close()

        return activity_df  # Retorna o DataFrame

url = "https://www.strava.com/clubs/1337810"
# url = "https://www.strava.com/clubs/1337810/recent_activity"
dados = scrape_activity(url)
