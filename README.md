# Community Maintenance Support

Some analytics to investigate community activity within the AgileVentures Slack community (and associated systems)

##How to run tests  
python run_tests.py from the command line at the root of the project should suffice

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
