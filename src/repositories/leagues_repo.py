from database.db import get_connection, execute_query


# ===============================
# LEAGUES
# ===============================

def create_league(name, season):
    """Създава нова лига"""
    conn = None
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO leagues (name, season) VALUES (?, ?)",
            (name, season)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error in create_league: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_league_by_name_season(name, season):
    """Връща league_id или None"""
    result = execute_query(
        "SELECT league_id, name, season FROM leagues WHERE name = ? AND season = ?",
        (name, season),
        fetch=True
    )
    return result[0] if result else None


def get_all_leagues():
    """Връща всички лиги"""
    return execute_query(
        "SELECT league_id, name, season, created_at FROM leagues ORDER BY created_at DESC",
        fetch=True
    )


def delete_league(league_id):
    """Изтрива лига (каскадно - трие и league_teams и matches)"""
    return execute_query("DELETE FROM leagues WHERE league_id = ?", (league_id,))


# ===============================
# LEAGUE TEAMS
# ===============================

def add_team_to_league(league_id, club_id):
    """Добавя отбор към лига"""
    conn = None
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO league_teams (league_id, club_id) VALUES (?, ?)",
            (league_id, club_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error in add_team_to_league: {e}")
        return False
    finally:
        if conn:
            conn.close()


def remove_team_from_league(league_id, club_id):
    """Премахва отбор от лига"""
    conn = None
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM league_teams WHERE league_id = ? AND club_id = ?",
            (league_id, club_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error in remove_team_from_league: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_league_teams(league_id):
    """Връща всички отбори в лига с техните данни"""
    return execute_query(
        """SELECT c.club_id, c.name, c.city, c.founded_year 
           FROM league_teams lt
           JOIN clubs c ON lt.club_id = c.club_id
           WHERE lt.league_id = ?
           ORDER BY c.name""",
        (league_id,),
        fetch=True
    )


def get_teams_count(league_id):
    """Брой отбори в лига"""
    result = execute_query(
        "SELECT COUNT(*) FROM league_teams WHERE league_id = ?",
        (league_id,),
        fetch=True
    )
    return result[0][0] if result else 0


def check_team_in_league(league_id, club_id):
    """Проверява дали отбор е в лига"""
    result = execute_query(
        "SELECT 1 FROM league_teams WHERE league_id = ? AND club_id = ?",
        (league_id, club_id),
        fetch=True
    )
    return len(result) > 0 if result else False


# ===============================
# MATCHES (за лиги)
# ===============================

def check_existing_schedule(league_id):
    """Проверява дали вече има генерирана програма за лига"""
    result = execute_query(
        "SELECT 1 FROM matches WHERE league_id = ? LIMIT 1",
        (league_id,),
        fetch=True
    )
    return len(result) > 0 if result else False


def delete_matches_for_league(league_id):
    """Изтрива всички мачове за дадена лига"""
    conn = None
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("DELETE FROM matches WHERE league_id = ?", (league_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error in delete_matches_for_league: {e}")
        return False
    finally:
        if conn:
            conn.close()


def create_matches_batch(matches_data):
    """
    Записва много мачове наведнъж
    matches_data: list of (league_id, round_no, home_club_id, away_club_id)
    """
    conn = None
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()

        for match in matches_data:
            league_id, round_no, home_id, away_id = match
            cursor.execute(
                """INSERT INTO matches (league_id, round_no, home_club_id, away_club_id)
                   VALUES (?, ?, ?, ?)""",
                (league_id, round_no, home_id, away_id)
            )

        conn.commit()
        return True

    except Exception as e:
        print(f"Transaction error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_matches_for_league(league_id):
    """Връща всички мачове за лига, подредени по кръг"""
    return execute_query(
        """SELECT m.round_no, 
                  h.name as home_team, 
                  a.name as away_team
           FROM matches m
           JOIN clubs h ON m.home_club_id = h.club_id
           JOIN clubs a ON m.away_club_id = a.club_id
           WHERE m.league_id = ?
           ORDER BY m.round_no, m.match_id""",
        (league_id,),
        fetch=True
    )