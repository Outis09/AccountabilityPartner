"""
Demo application for the Streamlit app.
This module serves as a demonstration of the Streamlit app's functionality, showcasing various features and components.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta

import analytics as hp

if "demo_analytics_view" not in st.session_state:
    st.session_state.analytics_view = "📊 Overview"


# get longest streak for a group of habits
def calc_streaks_grouped(df):
    overall_longest_streak = 0
    overall_current_streak = 0

    # group by habit

# habit categories and metadata
habit_categories = {
    "Productivity": [
        {"habit_id": 1, "name": "Plan the day", "frequency": "Daily", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 2, "name": "Clear email inbox", "frequency": "Daily", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 3, "name": "Deep work session", "frequency": "Daily", "tracking_type": "Duration (Minutes/hours)", "goal": 90, "goal_units": "minutes"},
        {"habit_id": 4, "name": "Complete top 3 tasks", "frequency": "Daily", "tracking_type": "Count (Number-based)", "goal": 3, "goal_units": "tasks"},
        {"habit_id": 5, "name": "Avoid multitasking", "frequency": "Daily", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 6, "name": "Review goals", "frequency": "Weekly", "tracking_type": "Yes/No (Completed or not)"},
    ],
    "Learning": [
        {"habit_id": 7, "name": "Learn Python", "frequency": "Daily", "tracking_type": "Duration (Minutes/hours)", "goal": 60, "goal_units": "minutes"},
        {"habit_id": 8, "name": "Learn Apache Airflow", "frequency": "Weekly", "tracking_type": "Duration (Minutes/hours)", "goal": 90, "goal_units": "minutes"},
        {"habit_id": 9, "name": "Take online course", "frequency": "Weekly", "tracking_type": "Count (Number-based)", "goal": 2, "goal_units": "modules"},
        {"habit_id": 10, "name": "Practice coding", "frequency": "Daily", "tracking_type": "Duration (Minutes/hours)", "goal": 45, "goal_units": "minutes"},
        {"habit_id": 11, "name": "Write technical blog", "frequency": "Weekly", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 12, "name": "Watch educational videos", "frequency": "Daily", "tracking_type": "Duration (Minutes/hours)", "goal": 30, "goal_units": "minutes"},
    ],
    "Health": [
        {"habit_id": 13, "name": "Workout", "frequency": "Weekly", "tracking_type": "Count (Number-based)", "goal": 5, "goal_units": "sessions"},
        {"habit_id": 14, "name": "Drink Water", "frequency": "Daily", "tracking_type": "Count (Number-based)", "goal": 8, "goal_units": "glasses"},
        {"habit_id": 15, "name": "Eat vegetables", "frequency": "Daily", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 16, "name": "Sleep 8 hours", "frequency": "Daily", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 17, "name": "Go for a walk", "frequency": "Daily", "tracking_type": "Duration (Minutes/hours)", "goal": 30, "goal_units": "minutes"},
    ],
    "Finance": [
        {"habit_id": 18, "name": "Track expenses", "frequency": "Daily", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 19, "name": "Update budget", "frequency": "Weekly", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 20, "name": "Save money", "frequency": "Weekly", "tracking_type": "Count (Number-based)", "goal": 3, "goal_units": "transactions"},
        {"habit_id": 21, "name": "Review bank account", "frequency": "Weekly", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 22, "name": "Pay bills", "frequency": "Monthly", "tracking_type": "Yes/No (Completed or not)"},
    ],
    "Chores": [
        {"habit_id": 23, "name": "Clean kitchen", "frequency": "Weekly", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 24, "name": "Do laundry", "frequency": "Weekly", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 25, "name": "Take out trash", "frequency": "Daily", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 26, "name": "Tidy bedroom", "frequency": "Daily", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 27, "name": "Water plants", "frequency": "Weekly", "tracking_type": "Yes/No (Completed or not)"},
    ],
    "Mental Health": [
        {"habit_id": 28, "name": "Meditate", "frequency": "Daily", "tracking_type": "Duration (Minutes/hours)", "goal": 10, "goal_units": "minutes"},
        {"habit_id": 29, "name": "Journal", "frequency": "Daily", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 30, "name": "Unplug from devices", "frequency": "Daily", "tracking_type": "Duration (Minutes/hours)", "goal": 60, "goal_units": "minutes"},
        {"habit_id": 31, "name": "Practice gratitude", "frequency": "Daily", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 32, "name": "Breathing exercise", "frequency": "Daily", "tracking_type": "Duration (Minutes/hours)", "goal": 5, "goal_units": "minutes"},
    ],
    "Personal Development": [
        {"habit_id": 33, "name": "Read a book", "frequency": "Daily", "tracking_type": "Duration (Minutes/hours)", "goal": 30, "goal_units": "minutes"},
        {"habit_id": 34, "name": "Review goals", "frequency": "Weekly", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 35, "name": "Listen to podcast", "frequency": "Daily", "tracking_type": "Duration (Minutes/hours)", "goal": 20, "goal_units": "minutes"},
        {"habit_id": 36, "name": "Self-reflection", "frequency": "Daily", "tracking_type": "Yes/No (Completed or not)"},
        {"habit_id": 37, "name": "Plan personal growth", "frequency": "Weekly", "tracking_type": "Yes/No (Completed or not)"},
    ]
}

log_notes_options = [
    "Felt incredibly focused and productive today.",
    "Struggled to concentrate but pushed through.",
    "Quick session, but got the essentials done.",
    "Didn't feel like doing it, but glad I did.",
    "Really enjoyed the process — very fulfilling.",
    "It was okay, nothing special.",
    "Kept getting distracted, had to restart a few times.",
    "Felt drained and unmotivated.",
    "Hit a flow state — lost track of time!",
    "Hard to get started but once I began, it flowed.",
    "Not my best, but better than nothing.",
    "Totally forgot I had to do this until the last minute.",
    "Everything clicked — smooth and easy.",
    "Did it out of habit, didn’t feel very engaged.",
    "Rushed through it just to check it off the list.",
    "It felt repetitive and a bit boring today.",
    "Took longer than usual but stayed consistent.",
    "Loved every moment of it, very rewarding.",
    "Feeling proud of the effort I put in today.",
    "I skipped yesterday, so I made sure to show up strong today.",
    "Had to push myself, but it was worth it in the end.",
    "Felt like I was on autopilot, but still got it done.",
    "Had a breakthrough moment during this activity.",
    "It was a struggle, but I learned something new.",
    "Felt like I was in a rut, but I pushed through.",
    "Today was a breeze, everything went smoothly.",
    "Felt a bit off, but managed to complete it.",
    "Had to adjust my approach, but it worked out.",
    "Felt like I was in a groove, very productive.",
    "It was a bit challenging, but I overcame it.",
    "Felt like I was in a creative flow, very inspiring.",
    "Had to adapt to some unexpected challenges, but I managed.",
    "Felt like I was in a zone, very focused.",
    "It was a bit frustrating, but I learned a lot.",
    "Felt like I was in a good rhythm, very productive.",
    "Had to push through some distractions, but I stayed focused.",
    "","",""
]

# flatten habit list 
habits = []
for category, items in habit_categories.items():
    for habit in items:
        habit["habit_category"] = category
        if "goal" not in habit:
            habit["goal"] = None
        if "goal_units" not in habit:
            habit["goal_units"] = None
        habits.append(habit)

# generate habit start dates
habit_start_dates = {
    habit['habit_id']: datetime.today() - timedelta(days=random.randint(0,90)) for habit in habits
}

# generate one log 
def generate_log(habit):
    start_date = habit_start_dates[habit['habit_id']]
    today = datetime.today()
    # generate log date between start date and today
    delta_days = (today - start_date).days
    log_date = start_date + timedelta(days=random.randint(0, delta_days))

    if habit["tracking_type"] == "Yes/No (Completed or not)":
        activity = random.choice(["Yes", "No"])
    elif habit["tracking_type"] == "Count (Number-based)":
        activity = random.randint(int(habit["goal"] * 0.5), habit["goal"] + 2)
    elif habit["tracking_type"] == "Duration (Minutes/hours)":
        activity = random.randint(int(habit["goal"] * 0.5), habit["goal"] + 10)

    return {
        "habit_id": habit['habit_id'],
        "log_date": log_date.isoformat(),
        "name": habit["name"],
        "habit_category": habit["habit_category"],
        "start_date": start_date.isoformat(),
        "frequency": habit["frequency"],
        "tracking_type": habit["tracking_type"],
        "goal": habit["goal"],
        "goal_units": habit["goal_units"],
        "activity": activity,
        "rating": random.randint(1, 5),
        "log_notes": random.choice(log_notes_options) or None
    }

# generate 1000 logs
demo_logs = [generate_log(random.choice(habits)) for _ in range(1000)]
demo_data = pd.DataFrame(demo_logs)
demo_data["log_date"] = pd.to_datetime(demo_data["log_date"])




def demo_sidebar(data):
    with st.sidebar:
        st.logo("images/AppLogo.png", size="large")
        if st.button("Home"):
            st.session_state.current_page = "home"
            st.session_state.show_login = False
            st.session_state.show_signup = False
            st.session_state.forgot_password = False
            st.session_state.username=None
            st.rerun()

        st.title("Filters")

        if st.session_state.demo_analytics_view == "📊 Overview":
            # date filters
            start_date = st.date_input("Start Date", value=data["log_date"].min().date())
            end_date = st.date_input("End Date", value=data["log_date"].max().date())
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            # filter data based on date range
            date_filtered_data = data[(data["log_date"] >= start_date) & (data["log_date"] <= end_date)]

            # category filters
            categories = date_filtered_data["habit_category"].unique().tolist()
            categories.insert(0, "All Categories")
            selected_category = st.selectbox("Select Category", categories)
            if selected_category != "All Categories":
                category_filtered_data = date_filtered_data[date_filtered_data["habit_category"] == selected_category]
            else:
                category_filtered_data = date_filtered_data.copy()
            return category_filtered_data
            
        elif st.session_state.demo_analytics_view == "📈 Activity Analytics":
            # category filters
            categories = data["habit_category"].unique().tolist()
            analytics_categories = st.selectbox("Select Category", categories)
            # filter data based on selected category
            category_filtered_data = data[data["habit_category"] == analytics_categories]
            # activity filters
            activities = category_filtered_data["name"].unique().tolist()
            selected_activity = st.selectbox("Select Activity", activities)
            # filter data based on selected activity
            activity_filtered_data = category_filtered_data[category_filtered_data["name"] == selected_activity]
            return activity_filtered_data
        elif st.session_state.demo_analytics_view == "🗃️ Data":
            # category filters
            categories = data["habit_category"].unique().tolist()
            categories.insert(0, "All Categories")
            selected_category = st.selectbox("Select Category", categories)
            if selected_category != "All Categories":
                category_filtered_data = data[data["habit_category"] == selected_category]
            else:
                category_filtered_data = data.copy()
            # activity filters
            activities = category_filtered_data["name"].unique().tolist()
            activities.insert(0, "All Activities")
            selected_activity = st.selectbox("Select Activity", activities)
            if selected_activity != "All Activities":
                activity_filtered_data = category_filtered_data[category_filtered_data["name"] == selected_activity]
            else:
                activity_filtered_data = category_filtered_data.copy()
            # date filters
            start_date = st.date_input("Start Date", value=activity_filtered_data["log_date"].min().date())
            end_date = st.date_input("End Date", value=activity_filtered_data["log_date"].max().date())
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            # filter data based on date range
            date_filtered_data = activity_filtered_data[(activity_filtered_data["log_date"] >= start_date) & (activity_filtered_data["log_date"] <= end_date)]
            return date_filtered_data



def demo_main(dataframe):
    st.title("Accountability Partner Demo")
    st.write("Track your habits and activities with ease!")
    st.info("Please note that the demo only shows the analytics features and does not allow users to create or track habits.")
    st.warning("The data for this demo is automatically generated and does not reflect real user data. It changes upon refresh therefore results may vary.")

    # radio for analytics view
    analytics_view = st.radio("Select Analytics View", 
                              ["📊 Overview", "📈 Activity Analytics", "🗃️ Data"], 
                              horizontal=True,
                              key="demo_analytics_view",
                              label_visibility="collapsed")
    
    # visuals for overview page
    if st.session_state.demo_analytics_view == "📊 Overview":
        # st.dataframe(dataframe)
        # kpi columns
        overview_kpi1, overview_kp2 = st.columns(2)
        with overview_kpi1:
            # first set of kpis
            kpi1, kpi2, kpi3 = st.columns(3)
            with kpi1:
                # total habits
                st.metric(label="Total Habits", value=dataframe['name'].nunique(), border=True)
            with kpi2:
                # total logs
                st.metric(label="Total Logs", value=dataframe['log_date'].count(), border=True)
            with kpi3:
                # average rating
                st.metric(label="Average Rating", value=round(dataframe['rating'].mean(),2), border=True)
        with overview_kp2:
            # second set of kpis
            kpi4, kpi5, kpi6 = st.columns(3)
            with kpi4:
                # best habit
                best_habit = dataframe.groupby('name')['rating'].mean().idxmax()
                st.metric(label="Best Habit (By rating)", value=best_habit, border=True)
            with kpi5:
                # longest streak
                longest_streak, _ = hp.calculate_streaks_grouped(dataframe)
                st.metric(label="Longest Streak", value=longest_streak, border=True)
            with kpi6:
                # average completion rate
                average_completion_rate = hp.calculate_average_completion(dataframe) 
                st.metric(label="Average Completion Rate", value=average_completion_rate, border=True)

        # columns for main charts
        charts1, charts2 = st.columns(2)
        with charts1:
            # completion rate chart
            with st.container(height=500):
                st.subheader("✅ Completion Rate")
                complt_rate_df = hp.completion_rate(dataframe)
                st.dataframe(complt_rate_df, hide_index=True)
            # average rating chart
            with st.container(height=500):
                st.subheader("⭐ Average Rating by Activity")
                habit_averages = dataframe.groupby('name')['rating'].mean().round(2).reset_index().sort_values(by='rating', ascending=True)
                if len(habit_averages) <= 10:
                    chart = hp.plot_bar_chart(habit_averages, 'name', 'rating', 'Activity', 'Average Rating')
                    
                    st.altair_chart(chart, use_container_width=True)
                else:
                    df_len = round(len(habit_averages)/2)
                    top, bottom = st.tabs([f'Top {df_len}', f'Bottom {df_len}'])
                    with top:
                        highest = habit_averages.iloc[df_len+1:]
                        chart = hp.plot_bar_chart(highest,'name', 'rating', 'Activity', 'Average Rating')
                        st.altair_chart(chart, use_container_width=True)
                    with bottom:
                        lowest = habit_averages.iloc[:df_len+1]
                        chart = hp.plot_bar_chart(lowest, 'name', 'rating', 'Activity', 'Average Rating')
                        st.altair_chart(chart,use_container_width=True)

        
        with charts2:
            # goal achievement visual
            with st.container(height=500):
                st.subheader("🎯 Goal Achievement")
                chart, message = hp.calc_goal_achievement(dataframe)
                if chart and not message:
                    st.altair_chart(chart,use_container_width=True)
                elif message:
                    st.info(message)

            # insights from activity logs
            with st.container(height=500):
                st.subheader("💡 Insights from Activity Logs")
                texts_df = dataframe[dataframe['log_notes'].str.strip().astype(bool)]
                if len(texts_df) == 0:
                    st.info("You do not have enough log notes for this visual. Please add notes to your next logs")
                else:
                    # tabs for highlights wordcloud and sentiment analysis
                    tab1, tab2 = st.tabs(["Highlights", "Sentiment Analysis"])
                    with tab1:
                        # st.write("Wordcloud of highlights from activity logs")
                        hp.create_wordcloud(texts_df, 'log_notes')
                    with tab2:
                        texts_df['processed_text'] = texts_df['log_notes'].apply(hp.text_preprocessor)
                        texts_df['sentiment'] = texts_df['processed_text'].apply(hp.sentiment_analyzer)
                        overview_sentiments = hp.get_sentiment_results(texts_df, 'sentiment')
                        fig, ax = plt.subplots(figsize=(4,3))
                        ax.pie(overview_sentiments['Percentage'], labels=overview_sentiments['Sentiment'], autopct='%1.1f%%', startangle=90)
                        ax.axis('equal')
                        st.pyplot(fig)
                        # st.write("Sentiment analysis of activity logs")
        
        # log calendar chart
        st.subheader("📅 Log Calendar")
        fig,ax = hp.plot_calplot(dataframe, 'log_date')
        st.pyplot(fig, use_container_width=True)

    # visuals for activity analytics page
    elif st.session_state.demo_analytics_view == "📈 Activity Analytics":
        # activity name
        habit = dataframe['name'].unique()[0]
        st.metric(label="Activity", value=habit)
        # kpi columns
        activity_kpi1, activity_kp2 = st.columns(2)
        with activity_kpi1:
            # first set of kpis
            kpi1, kpi2, kpi3 = st.columns(3)
            
            with kpi1:
                # total logs
                st.metric(label="Total Logs", value=dataframe.shape[0], border=True)
            with kpi2:
                # completion rate
                freq = dataframe['frequency'].unique()[0]
                start_date = pd.to_datetime(dataframe['start_date'].unique()[0])
                tracking = dataframe['tracking_type'].unique()[0]
                if tracking == "Yes/No (Completed or not)":
                    actual_logs = dataframe[dataframe['activity'] == "Yes"].shape[0]
                else:
                    actual_logs = dataframe.shape[0]
                expected_logs = hp.calculate_expected_logs(start_date, freq)
                completion_rate = round((actual_logs/expected_logs) * 100, 2)
                st.metric(label="Completion Rate", value=f"{completion_rate}%", border=True)
            with kpi3:
                # average rating
                avg_rating = dataframe['rating'].mean()
                st.metric(label="Average Rating", value=round(avg_rating,2), border=True)
        with activity_kp2:
            # second set of kpis
            kpi4, kpi5, kpi6 = st.columns(3)
            
            with kpi4:
                # current streak
                _, current_streak = hp.calculate_streaks_grouped(dataframe)
                st.metric(label="Current Streak", value=current_streak, border=True)
            with kpi5:
                # completed logs
                tracking = dataframe['tracking_type'].unique()[0]
                if tracking == "Yes/No (Completed or not)":
                    # Yes/No (Completed or not) tracking
                    completed = dataframe[dataframe['activity'] == "Yes"].shape[0]
                    # st.write(completed)
                    # not_completed = df.shape[0] - completed
                    st.metric(label="Completed", value=completed, delta_color="normal", border=True)
                    # st.write(dataframe[dataframe['activity'] == "Yes"])
                elif tracking == "Duration (Minutes/hours)":
                    # duration tracking
                    total_duration = dataframe['activity'].sum()
                    if total_duration > 60:
                        hours = round(total_duration / 60,2)
                        st.metric(label="Total Duration (hrs)", value=hours, delta_color="normal", border=True)
                    else:
                        st.metric(label="Total Duration (mins)", value=total_duration, delta_color="normal", border=True)
                elif tracking == "Count (Number-based)":
                    # count tracking
                    total_count = dataframe['activity'].sum()
                    goal_units = dataframe['goal_units'].unique()[0]
                    st.metric(label=goal_units.capitalize(), value=total_count, delta_color="normal", border=True)
            with kpi6:
                # goal achievement rate
                goal = dataframe['goal'].unique()[0]
                if tracking != "Yes/No (Completed or not)":
                    dataframe['goal_achievement'] = ((dataframe['activity'].astype(float) / float(goal)) * 100).clip(upper=100)
                    goal_achievement = f"{round(dataframe['goal_achievement'].mean(),2)}%"
                else:
                    goal_achievement = 'N/A'
                st.metric(label="Goal Achievement Rate", value=goal_achievement, border=True)

        # columns for main charts
        charts1, charts2 = st.columns(2)
        with charts1:
            # summary table
            with st.container(height=500):
                st.subheader("📋 Summary")
                summary_table = hp.create_summary_table(dataframe)
                st.dataframe(summary_table, hide_index=True)
            # activity logs against target
            with st.container(height=500):
                st.subheader("🎯 Log vs Target")
                if tracking != "Yes/No (Completed or not)":
                    goal = int(goal)
                    chart = hp.plot_line_chart(dataframe, 'log_date', 'activity', 'Log Date', goal_units,'goal', y_min=0, y_max=goal+10, y_tick_count=5)
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("This visual is not available for this activity")

            # day of week visual
            with st.container(height=500):
                st.subheader("🗓️ Activity Logs by Day of Week")
                dataframe['day_of_week'] = dataframe['log_date'].dt.day_name()
                order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                dataframe['day_of_week'] = pd.Categorical(dataframe['day_of_week'], categories=order, ordered=True)
                day_counts = dataframe['day_of_week'].value_counts().sort_index().reset_index()
                chart = hp.plot_bar_chart(day_counts, 'day_of_week', 'count', '', 'Number of Logs', orientation='vertical')
                st.altair_chart(chart, use_container_width=True)
        
        with charts2:
            # rating trend chart
            with st.container(height=500):
                st.subheader("📈 Rating Trends")
                chart = hp.plot_line_chart(dataframe, 'log_date', 'rating', 'Log Date', 'Rating', y_tick_count=5)
                st.altair_chart(chart, use_container_width=True)
            # insights from activity logs
            with st.container(height=500):
                st.subheader("💡 Insights from Activity Logs")
                texts_df = dataframe[dataframe['log_notes'].str.strip().astype(bool)]
                if len(texts_df) == 0:
                    st.info("You do not have enough log notes for this visual. Please add notes to your next logs")
                else:
                    # tabs for highlights wordcloud and sentiment analysis
                    tab1, tab2 = st.tabs(["Highlights", "Sentiment Analysis"])
                    with tab1:
                        hp.create_wordcloud(dataframe, 'log_notes')
                    with tab2:
                        texts_df['processed_text'] = texts_df['log_notes'].apply(hp.text_preprocessor)
                        texts_df['sentiment'] = texts_df['processed_text'].apply(hp.sentiment_analyzer)
                        # st.subheader('Sentiment Analysis')
                        overview_sentiments = hp.get_sentiment_results(texts_df, 'sentiment')
                        fig,ax = plt.subplots(figsize=(4,3))
                        ax.pie(overview_sentiments['Percentage'], labels=overview_sentiments['Sentiment'], autopct='%1.1f%%', startangle=90)
                        ax.axis('equal')
                        st.pyplot(fig)
                        st.write("Sentiment analysis of activity logs")
            # log intervals over time
            with st.container(height=500):
                st.subheader("⏱️ Log Intervals Over Time")
                log_intervals = hp.calculate_log_intervals_overtime(dataframe['log_date'])
                if log_intervals.shape[0] == 0:
                    st.info("This activity does not have enough logs to display this visual")
                else:
                    chart = hp.plot_line_chart(log_intervals, 'log_date', 'interval', 'Log Date', 'Interval (Days)', y_tick_count=5)
                    st.altair_chart(chart, use_container_width=True)
        
        # log calendar chart
        st.subheader("📅 Log Calendar")
        fig,ax = hp.plot_calplot(dataframe, 'log_date', cmap='YlGn_r')
        st.pyplot(fig, use_container_width=True)

    elif st.session_state.demo_analytics_view == "🗃️ Data":
        # data table for habits and activities
        df = dataframe[["log_date", "name", "habit_category", "frequency", "tracking_type", "goal", "goal_units", "activity","rating", "log_notes"]]
        df.rename(columns={
            "log_date": "Log Date",
            "name": "Habit Name",
            "habit_category": "Category",
            "frequency": "Frequency",
            "tracking_type": "Tracking Type",
            "goal": "Goal",
            "goal_units": "Goal Units",
            "activity": "Activity",
            "rating": "Rating",
            "log_notes": "Log Notes"
        }, inplace=True)
        st.subheader("📊 Habits and Activities Data")
        st.write(f"Showing {len(df)} records")
        st.dataframe(df, hide_index=True)


def demo_app():
    demo_df = demo_sidebar(demo_data)
    demo_main(demo_df)