import re

def detect_intent(text):
    text = text.strip()
    lower = text.lower()

    # exit
    if lower == "изход":
        return "exit", {}

    # help
    if lower == "помощ":
        return "help", {}

    # transfer
    match = re.search(
        r"^трансфер\s+(.+?)\s+от\s+(.+?)\s+в\s+(.+?)\s+(\d{2}-\d{2}-\d{4})$",
        text,
        re.IGNORECASE
    )
    if match:
        return "transfer_player", {
            "player": match.group(1),
            "from_club": match.group(2),
            "to_club": match.group(3),
            "date": match.group(4)
        }

    # show transfers player
    match = re.search(r"^покажи трансфери на\s+(.+)$", text, re.IGNORECASE)
    if match:
        return "show_transfers_player", {"name": match.group(1)}

    # show transfers club
    match = re.search(r"^покажи трансфери на клуб\s+(.+)$", text, re.IGNORECASE)
    if match:
        return "show_transfers_club", {"club": match.group(1)}

    league_intent, league_params = detect_league_intent(text)
    if league_intent:
        return league_intent, league_params

    return "unknown", {}


def detect_league_intent(text):
    """Разпознава intent-и за лиги"""
    text = text.strip()
    lower = text.lower()

    # създай лига
    match = re.search(
        r"^създай лига\s+(.+?)\s+(\d{4}/\d{4})$",
        text,
        re.IGNORECASE
    )
    if match:
        return "create_league", {
            "name": match.group(1).strip(),
            "season": match.group(2).strip()
        }

    # добави отбор в лига
    match = re.search(
        r"^добави отбор\s+(.+?)\s+в лига\s+(.+?)\s+(\d{4}/\d{4})$",
        text,
        re.IGNORECASE
    )
    if match:
        return "add_team_to_league", {
            "club": match.group(1).strip(),
            "league_name": match.group(2).strip(),
            "season": match.group(3).strip()
        }

    # премахни отбор от лига
    match = re.search(
        r"^премахни отбор\s+(.+?)\s+от лига\s+(.+?)\s+(\d{4}/\d{4})$",
        text,
        re.IGNORECASE
    )
    if match:
        return "remove_team_from_league", {
            "club": match.group(1).strip(),
            "league_name": match.group(2).strip(),
            "season": match.group(3).strip()
        }

    # покажи отбори в лига
    match = re.search(
        r"^покажи отбори в лига\s+(.+?)\s+(\d{4}/\d{4})$",
        text,
        re.IGNORECASE
    )
    if match:
        return "show_league_teams", {
            "league_name": match.group(1).strip(),
            "season": match.group(2).strip()
        }

    # генерирай програма
    match = re.search(
        r"^генерирай програма\s+(.+?)\s+(\d{4}/\d{4})$",
        text,
        re.IGNORECASE
    )
    if match:
        return "generate_schedule", {
            "league_name": match.group(1).strip(),
            "season": match.group(2).strip()
        }

    # изтрий програма
    match = re.search(
        r"^изтрий програма\s+(.+?)\s+(\d{4}/\d{4})$",
        text,
        re.IGNORECASE
    )
    if match:
        return "delete_schedule", {
            "league_name": match.group(1).strip(),
            "season": match.group(2).strip()
        }

    # покажи програма
    match = re.search(
        r"^покажи програма\s+(.+?)\s+(\d{4}/\d{4})$",
        text,
        re.IGNORECASE
    )
    if match:
        return "show_schedule", {
            "league_name": match.group(1).strip(),
            "season": match.group(2).strip()
        }

    return None, None