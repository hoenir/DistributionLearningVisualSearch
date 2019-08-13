# I don't think you need all these libraries but I'm not sure which are essential
library(apastats)
library(data.table)
library(ggplot2)
library(lsmeans)
library(tables)
library(mgcv) 
library(circular)
library(dplyr) 
library(CircStats)
library(scales)
library(stringr)
library(bbmle)
library(splines)
library(zeallot)
# my_augment function
my_augment <- function(model,newdf,se=T,...) {
  newdf<- cbind(newdf, predict(model, newdata=newdf, se =se,...))
  setDT(newdf)
  setnames(newdf,'fit','.fitted')
  newdf
}

# computes weighted circular SD
weighted_circ_sd<-function(x, w){
  sum_w<-sum(w)
  
  r <- sqrt((sum(w*sin(x))/sum_w)^2+(sum(w*cos(x))/sum_w)^2)
  sqrt(-2*log(r))
}

# this is the main function
# your data should have "subjectId" variable if you want to do the fitting by subjectId
# by_vars are the variables that define groups
# between_vars do the same but if they are set, by_vars are treated as within-subject variables so that when the curve minimum is estimated for the purpose of fitting, it's calculated across different levels of by_vars
# cur_dv is the dependent variable
# get curves allows to return the fitted curves
prep_for_circ<-function(data, circ_var,circ_borders=c(-90,90), circ_part = 1/6){
  circ_range <- max(circ_borders)-min(circ_borders)
  
  data1<-copy(data[get(circ_var)<(circ_borders[1]+circ_range*circ_part),])
  data1[,(circ_var):=get(circ_var)+ circ_range]
  
  data2<-copy(data[get(circ_var)>(circ_borders[2]-circ_range*circ_part),])
  data2[,(circ_var):=get(circ_var)- circ_range]
  print(c(data1[,.N],data2[,.N], data[,.N]))
  rbind(data,data1,data2)
}


get_mu_sigma_raw<-function(data, by_vars=c('group'), by_part = T, cur_iv = 'ctpd', between_vars = NULL, cur_dv = 'log_rt', get_curves = F){
  if (by_part){
    full_by_vars<-c(by_vars, 'subjectId')
  } else {
    full_by_vars<-by_vars
  }
  
  cur_data<-copy(data)
  
  setnames(cur_data, c(cur_dv), c('dv'))
  setnames(cur_data, c(cur_iv), c('iv'))
  curves_dt<-prep_for_circ(cur_data, 'iv', circ_part =  1/6)[,my_augment(loess(dv~iv,data=.SD, normalize=F, span = 0.6), data.frame(expand.grid(iv=-90:90))), keyby=full_by_vars]
  curves_dt<-curves_dt[!is.na(.fitted)]
  if (!is.null(between_vars)){
    curves_dt[,min_fitted:=min(.fitted), by=c(between_vars, 'subjectId')]
  } else {
    curves_dt[,min_fitted:=min(.fitted), by=full_by_vars]
  }
  
  curves_dt[!is.na(.fitted), max_point:=.fitted==max(.fitted, na.rm = T), by=full_by_vars]
  curves_dt[,scaling:=sum(.fitted-min_fitted), by = full_by_vars]
  curves_dt[,fitted_norm:=(.fitted-min_fitted)/scaling]
  mu_sigma_dt <- curves_dt[!is.na(.fitted),
                           .(mu=unclass(weighted.mean.circular(circular(iv/90*pi),
                                                               fitted_norm))/pi*90, 
                             sigma=weighted_circ_sd(iv/90*pi, fitted_norm)/pi*90,
                             max = iv[max_point==T],
                             a = min_fitted[1], 
                             b = scaling[1]),
                           by=full_by_vars]
  #mu_sigma_dt[,bias:=sign(ori_at_target_pos)*angle_dist(ori_at_target_pos,mu)]
  #print(mu_sigma_dt)
  if (!get_curves)
    mu_sigma_dt
  else
    list(mu_sigma_dt, curves_dt)
}


# data_for_gam is the data frame that holds only the trials that should be used for curve-fitting (i.e., the first test trials with errors excluded)
data_for_gam<- df_filter%>%
  filter(correct==1) %>% #only RTs for correct responses
  filter(dsd==5) %>% #For test streaks with Gaussian distr
  filter(trialN == 0)

data_for_gam_dt<-data_for_gam
setDT(data_for_gam_dt)
c(res_raw, curves_dt) %<-% get_mu_sigma_raw(data_for_gam_dt, get_curves = T)

plot.pointrange(res_raw,aes(x = group, y=mu))
plot.pointrange(res_raw,aes(x = group, y=sigma))
ggplot(curves_dt,aes(x=iv, y=fitted_norm, color=group))+ stat_summary(fun.y=base::mean, geom="line", size =3)+ 
  stat_summary(fun.data=mean_cl_normal, geom='smooth', se=T)
ggplot(curves_dt,aes(x=iv, y=.fitted, color=group))+ stat_summary(fun.y=base::mean, geom="line", size =3)+ 
  stat_summary(fun.data=mean_cl_normal, geom='smooth', se=T)