# import pandas as pd
# from datetime import date
# from datetime import timedelta
# import pdb
#
# users = pd.DataFrame({'user_name': ['A0', 'A1', 'A2', 'A3', 'A4', 'A5']}, index=['K0', 'K1', 'K2', 'K3', 'K4', 'K5'])
# posts = pd.DataFrame({'date': [date(2017,6,10), date(2017,6,8), date(2017,6,15), date(2017,6,24)],'text': ['hi', 'lolz', 'stuff', 'how are u boiz?'], 'user': ['K0', 'K1', 'K2', 'K0']})
#
# posts_users = posts.join(users, on="user",how="inner")
#
# def groupByWeek(df, index):
#     user = df['user'].loc[index]
#     date_of_row = df['date'].loc[index]
#     weekday =  date_of_row.weekday()
#     days_from_next_sunday =  timedelta(days = 6-weekday)
#     next_sunday = date_of_row + days_from_next_sunday
#     previous_saturday = next_sunday - timedelta(days = 6)
#     return previous_saturday.strftime("%d/%m/%y") + " - " + next_sunday.strftime("%d/%m/%y")
#
# #this can group by weeks but if we try to chain another group by to group by user, it blows up
# grouping = posts_users.groupby(by = ['user',lambda id: groupByWeek(posts_users, id)])
# new_df = pd.DataFrame({'weekly_post_total' : grouping.size()}).reset_index()
# print new_df[(new_df.user == "K0") & (new_df.level_1 == "05/06/17 - 11/06/17")]["weekly_post_total"][0]

import glob, re, json, csv, datetime

users = {}
with open('./av/users.json') as user_file:
    for user in json.load(user_file)["members"]:
        if 'email' in user['profile']:
            email = user['profile']['email']
        users[user['id']] = {"name": user['name'], "email": email}

def find_slack_id_by_email(user_email):
    for id, value in users.iteritems():
        if value['email'] == user_email:
            return id

files = glob.glob('./av/*/*.json')
posts = {}
for f in files:
    with open(f) as data_file:
        date = datetime.datetime.strptime(re.sub('.json', '',re.sub(r'.*(\d\d\d\d)\-(\d\d)\-(\d\d)', r'\1-\2-\3', f)), "%Y-%m-%d")
        data = json.load(data_file)
        for msg in data:
            if 'user' in msg:
                if msg['user'] in posts and date in posts[msg['user']]:
                    posts[msg['user']][date] += 1
                elif msg['user'] in posts:
                    posts[msg['user']][date] = 1
                else:
                    posts[msg['user']] = {}
                    posts[msg['user']][date] = 1

def total_posts_for_week_ending_on_given_day(posts, end_date):
    beginning_date = end_date - datetime.timedelta(days=6)
    return reduce(lambda total, date: posts[date] + total if date <= end_date and beginning_date <= date else total , posts, 0)

import re
def user_activity_levels(date):
    activity_levels = {}
    for user in posts:
      number_posts = total_posts_for_week_ending_on_given_day(posts[user], datetime.datetime.strptime(date,"%Y-%m-%d"))
      if number_posts > 0:
        activity_levels[users[user]['name']] = (number_posts, re.sub(r'.*\@','',users[user]['email']))
    return activity_levels

activity_levels_one_week_before_export = user_activity_levels('2017-07-08')
activity_levels_two_weeks_before_export = user_activity_levels('2017-07-01')
activity_levels_three_weeks_before_export = user_activity_levels('2017-06-24')

users_with_any_activity_in_last_three_weeks = list(set(activity_levels_one_week_before_export.keys()).union(activity_levels_two_weeks_before_export.keys()).union(activity_levels_three_weeks_before_export.keys()))

activities = {}
for user in users_with_any_activity_in_last_three_weeks:
    week1 = activity_levels_one_week_before_export.get(user,(0,''))[0]
    week2 = activity_levels_two_weeks_before_export.get(user,(0,''))[0]
    week3 = activity_levels_three_weeks_before_export.get(user,(0,''))[0]
    activities[user] = (week1, week2, week3)

import csv

ofile  = open('to_be_predicted.csv', "wb")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
writer.writerow(["user", "week3", "week2", "week1", "premium"])
for user in activities:
    week_1 = activities[user][0]
    week_2 = activities[user][1]
    week_3 = activities[user][2]
    values = [user, week_3, week_2, week_1 ]
    writer.writerow(values)
ofile.close()
