from database.db import get_connection, execute_query


def get_matches_by_league_and_round(league_id, round_no):
    """Връща всички мачове за дадена лига и кръг"""
    return execute_query(
        """SELECT m.match_id, m.home_club_id, h.name as home_name,
                  m.away_club_id, a.name as away_name,
                  m.home_goals, m.away_goals, m.status
         FROM matches m
         JOIN clubs h ON m.home_club_id = h.club_id
         JOIN clubs a ON m.away_club_id = a.club_id
         WHERE m.league_id = ? AND m.round_no = ?
         ORDER BY m.match_id""",
        (league_id, round_no),
        fetch=True
    )


def get_match_by_id(match_id):
    """Връща мач по ID"""
    result = execute_query(
        """SELECT m.match_id, m.league_id, l.name as league_name, l.season,
                  m.round_no, m.home_club_id, h.name as home_name,
                  m.away_club_id, a.name as away_name,
                  m.home_goals, m.away_goals, m.status
         FROM matches m
         JOIN leagues l ON m.league_id = l.league_id
         JOIN clubs h ON m.home_club_id = h.club_id
         JOIN clubs a ON m.away_club_id = a.club_id
         WHERE m.match_id = ?""",
        (match_id,),
        fetch=True
    )
    return result[0] if result else None


def get_match_by_teams(home_team_name, away_team_name, league_id=None):
    """Намира мач по имена на отбори, опционално в конкретна лига"""
    query = """SELECT m.match_id, m.league_id, l.name as league_name, l.season,
                      m.round_no, m.home_club_id, h.name as home_name,
                      m.away_club_id, a.name as away_name,
                      m.home_goals, m.away_goals, m.status
               FROM matches m
               JOIN leagues l ON m.league_id = l.league_id
               JOIN clubs h ON m.home_club_id = h.club_id
               JOIN clubs a ON m.away_club_id = a.club_id
               WHERE h.name = ? AND a.name = ?"""

    params = [home_team_name, away_team_name]

    if league_id:
        query += " AND m.league_id = ?"
        params.append(league_id)

    result = execute_query(query, tuple(params), fetch=True)
    return result[0] if result else None


def update_match_result(match_id, home_goals, away_goals, status='played'):
    """Обновява резултат на мач"""
    conn = None
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE matches SET home_goals = ?, away_goals = ?, status = ? WHERE match_id = ?",
            (home_goals, away_goals, status, match_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error in update_match_result: {e}")
        return False
    finally:
        if conn:
            conn.close()


def add_goal(match_id, player_id, club_id, minute, is_own_goal=0):
    """Добавя гол в базата"""
    conn = None
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO goals (match_id, player_id, club_id, minute, is_own_goal)
               VALUES (?, ?, ?, ?, ?)""",
            (match_id, player_id, club_id, minute, is_own_goal)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error in add_goal: {e}")
        return False
    finally:
        if conn:
            conn.close()


def add_card(match_id, player_id, club_id, minute, card_type):
    """Добавя картон в базата"""
    conn = None
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO cards (match_id, player_id, club_id, minute, card_type)
               VALUES (?, ?, ?, ?, ?)""",
            (match_id, player_id, club_id, minute, card_type)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error in add_card: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_match_events(match_id):
    """Връща всички събития (голове и картони) за мач"""
    # Взимаме головете
    goals = execute_query(
        """SELECT g.minute, 'goal' as type, p.full_name as player_name,
                  c.name as club_name, g.is_own_goal
         FROM goals g
         JOIN players p ON g.player_id = p.player_id
         JOIN clubs c ON g.club_id = c.club_id
         WHERE g.match_id = ?
         ORDER BY g.minute""",
        (match_id,),
        fetch=True
    )

    # Взимаме картоните
    cards = execute_query(
        """SELECT c.minute, 'card' as type, p.full_name as player_name,
                  cl.name as club_name, c.card_type
         FROM cards c
         JOIN players p ON c.player_id = p.player_id
         JOIN clubs cl ON c.club_id = cl.club_id
         WHERE c.match_id = ?
         ORDER BY c.minute""",
        (match_id,),
        fetch=True
    )

    return goals, cards


def get_league_id_by_name_season(name, season):
    """Връща league_id по име и сезон"""
    result = execute_query(
        "SELECT league_id FROM leagues WHERE name = ? AND season = ?",
        (name, season),
        fetch=True
    )
    return result[0][0] if result else None