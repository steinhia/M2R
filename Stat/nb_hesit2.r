###################################################### tableau de donnees #######################################


### importer tableau 
setwd("~/Documents/Alex/Stat/")
tab <- read.table("../Transcription/brutDebit.csv",sep=",",header=TRUE)


### type variable

tab$jour <- as.factor(as.character(tab$jour))
tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))
tab$condition[tab$condition=="0"] <- "mains libres"
tab$condition[tab$condition=="1"] <- "mains contraintes"
tab$condition[tab$condition=="2"] <- "pédalage pieds"
tab$condition[tab$condition=="3"] <- "pédalage mains"
tab$condition <- as.factor(tab$condition)

### packages utilises

library(multcomp)
library(lsmeans) # library(emmeans)
library(lme4)
library(DHARMa)


###################################################### statistiques descriptives #######################################


tgc <- summarySE(tab, measurevar="propHesit", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=propHesit, fill=condition)) + 
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$propHesit-tgc$se, ymax=tgc$propHesit+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("Nombre d'hésitations")
p <- p + ylab("nb")+ labs(fill='condition') 
p<- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
              plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
              legend.title=element_text(size=18), legend.text = element_text(size=16))
p


##############" effet de l'histoire


tgc <- summarySE(tab, measurevar="propHesit", groupvars=c("jour","histoire"))
p<-ggplot(data=tgc, aes(x=jour, y=propHesit, fill=histoire)) + 
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$propHesit-tgc$se, ymax=tgc$propHesit+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("Scores en dénomination")
p <- p + ylab("Erreur")+ labs(fill='histoire') 
p<- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
              plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
              legend.title=element_text(size=18), legend.text = element_text(size=16))
p


### creation fonction  moyenne intervalle de confiance

moyenne <- function(x){mean(x, na.rm=TRUE)}

fonction_ci_inf <- function(x){
moyenne_boot <- c()
for(i in 1:1000){moyenne_boot <- c(moyenne_boot,moyenne(sample(x=x,size=length(x),replace=TRUE)))}
return(quantile(moyenne_boot,0.025))}

fonction_ci_sup <- function(x){
moyenne_boot <- c()
for(i in 1:1000){moyenne_boot <- c(moyenne_boot,moyenne(sample(x=x,size=length(x),replace=TRUE)))}
return(quantile(moyenne_boot,0.975))}


### choix de la variale reponse et des facteurs groupants (a modifierselon l'exemple)

reponse <- tab$propHesit
facteur1 <- tab$condition
facteur2 <- tab$jour


### creation tableau pour graphique 

tab_agg_moyenne <- aggregate(as.numeric(as.character(reponse)), by=list(facteur1, facteur2),moyenne)
tab_agg_ci_inf <- aggregate(as.numeric(as.character(reponse)), by=list(facteur1, facteur2),fonction_ci_inf)

tab_agg_ci_sup <- aggregate(as.numeric(as.character(reponse)), by=list(facteur1, facteur2),fonction_ci_sup)
tab_graphique <- cbind(tab_agg_moyenne,tab_agg_ci_inf[,ncol(tab_agg_ci_inf)],tab_agg_ci_sup[,ncol(tab_agg_ci_sup)])

colnames(tab_graphique)[ncol(tab_graphique)-2] <- "moyenne"
colnames(tab_graphique)[ncol(tab_graphique)-1] <- "ci_inf"
colnames(tab_graphique)[ncol(tab_graphique)] <- "ci_sup"


### graphique (avec intervalle de confiance) 

mat <- matrix(tab_graphique$moyenne, nrow=nlevels(facteur1), dimnames=list(levels(facteur1),levels(facteur2)))
bar <- barplot(mat, beside = TRUE,  names.arg = colnames(mat), legend.text = TRUE,ylim=c(0,600), ylab="reponse", xlab="")
segments(as.vector(bar),tab_graphique$ci_inf,as.vector(bar),tab_graphique$ci_sup)




###################################################### modelisation #######################################


### ecriture modele initial

m0 <- glmer(propHesit~jour*condition + (1|id) , family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))

### selecconditionon modele (effets aleatoires)

# etape 1

m1 <- glmer(propHesit~jour*condition + (condition|id) , family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))
m2 <- glmer(propHesit~jour*condition + (jour|id) , family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))

anova(m0,m1)
anova(m0,m2)



### selection modele (effets fixes)

# etape 1

m3 <- glmer(propHesit~jour+condition + (jour|id), family="poisson", data=tab)
anova(m2,m3)



### validation modele (surdispersion) 

mod_choisi <- m2
simulationOutput <- simulateResiduals(fittedModel = mod_choisi, n = 1000)

plotSimulatedResiduals(simulationOutput = simulationOutput)
testUniformity(simulationOutput = simulationOutput)

plot(tab$propHesit~fitted(mod_choisi))
abline(a=0,b=1,col="red")


### comparaison multiples 

contrmat <- lsmeans(mod_choisi, pairwise~condition|jour,glhargs=list())[[2]]$linfct
comp_mult <- summary(glht(mod_choisi,linfct=contrmat)) # comp_mult <- emmeans(mod_choisi,pairwise~condition|jour)

