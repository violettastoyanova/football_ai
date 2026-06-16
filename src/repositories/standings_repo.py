from database.db import execute_query


def get_league_id(name, season):
    """Връща league_id по име и сезон"""
    result = execute_query(
        "SELECT league_id FROM leagues WHERE name = ? AND season = ?",
        (name, season),
        fetch=True
    )
    return result[0][0] if result else None


def get_teams_in_league(league_id):
    """Връща всички отбори в лига"""
    return execute_query(
        """SELECT c.club_id, c.name
           FROM league_teams lt
           JOIN clubs c ON lt.club_id = c.club_id
           WHERE lt.league_id = ?
           ORDER BY c.name""",
        (league_id,),
        fetch=True
    )


def get_played_matches_for_league(league_id):
    """Връща всички изиграни мачове за лига"""
    return execute_query(
        """SELECT m.home_club_id, m.away_club_id, 
                  m.home_goals, m.away_goals
           FROM matches m
           WHERE m.league_id = ? AND m.status = 'played'
           AND m.home_goals IS NOT NULL AND m.away_goals IS NOT NULL""",
        (league_id,),
        fetch=True
    )


def get_head_to_head_matches(league_id, team_ids):
    """Връща директните срещи между дадени отбори"""
    if not team_ids:
        return []

    placeholders = ','.join(['?'] * len(team_ids))
    query = f"""
        SELECT m.home_club_id, m.away_club_id, 
               m.home_goals, m.away_goals
        FROM matches m
        WHERE m.league_id = ? AND m.status = 'played'
        AND m.home_club_id IN ({placeholders}) 
        AND m.away_club_id IN ({placeholders})
        AND m.home_goals IS NOT NULL AND m.away_goals IS NOT NULL
    """
    params = [league_id] + team_ids + team_ids
    return execute_query(query, tuple(params), fetch=True)