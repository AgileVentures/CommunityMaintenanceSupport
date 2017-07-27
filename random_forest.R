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

library(ROCR)

pComp = prcomp(~ week1 + week2 + week3, train, scale = TRUE)
train$comp1 = pComp$x[,1]
test$comp1 = predict(pComp,newdata=test)[,1]

library(randomForest)
#model = glm(premium ~ comp1 ,data=train,family="binomial")

rf = randomForest(premium ~ week1 + week2 + week3, train, ntree=500)

#probTest = predict(model, type="response", newdata=test)
#predTest <- prediction(probTest, test$premium)
#perfTest <- performance(predTest, "auc")
#perfTest@y.values[[1]]

probTest = predict(rf, type="prob", newdata=test)[,2]
predTest <- prediction(probTest, test$premium)
perfTest <- performance(predTest, "auc")
perfTest@y.values[[1]] # 0.7092623

to_be_predicted <- read.csv("to_be_predicted.csv")

premiums <- read.csv("./av/av_members.csv")
premiums <- subset(premiums, premiums$Special != "Cancelled")

to_be_predicted <- subset(to_be_predicted, !(user %in% premiums$Slack))

predictions <- predict(rf, type="class", newdata=to_be_predicted)
print("the users who may well signup are:")
to_be_predicted[predictions == "rare",]$user

print("the top 10 free members that might signup are: ")

probs <- predict(rf, type="prob", newdata=to_be_predicted)[,2]
ids = names(sort(probs, decreasing=TRUE))[0:10]
to_be_predicted[ids,]$user
