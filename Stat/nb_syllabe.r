###################################################### tableau de donnees #######################################


### importer tableau 
setwd("~/Documents/Alex/Stat/")
tab <- read.table("../Transcription/brutDebit.csv",sep=",",header=TRUE)


### type variable

tab$jour <- as.factor(as.character(tab$jour))
tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))
tab$condition <- as.factor(as.character(tab$condition))


### packages utilises

library(multcomp)
library(lsmeans) # library(emmeans)
library(lme4)
library(DHARMa)


###################################################### statistiques descriptives #######################################



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

reponse <- tab$nbSyll
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

m0 <- glmer(nbSyll~jour*condition + (1|id) , family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))

### selecconditionon modele (effets aleatoires)

# etape 1

m1 <- glmer(nbSyll~jour*condition + (condition|id) , family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))
m2 <- glmer(nbSyll~jour*condition + (jour|id) , family="poisson", data=tab,control=glmerControl(optCtrl=list(maxfun=50000)))

anova(m0,m1)
anova(m0,m2)



### selection modele (effets fixes)

# etape 1

m3 <- glmer(nbSyll~jour+condition + (jour|id), family="poisson", data=tab)
anova(m2,m3)



### validation modele (surdispersion) 

mod_choisi <- m2
simulationOutput <- simulateResiduals(fittedModel = mod_choisi, n = 1000)

plotSimulatedResiduals(simulationOutput = simulationOutput)
testUniformity(simulationOutput = simulationOutput)

plot(tab$nbSyll~fitted(mod_choisi))
abline(a=0,b=1,col="red")


### comparaison multiples 

contrmat <- lsmeans(mod_choisi, pairwise~condition|jour,glhargs=list())[[2]]$linfct
comp_mult <- summary(glht(mod_choisi,linfct=contrmat)) # comp_mult <- emmeans(mod_choisi,pairwise~condition|jour)

