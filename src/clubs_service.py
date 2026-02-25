from db import execute_query


# ===============================
# ADD CLUB
# ===============================
def add_club(name, city, founded_year):

    # Проверка за валидна година
    if founded_year < 1800 or founded_year > 2100:
        return "Невалидна година на основаване."

    # Проверка за съществуващ клуб
    existing = execute_query(
        "SELECT club_id FROM clubs WHERE name = ?",
        (name,),
        fetch=True
    )

    if existing:
        return "Клуб с това име вече съществува."

    execute_query(
        "INSERT INTO clubs (name, city, founded_year) VALUES (?, ?, ?)",
        (name, city, founded_year)
    )

    return "Клубът беше добавен успешно."


# ===============================
# SHOW ALL CLUBS
# ===============================
def get_all_clubs():
    clubs = execute_query(
        "SELECT club_id, name, city, founded_year FROM clubs ORDER BY club_id",
        fetch=True
    )

    if not clubs:
        return "Няма въведени клубове."

    result = "Списък с всички клубове:\n"

    for club in clubs:
        result += f"{club[0]} | {club[1]} | {club[2]} | {club[3]}\n"

    return result


# ===============================
# DELETE CLUB
# ===============================
def delete_club(name):

    # Проверка дали клубът съществува
    club = execute_query(
        "SELECT club_id FROM clubs WHERE name = ?",
        (name,),
        fetch=True
    )

    if not club:
        return "Няма такъв клуб."

    club_id = club[0][0]

    # Проверка дали има играчи
    players = execute_query(
        "SELECT player_id FROM players WHERE club_id = ?",
        (club_id,),
        fetch=True
    )

    if players:
        return "Не може да изтриете клуб с налични играчи."

    execute_query(
        "DELETE FROM clubs WHERE club_id = ?",
        (club_id,)
    )

    return "Клубът беше изтрит успешно."
