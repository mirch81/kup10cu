
import requests
from config import BASE_URL, HEADERS

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

    # Avrupa kupaları için sezon = yıl, ligler için sezon = yıl - 1
    if league_id in [2, 3, 848]:
        season = year
    else:
        season = year - 1

    url = f"{BASE_URL}/fixtures"
    params = {
        "league": league_id,
        "season": season
    }

    # Eğer ay girildiyse tarih aralığı ekle
    if month:
        start_date = f"{year}-{str(month).zfill(2)}-01"
        if int(month) == 12:
            end_date = f"{int(year)+1}-01-01"
        else:
            end_date = f"{year}-{str(int(month)+1).zfill(2)}-01"
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
