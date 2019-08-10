###################################################### tableau de donnees #######################################
# effet aléatoire différent selon le jour 10.15298  0.0014
# pas d'interaction 5.730498  0.1255
# pas condition 1.471167  0.6889
# pas jour 0.1246253  0.7241
setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("../Transcription/csvFiles/brutDebit.csv",sep=",",header=TRUE)

# pê pédalage pieds != mains lbres
# pê mains contraintes != pédalage pieds
### type variable


tab$jour[tab$jour=="1"]<-"J1"
tab$jour[tab$jour=="2"]<-"J2"
tab$jour[tab$jour=="3"]<-"J3"
tab$jour <- as.factor(as.character(tab$jour))
tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))
tab$condition[tab$condition=="0"] <- "MAINS_LIBRES"
tab$condition[tab$condition=="1"] <- "MAINS_CONTRAINTES"
tab$condition[tab$condition=="2"] <- "PEDALAGE_PIEDS"
tab$condition[tab$condition=="3"] <- "PEDALAGE_MAINS"
tab$condition <- factor(tab$condition,levels = c("MAINS_LIBRES", "PEDALAGE_PIEDS", "PEDALAGE_MAINS","MAINS_CONTRAINTES"))
tab$condition <- as.factor(tab$condition)

### packages utilises

library(multcomp)
library(nlme)
library(ggplot2)



###################################################### statistiques descriptives #######################################

tgc <- summarySE(tab, measurevar="propHesit", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=propHesit, fill=condition)) +
  scale_fill_brewer() + theme_bw() +
  geom_bar(position=position_dodge(), stat="identity",colour="black") +
  geom_errorbar(aes(ymin=tgc$propHesit-tgc$se, ymax=tgc$propHesit+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) 
#  ggtitle("Proportion d'hésitations en rappel libre")
p <- p + ylab("PROP HESIT (%)")+ labs(fill='CONDITION') + xlab('JOUR')
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
              plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
              legend.title=element_text(size=18), legend.text = element_text(size=16))
p

###############" effet de l'histoire 

tgc <- summarySE(tab, measurevar="propHesit", groupvars=c("jour","histoire"))
p<-ggplot(data=tgc, aes(x=jour, y=propHesit, fill=histoire)) + 
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$propHesit-tgc$se, ymax=tgc$propHesit+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("Variabilité de la fréquence de pédalage")
p <- p + ylab("variance")+ labs(fill='histoire') 
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
p





### distribution
ggplot(tab, aes(x=tab$propHesit)) + geom_histogram(binwidth=10,color='black',fill='white') + xlab("variance de la fréquence de pédalage")
hist(tab$propHesit)

#
tab$propHesit<-(tab$propHesit*(nrow(tab)-1)+0.5)/nrow(tab)
# fait ça pour pas utiliser betareg
tab$propHesit<-log(tab$propHesit/(1-tab$propHesit))
###################################################### modelisation #######################################

### structure effets aleatoires

# un effet aleatoire intercept par sujet

fit0 <-  lme(propHesit~jour*condition, random=~1|id,data=tab, method="ML",na.action=na.exclude)


fit0 <-  lmer(propHesit~jour*condition+(1|id)+(1|histoire),data=tab,REML=FALSE,na.action=na.exclude)
plot(fit0, id~resid(.,type="p")|jour, abline=0, xlim=c(-5,5), xlab="residus standardises")
plot(fit0, id~resid(.,type="p")|condition, abline=0, xlim=c(-5,5), xlab="residus standardises")

# étape 0 : sél effets aléat : fit0bis

fit0bis<- lmer(propHesit~jour*condition+(1|id),data=tab,REML=FALSE,na.action=na.exclude)
anova(fit0,fit0bis)


# résidus standardisés
# plot des différents sujets, est-ce que les variabilités inter-individuelles changent selon le jour ?
plot(fit0, id~resid(.,type="p")|jour, abline=0, xlim=c(-5,5), xlab="residus standardises")

# plot des différents sujets, est-ce que les variabilités inter-individuelles changent selon la condition ?
plot(fit0, id~resid(.,type="p")|condition, abline=0, xlim=c(-5,5), xlab="residus standardises")


## etape 1

# structure des effets aléatoires
# un effet aleatoire intercept par sujet different par condition

# effet aléatoire différent selon la condition ?
fit1c <- lme(propHesit~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~condition-1)))),data=tab, method="ML",na.action=na.exclude)
# effet aléatoire différent selon le jour ?
fit1j <- lme(propHesit~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~jour-1)))),data=tab, method="ML",na.action=na.exclude)

anova(fit0,fit1c) #
anova(fit0,fit1j)# 
# garde fit1c


### matrice de variance covariance des erreurs

# meme variance selon les modalites de condition

boxplot(resid(fit1c,type="p")~tab$condition, xlab="residus normalises")
boxplot(resid(fit1c,type="p")~tab$jour, xlab="residus normalises")

fit_varc <- lme(propHesit~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~condition-1)))),weights=varIdent(form=~1|condition),data=tab, method="ML",na.action=na.exclude)
anova(fit1c,fit_varc) # ajoute de l'info

fit_varj <- lme(propHesit~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~condition-1)))),weights=varIdent(form=~1|jour),data=tab, method="ML",na.action=na.exclude)
anova(fit1c,fit_varj) # jour apporte de l'information -> garde fit_varj
# pas de variance résiduelle selon le jour ou la condition
# correlation entre jour

tab$combinaison <- as.factor(paste(tab$id,tab$condition))
tab$residus <- resid(fit1j,type="normalized")
mat <- matrix(rep(0,nlevels(tab$jour)*nlevels(tab$combinaison)),ncol=nlevels(tab$jour))
for(i in 1:nlevels(tab$combinaison)){for(j in 1:nlevels(tab$jour)){mat[i,j] <- tab$residus[which(tab$combinaison == levels(tab$combinaison)[i] & tab$jour == levels(tab$jour)[j])]}}

pairs(mat)
cor(mat)




### structure effets fixes

# etape 1
# on enlève l'intéraction et on teste
fit_cj <- update(fit1c,.~.-jour:condition)
anova(fit1c,fit_cj) # -> pas diff entre les 2 


# etape 2

fit_cj_c <- update(fit_cj,.~.-condition)
fit_cj_j <- update(fit_cj,.~.-jour)

anova(fit_cj,fit_cj_c) # enlève la condiiton -> chisq,p
anova(fit_cj,fit_cj_j) # 0.58 : enlève le jour
#on garde fit_cj_j !!

# -> on garde fit_cj_c


# etape 3 : on a enlevé le plus petit des 2 (un à chaque étape), on regarde si on enlève le deuxième

fit_cj_c_j <- update(fit_cj_c,.~.-jour)
anova(fit_cj_c_j,fit_cj_c) # on enlève le jour -> chisq,p




### validation du modele
# poser questions comment réécrire le modèle
mod_choisi <- fit_varc#lme(propHesit~condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~jour-1)))),data=tab, method="ML",na.action=na.exclude)


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

### comparaison multiples 
# patmat
patmat <- rbind(c(1,0,0,0,0,0,0,0),c(1,1,0,0,0,0,0,0),
                c(1,0,1,0,0,0,0,0),c(1,1,1,0,0,1,0,0),
                c(1,0,0,1,0,0,0,0),c(1,1,0,1,0,0,1,0),
                c(1,0,0,0,1,0,0,0),c(1,1,0,0,1,0,0,1)
)
rownames(patmat) <- c("jour1-Libre","jour2-Libre",
                      "jour1-Pieds","jour2-Pieds",
                      "jour1-Mains","jour2-Mains",
                      "jour1-Contrainte","jour2-Contrainte")


contrmat <- matrix(rep(0,8*10),ncol=8) # nbCol*nb Compar qu'on veut faire
#rownames(contrmat) <- c("j1C - j1L","j1M-j1P")

# # comparaisons j1
contrmat[1,] <- patmat[1,] - patmat[3,] # j1 mains libres-velo pieds PE EFFET 0.06
contrmat[2,] <- patmat[1,] - patmat[5,] # j1 mains libres - velo mains .
contrmat[3,] <- patmat[1,] - patmat[7,] # j1 mains libres - mains contraintes 0.18

contrmat[4,] <- patmat[2,] - patmat[4,] # j2 mains libres-velo pieds
contrmat[5,] <- patmat[2,] - patmat[6,] # j2 mains libres - velo mains .
contrmat[6,] <- patmat[2,] - patmat[8,] # j2 mains libres - mains contraintes

contrmat[7,] <- patmat[3,] - patmat[4,] # progression pieds.
contrmat[8,] <- patmat[5,] - patmat[6,] # progression mains
contrmat[9,] <- patmat[1,] - patmat[2,] # progression mains libres
contrmat[10,] <- patmat[7,] - patmat[8,] # progression mains contraintes

#contrmat <- lsmeans(mod_choisi, pairwise~condition|jour,glhargs=list())[[2]]$linfct
comp_mult <- summary(glht(mod_choisi,linfct=contrmat)) # comp_mult <- emmeans(mod_choisi,pairwise~condition|jour)



# comp_mult <- summary(glht(mod_choisi,linfct=mcp(condition="Tukey")))

