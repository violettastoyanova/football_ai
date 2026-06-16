import re
from datetime import datetime
from services.clubs_service import add_club, get_all_clubs, delete_club
from services.players_service import (
   add_player,
   get_players_by_club,
   get_all_players,
   update_player_number,
   update_player_position,
   update_player_status,
   delete_player
)
from services.transfers_service import (
   transfer_player,
   list_transfers_by_player,
   list_transfers_by_club
)
from chatbot.handlers_leagues import handle_league_commands
from chatbot.handlers_matches import handle_match_commands
from chatbot.handlers_standings import handle_standings_commands


class ChatBot:


   def log_command(self, text, intent, result):
       """Записва команда в лог файл с intent и статус"""
       with open("commands.log", "a", encoding="utf-8") as file:
           # Определяме статус (OK/ERROR)
           result_str = str(result)
           if "успешно" in result_str or "беше" in result_str:
               status = "OK"
           elif "грешка" in result_str.lower() or "error" in result_str.lower() or "невалиден" in result_str.lower():
               status = "ERROR"
           else:
               status = "INFO"


           file.write(f"{datetime.now()} | {text} | {intent} | {status} - {result_str}\n")


   def parse(self, text):
       text = text.strip()
       lower_text = text.lower()


       if not text:
           return "Моля, въведете команда."


       # ===============================
       # Обработка на команди за лиги
       # ===============================
       league_result = handle_league_commands(text, lower_text)
       if league_result is not None:
           intent = self._detect_league_intent(lower_text)
           self.log_command(text, intent, league_result)
           return league_result


       # ===============================
       # Обработка на команди за мачове
       # ===============================
       match_result = handle_match_commands(text, lower_text)
       if match_result is not None:
           intent = self._detect_match_intent(lower_text)
           self.log_command(text, intent, match_result)
           return match_result

       # ===============================
       # Обработка на команди за класиране
       # ===============================
       standings_result = handle_standings_commands(text, lower_text)
       if standings_result is not None:
           intent = "show_standings"
           self.log_command(text, intent, standings_result)
           return standings_result

       # ===============================
       # AI PREDICTION
       # ===============================
       if lower_text.startswith("прогноза"):
           from ai.ai_service import predict_match, format_prediction_result

           match = re.search(
               r'^прогноза\s+(.+?)\s+срещу\s+(.+)$',
               text,
               re.IGNORECASE
           )
           if not match:
               error_msg = "Формат: прогноза Отбор1 срещу Отбор2"
               self.log_command(text, "ai_prediction", error_msg)
               return error_msg

           home_team = match.group(1).strip()
           away_team = match.group(2).strip()

           # Проверка дали са различни отбори
           if home_team.lower() == away_team.lower():
               error_msg = "Не може да прогнозирате мач между един и същ отбор."
               self.log_command(text, "ai_prediction", error_msg)
               return error_msg

           result = predict_match(home_team, away_team)
           formatted_result = format_prediction_result(result)

           # Определяме статус за лог
           status = "OK" if not result.get('error') else "ERROR"
           self.log_command(text, "ai_prediction", formatted_result)

           return formatted_result



       # EXIT
       if lower_text == "изход":
           self.log_command(text, "exit", "Програмата приключи")
           return "exit"


       # HELP
       if lower_text == "помощ":
           help_text = """Възможни команди:


=== КЛУБОВЕ ===
добави клуб Име, Град, Година
покажи всички клубове
изтрий клуб Име


=== ИГРАЧИ ===
добави играч Име Фамилия DD-MM-YYYY Националност Клуб Позиция Номер
покажи играчи на Клуб
покажи всички играчи
промени номер на Име Фамилия НовНомер
промени позиция на Име Фамилия НоваПозиция
промени статус на Име Фамилия активен/контузен
изтрий играч Име Фамилия


=== ТРАНСФЕРИ ===
трансфер Играч от Отбор в Отбор DD-MM-YYYY
покажи трансфери на Играч
покажи трансфери на Клуб


=== ЛИГИ ===
създай лига <име> <сезон>           (сезон: YYYY/YYYY)
добави отбор <клуб> в лига <име> <сезон>
премахни отбор <клуб> от лига <име> <сезон>
покажи отбори в лига <име> <сезон>
генерирай програма <име> <сезон>
покажи програма <име> <сезон>
изтрий програма <име> <сезон>


=== МАЧОВЕ ===
покажи кръг <N> <лига> <сезон>
избери мач <match_id>
резултат <Домакин>-<Гост> <X>:<Y> запиши [в лига <име> <сезон>]
гол <Играч>, <Отбор>, <минута> минута [автогол]
картон <Играч>, <Отбор>, <Y/R>, <минута> минута
покажи събития [<match_id>]


=== КЛАСИРАНЕ ===
покажи класиране <лига> <сезон>


=== AI ПРОГНОЗА ===
прогноза <Отбор1> срещу <Отбор2>


=== ОБЩИ ===
помощ
изход
"""
           self.log_command(text, "help", "Показана помощ")
           return help_text


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
               error_msg = "Формат: добави клуб Име, Град, Година"
               self.log_command(text, "add_club", error_msg)
               return error_msg


           name = match.group(1).strip()
           city = match.group(2).strip()
           founded_year = int(match.group(3))


           result = add_club(name, city, founded_year)
           self.log_command(text, "add_club", result)
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
               error_msg = ("Формат: добави играч Име Фамилия DD-MM-YYYY "
                            "Националност Клуб Позиция Номер")
               self.log_command(text, "add_player", error_msg)
               return error_msg


           full_name = f"{match.group(1)} {match.group(2)}"
           birth_date = match.group(3)
           nationality = match.group(4)
           club = match.group(5)
           position = match.group(6)
           number = int(match.group(7))


           result = add_player(full_name, birth_date, nationality, club, position, number)
           self.log_command(text, "add_player", result)
           return result


       # ===============================
       # SHOW CLUBS
       # ===============================
       if lower_text == "покажи всички клубове":
           result = get_all_clubs()
           self.log_command(text, "list_clubs", result)
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
               error_msg = "Формат: покажи играчи на Клуб"
               self.log_command(text, "list_players_by_club", error_msg)
               return error_msg


           club = match.group(1).strip()
           result = get_players_by_club(club)
           self.log_command(text, "list_players_by_club", result)
           return result


       # ===============================
       # SHOW ALL PLAYERS
       # ===============================
       if lower_text == "покажи всички играчи":
           result = get_all_players()
           self.log_command(text, "list_all_players", result)
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
               error_msg = "Формат: изтрий клуб Име"
               self.log_command(text, "delete_club", error_msg)
               return error_msg


           name = match.group(1).strip()
           result = delete_club(name)
           self.log_command(text, "delete_club", result)
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
               error_msg = "Формат: промени номер на Име Фамилия НовНомер"
               self.log_command(text, "update_number", error_msg)
               return error_msg


           full_name = match.group(1).strip()
           new_number = int(match.group(2))


           result = update_player_number(full_name, new_number)
           self.log_command(text, "update_number", result)
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
               error_msg = "Формат: промени позиция на Име Фамилия НоваПозиция"
               self.log_command(text, "update_position", error_msg)
               return error_msg


           full_name = match.group(1).strip()
           new_position = match.group(2)


           result = update_player_position(full_name, new_position)
           self.log_command(text, "update_position", result)
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
               error_msg = "Формат: промени статус на Име Фамилия активен/контузен"
               self.log_command(text, "update_status", error_msg)
               return error_msg


           full_name = match.group(1).strip()
           new_status = match.group(2)


           result = update_player_status(full_name, new_status)
           self.log_command(text, "update_status", result)
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
               error_msg = "Формат: изтрий играч Име Фамилия"
               self.log_command(text, "delete_player", error_msg)
               return error_msg


           full_name = match.group(1).strip()
           result = delete_player(full_name)
           self.log_command(text, "delete_player", result)
           return result


       # ===============================
       # TRANSFER PLAYER
       # ===============================
       if lower_text.startswith("трансфер"):
           match = re.search(
               r"^трансфер\s+(.+?)\s+от\s+(.+?)\s+в\s+(.+?)\s+(\d{2}-\d{2}-\d{4})$",
               text,
               re.IGNORECASE
           )
           if not match:
               error_msg = "Формат: трансфер Играч от Отбор в Отбор DD-MM-YYYY"
               self.log_command(text, "transfer_player", error_msg)
               return error_msg


           player = match.group(1).strip()
           from_club = match.group(2).strip()
           to_club = match.group(3).strip()
           date = match.group(4)


           result = transfer_player(player, from_club, to_club, date)
           self.log_command(text, "transfer_player", result)
           return result


       # ===============================
       # SHOW TRANSFERS
       # ===============================
       if lower_text.startswith("покажи трансфери на"):
           match = re.search(
               r"^покажи трансфери на\s+(.+)$",
               text,
               re.IGNORECASE
           )
           if not match:
               error_msg = "Формат: покажи трансфери на Играч/Клуб"
               self.log_command(text, "show_transfers", error_msg)
               return error_msg


           name = match.group(1).strip()


           # първо пробва като играч
           result = list_transfers_by_player(name)


           if result and "Няма трансфери" not in result:
               self.log_command(text, "show_transfers_player", result)
               return result


           # ако няма -> пробва като клуб
           result = list_transfers_by_club(name)
           self.log_command(text, "show_transfers_club", result)
           return result


       # Невалидна команда
       error_msg = "Невалидна команда. Напиши 'помощ' за инструкции."
       self.log_command(text, "unknown", error_msg)
       return error_msg


   def _detect_league_intent(self, lower_text):
       """Помагателна функция за определяне на intent на league командите"""
       if lower_text.startswith("създай лига"):
           return "create_league"
       elif lower_text.startswith("добави отбор"):
           return "add_team_to_league"
       elif lower_text.startswith("премахни отбор"):
           return "remove_team_from_league"
       elif lower_text.startswith("покажи отбори в лига"):
           return "show_league_teams"
       elif lower_text.startswith("генерирай програма"):
           return "generate_schedule"
       elif lower_text.startswith("покажи програма"):
           return "show_schedule"
       elif lower_text.startswith("изтрий програма"):
           return "delete_schedule"
       else:
           return "league_command"


   def _detect_match_intent(self, lower_text):
       """Помагателна функция за определяне на intent на match командите"""
       if lower_text.startswith("покажи кръг"):
           return "show_round"
       elif lower_text.startswith("избери мач"):
           return "select_match"
       elif lower_text.startswith("резултат"):
           return "record_result"
       elif lower_text.startswith("гол"):
           return "add_goal"
       elif lower_text.startswith("картон"):
           return "add_card"
       elif lower_text.startswith("покажи събития"):
           return "show_events"
       else:
           return "match_command"