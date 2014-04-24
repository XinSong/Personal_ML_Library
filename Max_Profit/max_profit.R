overdue.2013<-read.table('data_processed.new',header=TRUE)
overdue.2013[,'is_overdue']<-ifelse(overdue.2013[,'overdue_dur']>3,1,ifelse(overdue.2013[,'overdue_dur']>0 & overdue.2013[,'overdue_dur']<=3,-1,0))
overdue.2013<-overdue.2013[overdue.2013$is_overdue!=-1,]
overdue.2013$is_overdue<-as.factor(overdue.2013$is_overdue)

#转化为因子变量
overdue.2013[,'provid']<-factor(overdue.2013[,'provid'])
overdue.2013[,'cityid']<-factor(overdue.2013[,'cityid'])
overdue.2013[,'vuser']<-factor(overdue.2013[,'vuser'])
overdue.2013[,'corp']<-factor(overdue.2013[,'corp'])
overdue.2013[,'main_tradeid']<-factor(overdue.2013[,'main_tradeid'])
overdue.2013[,'frameworkuser']<-factor(overdue.2013[,'frameworkuser'])

#去掉renewal_times、renewal_amt、week_x_days、trade1-3、cityid、frameworkuser、overdue_amt7_7、vuser、vuser_score、authICP_score、overdue_dur
#去掉week_x_days之后，auc值下降为0.79
overdue.2013<-subset(overdue.2013,select=-c(seq(6,52),seq(123,125,by=1),127,128,135,139,156,157,160)) 
#去掉framework_user、vuser、overdue_amt7_7、vuser_score、authICP_score、renewal_times

train.2013<-overdue.2013[overdue.2013$paytime<20131101,]
test.2013<-overdue.2013[overdue.2013$paytime>=20131101,]
sequence.isotonic_regression <- sample(9000,4500)
test.isotonic_regression <- test.2013[sequence.isotonic_regression,]
test <- test.2013[-sequence.isotonic_regression,]
train.2013.normal<-train.2013[train.2013$is_overdue==0,]
train.2013.overdue<-train.2013[train.2013$is_overdue==1,]

#所有客户的总逾期金额占总授信金额的76.5%，逾期金额占授信金额比例超过80%的客户数为50.8%，
#这说明大部分的逾期客户的逾期金额都很接近授信金额

#去掉rid、paytime和unpaidfundsnapshot
train.crf<-train.2013[,-c(1,2,13)]

crf.control<-cforest_control(mtry=sqrt(ncol(train.crf)))
credit.crf<-cforest(is_overdue~.,data=train.crf)
pred.isotonic_regression <- predict(credit.crf,newdata=test.isotonic_regression,type='prob')
pred.isotonic_regression.matrix<-do.call(rbind,pred.isotonic_regression)
pred.isotonic_regression.matrix<-as.data.frame(pred.isotonic_regression.matrix)
prediction.isotonic_regression<-prediction(pred.isotonic_regression.matrix[,2],test.isotonic_regression[,'is_overdue'])
auc.isotonic_regression<-performance(prediction.isotonic_regression,'auc')
auc.isotonic_regression
score.isotonic_regression <- cbind(pred.isotonic_regression.matrix[,2],as.numeric(as.character(test.isotonic_regression[,'is_overdue'])),test.isotonic_regression$unpaidfundsnapshot,test.isotonic_regression$fund)
score.isotonic_regression <- score.isotonic_regression[order(score.isotonic_regression[,1]),]
#输出文件格式：逾期模型打分，真实分类（0或1），真实逾期金额，真实授信金额
#注意：保序回归其实并不需要uid
write.table(score.isotonic_regression,file='score.txt',quote=FALSE,sep="\t",row.names=FALSE,col.names=FALSE)
#上述文件采用isotonic_regression_with_unpaid_ratio.py进行处理之后，

#利用随机森林，对最终测试集进行预测
pred.test <- predict(credit.crf,newdata=test,type='prob')
pred.test.matrix<-do.call(rbind,pred.test)
pred.test.matrix<-as.data.frame(pred.test.matrix)
prediction.test<-prediction(pred.test.matrix[,2],test[,'is_overdue'])
auc.test<-performance(prediction.test,'auc')
auc.test
score.test <- cbind(test[,'rid'],pred.test.matrix[,2],as.numeric(as.character(test[,'is_overdue'])))
score.test <- score.test[order(score.test[,2]),]
#输出文件格式：uid，逾期模型打分，真实分类（0或1）
write.table(score.test,file='score_test.txt',quote=FALSE,sep="\t",row.names=FALSE,col.names=FALSE)


#逾期客户中逾期超过30天的比例：0.050667
#逾期超过30天的客户逾期金额占授信金额的比例：0.5958528

beta<-0.5958528
#收费函数：有授信金额，决定收取的手续费
fee <- function(fund){
  if(fund<=2000)
    10
  else if(fund>2000 & fund<=10000)
    20
  else if(fund>10000 & fund<=20000)
    30
  else if(fund>20000)
    50
}

fee.all<- as.numeric(lapply(test[,'fund'],fee))
result<-cbind(test[,'rid'],test[,'fund'],fee.all)
result<-as.data.frame(result)

#运行rid_prob.sh,采用保序回归得到的结果，最终生成校正后的概率值和
#各区间的逾期金额占比
rid_prob <- read.table('rid_prob',header=FALSE)
colnames(rid_prob)<-c('rid','prob','unpaid_ratio')
colnames(result)<-c('rid','fund','fee')
result<-join(result,rid_prob,by='rid')
result$score <- pred.test.matrix[,2]
result$expected_return<-result[,'fee'] + -1 * result[,'fund'] * result[,'prob'] * result[,'unpaid_ratio']
result$unpaidfundsnapshot<-test$unpaidfundsnapshot
overdue_dur <- read.table('overdue_dur_day',header=TRUE)
overdue_dur <- overdue_dur[,c(1,3)]
colnames(overdue_dur) <- c('rid','overdue_dur')
result<-join(result,overdue_dur,by='rid')

result.orderByRate<-result[order(result[,'score']),]
result.orderByExpRet<-result[order(-result[,'expected_return']),]
x<-numeric()
y<-numeric()
sum<-0
for(i in seq(1,nrow(result.orderByExpRet))){
  x<-c(x,i)
  if(result.orderByExpRet[i,'overdue_dur']<=15)
    multiplier = 0
  else if(result.orderByExpRet[i,'overdue_dur']<=30)
    multiplier = 0
  else if(result.orderByExpRet[i,'overdue_dur']<=45)
    multiplier = 0
  else if(result.orderByExpRet[i,'overdue_dur']<=60)
    multiplier = 0.25
  else
    multiplier = 1
  sum <- sum + result.orderByExpRet[i,'fee'] - result.orderByExpRet[i,'unpaidfundsnapshot'] * multiplier 
  y<-c(y,sum)
}
plot(x,y,type='l',col='red',xlab='Top N Users',ylab='Profit')

x<-numeric()
y<-numeric()
sum<-0
for(i in seq(1,nrow(result.orderByRate))){
  x<-c(x,i)
  if(result.orderByRate[i,'overdue_dur']<=15)
    multiplier = 0
  else if(result.orderByRate[i,'overdue_dur']<=30)
    multiplier = 0
  else if(result.orderByRate[i,'overdue_dur']<=45)
    multiplier = 0
  else if(result.orderByRate[i,'overdue_dur']<=60)
    multiplier = 0.25
  else
    multiplier = 1
  sum <- sum + result.orderByRate[i,'fee'] - result.orderByRate[i,'unpaidfundsnapshot'] * multiplier
  y<-c(y,sum)
}
lines(x,y,col='green')
  

























