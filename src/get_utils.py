from datetime import datetime, timedelta


def get_msg_log(step: str, msg_type: str, athlete: int, activity: str = None) -> str:
    """Função para retornar uma mensagem de log

    Args:
        step (str): Step do scraping
        msg_type (str): tipo da mensagem, 'info' ou 'error'
        athlete (int): ID do atleta
        activity (str, optional): ID da atividade. Defaults to None.

    Returns:
        str: Mensagem de log
    """
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
    """Função para retornar uma lista com os números das semanas

    Args:
        num_weeks (int): Número de semanas a serem retornadas

    Returns:
        list: Lista com os números das semanas no formato 'YYYYWW'
    """
    today = datetime.today()
    weeks = []

    for i in range(num_weeks):
        week_date = today - timedelta(weeks=i)
        year, week, _ = week_date.isocalendar()
        weeks.append(int(f'{year}{week:02d}'))

    return weeks


def parse_time(time_str: str) -> str:
    """Função para converter uma string de tempo para o formato correto

    Args:
        time_str (str): String de tempo no formato 'HH:MM:SS' ou 'MM:SS'

    Raises:
        ValueError: Se o formato da string de tempo for inválido

    Returns:
        str: String de tempo no formato 'HH:MM:SS'
    """

    time_parts = time_str.split(':')

    # 'MM:SS'
    if len(time_parts) == 2:
        hours = 0
        minutes = int(time_parts[0])
        seconds = int(time_parts[1])
    # 'HH:MM:SS'
    elif len(time_parts) == 3:
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = int(time_parts[2])
    else:
        raise ValueError('Formato de tempo inválido')
    return f'{hours:02}:{minutes:02}:{seconds:02}'


def parse_datetime(activity_time: str) -> datetime:
    """Função para converter uma string de tempo para um objeto datetime

    Args:
        activity_time (str): String de tempo no formato 'HH:MM AM/PM on Weekday, Month Day, Year' ou 'Weekday, Month Day, Year'
        Exemplo: '7:18 PM on Tuesday, January 21, 2025' ou 'Friday, January 10, 2025'

    Raises:
        ValueError: Se o formato da string de tempo for inválido

    Returns:
        datetime: Objeto datetime com a data e hora da atividade
    """

    formats = [
        '%I:%M %p on %A, %B %d, %Y',  # Ex: '7:18 PM on Tuesday, January 21, 2025'
        '%A, %B %d, %Y',  # Ex: 'Friday, January 10, 2025'
    ]

    for fmt in formats:
        try:
            return datetime.strptime(activity_time.strip(), fmt)
        except ValueError:
            pass
    raise ValueError(f"Formato desconhecido: {activity_time}")
