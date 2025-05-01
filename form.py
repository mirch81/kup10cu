from api import get_fixture_events

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

        result_icon = "✅" if team_goals > opp_goals else "❌" if team_goals < opp_goals else "🤝"

        # Bu satır sadece string olarak dönecek, Streamlit'e yazdırmayacak
        summary = f"<div style='font-weight:bold; font-size:20px'>{date} – {team_name} vs {opponent} {result_icon} | MS: {home_goals}-{away_goals}</div>"

        # Gol dakikalarını da append edelim
        goal_info = ""

        team_goals_list = get_team_goals(events, home_name)
        opp_goals_list = get_team_goals(events, away_name)

        if team_goals_list:
            goal_info += f"<div><strong>🥅 {home_name}:</strong><br>" + "<br>".join(team_goals_list) + "</div>"
        if opp_goals_list:
            goal_info += f"<div><strong>🥅 {away_name}:</strong><br>" + "<br>".join(opp_goals_list) + "</div>"

        # Toplam HTML'i ekle
        full_html = summary + goal_info
        result.append(full_html)

    return result
