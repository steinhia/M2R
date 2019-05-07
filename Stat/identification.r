###################################################### tableau de donnees #######################################


### importer tableau 
setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("../RecallTest/brut.csv",sep=",",header=TRUE)

###

#tab$evaluation <- as.character(tab$evaluation)
#tab$evaluation[tab$evaluation=="True"] <- "0"
#tab$evaluation[tab$evaluation=="False"] <- "1"
#tab$evaluation <- as.factor(tab$evaluation)

### type variable

tab$jour <- as.factor(as.character(tab$jour))
tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))
tab$condition <- as.factor(as.character(tab$condition))


### packages uconditionlises

library(lme4)
library(AUC)
library(multcomp)



###################################################### statistiques descriptives #######################################



tgc <- summarySE(tab, measurevar="evaluation", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=evaluation, fill=condition)) + 
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$evaluation-tgc$se, ymax=tgc$evaluation+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("Scores en identification")
p <- p + ylab("Erreur")+ labs(fill='condition') 
p<- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
              plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
              legend.title=element_text(size=18), legend.text = element_text(size=16))
p


###

table(tab$jour,tab$condition,tab$evaluation)


###################################################### modelisation #######################################

### ecriture modele initial


mstart0 <- glmer(evaluation~jour*condition + (1|id), family="binomial", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))

st0 <- getME(mstart0,c("theta","fixef"))

# modèle initial où garde tout (jour,cond,id)
m0 <- glmer(evaluation~jour*condition + (1|id) ,start=st0, family="binomial", data=tab,control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=50000)))


### selecconditionon modele (effets aleatoires)

# etape 1

mstart1 <- glmer(evaluation~jour*condition + (condition|id), family="binomial", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))
mstart2 <- glmer(evaluation~jour*condition + (jour|id), family="binomial", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))

st1 <- getME(mstart1,c("theta","fixef"))
st2 <- getME(mstart2,c("theta","fixef"))

m1 <- glmer(evaluation~jour*condition + (condition|id),start=st1 , family="binomial", data=tab,control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=50000)))
m2 <- glmer(evaluation~jour*condition + (jour|id),start=st2 , family="binomial", data=tab,control=glmerControl(optimizer="bobyqa",optCtrl=list(maxfun=50000)))

anova(m0,m1)
anova(m0,m2)



### selecconditionon modele (effets fixes)

# etape 1

m3 <- glmer(evaluation~jour+condition + (1|id), family="binomial", data=tab)
anova(m0,m3)


# etape 2

m4 <- glmer(evaluation~jour + (1|id), family="binomial", data=tab)
m5 <- glmer(evaluation~condition + (1|id), family="binomial", data=tab)

anova(m3,m4)
anova(m3,m5)



### taux d'erreur + courbe roc

mod_choisi <- glmer(evaluation~jour + (1|id) , data=tab, family="binomial",control=glmerControl(optCtrl=list(maxfun=50000)))
prevision_prob <- predict(mod_choisi, newdata=tab, type="response")
prevision_label <- as.numeric(prevision_prob>0.5)

mat_conf <- table(tab$evaluation, prevision_label)
tx_erreur <- (mat_conf[1,2] + mat_conf[2,1])/nrow(tab)

pred <- roc( prevision_prob, tab$evaluation)
plot(pred)
auc(pred)


### comparaisons mulconditionples

patmat <- rbind(c(1,0,0),c(1,1,0),c(1,0,1))
rownames(patmat) <- c("jour1","jour2","jour3")

contrmat <- matrix(rep(0,3*3),ncol=3)
rownames(contrmat) <- c("jour1 - jour2","jour1-jour3","jour2-jour3")
contrmat[1,] <- patmat[1,] - patmat[2,]
contrmat[2,] <- patmat[1,] - patmat[3,]
contrmat[3,] <- patmat[2,] - patmat[3,]

comp_mult <- summary(glht(mod_choisi,linfct=contrmat))
