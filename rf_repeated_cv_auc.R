data = read.csv("data.csv",na.strings=c("","NA"))
nonzerodata = subset(data, week1 > 0 | week2 > 0 | week3 > 0)
nonzerodata = subset(nonzerodata, !is.na(country))
country_ppp = read.csv("country_ppp.csv")
nonzerodata = merge(x=nonzerodata,y=country_ppp, by.x="country", by.y="Country.Name")
nonzerodata = nonzerodata[, c('week3', 'week2', 'week1', 'premium', 'X2014')]
nonzerodata = subset(nonzerodata, !is.na(X2014))

library(caTools)
set.seed(1000)

library(caret)
numFolds = 5

library("ROCR")
aucs <- c()

library(DMwR)
library(randomForest)

for(rep in 1:1000){
  nonzerodata$folds <- createFolds(factor(nonzerodata$premium), k=numFolds, list=FALSE)
  for(i in 1:numFolds){
    train = subset(nonzerodata, folds != i)
    test  = subset(nonzerodata, folds == i)
    
    train$premium <- factor(ifelse(train$premium == 1,"rare","common")) 
    test$premium <- factor(ifelse(test$premium == 1, "rare", "common"))
    
    preProcValues <- preProcess(train[,c("week1", "week2", "week3", "X2014")], method = c("center", "scale"))
    
    train[,c("week1", "week2", "week3", "X2014")] <- predict(preProcValues, train[,c("week1", "week2", "week3", "X2014")])
    test[,c("week1", "week2", "week3", "X2014")] <- predict(preProcValues, test[,c("week1", "week2", "week3", "X2014")])
    
    set.seed(2000)
    
    train <- SMOTE(premium ~ ., train, perc.over = 500,perc.under=150)
    
    model = randomForest(premium ~ week1 + week2 + week3 + X2014, train, ntree=500)
    
    probTest = predict(model, type="prob", newdata=test)[,2]
    predTest <- prediction(probTest, test$premium)
    perfTest <- performance(predTest, "auc")
    aucs[(rep-1)*numFolds + i] <- perfTest@y.values[[1]]
  }
}
sd(aucs) 
mean(aucs)