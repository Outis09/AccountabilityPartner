# import sqlite for db executions
import sqlite3

# db name
db = 'accountability.db'

# function to save habits
def insert_habit(name, start_date, frequency, tracking,goal, goal_units, category, notes, end_date):
    # connect to db
    conn = sqlite3.connect(db)
    # create cursor for executing queries
    cursor = conn.cursor()

    # insert values
    cursor.execute("""
            INSERT INTO habits(name, start_date, frequency, tracking_type, category, notes, end_date)
            VALUES (?,?,?,?,?,?,?)
    """, (name, start_date, frequency, tracking,goal, goal_units, category, notes, end_date))

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
            WHERE end_date IS NULL OR end_date > current_timestamp
    """)
    valid_categories = [row[0] for row in cursor.fetchall()]
    # commit changes
    conn.commit()
    conn.close()
    return valid_categories

def get_habits(category):
    """Get habits that fall under a category"""
    # connect to db
    conn = sqlite3.connect(db)
    # create cursor for executing queries
    cursor = conn.cursor()
    # query to get categories
    cursor.execute("""
            SELECT name, frequency 
            FROM habits 
            WHERE category = (?) AND (end_date IS NULL OR end_date > current_timestamp)
    """, (category,))
    # store selected habits
    rows = cursor.fetchall()
    # commit changes and close connection
    conn.commit()
    conn.close()
    # dict with habit details
    habit_details = {name: frequency for name,frequency in rows}
    return habit_details

def get_habit_id(habit):
    """Get habit id for a given habit"""
    # connect to db
    conn = sqlite3.connect(db)
    # create cursor for executing categories
    cursor = conn.cursor()
    # query to get habit_id
    cursor.execute("""
        SELECT habit_id
        FROM habits
        WHERE name = (?)
        """, (habit,))
    id = [row[0] for row in cursor.fetchall()]
    conn.close()
    return id


    



