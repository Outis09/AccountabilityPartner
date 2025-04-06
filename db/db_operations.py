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

def get_categories():
    """Get valid categories from database"""
    # connect to db
    conn = sqlite3.connect(db)
    # create cursor for executing queries
    cursor = conn.cursor()
    # query to get categories
    cursor.execute("""
            SELECT category 
            FROM habits 
            WHERE end_date IS NULL OR end_date < current_timestamp
    """)
    valid_categories = [row[0] for row in cursor.fetchall()]
    # commit changes
    conn.commit()
    conn.close()
    return valid_categories

