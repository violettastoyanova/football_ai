from database.db import get_connection, execute_query
from services.players_service import get_club_id_by_name
from datetime import datetime


# ===============================
# TRANSFER PLAYER
# ===============================
def transfer_player(player_name, from_club, to_club, date, fee=None):

    # Проверка за дата (DD-MM-YYYY)
    try:
        datetime.strptime(date, "%d-%m-%Y")
    except ValueError:
        return "Невалиден формат на дата (DD-MM-YYYY)."

    # Проверка from != to
    if from_club == to_club:
        return "Играчът вече е в този клуб."

    # Проверка дали играчът съществува
    player = execute_query(
        "SELECT player_id, club_id FROM players WHERE full_name = ?",
        (player_name,),
        fetch=True
    )

    if not player:
        return "Играчът не съществува."

    player_id = player[0][0]
    current_club_id = player[0][1]

    # Вземаме ID на клубовете
    from_club_id = get_club_id_by_name(from_club)
    to_club_id = get_club_id_by_name(to_club)

    if not from_club_id or not to_club_id:
        return "Невалиден клуб."

    # Проверка: от ≠ към
    if from_club_id == to_club_id:
        return "Играчът вече е в този клуб."

    # Проверка: текущ клуб
    if current_club_id != from_club_id:
        return "Играчът не принадлежи на този клуб."

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # INSERT в transfers
        cursor.execute(
            """
            INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee)
            VALUES (?, ?, ?, ?, ?)
            """,
            (player_id, from_club_id, to_club_id, date, fee)
        )

        # UPDATE на играча
        cursor.execute(
            "UPDATE players SET club_id = ? WHERE player_id = ?",
            (to_club_id, player_id)
        )

        conn.commit()
        conn.close()

        return f"Успешен трансфер: {player_name} от {from_club} в {to_club} ({date})"

    except Exception as e:
        return f"Грешка при трансфер: {e}"


# ===============================
# LIST TRANSFERS BY PLAYER
# ===============================
def list_transfers_by_player(player_name):

    player = execute_query(
        "SELECT player_id FROM players WHERE full_name = ?",
        (player_name,),
        fetch=True
    )

    if not player:
        return None  # важно → за да може да пробва като клуб

    player_id = player[0][0]

    transfers = execute_query(
        """
        SELECT c1.name, c2.name, t.transfer_date, t.fee
        FROM transfers t
        LEFT JOIN clubs c1 ON t.from_club_id = c1.club_id
        JOIN clubs c2 ON t.to_club_id = c2.club_id
        WHERE t.player_id = ?
        ORDER BY t.transfer_date
        """,
        (player_id,),
        fetch=True
    )

    if not transfers:
        return f"Няма трансфери за {player_name}."

    result = f"Трансфери на {player_name}:\n"

    for t in transfers:
        fee = t[3] if t[3] else "-"
        result += f"{t[0]} → {t[1]} | {t[2]} | {fee}\n"

    return result


# ===============================
# LIST TRANSFERS BY CLUB
# ===============================
def list_transfers_by_club(club_name):

    club = execute_query(
        "SELECT club_id FROM clubs WHERE name = ?",
        (club_name,),
        fetch=True
    )

    if not club:
        return "Няма такъв клуб."

    club_id = club[0][0]

    transfers = execute_query(
        """
        SELECT p.full_name, c1.name, c2.name, t.transfer_date, t.fee
        FROM transfers t
        JOIN players p ON t.player_id = p.player_id
        LEFT JOIN clubs c1 ON t.from_club_id = c1.club_id
        JOIN clubs c2 ON t.to_club_id = c2.club_id
        WHERE t.from_club_id = ? OR t.to_club_id = ?
        ORDER BY t.transfer_date
        """,
        (club_id, club_id),
        fetch=True
    )

    if not transfers:
        return f"Няма трансфери на {club_name}."

    result = f"Трансфери на {club_name}:\n"

    for t in transfers:
        fee = t[4] if t[4] else "-"
        result += f"{t[0]}: {t[1]} → {t[2]} | {t[3]} | {fee}\n"

    return result