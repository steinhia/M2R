import csv
from scipy import stats

def CsvReader(name):
    with open(name, 'r') as f:
        reader = csv.reader(f)
        l = list(reader)
    return l


def name2num(name):
    name=name.replace(" ","")
    l=['GEN','PRES','CLAR','REINT','INT','EVAL','JUST','INFO','AG','DISAG','DEC','VIDE','NIR']
    return l.index(name)

# nombre d'occurrences des transitions
tab=[[0 for i in range(13)] for i in range(13)]
tabFrom=[0 for i in range(13)]
tabTo=[0 for i in range(13)]
erc=[[0 for i in range(13)] for i in range(13)]
tabProbCond=[[0 for i in range(13)] for i in range(13)]

l=CsvReader('fichier.csv')

# calcul des occurrences des transitions
for i,name in enumerate(l[:-1]): # indice et la valeur
    fromItem=name2num(name[0])
    toItem=name2num(l[i+1][0])
    tab[fromItem][toItem]+=1

# calcul des sommes
for i in range(13):
    tabFrom[i]=sum(tab[i]) # somme des lignes
    tabTo[i]=sum(tab[:][i]) # somme des colonnes
sumTot=sum(tabFrom)


# calcul des proba conditionnelles
for i in range(13):
    for j in range(13):
        tabProbCond[i][j]=tab[i][j]/tabFrom[i]
print(tabProbCond)

# calcul erc 
for i in range(13):
    for j in range(13):
            erc[i][j]=tabFrom[i]*tabTo[j]/sumTot
# transforme la liste de listes en une seule liste
erc1D = [item for sublist in erc for item in sublist]

unif1=stats.kstest(erc1D, 'uniform')
print("kolmogorov 1D",unif1)
unif2=stats.chisquare(erc1D)
print("khi2",unif2)
unif3=stats.chisquare(erc) # un résultat par ligne : à revoir signification erc
print("khi2 par ligne",unif3)
unif4=stats.chisquare(tabProbCond)
print("khi2 proba conditionnelles",unif4)


# zscore : différence par rapport à la moyenne
print("zscores")
for i,l in enumerate(tabProbCond):
    zscore=stats.zscore(l)
    print(i,zscore)



