###################################################### tableau de donnees #######################################
# nu   score~(re(random = ~1 | id)) 
# tau  score~jour + (re(random = ~1 | id)) 
# mu   score ~ jour 

### importer tableau 
setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("../Transcription/csvFiles/brutTranscriptionCT.csv",sep=",",header=TRUE)
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

### 
#tab$score <- as.factor(tab$score)
#tab$score <- tab$score/3


### packages utilises

library(gamlss)
library(ggplot2)


###################################################### statistiques descriptives #######################################

tgc <- summarySE(tab, measurevar="score", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=score, fill=condition)) + 
  scale_fill_brewer() + theme_bw() +
  geom_bar(position=position_dodge(), stat="identity",colour="black") +
  geom_errorbar(aes(ymin=tgc$score-tgc$se, ymax=tgc$score+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) 
#  ggtitle("score moyen en rappel libre à court terme")
p <- p + ylab("RAPPEL LIBRE CT")+ labs(fill='CONDITION') +xlab("JOUR")+ylim(0,1)
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
              plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
              legend.title=element_text(size=18), legend.text = element_text(size=16))
p


############## effet de l'histoire ##############""

tgc <- summarySE(tab, measurevar="score", groupvars=c("jour","histoire"))
p<-ggplot(data=tgc, aes(x=jour, y=score, fill=histoire)) + 
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$score-tgc$se, ymax=tgc$score+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("scores en dénomination par histoire")
p <- p + ylab("score")+ labs(fill='histoire') 
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
p

#########################################################

### P(score==0)

tab$score4 <- as.character(tab$score) 
tab$score4[tab$score4 != "0"] <- "autre"
tab$score4 <- as.factor(as.character(tab$score4))
prop.table(table(tab$score4,tab$condition),2)
prop.table(table(tab$score4,tab$jour),2)



### P(score==1)

tab$score3 <- as.character(tab$score) 
tab$score3[tab$score3 != "1"] <- "autre"
tab$score3 <- as.factor(as.character(tab$score3))
prop.table(table(tab$score3,tab$condition),2)
prop.table(table(tab$score3,tab$jour),2)





###################################################### modelisation #######################################


### ecriture modele

mod <- gamlss(score~jour*condition+ re(random=~1|id) ,nu.formula = ~jour*condition+ re(random=~1|id), tau.formula = ~jour*condition+ re(random=~1|id),family=BEINF,data=tab)


### selection modele

mod_choisi_nu <- stepGAIC(mod, scope=list(lower=~1,upper=~jour*condition + re(random=~1|id)),what=c("nu"))
mod_choisi_nu_tau <- stepGAIC(mod_choisi_nu, scope=list(lower=~1,upper=~jour*condition + re(random=~1|id)),what=c("tau"))
mod_choisi_nu_tau_mu <- stepGAIC(mod_choisi_nu_tau, scope=list(lower=~1,upper=~jour*condition + re(random=~1|id)),what=c("mu"))
# nu   score~(re(random = ~1 | id)) 774.84
# tau  score~jour + (re(random = ~1 | id))  774.84
# mu   score ~ jour 752.98

### validation modele

mod_choisi <- gamlss(score~jour ,nu.formula = re(random = ~1 | id) , tau.formula = jour + re(random = ~1 | id) ,family=BEINF,data=tab)
plot(mod_choisi)
Rsq(mod_choisi)


### comparaisons 

tab$jour <- relevel(tab$jour, ref="J1")
tab$condition <- relevel(tab$condition, ref="MAINS_LIBRES")
mod_choisi <- gamlss(score~jour ,nu.formula = ~jour+ re(random=~1|id), tau.formula = ~jour+ re(random=~1|id),family=BEINF,data=tab)
summary(mod_choisi)
