import glob, re, json, csv, datetime

def did_user_upgrade_in(premium_postings, user_id, date):
    if user_id in premium_postings.keys():
        upgrade_date = premium_postings[user_id]["start_date"]
        return 1 if upgrade_date < date and upgrade_date > (date - datetime.timedelta(days=7)) else 0
    else:
        return 0

def find_slack_id_by_email(users,user_email):
    for id, value in users.iteritems():
        if value['email'] == user_email:
            return id

def create_user_id_map_to_posts_and_upgrade_date_from_stripe_data(users,posts):
    with open('./av/stripe_customers.csv') as stripe_customers:
        premium_postings = {}
        reader = csv.DictReader(stripe_customers)
        for customer in reader:
            id = find_slack_id_by_email(users,customer['Email'])
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

def create_user_id_map_to_date_and_number_posts_from_archive_data(directory = '.'):
    files = glob.glob(directory + '/av/*/*.json')
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
