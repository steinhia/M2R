###################################################### tableau de donnees #######################################
# pas d'effet dans les comparaisons multiples mais effet jour condition : on fait quelles stats
# effet du type mais pas monstrueux
### importer tableau 
setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("../RecallTest/brut.csv",sep=",",header=TRUE)


tab$jour <- as.factor(as.character(tab$jour))
tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))

tab$condition[tab$condition=="0"] <- "mains libres"
tab$condition[tab$condition=="1"] <- "mains contraintes"
tab$condition[tab$condition=="2"] <- "pédalage pieds"
tab$condition[tab$condition=="3"] <- "pédalage mains"
tab$condition <- factor(tab$condition,levels = c("mains libres", "pédalage pieds", "pédalage mains","mains contraintes"))
tab$condition <- as.factor(tab$condition)
### packages uconditionlises

library(lme4)
library(AUC)
library(multcomp)
library(ggplot2)
library(psy)

# + = 2 effets, * = intéraction
################# effet condition  #####################
tgc <- summarySE(tab, measurevar="evaluation", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=evaluation, fill=condition)) + 
  scale_fill_brewer() + theme_bw() +
  scale_fill_brewer() + theme_bw() +
  geom_bar(position=position_dodge(), stat="identity",colour="black") +
 geom_errorbar(aes(ymin=tgc$evaluation-tgc$se, ymax=tgc$evaluation+tgc$se),
             width=.2,                    # Width of the error bars
            position=position_dodge(.9)) +
 ggtitle("Scores en identification")
p <- p + ylab("Scores")+ labs(fill='condition')
p<- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
              plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
              legend.title=element_text(size=18), legend.text = element_text(size=16))
# p<- p+facet_grid(.~type)
p

a<- tab$id
b<- tab$evaluation
tab2=data.table(id=a,evaluation=b)
df=as.data.frame.matrix(tab2)
cronbach(df)

################## effet de l'histoire #############

# tgc <- summarySE(tab, measurevar="evaluation", groupvars=c("jour","histoire"))
# p<-ggplot(data=tgc, aes(x=jour, y=evaluation, fill=histoire)) + 
#   geom_bar(position=position_dodge(), stat="identity") +
#   geom_errorbar(aes(ymin=tgc$evaluation-tgc$se, ymax=tgc$evaluation+tgc$se),
#                 width=.2,                    # Width of the error bars
#                 position=position_dodge(.9)) +
#   ggtitle("Effet de l'histoire sur l'identification")
# p <- p + ylab("Scores")+ labs(fill='histoire')
# p<- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
#               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
#               legend.title=element_text(size=18), legend.text = element_text(size=16))
# p


###

table(tab$jour,tab$condition,tab$evaluation)


###################################################### modelisation #######################################

### ecriture modele initial


mstart0 <- glmer(evaluation~jour*condition + (1|id), family="binomial", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))

st0 <- getME(mstart0,c("theta","fixef"))

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
anova(m0,m2) # on garde m2



### selecconditionon modele (effets fixes)

# etape 1
# doit écrire m2 + modif -> on garde jour|id, on teste intéraction
mstart3 <- glmer(evaluation~jour+condition + (jour|id), family="binomial", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))
st3 <- getME(mstart3,c("theta","fixef"))
m3 <- glmer(evaluation~jour+condition + (jour|id), family="binomial", data=tab, ,control=glmerControl(optCtrl=list(maxfun=50000)),start=st3)
anova(m2,m3) # on garde m3 
# pb convergence -> garde terme d'intéraction -> doute : vérifie dans compar multiples


# etape 2

# m4 <- glmer(evaluation~jour + (1|id), family="binomial", data=tab)
# m5 <- glmer(evaluation~condition + (1|id), family="binomial", data=tab)
# 
# anova(m2,m4)
# anova(m2,m5)



### taux d'erreur + courbe roc

mod_choisi <- m2#glmer(evaluation~jour + (1|id) , data=tab, family="binomial",control=glmerControl(optCtrl=list(maxfun=50000)))
prevision_prob <- predict(mod_choisi, newdata=tab, type="response")
prevision_label <- as.numeric(prevision_prob>0.5)

mat_conf <- table(tab$evaluation, prevision_label)
tx_erreur <- (mat_conf[1,2] + mat_conf[2,1])/nrow(tab) # 80% 

pred <- roc( prevision_prob, tab$evaluation)
plot(pred)
auc(pred)


### comparaisons mulconditionples
# avant chgt
# patmat <- rbind(c(1,0,0,0,0,0,0,0,0,0,0,0),c(1,1,0,0,0,0,0,0,0,0,0,0), c(1,0,1,0,0,0,0,0,0,0,0,0),
#                 c(1,0,0,1,0,0,0,0,0,0,0,0),c(1,1,0,1,0,0,1,0,0,0,0,0), c(1,0,1,1,0,0,0,1,0,0,0,0),
#                 c(1,0,0,0,1,0,0,0,0,0,0,0),c(1,1,0,0,1,0,0,0,1,0,0,0), c(1,0,1,0,1,0,0,0,0,1,0,0),
#                 c(1,0,0,0,0,1,0,0,0,0,0,0),c(1,1,0,0,0,1,0,0,0,0,1,0), c(1,0,1,0,0,1,0,0,0,0,0,1)) # donne valeur à chaque cellule
# rownames(patmat) <- c("jour1-Contrainte","jour2-Contrainte","jour3-Contrainte",
#                       "jour1-Libre","jour2-Libre","jour3-Libre",
#                       "jour1-Mains","jour2-Mains","jour3-Mains",
#                       "jour1-Pieds","jour2-Pieds","jour3-Pieds"
#                       ) # doit tout définir

# maintenant

patmat <- rbind(c(1,0,0,1,0,0,0,0,0,0,0,0),c(1,1,0,1,0,0,1,0,0,0,0,0), c(1,0,1,1,0,0,0,1,0,0,0,0),
                c(1,0,0,0,0,1,0,0,0,0,0,0),c(1,1,0,0,0,1,0,0,0,0,1,0), c(1,0,1,0,0,1,0,0,0,0,0,1),
                c(1,0,0,0,1,0,0,0,0,0,0,0),c(1,1,0,0,1,0,0,0,1,0,0,0), c(1,0,1,0,1,0,0,0,0,1,0,0),
                c(1,0,0,0,0,0,0,0,0,0,0,0),c(1,1,0,0,0,0,0,0,0,0,0,0), c(1,0,1,0,0,0,0,0,0,0,0,0))


# donne valeur à chaque cellule
rownames(patmat) <- c("jour1-Libre","jour2-Libre","jour3-Libre",
                      "jour1-Pieds","jour2-Pieds","jour3-Pieds",
                      "jour1-Mains","jour2-Mains","jour3-Mains",
                      "jour1-Contrainte","jour2-Contrainte","jour3-Contrainte")



# comparaisons multiples
contrmat <- matrix(rep(0,12*3),ncol=12) # nbCol*nb Compar qu'on veut faire
rownames(contrmat) <- c("j1C - j1L","j1M-j1P")

# # comparaisons j1
contrmat[1,] <- patmat[1,] - patmat[4,] # j1 mains libres-contraintes *
contrmat[2,] <- patmat[7,] - patmat[4,] # j1 mains libres - velo mains .
contrmat[3,] <- patmat[10,] - patmat[4,] # j1 mains libres - velo pieds -> pas significatif

# # comparaisons j2
# contrmat[4,] <- patmat[2,] - patmat[5,] # j1 mains libres-contraintes *
# contrmat[5,] <- patmat[8,] - patmat[5,] # j1 mains libres - velo mains .
# contrmat[6,] <- patmat[11,] - patmat[5,] # j1 mains libres - velo pieds -> pas significatif

# comparaisons j3
# contrmat[1,] <- patmat[3,] - patmat[6,] # j1 mains libres-contraintes *
# contrmat[2,] <- patmat[9,] - patmat[6,] # j1 mains libres - velo mains .
# contrmat[3,] <- patmat[12,] - patmat[6,] # j1 mains libres - velo pieds -> pas significatif

# contrmat[1,]<-(patmat[4,]+patmat[5,]+patmat[6,])-(patmat[1,]+patmat[2,]+patmat[3,])
# contrmat[2,]<-(patmat[4,]+patmat[5,]+patmat[6,])-(patmat[7,]+patmat[8,]+patmat[9,])
# contrmat[3,]<-(patmat[4,]+patmat[5,]+patmat[6,])-(patmat[10,]+patmat[11,]+patmat[12,])

# comparaison j2-j3
#contrmat[10,]<-(patmat[2,]+patmat[5,]+patmat[8,]+patmat[11,])-(patmat[3,]+patmat[6,]+patmat[9,]+patmat[12,])

# 4*3 pour les jours ou juste j2 j3
# 18 au sein d'un jour
# -> peut enlever entre j1 et j2
# Amélie : pourquoi a tout teste


comp_mult <- summary(glht(mod_choisi,linfct=contrmat,adjust.method="none"))
# % autres études que j1
