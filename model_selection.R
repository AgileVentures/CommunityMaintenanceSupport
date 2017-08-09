data = read.csv("data.csv",na.strings=c("","NA"))
nonzerodata = subset(data, week1 > 0 | week2 > 0 | week3 > 0)
nonzerodata = subset(nonzerodata, !is.na(country))
country_ppp = read.csv("country_ppp.csv")
nonzerodata = merge(x=nonzerodata,y=country_ppp, by.x="country", by.y="Country.Name")
nonzerodata = nonzerodata[, c('week3', 'week2', 'week1', 'premium', 'X2014')]
nonzerodata = subset(nonzerodata, !is.na(X2014))

set.seed(2000)
spl = sample.split(nonzerodata$premium, .6)
train = subset(nonzerodata, spl == TRUE)

rest = subset(nonzerodata, spl == FALSE)
spl2 = sample.split(rest$premium, .5)
validate = subset(rest, spl2 == TRUE)
test = subset(rest, spl2 == FALSE)

pComp = prcomp(~ week1 + week2 + week3, train, scale = TRUE)
train$comp1 = pComp$x[,1]
validate$comp1 = predict(pComp,newdata=validate)[,1]
test$comp1 = predict(pComp,newdata=test)[,1]

model1 = glm(premium ~ comp1,data=train,family="binomial")

probValidate = predict(model1, type="response", newdata=validate)
predValidate <- prediction(probValidate, validate$premium)   
perfModel1Validate <- performance(predValidate, "auc")

model2 = glm(premium ~ comp1 + X2014,data=train,family="binomial")

probValidate = predict(model2, type="response", newdata=validate)
predValidate <- prediction(probValidate, validate$premium)   
perfModel2Validate <- performance(predValidate, "auc")

library(caTools)
library(DMwR)

trainModel3 <- train
validateModel3 <- validate
testModel3 <- test
trainModel3$premium <- factor(ifelse(trainModel3$premium == 1,"rare","common"))
validateModel3$premium <- factor(ifelse(validateModel3$premium == 1, "rare", "common"))
testModel3$premium <- factor(ifelse(testModel3$premium == 1, "rare", "common"))

set.seed(2000)
trainModel3 <- SMOTE(premium ~ ., trainModel3, perc.over = 300,perc.under=500)

library(ROCR)
library(randomForest)

model3 = randomForest(premium ~ week1 + week2 + week3 + X2014, trainModel3, ntree=500)

probValidate = predict(model3, type="prob", newdata=validateModel3)[,2]
predValidate <- prediction(probValidate, validateModel3$premium)
perfModel3Validate <- performance(predValidate, "auc")

trainModel4 <- train[,c('week1', 'week2', 'week3', 'premium')]
validateModel4 <- validate[,c('week1', 'week2', 'week3', 'premium')]
testModel4 <- test[,c('week1', 'week2', 'week3', 'premium')]
trainModel4$premium <- factor(ifelse(trainModel4$premium == 1,"rare","common"))
validateModel4$premium <- factor(ifelse(validateModel4$premium == 1, "rare", "common"))
testModel4$premium <- factor(ifelse(testModel4$premium == 1, "rare", "common"))

set.seed(2000)
trainModel4 <- SMOTE(premium ~ ., trainModel4, perc.over = 300,perc.under=500)

library(ROCR)
library(randomForest)

model4 = randomForest(premium ~ week1 + week2 + week3, trainModel3, ntree=500)

probValidate = predict(model4, type="prob", newdata=validateModel4)[,2]
predValidate <- prediction(probValidate, validateModel4$premium)
perfModel4Validate <- performance(predValidate, "auc")

#since model2 wins on validation we now perform testing on model1
probTest = predict(model2, type="response", newdata=test)
predTest <- prediction(probTest, test$premium)   
perfModel2Test <- performance(predTest, "auc")
perfModel2Test@y.values