import slack_posts as sp
import datetime

users = sp.create_user_id_map_to_name_and_email_from_API_data() # id: {'name': name, 'email': email}
posts = sp.create_user_id_map_to_date_and_number_posts_from_archive_data() # id: { date: total_posts_on_that_day}
premium_postings = sp.create_user_id_map_to_posts_and_upgrade_date_from_stripe_and_paypal_data(users,posts) # id: {'posts': postss, 'created_at': upgrade date}


start_date = datetime.datetime(2016, 5, 1, 0, 0, 0)
number_of_weeks = 52

X = []
Y = []

for user_id, _ in sorted(users.items()):
    for multiplier in range(1,53):
        date = start_date + datetime.timedelta(days=7*multiplier)
        if user_id in posts.keys():
            week_minus_three = sp.total_posts_for_week_ending_on_given_day(posts[user_id], date)
            week_minus_two = sp.total_posts_for_week_ending_on_given_day(posts[user_id], date + datetime.timedelta(days=7))
            week_minus_one = sp.total_posts_for_week_ending_on_given_day(posts[user_id], date + datetime.timedelta(days=14))
            user_name = users[user_id]['name']
            # metric
            upgrade = sp.did_user_upgrade_in(premium_postings, user_id, date + datetime.timedelta(days=21))
            if upgrade == 1:
                start_of_week = (date+datetime.timedelta(days=14)).strftime("%Y-%m-%d")
                end_of_week = (date+datetime.timedelta(days=21)).strftime("%Y-%m-%d")
                upgrade_week = start_of_week+" - " + end_of_week
            else:
                upgrade_week = ""
            X.append([week_minus_three, week_minus_two, week_minus_one, upgrade_week, user_name])
            Y.append(upgrade)

import csv

ofile  = open('data.csv', "w")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
writer.writerow(["week3", "week2", "week1", "user_name", "signup_week", "premium"])
for idx, covariates in enumerate(X):
    covariates.append(Y[idx])
    writer.writerow(covariates)
ofile.close()
