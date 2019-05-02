###################################################### tableau de donnees #######################################


### importer tableau 


setwd("~/Documents/Alex/Stat/")
tab <- read.table("../RecallTest/brut.csv",sep=",",header=TRUE)

###

tab$evaluation <- as.character(tab$evaluation)
tab$evaluation[tab$evaluation=="True"] <- "1"
tab$evaluation[tab$evaluation=="False"] <- "0"
tab$evaluation <- as.factor(tab$evaluation)

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

### creaconditionon fonction  moyenne intervalle de confiance

moyenne <- function(x){mean(x, na.rm=TRUE)}

fonction_ci_inf <- function(x){
moyenne_boot <- c()
for(i in 1:1000){moyenne_boot <- c(moyenne_boot,moyenne(sample(x=x,size=length(x),replace=TRUE)))}
return(quantile(moyenne_boot,0.025))}

fonction_ci_sup <- function(x){
moyenne_boot <- c()
for(i in 1:1000){moyenne_boot <- c(moyenne_boot,moyenne(sample(x=x,size=length(x),replace=TRUE)))}
return(quantile(moyenne_boot,0.975))}


### choix de la variale reponse et des facteurs jourants (a modifierselon l'exemple)

reponse <- tab$evaluation
facteur1 <- tab$condition
facteur2 <- tab$jour


### creaconditionon tableau pour graphique 

tab_agg_moyenne <- aggregate(as.numeric(as.character(reponse)), by=list(facteur1, facteur2),moyenne)
tab_agg_ci_inf <- aggregate(as.numeric(as.character(reponse)), by=list(facteur1, facteur2),fonction_ci_inf)

tab_agg_ci_sup <- aggregate(as.numeric(as.character(reponse)), by=list(facteur1, facteur2),fonction_ci_sup)
tab_graphique <- cbind(tab_agg_moyenne,tab_agg_ci_inf[,ncol(tab_agg_ci_inf)],tab_agg_ci_sup[,ncol(tab_agg_ci_sup)])

colnames(tab_graphique)[ncol(tab_graphique)-2] <- "moyenne"
colnames(tab_graphique)[ncol(tab_graphique)-1] <- "ci_inf"
colnames(tab_graphique)[ncol(tab_graphique)] <- "ci_sup"


### graphique (avec intervalle de confiance) 

mat <- matrix(tab_graphique$moyenne, nrow=nlevels(facteur1), dimnames=list(levels(facteur1),levels(facteur2)))
bar <- barplot(mat, beside = TRUE,  names.arg = colnames(mat), legend.text = TRUE,ylim=c(0,1), ylab="reponse", xlab="")
segments(as.vector(bar),tab_graphique$ci_inf,as.vector(bar),tab_graphique$ci_sup)


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
