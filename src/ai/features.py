"""
Извличане на характеристики за AI прогноза
"""
from database.db import execute_query
from services.standings_service import get_standings
import re


def get_team_recent_form(team_name, num_matches=5):
    """
    Изчислява формата на отбор от последните N мача

    Връща: {
        'points': int,  # точки от последните N мача
        'gf': int,      # вкарани голове
        'ga': int,      # допуснати голове
        'played': int,  # изиграни мачове
        'wins': int,
        'draws': int,
        'losses': int,
        'form_percentage': float  # 0-1
    }
    """
    # Намираме club_id
    club = execute_query(
        "SELECT club_id FROM clubs WHERE name = ?",
        (team_name,),
        fetch=True
    )
    if not club:
        return None

    club_id = club[0][0]

    # Вземаме последните N мача като домакин или гост
    query = """
        SELECT m.home_club_id, m.away_club_id, m.home_goals, m.away_goals, m.status
        FROM matches m
        WHERE (m.home_club_id = ? OR m.away_club_id = ?)
        AND m.status = 'played'
        AND m.home_goals IS NOT NULL 
        AND m.away_goals IS NOT NULL
        ORDER BY m.match_date DESC, m.match_id DESC
        LIMIT ?
    """

    matches = execute_query(query, (club_id, club_id, num_matches), fetch=True)

    if not matches or len(matches) < 3:
        return None

    stats = {
        'points': 0,
        'gf': 0,
        'ga': 0,
        'played': 0,
        'wins': 0,
        'draws': 0,
        'losses': 0,
        'form_percentage': 0.0
    }

    for match in matches:
        home_id, away_id, home_goals, away_goals, status = match

        # Пропускаме мачове без резултат
        if home_goals is None or away_goals is None:
            continue

        stats['played'] += 1
        is_home = (home_id == club_id)

        if is_home:
            stats['gf'] += home_goals
            stats['ga'] += away_goals
            if home_goals > away_goals:
                stats['wins'] += 1
                stats['points'] += 3
            elif home_goals == away_goals:
                stats['draws'] += 1
                stats['points'] += 1
            else:
                stats['losses'] += 1
        else:
            stats['gf'] += away_goals
            stats['ga'] += home_goals
            if away_goals > home_goals:
                stats['wins'] += 1
                stats['points'] += 3
            elif away_goals == home_goals:
                stats['draws'] += 1
                stats['points'] += 1
            else:
                stats['losses'] += 1

    # Изчисляваме процент форма (точки от максимално възможните)
    if stats['played'] > 0:
        stats['form_percentage'] = stats['points'] / (stats['played'] * 3)

    return stats


def get_team_league_and_standings(team_name):
    """
    Намира в коя лига играе отборът и текущото му класиране
    """
    # Намираме club_id
    club = execute_query(
        "SELECT club_id FROM clubs WHERE name = ?",
        (team_name,),
        fetch=True
    )
    if not club:
        return None

    club_id = club[0][0]

    # Намираме лигата на отбора
    league = execute_query(
        """
        SELECT l.league_id, l.name, l.season
        FROM leagues l
        JOIN league_teams lt ON l.league_id = lt.league_id
        WHERE lt.club_id = ?
        ORDER BY l.created_at DESC
        LIMIT 1
        """,
        (club_id,),
        fetch=True
    )

    if not league:
        return None

    league_id, league_name, season = league[0]

    # Изчисляваме класиране
    standings_result = get_standings(league_name, season)
    if isinstance(standings_result, str) and "грешка" in standings_result.lower():
        return {
            'league_name': league_name,
            'season': season,
            'position': None,
            'total_teams': None,
            'position_percentage': 0.5  # средата
        }

    # Парсваме класирането за да намерим позицията на отбора
    # Това е опростено - в реална имплементация бихме използвали директна заявка
    lines = standings_result.split('\n')
    position = None
    total_teams = 0

    for line in lines:
        # Търсим редове с отбори (съдържат номерация)
        if re.match(r'^\s*\d+\s+', line):
            parts = re.split(r'\s{2,}', line.strip())
            if len(parts) >= 2:
                try:
                    pos = int(parts[0])
                    name = parts[1]
                    if name.strip() == team_name:
                        position = pos
                except ValueError:
                    continue
                total_teams += 1

    if position is None:
        position_percentage = 0.5
    else:
        position_percentage = 1 - (position / total_teams) if total_teams > 0 else 0.5

    return {
        'league_name': league_name,
        'season': season,
        'position': position,
        'total_teams': total_teams,
        'position_percentage': position_percentage
    }


def extract_features(home_team, away_team):
    """
    Извлича всички характеристики за два отбора
    """
    # 1. Форма на отборите
    home_form = get_team_recent_form(home_team)
    away_form = get_team_recent_form(away_team)

    if not home_form or not away_form:
        return None, "Недостатъчно данни за един от отборите (минимум 3 мача)"

    # 2. Класиране
    home_standings = get_team_league_and_standings(home_team)
    away_standings = get_team_league_and_standings(away_team)

    # 3. Извличане на ключови показатели
    features = {
        # Атакуваща сила (средно голове на мач)
        'home_attack': home_form['gf'] / home_form['played'] if home_form['played'] > 0 else 0,
        'away_attack': away_form['gf'] / away_form['played'] if away_form['played'] > 0 else 0,

        # Защитна сила (средно допуснати голове на мач)
        'home_defense': home_form['ga'] / home_form['played'] if home_form['played'] > 0 else 0,
        'away_defense': away_form['ga'] / away_form['played'] if away_form['played'] > 0 else 0,

        # Форма (процент точки)
        'home_form': home_form['form_percentage'],
        'away_form': away_form['form_percentage'],

        # Класиране
        'home_position': home_standings['position_percentage'] if home_standings else 0.5,
        'away_position': away_standings['position_percentage'] if away_standings else 0.5,

        # Бонус домакин (20% предимство)
        'home_advantage': 1.2
    }

    return features, None


def calculate_match_probabilities(features):
    """
    Изчислява вероятности за изход на мач въз основа на характеристиките
    """
    # Извличаме показателите
    home_attack = features['home_attack']
    away_attack = features['away_attack']
    home_defense = features['home_defense']
    away_defense = features['away_defense']
    home_form = features['home_form']
    away_form = features['away_form']
    home_position = features['home_position']
    away_position = features['away_position']
    home_advantage = features['home_advantage']

    # Изчисляваме очаквани голове (Expected Goals)
    # Базова формула: (атака * защита на противника) / средна стойност

    # Средни стойности за лигата (приблизителни)
    avg_goals_per_match = 2.5
    avg_attack = 1.25
    avg_defense = 1.25

    # Очаквани голове за домакин
    home_xg = (home_attack / avg_attack) * (away_defense / avg_defense) * (avg_goals_per_match / 2) * home_advantage
    # Очаквани голове за гост
    away_xg = (away_attack / avg_attack) * (home_defense / avg_defense) * (avg_goals_per_match / 2)

    # Коригираме с форма и класиране
    form_factor = home_form - away_form
    position_factor = home_position - away_position

    home_xg = home_xg * (1 + form_factor * 0.2 + position_factor * 0.1)
    away_xg = away_xg * (1 - form_factor * 0.2 - position_factor * 0.1)

    # Не позволяваме отрицателни стойности
    home_xg = max(0.1, home_xg)
    away_xg = max(0.1, away_xg)

    # Изчисляваме вероятности по Пуасоново разпределение (опростено)
    # За опростяване използваме проста нормализация на очакваните голове

    total_goals = home_xg + away_xg

    # Вероятност домакин да спечели: пропорционална на очакваните голове
    # с бонус за домакин
    home_win_prob = (home_xg / total_goals) * 1.1

    # Вероятност гост да спечели
    away_win_prob = (away_xg / total_goals) * 0.9

    # Вероятност за равен (по-висока когато отборите са равни)
    diff = abs(home_xg - away_xg) / (home_xg + away_xg + 0.1)
    draw_prob = 0.25 * (1 - diff) + 0.05  # между 5% и 30%

    # Нормализираме до 100%
    total = home_win_prob + away_win_prob + draw_prob
    home_win_prob = (home_win_prob / total) * 100
    away_win_prob = (away_win_prob / total) * 100
    draw_prob = (draw_prob / total) * 100

    return {
        'home_win': round(home_win_prob, 1),
        'draw': round(draw_prob, 1),
        'away_win': round(away_win_prob, 1)
    }