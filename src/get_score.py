import pandas as pd


class Scorer:
    def __init__(
        self,
        df: pd.DataFrame,
        col_time: list = ["moving_time", "elapsed_time", "duration"],
    ):
        self.df = df.copy()
        self.col_time = col_time
        self.columns = ["athlete_id", "date_time", "raised_points", "points"]

    def _points_for_activity_duration(self, value_per_minute: int = 1) -> pd.DataFrame:
        """Calcula os pontos baseado na duração da atividade em minutos.

        Args:
            value_per_minute (int, optional): Valor por minuto de atividade. Padrão é 1.

        Returns:
            pd.DataFrame: DataFrame com os pontos calculados.
        """
        df = self.df.copy()
        df["time"] = df[self.col_time].bfill(axis=1).iloc[:, 0]
        df["activity_minutes"] = df["time"].dt.total_seconds() // 60
        df["points"] = df["activity_minutes"] * value_per_minute
        df["raised_points"] = "Atividade " + df["link"].astype(str)

        return df[self.columns].dropna(how="all", axis=1)

    def _points_for_activity_frequency(
        self, rule: dict = {1: 1, 2: 1.2, 3: 1.3, 4: 1.4, 5: 1.5, 6: 1.5, 7: 1.5}
    ) -> pd.DataFrame:
        """Calcula os pontos baseado na frequência de atividades na semana.

        Args:
            rule (dict, optional): Dicionário com a regra de multiplicação dos pontos.
            Padrão é {1: 1, 2: 1.2, 3: 1.3, 4: 1.4, 5: 1.5, 6: 1.5, 7: 1.5}.

        Returns:
            pd.DataFrame: DataFrame com os pontos calculados.
        """
        df = (
            self.df.groupby(["athlete_id", "week"])
            .agg(
                days=("date", "nunique"),
                points_old=("points", "sum"),
                date_time=("date_time", "max"),
            )
            .reset_index()
        )

        df["rule"] = (
            df["days"].map(rule).fillna(1)
        )
        df["points"] = df["points_old"] * (df["rule"] - 1)
        df["date_time"] = df["date_time"].dt.normalize()
        df["raised_points"] = df.apply(
            lambda x: f"Pontos multiplicados pela regra {x['rule']} na semana {x['week']}, com {x['days']} dias ativos",
            axis=1,
        )

        return df[self.columns]

    def _points_for_events(self, value_per_event: int = 100, dates: list = None) -> pd.DataFrame:
        """Calcula os pontos baseado em eventos específicos.

        Args:
            value_per_event (int, optional): Valor por evento. Padrão é 100.
            dates (list, optional): Lista com as datas dos eventos. Padrão são os últimos dias para cada mês.

        Returns:
            pd.DataFrame: DataFrame com os pontos calculados.
        """
        df = self.df.copy()
        if dates is None:
            event_dates = pd.date_range(
                start=pd.Timestamp.today().replace(month=1, day=1), periods=12, freq="ME"
            ).strftime("%Y-%m-%d")
        else:
            event_dates = dates

        df = df[df["date"].isin(event_dates)]
        df["date_time"] = df["date_time"].dt.normalize()
        df["points"] = value_per_event
        df["raised_points"] = "Evento bônus no dia " + df["date"].astype(str)

        return df[self.columns]

    def score(self) -> pd.DataFrame:
        """Calcula a pontuação total dos atletas.

        Returns:
            pd.DataFrame: DataFrame com a pontuação total dos atletas.
        """
        score_duration = self._points_for_activity_duration()
        score_frequency = self._points_for_activity_frequency()
        score_events = self._points_for_events()

        return pd.concat(
            [score_duration, score_frequency, score_events], ignore_index=True
        )
