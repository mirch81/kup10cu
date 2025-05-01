
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from api import get_fixtures, SUPPORTED_LEAGUES, get_standings
from elo import calculate_elo_history
from form import get_team_last_matches, get_form_score, get_first_half_form_score, get_avg_goals_last_matches, get_team_avg_goals, get_btts_ratio

st.set_page_config(page_title="Futbol Tahmin Asistanı", layout="wide")
st.title("⚽ Futbol Tahmin Asistanı")

league_name = st.selectbox("Lig seçin", list(SUPPORTED_LEAGUES.keys()))
year = st.selectbox("Yıl seçin", list(range(2020, 2026))[::-1])
month = st.selectbox("Ay seçin", list(range(1, 13)))
status_filter = st.selectbox("Maç durumu", ["all", "played", "upcoming"])

all_fixtures = get_fixtures(league_name, year, status_filter="all")
monthly_fixtures = get_fixtures(league_name, year, month, status_filter)


standings = get_standings(league_name, year)
if standings:
    table = standings[0]['league']['standings'][0]
    df_standings = pd.DataFrame([{
        "Takım": team['team']['name'],
        "G": team['all']['win'],
        "B": team['all']['draw'],
        "M": team['all']['lose'],
        "AV": team['goalsDiff'],
        "P": team['points']
    } for team in table])

    st.subheader("📋 Lig Puan Durumu")
    st.dataframe(df_standings)

if monthly_fixtures:
    match_options = [
        f"{f['teams']['home']['name']} vs {f['teams']['away']['name']} - {f['fixture']['date'][:10]}"
        for f in monthly_fixtures
    ]
    selected_match = st.selectbox("Maç seçin", match_options)
    selected_fixture = monthly_fixtures[match_options.index(selected_match)]

    team_home = selected_fixture["teams"]["home"]["name"]
    team_away = selected_fixture["teams"]["away"]["name"]
    league_id = selected_fixture["league"]["id"]

    history, _ = calculate_elo_history(all_fixtures, selected_league_id=league_id)
    team_home_history = history.get(team_home, [])
    team_away_history = history.get(team_away, [])

    df_home = pd.DataFrame(team_home_history, columns=["date", team_home])
    df_away = pd.DataFrame(team_away_history, columns=["date", team_away])

    df_elo = pd.merge(df_home, df_away, on="date", how="outer").sort_values("date")
    df_elo.set_index("date", inplace=True)
    df_elo.ffill(inplace=True)

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

    # Tahmin motoru - Maç Sonucu
    form_home = get_form_score(all_fixtures, team_home)
    form_away = get_form_score(all_fixtures, team_away)

    elo_home = team_home_history[-1][1] if team_home_history else 1500
    elo_away = team_away_history[-1][1] if team_away_history else 1500

    form_weight = 10

    tahmin_skor_home = elo_home + form_home * form_weight
    tahmin_skor_away = elo_away + form_away * form_weight

    iy_home = get_first_half_form_score(all_fixtures, team_home)
    iy_away = get_first_half_form_score(all_fixtures, team_away)
    iy_weight = 10

    iy_score_home = elo_home + iy_home * iy_weight
    iy_score_away = elo_away + iy_away * iy_weight

    st.subheader("🔮 Tahminler")

    with st.container():
        st.markdown(f"""
        **Maç Sonucu Tahmini:**  
        {team_home} Elo ve Son 5 Maç Sonucu Skor: `{tahmin_skor_home:.1f}`  
        {team_away} Elo ve Son 5 Maç Sonucu Skor: `{tahmin_skor_away:.1f}`
        """)
        if tahmin_skor_home > tahmin_skor_away:
            st.markdown(f"➡️ Tahmin: **{team_home} kazanır**")
        elif tahmin_skor_home < tahmin_skor_away:
            st.markdown(f"➡️ Tahmin: **{team_away} kazanır**")
        else:
                st.markdown("➡️ Tahmin: **Beraberlik**")

        st.markdown("---")

        st.markdown(f"""
        **İlk Yarı Sonucu Tahmini:**  
        {team_home} Skor: `{iy_score_home:.1f}`  
        {team_away} Skor: `{iy_score_away:.1f}`
        """)

        if iy_score_home > iy_score_away:
            st.markdown(f"➡️ Tahmin: **{team_home} ilk yarıyı önde kapatır**")
        elif iy_score_home < iy_score_away:
            st.markdown(f"➡️ Tahmin: **{team_away} ilk yarıyı önde kapatır**")
        else:
                st.markdown("➡️ Tahmin: **İlk yarı berabere**")
        st.markdown("---")

        gol_home, mac_home = get_team_avg_goals(all_fixtures, team_home)
        gol_away, mac_away = get_team_avg_goals(all_fixtures, team_away)
        match_avg = (mac_home + mac_away) / 2

        st.markdown(f"""
        **2.5 Alt/Üst Tahmini:**

        {team_home}'ın attığı Gol Ortalaması: `{gol_home:.2f}`  
        {team_home} Maçlarındaki Toplam Gol Ortalaması: `{mac_home:.2f}`  

        {team_away}'ın attığı Gol Ortalaması: `{gol_away:.2f}`  
        {team_away} Maçlarındaki Toplam Gol Ortalaması: `{mac_away:.2f}`  

        **Maç Ortalama:** `{match_avg:.2f}`
        """)
        st.markdown("---")

        kg_home = get_btts_ratio(all_fixtures, team_home)
        kg_away = get_btts_ratio(all_fixtures, team_away)
        kg_avg = (kg_home + kg_away) / 2

        st.markdown(f"""**Karşılıklı Gol (KG) Tahmini:**
{team_home} Son 5 Maçta KG: `{kg_home * 100:.0f}%`
{team_away} Son 5 Maçta KG: `{kg_away * 100:.0f}%`
Ortalama: `{kg_avg * 100:.0f}%`""")

        if kg_avg > 0.5:
            st.markdown("➡️ Tahmin: **KG VAR**")
        else:
                st.markdown("➡️ Tahmin: **KG YOK**")


        if match_avg > 2.5:
            st.markdown("➡️ Tahmin: **2.5 ÜST**")
        else:
                st.markdown("➡️ Tahmin: **2.5 ALT**")

        st.markdown("---")

        

    # Son 5 maç
    st.subheader("📋 Son 5 Maç – Gol Dakikaları")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### {team_home}")
        summaries = get_team_last_matches(all_fixtures, team_home)
        for line in summaries:
            st.markdown(line, unsafe_allow_html=True)

    with col2:
        st.markdown(f"### {team_away}")
        summaries = get_team_last_matches(all_fixtures, team_away)
        for line in summaries:
            st.markdown(line, unsafe_allow_html=True)
else:
    st.warning("Seçilen filtrelere göre maç bulunamadı.")
