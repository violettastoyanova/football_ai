"""
AI Service - Прогноза на мачове
"""
from ai.features import extract_features, calculate_match_probabilities
from database.db import execute_query


def predict_match(home_team, away_team):
    """
    Прогнозира резултата от мач между два отбора

    Връща: {
        'home_team': str,
        'away_team': str,
        'probabilities': {
            'home_win': float,  # процент
            'draw': float,
            'away_win': float
        },
        'features': dict,  # за дебъг и документация
        'error': str или None
    }
    """

    # 1. Проверка дали отборите съществуват
    home_check = execute_query(
        "SELECT club_id FROM clubs WHERE name = ?",
        (home_team,),
        fetch=True
    )
    if not home_check:
        return {'error': f"Отбор '{home_team}' не съществува."}

    away_check = execute_query(
        "SELECT club_id FROM clubs WHERE name = ?",
        (away_team,),
        fetch=True
    )
    if not away_check:
        return {'error': f"Отбор '{away_team}' не съществува."}

    # 2. Проверка дали са в една лига
    home_club_id = home_check[0][0]
    away_club_id = away_check[0][0]

    # Намираме обща лига
    common_league = execute_query(
        """
        SELECT DISTINCT l.league_id
        FROM league_teams lt
        JOIN leagues l ON lt.league_id = l.league_id
        WHERE lt.club_id IN (?, ?)
        GROUP BY l.league_id
        HAVING COUNT(DISTINCT lt.club_id) = 2
        LIMIT 1
        """,
        (home_club_id, away_club_id),
        fetch=True
    )

    if not common_league:
        return {'error': f"Отборите не са в една лига."}

    # 3. Извличаме характеристики
    features, error = extract_features(home_team, away_team)

    if error:
        return {'error': error}

    if not features:
        return {'error': "Недостатъчно данни за прогноза (минимум 3 мача за всеки отбор)."}

    # 4. Изчисляваме вероятности
    probabilities = calculate_match_probabilities(features)

    # 5. Проверка за валидност
    total = probabilities['home_win'] + probabilities['draw'] + probabilities['away_win']
    if abs(total - 100) > 1:  # Допускаме 1% грешка при закръгляне
        # Нормализираме
        factor = 100 / total
        probabilities['home_win'] = round(probabilities['home_win'] * factor, 1)
        probabilities['draw'] = round(probabilities['draw'] * factor, 1)
        probabilities['away_win'] = round(probabilities['away_win'] * factor, 1)

    return {
        'home_team': home_team,
        'away_team': away_team,
        'probabilities': probabilities,
        'features': features,
        'error': None
    }


def format_prediction_result(result):
    """
    Форматира резултата от прогнозата за показване (без емоджита)
    """
    if result.get('error'):
        return f"Грешка: {result['error']}"

    home = result['home_team']
    away = result['away_team']
    probs = result['probabilities']

    output = f"\n{'=' * 50}\n"
    output += f"ПРОГНОЗА: {home} срещу {away}\n"
    output += f"{'=' * 50}\n\n"
    output += f"Победа {home}: {probs['home_win']}%\n"
    output += f"Равен: {probs['draw']}%\n"
    output += f"Победа {away}: {probs['away_win']}%\n"
    output += f"\n{'=' * 50}\n"

    # Добавяме информация за формата (опционално)
    if 'features' in result and result['features']:
        features = result['features']
        output += f"\nАтакуваща сила: {home} {features['home_attack']:.2f} | {away} {features['away_attack']:.2f}\n"
        output += f"Защитна сила: {home} {features['home_defense']:.2f} | {away} {features['away_defense']:.2f}\n"
        output += f"Форма: {home} {features['home_form'] * 100:.0f}% | {away} {features['away_form'] * 100:.0f}%\n"

    return output