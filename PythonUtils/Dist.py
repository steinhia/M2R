# -*- coding: utf-8 -*-

# calcul de la distance pour le test de dénomination 

Voy=['a','e','y','i','o','u','@','9','2:','OY','aU','aI','2:6','e:6','o:6','y:6','96','E6','u:6','E:6','O:6','i:6','I6','O6','Y6','U6','a:6','a6']

# 6 n'est utilisé qu'en diphtongue, sinon remplacé par @R
# sinon 6 ne rentre pas dans les schémas CVCVCVC, statut ni de voyelle ni consonne
Cons=['b','k','d','f','g','h','j','l','m','n','p','r','s','t','v','N','z','Z','C','ts','tS','dZ','S','x','?']
 # an=@,in=5,on=6,eu=9,j=Z,gn=N,ch=S
def createNaturalClasses():
# on met le schwa dans ouvert,semi-ouvert,ferme,arrondi,etire,voyAnt,voyPost,nasal,oral
# ok car prend en compte les classes contenant le schwa et pas la voyelle en question
# on a donc dist(*,voy)=0.55
# [voise,sourd,lieuAvant,Median,Posterieur,nasal,oral,occlusif,fricatif,liquide,ouvert,semi-ouvert,ferme,arrondi,etire,voyAnterieur,voyPosterieur]
    return ['bvdzZgRmnNjl','pftsSkxCh','pbmfv','tdnszlSZ','xCkgRNhj','mnN','ptkbdg','fsSvzZChxR','lj','a','oe@9','iyu','yuo9','iea@','iye@','uo','a9']
NaturalClasses=createNaturalClasses()

def _edit_dist_init(len1, len2):
    lev = []
    for i in range(len1):
        lev.append([0] * len2)  # initialize 2D array to zero
    for i in range(len1):
        lev[i][0] = i  # column 0: 0,1,2,3,4,...
    for j in range(len2):
        lev[0][j] = j  # row 0: 0,1,2,3,4,...
    return lev

def phonemeDist(NaturalClasses,c1,c2):
    n=0;n1=0;n2=0;
    c1=c1.lower()[0]
    c2=c2.lower()[0]
    if c1==c2:
        return 0
    for s in NaturalClasses:
        if c1 in s and c2 in s:
            n+=1
        elif c1 in s:
            n1+=1
        elif c2 in s:
            n2+=1
    if n+n1+n2!=0:
        return float((n1+n2))/float((n+n1+n2))
    return 1

def _edit_dist_step(lev, i, j, s1, s2, substitution_cost=1.0/0.7):
    c1 = s1[i - 1]
    c2 = s2[j - 1]
    # insertions ou deletions
    # skipping a character in s1
    a = lev[i - 1][j] + 1
    # skipping a character in s2
    b = lev[i][j - 1] + 1
    # substitution
    c = lev[i - 1][j - 1] + (substitution_cost*phonemeDist(NaturalClasses,c1,c2))
    # pick the cheapest
    lev[i][j] = min(a, b, c)


def edit_distance(s1, s2, substitution_cost=1.0/0.7):
    # set up a 2-D array
    s1=[x for x in s1 if x!='.']
    s2=[x for x in s2 if x!='.']
    len1=len(s1);len2=len(s2)
    lev=_edit_dist_init(len1+1,len2+1)
    for i in range(len1):
        for j in range(len2):
            _edit_dist_step(lev,i+1,j+1,s1,s2,substitution_cost=substitution_cost)
    return lev[len1][len2]
