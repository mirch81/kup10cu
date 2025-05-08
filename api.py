
import requests
from config import BASE_URL, HEADERS
from datetime import datetime

# Lig ID'leri
SUPPORTED_LEAGUES = {
    "Premier League": 39,
    "La Liga": 140,
    "Bundesliga": 78,
    "Serie A": 135,
    "Ligue 1": 61,
    "Süper Lig": 203,
    "Şampiyonlar Ligi": 2,
    "Avrupa Ligi": 3,
    "Konferans Ligi": 848
}

def get_fixtures(league_name, year, month=None, status_filter="all"):
    league_id = SUPPORTED_LEAGUES.get(league_name)
    if not league_id:
        return []

    today = datetime.today()
    current_year = today.year
    current_month = today.month

    if current_month < 7:
        season_guess = current_year - 1
    else:
        season_guess = current_year

    if league_id in [2, 3, 848]:
        season = season_guess
    else:
        season = year - 1

    url = f"{BASE_URL}/fixtures"
    params = {
        "league": league_id,
        "season": season
    }

    if month:
        start_date = f"{season}-{str(month).zfill(2)}-01"
        if int(month) == 12:
            end_date = f"{season+1}-01-01"
        else:
            end_date = f"{season}-{str(int(month)+1).zfill(2)}-01"
        params["from"] = start_date
        params["to"] = end_date

    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    fixtures = data.get("response", [])
    if status_filter == "played":
        fixtures = [f for f in fixtures if f["fixture"]["status"]["short"] in ["FT", "AET", "PEN"]]
    elif status_filter == "upcoming":
        fixtures = [f for f in fixtures if f["fixture"]["status"]["short"] == "NS"]

    return fixtures

def get_fixture_events(fixture_id):
    url = f"{BASE_URL}/fixtures/events"
    params = {"fixture": fixture_id}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    return data.get("response", [])

def get_standings(league_name, year):
    league_id = SUPPORTED_LEAGUES.get(league_name)

    today = datetime.today()
    current_year = today.year
    current_month = today.month

    if current_month < 7:
        season_guess = current_year - 1
    else:
        season_guess = current_year

    if league_id in [2, 3, 848]:
        season = season_guess
    else:
        season = year - 1

    url = f"{BASE_URL}/standings"
    params = {"league": league_id, "season": season}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    return data.get("response", [])
