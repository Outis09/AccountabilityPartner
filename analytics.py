import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import seaborn as sns
import calplot
from db import db_operations as db
import altair as alt
# wordcloud
from wordcloud import WordCloud
from datetime import datetime, timedelta
# sentiment analysis
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
# nltk.download(['vader_lexicon', 'punkt_tab', 'stopwords', 'wordnet'])

# set page config
st.set_page_config(
    page_title="Accountability Partner",
    page_icon="📊",
    layout="wide"
)
# page title
# st.title("Accountability Partner")
logo_icon = "AppLogo.png"
logo_image = "AppLogo.png"
st.logo(image=logo_image, size='large')


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

def plot_bar_chart(df, group_col, value_col, x_title, y_title):
    """Plots bar chart with altair"""
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
# sidebar for filters
with st.sidebar:
    st.title("Accountability Partner")
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
        on_change=update_active_view,
        label_visibility='collapsed'
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
        habit_averages = overview_df.groupby('name')['rating'].mean().round(2).reset_index().sort_values(by='rating',ascending=True)
        st.subheader("Average rating by activity")
        chart = plot_bar_chart(habit_averages,'name', 'rating', 'Activity', 'Average Rating')
        st.altair_chart(chart, use_container_width=True)
        # st.checkbox("Show values on chart", value=True)

        # wordcloud visual
        st.subheader("Highlights from your activity logs")
        # create wordcloud
        create_wordcloud(overview_df, 'log_notes')
        # sentiment analysis
        overview_df['processed_text'] = overview_df['log_notes'].apply(text_preprocessor)
        overview_df['sentiment'] = overview_df['processed_text'].apply(sentiment_analyzer)
        st.write('Sentiment Analysis')
        overview_sentiments = get_sentiment_results(overview_df, 'sentiment')
        st.dataframe(overview_sentiments, hide_index=True)

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
            ).reset_index().sort_values(by='average_goal_achievement', ascending=True)).round(2)
            # plot visual
            chart = plot_bar_chart(habit_achievement, 'habit_name', 'average_goal_achievement', 'Activity', 'Goal Achievement Rate')
            st.altair_chart(chart, use_container_width=True)




    # log calendar visual
    st.subheader("Log Calendar")
    # github_cmap = mcolors.ListedColormap([
    # "#ebedf0",  # 0 contributions
    # "#c6e48b",  # 1-9 contributions
    # "#7bc96f",  # 10-19
    # "#239a3b",  # 20-29
    # "#196127"   # 30+
    #     ])
    fig,ax = plot_calplot(overview_df, 'log_date')
    st.pyplot(fig, use_container_width=True)
elif st.session_state.active_view == "📈 Activity Analytics":
    st.header("Detailed Habit Analysis")
    # create 2 columns for visuals
    ana1, ana2 = st.columns(2)

    with ana1:
        # create summary table
        st.subheader("Activity Summary")
        habit = analytics_df.iloc[0]
        name = habit['name']
        goal = habit['goal']
        goal_units = habit['goal_units']
        frequency = habit['frequency']
        tracking = habit['tracking_type']
        start_date = habit['start_date']

        # goal achievement
        if tracking == "Yes/No (Completed or not)":
            analytics_df['goal_achievement'] = np.nan
        else:
            analytics_df['goal_achievement'] = ((analytics_df['activity'].astype(float) / goal.astype(float)) * 100).clip(upper=100)
        # average goal achievement
        avg_goal = analytics_df['goal_achievement'].mean()
        # average rating
        avg_rating = analytics_df['rating'].mean()
        # first and last logs
        first_log = analytics_df['log_date'].min()
        last_log = analytics_df['log_date'].max()
        # total logs
        total_logs = analytics_df.shape[0]
        # expected logs
        expected_logs = calculate_expected_logs(start_date, frequency)
        # target
        if pd.notna(goal) and goal not in [0, ""]:
            target = f"{int(goal)}  {goal_units.lower()}  {frequency.lower()}"
        else:
            target = frequency
        # streaks
        dates = analytics_df['log_date'].to_list()
        longest_streak, current_streak = calculate_streaks(dates, frequency)
        summary_data = {
            'Activity': name,
            'Target': target,
            'Expected Logs': expected_logs,
            'Total Logs': total_logs,
            'Average Rating': round(avg_rating, 2),
            'First Log Date': first_log.date(),
            'Last Log Date': last_log.date(),
            'Longest Streak': longest_streak,
            'Current Streak': current_streak
        }
        # convert to dataframe
        summary_df = pd.DataFrame(summary_data.items(), columns=['Metric', 'Value'])
        st.dataframe(summary_df, hide_index=True)

        # line chart for activity logs against target
        st.subheader('Log vs Target')
        if tracking != "Yes/No (Completed or not)":
            goal = int(goal)
            chart = plot_line_chart(analytics_df, 'log_date', 'activity', 'Log Date', goal_units,'goal', y_min=0, y_max=goal+10, y_tick_count=5)
            st.altair_chart(chart, use_container_width=True)


    with ana2:
        st.subheader("Rating Trends")
        chart = plot_line_chart(analytics_df,'log_date','rating', 'Log Date', 'Rating', y_tick_count=5)
        st.altair_chart(chart, use_container_width=True)

        st.subheader("Highlights from your activity logs")
        create_wordcloud(analytics_df, 'log_notes')
        # sentiment analysis
        analytics_df['processed_text'] = analytics_df['log_notes'].apply(text_preprocessor)
        analytics_df['sentiment'] = analytics_df['processed_text'].apply(sentiment_analyzer)
        st.write('Sentiment Analysis')
        sentiment_df = get_sentiment_results(analytics_df, 'sentiment')
        st.dataframe(sentiment_df, hide_index=True)



    # log calendar visual
    st.subheader("Log Calendar")
    fig,ax = plot_calplot(analytics_df, 'log_date', cmap='YlGn_r')
    st.pyplot(fig, use_container_width=True)

elif st.session_state.active_view == "🗃️ Data":
    df = merged_df.copy()
    st.header("Your activity logs data")
    # tab1, tab2, tab3 = st.tabs(['📊 Overview', '📈 Activity Analytics',  "🗃️ Data" ])
    st.write(f"Showing {len(df)} records based on your filter selections.")
    st.dataframe(df, hide_index=True)
    # st.dataframe(habit_df)


