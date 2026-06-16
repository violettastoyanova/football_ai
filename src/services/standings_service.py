from repositories import standings_repo as repo
from collections import defaultdict


class StandingsCalculator:
    def __init__(self, league_name, season):
        self.league_name = league_name
        self.season = season
        self.league_id = repo.get_league_id(league_name, season)

        if not self.league_id:
            self.error = f"Лига '{league_name}' за сезон {season} не съществува."
            return

        self.error = None
        self.teams = {}  # id -> name
        self.stats = defaultdict(lambda: {
            'mp': 0, 'w': 0, 'd': 0, 'l': 0,
            'gf': 0, 'ga': 0, 'gd': 0, 'pts': 0
        })

    def calculate(self):
        """Изчислява класирането"""
        if self.error:
            return None, self.error

        # Вземаме отборите
        teams_data = repo.get_teams_in_league(self.league_id)
        if not teams_data:
            return None, f"Няма отбори в лига '{self.league_name}' за сезон {self.season}."

        for club_id, name in teams_data:
            self.teams[club_id] = name

        # Вземаме изиграните мачове
        matches = repo.get_played_matches_for_league(self.league_id)

        if not matches:
            # Връщаме празна таблица
            standings = []
            for club_id, name in self.teams.items():
                standings.append({
                    'name': name,
                    'club_id': club_id,
                    'mp': 0, 'w': 0, 'd': 0, 'l': 0,
                    'gf': 0, 'ga': 0, 'gd': 0, 'pts': 0
                })
            return standings, "Няма изиграни мачове за тази лига."

        # Обработваме всеки мач
        for match in matches:
            home_id, away_id, home_goals, away_goals = match

            # Домакин
            self.stats[home_id]['mp'] += 1
            self.stats[home_id]['gf'] += home_goals
            self.stats[home_id]['ga'] += away_goals

            # Гост
            self.stats[away_id]['mp'] += 1
            self.stats[away_id]['gf'] += away_goals
            self.stats[away_id]['ga'] += home_goals

            # Определяме резултат
            if home_goals > away_goals:
                self.stats[home_id]['w'] += 1
                self.stats[away_id]['l'] += 1
                self.stats[home_id]['pts'] += 3
            elif home_goals < away_goals:
                self.stats[away_id]['w'] += 1
                self.stats[home_id]['l'] += 1
                self.stats[away_id]['pts'] += 3
            else:
                self.stats[home_id]['d'] += 1
                self.stats[away_id]['d'] += 1
                self.stats[home_id]['pts'] += 1
                self.stats[away_id]['pts'] += 1

        # Изчисляваме голова разлика
        for club_id in self.stats:
            self.stats[club_id]['gd'] = self.stats[club_id]['gf'] - self.stats[club_id]['ga']

        # Подготовка за сортиране
        standings = []
        for club_id, name in self.teams.items():
            stats = self.stats.get(club_id, {
                'mp': 0, 'w': 0, 'd': 0, 'l': 0,
                'gf': 0, 'ga': 0, 'gd': 0, 'pts': 0
            })
            standings.append({
                'name': name,
                'club_id': club_id,
                **stats
            })

        return standings, None

    def sort_standings(self, standings):
        """Сортира класирането по правилата (с директни срещи за отличен)"""
        # Първо сортираме по основни критерии
        standings.sort(key=lambda x: (-x['pts'], -x['gd'], -x['gf'], x['name']))

        # Отличен критерий: Директни срещи при равни точки
        i = 0
        while i < len(standings):
            # Намираме група с равни точки
            j = i
            while j < len(standings) and standings[j]['pts'] == standings[i]['pts']:
                j += 1

            if j - i > 1:  # Има равенство
                tied_teams = standings[i:j]
                team_ids = [t['club_id'] for t in tied_teams]

                # Вземаме директните срещи
                h2h_matches = repo.get_head_to_head_matches(self.league_id, team_ids)

                # Изчисляваме статистика само за директните срещи
                h2h_stats = defaultdict(lambda: {'pts': 0, 'gd': 0, 'gf': 0})

                for match in h2h_matches:
                    home_id, away_id, home_goals, away_goals = match
                    if home_id in team_ids and away_id in team_ids:
                        # И двата отбора са от групата
                        if home_goals > away_goals:
                            h2h_stats[home_id]['pts'] += 3
                            h2h_stats[home_id]['gf'] += home_goals
                            h2h_stats[home_id]['gd'] += (home_goals - away_goals)
                            h2h_stats[away_id]['gf'] += away_goals
                            h2h_stats[away_id]['gd'] += (away_goals - home_goals)
                        elif home_goals < away_goals:
                            h2h_stats[away_id]['pts'] += 3
                            h2h_stats[home_id]['gf'] += home_goals
                            h2h_stats[home_id]['gd'] += (home_goals - away_goals)
                            h2h_stats[away_id]['gf'] += away_goals
                            h2h_stats[away_id]['gd'] += (away_goals - home_goals)
                        else:
                            h2h_stats[home_id]['pts'] += 1
                            h2h_stats[away_id]['pts'] += 1
                            h2h_stats[home_id]['gf'] += home_goals
                            h2h_stats[away_id]['gf'] += away_goals

                # Сортираме групата по H2H
                tied_teams.sort(
                    key=lambda x: (
                        -h2h_stats.get(x['club_id'], {}).get('pts', 0),
                        -h2h_stats.get(x['club_id'], {}).get('gd', 0),
                        -h2h_stats.get(x['club_id'], {}).get('gf', 0),
                        x['name']
                    )
                )

                # Заместваме обратно
                standings[i:j] = tied_teams

            i = j

        return standings


def get_standings(league_name, season):
    """Главна функция за получаване на класиране"""
    calculator = StandingsCalculator(league_name, season)
    standings, error = calculator.calculate()

    if error:
        return error

    if not standings:
        return f"Няма отбори в лига '{league_name}' за сезон {season}."

    # Сортираме
    sorted_standings = calculator.sort_standings(standings)

    # Форматираме изхода
    result = f"\n{'=' * 70}\n"
    result += f" КЛАСИРАНЕ - Лига '{league_name}' (сезон {season})\n"
    result += f"{'=' * 70}\n"
    result += f"{'#':<3} {'Отбор':<25} {'M':>3} {'W':>3} {'D':>3} {'L':>3} {'GF:GA':>10} {'GD':>4} {'PTS':>4}\n"
    result += f"{'-' * 70}\n"

    for idx, team in enumerate(sorted_standings, 1):
        result += f"{idx:<3} {team['name']:<25} "
        result += f"{team['mp']:>3} {team['w']:>3} {team['d']:>3} {team['l']:>3} "
        result += f"{team['gf']:>2}:{team['ga']:<2} {team['gd']:>5} {team['pts']:>4}\n"

    result += f"{'=' * 70}"
    return result