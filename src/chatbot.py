import re
from datetime import datetime
from clubs_service import add_club, get_all_clubs, delete_club


class ChatBot:

    def log_command(self, text, result):
        with open("commands.log", "a", encoding="utf-8") as file:
            file.write(f"{datetime.now()} | {text} | {result}\n")

    def parse(self, text):
        text = text.strip()

        if not text:
            return "Моля, въведете команда."

        # EXIT
        if text.lower() == "изход":
            self.log_command(text, "exit")
            return "exit"

        # HELP
        if text.lower() == "помощ":
            help_text = """Възможни команди:
- Добави клуб Име, Град, 1914
- Покажи всички клубове
- Изтрий клуб Име
- помощ
- изход"""
            self.log_command(text, "help shown")
            return help_text

        # ADD CLUB
        match = re.search(r"добави клуб (.+), (.+), (\d{4})", text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            city = match.group(2).strip()
            year = int(match.group(3))

            result = add_club(name, city, year)
            self.log_command(text, result)
            return result

        # LIST CLUBS
        if text.lower() == "покажи всички клубове":
            result = get_all_clubs()
            self.log_command(text, "listed clubs")
            return result

        # DELETE CLUB
        match = re.search(r"изтрий клуб (.+)", text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            result = delete_club(name)
            self.log_command(text, result)
            return result

        self.log_command(text, "invalid command")
        return "Невалидна команда. Напишете 'помощ' за инструкции."
