import argparse
import os
import logging

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

from src.get_score import Scorer
from src.get_scraping import StravaScraper
from src.get_utils import import_all_data

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

PATH_TO_DATA = "data/"


def load_env_vars():
    """Carrega variáveis de ambiente e valida presença de credenciais."""
    load_dotenv()
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    if not email or not password:
        logging.error("As variáveis de ambiente EMAIL e PASSWORD são obrigatórias.")
        logging.error(
            "Certifique-se de que o arquivo .env está configurado corretamente."
        )
        exit(1)

    return email, password


def parse_arguments():
    """Faz o parsing dos argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Script de scraping e pontuação do Strava Club."
    )
    parser.add_argument(
        "--score", action="store_true", help="Se passado, executa a pontuação."
    )
    parser.add_argument(
        "--club-id", type=int, required=True, help="ID do clube Strava."
    )

    return parser.parse_args()


def scrape_club_members(scraper, club_id):
    """Coleta os membros do clube e salva os dados."""
    logging.info(f"Coletando membros do clube {club_id}...")

    members_df = scraper.get_club_members(club_id)
    members_df.to_parquet(PATH_TO_DATA + "members.parquet")

    members_list = members_df["athlete_id"].tolist()

    if not members_list:
        raise ValueError(f"Nenhum atleta encontrado no clube {club_id}")

    logging.info(f"Foram encontrados {len(members_list)} atletas no clube {club_id}.")
    return members_list


def scrape_athlete_activities(scraper, members_list):
    """Coleta atividades dos atletas e retorna um DataFrame consolidado."""
    all_activity_dfs = []

    for athlete_id in tqdm(
        members_list, total=len(members_list), desc="Coletando atividades dos atletas"
    ):
        activities = scraper.get_athlete_activities(athlete_id, weeks=2)

        for activity_id in tqdm(
            activities["activities"],
            desc=f"Atividades do atleta {athlete_id}",
            leave=False,
        ):
            activity_df = scraper.activity_data(athlete_id, activity_id)
            all_activity_dfs.append(activity_df)

    if all_activity_dfs:
        return pd.concat(all_activity_dfs, ignore_index=True)
    return pd.DataFrame()


def save_weekly_activity_data(all_activity_df):
    """Salva os dados de atividades organizados por semana."""
    weeks = all_activity_df["week"].unique()

    for week in tqdm(weeks, desc="Salvando arquivos semanais"):
        week_activity_df = all_activity_df[all_activity_df["week"] == week]
        week_activity_df.to_parquet(PATH_TO_DATA + f"activity_week_{week}.parquet")


def calculate_score():
    """Executa a pontuação dos atletas."""
    logging.info("Calculando pontuação...")
    try:
        data = import_all_data()
        score_df = Scorer(data).score()
        score_df.to_parquet(PATH_TO_DATA + "score.parquet")
        logging.info("Pontuação salva com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao calcular a pontuação: {e}")


def main():
    email, password = load_env_vars()
    args = parse_arguments()

    scraper = StravaScraper(email, password)
    scraper.start_browser()

    try:
        members_list = scrape_club_members(scraper, args.club_id)
        all_activity_df = scrape_athlete_activities(scraper, members_list)

        if not all_activity_df.empty:
            save_weekly_activity_data(all_activity_df)
    finally:
        scraper.close_browser()

    if args.score:
        calculate_score()


if __name__ == "__main__":
    main()
