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
    unresolved_emails = {}
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
    with open('./av/stripe_customers.csv') as stripe_customers:
        reader = csv.DictReader(stripe_customers)
        for customer in reader:
            id = find_slack_id_by_email(users,customer['Email'])
            signup_date_time = datetime.datetime.strptime(re.sub(r'(\d\d\d\d)\-(\d\d)\-(\d\d).*', r'\1-\2-\3', customer['Created (UTC)']), '%Y-%m-%d')
            if id:
                premium_postings[id] = {"posts": posts[id], "start_date": signup_date_time}
            else:
                print "user not found: "+ customer['Email']
                unresolved_emails[customer['Email']] = signup_date_time
        for customer_paypal_email in paypal_payments:
            id = find_slack_id_by_email(users, customer_paypal_email)
            if id:
                if id in premium_postings:
                    print "user switched payment methods: " + customer_paypal_email + " so we're using earliest payment date"
                    paypal_start_date =  paypal_payments[customer_paypal_email]
                    stripe_start_date =  premium_postings[id]["start_date"]
                    earliest_start_date = sorted([paypal_start_date, stripe_start_date])[0]
                    premium_postings[id] = {"posts": premium_postings[id]["posts"], "start_date": earliest_start_date}
                else:
                    premium_postings[id] = {"posts": posts[id], "start_date": paypal_payments[customer_paypal_email]}
            else:
                print "user with following paypal email not found: " + customer_paypal_email
                unresolved_emails[customer_paypal_email] = paypal_payments[customer_paypal_email]
        print "attempting to resolve emails with aid of unresolved_emails.csv"
        with open('./av/unresolved_emails.csv') as ur_emails:
            reader = csv.DictReader(ur_emails)
            for unresolved_email in reader:
                resolved_email = filter(lambda h: h == unresolved_email['unresolved_email'],unresolved_emails)
                if len(resolved_email) > 0:
                    resolved_email = resolved_email.pop()
                    id = find_slack_id_by_slack_name(users,unresolved_email['slack_name'])
                    if id:
                        signup_date = unresolved_emails[resolved_email]
                        if id in premium_postings:
                            "user has used different emails for different payment methods.  using earliest payment date for: " + resolved_email
                            premium_postings[id] = {"posts": posts[id], 'start_date': sorted([signup_date,premium_postings[id]['start_date']])[0]}
                        else:
                            premium_postings[id] = {"posts": posts[id], 'start_date': signup_date}
                        print 'successfully resolved signup date for email: ' + resolved_email
                        unresolved_emails.pop(resolved_email)
        remaining_unresolved_emails = unresolved_emails.keys()
        if len(remaining_unresolved_emails) > 0:
            print "the following emails remain unresolved: "
            print remaining_unresolved_emails
        else:
            print "we have successfully resolved all emails"
        return premium_postings


def find_slack_id_by_slack_name(users, user_name):
    resolved_id = filter(lambda id: users[id]['name'] == user_name, users)
    if len(resolved_id) > 0:
        return resolved_id.pop()
    else:
        print "couldn't find user with user name as follows: " + user_name

def total_posts_for_week_ending_on_given_day(posts, end_date):
    beginning_date = end_date - datetime.timedelta(days=6)
    return reduce(lambda total, date: posts[date] + total if date <= end_date and beginning_date <= date else total , posts, 0)

def create_user_id_map_to_name_and_email_from_API_data(email_to_countries):
    users = {}
    with open('./av/users.json') as user_file:
        for user in json.load(user_file)["members"]:
            if 'email' in user['profile']:
                email = user['profile']['email']
                if email in email_to_countries:
                    country = email_to_countries[email]
            users[user['id']] = {"name": user['name'], "email": email, "country": country}
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

def create_email_to_country_from_csv():
    email_to_country = {}
    with open('./av/user_countries.csv') as users_countries:
        reader = csv.DictReader(users_countries)
        for user_country in reader:
            email_to_country[user_country['email']] = user_country['country']
    return email_to_country
