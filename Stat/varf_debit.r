###################################################### tableau de donnees #######################################
# lme peut modéliser variab résiduelle diff avec test modèles emboités 
# lmer le teste suppose variable résiduelles équivalentes, même écriture que glmer

# interaction 6.916847(L)  0.0746(p)
# condition 0.5877723  0.8992
# jour 0.07896773  0.7787

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
tab$varNorm<- tab$varDeb/tab$meanDeb

tab$jour[tab$jour=="1"]<-"J1"
tab$jour[tab$jour=="2"]<-"J2"
tab$jour[tab$jour=="3"]<-"J3"
tab$jour <- as.factor(as.character(tab$jour))

### packages utilises

library(multcomp)
library(nlme)
library(ggplot2)
library(lme4)


###################################################### statistiques descriptives #######################################



tgc <- summarySE(tab, measurevar="varNorm", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=varNorm, fill=condition)) + 
  scale_fill_brewer() + theme_bw() +
  geom_bar(position=position_dodge(), stat="identity",colour="black") +
  geom_errorbar(aes(ymin=tgc$varNorm-tgc$se, ymax=tgc$varNorm+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) 
#  ggtitle("Variance du débit lors du rappel libre")
p <- p + ylab("VAR DEB (syllabes/s)")+ labs(fill='CONDITION') +xlab("JOUR")
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
p

#################" effet de l'histoire ##############""

tgc <- summarySE(tab, measurevar="varNorm", groupvars=c("jour","histoire"))
p<-ggplot(data=tgc, aes(x=jour, y=varNorm, fill=histoire)) +
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$varNorm-tgc$se, ymax=tgc$varNorm+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) 
 # ggtitle("Scores en dénomination par histoire")
p <- p + ylab("Erreur")+ labs(fill='histoire')
p<- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
              plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
              legend.title=element_text(size=18), legend.text = element_text(size=16))
p


### distribution

hist(tab$varDeb)




###################################################### modelisation #######################################

### structure effets aleatoires
# modèle linéaire mixte < dans les généralisé
# un effet aleatoire intercept par sujet
# syntaxe change
# regarde fit0, enlève histoire si pas variance résiduelle
#fit0 <-  lmer(varDeb~jour*condition+(1|id)+(1|histoire),data=tab,REML=FALSE,na.action=na.exclude)
fit0 <- lme(varDeb~jour*condition, random=~1|id,data=tab, method="ML",na.action=na.exclude)
#fit0 <-  lme(meanDeb~jour*condition, random=~1|id,data=tab, method="ML",na.action=na.exclude)
plot(fit0, id~resid(.,type="p")|jour, abline=0, xlim=c(-5,5), xlab="residus standardises")
plot(fit0, id~resid(.,type="p")|condition, abline=0, xlim=c(-5,5), xlab="residus standardises")

# étape 0 : sél effets aléat : fit0bis

#fit0bis<- lmer(varDeb~jour*condition+(1|id),data=tab,REML=FALSE,na.action=na.exclude)
#anova(fit0,fit0bis)
## etape 1


# un effet aleatoire intercept par sujet different par condition

fit1c <- lme(varDeb~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~condition-1)))),data=tab, method="ML",na.action=na.exclude)
fit1j <- lme(varDeb~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~jour-1)))),data=tab, method="ML",na.action=na.exclude)

anova(fit0,fit1c)
anova(fit0,fit1j)
# garde fit0 pour ne pas ajouter info qui sert à rien

### matrice de variance covariance des erreurs

# meme variance selon les modalites de condition

boxplot(resid(fit1j,type="p")~tab$condition, xlab="residus normalises")
boxplot(resid(fit1j,type="p")~tab$jour, xlab="residus normalises")

fit_varc <- lme(varDeb~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~jour-1)))),weights=varIdent(form=~1|condition),data=tab, method="ML",na.action=na.exclude)
anova(fit0,fit_varc)

fit_varj <- lme(varDeb~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~jour-1)))),weights=varIdent(form=~1|jour),data=tab, method="ML",na.action=na.exclude)
anova(fit0,fit_varj)

# garde fit0
# correlation entre jour

tab$combinaison <- as.factor(paste(tab$id,tab$condition))
tab$residus <- resid(fit1j,type="normalized")
mat <- matrix(rep(0,nlevels(tab$jour)*nlevels(tab$combinaison)),ncol=nlevels(tab$jour))
for(i in 1:nlevels(tab$combinaison)){for(j in 1:nlevels(tab$jour)){mat[i,j] <- tab$residus[which(tab$combinaison == levels(tab$combinaison)[i] & tab$jour == levels(tab$jour)[j])]}}

pairs(mat)
cor(mat)




### structure effets fixes

# etape 1

fit_cj <- update(fit0,.~.-jour:condition)
anova(fit0,fit_cj) # garde l'intéraction


# etape 2
# impact de la condition différent selon le jour
# si enlève l'intéraction, différence vraie quel que soit le jour
# si un jour dim, l'autre augm
fit_cj_c <- update(fit_cj,.~.-condition)
fit_cj_j <- update(fit_cj,.~.-jour)

anova(fit_cj,fit_cj_c)
anova(fit_cj,fit_cj_j)


# etape 3

fit_cj_j_c <- update(fit_cj_c,.~.-jour)
anova(fit_cj_j_c,fit_cj_c)

# enlève les deux




### validation du modele

mod_choisi <- fit0 #fit0 #lme(varDeb~condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~jour-1)))),data=tab, method="ML",na.action=na.exclude)


# calcul des r?sidus du model 1 avec interaction

resmod_choisi.std<-resid(mod_choisi,type="normalized",level=1)

# plot residuals

hist(resmod_choisi.std,breaks=15,freq=FALSE,xlab="Standardized residuals", main="Histogram of the standardized residuals")
lines(density(resmod_choisi.std))

qqnorm(resmod_choisi.std,main = 'Normal QQplot of the standardized residuals \n of the log model')
qqline(resmod_choisi.std)

plot(resmod_choisi.std~fitted(mod_choisi),xlab="Fitted values", ylab="Standardized residuals", main="Standardized residuals vs fitted values")
abline(a=0,b=0)



### comparaisons multiples
# ou fait avec patmat
# mod_choisi

patmat <- rbind(c(1,0,0,0,0,0,0,0),c(1,1,0,0,0,0,0,0), 
                c(1,0,1,0,0,0,0,0),c(1,1,1,0,0,1,0,0), 
                c(1,0,0,1,0,0,0,0),c(1,1,0,1,0,0,1,0), 
                c(1,0,0,0,1,0,0,0),c(1,1,0,0,1,0,0,1)) # donne valeur à chaque cellule
rownames(patmat) <- c("jour1-ML","jour2-ML",
                      "jour1-PP","jour2-PP",
                      "jour1-PM","jour2-PM",
                      "jour1-MC","jour2-PMC"
) # doit tout définir
contrmat <- matrix(rep(0,8*10),ncol=8) # nbCol*nb Compar qu'on veut faire
# # # comparaisons j1
contrmat[1,] <- patmat[7,] - patmat[1,] # j1 mains libres-contraintes *
contrmat[2,] <- patmat[5,] - patmat[1,] # j1 mains libres - velo mains .
contrmat[3,] <- patmat[3,] - patmat[1,] # j1 mains libres - velo pieds -> pas significatif

# # comparaisons j2
contrmat[4,] <- patmat[8,] - patmat[2,] # j1 mains libres-contraintes *
contrmat[5,] <- patmat[6,] - patmat[2,] # j1 mains libres - velo mains .
contrmat[6,] <- patmat[4,] - patmat[2,] # j1 mains libres - velo pieds -> pas significatif

contrmat[7,] <- patmat[1,] - patmat[2,] # j1 mains libres-contraintes *
contrmat[8,] <- patmat[3,] - patmat[4,] # j1 mains libres - velo mains .
contrmat[9,] <- patmat[5,] - patmat[6,] # j1 mains libres - velo pieds -> pas significatif
contrmat[10,] <- patmat[7,] - patmat[8,] # j1 mains libres - velo pieds -> pas significatif

comp_mult <- summary(glht(mod_choisi,linfct=contrmat,adjust.method="none"))

  
  #comp_mult <- summary(glht(mod_choisi,linfct=mcp(condition="Tukey")))

