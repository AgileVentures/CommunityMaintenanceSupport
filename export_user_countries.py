from pgdb import connect

con = connect(database='cms_user', host='localhost:5432', user='postgres')
cursor = con.cursor()

results = cursor.execute("SELECT email, country_name from users").fetchall()

import csv

ofile  = open('av/user_countries.csv', "wb")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
writer.writerow(["email", "country"])

for result in results:
    writer.writerow([result.email, result.country_name])
ofile.close()
