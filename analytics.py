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
st.title("📊Activity Logs Visualization")

# extract habit data into df
habit_df = db.get_all_habits_to_df()
# extract activity logs into df
activity_df = db.get_all_activity_logs()
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
        habit_averages = filtered_df.groupby('name')['rating'].mean().reset_index().sort_values(by='rating',ascending=True)
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
        st.subheader("Completion Rate")
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

            consistency_rate = "%.2f" % ((actual_logs/expected_logs) * 100)
            consistency_list.append({
                "Habit": name,
                "Expected Logs": expected_logs,
                "Actual Logs":actual_logs,
                "Completion Rate(%)": consistency_rate
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
    st.dataframe(habit_df)