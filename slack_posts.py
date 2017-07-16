import glob, re, json, csv, datetime,time,pytz

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

def create_user_id_map_to_posts_and_upgrade_date_from_stripe_and_paypal_data(users,posts):
    paypal_payments = {}
    premium_postings = {}
    with open('./av/PayPalPayments.csv') as payments:
        reader = csv.DictReader(payments)
        for payment in reader:
            if payment['Balance Impact'] == "Credit" and payment['Type'] == "Subscription Payment":
                email = payment['From Email Address']
                date_time_string = payment['Date'] + " " + payment['Time']
                if payment['Gross'] == '10.00':
                    trial_period_adjustment = datetime.timedelta(days=7)
                else:
                    trial_period_adjustment = datetime.timedelta(days=0)
                bst = pytz.timezone('Europe/London')
                date_and_time = bst.localize(datetime.datetime(*time.strptime(date_time_string, "%d/%m/%Y %H:%M:%S")[0:6]) - trial_period_adjustment).astimezone(pytz.utc).replace(tzinfo=None)
                if email not in paypal_payments:
                    paypal_payments[email] = [date_and_time]
                else:
                    paypal_payments[email].append(date_and_time)
        for email in paypal_payments:
            paypal_payments[email] = sorted(paypal_payments[email])[0]
    print paypal_payments
    with open('./av/stripe_customers.csv') as stripe_customers:
        reader = csv.DictReader(stripe_customers)
        for customer in reader:
            id = find_slack_id_by_email(users,customer['Email'])
            if id:
                premium_postings[id] = {"posts": posts[id], "start_date": datetime.datetime.strptime(re.sub(r'(\d\d\d\d)\-(\d\d)\-(\d\d).*', r'\1-\2-\3', customer['Created (UTC)']), '%Y-%m-%d')}
            else:
                print "user not found: "+ customer['Email']
        for customer_paypal_email in paypal_payments:
            id = find_slack_id_by_email(users, customer_paypal_email)
            if id:
                print "found user with email: " + customer_paypal_email
                if id in premium_postings:
                    print "user switched payment methods: " + customer_paypal_email + "so we're using earliest payment date"
                    paypal_start_date =  paypal_payments[customer_paypal_email]
                    stripe_start_date =  premium_postings[id]["start_date"]
                    earliest_start_date = sorted([paypal_start_date, stripe_start_date])[0]
                    premium_postings[id] = {"posts": premium_postings[id]["posts"], "start_date": earliest_start_date}
                else:
                    premium_postings[id] = {"posts": posts[id], "start_date": paypal_payments[customer_paypal_email]}
            else:
                print "user with following paypal email not found: " + customer_paypal_email
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
