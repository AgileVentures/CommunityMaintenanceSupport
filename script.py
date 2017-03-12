import glob, re, json, csv, datetime

import matplotlib.pyplot as plt

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

# posts contains usernames as keys, to another map that has (date)day keys,
# with values being number of posts on that day

premium_postings = {}
with open('./av/stripe_customers.csv') as stripe_customers:
    reader = csv.DictReader(stripe_customers)
    for customer in reader:
        id = find_slack_id_by_email(customer['Email'])
        if id:
            premium_postings[id] = {"posts": posts[id], "start_date": datetime.datetime.strptime(re.sub(r'(\d\d\d\d)\-(\d\d)\-(\d\d).*', r'\1-\2-\3', customer['Created (UTC)']), '%Y-%m-%d')}
        else:
            print "user not found: "+ customer['Email']

# premium postings is the subset of the posts map where the user email
# matches a premium user email (and includes start date)

def total_posts_for_week_ending_on_given_day(posts, end_date):
    beginning_date = end_date - datetime.timedelta(days=6)
    return reduce(lambda total, date: posts[date] + total if date <= end_date and beginning_date <= date else total , posts, 0)

# one_week_before_premium_signup = {}
# two_weeks_before_premium_signup = {}
# three_weeks_before_premium_signup = {}
# for premium_user in premium_postings:
#     one_week_before_premium_signup[premium_user] = total_posts_for_week_ending_on_given_day(premium_postings[premium_user]["posts"], premium_postings[premium_user]["start_date"])
#     two_weeks_before_premium_signup[premium_user] = total_posts_for_week_ending_on_given_day(premium_postings[premium_user]['posts'],premium_postings[premium_user]["start_date"] - datetime.timedelta(days=7))
#     three_weeks_before_premium_signup[premium_user] = total_posts_for_week_ending_on_given_day(premium_postings[premium_user]['posts'],premium_postings[premium_user]["start_date"] - datetime.timedelta(days=14))

# plt.figure()
# plt.boxplot([one_week_before_premium_signup.values(), two_weeks_before_premium_signup.values(), three_weeks_before_premium_signup.values()],1)

# plt.show()

one_week_before_export = {}
export_time = datetime.datetime.strptime('2017-01-22',"%Y-%m-%d")
for user in posts: 
  number_posts = total_posts_for_week_ending_on_given_day(posts[user], export_time)
  if number_posts > 0:
    one_week_before_export[users[user]['name']] = number_posts

import pprint
import operator
pp = pprint.PrettyPrinter(indent=4)
output = sorted(one_week_before_export.items(), key=operator.itemgetter(1))

pp.pprint(output)



