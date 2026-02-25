import sqlite3
import os




BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "football.db")




def get_connection():
   try:
       conn = sqlite3.connect(DB_PATH)
       conn.execute("PRAGMA foreign_keys = ON;")
       return conn
   except sqlite3.Error as e:
       print("Грешка при връзка с базата:", e)




def initialize_database():
   schema_path = os.path.join(PROJECT_ROOT, "sql", "schema.sql")


   if not os.path.exists(schema_path):
       print("schema.sql не е намерен.")
       return


   conn = get_connection()


   with open(schema_path, "r", encoding="utf-8") as file:
       schema_sql = file.read()


   conn.executescript(schema_sql)
   conn.commit()
   conn.close()




def execute_query(query, params=(), fetch=False):
   try:
       conn = get_connection()
       cursor = conn.cursor()
       cursor.execute(query, params)


       if fetch:
           result = cursor.fetchall()
           conn.close()
           return result


       conn.commit()
       conn.close()
       return True


   except sqlite3.Error as e:
       return f"Database error: {e}"
