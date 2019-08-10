###################################################### tableau de donnees #######################################
#TODO : j'analyse lequel : avec ou sans outliers ?
# pas d'effet de la condition : L-value : 0.7934648 p= 0.3731
# enlève outlier mais ça change pas le nombre
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
tab$condition <- as.factor(tab$condition)
tab$baseline[tab$histoire=="-1"] <- "baseline"
tab$baseline[tab$histoire=="3" | tab$histoire=="2" | tab$histoire=="1" | tab$histoire=="0"] <- "recall"
tab$varNorm<- tab$var.f/tab$mean.f

xMax=mean(tab$var.f)+2*sqrt(var(tab$var.f))
xMin=mean(tab$var.f)-2*sqrt(var(tab$var.f))

b<- tab$condition[which(tab$baseline=="baseline")]
c<- tab$var.f[which(tab$baseline=="baseline")]
d<- tab$id[which(tab$baseline=="baseline")]
tab3=data.table(condition=b,var.f=c,id=d)

# juste baseline
b<- tab$condition[which(tab$baseline=="baseline" & tab$var.f<xMax)]
c<- tab$var.f[which(tab$baseline=="baseline" & tab$var.f<xMax)]
d<- tab$id[which(tab$baseline=="baseline" & tab$var.f<xMax)]
tab2=data.table(condition=b,var.f=c,id=d)

### packages utilises

library(multcomp)
library(nlme)
library(ggplot2)
library(data.table)



###################################################### statistiques descriptives #######################################
# histo var fréquence
b <- ggplot(tab, aes(x = tab$var.f))
b<- b + geom_histogram(bins=10)
b <- b+ facet_grid(.~condition)
b

# histo var z
b <- ggplot(tab, aes(x = tab$varz))
b<- b + geom_histogram(bins=10)
b <- b+ facet_grid(.~condition)
b

# régression
b <- ggplot(tab, aes(x = tab$var.f, y=tab$varz))
b<- b + geom_point() # rajouter y dans le ggplot de base
b <- b+ facet_grid(.~condition)
b


# 
# x=0.05
# a<- tab$id[which(tab$var.f<x)]
# b<- tab$jour[which(tab$var.f<x)]
# c<- tab$condition[which(tab$var.f<x)]
# d<- tab$var.f[which(tab$var.f<x)]
# e<- tab$baseline[which(tab$var.f<x)]
# tab2=data.table(id=a,jour=b,condition=c,var.f=d,baseline=e)
# 
# x=0.000005
# a<- tab$id[which(tab$var.f<x)]
# b<- tab$jour[which(tab$var.f<x)]
# c<- tab$condition[which(tab$var.f<x)]
# d<- tab$var.f[which(tab$var.f<x)]
# e<- tab$baseline[which(tab$var.f<x)]
# tab3=data.table(id=a,jour=b,condition=c,var.f=d,baseline=e)
# 


tgc <- summarySE(tab2, measurevar="var.f", groupvars=c("condition"))
p<-ggplot(data=tgc, aes(x=condition, y=var.f)) +
  scale_fill_brewer() + theme_bw() +
  geom_bar(position=position_dodge(), stat="identity",colour="black") +
  geom_errorbar(aes(ymin=tgc$var.f-tgc$se, ymax=tgc$var.f+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) 
#  ggtitle("Variabilité de la fréquence de pédalage")
p <- p + ylab("VAR_MOCAP_BL")+ labs(fill='pédalage')
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
              plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
              legend.title=element_text(size=18), legend.text = element_text(size=16))
#p <- p+ facet_grid(.~baseline)
p

###############" effet de l'histoire 

tgc <- summarySE(tab, measurevar="var.f", groupvars=c("jour","histoire"))
p<-ggplot(data=tgc, aes(x=jour, y=var.f, fill=histoire)) + 
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$var.f-tgc$se, ymax=tgc$var.f+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("Variabilité de la fréquence de pédalage")
p <- p + ylab("variance")+ labs(fill='histoire') 
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
p





### distribution
ggplot(tab, aes(x=tab$var.f)) + geom_histogram(binwidth=10,color='black',fill='white') + xlab("variance de la fréquence de pédalage")
hist(tab$var.f)




###################################################### modelisation #######################################

### structure effets aleatoires

# un effet aleatoire intercept par sujet

fit0 <-  lme(var.f~condition, random=~1|id,data=tab2, method="ML",na.action=na.exclude)

fit0 <-  lmer(var.f~condition+(1|id)+(1|histoire),data=tab,REML=FALSE,na.action=na.exclude)
plot(fit0, id~resid(.,type="p")|jour, abline=0, xlim=c(-5,5), xlab="residus standardises")
plot(fit0, id~resid(.,type="p")|condition, abline=0, xlim=c(-5,5), xlab="residus standardises")

# étape 0 : sél effets aléat : fit0bis

fit0bis<- lmer(var.f~condition+(1|id),data=tab,REML=FALSE,na.action=na.exclude)
anova(fit0,fit0bis)



# résidus standardisés
## plot des différents sujets, est-ce que les variabilités inter-individuelles changent selon la condition ?
plot(fit0, id~resid(.,type="p")|condition, abline=0, xlim=c(-5,5), xlab="residus standardises")


## etape 1

# structure des effets aléatoires
# un effet aleatoire intercept par sujet different par condition

# effet aléatoire différent selon la condition ?
#fit1c <-  lmer(var.f~condition+(1|id)+(1|histoire)+(1|condition),data=tab,REML=FALSE,na.action=na.exclude)
fit1c <- lme(var.f~condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~condition-1)))),data=tab2, method="ML",na.action=na.exclude)
# par de variacne résiduelle par individu
anova(fit0,fit1c) 
# garde fit1c


### matrice de variance covariance des erreurs

# meme variance selon les modalites de condition

#boxplot(resid(fit0,type="p")~tab2$condition, xlab="residus normalises")


#fit_varc <- lme(var.f~condition, random=~1|id,weights=varIdent(form=~1|condition),data=tab2, method="ML",na.action=na.exclude)
#anova(fit0,fit_varc) # garde fit0


# correlation entre jour

tab2$combinaison <- as.factor(paste(tab2$id,tab2$condition))
tab2$residus <- resid(fit1j,type="normalized")
mat <- matrix(rep(0,nlevels(tab2$jour)*nlevels(tab2$combinaison)),ncol=nlevels(tab2$jour))
for(i in 1:nlevels(tab2$combinaison)){for(j in 1:nlevels(tab2$jour)){mat[i,j] <- tab2$residus[which(tab2$combinaison == levels(tab2$combinaison)[i] & tab2$jour == levels(tab2$jour)[j])]}}

pairs(mat)
cor(mat)




### structure effets fixes

# etape 1

fit_cj_c <- update(fit0,.~.-condition)

anova(fit0,fit_cj_c) # peut pas enlever la condition
# -> on garde fit_cj_j : on enlève la condition


# etape 3 : on a enlevé le plus petit des 2 (un à chaque étape), on regarde si on enlève le deuxième

#fit_cj_j_c <- update(fit_cj_j,.~.-condition)
#anova(fit_cj_j_c,fit_cj_j) # on enlève pas la condition




### validation du modele
# poser questions comment réécrire le modèle
mod_choisi <- lme(var.f~condition, random=~1|id,data=tab2, method="ML",na.action=na.exclude)


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
# écrit z-value, p-value)
comp_mult <- summary(glht(mod_choisi,linfct=mcp(condition="Tukey")))

