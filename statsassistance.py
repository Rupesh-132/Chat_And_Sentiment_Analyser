
from urlextract import URLExtract # Library to extract the links from messages
import requests

import emoji
import pandas as pd
from collections import Counter
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# vader_lexicon is a pre-trained sentiment analysis tool that is part of the nltk (Natural Language Toolkit) library in Python.
# It is based on the VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment analysis algorithm, which is specifically designed to analyze sentiments expressed in social media.
# The VADER lexicon is a list of words and associated sentiment scores,
# where the sentiment scores range from -1 to 1, with -1 representing a negative sentiment, 0 representing a neutral sentiment, and 1 representing a positive sentiment.
nltk.download('vader_lexicon')
import streamlit as st
import time


# Calculates stats on the group and user level
@st.experimental_memo
@st.cache(suppress_st_warning=True)
def get_stats(selected_user,df):
    if selected_user != 'Group':
        df = df[df['user'] == selected_user]

    # 1.number of messages
    number_of_messages = df.shape[0]
    # 2. total number or words
    total_words = []
    for message in df["messages"]:
        total_words.extend(message.split(" "))

    # 3. getting the number of media in the group
    number_of_media = df[df["messages"] == "<Media omitted>\n"].shape[0]

    # 4. Counting the total links in the group
    url_list = []
    for message in df["messages"]:
        url_list.extend(URLExtract().find_urls(message))

    return number_of_messages, len(total_words), number_of_media, len(url_list)


# Calculates the busiest user in the group
@st.experimental_memo
@st.cache(suppress_st_warning=True)
def get_busiest_user(df):
    # 1. top busiest users.
    X = df["user"].value_counts().head()

    # 2. %contribution selected user
    per_contri_df = round(df["user"].value_counts() / df.shape[0] * 100, 2).reset_index().rename(
        columns={"index": "Name", "user": "Contribution%"})
    return X,per_contri_df


# This function calculates overall emojis used in the group
@st.experimental_memo
@st.cache(suppress_st_warning=True)
def get_emoji(selected_user,df):
    if selected_user == "Group":
        emoji_list = []
        for message in df["messages"]:
            emoji_list.extend([c for c in message if c in emoji.EMOJI_DATA])
            df_emojis = pd.DataFrame(emoji_list).value_counts()
            emoji_types = df_emojis.index
            emoji_freq = df_emojis.values
            emoji_df = pd.DataFrame(list(zip(emoji_types, emoji_freq)),
                                    columns=['Emoji', 'Frequency'])
        return emoji_df


# This function calculates the emoji user wise
@st.experimental_memo
@st.cache(suppress_st_warning=True)
def plot_emoji(selected_user,df):

    user_df = df[df["user"] == selected_user]
    emoji_list_user = []
    for message in user_df["messages"]:
        emoji_list_user.extend([c for c in message if c in emoji.EMOJI_DATA])

    user_emojis = pd.DataFrame(emoji_list_user)
    user_raw_df = user_emojis.value_counts()
    user_emoji_df = pd.DataFrame(list(zip(user_raw_df.index, user_raw_df.values)), columns=["Emojis", "Frequency"])
    user_final_df = user_emoji_df.head(4)
    return user_final_df


@st.experimental_memo
@st.cache(suppress_st_warning=True)
def most_common_words(selected_user,df):

    # We can use hinglish stopwords i.e hindi+english to remove that from our dataframe

    f = open("stop_hinglish.txt", "r")
    stop_words = f.read()
    print(stop_words)

    # We only update the dataframe if the selected user is not Group
    if selected_user != 'Group':
        df = df[df['user'] == selected_user]

    # Remove group notification
    # Remove media omitted
    temp = df[df["user"] != "group_notification"]
    temp = temp[temp["messages"] != "<Media omitted>\n"]

    #  Counting the most 20 most common words
    words = []
    for message in temp["messages"]:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    comm_words_df = pd.DataFrame(Counter(words).most_common(20)).rename(columns={0: "Words", 1: "Count"})

    return  comm_words_df


# For the montly timeline
@st.experimental_memo
@st.cache(suppress_st_warning=True)
def monthly_timeline(selected_user,df):
    # We only update the dataframe if the selected user is not Group
    if selected_user != 'Group':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(["year", "month_name", "month_num"]).count()["messages"].reset_index()
    # Combining the year and month together
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline["month_name"][i] + "-" + str(timeline["year"][i]))

    timeline["time"] = time

    return timeline


@st.experimental_memo
@st.cache(suppress_st_warning=True)
def daily_timeline(selected_user,df):
    # We only update the dataframe if the selected user is not Group
    if selected_user != 'Group':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby("daily").count()["messages"].reset_index()
    daily_timeline["year"] = df["year"]

    return daily_timeline


@st.experimental_memo
@st.cache(suppress_st_warning=True)
def weekly_activities(selected_user,df):
    # We only update the dataframe if the selected user is not Group
    if selected_user != 'Group':
        df = df[df['user'] == selected_user]

    weekdays = df["Day_name"].value_counts().reset_index().rename(
        columns={"index": "Days", "Day_name": "Message_Count"})

    return weekdays


@st.experimental_memo
@st.cache(suppress_st_warning=True)
def monthly_activities(selected_user,df):
    # We only update the dataframe if the selected user is not Group
    if selected_user != 'Group':
        df = df[df['user'] == selected_user]

    months = df["month_name"].value_counts().reset_index().rename(
        columns={"index": "Month", "month_name": "Message_Count"})

    return months


@st.experimental_memo
@st.cache(suppress_st_warning=True)
def plot_heatmap(selected_user,df):
    if selected_user != 'Group':
        df = df[df['user'] == selected_user]
    activity_pivot_table =df.pivot_table(index="Day_name", columns="Period", values="messages", aggfunc="count")

    return activity_pivot_table


@st.experimental_memo
@st.cache(suppress_st_warning=True)
def sentiment_Analysis(selected_user,df):
    if selected_user != 'Group':
        df = df[df['user'] == selected_user]

    data = pd.DataFrame(df, columns=["date", "time", "user", "messages"])
    # df['Date']=pd.to_datetime(df[''])

    sentiments = SentimentIntensityAnalyzer()
    df["positive"] = [sentiments.polarity_scores(i)["pos"] for i in df["messages"]]
    df["negative"] = [sentiments.polarity_scores(i)["neg"] for i in df["messages"]]
    df["neutral"] = [sentiments.polarity_scores(i)["neu"] for i in df["messages"]]

    return df


# ---- LOAD ASSETS ----

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()
