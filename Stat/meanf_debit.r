###################################################### tableau de donnees #######################################
# DOne : pas d'effet
# effet aléatoire lié au participant
# pas de condiiton 1.323253  0.7236
# pas de jour 1.46358  0.2264
# pas d'interaction 1.675263  0.6424


### importer tableau 

setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("../Transcription/csvFiles/brutSyll.csv",sep=",",header=TRUE)

### type variable


tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))
tab$condition[tab$condition=="0"] <- "MAINS_LIBRES"
tab$condition[tab$condition=="1"] <- "MAINS_CONTRAINTES"
tab$condition[tab$condition=="2"] <- "PEDALAGE_PIEDS"
tab$condition[tab$condition=="3"] <- "PEDALAGE_MAINS"
tab$condition <- factor(tab$condition,levels = c("MAINS_LIBRES", "PEDALAGE_PIEDS", "PEDALAGE_MAINS","MAINS_CONTRAINTES"))
tab$condition <- as.factor(tab$condition)

tab$jour[tab$jour=="1"]<-"J1"
tab$jour[tab$jour=="2"]<-"J2"
tab$jour[tab$jour=="3"]<-"J3"
tab$jour <- as.factor(as.character(tab$jour))

### packages utilises

library(multcomp)
library(nlme)
library(ggplot2)


###################################################### statistiques descriptives #######################################

tgc <- summarySE(tab, measurevar="meanDeb", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=meanDeb, fill=condition)) + 
  scale_fill_brewer() + theme_bw() +
  geom_bar(position=position_dodge(), stat="identity",colour="black") +
  geom_errorbar(aes(ymin=tgc$meanDeb-tgc$se, ymax=tgc$meanDeb+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) 
#  ggtitle("Débit moyen lors du rappel libre (syllabes/s)")
p <- p + ylab("MEAN DEB (syllabes/s)")+ labs(fill='CONDITION') +xlab('JOUR')
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
p

##############" effet de l'histoire ########"""

tgc <- summarySE(tab, measurevar="meanDeb", groupvars=c("jour","histoire"))
p<-ggplot(data=tgc, aes(x=jour, y=meanDeb, fill=histoire)) +
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$meanDeb-tgc$se, ymax=tgc$meanDeb+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) 
#  ggtitle("Débit moyen selon le jour et la condition")
p <- p + ylab("débit moyen")+ labs(fill='histoire')
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
p

### distribution

hist(tab$meanDeb)




###################################################### modelisation #######################################

### structure effets aleatoires

# un effet aleatoire intercept par sujet

# fit0 <-  lme(meanDeb~jour*condition, random=~1|id,data=tab, method="ML",na.action=na.exclude)
# plot(fit0, id~resid(.,type="p")|jour, abline=0, xlim=c(-5,5), xlab="residus standardises")
# plot(fit0, id~resid(.,type="p")|condition, abline=0, xlim=c(-5,5), xlab="residus standardises")


fit0 <-  lmer(meanDeb~jour*condition+(1|id)+(1|histoire),data=tab,REML=FALSE,na.action=na.exclude)
fit0 <-  lme(meanDeb~jour*condition, random=~1|id,data=tab, method="ML",na.action=na.exclude)
plot(fit0, id~resid(.,type="p")|jour, abline=0, xlim=c(-5,5), xlab="residus standardises")
plot(fit0, id~resid(.,type="p")|condition, abline=0, xlim=c(-5,5), xlab="residus standardises")

# étape 0 : sél effets aléat : fit0bis

fit0bis<- lmer(meanDeb~jour*condition+(1|id),data=tab,REML=FALSE,na.action=na.exclude)
anova(fit0,fit0bis)
# 0.36 : on laisse comme ça


## etape 1


# un effet aleatoire intercept par sujet different par condition

fit1c <- lme(meanDeb~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~condition-1)))),data=tab, method="ML",na.action=na.exclude)
fit1j <- lme(meanDeb~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~jour-1)))),data=tab, method="ML",na.action=na.exclude)

anova(fit0,fit1c)
anova(fit0,fit1j)


### matrice de variance covariance des erreurs

# meme variance selon les modalites de condition

boxplot(resid(fit0,type="p")~tab$condition, xlab="residus normalises")
boxplot(resid(fit0,type="p")~tab$jour, xlab="residus normalises")

fit_varc <- lme(meanDeb~jour*condition, random=~1|id,weights=varIdent(form=~1|condition),data=tab, method="ML",na.action=na.exclude)
anova(fit0,fit_varc)

fit_varj <- lme(meanDeb~jour*condition, random=~1|id,weights=varIdent(form=~1|jour),data=tab, method="ML",na.action=na.exclude)
anova(fit0,fit_varj)

# garde fit0 car le modèle le plus simple

# correlation entre jour

tab$combinaison <- as.factor(paste(tab$id,tab$condition))
tab$residus <- resid(fit_varj,type="normalized")
mat <- matrix(rep(0,nlevels(tab$jour)*nlevels(tab$combinaison)),ncol=nlevels(tab$jour))
for(i in 1:nlevels(tab$combinaison)){for(j in 1:nlevels(tab$jour)){mat[i,j] <- tab$residus[which(tab$combinaison == levels(tab$combinaison)[i] & tab$jour == levels(tab$jour)[j])]}}

pairs(mat)
cor(mat)




### structure effets fixes

# etape 1

fit_cj <- update(fit0,.~.-jour:condition)
anova(fit0,fit_cj)
# gpas de différence : garde le modèle le plus simple

# etape 2

fit_cj_c <- update(fit_cj,.~.-condition)
fit_cj_j <- update(fit_cj,.~.-jour)

anova(fit_cj,fit_cj_c)
anova(fit_cj,fit_cj_j)
# enlève celui avec la plus grosse p-value fit_cj_c


# etape 3

fit_cj_j_c <- update(fit_cj_c,.~.-jour)
anova(fit_cj_j_c,fit_cj_c)




### validation du modele

mod_choisi <-fit_cj_j_c # lme(meanDeb~1, random=~1|id,weights=varIdent(form=~1|jour),data=tab, method="ML",na.action=na.exclude)


# calcul des r?sidus du model 1 avec interaction

resmod_choisi.std<-resid(mod_choisi,type="normalized",level=1)

# plot residuals

hist(resmod_choisi.std,breaks=15,freq=FALSE,xlab="Standardized residuals", main="Histogram of the standardized residuals")
lines(density(resmod_choisi.std))

qqnorm(resmod_choisi.std,main = 'Normal QQplot of the standardized residuals \n of the log model')
qqline(resmod_choisi.std)

plot(resmod_choisi.std~fitted(mod_choisi),xlab="Fitted values", ylab="Standardized residuals", main="Standardized residuals vs fitted values")
abline(a=0,b=0)




