PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS cards;
DROP TABLE IF EXISTS goals;
DROP TABLE IF EXISTS transfers;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS clubs;
DROP TABLE IF EXISTS league_teams;
DROP TABLE IF EXISTS leagues;


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
-- TABLE: players
---------------------------------------------------
CREATE TABLE IF NOT EXISTS players (
  player_id INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name TEXT NOT NULL,
  birth_date TEXT NOT NULL,
  nationality TEXT NOT NULL,
  position TEXT NOT NULL CHECK(position IN ('Вратар','Защитник','Полузащитник','Нападател')),
  number INTEGER NOT NULL CHECK(number BETWEEN 1 AND 99),
  status TEXT NOT NULL DEFAULT 'активен',
  club_id INTEGER NOT NULL,
  FOREIGN KEY (club_id) REFERENCES clubs(club_id)
      ON DELETE CASCADE
);


---------------------------------------------------
-- TABLE: leagues
---------------------------------------------------
CREATE TABLE IF NOT EXISTS leagues (
  league_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  season TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(name, season)
);


---------------------------------------------------
-- TABLE: league_teams
---------------------------------------------------
CREATE TABLE IF NOT EXISTS league_teams (
  league_id INTEGER NOT NULL,
  club_id INTEGER NOT NULL,
  joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (league_id, club_id),
  FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE,
  FOREIGN KEY (club_id) REFERENCES clubs(club_id) ON DELETE CASCADE
);


---------------------------------------------------
-- TABLE: matches (пълна версия за етап 6)
---------------------------------------------------
CREATE TABLE IF NOT EXISTS matches (
  match_id INTEGER PRIMARY KEY AUTOINCREMENT,
  home_club_id INTEGER NOT NULL,
  away_club_id INTEGER NOT NULL,
  match_date TEXT,
  home_goals INTEGER DEFAULT NULL,
  away_goals INTEGER DEFAULT NULL,
  league_id INTEGER,
  round_no INTEGER,
  status TEXT DEFAULT 'scheduled',
  FOREIGN KEY (home_club_id) REFERENCES clubs(club_id),
  FOREIGN KEY (away_club_id) REFERENCES clubs(club_id),
  FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE
);


---------------------------------------------------
-- TABLE: goals (НОВО за етап 6)
---------------------------------------------------
CREATE TABLE IF NOT EXISTS goals (
  goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
  match_id INTEGER NOT NULL,
  player_id INTEGER NOT NULL,
  club_id INTEGER NOT NULL,
  minute INTEGER NOT NULL CHECK(minute BETWEEN 1 AND 120),
  is_own_goal INTEGER DEFAULT 0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
  FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
  FOREIGN KEY (club_id) REFERENCES clubs(club_id) ON DELETE CASCADE
);


---------------------------------------------------
-- TABLE: cards (НОВО за етап 6)
---------------------------------------------------
CREATE TABLE IF NOT EXISTS cards (
  card_id INTEGER PRIMARY KEY AUTOINCREMENT,
  match_id INTEGER NOT NULL,
  player_id INTEGER NOT NULL,
  club_id INTEGER NOT NULL,
  minute INTEGER NOT NULL CHECK(minute BETWEEN 1 AND 120),
  card_type TEXT NOT NULL CHECK(card_type IN ('Y', 'R')),
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
  FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
  FOREIGN KEY (club_id) REFERENCES clubs(club_id) ON DELETE CASCADE
);


---------------------------------------------------
-- TABLE: transfers
---------------------------------------------------
CREATE TABLE IF NOT EXISTS transfers (
  transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
  player_id INTEGER NOT NULL,
  from_club_id INTEGER,
  to_club_id INTEGER NOT NULL,
  transfer_date TEXT NOT NULL,
  fee REAL CHECK(fee >= 0),
  note TEXT,
  CHECK (to_club_id != from_club_id),
  FOREIGN KEY (player_id) REFERENCES players(player_id),
  FOREIGN KEY (from_club_id) REFERENCES clubs(club_id),
  FOREIGN KEY (to_club_id) REFERENCES clubs(club_id)
);


---------------------------------------------------
-- SEED DATA: clubs
---------------------------------------------------
INSERT OR IGNORE INTO clubs (name, city, founded_year) VALUES
('Левски', 'София', 1914),
('ЦСКА', 'София', 1948),
('Лудогорец', 'Разград', 2001),
('Ботев', 'Пловдив', 1912),
('Черно море', 'Варна', 1913),
('Спартак', 'Варна', 1918),
('Арда', 'Кърджали', 1924),
('Славия', 'София', 1913),
('Локомотив', 'Пловдив', 1926),
('Берое', 'Стара Загора', 1916);


---------------------------------------------------
-- SEED DATA: players
---------------------------------------------------
INSERT OR IGNORE INTO players
(full_name, birth_date, nationality, position, number, status, club_id)
VALUES
-- ЛЕВСКИ
('Иван Петров', '1998-05-12', 'България', 'Нападател', 9, 'активен', 1),
('Николай Стоянов', '2001-01-15', 'България', 'Вратар', 1, 'активен', 1),
('Мартин Петров', '1999-07-20', 'България', 'Полузащитник', 10, 'активен', 1),
('Александър Иванов', '2002-11-05', 'България', 'Защитник', 5, 'активен', 1),
('Димитър Георгиев', '2000-02-28', 'България', 'Нападател', 7, 'активен', 1),

-- ЦСКА
('Георги Иванов', '1995-03-22', 'България', 'Полузащитник', 8, 'активен', 2),
('Даниел Колев', '1997-08-19', 'България', 'Защитник', 4, 'активен', 2),
('Стойчо Стоев', '1998-09-15', 'България', 'Нападател', 9, 'активен', 2),
('Йордан Йорданов', '2001-03-10', 'България', 'Вратар', 12, 'активен', 2),

-- ЛУДОГОРЕЦ
('Марио Соуза', '1997-07-11', 'Бразилия', 'Нападател', 10, 'активен', 3),
('Алекс Сантос', '1999-09-09', 'Бразилия', 'Защитник', 5, 'контузен', 3),
('Калоян Колев', '1997-12-01', 'България', 'Защитник', 15, 'активен', 3),
('Ивайло Димитров', '2000-06-18', 'България', 'Полузащитник', 20, 'активен', 3),

-- БОТЕВ
('Петър Димитров', '2000-03-14', 'България', 'Полузащитник', 7, 'активен', 4),
('Хуан Карлос', '1996-12-02', 'Испания', 'Нападател', 11, 'активен', 4),
('Антон Антонов', '1999-04-25', 'България', 'Вратар', 22, 'активен', 4),
('Васил Василев', '2001-08-14', 'България', 'Защитник', 18, 'активен', 4),

-- ЧЕРНО МОРЕ
('Стефан Илиев', '1998-06-30', 'България', 'Защитник', 3, 'активен', 5),
('Роберто Силва', '1994-04-18', 'Португалия', 'Полузащитник', 6, 'активен', 5),
('Николай Николов', '1998-10-30', 'България', 'Нападател', 14, 'активен', 5),
('Петър Петров', '2002-01-22', 'България', 'Полузащитник', 19, 'активен', 5),
('Георги Георгиев', '2000-05-09', 'България', 'Защитник', 8, 'активен', 5),

-- СПАРТАК
('Спартак Спасов', '1999-11-11', 'България', 'Нападател', 11, 'активен', 6),
('Владимир Владимиров', '2001-07-07', 'България', 'Защитник', 4, 'активен', 6),
('Кристиян Кръстев', '2000-12-24', 'България', 'Вратар', 1, 'активен', 6),

-- АРДА
('Емил Емилов', '2000-03-15', 'България', 'Нападател', 9, 'активен', 7),
('Димитър Димитров', '1999-06-20', 'България', 'Защитник', 5, 'активен', 7),

-- СЛАВИЯ
('Славчо Славчев', '1998-04-10', 'България', 'Полузащитник', 8, 'активен', 8),
('Румен Руменов', '2001-09-25', 'България', 'Вратар', 1, 'активен', 8),

-- ЛОКОМОТИВ
('Лъчезар Лъчев', '1997-11-30', 'България', 'Нападател', 10, 'активен', 9),
('Пламен Пламенов', '2000-07-18', 'България', 'Защитник', 3, 'активен', 9),

-- БЕРОЕ
('Бероев Борис', '1999-02-14', 'България', 'Полузащитник', 7, 'активен', 10),
('Стоян Стоянов', '2002-08-08', 'България', 'Нападател', 11, 'активен', 10);


---------------------------------------------------
-- SEED DATA: leagues
---------------------------------------------------
INSERT OR IGNORE INTO leagues (name, season) VALUES
('Първа лига', '2025/2026'),
('Втора лига', '2025/2026'),
('Трета лига', '2025/2026'),
('Младежка лига', '2025/2026');


---------------------------------------------------
-- SEED DATA: league_teams (добавяне на отбори в лигите)
---------------------------------------------------

-- Първа лига - отбори
INSERT OR IGNORE INTO league_teams (league_id, club_id)
SELECT l.league_id, c.club_id
FROM leagues l, clubs c
WHERE l.name = 'Първа лига'
  AND l.season = '2025/2026'
  AND c.name IN ('Левски', 'ЦСКА', 'Лудогорец', 'Ботев');

-- Втора лига - отбори
INSERT OR IGNORE INTO league_teams (league_id, club_id)
SELECT l.league_id, c.club_id
FROM leagues l, clubs c
WHERE l.name = 'Втора лига'
  AND l.season = '2025/2026'
  AND c.name IN ('Черно море', 'Спартак', 'Левски', 'ЦСКА', 'Арда', 'Славия');

-- Трета лига - отбори
INSERT OR IGNORE INTO league_teams (league_id, club_id)
SELECT l.league_id, c.club_id
FROM leagues l, clubs c
WHERE l.name = 'Трета лига'
  AND l.season = '2025/2026'
  AND c.name IN ('Ботев', 'Лудогорец', 'Черно море', 'Спартак', 'Локомотив', 'Берое');


---------------------------------------------------
-- SEED DATA: transfers
---------------------------------------------------
INSERT OR IGNORE INTO transfers
(player_id, from_club_id, to_club_id, transfer_date, fee)
VALUES
(1, 1, 3, '2024-01-10', 50000),
(3, 2, 1, '2024-02-15', 30000),
(5, 3, 2, '2024-03-20', 70000),
(9, 5, 4, '2024-05-30', 15000),
(8, 4, 3, '2024-06-12', 40000);