PRAGMA foreign_keys = ON;

-- Ако искаш чисто презареждане
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS clubs;

---------------------------------------------------
-- TABLE: clubs
---------------------------------------------------
CREATE TABLE IF NOT EXISTS clubs (
    club_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    city TEXT NOT NULL,
    founded_year INTEGER NOT NULL
);

---------------------------------------------------
-- TABLE: players (ЕТАП 3 версия)
---------------------------------------------------
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    nationality TEXT NOT NULL,
    position TEXT NOT NULL CHECK(position IN ('Вратар','Защитник','Полузащитник','Нападател')),
    number INTEGER NOT NULL CHECK(number BETWEEN 1 AND 99),
    status TEXT NOT NULL DEFAULT 'active',
    club_id INTEGER NOT NULL,
    FOREIGN KEY (club_id) REFERENCES clubs(club_id)
        ON DELETE CASCADE
);

---------------------------------------------------
-- TABLE: matches
---------------------------------------------------
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

---------------------------------------------------
-- SEED DATA: clubs
---------------------------------------------------
INSERT OR IGNORE INTO clubs (name, city, founded_year) VALUES
('Левски', 'София', 1914),
('ЦСКА', 'София', 1948),
('Лудогорец', 'Разград', 2001),
('Ботев', 'Пловдив', 1912),
('Черно море', 'Варна', 1913);

---------------------------------------------------
-- SEED DATA: players (ЕТАП 3 структура)
---------------------------------------------------
INSERT OR IGNORE INTO players
(full_name, birth_date, nationality, position, number, status, club_id)
VALUES

-- ЛЕВСКИ
('Иван Петров', '1998-05-12', 'България', 'Нападател', 9, 'активен', 1),
('Николай Стоянов', '2001-01-15', 'България', 'Вратар', 1, 'активен', 1),

-- ЦСКА
('Георги Иванов', '1995-03-22', 'България', 'Полузащитник', 8, 'активен', 2),
('Даниел Колев', '1997-08-19', 'България', 'Защитник', 4, 'активен', 2),

-- ЛУДОГОРЕЦ
('Марио Соуза', '1997-07-11', 'Бразилия', 'Нападател', 10, 'активен', 3),
('Алекс Сантос', '1999-09-09', 'Бразилия', 'Защитник', 5, 'контузен', 3),

-- БОТЕВ
('Петър Димитров', '2000-03-14', 'България', 'Полузащитник', 7, 'активен', 4),
('Хуан Карлос', '1996-12-02', 'Испания', 'Нападател', 11, 'активен', 4),

-- ЧЕРНО МОРЕ
('Стефан Илиев', '1998-06-30', 'България', 'Защитник', 3, 'активен', 5),
('Роберто Силва', '1994-04-18', 'Португалия', 'Полузащитник', 6, 'активен', 5);


---------------------------------------------------
-- SEED DATA: matches
---------------------------------------------------
INSERT OR IGNORE INTO matches
(home_club_id, away_club_id, match_date, home_goals, away_goals)
VALUES
(1, 2, '2024-10-10', 2, 1),
(3, 4, '2024-11-02', 3, 0);
