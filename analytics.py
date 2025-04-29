import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import calplot
from db import db_operations as db
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
st.title("Accountability Partner")
st.subheader("Your Habit Dashboard")

# load and cache data
@st.cache_data
def load_data():
    """Load habits and activity logs dataframe"""
    habit_df = db.get_all_habits_to_df()
    activity_df = db.get_all_activity_logs()
    merged_df = pd.merge(activity_df, habit_df, on='habit_id', how='left')
    merged_df.drop(columns='name_y', inplace=True)
    merged_df.rename(columns={'name_x':'name'}, inplace=True)
    return habit_df, activity_df,merged_df

habit_df,activity_df, merged_df = load_data()
merged_df['log_date'] = pd.to_datetime(merged_df['log_date'])

def update_active_view():
    st.session_state.active_view = st.session_state.view_radio

# initialize session state
if 'active_view' not in st.session_state:
    st.session_state.active_view = "📊 Overview"
if 'view_radio' not in st.session_state:
    st.session_state.view_radio = "📊 Overview"

# container for the main view selector
view_container = st.container()


# sidebar for filters
with st.sidebar:
    st.header("Filters")

    if st.session_state.active_view == "📊 Overview":
        # date filters for overview page
        start_date = st.date_input("Start date", merged_df['log_date'].min().date())
        end_date = st.date_input("End date", merged_df['log_date'].max().date())
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        overview_df01 = merged_df[(merged_df['log_date'] >= start_date) & (merged_df['log_date'] <= end_date)]

        # category filters
        categories = overview_df01['category'].unique()
        categories_with_all = ['All categories'] + sorted(categories)
        selected_category = st.selectbox("Select category", options=categories_with_all)

        if selected_category == 'All categories':
            overview_df = overview_df01.copy()
        else:
            overview_df = merged_df[merged_df['category'] == selected_category]

    elif st.session_state.active_view == '📈 Activity Analytics':
        # category filters
        analytics_categories = merged_df['category'].unique()
        analytics_selected_category = st.selectbox('Select category', options=analytics_categories)

        analytics_df01 = merged_df[merged_df['category'] == analytics_selected_category]

        # habit filters
        analytics_habits = analytics_df01['name'].unique()
        analytics_selected_habit = st.selectbox("Select habit", options=analytics_habits)
        analytics_df = analytics_df01[analytics_df01['name'] == analytics_selected_habit]
    elif st.session_state.active_view == '🗃️ Data':
        st.write("testing")

# create radio in container
with view_container:
    selected_view = st.radio(
        "Select View",
        ["📊 Overview", "📈 Activity Analytics", "🗃️ Data"],
        horizontal=True,
        key="view_radio",
        on_change=update_active_view
    )

    # update session state based on selection
    if selected_view == "📊 Overview":
        st.session_state.active_view = "📊 Overview"
    elif selected_view == "📈 Activity Analytics":
        st.session_state.active_view = "📈 Activity Analytics"
    elif selected_view == "🗃️ Data":
        st.session_state.active_view = "🗃️ Data"


# display selected view content
if st.session_state.active_view == "📊 Overview":
    st.header("📈 Visualize your progress")

    # create 2 columns for charts
    col1, col2 = st.columns(2)

    with col1:
        # average rating per habit visual
        habit_averages = overview_df.groupby('name')['rating'].mean().reset_index().sort_values(by='rating',ascending=True)
        st.subheader("Average rating by activity")
        fig,ax = plt.subplots(figsize=(6,4))
        sns.barplot(y='name',
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

        # wordcloud visual
        st.subheader("Highlights from your activity logs")
        notes = overview_df['log_notes'].dropna().to_list()
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
        # completion rate visual
        st.subheader("Completion Rate")
        today = pd.to_datetime(datetime.now().date())
        consistency_list = []
        unique_habits = overview_df[['habit_id', 'name', 'frequency', 'start_date']].drop_duplicates()
        for index,row in unique_habits.iterrows():
            habit_id = row['habit_id']
            name = row['name']
            frequency = row['frequency']
            start_date = pd.to_datetime(row['start_date'])
            # actual logs
            actual_logs = overview_df[overview_df['habit_id'] == habit_id].shape[0]
            # calculate expected logs based on habit frequency
            if frequency == "Daily":
                # if frequency is daily, expected logs is days between start date and today
                expected_logs = max((today-start_date).days + 1, 1)
            elif frequency == "Weekly":
                # if frequency is weekly, expected logs is weeks between start date and today
                expected_logs = max(((today - start_date).days // 7)+1, 1)
            elif frequency == "Monthly":
                # if frequency is monthly, expected logs is months between start date and today
                expected_logs = max(((today.year - start_date.year) * 12 + (today.month - start_date.month)) + 1, 1)
            # calculate completion rate
            consistency_rate = "%.2f" % ((actual_logs/expected_logs) * 100)
            consistency_list.append({
                "Habit": name,
                "Expected Logs": expected_logs,
                "Actual Logs":actual_logs,
                "Completion Rate(%)": float(consistency_rate)
            })
        # convert completion rate list to dataframe
        consistency_df = pd.DataFrame(consistency_list)
        # dispay dataframe as table
        st.dataframe(consistency_df)

        # goal achievement visual
        st.subheader("Goal Achievement")
        # filter for only tracking types that allow for goal tracking
        goal_df = overview_df[overview_df['tracking_type'].isin(['Duration (Minutes/hours)', 'Count (Number-based)'])]
        if goal_df.shape[0] == 0:
            st.write("This category does not have habits to be displayed for this visual")
        else:
            # calculate achievement per activity log
            goal_df['goal_achievement'] = ((goal_df['activity'].astype(float) / goal_df['goal'].astype('float')) * 100).clip(upper=100)
            # group by habit
            habit_achievement = (goal_df.groupby('habit_id').agg(
                average_goal_achievement = ("goal_achievement", "mean"),
                total_logs = ("log_id", 'count'),
                habit_name = ("name", 'first')
            ).reset_index().sort_values(by='average_goal_achievement', ascending=True))
            # plot visual
            fig,ax = plt.subplots(figsize=(6,4))
            sns.barplot(y='habit_name',
                        x='average_goal_achievement',
                        data = habit_achievement,
                        orient='h',
                        ax=ax)
            ax.set_xlabel('Average Goal Achievement (%)')
            ax.set_ylabel("Habit")
            ax.invert_yaxis()
            plt.tight_layout()
            st.pyplot(fig)



    # log calendar visual
    st.subheader("Log Calendar")
    cal_data = (overview_df.groupby('log_date').size())
    cal_data.index = pd.to_datetime(cal_data.index)
    fig, ax = calplot.calplot(cal_data, cmap="YlGn", figsize=(8,3))
    st.pyplot(fig, use_container_width=True)
elif st.session_state.active_view == "🗃️ Data":
    df = merged_df.copy()
    st.header("Your activity logs data")
    # tab1, tab2, tab3 = st.tabs(['📊 Overview', '📈 Activity Analytics',  "🗃️ Data" ])
    st.write(f"Showing {len(df)} records based on your filter selections.")
    st.dataframe(df)
    # st.dataframe(habit_df)
