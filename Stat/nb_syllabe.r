###################################################### tableau de donnees #######################################

# TODO : bizarre, pourquoi effet d'intéraction? fonction not defined
### importer tableau 
setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("../Transcription/brutDebit.csv",sep=",",header=TRUE)


### type variable

tab$jour <- as.factor(as.character(tab$jour))
tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))
tab$condition[tab$condition=="0"] <- "mains libres"
tab$condition[tab$condition=="1"] <- "mains contraintes"
tab$condition[tab$condition=="2"] <- "pédalage pieds"
tab$condition[tab$condition=="3"] <- "pédalage mains"
tab$condition <- factor(tab$condition,levels = c("mains libres", "pédalage pieds", "pédalage mains","mains contraintes"))

tab$condition <- as.factor(tab$condition)

### packages utilises

library(multcomp)
library(lsmeans) # library(emmeans)
library(lme4)
#library(DHARMa)


###################################################### statistiques descriptives #######################################


tgc <- summarySE(tab, measurevar="nbSyll", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=nbSyll, fill=condition)) + 
  scale_fill_brewer() + theme_bw() +
  geom_bar(position=position_dodge(), stat="identity",colour="black") +
  geom_errorbar(aes(ymin=tgc$nbSyll-tgc$se, ymax=tgc$nbSyll+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("Nombre de syllabes total \n par jour et condition")
p <- p + ylab("nombre de syllabes")+ labs(fill='condition') 
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

m0 <- glmer(nbSyll~jour*condition + (1|id) , family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))

### selecconditionon modele (effets aleatoires)

# etape 1

m1 <- glmer(nbSyll~jour*condition + (condition|id) , family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))
m2 <- glmer(nbSyll~jour*condition + (jour|id) , family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))

anova(m0,m1)
anova(m0,m2)
# garde + petit AIC et refait ?
m3<-glmer(nbSyll~jour*condition + (jour+condition|id), family="poisson", data=tab)
anova(m2,m3)
# on garde les 2 effets résiduels



### selection modele (effets fixes)

# etape 1

m4<- glmer(nbSyll~jour+condition + (jour+condition|id), family="poisson", data=tab)
anova(m3,m4) # on garde m3 : l'intéraction
# bizarre : pourquoi garde l'intéraction ??


### validation modele (surdispersion) 

mod_choisi <- m3
simulationOutput <- simulateResiduals(fittedModel = mod_choisi, n = 1000)

plotSimulatedResiduals(simulationOutput = simulationOutput)
testUniformity(simulationOutput = simulationOutput)

plot(tab$nbSyll~fitted(mod_choisi))
abline(a=0,b=1,col="red")


### comparaison multiples 

contrmat <- lsmeans(mod_choisi, pairwise~condition|jour,glhargs=list())[[2]]$linfct
comp_mult <- summary(glht(mod_choisi,linfct=contrmat)) # comp_mult <- emmeans(mod_choisi,pairwise~condition|jour)

