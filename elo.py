
from collections import defaultdict
import math

K = 30

EUROPEAN_LEAGUE_IDS = {2, 3, 848}

def expected_score(elo_a, elo_b):
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))

def update_elo(elo_a, elo_b, score_a, score_b):
    expected_a = expected_score(elo_a, elo_b)
    if score_a > score_b:
        actual_a = 1
    elif score_a == score_b:
        actual_a = 0.5
    else:
        actual_a = 0

    change = K * (actual_a - expected_a)
    return elo_a + change, elo_b - change

def calculate_elo_history(fixtures, selected_league_id):
    elo = defaultdict(lambda: 1500)
    history = defaultdict(list)
    initialized = set()

    sorted_fixtures = sorted(fixtures, key=lambda x: x["fixture"]["date"])
    if not sorted_fixtures:
        return history, elo

    for match in sorted_fixtures:
        league_id = match["league"]["id"]
        
        if selected_league_id not in EUROPEAN_LEAGUE_IDS and league_id != selected_league_id:
            continue

        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        home_goals = match["goals"]["home"]
        away_goals = match["goals"]["away"]

        if home_goals is None or away_goals is None:
            continue

        date = match["fixture"]["date"][:10]

        for team in [home, away]:
            if team not in initialized:
                history[team].append((date, 1500))
                initialized.add(team)

        old_home_elo = elo[home]
        old_away_elo = elo[away]
        new_home_elo, new_away_elo = update_elo(old_home_elo, old_away_elo, home_goals, away_goals)

        elo[home] = new_home_elo
        elo[away] = new_away_elo

        history[home].append((date, new_home_elo))
        history[away].append((date, new_away_elo))

    return history, elo
