
# When the user enter the text file of their chat this function will convert that txt file into the dataframe
# Library for regular expression
import re
import pandas as pd


def preprocess(data):
    pattern_24hrs = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'

    messages_24hrs = re.split(pattern_24hrs, data)[1:]
    messages_24hrs  # this is a list

    # if the time is in 12hr format
    if bool(messages_24hrs) == False:
        pattern_12hrs = '\d{1,2}\/\d{2,4}\/\d{2,4},\s\d{1,2}:\d{1,2}\s\w{1,2}'
        messages_12hrs = re.split(pattern_12hrs, data)[1:]

    ## Finding the list
    if bool(messages_24hrs) == False:
        dates = re.findall(pattern_12hrs, data)
    else:
        dates = re.findall(pattern_24hrs, data)

    if bool(messages_24hrs) == True:
        df = pd.DataFrame({'user_message': messages_24hrs, 'message_date': dates})
    else:
        df = pd.DataFrame({'user_message': messages_12hrs, 'message_date': dates})

    ## Converting the message_date type
    from datetime import datetime
    if bool(messages_24hrs) == True:
        df["message_date"] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %H:%M - ')
        df.rename(columns={"message_date": "date"}, inplace=True)
    else:
        date = []
        time = []
        for column in df["message_date"].values:
            x = column.split(", ")

            date.append(x[0])
            time.append(x[1])
        df["date"] = date
        df["time"] = time

        updated_time = []
        for column in df["time"].values:
            x = column.split("- ")
            updated_time.append(x[0])
        df["time"] = updated_time


    ## Separating user and their messages
    users = []
    messages = []
    for message in df['user_message']:
        if bool(messages_24hrs) == True:
            entry = re.split('([\w\W]+?):\s', message)
        else:
            entry = re.split('-([\w\W]+?):\s', message)

        if entry[1:]:  ## user name
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append("group_notification")
            messages.append(entry[0])
    df["user"] = users
    df["messages"] = messages

    df.drop(columns=["user_message"], inplace=True)

    if bool(messages_24hrs) == True:
        df['year'] = df["date"].dt.year
        df["month_num"] = df["date"].dt.month
        df["month_name"] = df["date"].dt.month_name()
        df["day"] = df["date"].dt.day
        df["hour"] = df["date"].dt.hour
        df["minute"] = df["date"].dt.minute
        df["daily"] = df["date"].dt.date
        df["Day_name"] = df["date"].dt.day_name()

        period = []
        for hour in df[["Day_name", "hour"]]["hour"]:
            if hour == 23:
                period.append(str(hour) + "-" + str("00"))
            elif hour == 0:
                period.append(str("00") + "-" + str(hour + 1))
            else:
                period.append(str(hour) + "-" + str(hour + 1))

        df["Period"] = period

    else:  # If it is 12hr format
        df["date"] = pd.to_datetime(df["date"])
        df["time"] = pd.to_datetime(df["time"])
        df['year'] = df["date"].dt.year
        df["month_num"] = df["date"].dt.month
        df["month_name"] = df["date"].dt.month_name()
        df["day"] = df["date"].dt.day
        df["hour"] = df["time"].dt.hour
        df["minute"] = df["time"].dt.minute
        df["daily"] = df["date"].dt.date
        df["Day_name"] = df["date"].dt.day_name()

        period = []
        for hour in df[["Day_name", "hour"]]["hour"]:
            if hour == 23:
                period.append(str(hour) + "-" + str("00"))
            elif hour == 0:
                period.append(str("00") + "-" + str(hour + 1))
            else:
                period.append(str(hour) + "-" + str(hour + 1))
        df["Period"] = period

    return df

