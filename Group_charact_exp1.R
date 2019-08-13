library(readr)
library(data.table)
library(reshape2)
library(lme4)
library(readxl)
library("ggpubr")
library(segmented)
library(xlsx)
library(tidyverse)
library(ggplot2)

demo_ASD <- read_csv("Data/deelnemers_ASD.csv")
demo_TD <- read_csv("Data/CONTROLEdeelnemers.csv")
demo_ASD <- select(demo_ASD, SubjectId,leeftijd, Geslacht, VIQ, PIQ,SRS_TOTAAL,IU,CBCL,SP)
demo_ASD <- filter(demo_ASD,!is.na(SubjectId))
demo_ASD$SubjectId = as.factor(demo_ASD$SubjectId)

demo_ASD$Group <- 'ASD'
demo_ASD <- filter(demo_ASD,!grepl("002",SubjectId))
demo_TD <- select(demo_TD, SubjectId,leeftijd, Geslacht, VIQ, PIQ,SRS_TOTAAL,IU,CBCL,SP)
demo_TD <- filter(demo_TD,!grepl("316",SubjectId),!grepl("315",SubjectId),!grepl("322",SubjectId),!grepl("310",SubjectId),!grepl("321",SubjectId))
demo_TD$SubjectId = as.factor(demo_TD$SubjectId)
demo_TD$Group <- 'TD'
demo_TD$SP = as.integer(demo_TD$SP)
  

demo<-bind_rows(demo_ASD,demo_TD)
demo <- demo%>%
  mutate(FIQ=((PIQ + VIQ)/2))%>%
  rename(subjectId=SubjectId)
demo$subjectId = as.factor(demo$subjectId)
demo$Group = factor(demo$Group)

demo%>%
  group_by(Group)%>%
  summarise(N = n(),mean_age=mean(leeftijd), minimum_age=min(leeftijd), maximum_age = max(leeftijd), sd_age=sd(leeftijd), n_girls = sum(Geslacht))
mean(demo$leeftijd)
sd(demo$leeftijd)
min(demo$leeftijd)
max(demo$leeftijd)
ggplot(demo,aes(leeftijd)) +geom_histogram(binwidth = 1) + facet_grid(~Group)

demo%>%
  group_by(Group)%>%
  summarise(N = n(),mean_VIQ=mean(VIQ), minimum_VIQ=min(VIQ), maximum_VIQ = max(VIQ), sd_VIQ=sd(VIQ), n_girls = sum(Geslacht))
demo%>%
  group_by(Group)%>%
  summarise(N = n(),mean_PIQ=mean(PIQ), minimum_PIQ=min(PIQ), maximum_PIQ = max(PIQ), sd_PIQ=sd(PIQ), n_girls = sum(Geslacht))
demo%>%
  group_by(Group)%>%
  summarise(N = n(),mean_FIQ=mean(FIQ), minimum_FIQ=min(FIQ), maximum_FIQ = max(FIQ), sd_FIQ=sd(FIQ), n_girls = sum(Geslacht))

demo%>%
  group_by(Group)%>%
  summarise(N = n(),mean_SRS_TOTAAL=mean(SRS_TOTAAL,na.rm=TRUE), minimum_SRS_TOTAAL=min(SRS_TOTAAL,na.rm=TRUE), maximum_SRS_TOTAAL = max(SRS_TOTAAL,na.rm=TRUE), sd_SRS_TOTAAL=sd(SRS_TOTAAL,na.rm=TRUE), n_girls = sum(Geslacht))
demo%>%
  group_by(Group)%>%
  summarise(N = n(),mean_SP=mean(SP,na.rm=TRUE), minimum_SP=min(SP,na.rm=TRUE), maximum_SP = max(SP,na.rm=TRUE), sd_SP=sd(SP,na.rm=TRUE), n_girls = sum(Geslacht))
demo%>%
  group_by(Group)%>%
  summarise(N = n(),mean_CBCL=mean(CBCL,na.rm=TRUE), minimum_CBCL=min(CBCL,na.rm=TRUE), maximum_CBCL = max(CBCL,na.rm=TRUE), sd_CBCL=sd(CBCL,na.rm=TRUE), n_girls = sum(Geslacht))

t.test(demo$leeftijd ~ demo$Group)
t.test(demo$PIQ ~ demo$Group)
t.test(demo$VIQ ~ demo$Group)
t.test(demo$FIQ ~ demo$Group)
t.test(demo$CBCL ~ demo$Group)
t.test(demo$SRS_TOTAAL ~ demo$Group)
t.test(demo$SP ~ demo$Group)
res <- prop.test(x = c(8, 11), n = c(24, 24))
# Printing the results
res 

ggplot(demo,aes(Group,leeftijd, color=Group)) + geom_boxplot() + geom_point() + theme_classic() + xlab("Group") + ylab("Age") + ggtitle("Age per group") 
ggplot(demo,aes(Group,PIQ, color=Group)) + geom_boxplot() + geom_point() + theme_classic() + xlab("Group") + ylab("PIQ") + ggtitle("PIQ per group") 
ggplot(demo,aes(Group,VIQ, color=Group)) + geom_boxplot() + geom_point() + theme_classic() + xlab("Group") + ylab("VIQ") + ggtitle("VIQ per group") 
ggplot(demo,aes(Group,FIQ, color=Group)) + geom_boxplot() + geom_point() + theme_classic() + xlab("Group") + ylab("FIQ") + ggtitle("FIQ per group") 
ggplot(demo,aes(Group,SP, color=Group)) + geom_boxplot() + geom_point() + theme_classic() + xlab("Group") + ylab("SP") + ggtitle("SP per group") 

ggboxplot(demo, x = "Group", y = "leeftijd", color = "Group", legend = "right", ylab="Age", xlab = "Group" ) 
