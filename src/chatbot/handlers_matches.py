import re
from services import matches_service as service


class MatchHandler:
    def __init__(self):
        self.session_id = "default"

    def handle(self, text, lower_text):
        """Обработва команди за мачове"""

        # Покажи кръг <N> <лига> <сезон>
        match = re.search(
            r'^покажи кръг\s+(\d+)\s+(.+?)\s+(\d{4}/\d{4})$',
            text,
            re.IGNORECASE
        )
        if match:
            round_no = int(match.group(1))
            league_name = match.group(2).strip()
            season = match.group(3).strip()
            return service.show_round_matches(league_name, season, round_no)

        # Избери мач <id>
        match = re.search(r'^избери мач\s+(\d+)$', text, re.IGNORECASE)
        if match:
            match_id = int(match.group(1))
            match_data = service.repo.get_match_by_id(match_id)
            if not match_data:
                return f"Мач с ID {match_id} не съществува."

            service.set_current_match(match_id, self.session_id)
            home_name = match_data[6]
            away_name = match_data[8]
            return f"Избран мач #{match_id}: {home_name} vs {away_name}"

        # Резултат <Домакин>-<Гост> <X>:<Y> запиши [в лига <име> <сезон>]
        match = re.search(
            r'^резултат\s+(.+?)-(.+?)\s+(\d+):(\d+)\s+запиши(?:\s+в лига\s+(.+?)\s+(\d{4}/\d{4}))?$',
            text,
            re.IGNORECASE
        )
        if match:
            home_team = match.group(1).strip()
            away_team = match.group(2).strip()
            home_goals = match.group(3)
            away_goals = match.group(4)
            league_name = match.group(5).strip() if match.group(5) else None
            season = match.group(6).strip() if match.group(6) else None

            return service.record_result(home_team, away_team, home_goals, away_goals, league_name, season)

        # Гол - формат: гол Играч, Отбор, минута [автогол]
        match = re.search(
            r'^гол\s+([^,]+),\s*([^,]+),\s*(\d+)\s*минута(?:\s*автогол)?$',
            text,
            re.IGNORECASE
        )
        if match:
            player_name = match.group(1).strip()
            club_name = match.group(2).strip()
            minute = match.group(3)
            is_own_goal = 'автогол' in text.lower()

            match_id = service.get_current_match(self.session_id)
            if not match_id:
                return "Няма избран мач. Първо използвайте 'избери мач <id>'"

            return service.add_goal_to_match(match_id, player_name, club_name, minute, is_own_goal, self.session_id)

        # Картон - формат: картон Играч, Отбор, Y/R, минута
        match = re.search(
            r'^картон\s+([^,]+),\s*([^,]+),\s*([YR]),\s*(\d+)\s*минута$',
            text,
            re.IGNORECASE
        )
        if match:
            player_name = match.group(1).strip()
            club_name = match.group(2).strip()
            card_type = match.group(3).upper()
            minute = match.group(4)

            match_id = service.get_current_match(self.session_id)
            if not match_id:
                return "Няма избран мач. Първо използвайте 'избери мач <id>'"

            return service.add_card_to_match(match_id, player_name, club_name, card_type, minute, self.session_id)

        # Покажи събития [id]
        match = re.search(r'^покажи събития(?:\s+(\d+))?$', text, re.IGNORECASE)
        if match:
            if match.group(1):
                match_id = int(match.group(1))
            else:
                match_id = service.get_current_match(self.session_id)
                if not match_id:
                    return "Няма избран мач. Използвайте 'покажи събития <id>' или 'избери мач <id>'"

            return service.show_match_events(match_id)

        return None


def handle_match_commands(text, lower_text):
    """Функция за интеграция със съществуващия ChatBot"""
    handler = MatchHandler()
    return handler.handle(text, lower_text)