import requests
from datetime import datetime
from config import BASE_URL, HEADERS

import streamlit as st
st.title("⚽ Tahmin Asistanı Başladı!")


# Desteklenen ligler ve API ID'leri
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

def get_fixtures(league_name, year, month, status_filter="all"):
    league_id = SUPPORTED_LEAGUES.get(league_name)
    if not league_id:
        return []

    # Başlangıç ve bitiş tarihi ayarla
    start_date = f"{year}-{str(month).zfill(2)}-01"
    if int(month) == 12:
        end_date = f"{int(year)+1}-01-01"
    else:
        end_date = f"{year}-{str(int(month)+1).zfill(2)}-01"

    url = f"{BASE_URL}/fixtures"
    params = {
        "league": league_id,
        "season": year,
        "from": start_date,
        "to": end_date
    }

    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    # Oynanmış / oynanmamış filtreleme
    fixtures = data.get("response", [])
    if status_filter == "played":
        fixtures = [f for f in fixtures if f["fixture"]["status"]["short"] in ["FT", "AET", "PEN"]]
    elif status_filter == "upcoming":
        fixtures = [f for f in fixtures if f["fixture"]["status"]["short"] == "NS"]

    return fixtures

from elo import calculate_elo_history
import pandas as pd
import streamlit as st

# Seçilen maçtan takımları al
if selected_fixture:
    team_home = selected_fixture["teams"]["home"]["name"]
    team_away = selected_fixture["teams"]["away"]["name"]
    league_id = selected_fixture["league"]["id"]

    # Elo geçmişini hesapla
    history, _ = calculate_elo_history(fixtures, selected_league_id=league_id)

    # Seçilen iki takımın geçmişini çıkar
    team_home_history = history.get(team_home, [])
    team_away_history = history.get(team_away, [])

    # Veriyi DataFrame’e çevir
    df_home = pd.DataFrame(team_home_history, columns=["date", team_home])
    df_away = pd.DataFrame(team_away_history, columns=["date", team_away])

    # Tarihe göre birleştir
    df_elo = pd.merge(df_home, df_away, on="date", how="outer").sort_values("date")
    df_elo.set_index("date", inplace=True)

    # Grafik göster
    st.subheader("📊 Elo Puan Grafiği")
    st.line_chart(df_elo)
