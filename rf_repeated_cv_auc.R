data = read.csv("data.csv")
nonzerodata = subset(data, week1 > 0 | week2 > 0 | week3 > 0)

library(caTools)
set.seed(1000)

library(caret)
numFolds = 5

library("ROCR")
libray(DMwR)
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
    
    set.seed(2000)
    
    train <- SMOTE(premium ~ ., train, perc.over = 500,perc.under=150)
    
    model = randomForest(premium ~ week1 + week2 + week3, train, ntree=500)
    
    probTest = predict(model, type="prob", newdata=test)[,2]
    predTest <- prediction(probTest, test$premium)
    perfTest <- performance(predTest, "auc")
    aucs[(rep-1)*numFolds + i] <- perfTest@y.values[[1]]
  }
}
sd(aucs) 
mean(aucs)