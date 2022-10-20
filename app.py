import streamlit as st
import numpy as np
import preprocessor
import statsassistance
import matplotlib.pyplot as plt
import plotly.express as px
from plotly import graph_objects as go
import math

from streamlit_lottie import st_lottie
import requests
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")


st.sidebar.title("Chat Analyser")
uploaded_file = st.sidebar.file_uploader("Choose a file")


if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)
    st.header("Complete Chat Dataset")
    st.dataframe(df)

    # fetch unique users
    unique_user_list = df["user"].unique().tolist()

    # Remove user group_notification as it is not required
    unique_user_list.remove('group_notification')
    unique_user_list.sort()
    unique_user_list.insert(0,"Group")
    selected_user = st.sidebar.selectbox("Show analysis wrt",unique_user_list)

    # On button click -> Analysis will start
    if st.sidebar.button("Show Analysis"):

        number_of_messages,number_of_words,number_of_media,url_count = statsassistance.get_stats(selected_user,df)

        col1,col2,col3,col4 = st.columns(4)

        with col1:
            st.subheader("All Messages")
            st.title(number_of_messages)
        with col2:
            st.subheader("Total Words")
            st.title(number_of_words)
        with col3:
            st.subheader("Total Media")
            st.title(number_of_media)
        with col4:
            st.subheader("Link Shared")
            st.title(url_count)
        st.write("---")

        # Displaying the monthly-yearly timeline graph
        timeline = statsassistance.monthly_timeline(selected_user,df)
        fig = px.line(timeline, x="time", y="messages", title='Messages across time')
        fig.update_layout(height=600)
        fig.update_layout(width=4000)
        st.plotly_chart(fig, height=600, width=6000, use_container_width=True)
        st.write("---")

        # Displaying the daily timeline
        daily_timeline = statsassistance.daily_timeline(selected_user,df)
        fig = px.line(daily_timeline, x="daily", y="messages", title='Messages daily', color="year")
        fig.update_layout(height=600)
        fig.update_layout(width=4000)
        st.plotly_chart(fig, height=600, width=6000, use_container_width=True)
        st.write("---")

        # Displaying the most busy days
        st.title("Most Busy Days")
        weekdays = statsassistance.weekly_activities(selected_user,df)
        fig.update_layout(height=600)
        fig.update_layout(width=6000)
        fig = px.bar(weekdays, x="Days", y="Message_Count", color="Days", title=str(weekdays["Days"][0])+" is the most  Busy Day")
        st.plotly_chart(fig, height=600, width=6000, use_container_width=True)
        st.write("---")

        # Displaying the most busy months
        st.title("Most Busy Months")
        months = statsassistance.monthly_activities(selected_user, df)
        fig.update_layout(height=600)
        fig.update_layout(width=6000)
        fig = px.bar(months, x="Month", y="Message_Count", color="Month",
                     title=str(months["Month"][0]) + " is the most  Busy Month")
        st.plotly_chart(fig, height=600, width=6000, use_container_width=True)
        st.write("---")

        # Displaying the heatmap of every hour on Days basis
        st.title("Activity Heatmap")
        activity_pivot_table = statsassistance.plot_heatmap(selected_user,df)
        plt.figure(figsize=(20, 6))
        fig,ax = plt.subplots()
        ax = sns.heatmap(activity_pivot_table)
        st.pyplot(fig)
        st.write("---")


        # Finding the busiest user in the group
        if selected_user == "Group":

            X,per_contri_df = statsassistance.get_busiest_user(df)
            figure,ax = plt.subplots()

            col1,col2 = st.columns(2)

            with col1:
                # 1. displaying the dataframe of the contribution
                st.header(" ")
                st.subheader("Dataset Of Contribution")
                st.dataframe(per_contri_df)
                st.write("\n")

            st.write("---")
            # 1. displaying the Funnel of the contribution
            st.header(" ")
            st.header("Funnel Of Contribution")

            fig = px.funnel(per_contri_df, x='Name', y='Contribution%')
            fig.update_layout(height=500)
            fig.update_layout(width=6000)
            st.plotly_chart(fig, height=600, width=4000, use_container_width=True)
            st.write("---")

            # 1. Plotting the funnel graph for the busiest users in the group
            Name = X.index
            Active_Count = np.round(X.values / df.shape[0] * 100, 2)
            st.header("Busiest Users")
            st.subheader(Name[0] + " is the most busiest user in the group!")
            fig = go.Figure(go.Funnel(
                y=Name,
                x=Active_Count,
                orientation="h",
                marker={"color": ["Purple", "Orange", "Green", "Brown", "tan"]}))
            fig.update_layout(height=500)
            st.plotly_chart(fig, height=600, width=1000,use_container_width=True)

            # Displaying the dataframe of various emojis used in the group
            with col2:
                st.header(" ")
                st.subheader("Emoji Used")
                emoji_df = statsassistance.get_emoji(selected_user,df)
                st.dataframe(emoji_df)
            st.write("---")

            # Displaying the dataframes of top emojis used by each user
            col1, col2 = st.columns(2)
            i = 0;
            for user in unique_user_list:
                if user!="Group":
                    user_final_df = statsassistance.plot_emoji(user,df)
                    with col1:
                        st.header(" ")
                        st.subheader(" ")
                        st.subheader(user)
                        st.dataframe(user_final_df)
                        st.write("---")

                    with col2:
                        # this is used just to align the pie properly in the display
                        st.text("")
                        if i == 0:
                            st.text("")
                            i = i+1

                        # pie using plotly
                        flag = True;
                        if user_final_df.empty:
                            flag = False

                        # If emoji dataframe is empty
                        if flag == False:
                            st.text(user)
                            st.info(user+" has not used any emojis!")
                            st.write("---")
                        else:
                            st.text(user)
                            fig = px.pie(user_final_df,values=user_final_df["Frequency"],names= user_final_df["Emojis"])
                            fig.update_layout(height=300)
                            fig.update_layout(width=300)
                            st.plotly_chart(fig,height=300, width=300,use_container_width=True)
                            st.write("---")

            st.write("---")
            with st.container():
                with col1:
                    st.subheader("Dataframe(Top 20 Words)")
                    most_comm_word = statsassistance.most_common_words(selected_user,df)
                    st.dataframe(most_comm_word)

            with st.container():
                st.subheader("Top 20 Most Common Words")
                fig.update_layout(height=700)
                fig.update_layout(width=7000)
                fig = px.bar(most_comm_word, x="Words", y="Count")
                st.plotly_chart(fig,height=300, width=300,use_container_width=True)
                st.write("---")


























