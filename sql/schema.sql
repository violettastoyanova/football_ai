PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS clubs (
    club_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    city TEXT NOT NULL,
    founded_year INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    nationality TEXT NOT NULL,
    position TEXT NOT NULL,
    number INTEGER NOT NULL,
    club_id INTEGER NOT NULL,
    FOREIGN KEY (club_id) REFERENCES clubs(club_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    home_club_id INTEGER NOT NULL,
    away_club_id INTEGER NOT NULL,
    match_date TEXT NOT NULL,
    home_goals INTEGER DEFAULT 0,
    away_goals INTEGER DEFAULT 0,
    FOREIGN KEY (home_club_id) REFERENCES clubs(club_id),
    FOREIGN KEY (away_club_id) REFERENCES clubs(club_id)
);

INSERT OR IGNORE INTO clubs (name, city, founded_year) VALUES
('Левски', 'София', 1914),
('ЦСКА', 'София', 1948),
('Лудогорец', 'Разград', 2001),
('Ботев', 'Пловдив', 1912),
('Черно море', 'Варна', 1913);

INSERT OR IGNORE INTO players
(first_name, last_name, birth_date, nationality, position, number, club_id)
VALUES
('Иван', 'Петров', '1998-05-12', 'България', 'Нападател', 9, 1),
('Георги', 'Иванов', '1995-03-22', 'България', 'Полузащитник', 8, 2),
('Марио', 'Соуза', '1997-07-11', 'Бразилия', 'Нападател', 10, 3);

INSERT OR IGNORE INTO matches
(home_club_id, away_club_id, match_date, home_goals, away_goals)
VALUES
(1, 2, '2024-10-10', 2, 1);