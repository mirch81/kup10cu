
from collections import defaultdict

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
        home = match['teams']['home']
        away = match['teams']['away']
        home_name = home['name']
        away_name = away['name']
        home_goals = match['goals']['home']
        away_goals = match['goals']['away']
        date = match['fixture']['date'][:10]
        events = match.get('events', [])

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

        # İlk yarı skoru hesapla (event'lerden)
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
