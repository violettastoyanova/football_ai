import re
from services.leagues_service import (
    create_league,
    add_team_to_league,
    remove_team_from_league,
    show_league_teams,
    generate_schedule,
    delete_schedule
)

def show_full_schedule(league_name, season):
    """Показва пълната програма за лига"""
    from services.leagues_service import display_full_schedule
    return display_full_schedule(league_name, season)


def handle_league_commands(text, lower_text):
    """Обработва команди, свързани с лиги"""

    # Създай лига <име> <сезон>
    match = re.search(
        r'^създай лига\s+(.+?)\s+(\d{4}/\d{4})$',
        text,
        re.IGNORECASE
    )
    if match:
        name = match.group(1).strip()
        season = match.group(2).strip()
        return create_league(name, season)

    # Покажи програма <име> <сезон>
    match = re.search(
        r'^покажи програма\s+(.+?)\s+(\d{4}/\d{4})$',
        text,
        re.IGNORECASE
    )
    if match:
        league_name = match.group(1).strip()
        season = match.group(2).strip()
        return show_full_schedule(league_name, season)

    # Добави отбор <клуб> в лига <име> <сезон>
    match = re.search(
        r'^добави отбор\s+(.+?)\s+в лига\s+(.+?)\s+(\d{4}/\d{4})$',
        text,
        re.IGNORECASE
    )
    if match:
        club_name = match.group(1).strip()
        league_name = match.group(2).strip()
        season = match.group(3).strip()
        return add_team_to_league(club_name, league_name, season)

    # Премахни отбор <клуб> от лига <име> <сезон>
    match = re.search(
        r'^премахни отбор\s+(.+?)\s+от лига\s+(.+?)\s+(\d{4}/\d{4})$',
        text,
        re.IGNORECASE
    )
    if match:
        club_name = match.group(1).strip()
        league_name = match.group(2).strip()
        season = match.group(3).strip()
        return remove_team_from_league(club_name, league_name, season)

    # Покажи отбори в лига <име> <сезон>
    match = re.search(
        r'^покажи отбори в лига\s+(.+?)\s+(\d{4}/\d{4})$',
        text,
        re.IGNORECASE
    )
    if match:
        league_name = match.group(1).strip()
        season = match.group(2).strip()
        return show_league_teams(league_name, season)

    # Генерирай програма <име> <сезон>
    match = re.search(
        r'^генерирай програма\s+(.+?)\s+(\d{4}/\d{4})$',
        text,
        re.IGNORECASE
    )
    if match:
        league_name = match.group(1).strip()
        season = match.group(2).strip()
        return generate_schedule(league_name, season)

    # Изтрий програма <име> <сезон> (допълнителна команда)
    match = re.search(
        r'^изтрий програма\s+(.+?)\s+(\d{4}/\d{4})$',
        text,
        re.IGNORECASE
    )
    if match:
        league_name = match.group(1).strip()
        season = match.group(2).strip()
        return delete_schedule(league_name, season)

    return None  # Командата не е за лиги