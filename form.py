
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

        summary = f"<br><div style='font-weight:bold; font-size:20px'>{date} – {team_name} vs {opponent} {result_icon} | MS: {home_goals}-{away_goals}</div>"

        goal_info = ""
        team_goals_list = get_team_goals(events, home_name)
        opp_goals_list = get_team_goals(events, away_name)

        if team_goals_list:
            goal_info += f"<div><strong>🥅 {home_name}:</strong><br>" + "<br>".join(team_goals_list) + "</div>"
        if opp_goals_list:
            goal_info += f"<div><strong>🥅 {away_name}:</strong><br>" + "<br>".join(opp_goals_list) + "</div>"

        full_html = summary + goal_info
        result.append(full_html)

    return result

def get_form_score(fixtures, team_name, max_matches=5):
    score = 0
    count = 0

    played_matches = [
        f for f in fixtures
        if f['goals']['home'] is not None and f['goals']['away'] is not None
        and (f['teams']['home']['name'] == team_name or f['teams']['away']['name'] == team_name)
    ]

    sorted_matches = sorted(played_matches, key=lambda x: x['fixture']['date'], reverse=True)[:max_matches]

    for match in sorted_matches:
        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        home_goals = match['goals']['home']
        away_goals = match['goals']['away']

        if team_name == home:
            team_goals = home_goals
            opp_goals = away_goals
        else:
            team_goals = away_goals
            opp_goals = home_goals

        if team_goals > opp_goals:
            score += 3
        elif team_goals == opp_goals:
            score += 1

        count += 1

    return score / count if count else 0

def get_first_half_form_score(fixtures, team_name, max_matches=5):
    score = 0
    count = 0

    played_matches = [
        f for f in fixtures
        if f['goals']['home'] is not None and f['goals']['away'] is not None
        and (f['teams']['home']['name'] == team_name or f['teams']['away']['name'] == team_name)
    ]

    sorted_matches = sorted(played_matches, key=lambda x: x['fixture']['date'], reverse=True)[:max_matches]

    for match in sorted_matches:
        fixture_id = match['fixture']['id']
        events = get_fixture_events(fixture_id)

        home = match['teams']['home']['name']
        away = match['teams']['away']['name']

        home_iy = len([e for e in events if e.get('type') == 'Goal' and e.get('team', {}).get('name') == home and e.get('time', {}).get('elapsed', 46) < 46])
        away_iy = len([e for e in events if e.get('type') == 'Goal' and e.get('team', {}).get('name') == away and e.get('time', {}).get('elapsed', 46) < 46])

        if team_name == home:
            team_iy = home_iy
            opp_iy = away_iy
        else:
            team_iy = away_iy
            opp_iy = home_iy

        if team_iy > opp_iy:
            score += 3
        elif team_iy == opp_iy:
            score += 1

        count += 1

    return score / count if count else 0


def get_avg_goals_last_matches(fixtures, team_name, max_matches=5):
    total_goals = 0
    count = 0

    played_matches = [
        f for f in fixtures
        if f['goals']['home'] is not None and f['goals']['away'] is not None
        and (f['teams']['home']['name'] == team_name or f['teams']['away']['name'] == team_name)
    ]

    sorted_matches = sorted(played_matches, key=lambda x: x['fixture']['date'], reverse=True)[:max_matches]

    for match in sorted_matches:
        total = match['goals']['home'] + match['goals']['away']
        total_goals += total
        count += 1

    return total_goals / count if count > 0 else 0

def get_team_avg_goals(fixtures, team_name, max_matches=5):
    total_scored = 0
    total_goals = 0
    count = 0

    played_matches = [
        f for f in fixtures
        if f['goals']['home'] is not None and f['goals']['away'] is not None
        and (f['teams']['home']['name'] == team_name or f['teams']['away']['name'] == team_name)
    ]

    sorted_matches = sorted(played_matches, key=lambda x: x['fixture']['date'], reverse=True)[:max_matches]

    for match in sorted_matches:
        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        home_goals = match['goals']['home']
        away_goals = match['goals']['away']

        if team_name == home:
            scored = home_goals
        else:
            scored = away_goals

        total_scored += scored
        total_goals += home_goals + away_goals
        count += 1

    return (
        total_scored / count if count else 0,
        total_goals / count if count else 0
    )

def get_btts_ratio(fixtures, team_name, max_matches=5):
    count = 0
    btts = 0

    played_matches = [
        f for f in fixtures
        if f['goals']['home'] is not None and f['goals']['away'] is not None
        and (f['teams']['home']['name'] == team_name or f['teams']['away']['name'] == team_name)
    ]

    sorted_matches = sorted(played_matches, key=lambda x: x['fixture']['date'], reverse=True)[:max_matches]

    for match in sorted_matches:
        home_goals = match['goals']['home']
        away_goals = match['goals']['away']
        if home_goals > 0 and away_goals > 0:
            btts += 1
        count += 1

    return btts / count if count > 0 else 0
