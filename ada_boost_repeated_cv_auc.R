data = read.csv("data.csv")
nonzerodata = subset(data, week1 > 0 | week2 > 0 | week3 > 0)

library(caTools)
set.seed(1000)

library(caret)
numFolds = 5

library("ROCR")
aucs <- c()

library(DMwR)
library(gbm)

for(rep in 1:1000){
  nonzerodata$folds <- createFolds(factor(nonzerodata$premium), k=numFolds, list=FALSE)
  for(i in 1:numFolds){
    train = subset(nonzerodata, folds != i)
    test  = subset(nonzerodata, folds == i)
    
    train$premium <- factor(ifelse(train$premium == 1,"rare","common")) 
    test$premium <- factor(ifelse(test$premium == 1, "rare", "common"))
    
    set.seed(2000)
    
    train <- SMOTE(premium ~ ., train, perc.over = 500,perc.under=150)
    
    train$premium <- ifelse(train$premium == "rare", 1,0)
    test$premium <- ifelse(test$premium == "rare", 1,0)
    
    model = gbm(premium ~ week1 + week2 + week3, distribution="adaboost", data=train)
    
    probTest = predict(model,test, n.trees=100,type="response")
    predTest <- prediction(probTest, test$premium)
    perfTest <- performance(predTest, "auc")
    aucs[(rep-1)*numFolds + i] <- perfTest@y.values[[1]]
  }
}
sd(aucs) 
mean(aucs)