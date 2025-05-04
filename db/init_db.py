# import sqlite
import sqlite3

def initialize_database():
    """
    Initialize db and create necessary tables
    """
    # connect to accountability.db if exists or create if otherwise
    conn = sqlite3.connect("data/accountability.db")
    cursor = conn.cursor()

    # create habits table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits(
                   habit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   start_date TEXT,
                   frequency TEXT,
                   category TEXT,
                   tracking_type TEXT,
                   goal REAL,
                   goal_units TEXT,
                   notes TEXT,
                   end_date TEXT, 
                   created_at TEXT NOT NULL DEFAULT current_timestamp
                   )
    """)

    # create activity logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs(
                   log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   habit_id INTEGER NOT NULL,
                   log_date TEXT NOT NULL,
                   activity TEXT NOT NULL,
                   rating INTEGER NOT NULL,
                   log_notes TEXT,
                   created_at TEXT DEFAULT CURRENT_TIMESTAMP
                   )
                   """)

    # create categories table

    conn.commit()
    conn.close()



initialize_database()