import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import calplot
# wordcloud
from wordcloud import WordCloud
from datetime import datetime

# set page config
st.set_page_config(
    page_title="Accountability Partner",
    page_icon="📊",
    layout="wide"
)

# page title
st.title("📊Activity Logs Visualization")

# create sample data
headers = ['log_id', 'habit_id', 'log_date', 'activity', 'rating', 'log_notes', 'created_at']
activity_logs_data = [
    (1, 1, "2025-04-01", "Yes", 5, "Felt great", "2025-04-01"),
    (2, 1, "2025-04-02", "Yes", 4, "Shorter run today", "2025-04-02"),
    (3, 2, "2025-04-01", "25", 3, "Almost made the 30-minute mark", "2025-04-01"),
    (4, 2, "2025-04-02", "30", 5, "Completed!", "2025-04-02"),
    (5, 3, "2025-04-01", "7", 4, "One short", "2025-04-01"),
    (6, 3, "2025-04-02", "8", 5, "Perfect", "2025-04-02"),
    (7, 4, "2025-04-01", "10", 3, "Distracted", "2025-04-01"),
    (8, 4, "2025-04-02", "15", 5, "Much better", "2025-04-02"),
    (9, 5, "2025-04-01", "Yes", 4, "On track", "2025-04-01"),
    (10, 6, "2025-04-01", "60", 5, "Wrote a new function", "2025-04-01"),
    (11, 6, "2025-04-02", "30", 4, "Watched a tutorial", "2025-04-02"),
    (12, 7, "2025-03-30", "Yes", 3, "Quick clean-up", "2025-03-30"),
    (13, 8, "2025-04-01", "30", 5, "Feeling stronger", "2025-04-01"),
    (14, 8, "2025-04-02", "25", 4, "Almost there", "2025-04-02"),
    (15, 9, "2025-04-01", "Yes", 5, "Emotional writing", "2025-04-01"),
    (16, 9, "2025-04-02", "Yes", 4, "Short reflections", "2025-04-02"),
    (17, 10, "2025-04-01", "20", 5, "Great session", "2025-04-01"),
    (18, 10, "2025-04-02", "20", 4, "Little tired", "2025-04-02"),
    (19, 2, "2025-04-03", "30", 5, "New chapter", "2025-04-03"),
    (20, 4, "2025-04-03", "10", 2, "Too noisy", "2025-04-03"),
    (21, 5, "2025-04-03", "Yes", 4, "Weekly budget done", "2025-04-03"),
    (22, 1, "2025-04-03", "Yes", 4, "Normal pace", "2025-04-03"),
    (23, 6, "2025-04-03", "45", 5, "Solved a problem", "2025-04-03"),
    (24, 8, "2025-04-03", "30", 5, "No sweat", "2025-04-03"),
    (25, 3, "2025-04-03", "6", 3, "Low today", "2025-04-03"),
    (26, 7, "2025-04-07", "Yes", 5, "Spring cleaned", "2025-04-07"),
    (27, 10, "2025-04-03", "20", 4, "Kept up streak", "2025-04-03"),
    (28, 9, "2025-04-03", "Yes", 4, "Short but honest", "2025-04-03"),
    (29, 1, "2025-04-04", "No", 1, "Felt lazy", "2025-04-04"),
    (30, 2, "2025-04-04", "20", 3, "Skimmed pages", "2025-04-04"),
]

activity_df = pd.DataFrame(activity_logs_data, columns=headers)

habits_headers = ['habit_id', 'name', 'start_date', 'frequency', 'category', 'tracking_type', 'goal', 'goal_units', 'notes', 'end_date', 'created_at']
habits_data = [
    (1, "Morning Jog", "2024-12-01", "Daily", "Health", "Yes/No", None, None, "Jog around the block", "2025-06-01", "2024-12-01"),
    (2, "Read Book", "2025-01-10", "Daily", "Personal Development", "Duration", 30, "Minutes", "Read non-fiction", "2025-07-10", "2025-01-10"),
    (3, "Drink Water", "2025-02-01", "Daily", "Health", "Count", 8, "Glasses", "Hydration target", None, "2025-02-01"),
    (4, "Meditate", "2025-01-05", "Daily", "Mental Health", "Duration", 15, "Minutes", "Morning meditation", None, "2025-01-05"),
    (5, "Budget Tracking", "2025-01-15", "Weekly", "Finance", "Yes/No", None, None, "Track weekly spending", None, "2025-01-15"),
    (6, "Study Python", "2025-02-20", "Daily", "Learning", "Duration", 60, "Minutes", "Improve coding", None, "2025-02-20"),
    (7, "Clean Room", "2025-03-01", "Weekly", "Chores", "Yes/No", None, None, "Declutter space", None, "2025-03-01"),
    (8, "Push Ups", "2025-01-20", "Daily", "Fitness", "Count", 30, "Reps", "Stay strong", None, "2025-01-20"),
    (9, "Journal", "2025-03-01", "Daily", "Mental Health", "Yes/No", None, None, "Reflect on day", None, "2025-03-01"),
    (10, "Duolingo Practice", "2025-01-01", "Daily", "Learning", "Duration", 20, "Minutes", "French lessons", None, "2025-01-01"),
]

habit_df = pd.DataFrame(habits_data, columns=habits_headers)
# habit_df['start_date'] == pd.to_datetime(habit_df['start_date'])

# sidebar for filters
with st.sidebar: 
    st.header("Accountability Partner")

    # date filters
    start_date = st.date_input("Start date", activity_df['log_date'].min())
    end_date = st.date_input("End date", activity_df['log_date'].max())

    # category filters
    categories = habit_df['category'].unique()
    categories_with_all = ['All categories'] + sorted(categories)
    selected_category = st.selectbox("Select category",options=categories_with_all)
    if selected_category == 'All categories':
        filtered_df = activity_df.copy()
        filtered_habits = habit_df.copy()
    else:
        filtered_habits = habit_df[habit_df["category"] == selected_category]
        filtered_df = activity_df[activity_df['habit_id'].isin(filtered_habits['habit_id'])]

    # if selected_category:
    #     filtered_habits = habit_df[habit_df["category"] == selected_category]
    #     filtered_df = activity_df[activity_df['habit_id'].isin(filtered_habits['habit_id'])]
    #     habits = st.multiselect("Select Habits",
    #                             options=filtered_habits['name'])

# convert column to date
filtered_df['log_date'] = pd.to_datetime(filtered_df['log_date'])

tab1, tab2 = st.tabs(['📈 Charts',  "🗃️ Data" ])        
with tab1:
    st.header("📈 Visualize your progress")

    # create 2 columns for charts
    col1, col2 = st.columns(2)

    with col1:
        # average rating per habit visual
        habit_averages = filtered_df.groupby('habit_id')['rating'].mean().reset_index().sort_values(by='rating',ascending=False)
        st.subheader("Average rating by activity")
        fig,ax = plt.subplots(figsize=(6,4))
        sns.barplot(y='habit_id',
                     x='rating', 
                     data=habit_averages,
                       orient='h',
                         ax=ax)
        ax.invert_yaxis()
        ax.set_ylabel('Habit', fontsize=12)
        ax.set_xlabel('Average Rating', fontsize=12)
        plt.tight_layout()
        st.pyplot(fig)
        # st.checkbox("Show values on chart", value=True)


        st.subheader("Highlights from your activity logs")
        notes = filtered_df['log_notes'].dropna().to_list()
        text = " ".join(notes)
        if text.strip() == "":
            st.info("Wordcloud not available because there are not enough notes from your logs to build the visual")
        else:
            wordcloud = WordCloud(width=800, height=400, background_color='white',colormap='viridis').generate(text)
            fig,ax = plt.subplots(figsize=(6,4))
            ax.imshow(wordcloud,interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)

    with col2:
        st.subheader("Consistency report")
        today = pd.to_datetime(datetime.now().date())
        consistency_list = []
        for index,row in filtered_habits.iterrows():
            habit_id = row['habit_id']
            name = row['name']
            frequency = row['frequency']
            start_date = pd.to_datetime(row['start_date'])

            # actual logs
            actual_logs = filtered_df[filtered_df['habit_id'] == habit_id].shape[0]

            # expected logs
            if frequency == "Daily":
                expected_logs = max((today-start_date).days + 1, 1)
            elif frequency == "Weekly":
                expected_logs = max(((today - start_date).days // 7)+1, 1)
            elif frequency == "Monthly":
                expected_logs = max(((today.year - start_date.year) * 12 + (today.month - start_date.month)) + 1, 1)

            consistency_rate = round((actual_logs/expected_logs) * 100,2)
            consistency_list.append({
                "habit_id": habit_id,
                "name": name,
                "consistency rate": consistency_rate,
                "actual_logs":actual_logs,
                "expected_logs": expected_logs
            })

        consistency_df = pd.DataFrame(consistency_list)

        st.dataframe(consistency_df)


    # log calendar visual
    st.subheader("Log Calendar")
    cal_data = (filtered_df.groupby('log_date').size())
    cal_data.index = pd.to_datetime(cal_data.index)
    fig, ax = calplot.calplot(cal_data, cmap="YlGn", figsize=(8,3))
    st.pyplot(fig, use_container_width=True)


with tab2:
    st.header("Your activity logs data")
    st.write(f"Showing {len(filtered_df)} records based on your filter selections.")
    st.dataframe(filtered_df)
    st.dataframe(activity_df)