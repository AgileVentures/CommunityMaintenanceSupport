data = read.csv("data.csv")
nonzerodata = subset(data, week1 > 0 | week2 > 0 | week3 > 0)
library(caTools)
library(DMwR)
set.seed(2000)
spl = sample.split(nonzerodata$premium,SplitRatio = .75)
train = nonzerodata[spl,]
test = nonzerodata[!spl,]

train$premium <- factor(ifelse(train$premium == 1,"rare","common"))
test$premium <- factor(ifelse(test$premium == 1, "rare", "common"))

train <- SMOTE(premium ~ ., train, perc.over = 300,perc.under=500)
table(train$premium)

train$premium <- ifelse(train$premium == "rare", 1,0)
test$premium <- ifelse(test$premium == "rare", 1,0)


library(ROCR)
library(gbm)

ab = gbm(premium ~ week1 + week2 + week3, distribution="adaboost", data=train)

probTest = predict(ab,test, n.trees=100,type="response")
predTest <- prediction(probTest, test$premium)
perfTest <- performance(predTest, "auc")
perfTest@y.values[[1]] # 0.7092623

to_be_predicted <- read.csv("to_be_predicted.csv")

premiums <- read.csv("./av/av_members.csv")
premiums <- subset(premiums, premiums$Special != "Cancelled")

to_be_predicted <- subset(to_be_predicted, !(user %in% premiums$Slack))

print("the top 10 free members that might signup are: ")

to_be_predicted$probs <- predict(ab, type="response", n.trees=100,newdata=to_be_predicted)
to_be_predicted <- to_be_predicted[order(-to_be_predicted$probs),]
ids = names(sort(probs, decreasing=TRUE))[0:10]

predicted <- to_be_predicted[0:10,]
predicted$user
predicted$email
