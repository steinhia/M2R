###################################################### tableau de donnees #######################################

# peut être effet de var ipu et var deb, pas d'effet de la moyenne
# pas d'effet SDTD ou meanIPU ?
# durée des pauses -> histogramme par condition
setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("../Transcription/brutSyll.csv",sep=",",header=TRUE)

### type variable

tab$jour <- as.factor(as.character(tab$jour))
tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))
tab$condition[tab$condition=="0"] <- "mains libres"
tab$condition[tab$condition=="1"] <- "mains contraintes"
tab$condition[tab$condition=="2"] <- "pédalage pieds"
tab$condition[tab$condition=="3"] <- "pédalage mains"
tab$condition <- as.factor(tab$condition)
tab


### packages utilises

library(multcomp)
library(nlme)
library(ggplot2)

lm_eqn <- function(df,v1,v2){
  m <- lm(v1 ~ v2, df);
  eq <- substitute(italic(y) == a + b %.% italic(x)*","~~italic(r)^2~"="~r2, 
                   list(a = format(coef(m)[1], digits = 2),
                        b = format(coef(m)[2], digits = 2),
                        r2 = format(summary(m)$r.squared, digits = 3)))
  as.character(as.expression(eq));
}


b <- ggplot(tab, aes(x = tab$meanDeb, y=tab$SpeechRate))
b<- b + geom_point() # rajouter y dans le ggplot de base
b<- b+geom_smooth(method = "lm")
b <-b + geom_text(x = 2, y = 4, label = lm_eqn(tab,tab$meanDeb,tab$SpeechRate), parse = TRUE)
b
###################################################### statistiques descriptives #######################################

tgc <- summarySE(tab, measurevar="meanIPU", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=meanIPU, fill=condition)) + 
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$meanIPU-tgc$se, ymax=tgc$meanIPU+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("mean IPU")
p <- p + ylab("mean ipu")+ labs(fill='condition') 
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
p

##############" effet de l'histoire ########"""

tgc <- summarySE(tab, measurevar="meanIPU", groupvars=c("jour","histoire"))
p<-ggplot(data=tgc, aes(x=jour, y=meanIPU, fill=histoire)) + 
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$meanIPU-tgc$se, ymax=tgc$meanIPU+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("Débit moyen selon le jour et la condition")
p <- p + ylab("débit moyen")+ labs(fill='histoire') 
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
p

### distribution

hist(tab$meanIPU)




###################################################### modelisation #######################################

### structure effets aleatoires

# un effet aleatoire intercept par sujet

fit0 <-  lme(meanIPU~jour*condition, random=~1|id,data=tab, method="ML",na.action=na.exclude)
plot(fit0, id~resid(.,type="p")|jour, abline=0, xlim=c(-5,5), xlab="residus standardises")
plot(fit0, id~resid(.,type="p")|condition, abline=0, xlim=c(-5,5), xlab="residus standardises")


## etape 1


# un effet aleatoire intercept par sujet different par condition

fit1c <- lme(meanIPU~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~condition-1)))),data=tab, method="ML",na.action=na.exclude)
fit1j <- lme(meanIPU~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~jour-1)))),data=tab, method="ML",na.action=na.exclude)

anova(fit0,fit1c)
anova(fit0,fit1j)


### matrice de variance covariance des erreurs

# meme variance selon les modalites de condition

boxplot(resid(fit0,type="p")~tab$condition, xlab="residus normalises")
boxplot(resid(fit0,type="p")~tab$jour, xlab="residus normalises")

fit_varc <- lme(meanIPU~jour*condition, random=~1|id,weights=varIdent(form=~1|condition),data=tab, method="ML",na.action=na.exclude)
anova(fit0,fit_varc)

fit_varj <- lme(meanIPU~jour*condition, random=~1|id,weights=varIdent(form=~1|jour),data=tab, method="ML",na.action=na.exclude)
anova(fit0,fit_varj)


# correlation entre jour

tab$combinaison <- as.factor(paste(tab$id,tab$condition))
tab$residus <- resid(fit_varj,type="normalized")
mat <- matrix(rep(0,nlevels(tab$jour)*nlevels(tab$combinaison)),ncol=nlevels(tab$jour))
for(i in 1:nlevels(tab$combinaison)){for(j in 1:nlevels(tab$jour)){mat[i,j] <- tab$residus[which(tab$combinaison == levels(tab$combinaison)[i] & tab$jour == levels(tab$jour)[j])]}}

pairs(mat)
cor(mat)




### structure effets fixes

# etape 1

fit_cj <- update(fit_varj,.~.-jour:condition)
anova(fit_varj,fit_cj)


# etape 2

fit_cj_c <- update(fit_cj,.~.-condition)
fit_cj_j <- update(fit_cj,.~.-jour)

anova(fit_cj,fit_cj_c)
anova(fit_cj,fit_cj_j)


# etape 3

fit_cj_j_c <- update(fit_cj_j,.~.-condition)
anova(fit_cj_j_c,fit_cj_j)




### validation du modele

mod_choisi <- lme(meanIPU~1, random=~1|id,weights=varIdent(form=~1|jour),data=tab, method="ML",na.action=na.exclude)


# calcul des r?sidus du model 1 avec interaction

resmod_choisi.std<-resid(mod_choisi,type="normalized",level=1)

# plot residuals

hist(resmod_choisi.std,breaks=15,freq=FALSE,xlab="Standardized residuals", main="Histogram of the standardized residuals")
lines(density(resmod_choisi.std))

qqnorm(resmod_choisi.std,main = 'Normal QQplot of the standardized residuals \n of the log model')
qqline(resmod_choisi.std)

plot(resmod_choisi.std~fitted(mod_choisi),xlab="Fitted values", ylab="Standardized residuals", main="Standardized residuals vs fitted values")
abline(a=0,b=0)




