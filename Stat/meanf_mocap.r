###################################################### tableau de donnees #######################################
# mean mocap : on garde la condition
# pas de plot, seulement les valeurs

### importer tableau 
setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("../MoCapAnalysis/brutMoCap.csv",sep=",",header=TRUE)

### type variable

tab$jour <- as.factor(as.character(tab$jour))
tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))
tab$condition[tab$condition=="2"] <- "pieds"
tab$condition[tab$condition=="3"] <- "mains"
#tab$condition <- factor(tab$condition,levels = c("pédalage pieds", "pédalage mains"))
tab$baseline[tab$histoire=="-1"] <- "baseline"
tab$baseline[tab$histoire=="3" | tab$histoire=="2" | tab$histoire=="1" | tab$histoire=="0"] <- "recall"

# juste baseline
b<- tab$condition[which(tab$baseline=="baseline")]
c<- tab$mean.f[which(tab$baseline=="baseline")]
d<- tab$id[which(tab$baseline=="baseline")]
tab2=data.table(condition=b,mean.f=c,id=d)



tab$combinaison<- as.factor(paste(tab$condition,tab$jour,tab$baseline))






### packages utilises

library(multcomp)
library(nlme)
library(ggplot2)


###################################################### statistiques descriptives #######################################

tgc <- summarySE(tab2, measurevar="mean.f", groupvars=c("condition"))
p<-ggplot(data=tgc, aes(x=condition, y=mean.f)) + 
  scale_fill_brewer() + theme_bw() +
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$mean.f-tgc$se, ymax=tgc$mean.f+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("Moyenne de la fréquence de pédalage")
p <- p + ylab("fréquence moyenne")+ labs(fill='pédalage') 
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
#p <- p+ facet_grid(.~baseline)
p

###############" effet de l'histoire ##########

# tgc <- summarySE(tab, measurevar="mean.f", groupvars=c("jour","histoire"))
# p<-ggplot(data=tgc, aes(x=jour, y=mean.f, fill=histoire)) + 
#   geom_bar(position=position_dodge(), stat="identity") +
#   geom_errorbar(aes(ymin=tgc$mean.f-tgc$se, ymax=tgc$mean.f+tgc$se),
#                 width=.2,                    # Width of the error bars
#                 position=position_dodge(.9)) +
#   ggtitle("Moyenne de la fréquence de pédalage")
# p <- p + ylab("fréquence moyenne")+ labs(fill='pédalage') 
# p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
#                plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
#                legend.title=element_text(size=18), legend.text = element_text(size=16))
# p
### distribution

hist(tab$mean.f)




###################################################### modelisation #######################################

### structure effets aleatoires

# un effet aleatoire intercept par sujet
# pas varib indiv selon j et c
fit0 <-  lme(mean.f~condition, random=~1|id,data=tab2, method="ML",na.action=na.exclude)
plot(fit0, id~resid(.,type="p")|condition, abline=0, xlim=c(-5,5), xlab="residus standardises")
# -> une seule valeur par sujet -> on saute


## etape 1


# un effet aleatoire intercept par sujet different par condition

fit1c <- lme(mean.f~condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~condition-1)))),data=tab2, method="ML",na.action=na.exclude)

anova(fit0,fit1c)
# pas différence, on rajoute pas d'effet aléatoire



### matrice de variance covariance des erreurs

# meme variance selon les modalites de condition

boxplot(resid(fit0,type="p")~tab$condition, xlab="residus normalises")


fit_varc <- lme(mean.f~condition, random=~1|id,weights=varIdent(form=~1|condition),data=tab2, method="ML",na.action=na.exclude)
anova(fit0,fit_varc)
# 0.92 : pas de variance différente selon la condition
# -> par variabilité résiduelle # selon la condition

#fit_varj <- lme(mean.f~condition, random=~1|id,weights=varIdent(form=~1|jour),data=tab, method="ML",na.action=na.exclude)
#anova(fit0,fit_varj)


# correlation entre jour

# tab$condition <- as.factor(paste(tab$id,tab$condition))
# tab$residus <- resid(fit_varj,type="normalized")
# mat <- matrix(rep(0,nlevels(tab$jour)*nlevels(tab$condition)),ncol=nlevels(tab$jour))
# for(i in 1:nlevels(tab$condition)){for(j in 1:nlevels(tab$jour)){mat[i,j] <- tab$residus[which(tab$condition == levels(tab$condition)[i] & tab$jour == levels(tab$jour)[j])]}}
# 
# pairs(mat)
# cor(mat)


tab2$residus <- resid(fit_varj,type="normalized")
mat <- matrix(rep(0,nlevels(tab2$condition)),ncol=nlevels(tab2$jour))
for(i in 1:nlevels(tab2$condition)){for(j in 1:nlevels(tab2$jour)){mat[i,j] <- tab2$residus[which(tab2$condition == levels(tab2$condition)[i] & tab2$jour == levels(tab2$jour)[j])]}}

pairs(mat)
cor(mat)



### structure effets fixes

# etape 1
fit_c <- update(fit0,.~.-condition)
anova(fit0,fit_c)
# différence : on garde la condition




# etape 3

# fit_cj_j_c <- update(fit_cj_j,.~.-condition)
# anova(fit_cj_j_c,fit_cj_j)




### validation du modele

mod_choisi <- lme(mean.f~condition, random=~1|id,data=tab2, method="ML",na.action=na.exclude)


# calcul des r?sidus du model 1 avec interaction

resmod_choisi.std<-resid(mod_choisi,type="normalized",level=1)

# plot residuals

hist(resmod_choisi.std,breaks=15,freq=FALSE,xlab="Standardized residuals", main="Histogram of the standardized residuals")
lines(density(resmod_choisi.std)) # résidus suivent distrib Normale

qqnorm(resmod_choisi.std,main = 'Normal QQplot of the standardized residuals \n of the log model')
qqline(resmod_choisi.std) # confirmé car aligné

plot(resmod_choisi.std~fitted(mod_choisi),xlab="Fitted values", ylab="Standardized residuals", main="Standardized residuals vs fitted values")
abline(a=0,b=0)

# patmat <- rbind(c(1,0,0,0,0,0),c(1,1,0,0,0,0),c(1,0,1,0,0,0),c(1,0,0,1,0,0),c(1,0,0,0,1,0),c(1,0,0,0,0,1))
# contrmat <- matrix(rep(0,6*),ncol=6)
# contrmat[1,] <- patmat[,] - patmat[,]
# 
# comp_mult <- summary(glht(mod_choisi,linfct=contrmat))


