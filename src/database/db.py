import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../.."))
DB_PATH = os.path.join(PROJECT_ROOT, "football.db")


def get_connection():
   try:
       conn = sqlite3.connect(DB_PATH, timeout=20)
       conn.execute("PRAGMA foreign_keys = ON;")
       return conn
   except sqlite3.Error as e:
       print("Грешка при връзка с базата:", e)
       return None


def initialize_database():
   schema_path = os.path.join(PROJECT_ROOT, "sql", "schema.sql")

   if not os.path.exists(schema_path):
       print("schema.sql не е намерен.")
       return

   conn = get_connection()
   if not conn:
       return

   try:
       with open(schema_path, "r", encoding="utf-8") as file:
           schema_sql = file.read()

       conn.executescript(schema_sql)
       conn.commit()
       # Премахнат print
   except Exception as e:
       print(f"Error initializing database: {e}")
   finally:
       conn.close()


def upgrade_database():
    """Надгражда базата данни с новите таблици за етап 6"""
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        # Проверка и добавяне на колона status в matches
        cursor.execute("PRAGMA table_info(matches)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'status' not in columns:
            cursor.execute("ALTER TABLE matches ADD COLUMN status TEXT DEFAULT 'scheduled'")
            # Премахнат print

        # Създаване на таблица goals
        cursor.execute("""
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
            )
        """)
        # Премахнат print

        # Създаване на таблица cards
        cursor.execute("""
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
            )
        """)
        # Премахнат print

        conn.commit()
        # Премахнат print
    except Exception as e:
        print(f"Error upgrading database: {e}")
    finally:
        conn.close()


def execute_query(query, params=(), fetch=False):
   conn = None
   try:
       conn = get_connection()
       if not conn:
           return "Database connection failed"

       cursor = conn.cursor()
       cursor.execute(query, params)

       if fetch:
           result = cursor.fetchall()
           return result

       conn.commit()
       return True

   except sqlite3.Error as e:
       return f"Database error: {e}"
   finally:
       if conn:
           conn.close()
