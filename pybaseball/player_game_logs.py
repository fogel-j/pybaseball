import pandas as pd
from bs4 import BeautifulSoup

from . import cache
from .datasources.bref import BRefSession

session = BRefSession()

_URL = "https://www.baseball-reference.com/players/gl.fcgi?id={}&t={}&year={}"

def get_table(season: int, player_id: str, log_type: str) -> pd.DataFrame:
    if log_type == "batting":
        t_param = 'b'
    elif log_type == "pitching":
        t_param = 'p'
    elif log_type == "fielding":
        t_param = 'f'
    content = session.get(_URL.format(player_id, t_param, season)).content
    soup = BeautifulSoup(content, "lxml")
    table_id = "{}_gamelogs".format(log_type)
    table = soup.find("table", attrs=dict(id=table_id))
    if table is None:
        raise RuntimeError("Table with expected id not found on scraped page.")
    data = pd.read_html(str(table))[0]
    return data


def postprocess(data: pd.DataFrame) -> pd.DataFrame:
    data.drop("Rk", axis=1, inplace=True)  # drop index column
    repl_dict = {
        "Gtm": "Game",
        "Unnamed: 5": "Home"
    }
    data.rename(repl_dict, axis=1, inplace=True)
    data.drop(data.tail(1).index, inplace=True)
    data["Home"] = data["Home"].isnull()  # '@' if away, empty if home
    data = data[data["Game"].str.match(r"\d+")]  # drop empty month rows
    split_data = data['Rslt'].str.split(',', expand=True)
    data.loc[:, 'W/L'] = split_data[0]
    data.loc[:, 'Score'] = split_data[1] # Splitting the Rslt column to two -> W/L , Score
    data.drop(columns=['Rslt', 'Game', 'Gcar'], inplace=True)  
    data = data.apply(pd.to_numeric, errors="ignore")
    # data["Game"] = data["Game"].astype(int)
    return data.reset_index(drop=True)


@cache.df_cache()
def player_game_logs(season: int, player_id: str, log_type: str) -> pd.DataFrame:
    """
    Get Baseball Reference batting or pitching game logs for a team-season.

    :param season: year of logs
    :param player_id: baseball-reference player id
    :param log_type: "batting" , "pitching" or "fielding"
    :return: pandas.DataFrame of game logs
    """
    if log_type not in ("batting", "pitching", "fielding"):
        raise ValueError("`log_type` must be either 'batting', 'pitching' or 'fielding'.")
    data = get_table(season, player_id, log_type)
    data = postprocess(data)
    return data