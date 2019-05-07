###################################################### tableau de donnees #######################################


### importer tableau 

setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("../RecallTest/brut.csv",sep=",",header=TRUE)


### type variable

tab$jour <- as.factor(as.character(tab$jour))
tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))

tab$condition[tab$condition=="0"] <- "mains libres"
tab$condition[tab$condition=="1"] <- "mains contraintes"
tab$condition[tab$condition=="2"] <- "pédalage pieds"
tab$condition[tab$condition=="3"] <- "pédalage mains"
tab$condition <- as.factor(tab$condition)


### 

tab$distance2 <- tab$distance/10


### packages utilises

library(gamlss)



tgc <- summarySE(tab, measurevar="distance2", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=distance2, fill=condition)) + 
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$distance2-tgc$se, ymax=tgc$distance2+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("Scores en dénomination")
p <- p + ylab("Erreur")+ labs(fill='condition') 
p<- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
              plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
              legend.title=element_text(size=18), legend.text = element_text(size=16))
p







# distance 2 = ramené entre 0 et 1


### P(distance==0)

tab$distance4 <- as.character(tab$distance2) 
tab$distance4[tab$distance4 != "0"] <- "autre"
tab$distance4 <- as.factor(as.character(tab$distance4))
prop.table(table(tab$distance4,tab$condition),2)
prop.table(table(tab$distance4,tab$jour),2)



### P(distance==1)

tab$distance3 <- as.character(tab$distance2) 
tab$distance3[tab$distance3 != "1"] <- "autre"
tab$distance3 <- as.factor(as.character(tab$distance3))
prop.table(table(tab$distance3,tab$condition),2)
prop.table(table(tab$distance3,tab$jour),2)





###################################################### modelisation #######################################


### ecriture modele

mod <- gamlss(distance2~jour*condition+ re(random=~1|id) ,nu.formula = ~jour*condition+ re(random=~1|id), tau.formula = ~jour*condition+ re(random=~1|id),family=BEINF,data=tab)


### selection modele
# 3 cas 0, 1 ou autre
# AIC = mesure qualité/parcimonie du modèle -> choisit le plus faible AIC
mod_choisi_nu <- stepGAIC(mod, scope=list(lower=~1,upper=~jour*condition + re(random=~1|id)),what=c("nu"))
mod_choisi_nu_tau <- stepGAIC(mod_choisi_nu, scope=list(lower=~1,upper=~jour*condition + re(random=~1|id)),what=c("tau"))
mod_choisi_nu_tau_mu <- stepGAIC(mod_choisi_nu_tau, scope=list(lower=~1,upper=~jour*condition + re(random=~1|id)),what=c("mu"))


### validation modele

mod_choisi <- gamlss(distance2~jour+condition+ re(random=~1|id) ,nu.formula = ~jour+ re(random=~1|id), tau.formula = ~jour+condition+ re(random=~1|id),family=BEINF,data=tab)
plot(mod_choisi)
Rsq(mod_choisi)


### comparaisons 

tab$jour <- relevel(tab$jour, ref="1")
tab$condition <- relevel(tab$condition, ref="3")
mod_choisi <- gamlss(distance2~jour+condition+ re(random=~1|id) ,nu.formula = ~jour+ re(random=~1|id), tau.formula = ~jour+condition+ re(random=~1|id),family=BEINF,data=tab)
summary(mod_choisi)
