import glob, re, json, csv, datetime

def did_user_upgrade_in(user_id, date):
    if user_id in premium_postings.keys():
        upgrade_date = premium_postings[user_id]["start_date"]
        return 1 if upgrade_date < date and upgrade_date > (date - datetime.timedelta(days=7)) else 0
    else:
        return 0 

def find_slack_id_by_email(user_email):
    for id, value in users.iteritems():
        if value['email'] == user_email:
            return id

def create_user_id_map_to_posts_and_upgrade_date_from_stripe_data():
    with open('./av/stripe_customers.csv') as stripe_customers:
        premium_postings = {}
        reader = csv.DictReader(stripe_customers)
        for customer in reader:
            id = find_slack_id_by_email(customer['Email'])
            if id:
                premium_postings[id] = {"posts": posts[id], "start_date": datetime.datetime.strptime(re.sub(r'(\d\d\d\d)\-(\d\d)\-(\d\d).*', r'\1-\2-\3', customer['Created (UTC)']), '%Y-%m-%d')}
            else:
                print "user not found: "+ customer['Email']
        return premium_postings

def total_posts_for_week_ending_on_given_day(posts, end_date):
    beginning_date = end_date - datetime.timedelta(days=6)
    return reduce(lambda total, date: posts[date] + total if date <= end_date and beginning_date <= date else total , posts, 0)

def create_user_id_map_to_name_and_email_from_API_data():
    users = {}
    with open('./av/users.json') as user_file:
        for user in json.load(user_file)["members"]:
            if 'email' in user['profile']:
                email = user['profile']['email']
            users[user['id']] = {"name": user['name'], "email": email}
    return users

def create_user_id_map_to_date_and_number_posts_from_archive_data():
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
    return posts


users = create_user_id_map_to_name_and_email_from_API_data() # id: {'name': name, 'email': email}
posts = create_user_id_map_to_date_and_number_posts_from_archive_data() # id: { date: total_posts_on_that_day}
premium_postings = create_user_id_map_to_posts_and_upgrade_date_from_stripe_data() # id: {'posts': postss, 'created_at': upgrade date}

# X = array([[23,34,12,12.5],[21,34,12,19.5], ...])

# # loop through users
#   # loop through dates (week -3, week -2, week -1, week 0)
#     # generate data array; [week-2,week-1,week0,metric]
#     # lookup in premium_postings is user upgrade within week0?
#       # if it is, then Y data is 1, if not (or no upgrade) 0
 
# Y = array([0,0, ...., 1, ...])

start_date = datetime.datetime(2016, 5, 1, 0, 0, 0)
number_of_weeks = 52

X = []
Y = []

for user_id in users:
    for multiplier in range(1,53): 
        date = start_date + datetime.timedelta(days=7*multiplier)
        if user_id in posts.keys():
            week_minus_three = total_posts_for_week_ending_on_given_day(posts[user_id], date)
            week_minus_two = total_posts_for_week_ending_on_given_day(posts[user_id], date + datetime.timedelta(days=7))
            week_minus_one = total_posts_for_week_ending_on_given_day(posts[user_id], date + datetime.timedelta(days=14))
            # metric 
            X.append([week_minus_three, week_minus_two, week_minus_one])
            upgrade = did_user_upgrade_in(user_id, date + datetime.timedelta(days=21))
            Y.append(upgrade)

# print X
# print Y   

import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model, datasets

h = .02  # step size in the mesh

logreg = linear_model.LogisticRegression(C=1e5) 

# we create an instance of Neighbours Classifier and fit the data.
logreg.fit(X, Y)
