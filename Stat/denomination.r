###################################################### tableau de donnees #######################################
# score ~ jour + (re(random = ~1 | id)) -> pour les 3

# mu entre 0 et 1 : jour + (re(random = ~1 | id)) 
# nu O : ~jour + (re(random = ~1 | id)) 
# tau 1 : ~jour + (re(random = ~1 | id)) 

### importer tableau 

setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("../RecallTest/brut.csv",sep=",",header=TRUE)


### type variable


tab$id <- as.factor(tab$id)
tab$histoire <- as.factor(as.character(tab$histoire))

tab$condition[tab$condition=="0"] <- "MAINS_LIBRES"
tab$condition[tab$condition=="1"] <- "MAINS_CONTRAINTES"
tab$condition[tab$condition=="2"] <- "PEDALAGE_PIEDS"
tab$condition[tab$condition=="3"] <- "PEDALAGE_MAINS"
tab$condition <- factor(tab$condition,levels = c("MAINS_LIBRES", "PEDALAGE_PIEDS", "PEDALAGE_MAINS","MAINS_CONTRAINTES"))
tab$condition <- as.factor(tab$condition)
tab$nb0=as.factor(as.numeric((tab$score=='0')))

tab$jour[tab$jour=="1"]<-"J1"
tab$jour[tab$jour=="2"]<-"J2"
tab$jour[tab$jour=="3"]<-"J3"
tab$jour <- as.factor(as.character(tab$jour))
#tab$score<- as.factor(tab$score)

# score différent de 0
a<- tab$jour[which(tab$score!='0')] # & tab$score!='1')]
b<- tab$condition[which(tab$score!='0')]# & tab$score!='1')]
c<- tab$score[which(tab$score!='0')]#  & tab$score!='1')]
d<- tab$id[which(tab$score!='0')]#  & tab$score!='1')]
e<- tab$histoire[which(tab$score!='0')]#  & tab$score!='1')]
f<- tab$type[which(tab$score!='0')]#  & tab$score!='1')]
tab2=data.table(jour=a,condition=b,score=c,id=d,histoire=e,type=f)


# score différent == 0  ###et 1
a<- tab$jour[which(tab$score=="0")]
b<- tab$condition[which(tab$score=="0")]
c<- (tab$score=="0")[which(tab$score=="0")]
d<- tab$id[which(tab$score=="0")]
e<- tab$histoire[which(tab$score=="0")]
f<- tab$type[which(tab$score=="0")]
tab3=data.table(jour=a,condition=b,score=c,id=d,histoire=e,type=f)

# nombre de 0
a<- sum(tab$score=='0')
# nombre de 1


tab2$jour <- as.factor(as.character(tab2$jour))
tab3$jour <- as.factor(as.character(tab3$jour))
tab2$condition <- factor(tab2$condition,levels = c("mains libres", "pédalage pieds", "pédalage mains","mains contraintes"))


### packages utilises

library(gamlss)
library(ggplot2)
library(data.table)   

# splitFacet <- function(x){
#   facet_vars <- names(x$facet$params$facets)         # 1
#   x$facet    <- ggplot2::ggplot()$facet              # 2
#   datasets   <- split(x$data, x$data[facet_vars])    # 3
#   cat("var",facet_vars)
#   new_plots  <- lapply(datasets,function(new_data) { # 4
#     cat("var",facet_vars)
#     x$data <- new_data
#     x})
# }  
# 
# 
# 
# myplots3 <-
#   df %>% 
#   split(ceiling(group_indices(.,z)/n_facets)) %>% 
#   map(~ggplot(.,aes(x =x, y=y))+geom_point()+facet_wrap(~z))
# 
# myplots3[[3]]

  tgc <- summarySE(tab, measurevar="score", groupvars=c("jour","condition"))
  p<-ggplot(tgc, aes(x=jour, y=score, fill=condition)) + 
    scale_fill_brewer() + theme_bw() +
    geom_bar(position=position_dodge(), stat="identity" ,colour="black") +
     geom_errorbar(aes(ymin=tgc$score-tgc$se, ymax=tgc$score+tgc$se),
     width=.2,         # Width of the error bars
     position=position_dodge(.9)) 
   # ggtitle(paste("Scores en dénomination"))
  p <- p + ylab("DENOM")+ labs(fill='CONDITION')+xlab("JOUR")+ylim(0,1)
  p<- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
                plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
                legend.title=element_text(size=18), legend.text = element_text(size=16))
  # p<- p+facet_grid(.~type)

  p

  # scale fill brewer -> bleue dégradée
################# score complet individuel ###########

# for(s in levels(tab$id))
# {
# tgc <- summarySE(subset(tab,id==s), measurevar="score", groupvars=c("jour","condition","id"))
# p<-ggplot(tgc, aes(x=jour, y=score, fill=condition)) + 
#   geom_bar(position=position_dodge(), stat="identity") +
#   # geom_errorbar(aes(ymin=tgc$score-tgc$se, ymax=tgc$score+tgc$se),
#   #               width=.2,                    # Width of the error bars
#   #               position=position_dodge(.9)) +
#   ggtitle(paste(s,"Scores en dénomination"))
# p <- p + ylab("Scores")+ labs(fill='condition')
# p<- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
#               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
#               legend.title=element_text(size=18), legend.text = element_text(size=16))
# p
# ggsave(paste(s,"fig.png"))
# }

# ggsave 
# cmd -> imprime tout va dans pdf (dev)
# dev.off

######## score sans 0 

tgc <- summarySE(tab2, measurevar="score", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=score, fill=condition)) +
  # #p<-p+geom_histogram()
   geom_bar(position=position_dodge(), stat="identity",colour="black") +
  scale_fill_brewer() + theme_bw() +
   geom_errorbar(aes(ymin=tgc$score-tgc$se, ymax=tgc$score+tgc$se),
                 width=.2,                    # Width of the error bars
                 position=position_dodge(.9)) +
   ggtitle("Scores en dénomination en cas de réponse")
p <- p + ylab("Score")+ labs(fill='condition')
p<- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
              plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
              legend.title=element_text(size=18), legend.text = element_text(size=16))
p

########## score binaire : effet plancher trop important ############

tgc <- summarySE(tab, measurevar="scoreBinaire", groupvars=c("jour","condition"))
p<-ggplot(data=tgc, aes(x=jour, y=scoreBinaire, fill=condition)) + 
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$scoreBinaire-tgc$se, ymax=tgc$scoreBinaire+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("Scores en identification")
p <- p + ylab("Scores")+ labs(fill='condition')
p<- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
              plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
              legend.title=element_text(size=18), legend.text = element_text(size=16))
p


####### histogramme des 0 et des 1 ######################





# tgc <- summarySE(tab, measurevar="score", groupvars=c("jour","condition","id"))
# #p<-ggplot(data=tab, aes(x=score)) 
# #p<-ggplot(data=tgc, aes(x=jour, y=score, fill=condition)) +
# p<-ggplot(data=tgc, aes(x=jour, y=score, fill=condition)) +
# #p<-p+geom_histogram()
#   geom_bar(position=position_dodge(), stat="identity") +
#   geom_errorbar(aes(ymin=tgc$score-tgc$se, ymax=tgc$score+tgc$se),
#                 width=.2,                    # Width of the error bars
#                 position=position_dodge(.9)) +
#   ggtitle("Scores en dénomination")
# p <- p + ylab("Score")+ labs(fill='condition')
# p<- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
#               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
#               legend.title=element_text(size=18), legend.text = element_text(size=16))
#  p <- p+ facet_grid(.~id)
# p1<- splitFacet(p)
# p1

############# effet de l'histoire ###############

tgc <- summarySE(tab, measurevar="score", groupvars=c("jour","histoire"))
p<-ggplot(data=tgc, aes(x=jour, y=score, fill=histoire)) + 
  geom_bar(position=position_dodge(), stat="identity") +
  geom_errorbar(aes(ymin=tgc$score-tgc$se, ymax=tgc$score+tgc$se),
                width=.2,                    # Width of the error bars
                position=position_dodge(.9)) +
  ggtitle("Erreurs cumulées en dénomination par histoire")
p <- p + ylab("Erreur")+ labs(fill='histoire') 
p <- p + theme(axis.text=element_text(size=16), axis.title=element_text(size=18),
               plot.title = element_text(family = "Helvetica", face = "bold", size = (20)),
               legend.title=element_text(size=18), legend.text = element_text(size=16))
p





# score 2 = ramené entre 0 et 1


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
# 3 cas 0, 1 ou autre
# AIC = mesure qualité/parcimonie du modèle -> choisit le plus faible AIC
mod_choisi_nu <- stepGAIC(mod, scope=list(lower=~1,upper=~jour*condition + re(random=~1|id)),what=c("nu"))
mod_choisi_nu_tau <- stepGAIC(mod_choisi_nu, scope=list(lower=~1,upper=~jour*condition + re(random=~1|id)),what=c("tau"))
mod_choisi_nu_tau_mu <- stepGAIC(mod_choisi_nu_tau, scope=list(lower=~1,upper=~jour*condition + re(random=~1|id)),what=c("mu"))
# on enlève la condition pour les 3

# mu entre 0 et 1 jour + (re(random = ~1 | id)) 1260.0
# nu O ~jour + (re(random = ~1 | id)) 1246.5
# tau 1 ~jour + (re(random = ~1 | id)) 1233.9
# critère AIC information (information criteria)
# peut regarder # d'AIC mais pas de référence
# (re(random = ~1 | id)) : rajoute effet aléatoire du participant




### validation modele
# gamlss -> modèle beta, stepGAIG fait sélection itérative
mod_choisi <- gamlss(score~jour+ re(random=~1|id) ,nu.formula = ~jour+ re(random=~1|id), tau.formula = ~jour+ re(random=~1|id),family=BEINF,data=tab)
plot(mod_choisi)
Rsq(mod_choisi)

# Call:  gamlss(formula = score ~ jour + (re(random = ~1 | id)),  
#nu.formula = ~jour + (re(random = ~1 | id)), tau.formula = ~jour +  
#  (re(random = ~1 | id)), family = BEINF, data = tab,      trace = FALSE) 
# slmt 40% variation de la variable réponse expliquée par le modèle
# tau 1 nu 0
### comparaisons 
#j2/#j3
tab$jour <- relevel(tab$jour, ref="J2")
tab$condition <- relevel(tab$condition, ref="MAINS_LIBRES")
mod_choisi <- gamlss(score~jour+ re(random=~1|id) ,nu.formula = ~jour+ re(random=~1|id), tau.formula = ~jour+ re(random=~1|id),family=BEINF,data=tab)
summary(mod_choisi)

#nu (0) pas != j2 j3
# tau j2 !=j3
# mu pas != j2 j3
