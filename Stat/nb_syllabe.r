###################################################### tableau de donnees #######################################
#10.06 : on garde m2
# nbSyll~jour*condition + (1|id) +(1|histoire),
# on garde l'interaction chisq(3)=52.713  p= 2.111e-11
### importer tableau 
setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("../Transcription/csvFiles/brutDebit.csv",sep=",",header=TRUE)


### type variable



tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))
tab$condition[tab$condition=="0"] <- "MAINS_LIBRES"
tab$condition[tab$condition=="1"] <- "MAINS_CONTRAINTES"
tab$condition[tab$condition=="2"] <- "PEDALAGE_PIEDS"
tab$condition[tab$condition=="3"] <- "PEDALAGE_MAINS"
tab$condition <- factor(tab$condition,levels = c("MAINS_LIBRES", "PEDALAGE_PIEDS", "PEDALAGE_MAINS","MAINS_CONTRAINTES"))
tab$condition <- as.factor(tab$condition)
tab$jour[tab$jour=="1"]<-"J1"
tab$jour[tab$jour=="2"]<-"J2"
tab$jour[tab$jour=="3"]<-"J3"
tab$jour <- as.factor(as.character(tab$jour))
### packages utilises

library(multcomp)
library(lsmeans) # library(emmeans)
library(lme4)
library(DHARMa)
library(ggplot2)

##################################################### statistiques descriptives #######################################


tgc <- summarySE(tab, measurevar="nbSyll", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=nbSyll, fill=condition)) + 
  scale_fill_brewer() + theme_bw() +
  geom_bar(position=position_dodge(), stat="identity",colour="black") +
  geom_errorbar(aes(ymin=tgc$nbSyll-tgc$se, ymax=tgc$nbSyll+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) 
#  ggtitle("Nombre de syllabes total")
p <- p + ylab("NB SYLL")+ labs(fill='CONDITION') +xlab("JOUR")
p<- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
              plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
              legend.title=element_text(size=18), legend.text = element_text(size=16))
p


##############" effet de l'histoire


# tgc <- summarySE(tab, measurevar="nbSyll", groupvars=c("jour","histoire"))
# p<-ggplot(data=tgc, aes(x=jour, y=nbSyll, fill=histoire)) +
#   geom_bar(position=position_dodge(), stat="identity") +
#   geom_errorbar(aes(ymin=tgc$nbSyll-tgc$se, ymax=tgc$nbSyll+tgc$se),
#                 width=.2,                    # Width of the error bars
#                 position=position_dodge(.9)) +
#   ggtitle("Nombre de syllabes par histoire")
# p <- p + ylab("Erreur")+ labs(fill='histoire')
# p<- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
#               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
#               legend.title=element_text(size=18), legend.text = element_text(size=16))
# p


###################################################### modelisation #######################################


### ecriture modele initial

m0 <- glmer(nbSyll~jour*condition + (1|id) +(1|histoire), family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))

### selecconditionon modele (effets aleatoires)
# etape 0


mstarth <- glmer(nbSyll~jour*condition + (1|id), family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))
sth <- getME(mstarth,c("theta","fixef"))
mh <- glmer(nbSyll~jour*condition + (1|id),start=sth, family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))
anova(m0,mstarth)


# etape 1

m1 <- glmer(nbSyll~jour*condition + (1|histoire)+(condition|id) , family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))
m2 <- glmer(nbSyll~jour*condition + (1|histoire)+(jour|id) , family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))

anova(m0,m1)
anova(m0,m2)
# garde + petit AIC et refait ?
#m3<-glmer(nbSyll~jour*condition + (histoire+jour+condition|id), family="poisson", data=tab)
mstart3<-glmer(nbSyll~jour*condition + (1|histoire)+(jour|id)+(condition|id), family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))
st3 <- getME(mstart3,c("theta","fixef"))
m3<-glmer(nbSyll~jour*condition + (1|histoire)+(jour|id)+(condition|id),start=st3, family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))
anova(m2,m3)
# on garde les 2 effets résiduels
# on garde m3 : variab inter-indiv # selon le jour et la condition (p-value,kh2)
# chisq(12)=459, p<0.0001
# si converge pas, garde m2

### selection modele (effets fixes)

# etape 1

m4_start<- glmer(nbSyll~jour+condition + (1|histoire)+(jour|id), family="poisson", data=tab)
st4<-getME(m4_start,c("theta","fixef"))
m4<- glmer(nbSyll~jour+condition + (1|histoire)+(jour|id), family="poisson", data=tab,start=st4)

anova(m2,m4) # on garde m2 : l'intéraction
# bizarre : pourquoi garde l'intéraction ?? pour certaines conditions, évolution différente entre les 2 jours
# évolution différente entre les 2 jours selon c

### validation modele (surdispersion) 

mod_choisi <- m2
simulationOutput <- simulateResiduals(fittedModel = mod_choisi, n = 1000)

plotSimulatedResiduals(simulationOutput = simulationOutput)
testUniformity(simulationOutput = simulationOutput)

plot(tab$nbSyll~fitted(mod_choisi))
abline(a=0,b=1,col="red")


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
contrmat[1,] <- patmat[1,] - patmat[3,] # j1 mains libres-velo pieds
contrmat[2,] <- patmat[1,] - patmat[5,] # j1 mains libres - velo mains .
contrmat[3,] <- patmat[1,] - patmat[7,] # j1 mains libres - mains contraintes

contrmat[4,] <- patmat[2,] - patmat[4,] # j1 mains libres-velo pieds
contrmat[5,] <- patmat[2,] - patmat[6,] # j1 mains libres - velo mains .
contrmat[6,] <- patmat[2,] - patmat[8,] # j1 mains libres - mains contraintes

contrmat[7,] <- patmat[3,] - patmat[4,] # progression pieds.
contrmat[8,] <- patmat[5,] - patmat[6,] # progression Vmains
contrmat[9,] <- patmat[1,] - patmat[2,] # progression mains L
contrmat[10,] <- patmat[7,] - patmat[8,] # progression mains C

contrmat <- lsmeans(mod_choisi, pairwise~condition|jour,glhargs=list())[[2]]$linfct
#comp_mult <- summary(glht(mod_choisi,linfct=contrmat)) # comp_mult <- emmeans(mod_choisi,pairwise~condition|jour)
comp_mult <- emmeans(mod_choisi,pairwise~condition|jour)

