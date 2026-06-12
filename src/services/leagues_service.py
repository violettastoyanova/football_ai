
from repositories import leagues_repo as repo
from services.players_service import get_club_id_by_name
import re
import random  # ДОБАВЕНА РЕД 1


def validate_season(season):
    """Валидира формата на сезона (YYYY/YYYY)"""
    pattern = r'^\d{4}/\d{4}$'
    if not re.match(pattern, season):
        return False
    years = season.split('/')
    if int(years[1]) != int(years[0]) + 1:
        return False
    return True


def create_league(name, season):
    """Създава нова лига с валидации"""

    if not validate_season(season):
        return "Невалиден формат на сезон. Използвайте YYYY/YYYY (напр. 2025/2026)"

    existing = repo.get_league_by_name_season(name, season)
    if existing:
        return f"Лига '{name}' за сезон {season} вече съществува."

    success = repo.create_league(name, season)
    if success:
        return f"Лига '{name}' за сезон {season} беше създадена успешно."
    else:
        return "Грешка при създаване на лига."


def add_team_to_league(club_name, league_name, season):
    """Добавя отбор към лига"""

    club_id = get_club_id_by_name(club_name)
    if not club_id:
        return f"Клуб '{club_name}' не съществува. Използвайте 'покажи всички клубове' за списък."

    league = repo.get_league_by_name_season(league_name, season)
    if not league:
        return f"Лига '{league_name}' за сезон {season} не съществува."

    league_id = league[0]

    if repo.check_team_in_league(league_id, club_id):
        return f"Клуб '{club_name}' вече е в лига '{league_name}'."

    success = repo.add_team_to_league(league_id, club_id)
    if success:
        return f"Клуб '{club_name}' беше добавен към лига '{league_name}' за сезон {season}."
    else:
        return "Грешка при добавяне на отбор."


def remove_team_from_league(club_name, league_name, season):
    """Премахва отбор от лига"""

    club_id = get_club_id_by_name(club_name)
    if not club_id:
        return f"Клуб '{club_name}' не съществува."

    league = repo.get_league_by_name_season(league_name, season)
    if not league:
        return f"Лига '{league_name}' за сезон {season} не съществува."

    league_id = league[0]

    # Първо провери дали отборът е в лигата
    if not repo.check_team_in_league(league_id, club_id):
        return f"Клуб '{club_name}' не е в лига '{league_name}'."

    # Проверка дали има генерирана програма
    if repo.check_existing_schedule(league_id):
        return f"НЕ МОЖЕ ДА ПРЕМАХНЕТЕ ОТБОР - вече има генерирана програма за лига '{league_name}'. Първо използвайте 'изтрий програма'."

    success = repo.remove_team_from_league(league_id, club_id)
    if success:
        return f"Клуб '{club_name}' беше премахнат от лига '{league_name}'."
    else:
        return "Грешка при премахване на отбор."


def show_league_teams(league_name, season):
    """Показва всички отбори в лига"""

    league = repo.get_league_by_name_season(league_name, season)
    if not league:
        return f"Лига '{league_name}' за сезон {season} не съществува."

    league_id = league[0]
    teams = repo.get_league_teams(league_id)

    if not teams:
        return f"Няма отбори в лига '{league_name}' за сезон {season}."

    result = f"Отбори в лига '{league_name}' (сезон {season}):\n"
    for team in teams:
        result += f"  • {team[1]} (ID: {team[0]}) | {team[2]} | основан {team[3]}\n"

    return result


def display_full_schedule(league_name, season):
    """Показва пълната програма за лига"""

    league = repo.get_league_by_name_season(league_name, season)
    if not league:
        return f"Лига '{league_name}' за сезон {season} не съществува."

    league_id = league[0]
    matches = repo.get_matches_for_league(league_id)

    if not matches:
        return None  # Връщаме None, ако няма програма

    result = f"\n{'=' * 50}\n"
    result += f" ПРОГРАМА - Лига '{league_name}' (сезон {season})\n"
    result += f"{'=' * 50}\n"

    # Групираме мачовете по кръг
    current_round = 1
    round_matches = []

    for match in matches:
        # Проверка дали match има правилната структура
        if len(match) < 3:
            continue

        round_no = match[0]
        home = match[1]
        away = match[2]

        if round_no != current_round:
            if round_matches:
                result += f"\n КРЪГ {current_round}:\n"
                for m in round_matches:
                    result += f"   {m[0]} vs {m[1]}\n"
            round_matches = []
            current_round = round_no

        round_matches.append((home, away))

    # Последния кръг
    if round_matches:
        result += f"\n КРЪГ {current_round}:\n"
        for m in round_matches:
            result += f"   {m[0]} vs {m[1]}\n"

    result += f"\n{'=' * 50}\n"
    result += f" Статистика: {current_round} кръга, {len(matches)} мача\n"

    return result


def generate_schedule(league_name, season):
    """Генерира програма (round-robin) за лига"""

    # Проверка за лига
    league = repo.get_league_by_name_season(league_name, season)
    if not league:
        return f"Лига '{league_name}' за сезон {season} не съществува."

    league_id = league[0]

    # Проверка за вече генерирана програма
    if repo.check_existing_schedule(league_id):
        return f"Вече има генерирана програма за лига '{league_name}'. Използвайте 'изтрий програма' ако искате да генерирате наново."

    # Вземаме отборите
    teams = repo.get_league_teams(league_id)
    if len(teams) < 4:
        return f"Недостатъчно отбори за генериране на програма. Минимум 4 отбора. (Сега: {len(teams)})"

    # Извличаме ID-тата на клубовете
    team_ids = [team[0] for team in teams]
    n = len(team_ids)

    # Създаваме mapping от ID към име
    id_to_name = {team[0]: team[1] for team in teams}

    # ДОБАВЕНА РЕД 2: РАЗМЕСВАНЕ НА ОТБОРИТЕ В СЛУЧАЕН РЕД
    random.shuffle(team_ids)

    # Round-robin алгоритъм (правилен)
    schedule = []

    # Ако е нечетен брой, добавяме BYE (None)
    if n % 2 == 1:
        team_ids.append(None)
        n += 1

    rounds = n - 1
    total_matches = n * (n - 1) // 2

    # Инициализация за алгоритъма
    half = n // 2
    teams_list = team_ids.copy()

    for round_num in range(rounds):
        round_matches = []

        # Сдвояваме отборите: първи с последен, втори с предпоследен и т.н.
        for i in range(half):
            home = teams_list[i]
            away = teams_list[n - 1 - i]

            # Пропускаме BYE мачове
            if home is not None and away is not None:
                # Редуваме домакин/гост във всеки кръг
                if round_num % 2 == 0:
                    round_matches.append((league_id, round_num + 1, home, away))
                else:
                    round_matches.append((league_id, round_num + 1, away, home))

        schedule.extend(round_matches)

        # Ротация: запазваме първия елемент на място, местим останалите
        # Стандартен алгоритъм: teams_list[1:] = [teams_list[-1]] + teams_list[1:-1]
        last = teams_list[-1]
        for i in range(n - 1, 1, -1):
            teams_list[i] = teams_list[i - 1]
        teams_list[1] = last

    # Записваме всички мачове в базата
    success = repo.create_matches_batch(schedule)

    if not success:
        return "Грешка при записване на програмата в базата данни."

    # Статистика
    actual_teams = len([t for t in team_ids if t is not None])
    result = f" Програмата за лига '{league_name}' (сезон {season}) беше генерирана успешно!\n"
    result += f" {actual_teams} отбора, {rounds} кръга, {len(schedule)} мача.\n\n"
    result += " Първи кръг:\n"

    # Показваме първите мачове
    first_round = [m for m in schedule if m[1] == 1]
    for match in first_round[:5]:
        _, _, home, away = match
        home_name = id_to_name.get(home, "?")
        away_name = id_to_name.get(away, "?")
        result += f"  • {home_name} vs {away_name}\n"

    if len(schedule) > 5:
        result += f"  ... и още {len(schedule) - 5} мача."

    return result


def delete_schedule(league_name, season):
    """Изтрива програмата за лига"""

    league = repo.get_league_by_name_season(league_name, season)
    if not league:
        return f"Лига '{league_name}' за сезон {season} не съществува."

    league_id = league[0]

    if not repo.check_existing_schedule(league_id):
        return f"Няма генерирана програма за лига '{league_name}'."

    success = repo.delete_matches_for_league(league_id)
    if success:
        return f"Програмата за лига '{league_name}' беше изтрита успешно."
    else:
        return "Грешка при изтриване на програма."