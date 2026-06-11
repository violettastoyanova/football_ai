from repositories import matches_repo as repo
from services.players_service import get_club_id_by_name
from services.leagues_service import validate_season
from database.db import execute_query

# Глобален контекст за текущ мач
current_match_context = {}


def set_current_match(match_id, chat_session_id="default"):
    """Задава текущ мач за сесия"""
    current_match_context[chat_session_id] = match_id


def get_current_match(chat_session_id="default"):
    """Връща текущия мач за сесия"""
    return current_match_context.get(chat_session_id)


def show_round_matches(league_name, season, round_no):
    """Показва мачовете за даден кръг"""
    if not validate_season(season):
        return "Невалиден формат на сезон. Използвайте YYYY/YYYY"

    league_id = repo.get_league_id_by_name_season(league_name, season)
    if not league_id:
        return f"Лига '{league_name}' за сезон {season} не съществува."

    matches = repo.get_matches_by_league_and_round(league_id, round_no)

    if not matches:
        return f"Няма мачове за кръг {round_no} в лига '{league_name}' (сезон {season})."

    result = f"\n{'=' * 60}\n"
    result += f"КРЪГ {round_no} - Лига '{league_name}' (сезон {season})\n"
    result += f"{'=' * 60}\n"

    for match in matches:
        match_id = match[0]
        home_name = match[2]
        away_name = match[4]
        home_goals = match[5]
        away_goals = match[6]
        status = match[7]

        if status == 'played':
            result += f"  #{match_id}: {home_name} {home_goals}:{away_goals} {away_name} (изигран)\n"
        else:
            result += f"  #{match_id}: {home_name} vs {away_name} (неизигран)\n"

    result += f"{'=' * 60}"
    return result


def record_result(home_team, away_team, home_goals, away_goals, league_name=None, season=None):
    """Записва резултат от мач"""
    try:
        home_goals = int(home_goals)
        away_goals = int(away_goals)
        if home_goals < 0 or away_goals < 0:
            return "Головете трябва да са положителни числа или нула."
    except ValueError:
        return "Невалиден формат за голове. Използвайте цели числа."

    league_id = None
    if league_name and season:
        if not validate_season(season):
            return "Невалиден формат на сезон."
        league_id = repo.get_league_id_by_name_season(league_name, season)
        if not league_id:
            return f"Лига '{league_name}' за сезон {season} не съществува."

    match = repo.get_match_by_teams(home_team, away_team, league_id)

    if not match:
        if league_name:
            return f"Няма мач между {home_team} и {away_team} в лига '{league_name}'."
        else:
            return f"Няма мач между {home_team} и {away_team}. Посочете лига и сезон или изберете мач."

    match_id = match[0]
    current_status = match[11]

    if current_status == 'played':
        return f"Мачът вече е игран. Ако искате да промените резултата, първо използвайте 'изтрий резултат'."

    success = repo.update_match_result(match_id, home_goals, away_goals)

    if success:
        return f"Записано: {home_team} {home_goals}:{away_goals} {away_team} (мач #{match_id})"
    else:
        return "Грешка при записване на резултата."


def add_goal_to_match(match_id, player_name, club_name, minute, is_own_goal=False, chat_session_id="default"):
    """Добавя гол към мач"""
    try:
        minute = int(minute)
        if minute < 1 or minute > 120:
            return "Минутата трябва да бъде между 1 и 120."
    except ValueError:
        return "Невалиден формат за минута."

    match = repo.get_match_by_id(match_id)
    if not match:
        return f"Мач с ID {match_id} не съществува."

    if match[11] != 'played':
        return "Можете да добавяте голове само след като мачът е изигран (първо запишете резултат)."

    home_club_id = match[5]
    away_club_id = match[7]
    home_name = match[6]
    away_name = match[8]

    club_id = get_club_id_by_name(club_name)
    if not club_id:
        return f"Клуб '{club_name}' не съществува."

    if club_id not in [home_club_id, away_club_id]:
        return f"Клуб '{club_name}' не участва в този мач. Участници: {home_name} и {away_name}"

    player_check = execute_query(
        "SELECT player_id, club_id FROM players WHERE full_name = ?",
        (player_name,),
        fetch=True
    )

    if not player_check:
        return f"Играч '{player_name}' не съществува."

    player_id = player_check[0][0]
    player_club_id = player_check[0][1]

    if player_club_id != club_id:
        return f"Играч '{player_name}' не играе за {club_name}."

    success = repo.add_goal(match_id, player_id, club_id, minute, 1 if is_own_goal else 0)

    if success:
        own_goal_text = " (автогол)" if is_own_goal else ""
        return f"Гол: {player_name} ({club_name}) в {minute} минута{own_goal_text}"
    else:
        return "Грешка при добавяне на гол."


def add_card_to_match(match_id, player_name, club_name, card_type, minute, chat_session_id="default"):
    """Добавя картон към мач"""
    card_type = card_type.upper()
    if card_type not in ['Y', 'R']:
        return "Невалиден тип картон. Използвайте 'Y' за жълт или 'R' за червен."

    try:
        minute = int(minute)
        if minute < 1 or minute > 120:
            return "Минутата трябва да бъде между 1 и 120."
    except ValueError:
        return "Невалиден формат за минута."

    match = repo.get_match_by_id(match_id)
    if not match:
        return f"Мач с ID {match_id} не съществува."

    if match[11] != 'played':
        return "Можете да добавяте картони само след като мачът е изигран."

    home_club_id = match[5]
    away_club_id = match[7]
    home_name = match[6]
    away_name = match[8]

    club_id = get_club_id_by_name(club_name)
    if not club_id:
        return f"Клуб '{club_name}' не съществува."

    if club_id not in [home_club_id, away_club_id]:
        return f"Клуб '{club_name}' не участва в този мач."

    player_check = execute_query(
        "SELECT player_id, club_id FROM players WHERE full_name = ?",
        (player_name,),
        fetch=True
    )

    if not player_check:
        return f"Играч '{player_name}' не съществува."

    player_id = player_check[0][0]
    player_club_id = player_check[0][1]

    if player_club_id != club_id:
        return f"Играч '{player_name}' не играе за {club_name}."

    if card_type == 'R':
        existing_red = execute_query(
            "SELECT 1 FROM cards WHERE match_id = ? AND player_id = ? AND card_type = 'R'",
            (match_id, player_id),
            fetch=True
        )
        if existing_red:
            return f"Играч '{player_name}' вече има червен картон в този мач."

    success = repo.add_card(match_id, player_id, club_id, minute, card_type)

    if success:
        card_name = "ЖЪЛТ" if card_type == 'Y' else "ЧЕРВЕН"
        return f"{card_name} КАРТОН: {player_name} ({club_name}) в {minute} минута"
    else:
        return "Грешка при добавяне на картон."


def show_match_events(match_id):
    """Показва всички събития за мач"""
    match = repo.get_match_by_id(match_id)
    if not match:
        return f"Мач с ID {match_id} не съществува."

    goals, cards = repo.get_match_events(match_id)

    events = []

    for goal in goals:
        minute = goal[0]
        player = goal[2]
        club = goal[3]
        own_goal = goal[4]
        text = f"{minute}' ГОЛ: {player} ({club})"
        if own_goal:
            text += " [АВТОГОЛ]"
        events.append((minute, text))

    for card in cards:
        minute = card[0]
        player = card[2]
        club = card[3]
        card_type = card[4]
        card_symbol = "ЖЪЛТ" if card_type == 'Y' else "ЧЕРВЕН"
        text = f"{minute}' {card_symbol} КАРТОН: {player} ({club})"
        events.append((minute, text))

    events.sort(key=lambda x: x[0])

    home_name = match[6]
    away_name = match[8]
    home_goals = match[9] or 0
    away_goals = match[10] or 0

    result = f"\n{'=' * 60}\n"
    result += f"СЪБИТИЯ - {home_name} {home_goals}:{away_goals} {away_name} (мач #{match_id})\n"
    result += f"{'=' * 60}\n"

    if not events:
        result += "Няма записани събития.\n"
    else:
        for _, event_text in events:
            result += f"  {event_text}\n"

    result += f"{'=' * 60}"
    return result