from datetime import datetime, timedelta


def get_msg_log(step: str, msg_type: str, athlete: int, activity: str = None) -> str:
    activity = f"[{activity}]" if activity else ""
    messages = {
        "start": {
            "info": "Iniciando o scraping...",
            "error": "Erro ao iniciar o scraping.",
        },
        "login": {
            "info": "Realizando login...",
            "error": "Erro ao realizar login.",
        },
        "members": {
            "info": "Coletando membros do clube...",
            "error": "Erro ao coletar membros do clube.",
        },
        "activities": {
            "info": "Coletando atividades...",
            "error": "Erro ao coletar atividades.",
        },
        "activity": {
            "info": "Coletando dados da atividade...",
            "error": "Erro ao coletar dados da atividade.",
        },
    }
    message = f"{athlete}: {activity} " + messages[step][msg_type]
    return message


def get_week(num_weeks: int) -> list:
    today = datetime.today()
    weeks = []

    for i in range(num_weeks):
        week_date = today - timedelta(weeks=i)
        year, week, _ = week_date.isocalendar()
        weeks.append(int(f"{year}{week:02d}"))

    return weeks


def parse_time(time_str) -> str:
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


def parse_datetime(activity_time):
    formats = [
        "%I:%M %p on %A, %B %d, %Y",  # Exemplo: "7:18 PM on Tuesday, January 21, 2025"
        "%A, %B %d, %Y"                # Exemplo: "Friday, January 10, 2025"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(activity_time.strip(), fmt)
        except ValueError:
            pass
    raise ValueError(f"Formato desconhecido: {activity_time}")
