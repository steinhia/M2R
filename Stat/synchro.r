###################################################### tableau de donnees #######################################
### importer tableau 

library(data.table)
setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("brutResume.csv",sep=",",header=TRUE)

tab$jour[tab$jour=="1"]<-"J1"
tab$jour[tab$jour=="2"]<-"J2"
tab$jour[tab$jour=="3"]<-"J3"
tab$jour <- as.factor(as.character(tab$jour))
tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))


############## jours ensemble ###################

 a<- tab$jour[which(tab$condition=="2")] 
 b<- tab$condition[which(tab$condition=="2")] 
 c<- tab$id[which(tab$condition=="2")] 
 d<- tab$freq.moy.pédalage[which(tab$condition=="2")] 
 e<- tab$debit.moyen[which(tab$condition=="2")] 
 f<- tab$variance.pédalage[which(tab$condition=="2")] 
 g<- tab$variance.debit[which(tab$condition=="2")] 
 tab3=data.table(jour=a,condition=b,freq.moy.pedalage=d,id=c,debit.moyen=e,variance.pédalage=f,variance.debit=g)
 tab3$condition<-as.factor(tab3$condition)

 a<- tab$jour[which(tab$condition=="3")] 
 b<- tab$condition[which(tab$condition=="3")] 
 c<- tab$id[which(tab$condition=="3")] 
 d<- tab$freq.moy.pédalage[which(tab$condition=="3")] 
 e<- tab$debit.moyen[which(tab$condition=="3")] 
 f<- tab$variance.pédalage[which(tab$condition=="3")] 
 g<- tab$variance.debit[which(tab$condition=="3")] 
 tab4=data.table(jour=a,condition=b,freq.moy.pedalage=d,id=c,debit.moyen=e,variance.pédalage=f,variance.debit=g)
 tab4$condition<-as.factor(tab3$condition)

 
 cor.test(tab3$debit.moyen,tab3$freq.moy.pedalage,method='spearman') # pieds
 cor.test(tab4$debit.moyen,tab4$freq.moy.pedalage,method='spearman') # mains
 
 cor.test(tab3$variance.debit,tab3$variance.pédalage,method='spearman') # pieds
 cor.test(tab4$variance.debit,tab4$variance.pédalage,method='spearman') # mains
 
 
################# on sépare par jour #################################
 
 c<- tab$id[which(tab$condition=="2"& tab$jour=="J1")] 
 d<- tab$freq.moy.pédalage[which(tab$condition=="2"& tab$jour=="J1")] 
 e<- tab$debit.moyen[which(tab$condition=="2"& tab$jour=="J1")] 
 tab5=data.table(jour=a,condition=b,freq.moy.pedalage=d,id=c,debit.moyen=e)
 cor.test(tab5$debit.moyen,tab5$freq.moy.pedalage,method='spearman') # pieds

 c<- tab$id[which(tab$condition=="2"& tab$jour=="J2")] 
 d<- tab$freq.moy.pédalage[which(tab$condition=="2"& tab$jour=="J2")] 
 e<- tab$debit.moyen[which(tab$condition=="2"& tab$jour=="J2")] 
 tab6=data.table(jour=a,condition=b,freq.moy.pedalage=d,id=c,debit.moyen=e)
 cor.test(tab6$debit.moyen,tab6$freq.moy.pedalage,method='spearman') # pieds
 
 
 c<- tab$id[which(tab$condition=="3"& tab$jour=="J1")] 
 d<- tab$freq.moy.pédalage[which(tab$condition=="3"& tab$jour=="J1")] 
 e<- tab$debit.moyen[which(tab$condition=="3"& tab$jour=="J1")] 
 tab7=data.table(jour=a,condition=b,freq.moy.pedalage=d,id=c,debit.moyen=e)
 cor.test(tab7$debit.moyen,tab7$freq.moy.pedalage,method='spearman') # pieds
 
 c<- tab$id[which(tab$condition=="3"& tab$jour=="J2")] 
 d<- tab$freq.moy.pédalage[which(tab$condition=="3"& tab$jour=="J2")] 
 e<- tab$debit.moyen[which(tab$condition=="3"& tab$jour=="J2")] 
 tab8=data.table(jour=a,condition=b,freq.moy.pedalage=d,id=c,debit.moyen=e)
 cor.test(tab8$debit.moyen,tab8$freq.moy.pedalage,method='spearman') # pieds
 
 
############################################################ 
 
 
# b<- tab$freq.moy.pédalage[which(tab$jour!='J3' & (tab$condition=="2" | tab$condition=="3"))] 
# c<- tab$debit.moyen[which(tab$jour!='J3' & (tab$condition=="2" | tab$condition=="3"))] 
# d<- tab$condition[which(tab$jour!='J3' & (tab$condition=="2" | tab$condition=="3"))] 
# e<- tab$id[which(tab$jour!='J3' & (tab$condition=="2" | tab$condition=="3"))] 
# tab2=data.table(jour=a,condition=d,freq.moy.pedalage=b,id=e,debit.moyen=c)
# tab2$condition[tab2$condition=="2"] <- "pédalage pieds"
# tab2$condition[tab2$condition=="3"] <- "pédalage mains"
# tab2$condition <- factor(tab$condition,levels = c("pédalage pieds", "pédalage mains"))


tab$condition[tab$condition=="0"] <- "mains libres"
tab$condition[tab$condition=="1"] <- "mains contraintes"
tab$condition[tab$condition=="2"] <- "pédalage pieds"
tab$condition[tab$condition=="3"] <- "pédalage mains"
tab$condition <- factor(tab$condition,levels = c("pédalage pieds", "pédalage mains","mains libres","mains contraintes"))
tab$nb <- tab$nbCycles.parole.mocap
#tab$nb <- as.factor(tab$nb)
tab$varNMocap<- tab$variance.pédalage/tab$freq.moy.pédalage
tab$var<-tab$variance.debit/tab$debit.moyen





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


b <- ggplot(tab, aes(x = tab$debit.moyen, y=tab$mean_ped_rl, colour=tab$condition, shape=tab$condition))
b<- b + geom_point(size=4) # rajouter y dans le ggplot de base
#b<- b+geom_smooth(method = "lm")
#b <-b + geom_text(x = 2, y = 4, label = lm_eqn(tab,tab$debit.moyen,tab$freq.moy.pédalage), parse = TRUE)
b <- b + ylab("fréquence moyenne de pédalage")+ xlab("débit moyen") 
b<- b+facet_grid(.~jour)
b


cor.test(tab$debit.moyen,tab$freq.moy.pédalage,method='spearman')


















# yp nulle : coeff coerrelation=0 (pas correl) -> rejette pas
# p-value : rejette pas l'hypothèse nulle
# rho : valeur estimée du coefficient de corrélation

b <- ggplot(tab, aes(x = tab$variance.debit, y=tab$variance.pédalage, colour=tab$condition, shape=tab$condition))
b<- b + geom_point(size=4) # rajouter y dans le ggplot de base
#b<- b+geom_smooth(method = "lm")
#b <-b + geom_text(x = 2, y = 4, label = lm_eqn(tab,tab$debit.moyen,tab$freq.moy.pédalage), parse = TRUE)
b <- b + ylab("variance de la fréquence de pédalage")+ xlab("variance du débit") 
b<- b+facet_grid(.~jour)
b
cor.test(tab$variance.debit,tab$variance.pédalage,method='spearman')


cor.test(tab2$var.f,tab2$varz,method='spearman')
###################################################### statistiques descriptives #######################################

tgc <- summarySE(tab, measurevar="nb", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=nb, fill=condition)) + 
  scale_fill_brewer() + theme_bw() +
  geom_bar(position=position_dodge(), stat="identity",colour="black") +
  geom_errorbar(aes(ymin=tgc$nb-tgc$se, ymax=tgc$nb+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) 
#  ggtitle("Rapport entre le débit et la vitesse de pédalage")
p <- p + ylab("débit/pédalage")+ labs(fill='condition') 
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
p

##############" effet de l'histoire ########"""

tgc <- summarySE(tab, measurevar="nb", groupvars=c("jour","histoire"))
p<-ggplot(data=tgc, aes(x=jour, y=nb, fill=histoire)) + 
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$nb-tgc$se, ymax=tgc$nb+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("Débit moyen selon le jour et la condition")
p <- p + ylab("débit moyen")+ labs(fill='histoire') 
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
p

### distribution

hist(tab$nb)




###################################################### modelisation #######################################

### structure effets aleatoires

# un effet aleatoire intercept par sujet

fit0 <-  lme(nb~jour*condition, random=~1|id,data=tab, method="ML",na.action=na.exclude)
plot(fit0, id~resid(.,type="p")|jour, abline=0, xlim=c(-5,5), xlab="residus standardises")
plot(fit0, id~resid(.,type="p")|condition, abline=0, xlim=c(-5,5), xlab="residus standardises")


## etape 1


# un effet aleatoire intercept par sujet different par condition

fit1c <- lme(nb~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~condition-1)))),data=tab, method="ML",na.action=na.exclude)
fit1j <- lme(nb~jour*condition, random=list(id=pdBlocked(list(pdIdent(~1),pdIdent(~jour-1)))),data=tab, method="ML",na.action=na.exclude)

anova(fit0,fit1c)
anova(fit0,fit1j)


### matrice de variance covariance des erreurs

# meme variance selon les modalites de condition

boxplot(resid(fit0,type="p")~tab$condition, xlab="residus normalises")
boxplot(resid(fit0,type="p")~tab$jour, xlab="residus normalises")

fit_varc <- lme(nb~jour*condition, random=~1|id,weights=varIdent(form=~1|condition),data=tab, method="ML",na.action=na.exclude)
anova(fit0,fit_varc)

fit_varj <- lme(nb~jour*condition, random=~1|id,weights=varIdent(form=~1|jour),data=tab, method="ML",na.action=na.exclude)
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

mod_choisi <- lme(nb~1, random=~1|id,weights=varIdent(form=~1|jour),data=tab, method="ML",na.action=na.exclude)


# calcul des r?sidus du model 1 avec interaction

resmod_choisi.std<-resid(mod_choisi,type="normalized",level=1)

# plot residuals

hist(resmod_choisi.std,breaks=15,freq=FALSE,xlab="Standardized residuals", main="Histogram of the standardized residuals")
lines(density(resmod_choisi.std))

qqnorm(resmod_choisi.std,main = 'Normal QQplot of the standardized residuals \n of the log model')
qqline(resmod_choisi.std)

plot(resmod_choisi.std~fitted(mod_choisi),xlab="Fitted values", ylab="Standardized residuals", main="Standardized residuals vs fitted values")
abline(a=0,b=0)




