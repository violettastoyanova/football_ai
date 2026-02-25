from db import execute_query
from datetime import datetime


VALID_POSITIONS = {"Вратар", "Защитник", "Полузащитник", "Нападател"}
VALID_STATUSES = {"активен", "контузен"}


def validate_date(date_text):
    try:
        datetime.strptime(date_text, "%d-%m-%Y")
        return True
    except ValueError:
        return False


def get_club_id_by_name(club_name):
    result = execute_query(
        "SELECT club_id FROM clubs WHERE name = ?",
        (club_name,),
        fetch=True
    )
    return result[0][0] if result else None


# ===============================
# ADD PLAYER
# ===============================
def add_player(full_name, birth_date, nationality, club_name, position, number):

    if position not in VALID_POSITIONS:
        return "Невалидна позиция."

    if number < 1 or number > 99:
        return "Невалиден номер (1–99)."

    if not validate_date(birth_date):
        return "Невалиден формат на дата (DD-MM-YYYY)."

    club_id = get_club_id_by_name(club_name)
    if not club_id:
        return "Няма такъв клуб."

    existing_player = execute_query(
        "SELECT player_id FROM players WHERE full_name = ? AND club_id = ?",
        (full_name, club_id),
        fetch=True
    )

    if existing_player:
        return "Играч с това име вече съществува в този клуб."

    existing_number = execute_query(
        "SELECT player_id FROM players WHERE number = ? AND club_id = ?",
        (number, club_id),
        fetch=True
    )

    if existing_number:
        return "В този клуб вече има играч с този номер."

    execute_query(
        """INSERT INTO players
        (full_name, birth_date, nationality, position, number, status, club_id)
        VALUES (?, ?, ?, ?, ?, 'активен', ?)""",
        (full_name, birth_date, nationality, position, number, club_id)
    )

    return "Играчът беше добавен успешно."


# ===============================
# LIST PLAYERS
# ===============================
def get_players_by_club(club_name):

    club_id = get_club_id_by_name(club_name)
    if not club_id:
        return "Няма такъв клуб."

    players = execute_query(
        """SELECT full_name, position, number, status
           FROM players WHERE club_id = ?
           ORDER BY number""",
        (club_id,),
        fetch=True
    )

    if not players:
        return "Няма играчи в този клуб."

    result = f"Играчите на {club_name}:\n"
    for p in players:
        result += f"{p[0]} | {p[1]} | №{p[2]} | {p[3]}\n"

    return result


# ===============================
# UPDATE NUMBER
# ===============================
def update_player_number(full_name, new_number):

    if new_number < 1 or new_number > 99:
        return "Невалиден номер."

    player = execute_query(
        "SELECT club_id FROM players WHERE full_name = ?",
        (full_name,),
        fetch=True
    )

    if not player:
        return "Играчът не съществува."

    club_id = player[0][0]

    existing_number = execute_query(
        "SELECT player_id FROM players WHERE number = ? AND club_id = ?",
        (new_number, club_id),
        fetch=True
    )

    if existing_number:
        return "В този клуб вече има играч с този номер."

    execute_query(
        "UPDATE players SET number = ? WHERE full_name = ?",
        (new_number, full_name)
    )

    return "Номерът беше обновен успешно."


# ===============================
# UPDATE POSITION
# ===============================
def update_player_position(full_name, new_position):

    if new_position not in VALID_POSITIONS:
        return "Невалидна позиция."

    existing = execute_query(
        "SELECT player_id FROM players WHERE full_name = ?",
        (full_name,),
        fetch=True
    )

    if not existing:
        return "Играчът не съществува."

    execute_query(
        "UPDATE players SET position = ? WHERE full_name = ?",
        (new_position, full_name)
    )

    return "Позицията беше обновена успешно."


# ===============================
# UPDATE STATUS
# ===============================
def update_player_status(full_name, new_status):

    if new_status not in VALID_STATUSES:
        return "Невалиден статус (активен/контузен)."

    existing = execute_query(
        "SELECT player_id FROM players WHERE full_name = ?",
        (full_name,),
        fetch=True
    )

    if not existing:
        return "Играчът не съществува."

    execute_query(
        "UPDATE players SET status = ? WHERE full_name = ?",
        (new_status, full_name)
    )

    return "Статусът беше обновен успешно."


# ===============================
# DELETE PLAYER
# ===============================
def delete_player(full_name):

    existing = execute_query(
        "SELECT player_id FROM players WHERE full_name = ?",
        (full_name,),
        fetch=True
    )

    if not existing:
        return "Играчът не съществува."

    execute_query(
        "DELETE FROM players WHERE full_name = ?",
        (full_name,)
    )

    return "Играчът беше изтрит успешно."
