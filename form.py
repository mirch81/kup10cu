from api import get_fixture_events
import streamlit as st
import pandas as pd

def get_team_goals(events, team_name):
    goals = []
    for e in events:
        if e.get('type') == 'Goal' and e.get('team', {}).get('name') == team_name:
            minute = e.get('time', {}).get('elapsed')
            scorer = e.get('player', {}).get('name', 'Bilinmiyor')
            if minute is not None:
                goals.append({"Dakika": f"{minute}'", "Oyuncu": scorer})
    return goals

def get_team_last_matches(fixtures, team_name, max_matches=5):
    result = []

    played_matches = [
        f for f in fixtures
        if f['goals']['home'] is not None and f['goals']['away'] is not None
        and (f['teams']['home']['name'] == team_name or f['teams']['away']['name'] == team_name)
    ]

    sorted_matches = sorted(played_matches, key=lambda x: x['fixture']['date'], reverse=True)[:max_matches]

    for match in sorted(sorted_matches, key=lambda x: x['fixture']['date']):
        fixture_id = match['fixture']['id']
        events = get_fixture_events(fixture_id)

        home = match['teams']['home']
        away = match['teams']['away']
        home_name = home['name']
        away_name = away['name']
        home_goals = match['goals']['home']
        away_goals = match['goals']['away']
        date = match['fixture']['date'][:10]

        if team_name == home_name:
            opponent = away_name
            team_goals = home_goals
            opp_goals = away_goals
        else:
            opponent = home_name
            team_goals = away_goals
            opp_goals = home_goals

        if team_goals > opp_goals:
            result_icon = "✅"
        elif team_goals < opp_goals:
            result_icon = "❌"
        else:
            result_icon = "🤝"

        summary = f"**{date} – {home_name} vs {away_name}** {result_icon} | MS: {home_goals}-{away_goals}"

        team_goals_list = get_team_goals(events, home_name)
        opp_goals_list = get_team_goals(events, away_name)

        df_home = pd.DataFrame(team_goals_list) if team_goals_list else pd.DataFrame(columns=["Dakika", "Oyuncu"])
        df_away = pd.DataFrame(opp_goals_list) if opp_goals_list else pd.DataFrame(columns=["Dakika", "Oyuncu"])

        col1, col2, col3 = st.columns([1.5, 2, 1.5])

        with col1:
            st.markdown(f"#### 🥅 {home_name} Golleri")
            st.table(df_home)

        with col2:
            st.markdown(summary)

        with col3:
            st.markdown(f"#### 🥅 {away_name} Golleri")
            st.table(df_away)

        result.append(summary)

    return result
