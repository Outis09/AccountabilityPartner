# import sqlite
import sqlite3

def initialize_database():
    """
    Initialize db and create necessary tables
    """
    # connect to accountability.db if exists or create if otherwise
    conn = sqlite3.connect("accountability.db")
    cursor = conn.cursor()

    # create habits table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   start_date TEXT,
                   frequency TEXT,
                   category TEXT,
                   tracking_type TEXT,
                   notes TEXT,
                   end_date TEXT, 
                   created_at TEXT NOT NULL DEFAULT current_timestamp
                   )
    """)

    # # create activity logs table
    # cursor.execute("""""
    #     CREATE TABLE IF NOT EXISTS activity_logs
    #                """)

    # create categories table

    conn.commit()
    conn.close()



