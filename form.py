from collections import defaultdict

def get_goal_minutes(events, team_name):
    if not events:
        return []
    return [e['time']['minute'] for e in events if e.get('type') == 'Goal' and e.get('team', {}).get('name') == team_name]

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

        # Sonuç simgesi
        if team_goals > opp_goals:
            result_icon = "✅"
        elif team_goals < opp_goals:
            result_icon = "❌"
        else:
            result_icon = "🤝"

        # Başlık satırı
        summary = f"**{date} – {team_name} vs {opponent}** {result_icon} | MS: {team_goals}-{opp_goals}"

        # Gol dakikaları
        team_goals_min = get_goal_minutes(events, team_name)
        opp_goals_min = get_goal_minutes(events, opponent)
        if team_goals_min:
            summary += f"\n🥅 {team_name}: " + ', '.join([str(g) + "'" for g in team_goals_min])
        if opp_goals_min:
            summary += f"\n🥅 {opponent}: " + ', '.join([str(g) + "'" for g in opp_goals_min])

        result.append(summary)

    return result
