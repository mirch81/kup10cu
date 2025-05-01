from api import get_fixture_events
import streamlit as st

def get_goal_minutes(events, team_name):
    if not events:
        return []
    goal_minutes = []
    for e in events:
        if e.get('type') == 'Goal' and e.get('team', {}).get('name') == team_name:
            minute = e.get('time', {}).get('minute')
            if minute is not None:
                goal_minutes.append(minute)
    return goal_minutes

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
        if events:
        st.code(events[:3], language="json")  # İlk 3 event'i JSON olarak göster

        st.warning(f"🧪 {match['fixture']['date'][:10]} – {team_name} vs {match['teams']['home']['name']} / {match['teams']['away']['name']} | Fixture ID: {fixture_id} | Events: {len(events)}")

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

        summary = f"**{date} – {team_name} vs {opponent}** {result_icon} | MS: {team_goals}-{opp_goals}"

        team_goals_min = get_goal_minutes(events, team_name)
        opp_goals_min = get_goal_minutes(events, opponent)
        if team_goals_min:
            summary += f"\n🥅 {team_name}: " + ', '.join([str(g) + "'" for g in team_goals_min])
        if opp_goals_min:
            summary += f"\n🥅 {opponent}: " + ', '.join([str(g) + "'" for g in opp_goals_min])

        result.append(summary)

    return result
