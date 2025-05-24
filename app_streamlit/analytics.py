import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import calplot
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import altair as alt
# wordcloud
from wordcloud import WordCloud
from datetime import datetime
# sentiment analysis
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
# nltk.download(['vader_lexicon', 'punkt_tab', 'stopwords', 'wordnet'])

# initialize session states
if 'active_view' not in st.session_state:
    st.session_state.active_view = "📊 Overview"
if 'view_radio' not in st.session_state:
    st.session_state.view_radio = "📊 Overview"

# container for the main view selector
view_container = st.container()


# function to calculate streaks
def calculate_streaks(dates, freq):
    if len(dates) == 0:
        return 0,0
    dates = sorted(dates)
    longest = current = 1
    max_streak = 1

    for i in range(1, len(dates)):
        gap = (dates[i] - dates[i-1]).days
        if (
            (freq == 'Daily' and gap == 1) or
            (freq == "Weekly" and gap <= 7) or
            (freq == "Monthly" and (dates[i].month != dates[i-1].month and gap <= 31))
        ):
            current += 1
            max_streak = max(max_streak, current)
        else:
            current = 1

    today = pd.to_datetime("today").normalize()
    days_since_last = (today - dates[-1]).days
    is_still_active = (
        (freq == "Daily" and days_since_last <= 1) or
        (freq == "Weekly" and days_since_last <=7) or
        (freq == "Monthly" and days_since_last <= 31)
    )
    current_streak = current if is_still_active else 0
    return max_streak, current_streak

def calculate_streaks_grouped(df):
    """
    Calculate the longest and current streak across multiple habits with different frequencies.
    Expects a DataFrame with 'habit_id', 'log_date', and 'frequency' columns.
    """
    overall_max_streak = 0
    overall_current_streak = 0

    # Group by habit
    grouped = df.groupby('habit_id')
    
    for habit_id, group in grouped:
        dates = sorted(pd.to_datetime(group['log_date']).dt.normalize())
        freq = group['frequency'].iloc[0]
        max_streak, current_streak = calculate_streaks(dates, freq)

        overall_max_streak = max(overall_max_streak, max_streak)
        overall_current_streak = max(overall_current_streak, current_streak)

    return overall_max_streak, overall_current_streak

def average_log_interval(log_dates):
    """Calculates the average interval between logs"""
    if len(log_dates) < 2:
        return 0
    log_dates = sorted(pd.to_datetime(log_dates))
    intervals = [(log_dates[i] - log_dates[i-1]).days for i in range(1, len(log_dates))]
    return sum(intervals) / len(intervals)

def calculate_log_intervals_overtime(log_dates):
    """Calculates the intervals between logs over time"""
    log_dates = sorted(pd.to_datetime(log_dates))
    intervals = []
    for i in range(1, len(log_dates)):
        gap = (log_dates[i] - log_dates[i-1]).days
        intervals.append({
            'log_date': log_dates[i],
            'interval': gap
        })
    return pd.DataFrame(intervals)

def calculate_expected_logs(date, frequency):
    today = pd.to_datetime("today").normalize()
    date = pd.to_datetime(date)
    # if frequency is daily, expected logs is days between start date and today
    if frequency == "Daily":
        expected_logs = max((today - date).days + 1, 1)
    # if frequency is weekly, expected logs is weeks between start date and today
    elif frequency == "Weekly":
        expected_logs = max(((today - date).days // 7)+1,1)
    # if frequency is monthly, expected logs is months between start date and today
    elif frequency == "Monthly":
        expected_logs = max(((today.year - date.year) * 12 + (today.month - date.month)) + 1, 1)
    return expected_logs

def plot_bar_chart(df, group_col, value_col, x_title, y_title, orientation='horizontal'):
    """Plots bar chart with altair"""
    if orientation == 'vertical':
        # vertical bar chart
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(f'{group_col}:N', sort=None, title=x_title, axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f'{value_col}:Q', title=y_title),
            tooltip=[
                alt.Tooltip(f'{group_col}:N',title=x_title),
                alt.Tooltip(f'{value_col}:Q', title=y_title)]
        ).properties(
            width=600,
            height = 400
        )
    else:
        # horizontal bar chart
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(f'{value_col}:Q', title=x_title),
            y=alt.Y(f'{group_col}:N', sort='-x', title=y_title),
            tooltip=[
                alt.Tooltip(f'{group_col}:N',title=x_title),
                alt.Tooltip(f'{value_col}:Q', title=y_title)]
        ).properties(
            width=600,
            height = 400
        )
    return chart

def plot_line_chart(df, date_col, value_col, x_title, y_title, target_value=None, y_min=None, y_max=None, y_tick_count=None):
    """Plots a line chart with altair"""
    # df['display_date'] = pd.to_datetime(df[date_col]).dt.strftime('%a %d')
    # df[date_col] = df[date_col].dt.strftime('%Y-%m-%d')
    df[date_col] = pd.to_datetime(df[date_col])
    df[value_col] = df[value_col].astype(float)

    chart = alt.Chart(df).properties(
        width = 700,
        height = 400
    )
    
    line = chart.mark_line(point=True).encode(
        x=alt.X(f'{date_col}:T',
                title=x_title,
                # sort=alt.SortField(field=date_col, order='ascending')
                ),
        y=alt.Y(f'{value_col}:Q', 
                title=y_title,
                scale=alt.Scale(domain=[y_min, y_max]) if y_min is not None and y_max is not None else alt.Undefined,
                axis=alt.Axis(title=y_title, tickCount=y_tick_count) if y_tick_count else alt.Undefined),
        tooltip=[
            alt.Tooltip(f'{date_col}:T', title=x_title),
            alt.Tooltip(f'{value_col}:Q', title=y_title)
        ]
    )

    # add target line if specified
    if target_value is not None:
        # target_df = pd.DataFrame({value_col: [target_value]})
        # rule = alt.Chart(target_df).mark_rule(color='red').encode(y=alt.Y(f'{value_col}:Q'))
        # yscale = alt.Scale(domain=[
        #     min(df[value_col].min(), target_value),
        #     max(df[value_col].max(), target_value)
        # ])
        
        rule = chart.mark_rule(color='red').encode(
            alt.Y(f'max({target_value}):Q'))

        # text = alt.Chart().mark_text(
        #     text='Target',
        #     align='right',
        #     baseline='bottom',
        #     dx=5,
        #     dy=-5,
        #     color='red'
        # ).encode(
        #    # y=alt.datum(target_value),
        #     # x=alt.value(chart.width - 30 )
        # )

        chart = line + rule
    else:
        chart = line

    return chart

def plot_calplot(df, date_col, cmap='YlGn'):
    """Plots a calendar plot"""
    cal_data = df.groupby(date_col).size()
    cal_data.index = pd.to_datetime(cal_data.index)
    fig,ax = calplot.calplot(cal_data, cmap=cmap, figsize=(8,3))
    return fig,ax

def create_wordcloud(df, notes_col):
    """Create wordcloud"""
    notes = df[notes_col].dropna().to_list()
    text = " ".join(notes)
    if text.strip() == "":
        st.info("Wordcloud not available because there are not enough notes from your logs to build the visual")
    else:
        wordcloud = WordCloud(width=800, height=400, background_color='white',colormap='viridis').generate(text)
        fig,ax = plt.subplots(figsize=(6,4))
        ax.imshow(wordcloud,interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

def text_preprocessor(text):
    """Preprocesses text for sentiment analysis"""
    # tokenize text
    tokens = word_tokenize(text.lower())
    # remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stop_words]
    # lemmatize text
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
    # get processed text
    processed_text = ' '.join(lemmatized_tokens)
    return processed_text

# initialize the VADER sentiment analyzer
@st.cache_resource
def load_nltk_resources():

    try:
        nltk.download('punkt_tab', quiet=True)
    except:
        nltk.download('punkt', quiet=True)
    resources = [
        ('sentiment/vader_lexicon.zip', 'vader_lexicon'),
        ('corpora/stopwords', 'stopwords'),
        ('corpora/wordnet', 'wordnet')
    ]

    for resource_path, download_name in resources:
        try:
            nltk.data.find(resource_path)
        except (LookupError, ImportError):
            nltk.download(download_name)

    return SentimentIntensityAnalyzer()
sid = load_nltk_resources()
def sentiment_analyzer(text):
    """Analyzes the sentiment of a text"""
    # get sentiment scores
    scores = sid.polarity_scores(text)['compound']
    # criteria for sentiment classification
    if scores >= 0.05:
        return 'positive'
    elif scores <= -0.05:
        return 'negative'
    else:
        return 'neutral'

def get_sentiment_results(df, sentiment_col):
    """Gets the percentage of each sentiment"""
    sentiment_counts = df[sentiment_col].value_counts()
    sentiment_percentage  = (sentiment_counts/len(df) * 100).round(2)
    sentiment_df = pd.DataFrame({
        'Sentiment': sentiment_counts.index,
        'Percentage': sentiment_percentage.values
    })
    sentiment_df = sentiment_df.sort_values(by='Percentage', ascending=False).reset_index(drop=True)
    return sentiment_df




def show_sidebar(merged_df):
    with st.sidebar:
        st.title('Filters')
        if st.session_state.sub_option == "📊 Overview":
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
            return overview_df
        elif st.session_state.sub_option == "📈 Activity Analytics":
            # category filters
            analytics_categories = merged_df['category'].unique()
            analytics_selected_category = st.selectbox('Select category', options=analytics_categories)

            analytics_df01 = merged_df[merged_df['category'] == analytics_selected_category]

            # habit filters
            analytics_habits = analytics_df01['name'].unique()
            analytics_selected_habit = st.selectbox("Select habit", options=analytics_habits)
            analytics_df = analytics_df01[analytics_df01['name'] == analytics_selected_habit]
            return analytics_df
        elif st.session_state.sub_option == "🗃️ Data":
            # data filters for data page
            data_categories = merged_df['category'].unique()
            data_categories_with_all = ['All categories'] + sorted(data_categories)
            selected_data_category = st.selectbox("Select category", options=data_categories_with_all)
            if selected_data_category == 'All categories':
                data_df = merged_df.copy()
            else:
                data_df = merged_df[merged_df['category'] == selected_data_category]
            # habit filters
            data_habits = data_df['name'].unique()
            data_habits_with_all = ['All habits'] + sorted(data_habits)
            selected_data_habit = st.selectbox("Select habit", options=data_habits_with_all)
            if selected_data_habit == 'All habits':
                data_df = data_df.copy()
            else:
                data_df = data_df[data_df['name'] == selected_data_habit]
            # date filters
            data_start_date = st.date_input("Start date", data_df['log_date'].min().date())
            data_end_date = st.date_input("End date", data_df['log_date'].max().date())
            data_start_date = pd.to_datetime(data_start_date)
            data_end_date = pd.to_datetime(data_end_date)
            data_df = data_df[(data_df['log_date'] >= data_start_date) & (data_df['log_date'] <= data_end_date)]
            return data_df

def show_visuals(df):
    if st.session_state.sub_option == "📊 Overview":
        # st.header("📈 Visualize your progress")

        # create 2 columns for charts
        col1, col2 = st.columns(2)

        with col1:
            # columns for KPI metrics
            kpi1,kpi2,kpi3 = st.columns(3)
            with kpi1:
                # with st.container(height=100):
                    # total habits
                    st.metric(label="Total Habits", value=df['habit_id'].nunique(), border=True)
            with kpi2:
                # with st.container(height=100):
                # total logs
                st.metric(label="Total Logs", value=df['log_id'].nunique(), border=True)
            with kpi3:
                # average rating
                st.metric(label="Average Rating", value=round(df['rating'].mean(),2), delta_color="normal", border=True)
                
            # completion rate visual
            with st.container(height=500):
                st.subheader("✅ Completion Rate")
                today = pd.to_datetime(datetime.now().date())
                consistency_list = []
                unique_habits = df[['habit_id', 'name', 'frequency', 'start_date']].drop_duplicates()
                for index,row in unique_habits.iterrows():
                    habit_id = row['habit_id']
                    name = row['name']
                    frequency = row['frequency']
                    start_date = pd.to_datetime(row['start_date'])
                    # actual logs
                    actual_logs = df[df['habit_id'] == habit_id].shape[0]
                    # calculate expected logs based on habit frequency
                    expected_logs = calculate_expected_logs(start_date, frequency)
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
                st.dataframe(consistency_df, hide_index=True)

            with st.container(height=500):
                # average rating per habit visual
                habit_averages = df.groupby('name')['rating'].mean().round(2).reset_index().sort_values(by='rating',ascending=True)
                st.subheader("⭐ Average Rating by Activity")
                chart = plot_bar_chart(habit_averages,'name', 'rating', 'Activity', 'Average Rating')
                st.altair_chart(chart, use_container_width=True)
                # st.checkbox("Show values on chart", value=True)



        with col2:
            # columns for KPI metrics
            kpi4,kpi5, kpi6 = st.columns(3)
            with kpi4:
                    # best habit
                best_habit = df.groupby('name')['rating'].mean().idxmax()
                st.metric(label="Best Habit (By rating)", value=best_habit, delta_color="normal", border=True)

                    # st.metric(label="Total Categories", value=df['category'].nunique(), border=True)
            with kpi5:
                # longest streak
                longest_streak, current_streak = calculate_streaks_grouped(df)
                st.metric(label="Longest Streak", value=longest_streak, delta_color="normal", border=True)
            with kpi6:
                # average completion rate
                unique_habits = df[['habit_id', 'frequency', 'start_date']].drop_duplicates()
                total_expected_logs = 0
                total_actual_logs = 0
                for index,row in unique_habits.iterrows():
                    habit_id = row['habit_id']
                    frequency = row['frequency']
                    start_date = pd.to_datetime(row['start_date'])
                    # actual logs
                    actual_logs = df[df['habit_id'] == habit_id].shape[0]
                    # calculate expected logs based on habit frequency
                    expected_logs = calculate_expected_logs(start_date, frequency)
                    total_expected_logs += expected_logs
                    total_actual_logs += actual_logs
                if total_expected_logs > 0:
                    average_completion_rate = round((total_actual_logs/total_expected_logs) * 100,2)
                else:
                    average_completion_rate = 0
                # with st.container(height=100):
                #     st.write("Average Completion Rate")
                #     if average_completion_rate < 80:
                #         st.markdown(f"<h4 style='color:red;'>{average_completion_rate:.2f}%</h4>", unsafe_allow_html=True)
                #     else:
                #         st.markdown(f"<h4 style='color:green;'>{average_completion_rate:.2f}%</h4>", unsafe_allow_html=True)
                st.metric(label="Average Completion Rate", value=f"{average_completion_rate}%", delta_color="normal", border=True)


            with st.container(height=500):
                # goal achievement visual
                st.subheader("🎯 Goal Achievement")
                # filter for only tracking types that allow for goal tracking
                goal_df = df[df['tracking_type'].isin(['Duration (Minutes/hours)', 'Count (Number-based)'])]
                if goal_df.shape[0] == 0:
                    st.info("This category does not have habits to be displayed for this visual")
                else:
                    # calculate achievement per activity log
                    goal_df['goal_achievement'] = ((goal_df['activity'].astype(float) / goal_df['goal'].astype('float')) * 100).clip(upper=100)
                    # group by habit
                    habit_achievement = (goal_df.groupby('habit_id').agg(
                        average_goal_achievement = ("goal_achievement", "mean"),
                        total_logs = ("log_id", 'count'),
                        habit_name = ("name", 'first')
                    ).reset_index().sort_values(by='average_goal_achievement', ascending=True)).round(2)
                    # plot visual
                    chart = plot_bar_chart(habit_achievement, 'habit_name', 'average_goal_achievement', 'Activity', 'Goal Achievement Rate')
                    st.altair_chart(chart, use_container_width=True)

            with st.container(height=500):
                # give users option to select wordcloud visual or sentiment analysis
                # st.subheader("Highlights and Sentiment Analysis from your activity logs")
                # st.write("Select the visual you want to see")
                st.subheader("💡 Insights from Activity Logs")
                tab1, tab2 = st.tabs(['Highlights', 'Sentiment Analysis'])
                with tab1:
                    # wordcloud visual
                    # st.subheader("Highlights from your activity logs")
                    # create wordcloud
                    create_wordcloud(df, 'log_notes')
                with tab2:
                    # sentiment analysis
                    df['processed_text'] = df['log_notes'].apply(text_preprocessor)
                    df['sentiment'] = df['processed_text'].apply(sentiment_analyzer)
                    # st.subheader('Sentiment Analysis')
                    overview_sentiments = get_sentiment_results(df, 'sentiment')
                    fig,ax = plt.subplots(figsize=(4,3))
                    ax.pie(overview_sentiments['Percentage'], labels=overview_sentiments['Sentiment'], autopct='%1.1f%%', startangle=90)
                    ax.axis('equal')
                    st.pyplot(fig)
                    # st.dataframe(overview_sentiments, hide_index=True)

        # log calendar visual
        st.subheader("📅 Log Calendar")
        # github_cmap = mcolors.ListedColormap([
        # "#ebedf0",  # 0 contributions
        # "#c6e48b",  # 1-9 contributions
        # "#7bc96f",  # 10-19
        # "#239a3b",  # 20-29
        # "#196127"   # 30+
        #     ])
        fig,ax = plot_calplot(df, 'log_date')
        st.pyplot(fig, use_container_width=True)
    elif st.session_state.sub_option == "📈 Activity Analytics":
        habit_name  = df['name'].unique()[0]
        st.metric(label='Activity', value=habit_name)
        # create 2 columns for visuals
        ana1, ana2 = st.columns(2)

        with ana1:
            # columns for KPI metrics
            kpi1,kpi2, kpi3 = st.columns(3)
            with kpi1:
                st.metric(label="Total Logs", value=df['log_id'].nunique(), border=True)
            with kpi2:
                # completion rate
                # calculate expected logs based on habit frequency
                frequency = df['frequency'].unique()[0]
                start_date = pd.to_datetime(df['start_date'].unique()[0])
                actual_logs = df.shape[0]
                expected_logs = calculate_expected_logs(start_date, frequency)
                completion_rate = round((actual_logs/expected_logs) * 100,2)
                st.metric(label="Completion Rate", value=f"{completion_rate}%", delta_color="normal", border=True)
            with kpi3:
                # average rating
                avg_rating = df['rating'].mean()
                st.metric(label="Average Rating", value=round(avg_rating,2), delta_color="normal", border=True)
                # 
            with st.container(height=500):
                # create summary table
                st.subheader("📋 Summary")
                habit = df.iloc[0]
                name = habit['name']
                goal = habit['goal']
                goal_units = habit['goal_units']
                frequency = habit['frequency']
                tracking = habit['tracking_type']
                start_date = habit['start_date']
                # goal achievement
                if tracking == "Yes/No (Completed or not)":
                    df['goal_achievement'] = np.nan
                else:
                    df['goal_achievement'] = ((df['activity'].astype(float) / float(goal)) * 100).clip(upper=100)
                # average goal achievement
                avg_goal = df['goal_achievement'].mean()
                # average rating
                avg_rating = df['rating'].mean()
                # first and last logs
                first_log = df['log_date'].min()
                last_log = df['log_date'].max()
                # total logs
                total_logs = df.shape[0]
                # expected logs
                expected_logs = calculate_expected_logs(start_date, frequency)
                # completion rate
                completion_rate = round((total_logs/expected_logs) * 100,2)
                # target
                if pd.notna(goal) and goal not in [0, ""]:
                    target = f"{int(goal)}  {goal_units.lower()}  {frequency.lower()}"
                else:
                    target = frequency
                # streaks
                dates = df['log_date'].to_list()
                longest_streak, current_streak = calculate_streaks(dates, frequency)
                # average log interval
                avg_interval = average_log_interval(dates)
                # create summary data
                summary_data = {
                    'Target': target,
                    'Expected Logs': expected_logs,
                    'Total Logs': total_logs,
                    'Completion Rate': f'{completion_rate}%',
                    'Average Rating': round(avg_rating, 2),
                    'First Log Date': first_log.date(),
                    'Last Log Date': last_log.date(),
                    'Longest Streak': longest_streak,
                    'Current Streak': current_streak,
                    'Average Log Interval': f"{avg_interval:.2f} days"

                }
                # convert to dataframe
                summary_df = pd.DataFrame(summary_data.items(), columns=['Metric', 'Value'])
                st.dataframe(summary_df, hide_index=True)

            with st.container(height=500):
                # line chart for activity logs against target
                # add emoji
                st.subheader('🎯 Log vs Target')
                if tracking != "Yes/No (Completed or not)":
                    goal = int(goal)
                    chart = plot_line_chart(df, 'log_date', 'activity', 'Log Date', goal_units,'goal', y_min=0, y_max=goal+10, y_tick_count=5)
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("This visual is not available for this activity")

            with st.container(height=500):
                # day of week visual
                df['day_of_week'] = df['log_date'].dt.day_name()
                order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=order, ordered=True)
                day_counts = df['day_of_week'].value_counts().sort_index().reset_index()
                st.subheader("🗓️ Activity Logs by Day of Week")
                # st.dataframe(day_counts, hide_index=True)
                chart = plot_bar_chart(day_counts, 'day_of_week', 'count', 'Number of Logs', 'Day of Week', orientation='vertical')
                st.altair_chart(chart, use_container_width=True)



        with ana2:
            # columns for KPI metrics
            kpi4,kpi5, kpi6 = st.columns(3)
            with kpi4:
                # current streak
                _ , current_streak = calculate_streaks_grouped(df)
                st.metric(label="Current Streak", value=current_streak, delta_color="normal", border=True)
                # st.metric(label="N/A", value="N/A", border=True)
            with kpi5:
                # context aware kpi for duration, count, or yes/no
                if tracking == "Yes/No (Completed or not)":
                    # yes/no tracking
                    completed = df[df['activity'] == "Yes"].shape[0]
                    # st.write(completed)
                    # not_completed = df.shape[0] - completed
                    st.metric(label="Completed", value=completed, delta_color="normal", border=True)
                elif tracking == "Duration (Minutes/hours)":
                    # duration tracking
                    total_duration = df['activity'].sum()
                    if total_duration > 60:
                        hours = round(total_duration / 60,2)
                        st.metric(label="Total Duration", value=f"{hours} hours", delta_color="normal", border=True)
                    else:
                        st.metric(label="Total Duration", value=f"{total_duration} minutes", delta_color="normal", border=True)
                elif tracking == "Count (Number-based)":
                    # count tracking
                    total_count = df['activity'].sum()
                    goal_units = df['goal_units'].unique()[0]
                    st.metric(label=goal_units, value=total_count, delta_color="normal", border=True)
            with kpi6:
                # goal achievement rate
                tracking = df['tracking_type'].unique()[0]
                goal = df['goal'].unique()[0]
                if tracking != "Yes/No (Completed or not)":
                    df['goal_achievement'] = ((df['activity'].astype(float) / float(goal)) * 100).clip(upper=100)
                    goal_achievement = f"{round(df['goal_achievement'].mean(),2)}%"
                else:
                    goal_achievement = 'N/A'
                st.metric(label="Goal Achievement Rate", value=goal_achievement, delta_color="normal", border=True)

            with st.container(height=500):
                st.subheader("📈 Rating Trends")
                chart = plot_line_chart(df,'log_date','rating', 'Log Date', 'Rating', y_tick_count=5)
                st.altair_chart(chart, use_container_width=True)

            with st.container(height=500):
                st.subheader("💡 Insights from Activity Logs")
                tab1, tab2 = st.tabs(['Highlights', 'Sentiment Analysis'])
                with tab1:
                    create_wordcloud(df, 'log_notes')
                with tab2:
                    # sentiment analysis
                    df['processed_text'] = df['log_notes'].apply(text_preprocessor)
                    df['sentiment'] = df['processed_text'].apply(sentiment_analyzer)
                    # pie chart for sentiment analysis
                    fig,ax = plt.subplots(figsize=(4,3))
                    ax.pie(df['sentiment'].value_counts(), labels=df['sentiment'].value_counts().index, autopct='%1.1f%%', startangle=90)
                    ax.axis('equal')
                    st.pyplot(fig)
                    # st.write('Sentiment Analysis')
                    # sentiment_df = get_sentiment_results(df, 'sentiment')
                    # st.dataframe(sentiment_df, hide_index=True)

            # log intervals over time
            with st.container(height=500):
                st.subheader("⌚ Log Intervals Over Time")
                log_intervals = calculate_log_intervals_overtime(df['log_date'])
                chart = plot_line_chart(log_intervals, 'log_date', 'interval', 'Log Date', 'Interval (Days)', y_tick_count=5)
                st.altair_chart(chart, use_container_width=True)



        # log calendar visual
        st.subheader(" 📅 Log Calendar")
        fig,ax = plot_calplot(df, 'log_date', cmap='YlGn_r')
        st.pyplot(fig, use_container_width=True)

    elif st.session_state.sub_option == "🗃️ Data":
        data = df[['log_date','name','category','activity','goal','goal_units','tracking_type','rating','log_notes']]
        data.rename(columns={
            'log_date': 'Log Date',
            'name': 'Activity',
            'category': 'Category',
            'activity': 'Activity (Yes/No/Count/Duration)',
            'goal': 'Goal',
            'goal_units': 'Goal Units',
            'tracking_type': 'Tracking Type',
            'rating': 'Rating',
            'log_notes': 'Notes'
        }, inplace=True)
        st.header("Your activity logs data")
        # tab1, tab2, tab3 = st.tabs(['📊 Overview', '📈 Activity Analytics',  "🗃️ Data" ])
        st.write(f"Showing {len(data)} records based on your filter selections.")
        st.dataframe(data, hide_index=True)
        # st.dataframe(habit_df)






def show_analytics(merged_df):
    """Main function to show the analytics page"""
    st.radio(label="Sub", options=["📊 Overview", "📈 Activity Analytics", "🗃️ Data"], key="sub_option", label_visibility='collapsed', horizontal=True)
    df = show_sidebar(merged_df)
    show_visuals(df)
    # with st.sidebar:
    #     st.write('Testing')
    #     if st.session_state.sub_option == "📊 Overview":
    #         st.write("Filters for option 1")
    #     elif st.session_state.sub_option == "2":
    #         st.write("Filters for option 2")
    #     elif st.session_state.sub_option == "3":
    #         st.write("Filters for option 3")

