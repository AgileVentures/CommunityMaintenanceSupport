data = read.csv("data.csv")
nonzerodata = subset(data, week1 > 0 | week2 > 0 | week3 > 0)

library(caTools)
set.seed(1000)

library(caret)
numFolds = 5

library("ROCR")
libray(DMwR)
aucs <- c()
for(rep in 1:1000){
  nonzerodata$folds <- createFolds(factor(nonzerodata$premium), k=numFolds, list=FALSE)
  
  for(i in 1:numFolds){
    train = subset(nonzerodata, folds != i)
    test  = subset(nonzerodata, folds == i)
    
    #train$premium <- factor(ifelse(train$premium == 1,"rare","common")) 
    #test$premium <- factor(ifelse(test$premium == 1, "rare", "common"))
    #train <- SMOTE(premium ~ ., train, perc.over = 500,perc.under=150)
    
    pComp = prcomp(~ week1 + week2 + week3, train, scale = TRUE)
    train$comp1 = pComp$x[,1]
    test$comp1 = predict(pComp,newdata=test)[,1]
    
    model = glm(premium ~ comp1 ,data=train,family="binomial")
    
    probTest = predict(model, type="response", newdata=test)
    predTest <- prediction(probTest, test$premium)   
    perfTest <- performance(predTest, "auc")
    aucs[(rep-1)*numFolds + i] <- perfTest@y.values[[1]]
  }
  #print(aucs[((rep-1)*numFolds + 1) : ((rep-1)*numFolds + numFolds)])
}
sd(aucs) 
mean(aucs)