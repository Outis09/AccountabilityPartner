import pandas as pd
import streamlit as st
from supabase import create_client, Client
from datetime import date, timedelta


# initialize supabase client
def init_supabase():
    url=st.secrets["SUPABASE_URL"]
    key=st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# function to get user data
# @st.cache_data
def get_data(user_id):
    """Fetch user data from the database."""
    # get supabase client
    supabase = st.session_state.supabase
    if user_id is None:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    habits =  supabase.table("habits").select("*").eq("user_id", user_id).execute()
    activities = supabase.table("activity_logs").select("*").eq("user_id", user_id).execute()
    habits_df = pd.DataFrame(habits.data)
    activities_df = pd.DataFrame(activities.data)
    if habits_df.empty or activities_df.empty:
        return habits_df, activities_df, pd.DataFrame()
    else:
        merged_df = pd.merge(activities_df, habits_df, on='habit_id', how='left')
        merged_df['log_date'] = pd.to_datetime(merged_df['log_date'])
        # merged_df.drop(columns='name_y', inplace=True)
        # merged_df.rename(columns={'name_x':'name'}, inplace=True)
        return habits_df, activities_df, merged_df
    

# get distinct categories
@st.cache_data
def get_categories(user_id):
    """Fetch distinct categories from the database."""
    # get supabase client
    supabase = st.session_state.supabase
    if user_id is None:
        return []
    categories = supabase.table("habits").select("category").eq("user_id", user_id).execute()
    categories_df = pd.DataFrame(categories.data)
    return categories_df['category'].dropna().unique().tolist()

# get distinct habits for a category
@st.cache_data 
def get_habits(user_id, category):
    """Fetch distinct habits and tracking types for a category from the database."""
    supabase = st.session_state.supabase
    if user_id is None or category is None:
        return {}
    habits = supabase.table("habits").select("name, tracking_type").eq("user_id", user_id).eq("category", category).execute()
    habits_df = pd.DataFrame(habits.data)
    if habits_df.empty:
        return {}
    return dict(zip(habits_df["name"], habits_df["tracking_type"]))


# get habit id
@st.cache_data
def get_habit_id(user_id, habit_name):
    """Fetch habit id for a habit name from the database."""
    # get supabase client
    supabase = st.session_state.supabase
    if user_id is None or habit_name is None:
        return None
    habit = supabase.table("habits").select("habit_id").eq("user_id", user_id).eq("name", habit_name).execute()
    habit_df = pd.DataFrame(habit.data)
    if not habit_df.empty:
        return habit_df['habit_id'].values[0]
    else:
        return None
    
# insert activity log
def insert_activity_log(user_id, habit_id, log_date, activity, rating, log_notes):
    """Insert activity log into the database."""
    # get supabase client
    supabase = st.session_state.supabase
    if user_id is None or habit_id is None:
        return False
    data = {
        "user_id": user_id,
        "habit_id": habit_id,
        "log_date": log_date.isoformat(),
        "activity": activity,
        "rating": rating,
        "log_notes": log_notes
    }
    response = supabase.table("activity_logs").insert(data).execute()
    if response.data:
        return True
    else:
        return False
    
# insert habit
def insert_habit(user_id, name, start_date, frequency, tracking_type, goal, goal_units, category, notes, end_date=None):
    """Insert habit into the database."""
    # get supabase client
    supabase = st.session_state.supabase
    if user_id is None:
        return False
    data = {
        "user_id": user_id,
        "name": name,
        "start_date": start_date,
        "frequency": frequency,
        "tracking_type": tracking_type,
        "goal": goal,
        "goal_units": goal_units,
        "category": category,
        "notes": notes,
        "end_date": end_date
    }
    response = supabase.table("habits").insert(data).execute()
    if response.data:
        return True
    else:
        return False
    
# get unlogged activities
def get_unlogged_activities(user_id):
    """Fetch activities that are due for the user."""
    # get supabase client
    supabase = st.session_state.supabase
    if user_id is None:
        return [], [], []
    # today
    today = date.today()
    # convert to iso format
    today_iso = today.isoformat()
    # start of the week
    start_of_week = today - timedelta(days=today.weekday())
    # start of the month
    start_of_month = today.replace(day=1)
    # get all habits
    habits = supabase.table("habits").select("*").eq("user_id", user_id).execute().data
    # if no habits, return empty lists
    if not habits:
        return [], [], []
    # get all activities for this month
    recent_logs = supabase.table("activity_logs")\
        .select("*")\
        .eq("user_id", user_id)\
        .gte("log_date", start_of_month)\
        .execute()\
        .data
    # list to hold unlogged activities
    daily_activities = []
    weekly_activities = []
    monthly_activities = []
    # loop through habits
    for habit in habits:
        # get habit details
        habit_id = habit['habit_id']
        habit_name = habit['name']
        habit_frequency = habit['frequency']
        if habit_frequency == "Daily":
            # check if activity is logged for today
            if not any(log['habit_id'] == habit_id and log['log_date'] == today_iso for log in recent_logs):
                daily_activities.append(habit_name)
        elif habit_frequency == "Weekly":
            # check if activity is logged for this week
            if not any(log['habit_id'] == habit_id and log['log_date'] >= start_of_week.isoformat() for log in recent_logs):
                weekly_activities.append(habit_name)
        elif habit_frequency == "Monthly":
            # check if activity is logged for this month
            if not any(log['habit_id'] == habit_id and log['log_date'] >= start_of_month.isoformat() for log in recent_logs):
                monthly_activities.append(habit_name)
    # return activities
    return daily_activities, weekly_activities, monthly_activities

