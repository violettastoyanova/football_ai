from db import execute_query


def add_club(name, city, founded_year):

    if not name or not city:
        return "Невалидни данни."

    if founded_year < 1800 or founded_year > 2026:
        return "Невалидна година."

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


def get_all_clubs():
    clubs = execute_query(
        "SELECT club_id, name, city, founded_year FROM clubs",
        fetch=True
    )

    if not clubs:
        return "Няма въведени клубове."

    result = ""
    for club in clubs:
        result += f"{club[0]} | {club[1]} | {club[2]} | {club[3]}\n"

    return result


def delete_club(name):

    existing = execute_query(
        "SELECT club_id FROM clubs WHERE name = ?",
        (name,),
        fetch=True
    )

    if not existing:
        return "Няма такъв клуб."

    execute_query(
        "DELETE FROM clubs WHERE name = ?",
        (name,)
    )

    return "Клубът беше изтрит успешно."
