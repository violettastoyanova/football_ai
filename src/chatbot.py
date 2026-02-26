import re
from datetime import datetime
from clubs_service import add_club, get_all_clubs, delete_club
from players_service import (
    add_player,
    get_players_by_club,
    get_all_players,
    update_player_number,
    update_player_position,
    update_player_status,
    delete_player
)


class ChatBot:

    def log_command(self, text, result):
        with open("commands.log", "a", encoding="utf-8") as file:
            file.write(f"{datetime.now()} | {text} | {result}\n")

    def parse(self, text):
        text = text.strip()
        lower_text = text.lower()

        if not text:
            return "Моля, въведете команда."

        # EXIT
        if lower_text == "изход":
            self.log_command(text, "exit")
            return "exit"

        # HELP
        if lower_text == "помощ":
            return """Възможни команди:

добави клуб Име, Град, Година
покажи всички клубове
изтрий клуб Име

добави играч Име Фамилия DD-MM-YYYY Националност Клуб Позиция Номер
покажи играчи на Клуб
покажи всички играчи
промени номер на Име Фамилия НовНомер
промени позиция на Име Фамилия НоваПозиция
промени статус на Име Фамилия активен/контузен
изтрий играч Име Фамилия

помощ
изход
"""

        # ===============================
        # ADD CLUB
        # ===============================
        if lower_text.startswith("добави клуб"):

            match = re.search(
                r"^добави клуб\s+(.+?),\s*(.+?),\s*(\d{4})$",
                text,
                re.IGNORECASE
            )

            if not match:
                return "Формат: добави клуб Име, Град, Година"

            name = match.group(1).strip()
            city = match.group(2).strip()
            founded_year = int(match.group(3))

            result = add_club(name, city, founded_year)
            self.log_command(text, result)
            return result

        # ===============================
        # ADD PLAYER
        # ===============================
        if lower_text.startswith("добави играч"):

            match = re.search(
                r"^добави играч\s+(.+?)\s+(.+?)\s+(\d{2}-\d{2}-\d{4})\s+(.+?)\s+(.+?)\s+(Вратар|Защитник|Полузащитник|Нападател)\s+(\d+)$",
                text,
                re.IGNORECASE
            )

            if not match:
                return ("Формат: добави играч Име Фамилия DD-MM-YYYY "
                        "Националност Клуб Позиция Номер")

            full_name = f"{match.group(1)} {match.group(2)}"
            birth_date = match.group(3)
            nationality = match.group(4)
            club = match.group(5)
            position = match.group(6)
            number = int(match.group(7))

            result = add_player(full_name, birth_date, nationality, club, position, number)
            self.log_command(text, result)
            return result

        # ===============================
        # SHOW CLUBS
        # ===============================
        if lower_text == "покажи всички клубове":
            result = get_all_clubs()
            self.log_command(text, result)
            return result

        # ===============================
        # SHOW PLAYERS
        # ===============================
        if lower_text.startswith("покажи играчи на"):

            match = re.search(
                r"^покажи играчи на\s+(?:клуб\s+)?(.+)$",
                text,
                re.IGNORECASE
            )

            if not match:
                return "Формат: покажи играчи на Клуб"

            club = match.group(1).strip()
            result = get_players_by_club(club)
            self.log_command(text, result)
            return result

        # ===============================
        # SHOW ALL PLAYERS
        # ===============================
        if lower_text == "покажи всички играчи":
            result = get_all_players()
            self.log_command(text, result)
            return result

        # ===============================
        # DELETE CLUB
        # ===============================
        if lower_text.startswith("изтрий клуб"):

            match = re.search(
                r"^изтрий клуб\s+(.+)$",
                text,
                re.IGNORECASE
            )

            if not match:
                return "Формат: изтрий клуб Име"

            name = match.group(1).strip()

            result = delete_club(name)
            self.log_command(text, result)
            return result

        # ===============================
        # UPDATE NUMBER
        # ===============================
        if lower_text.startswith("промени номер на"):

            match = re.search(
                r"^промени номер на\s+(.+?)\s+(\d+)$",
                text,
                re.IGNORECASE
            )

            if not match:
                return "Формат: промени номер на Име Фамилия НовНомер"

            full_name = match.group(1).strip()
            new_number = int(match.group(2))

            result = update_player_number(full_name, new_number)
            self.log_command(text, result)
            return result

        # ===============================
        # UPDATE POSITION
        # ===============================
        if lower_text.startswith("промени позиция на"):

            match = re.search(
                r"^промени позиция на\s+(.+?)\s+(Вратар|Защитник|Полузащитник|Нападател)$",
                text,
                re.IGNORECASE
            )

            if not match:
                return "Формат: промени позиция на Име Фамилия НоваПозиция"

            full_name = match.group(1).strip()
            new_position = match.group(2)

            result = update_player_position(full_name, new_position)
            self.log_command(text, result)
            return result

        # ===============================
        # UPDATE STATUS
        # ===============================
        if lower_text.startswith("промени статус на"):

            match = re.search(
                r"^промени статус на\s+(.+?)\s+(активен|контузен)$",
                text,
                re.IGNORECASE
            )

            if not match:
                return "Формат: промени статус на Име Фамилия активен/контузен"

            full_name = match.group(1).strip()
            new_status = match.group(2)

            result = update_player_status(full_name, new_status)
            self.log_command(text, result)
            return result

        # ===============================
        # DELETE PLAYER
        # ===============================
        if lower_text.startswith("изтрий играч"):

            match = re.search(
                r"^изтрий играч\s+(.+)$",
                text,
                re.IGNORECASE
            )

            if not match:
                return "Формат: изтрий играч Име Фамилия"

            full_name = match.group(1).strip()

            result = delete_player(full_name)
            self.log_command(text, result)
            return result

        return "Невалидна команда."
