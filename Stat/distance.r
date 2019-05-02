###################################################### tableau de donnees #######################################


### importer tableau 
setwd("~/Documents/Alex/Stat/")
tab <- read.table("../RecallTest/brut.csv",sep=",",header=TRUE)


### type variable

tab$jour <- as.factor(as.character(tab$jour))
tab$id <- as.factor(as.character(tab$id))
tab$histoire <- as.factor(as.character(tab$histoire))
tab$condition <- as.factor(as.character(tab$condition))


### 

tab$distance2 <- tab$distance/10


### packages utilises

library(gamlss)



###################################################### statistiques descriptives #######################################


### absence id jour2,jour3 <=> distance jour1,jour2 ?

table(tab$id,tab$jour)
boxplot(distance~id, data=tab, subset=which(tab$jour=="1"))
boxplot(distance~id, data=tab, subset=which(tab$jour=="2"))



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

reponse <- tab$distance2
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
bar <- barplot(mat, beside = TRUE,  names.arg = colnames(mat), legend.text = TRUE,ylim=c(0,1), ylab="reponse", xlab="")
segments(as.vector(bar),tab_graphique$ci_inf,as.vector(bar),tab_graphique$ci_sup)


### P(distance==0)

tab$distance4 <- as.character(tab$distance2) 
tab$distance4[tab$distance4 != "0"] <- "autre"
tab$distance4 <- as.factor(as.character(tab$distance4))
prop.table(table(tab$distance4,tab$condition),2)
prop.table(table(tab$distance4,tab$jour),2)



### P(distance==1)

tab$distance3 <- as.character(tab$distance2) 
tab$distance3[tab$distance3 != "1"] <- "autre"
tab$distance3 <- as.factor(as.character(tab$distance3))
prop.table(table(tab$distance3,tab$condition),2)
prop.table(table(tab$distance3,tab$jour),2)





###################################################### modelisation #######################################


### ecriture modele

mod <- gamlss(distance2~jour*condition+ re(random=~1|id) ,nu.formula = ~jour*condition+ re(random=~1|id), tau.formula = ~jour*condition+ re(random=~1|id),family=BEINF,data=tab)


### selection modele

mod_choisi_nu <- stepGAIC(mod, scope=list(lower=~1,upper=~jour*condition + re(random=~1|id)),what=c("nu"))
mod_choisi_nu_tau <- stepGAIC(mod_choisi_nu, scope=list(lower=~1,upper=~jour*condition + re(random=~1|id)),what=c("tau"))
mod_choisi_nu_tau_mu <- stepGAIC(mod_choisi_nu_tau, scope=list(lower=~1,upper=~jour*condition + re(random=~1|id)),what=c("mu"))


### validation modele

mod_choisi <- gamlss(distance2~jour+condition+ re(random=~1|id) ,nu.formula = ~jour+ re(random=~1|id), tau.formula = ~jour+condition+ re(random=~1|id),family=BEINF,data=tab)
plot(mod_choisi)
Rsq(mod_choisi)


### comparaisons 

tab$jour <- relevel(tab$jour, ref="1")
tab$condition <- relevel(tab$condition, ref="3")
mod_choisi <- gamlss(distance2~jour+condition+ re(random=~1|id) ,nu.formula = ~jour+ re(random=~1|id), tau.formula = ~jour+condition+ re(random=~1|id),family=BEINF,data=tab)
summary(mod_choisi)
