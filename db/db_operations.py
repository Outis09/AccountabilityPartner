# import sqlite for db executions
import sqlite3
from tkinter import messagebox
import pandas as pd
import streamlit as st

# db name
db = 'data/accountability.db'

# function to save habits
def insert_habit(name, start_date, frequency, tracking,goal, goal_units, category, notes, end_date):
    # connect to db
    conn = sqlite3.connect(db)
    # create cursor for executing queries
    cursor = conn.cursor()

    # insert values
    cursor.execute("""
            INSERT INTO habits(name, start_date, frequency,category,tracking_type,goal, goal_units, notes, end_date)
            VALUES (?,?,?,?,?,?,?,?,?)
    """, (name, start_date, frequency,category, tracking,goal, goal_units, notes, end_date))

    # commit changes
    conn.commit()
    conn.close()

def insert_activity(habit_id,log_date,activity, rating, log_notes):
    # connect to db
    conn = sqlite3.connect(db)
    # create cursor for executing queries
    cursor = conn.cursor()
    # insert values
    cursor.execute("""
                INSERT INTO activity_logs(habit_id, log_date, activity, rating,log_notes)
                   VALUES (?,?,?,?,?)
        """, (habit_id, log_date, activity, rating, log_notes))
    # commit changes
    conn.commit()
    # close connection
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
            SELECT name, tracking_type
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
    id = cursor.fetchone()
    conn.close()
    return id[0]

def safe_db_call(db_function, *args, success_message="Operation Successful", framework='tkinter'):
    try:
        db_function(*args)
        if framework == 'tkinter':
            messagebox.showinfo("Success", success_message)
        elif framework == 'streamlit':
            st.success(success_message)
        return True
    except Exception as e:
        if framework == 'tkinter':
            if isinstance(e, sqlite3.IntegrityError):
                messagebox.showerror("Integrity Error", f"Data constraint violated: {e}")
            elif isinstance(e, sqlite3.OperationalError):
                messagebox.showerror("Operational Error", f"Database error: {e}")
            elif isinstance(e, sqlite3.ProgrammingError):
                messagebox.showerror("Programming Error", f"Code issue: {e}")
            else:
                messagebox.showerror("Database Error", f"An unexpected error occurred: {e}")
        elif framework == "streamlit":
            if isinstance(e, sqlite3.IntegrityError):
                st.error(f"Data constraint violated: {e}")
            elif isinstance(e, sqlite3.OperationalError):
                st.error(f"Database error: {e}")
            elif isinstance(e, sqlite3.ProgrammingError):
                st.error(f"Code issue: {e}")
            else:
                st.error(f"An unexpected database error occurred: {e}")
        return False

def get_all_habits_to_df():
    """Get all data for habits"""
        # connect to db
    conn = sqlite3.connect(db)
    # create cursor for executing categories
    cursor = conn.cursor()
    # query to get all habits data
    cursor.execute("""
    SELECT habit_id, name, start_date, frequency, category, tracking_type,goal, goal_units,notes, end_date
    FROM habits
    """)
    # get rows
    rows = cursor.fetchall()
    # get column names
    columns = [description[0] for description in cursor.description]
    # convert to dataframe
    habits_df = pd.DataFrame(rows, columns=columns)
    # close connection
    conn.close()
    return habits_df

def get_all_activity_logs():
    """Get all activity logs data"""
            # connect to db
    conn = sqlite3.connect(db)
    # create cursor for executing categories
    cursor = conn.cursor()
    # query to get all habits data
    cursor.execute("""
    SELECT a.log_id, a.habit_id, h.name, a.log_date, a.activity, a.rating, a.log_notes
    FROM activity_logs a
    JOIN habits h on a.habit_id = h.habit_id
    """)
    # get rows
    rows = cursor.fetchall()
    # get column names
    columns = [description[0] for description in cursor.description]
    # convert to dataframe
    activity_df = pd.DataFrame(rows, columns=columns)
    # close connection
    conn.close()
    return activity_df


    



