data = read.csv("data.csv")
nonzerodata = subset(data, week1 > 0 | week2 > 0 | week3 > 0)
pr = princomp(nonzerodata[,1:3], cor=TRUE, scale=TRUE)
nonzerodata$comp1 = pr$scores[,1]

library(caTools)
set.seed(1000)

library(caret)
numFolds = 5
nonzerodata$folds <- createFolds(factor(nonzerodata$premium), k=numFolds, list=FALSE)

library("ROCR")
aucs <- c()
for(rep in 1:1000){
  nonzerodata$folds <- createFolds(factor(nonzerodata$premium), k=numFolds, list=FALSE)
  
  for(i in 1:numFolds){
    train = subset(nonzerodata, folds != i)
    test  = subset(nonzerodata, folds == i)

    model = glm(premium ~ comp1 ,data=train,family="binomial")
    probTrain=predict(model,type=c("response"))    
    predTrain <- prediction(probTrain, train$premium)   
    perfTrain <- performance(predTrain, "auc")

    probTest = predict(model, type="response", newdata=test)
    predTest <- prediction(probTest, test$premium)   
    perfTest <- performance(predTest, "auc")
    aucs[(rep-1)*numFolds + i] <- perfTest@y.values[[1]]
  }
  #print(aucs[((rep-1)*numFolds + 1) : ((rep-1)*numFolds + numFolds)])
}
sd(aucs) #.1797646
mean(aucs) #.6628563