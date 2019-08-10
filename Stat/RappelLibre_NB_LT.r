###################################################### tableau de donnees #######################################


### importer tableau 
setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("../Transcription/csvFiles/brutTranscriptionLT.csv",sep=",",header=TRUE)
### type variable

tab$jour <- as.factor(as.character(tab$jour))
tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))
tab$score <- as.character(tab$score)
tab$condition[tab$condition=="0"] <- "MAINS_LIBRES"
tab$condition[tab$condition=="1"] <- "MAINS_CONTRAINTES"
tab$condition[tab$condition=="2"] <- "PEDALAGE_PEDS"
tab$condition[tab$condition=="3"] <- "PEDALAGE_MAINS"
tab$condition <- factor(tab$condition,levels = c("MAINS_LIBRES", "PEDALAGE_PEDS", "PEDALAGE_MAINS","MAINS_CONTRAINTES"))
tab$condition <- as.factor(tab$condition)
tab$nb0<-as.numeric((tab$score)=='0')
#tab$score_cumulé <- as.factor(as.character(tab$score_cumulé))
### )
#tab$score <- as.factor(tab$score)
#tab$score <- tab$score/3


### packages utilises

library(gamlss)
library(ggplot2)


###################################################### statistiques descriptives #######################################
# calcul du nombre de 0







tgc <- summarySE(tab, measurevar="nbRepet", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=nbRepet, fill=condition)) + 
  scale_fill_brewer() + theme_bw() +
  geom_bar(position=position_dodge(), stat="identity",colour="black") +
  geom_errorbar(aes(ymin=tgc$nbRepet-tgc$se, ymax=tgc$nbRepet+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) 
 # ggtitle("Nombre de répétitions des pseudo-mots \n  en rappel libre à long terme")
p <- p + ylab("Score")+ labs(fill='condition') 
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
              plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
              legend.title=element_text(size=18), legend.text = element_text(size=16))
p

tgc <- summarySE(tab, measurevar="nb0", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=nb0, fill=condition)) + 
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$nb0-tgc$se, ymax=tgc$nb0+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("Nombre de répétitions des pseudo-mots \n  en rappel libre à long terme")
p <- p + ylab("Score")+ labs(fill='condition') 
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
p

############# effet de l'histoire ###############

# tgc <- summarySE(tab, measurevar="nbRepet", groupvars=c("jour","histoire"))
# p<-ggplot(data=tgc, aes(x=jour, y=nbRepet, fill=histoire)) + 
#   geom_bar(position=position_dodge(), stat="identity") +
#   geom_errorbar(aes(ymin=tgc$nbRepet-tgc$se, ymax=tgc$nbRepet+tgc$se),
#                 width=.2,                    # Width of the error bars
#                 position=position_dodge(.9)) +
#   ggtitle("Scores cumulés en dénomination par histoire")
# p <- p + ylab("Score")+ labs(fill='histoire') 
# p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
#                plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
#                legend.title=element_text(size=18), legend.text = element_text(size=16))
# p

###################################################################



### ecriture modele initial

m0 <- glmer(nbRepet~jour*condition + (1|id) , family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))

### selecconditionon modele (effets aleatoires)

# etape 1

m1 <- glmer(nbRepet~jour*condition + (condition|id) , family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))
m2 <- glmer(nbRepet~jour*condition + (jour|id) , family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))

anova(m0,m1)
anova(m0,m2)
# garde + petit AIC : m2




### selection modele (effets fixes)

# etape 1

m4<- glmer(nbRepet~jour+condition + (jour+condition|id), family="poisson", data=tab)
anova(m2,m4) # on garde m2 : l'intéraction
# bizarre : pourquoi garde l'intéraction ??


### validation modele (surdispersion) 

mod_choisi <- m2
simulationOutput <- simulateResiduals(fittedModel = mod_choisi, n = 1000)

plotSimulatedResiduals(simulationOutput = simulationOutput)
testUniformity(simulationOutput = simulationOutput)

plot(tab$nbRepet~fitted(mod_choisi))
abline(a=0,b=1,col="red")


### comparaison multiples 

contrmat <- lsmeans(mod_choisi, pairwise~condition|jour,glhargs=list())[[2]]$linfct
comp_mult <- summary(glht(mod_choisi,linfct=contrmat)) # comp_mult <- emmeans(mod_choisi,pairwise~condition|jour)





