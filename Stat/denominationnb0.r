###################################################### tableau de donnees #######################################


### importer tableau 
setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("brutResume.csv",sep=",",header=TRUE)
### type variable

tab$jour <- as.factor(as.character(tab$jour))
tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))
tab$condition[tab$condition=="0"] <- "mains libres"
tab$condition[tab$condition=="1"] <- "mains contraintes"
tab$condition[tab$condition=="2"] <- "pédalage pieds"
tab$condition[tab$condition=="3"] <- "pédalage mains"
tab$condition <- factor(tab$condition,levels = c("mains libres", "mains contraintes", "pédalage mains", "pédalage pieds"))
tab$condition <- as.factor(tab$condition)

### packages utilises

library(gamlss)
library(ggplot2)


###################################################### statistiques descriptives #######################################


############################# nb0 #######################

tgc <- summarySE(tab, measurevar="nb0", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=nb0, fill=condition)) + 
  scale_fill_brewer() + theme_bw() +
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$nb0-tgc$se, ymax=tgc$nb0+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) 
  ggtitle("nb0s en dénomination")
p <- p + ylab("nb0")+ labs(fill='condition') 
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
              plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
              legend.title=element_text(size=18), legend.text = element_text(size=16))
p

############################# nb1 #######################

tgc <- summarySE(tab, measurevar="nb1", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=nb1, fill=condition)) + 
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$nb1-tgc$se, ymax=tgc$nb1+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("nb1s en dénomination")
p <- p + ylab("nb1")+ labs(fill='condition') 
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
p


############## effet de l'histoire énorme !!!! ##############""

tgc <- summarySE(tab, measurevar="nb1", groupvars=c("jour","histoire"))
p<-ggplot(data=tgc, aes(x=jour, y=nb1, fill=histoire)) + 
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$nb1-tgc$se, ymax=tgc$nb1+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("nb1s en dénomination par histoire")
p <- p + ylab("nb1")+ labs(fill='histoire') 
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
p

#########################################################

### P(nb0==0)

tab$nb04 <- as.character(tab$nb0) 
tab$nb04[tab$nb04 != "0"] <- "autre"
tab$nb04 <- as.factor(as.character(tab$nb04))
prop.table(table(tab$nb04,tab$condition),2)
prop.table(table(tab$nb04,tab$jour),2)



### P(nb0==1)

tab$nb03 <- as.character(tab$nb0) 
tab$nb03[tab$nb03 != "1"] <- "autre"
tab$nb03 <- as.factor(as.character(tab$nb03))
prop.table(table(tab$nb03,tab$condition),2)
prop.table(table(tab$nb03,tab$jour),2)





###################################################### modelisation #######################################


### ecriture modele

mod <- gamlss(nb0~jour*condition+ re(random=~1|id) ,nu.formula = ~jour*condition+ re(random=~1|id), tau.formula = ~jour*condition+ re(random=~1|id),family=BEINF,data=tab)


### selection modele

mod_choisi_nu <- stepGAIC(mod, scope=list(lower=~1,upper=~jour*condition + re(random=~1|id)),what=c("nu"))
mod_choisi_nu_tau <- stepGAIC(mod_choisi_nu, scope=list(lower=~1,upper=~jour*condition + re(random=~1|id)),what=c("tau"))
mod_choisi_nu_tau_mu <- stepGAIC(mod_choisi_nu_tau, scope=list(lower=~1,upper=~jour*condition + re(random=~1|id)),what=c("mu"))


### validation modele

mod_choisi <- gamlss(nb0~jour+condition+ re(random=~1|id) ,nu.formula = ~jour+ re(random=~1|id), tau.formula = ~jour+condition+ re(random=~1|id),family=BEINF,data=tab)
plot(mod_choisi)
Rsq(mod_choisi)


### comparaisons 

tab$jour <- relevel(tab$jour, ref="1")
tab$condition <- relevel(tab$condition, ref="3")
mod_choisi <- gamlss(nb0~jour+condition+ re(random=~1|id) ,nu.formula = ~jour+ re(random=~1|id), tau.formula = ~jour+condition+ re(random=~1|id),family=BEINF,data=tab)
summary(mod_choisi)
