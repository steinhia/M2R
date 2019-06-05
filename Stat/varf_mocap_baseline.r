###################################################### tableau de donnees #######################################
# Done : on garde l'intéraction

### importer tableau 
setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("../MoCapAnalysis/brutMoCapBaseline.csv",sep=",",header=TRUE)


### type variable

tab$jour <- as.factor(as.character(tab$jour))
tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))
tab$condition[tab$condition=="2"] <- "pieds"
tab$condition[tab$condition=="3"] <- "mains"
tab$condition <- as.factor(tab$condition)


### packages utilises

library(multcomp)
library(nlme)
library(ggplot2)
library(data.table)


###################################################### statistiques descriptives #######################################

# histo var fréquence
b <- ggplot(tab, aes(x = tab$varf.rb))
b<- b + geom_histogram(bins=10)
b <- b+ facet_grid(.~condition)
b


xMax=mean(tab$varf.rb)+2*sqrt(var(tab$varf.rb))
xMin=mean(tab$varf.rb)-2*sqrt(var(tab$varf.rb))
#x=100
a<- tab$id[which(tab$varf.rb<xMax)]
b<- tab$jour[which(tab$varf.rb<xMax)]
c<- tab$condition[which(tab$varf.rb<xMax)]
d<- tab$varf.rb[which(tab$varf.rb<xMax)]
tab2=data.table(id=a,jour=b,condition=c,varf.rb=d)



tgc <- summarySE(tab2, measurevar="varf.rb", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=varf.rb, fill=condition)) + 
  scale_fill_brewer() + theme_bw() +
  geom_bar(position=position_dodge(), stat="identity",colour="black") +
  geom_errorbar(aes(ymin=tgc$varf.rb-tgc$se, ymax=tgc$varf.rb+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("Variabilité de la fréquence de pédalage \n recall/baseline avec outliers")
p <- p + ylab("variance")+ labs(fill='pédalage') 
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
              plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
              legend.title=element_text(size=18), legend.text = element_text(size=16))
p

###############" effet de l'histoire 
# 
# tgc <- summarySE(tab, measurevar="varf.rb", groupvars=c("jour","histoire"))
# p<-ggplot(data=tgc, aes(x=jour, y=varf.rb, fill=histoire)) + 
#   geom_bar(position=position_dodge(), stat="identity") +
#   geom_errorbar(aes(ymin=tgc$varf.rb-tgc$se, ymax=tgc$varf.rb+tgc$se),
#                 width=.2,                    # Width of the error bars
#                 position=position_dodge(.9)) +
#   ggtitle("Variabilité de la fréquence de pédalage")
# p <- p + ylab("variance")+ labs(fill='histoire') 
# p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
#                plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
#                legend.title=element_text(size=18), legend.text = element_text(size=16))
# p





### distribution
ggplot(tab, aes(x=tab$varf.rb)) + geom_histogram(binwidth=10,color='black',fill='white') + xlab("variance de la fréquence de pédalage")
hist(tab$varf.rb)




###################################################### modelisation #######################################

### structure effets aleatoires

# un effet aleatoire intercept par sujet

fit0 <-  lme(varf.rb~jour*condition, random=~1|id,data=tab, method="ML",na.action=na.exclude)

# résidus standardisés
# plot des différents sujets, est-ce que les variabilités inter-individuelles changent selon le jour ?
plot(fit0, id~resid(.,type="p")|jour, abline=0, xlim=c(-5,5), xlab="residus standardises")

# plot des différents sujets, est-ce que les variabilités inter-individuelles changent selon la condition ?
plot(fit0, id~resid(.,type="p")|condition, abline=0, xlim=c(-5,5), xlab="residus standardises")


## etape 1

# structure des effets aléatoires
# un effet aleatoire intercept par sujet different par condition

# effet aléatoire différent selon la condition ?
fit1c <- lme(varf.rb~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~condition-1)))),data=tab, method="ML",na.action=na.exclude)
# effet aléatoire différent selon le jour ?
fit1j <- lme(varf.rb~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~jour-1)))),data=tab, method="ML",na.action=na.exclude)
# on enlève un effet résiduel par jour

anova(fit0,fit1c) 
anova(fit0,fit1j)
# pas très loin, mais garde fit0

### matrice de variance covariance des erreurs

# meme variance selon les modalites de condition

boxplot(resid(fit1j,type="p")~tab$condition, xlab="residus normalises")
boxplot(resid(fit1j,type="p")~tab$jour, xlab="residus normalises")

fit_varc <- lme(varf.rb~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~jour-1)))),weights=varIdent(form=~1|condition),data=tab, method="ML",na.action=na.exclude)
anova(fit0,fit_varc) # ajoute pas d'information : 0.91

fit_varj <- lme(varf.rb~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~jour-1)))),weights=varIdent(form=~1|jour),data=tab, method="ML",na.action=na.exclude)
anova(fit0,fit_varj) # non plus


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
fit_cj <- update(fit0,.~.-jour:condition)
anova(fit0,fit_cj) # -> 0.07 on garde l'intéraction


# etape 2

fit1c_c <- update(fit_cj,.~.-condition)

fit1c_j <- update(fit_cj,.~.-jour)

anova(fit_cj,fit1c_c) # peut pas enlever la condition
anova(fit_cj,fit1c_j) # peut pas enlever le jour

# -> on garde fit_cj


# etape 3 : on a enlevé le plus petit des 2 (un à chaque étape), on regarde si on enlève le deuxième

#fit_cj_j_c <- update(fit_cj_j,.~.-condition)
#anova(fit_cj_j_c,fit_cj_j) # on enlève pas la condition




### validation du modele
# poser questions comment réécrire le modèle
mod_choisi <- fit0 #lme(varf.rb~condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~jour-1)))),data=tab, method="ML",na.action=na.exclude)


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
# TODO regarde
comp_mult <- summary(glht(mod_choisi,linfct=mcp(condition="Tukey")))

