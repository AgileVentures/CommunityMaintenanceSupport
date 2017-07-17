import slack_posts as sp
import datetime

users = sp.create_user_id_map_to_name_and_email_from_API_data() # id: {'name': name, 'email': email}
posts = sp.create_user_id_map_to_date_and_number_posts_from_archive_data() # id: { date: total_posts_on_that_day}
premium_postings = sp.create_user_id_map_to_posts_and_upgrade_date_from_stripe_and_paypal_data(users,posts) # id: {'posts': postss, 'created_at': upgrade date}

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

for user_id, _ in sorted(users.items()):
    for multiplier in range(1,53):
        date = start_date + datetime.timedelta(days=7*multiplier)
        if user_id in posts.keys():
            week_minus_three = sp.total_posts_for_week_ending_on_given_day(posts[user_id], date)
            week_minus_two = sp.total_posts_for_week_ending_on_given_day(posts[user_id], date + datetime.timedelta(days=7))
            week_minus_one = sp.total_posts_for_week_ending_on_given_day(posts[user_id], date + datetime.timedelta(days=14))
            user_name = users[user_id]['name']
            # metric
            X.append([week_minus_three, week_minus_two, week_minus_one, user_name])
            upgrade = sp.did_user_upgrade_in(premium_postings, user_id, date + datetime.timedelta(days=21))
            Y.append(upgrade)

import csv

ofile  = open('data.csv', "wb")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
writer.writerow(["week3", "week2", "week1", "user_name", "premium"])
for idx, covariates in enumerate(X):
    covariates.append(Y[idx])
    writer.writerow(covariates)
ofile.close()

# import statsmodels.api as sm
#
# X2 = sm.add_constant(X)
# est = sm.Logit(Y, X2)
# est2 = est.fit()
# print(est2.summary())
# prediction_probabilities = est2.predict()
#
# L = .0003
# falsePositives = truePositives = falseNegatives = trueNegatives = 0
#
# for index, p in enumerate(prediction_probabilities):
#     result = Y[index]
#     #here we are predicting negative
#     if p < L:
#         #but the result is a positive
#         if (result == 1):
#             falseNegatives += 1
#         #and the result is a negative
#         else:
#             trueNegatives += 1
#     #here we are predicting a positive
#     else:
#         #but the result is a negative
#         if (result == 0):
#             falsePositives += 1
#         #and the result is a positive
#         else:
#             truePositives += 1
#
# print(falsePositives)
# print(truePositives)
# print(falseNegatives)
# print(trueNegatives)
#
# print 'recall is: {:10.4f}'.format(truePositives / (1.0 * (truePositives + falseNegatives)))
# print 'precision is: {:10.4f}'.format(truePositives / (1.0 * (truePositives + falsePositives)))
