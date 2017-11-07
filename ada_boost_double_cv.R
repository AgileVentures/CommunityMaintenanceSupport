data = read.csv("data.csv")
nonzerodata = subset(data, week1 > 0 | week2 > 0 | week3 > 0)
nonzerodata$premium <- factor(ifelse(nonzerodata$premium == 1,"rare","common")) 


library(caTools)

adaboost_with_smote <- list(type = "Classification",
              library = c("DMwR","gbm"),
              loop = function(grid) {            
                loop <- grid[which.max(grid$ntrees),,drop = FALSE]
                submodels <- grid[-which.max(grid$ntrees),,drop = FALSE]
                submodels <- list(submodels)  
                list(loop = loop, submodels = submodels)
              }) 

prm <- data.frame(parameter = c("overratio", "ntrees", "minobsinnode"),
                  class = rep("numeric", 3),
                  label = c("PercOverRatio","numberOfTrees","minObsPerNode"))
adaboost_with_smote$parameters <- prm

adbSmoteGrid <- function(x, y, len = NULL, search = "grid") {
  library(DMwR)
  library(gbm3)
  
  if(is.null(len)){
    len = 5000
  }
 
  if(search == "grid") {
    out <- expand.grid(overratio = 150*seq(from=1,to=5, by=(5-1)/(len - 1)), ntrees=floor(seq(from=50,to=1000,by=(1000-50)/(100-1))), minobsinnode=seq(from=10,to=235,by=25))
  } 
  out
}

adaboost_with_smote$grid <- adbSmoteGrid

adbSmoteFit <- function(x, y, wts, param, lev, last, weights, classProbs, ...) { 
  x <- as.data.frame(x)
  x$premium <- y 

  set.seed(2000)
  upsampled_data <- SMOTE(premium ~ ., x, perc.over = param$overratio,perc.under=150)
  
  upsampled_data$premium <- ifelse(upsampled_data$premium == "rare", 1,0)
  gc()
  gbm(premium ~ ., distribution="adaboost", data=upsampled_data, n.trees=param$ntrees, n.minobsinnode = param$minobsinnode)
}

adaboost_with_smote$fit <- adbSmoteFit

adbSmotePredict<- function(modelFit, newdata, preProc = NULL, submodels = NULL){
  treecount = length(modelFit$trees)
  out <- as.factor(ifelse(predict(modelFit,as.data.frame(newdata), n.trees=treecount)==1, "rare", "common"))
  if(!is.null(submodels)) {
    ## Save _all_ the predictions in a list
    tmp <- out
    out <- vector(mode = "list", length = nrow(submodels) + 1)
    out[[1]] <- tmp
    for(j in seq(along = submodels$ntrees)) {
      out[[j+1]] <- as.factor(ifelse(predict(modelFit, as.data.frame(newdata), n.trees = submodels$ntrees[j])==1,"rare","common"))
    }
  }
  gc()
  out
}
adaboost_with_smote$predict <- adbSmotePredict

adbSmoteProb <- function(modelFit, newdata, preProc = NULL, submodels = NULL){
  treecount = length(modelFit$trees)
  values <- predict(modelFit, as.data.frame(newdata), type="response", n.trees = treecount) 
  out <- data.frame(rare=values, common = 1-values )
  if(!is.null(submodels)) {
    ## Save _all_ the predictions in a list
    tmp <- out
    out <- vector(mode = "list", length = nrow(submodels) + 1)
    out[[1]] <- tmp
    for(j in seq(along = submodels$ntrees)) {
      prob_rare = predict(modelFit, as.data.frame(newdata), type="response", n.trees = submodels$ntrees[j])
      out[[j+1]] <- data.frame(rare=prob_rare, common = 1-prob_rare)
    }
  }
  gc()
  out
}  
adaboost_with_smote$prob <- adbSmoteProb

adaboost_with_smote$levels <- function(x){
  as.factor(c("rare", "common"))
}

set.seed(998)

numFolds <- 5
nonzerodata$folds <- createFolds(factor(nonzerodata$premium), k=numFolds, list=FALSE)
library(ROCR)
aucs <- c()
#library(doParallel)
#cl <- makeCluster(4)
#registerDoParallel(cl)
for(i in 1:numFolds) {
  print("starting number: ")
  print(i)
  library(caret)
  library(ROCR)
  train = subset(nonzerodata, folds != i)
  mean_train_week1 <- mean(train$week1)
  mean_train_week2 <- mean(train$week2)
  mean_train_week3 <- mean(train$week3)
  sd_train_week1 <- sd(train$week1)
  sd_train_week2 <- sd(train$week2)
  sd_train_week3 <- sd(train$week3)
  
  train$week1 <- (train$week1-mean_train_week1)/sd_train_week1
  train$week2 <- (train$week2-mean_train_week2)/sd_train_week2
  train$week3 <- (train$week3-mean_train_week3)/sd_train_week3
  
  
  test  = subset(nonzerodata, folds == i)

  test$week1 <- (test$week1-mean_train_week1)/sd_train_week1
  test$week2 <- (test$week2-mean_train_week2)/sd_train_week2
  test$week3 <- (test$week3-mean_train_week3)/sd_train_week3
  
  
  fitControl <- trainControl(method = "repeatedcv",
                             ## 10-fold CV...
                             number = 10,
                             ## repeated ten times
                             repeats = 10,
                             classProbs=TRUE,
                             summaryFunction= twoClassSummary)
  adbSmoted <- train(premium ~ week1+week2+week3, data = train, 
                     method = adaboost_with_smote, 
                     metric="ROC",
                     tuneLength = 100,
                     trControl = fitControl)
  
  model <- adbSmoted$finalModel
  treecount = length(model$trees)
  probTest = predict(model,test, n.trees=treecount,type="response")
  predTest <- prediction(probTest, test$premium)
  perfTest <- performance(predTest, "auc")
  aucs[i] <- perfTest@y.values[[1]]
  print("done number: ")
  print(i)
}
mean(aucs)
stopCluster(cl)



