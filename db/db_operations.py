# import sqlite for db executions
import sqlite3

# db name
db = 'accountability.db'

# function to save habits
def insert_habit(name, start_date, frequency, category, notes, end_date):
    # connect to db
    conn = sqlite3.connect(db)
    # create cursor for executing queries
    cursor = conn.cursor()

    # insert values
    cursor.execute("""
            INSERT INTO habits(name, start_date, frequency, category, notes, end_date)
            VALUES (?,?,?,?,?,?)
    """, (name, start_date, frequency, category, notes, end_date))

    # commit changes
    conn.commit()
    conn.close()
