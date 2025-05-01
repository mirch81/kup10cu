
import requests
from config import BASE_URL, HEADERS
import streamlit as st

@st.cache_data(show_spinner=False)
def load_match_with_events(fixture_id):
    url = f"{BASE_URL}/fixtures"
    params = {"id": fixture_id}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    if data.get("response"):
        return data["response"][0]
    return None

def get_goal_minutes(events, team_name):
    return [e['time']['minute'] for e in events if e['type'] == 'Goal' and e['team']['name'] == team_name]

def get_team_last_matches(fixtures, team_name, max_matches=5):
    result = []

    played_matches = [
        f for f in fixtures
        if f['goals']['home'] is not None and f['goals']['away'] is not None
        and (f['teams']['home']['name'] == team_name or f['teams']['away']['name'] == team_name)
    ]

    sorted_matches = sorted(played_matches, key=lambda x: x['fixture']['date'], reverse=True)[:max_matches]

    for match in sorted(sorted_matches, key=lambda x: x['fixture']['date']):
        match_detail = load_match_with_events(match['fixture']['id'])
        if not match_detail:
            continue

        home = match_detail['teams']['home']
        away = match_detail['teams']['away']
        home_name = home['name']
        away_name = away['name']
        home_goals = match_detail['goals']['home']
        away_goals = match_detail['goals']['away']
        events = match_detail.get('events', [])
        date = match_detail['fixture']['date'][:10]

        if team_name == home_name:
            opponent = away_name
            team_goals = home_goals
            opp_goals = away_goals
        else:
            opponent = home_name
            team_goals = away_goals
            opp_goals = home_goals

        # Maç sonucu simgesi
        if team_goals > opp_goals:
            result_icon = "✅"
        elif team_goals < opp_goals:
            result_icon = "❌"
        else:
            result_icon = "🤝"

        # İlk yarı skoru event'lerden hesapla
        team_first_half_goals = len([e for e in events if e['type'] == 'Goal' and e['team']['name'] == team_name and e['time']['elapsed'] <= 45])
        opp_first_half_goals = len([e for e in events if e['type'] == 'Goal' and e['team']['name'] == opponent and e['time']['elapsed'] <= 45])

        summary = f"{date} – vs {opponent} {result_icon}"
        summary += f"\nİY: {team_first_half_goals}-{opp_first_half_goals} / MS: {team_goals}-{opp_goals}"

        team_goals_min = get_goal_minutes(events, team_name)
        opp_goals_min = get_goal_minutes(events, opponent)
        if team_goals_min:
            summary += f"\n🥅 {team_name}: " + ', '.join(str(g) + "'" for g in team_goals_min)
        if opp_goals_min:
            summary += f"\n🥅 {opponent}: " + ', '.join(str(g) + "'" for g in opp_goals_min)

        result.append(summary)

    return result
