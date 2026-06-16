import re
from services.standings_service import get_standings


def handle_standings_commands(text, lower_text):
    """Обработва команди за класиране"""

    # Покажи класиране <лига> <сезон>
    match = re.search(
        r'^покажи класиране\s+(.+?)\s+(\d{4}/\d{4})$',
        text,
        re.IGNORECASE
    )
    if match:
        league_name = match.group(1).strip()
        season = match.group(2).strip()
        return get_standings(league_name, season)

    return None