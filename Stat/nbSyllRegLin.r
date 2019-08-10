

### importer tableau 
setwd("~/Documents/Alex/Stat/")
source("summarySE.r")
tab <- read.table("brutResume.csv",sep=",",header=TRUE)


lm_eqn <- function(df,v1,v2){
  m <- lm(v1 ~ v2, df);
  eq <- substitute(italic(y) == a + b %.% italic(x)*","~~italic(r)^2~"="~r2, 
                   list(a = format(coef(m)[1], digits = 2),
                        b = format(coef(m)[2], digits = 2),
                        r2 = format(summary(m)$r.squared, digits = 3)))
  as.character(as.expression(eq));
}


b <- ggplot(tab, aes(x = tab$nbSyll, y=tab$nbSyllAudio))
b<- b + geom_point() # rajouter y dans le ggplot de base
b<- b+geom_smooth(method = "lm")
b <-b + geom_text(x = 250, y = 800, label = lm_eqn(tab,tab$nbSyll,tab$nbSyllAudio), parse = TRUE)
b
cor.test(tab$nbSyll,tab$nbSyllAudio,method='spearman')

# taille >150 : pas besoin de vérifier la normalité
var.test(tab$nbSyll,tab$nbSyllAudio) # variances égales (p-value = 0.7893)
shapiro.test(tab$nbSyll) # p-value = 0.02128
shapiro.test(tab$nbSyllAudio) # p-value = 0.007778
qqnorm(tab$nbSyll)
qqnorm(tab$nbSyllAudio)

t.test(tab$nbSyll,tab$nbSyllAudio,paired=TRUE)
# diff moyenne = 12 : on utilise la corrélation
# je le mets dans le mémoire

#h<- ggplot(tab,x=tab$nbSyll) +geom_histogram()
h1<-ggplot(tab, aes(x=tab$nbSyll)) + geom_histogram()
h1
h2<-ggplot(tab, aes(x=tab$nbSyllAudio)) + geom_histogram()
h2
a=var(tab$nbSyll,na.rm=TRUE)
b=var(tab$nbSyllAudio,na.rm=TRUE)
(b-a)/a
(b-a)/b
# # lien entre les 2 variances
# g <- ggplot(tab, aes(x = tab$debit.moyen, y=tab$variance.pédalage))
# g<- g + geom_point() # rajouter y dans le ggplot de base
# g<- g+geom_smooth(method = "lm")
# g <-g + geom_text(x = 1, y = 0.1, label = lm_eqn(tab,dénomination,variance.pédalage), parse = TRUE)
# g