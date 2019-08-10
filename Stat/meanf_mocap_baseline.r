###################################################### tableau de donnees #######################################
# Attention : diviser les deux moyennes c'est pas la même chose que faire le quotient pour chaque et en calculer la moyenne
# DONE : pas effet jour, mais de la condition
# pas d'interaction L=0.004992785  p=0.9437
# effet condition  6.558069  0.0104
# aps effet jour 0.6004413  0.4384

# effet aléatoire différent selon la condition L 17.8433 , p <.0001



### importer tableau 
setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("../MoCapAnalysis/brutMoCapBaseline.csv",sep=",",header=TRUE)

### type variable

tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))
tab$condition[tab$condition=="2"] <- "PEDALAGE_PIEDS"
tab$condition[tab$condition=="3"] <- "PEDALAGE_MAINS"
#tab$condition <- factor(tab$condition,levels = c("pédalage mains", "pédalage pieds"))
tab$condition <- as.factor(as.character(tab$condition))
tab$jour[tab$jour=="1"]<-"J1"
tab$jour[tab$jour=="2"]<-"J2"
tab$jour[tab$jour=="3"]<-"J3"
tab$jour <- as.factor(as.character(tab$jour))



### packages utilises

library(multcomp)
library(nlme)
library(ggplot2)


###################################################### statistiques descriptives #######################################
x=100
a<- tab$id[which(tab$meanf.rb<x)]
b<- tab$jour[which(tab$meanf.rb<x)]
c<- tab$condition[which(tab$meanf.rb<x)]
d<- tab$meanf.rb[which(tab$meanf.rb<x)]
tab2=data.table(id=a,jour=b,condition=c,meanf.rb=d)




tgc <- summarySE(tab2, measurevar="meanf.rb", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=meanf.rb, fill=condition)) + 
  scale_fill_brewer() + theme_bw() +
  geom_bar(position=position_dodge(), stat="identity",colour="black") +
  geom_errorbar(aes(ymin=tgc$meanf.rb-tgc$se, ymax=tgc$meanf.rb+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) 
#  ggtitle("fréquence moyenne de pédalage")
p <- p + ylab("MEAN PED RL (%)")+ labs(fill='CONDITION')+xlab('JOUR') 
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
p

###############" effet de l'histoire ##########

tgc <- summarySE(tab, measurevar="meanf.rb", groupvars=c("jour","histoire"))
p<-ggplot(data=tgc, aes(x=jour, y=meanf.rb, fill=histoire)) +
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$meanf.rb-tgc$se, ymax=tgc$meanf.rb+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("Moyenne de la fréquence de pédalage")
p <- p + ylab("fréquence moyenne")+ labs(fill='pédalage')
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
p
### distribution

hist(tab$meanf.rb)




###################################################### modelisation #######################################

### structure effets aleatoires

# un effet aleatoire intercept par sujet

 fit0 <-  lme(meanf.rb~jour*condition, random=~1|id,data=tab, method="ML",na.action=na.exclude)
 plot(fit0, id~resid(.,type="p")|jour, abline=0, xlim=c(-5,5), xlab="residus standardises")
 plot(fit0, id~resid(.,type="p")|condition, abline=0, xlim=c(-5,5), xlab="residus standardises")

#fit0 <-  lmer(meanf.rb~jour*condition+(1|id)+(1|histoire),data=tab,REML=FALSE,na.action=na.exclude)
# plot(fit0, id~resid(.,type="p")|jour, abline=0, xlim=c(-5,5), xlab="residus standardises")
# plot(fit0, id~resid(.,type="p")|condition, abline=0, xlim=c(-5,5), xlab="residus standardises")

# étape 0 : sél effets aléat : fit0bis

fit0bis<- lmer(meanf.rb~jour*condition+(1|id),data=tab,REML=FALSE,na.action=na.exclude)
anova(fit0,fit0bis)

## etape 1


# un effet aleatoire intercept par sujet different par condition

fit1c <- lme(meanf.rb~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~condition-1)))),data=tab, method="ML",na.action=na.exclude)
fit1j <- lme(meanf.rb~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~jour-1)))),data=tab, method="ML",na.action=na.exclude)

anova(fit0,fit1c) # -> effet aléatoire différent par sujet selon la condition
anova(fit0,fit1j) # pas de différence, on enlève le jour
# on garde fit1c


### matrice de variance covariance des erreurs

# meme variance selon les modalites de condition

boxplot(resid(fit0,type="p")~tab$condition, xlab="residus normalises")
boxplot(resid(fit0,type="p")~tab$jour, xlab="residus normalises")

fit_varc <- lme(meanf.rb~jour*condition, random=~1|id,weights=varIdent(form=~1|condition),data=tab, method="ML",na.action=na.exclude)
anova(fit1c,fit_varc)

fit_varj <- lme(meanf.rb~jour*condition, random=~1|id,weights=varIdent(form=~1|jour),data=tab, method="ML",na.action=na.exclude)
anova(fit1c,fit_varj)
# on garde fit1c

# correlation entre jour

tab$combinaison <- as.factor(paste(tab$id,tab$condition))
tab$residus <- resid(fit_varj,type="normalized")
mat <- matrix(rep(0,nlevels(tab$jour)*nlevels(tab$combinaison)),ncol=nlevels(tab$jour))
for(i in 1:nlevels(tab$combinaison)){for(j in 1:nlevels(tab$jour)){mat[i,j] <- tab$residus[which(tab$combinaison == levels(tab$combinaison)[i] & tab$jour == levels(tab$jour)[j])]}}

pairs(mat)
cor(mat)




### structure effets fixes

# etape 1

fit_cj <- update(fit1c,.~.-jour:condition)
anova(fit1c,fit_cj)
# on vire l'intéraction car pas de diff entre les 2 modèles

# etape 2

fit_cj_c <- update(fit_cj,.~.-condition) # la y a diff : on garde la condition
fit_cj_j <- update(fit_cj,.~.-jour) # pas de diff : on vire le jour

anova(fit_cj,fit_cj_c)
anova(fit_cj,fit_cj_j)
# on n'enlève rien



### validation du modele

mod_choisi <-fit_cj_j # lme(meanf.rb~1, random=~1|id,weights=varIdent(form=~1|jour),data=tab, method="ML",na.action=na.exclude)


# calcul des r?sidus du model 1 avec interaction

resmod_choisi.std<-resid(mod_choisi,type="normalized",level=1)

# plot residuals

hist(resmod_choisi.std,breaks=15,freq=FALSE,xlab="Standardized residuals", main="Histogram of the standardized residuals")
lines(density(resmod_choisi.std))

qqnorm(resmod_choisi.std,main = 'Normal QQplot of the standardized residuals \n of the log model')
qqline(resmod_choisi.std)

plot(resmod_choisi.std~fitted(mod_choisi),xlab="Fitted values", ylab="Standardized residuals", main="Standardized residuals vs fitted values")
abline(a=0,b=0)




