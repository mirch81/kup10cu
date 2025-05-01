from api import get_fixture_events
import streamlit as st

def get_team_goals(events, team_name):
    goals = []
    for e in events:
        if e.get('type') == 'Goal' and e.get('team', {}).get('name') == team_name:
            minute = e.get('time', {}).get('elapsed')
            scorer = e.get('player', {}).get('name', 'Bilinmiyor')
            if minute is not None:
                goals.append(f"- {minute}' {scorer}")
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

        # Maç ismini 5px daha büyük ve kalın yapıyoruz
        summary = f"<div style='font-weight:bold; font-size:25px'>{date} – {team_name} vs {opponent} {result_icon} | MS: {home_goals}-{away_goals}</div>"
        st.markdown(summary, unsafe_allow_html=True)

        team_goals_list = get_team_goals(events, home_name)
        opp_goals_list = get_team_goals(events, away_name)
        
        # Gol atan takımların isimlerini kalın yapıyoruz
        if team_goals_list:
            st.markdown(f"**🥅 {home_name}:**")
            for g in team_goals_list:
                st.markdown(g)
        if opp_goals_list:
            st.markdown(f"**🥅 {away_name}:**")
            for g in opp_goals_list:
                st.markdown(g)

        result.append(summary)

    return result
