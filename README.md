# Community Maintenance Support

Some analytics to investigate community activity within the AgileVentures Slack community (and associated systems)

## How to run tests  
python run_tests.py from the command line at the root of the project should suffice

# How to train and predict using basic RandomForest model
You first need the slack archive unzipped into av subfolder.  Inside that av subfolder, you also need to place a users.json file FROM the users.list api.  You also need a stripe_customers.csv with stripe signup data.

Then run python data_dump.py to export the historic user signup and user activity data to data.csv, which should be git ignored.

Also, run, python export.py to export the current week's data to to_be_predicted.csv.  The script as currently constituted will export data for the week ending on July 8th 2017 and the preceding 3 weeks of activity.  To change this to accomodate future archive dumps and dates, change the dates as appropriate in export.py

Now with both data.csv and to_be_predicted.csv in the main folder, open up R or R studio.  Set the current working directory to the main folder for CommunityMaintenanceSupport and run the
code contained in random_forest.R.  You should get some output predicting those likely to signup.

## Objective

How to identify community members who are contributing more and provide them with additional support.

```
As an AgileVentures admin
So that I can ensure the AV revenue stream
I would like to know which members are likely to be downgrading in order to offer them additional help and support
```

```
As an AgileVentures admin
So that I can ensure the AV revenue stream
I would like to know which members to approach to suggest premium upgrades to
```

```
As an AgileVentures admin
So that I can ensure we have a healthy community with lots of inspiring projects with great contributors
I would like to know which members to offer additional help and support to
```

## Completed so Far

* Analysis of Slack activity in the three weeks leading up to Premium signup -> saw a possible trend of increasing activituy
* Ranking of Slack users by number of posts in a given week, and associated email domains

## ToDo

* [x] Weighted ranking over multiple weeks (looking for increasing activity)
* [ ] Normalise metric over activity levels to see growth at all levels
* [ ] Use weighted ranking on previous successes, to see if they show up
* [ ] Logistic regression (identify predictors)
* [ ] Automated contacting? (send "how are you doing" to anyone in the top ranked users, who has not had a DM with a mentor that week)
* [ ] refactor code to short methods, more self documenting?
