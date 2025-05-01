
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from api import get_fixtures, SUPPORTED_LEAGUES
from elo import calculate_elo_history

st.set_page_config(page_title="Futbol Tahmin Asistanı", layout="wide")
st.title("⚽ Futbol Tahmin Asistanı")

# 1. Lig seçimi
league_name = st.selectbox("Lig seçin", list(SUPPORTED_LEAGUES.keys()))

# 2. Yıl seçimi
year = st.selectbox("Yıl seçin", list(range(2020, 2026))[::-1])

# 3. Ay seçimi
month = st.selectbox("Ay seçin", list(range(1, 13)))

# 4. Maç durumu seçimi
status_filter = st.selectbox("Maç durumu", ["all", "played", "upcoming"])

# 5. Maçları çek
fixtures = get_fixtures(league_name, year, month, status_filter)

# 6. Maç seçimi
if fixtures:
    match_options = [
        f"{f['teams']['home']['name']} vs {f['teams']['away']['name']} - {f['fixture']['date'][:10]}"
        for f in fixtures
    ]
    selected_match = st.selectbox("Maç seçin", match_options)
    selected_fixture = fixtures[match_options.index(selected_match)]

    # Elo grafiği
    team_home = selected_fixture["teams"]["home"]["name"]
    team_away = selected_fixture["teams"]["away"]["name"]
    league_id = selected_fixture["league"]["id"]

    history, _ = calculate_elo_history(fixtures, selected_league_id=league_id)
    team_home_history = history.get(team_home, [])
    team_away_history = history.get(team_away, [])

    df_home = pd.DataFrame(team_home_history, columns=["date", team_home])
    df_away = pd.DataFrame(team_away_history, columns=["date", team_away])

    df_elo = pd.merge(df_home, df_away, on="date", how="outer").sort_values("date")
    df_elo.set_index("date", inplace=True)

    # Boşlukları kapat: bir takımın puanı yoksa son bilinen değerle doldur
    df_elo.ffill(inplace=True)

    # 📊 Plotly çizgi grafiği
    st.subheader("📊 Elo Puan Grafiği")
    min_val = df_elo.min().min()
    max_val = df_elo.max().max()

    fig = go.Figure()
    for team in df_elo.columns:
        fig.add_trace(go.Scatter(x=df_elo.index, y=df_elo[team], mode='lines+markers', name=team))

    fig.update_layout(
        title="Elo Puan Grafiği",
        xaxis_title="Tarih",
        yaxis_title="Elo Puanı",
        yaxis=dict(range=[min_val - 10, max_val + 10]),
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Seçilen filtrelere göre maç bulunamadı.")
