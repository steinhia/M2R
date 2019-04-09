# -*- coding: utf-8 -*-
import math
import csv
import operator
import random
import os
import numpy as np
from collections import Counter
import codecs
import re
import time
from functools import partial
import pickle

# attention, on a transformé tous les 1 en 5, et tous les 2 en 9, E en e

def MotsTriphoneOk(mot,list3,Mots):
    # en allemand, pas de schwa, seulement un allophone de è 
    for i in range(0,len(mot)-2):
        tri=mot[i:i+3]
        if tuple(tri) not in list3[i]:
            return False
    return True
 
# on ne peut pas faire des histogrammes de tuples, on choisit l'indice et pas la syll
# on a 3 histogrammes de syllabes selon CV CVC ou V
def GenerateOneWord(Schema,dicoHisto,list3,Mots):
    histo=[[],[],[]]
    for i in range(3):
        histo[i]=dicoHisto[Schema[i]]
    word=[]
    for i in histo:
        n=len(i)
        pb=[l[1] for l in i]
        pb=[j/sum(pb) for j in pb]
        word+=list(i[np.random.choice(range(n),1,p=pb)[0]][0]) #indices,weights
    if not MotsTriphoneOk(word,list3,Mots):
        return GenerateOneWord(Schema,dicoHisto,list3,Mots)
    return word


def WordWithPba(mot):
    PbaPhono=WordSegmentFreq(mot)
    PbaSyll=WordSyllFreq(mot)
    return [mot,PbaPhono,PbaSyll,PbaPhono*PbaSyll]


def GeneratePM(SyllHisto,nbSyllFinal,list3,pMoy,pMoyBiPhones):
     # on génère les pseudo mots, puis on garde les + probables
    res=False
    nb9 = nbSyllFinal/9
    MotsOpti=[[],[],[]];    
    for i,schema in enumerate([["CV","CV","CVC"],["CV","CVC","CVC"],["CVC","CV","CVC"]]):
        print "schema i"
        Mots=[]
        for j in range(5000):
            if j%1000==0:
                print j
            mot=GenerateOneWord(schema,SyllHisto,list3,Mots)
            Mots.append(mot)
        MotsWithDist=map(WordWithPba,Mots)
        SortedMotsWithDist=sorted(MotsWithDist, key=operator.itemgetter(3),reverse=True)
        cpt=0
        print "selection"
        for word in SortedMotsWithDist:
            res=True
            for j in range(3):
                if cpt>nb9:
                    res=False
                else:
                    for fWord in MotsOpti[j]:
                        if edit_distance(word[0],fWord)<3:
                            res=False
            if res:
                MotsOpti[i].append(word[0])
                cpt+=1
    return MotsOpti
 

#Voy=['a:','a','a~','E','e:','e','E:','y:','Y','y','i:','i','I','o','o:','O','U','u:','u','@','9','2:','OY','aU','aI','2:6','e:6','o:6','y:6','96','E6','u:6','E:6','O:6','i:6','I6','O6','Y6','U6','a:6','a6']
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


# au début, on considère qu'il faut 5 insertions pour aller de X[0] à Y[:5]
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


def calcOneDist(mot,AllWordsList):
    # si le nombre est petit, c'est que la similarite est grande
    #s=sommej dj * exp(-dij)
    dList=map(partial(edit_distance,mot),[x[0] for x in AllWordsList])
    i=min(dList)
    neighbor=AllWordsList[dList.index(i)][0]
    for x in AllWordsList :
        if (len(x[0])>3 and x[0] in mot and x[1]>1) or (mot in x[0] and x[1]>1):
            neighbor=x[0]
            i=0
    return([mot,i,neighbor])
    

def calcDist(Mots,AllWordsList,nbSyll):
    nb9=nbSyll/9
    # on calcule leur distance de Levenshtein avec la base
    WordDist=[[],[],[]]
    for schema in range(3):
        for mot in Mots[schema] :# pseudo-mots
            d=calcOneDist(mot,AllWordsList)
            if (d[1]>=1 and d[1] <=2.0):
                print d
            WordDist[schema].append(d)
    return WordDist

# évaluation au moment de choisir les 60 et lorsqu'on en garde que 36
def evalScore(tab,PositionalSegmentFreq):
    # liste des mots choisis
    liste=[[x[0] for x in t] for t in tab]
    liste=liste[0]+liste[1]+liste[2]
    simil=[[x[1] for x in t] for t in tab]
    simil=simil[0]+simil[1]+simil[2]
    print "liste    ",liste
    f=0
    for i in liste:
        f+=WordSegmentFreq(i)
    f/=len(liste)
    #freq=sum(map(WordSegmentFreq,liste))/len(liste)
    var=np.var(simil)
    return [var,f]

def WordSegmentFreq(mot):
    res=0
    mot=[ i for i in mot if i!='.']
    for i,pho in enumerate(mot):
        res+=PositionalSegmentFreq[pho][i]
    return res

# proba phonotactique d'un mot dans le dico
def WordSyllFreq(mot):
    res=0
    mot=[ i for i in mot if i!='.']
    for i in range(len(mot)-1):
        bipho=mot[i:i+2]
        if bipho in PositionalSyllFreq.keys():
            res+=PositionalSyllFreq[bipho][i]
    return res


#### Main
nbSyllFinal=27*10*3 # première génération, 26cpar schéma, 78 en tout
nbSyllSelect=162 # on garde les moins proches de la base, 14 par schéma 
nbSyll=72 # taille de la liste finale, 8 par schéma
nbList=1




with open('germanWords.pkl','rb') as f:
    [WordsList,AllWordsList,PositionalSegmentFreq,PositionalSyllFreq,list3,HistoSyll]=pickle.load(f)
# pour ALLWL, on a juste besoin de l'écriture
# proba moyenne des mots de la base
#pMoy=sum(map(WordSegmentFreq,[x[0] for x in WordsList]))/len(WordsList)
#pMoyBiPhones=sum(map(WordSyllFreq,[x[0] for x in WordsList]))/len(WordsList)


# classes naturelles des phonemes
NaturalClasses=createNaturalClasses()

### génération des pseudos mots

for i in AllWordsList:
    if i[0]=='g' and i[1]=='@':
        print i

for i in list3[0]:
    if '@' in i:
        print i


for n in range(0):
    t=time.time()
#    Mots=GeneratePM(HistoSyll,nbSyllFinal,list3,pMoy,pMoyBiPhones)
    with open('germanList.pkl','rb') as f:
        Mots=pickle.load(f)
    # on calcule les distances
    #print "Mots ",Mots
    WordDist=calcDist(Mots,AllWordsList,nbSyll)

    # on garde les mots entre distance 1 et 2 avec grande pba phono
    # on sélectionne les mots les plus loin de la base pour chaque liste
    WordDistOk=[[],[],[]]
    for i,l in enumerate(WordDist):
        WordDistOk[i]=sorted(WordDist[i],key=operator.itemgetter(1),reverse=True)
    for i,l in enumerate(WordDistOk):
        WordDistOk[i]=[x for x in WordDistOk[i] if x[1]>=1 and x[1]<=2]
#    for i,l in enumerate(WordDistOk):
#        WordDistOk[i]=WordDistOk[i][:45]#
    ev=evalScore(WordDistOk,PositionalSegmentFreq)
    MotsOpti=WordDistOk
#    PbaPhono=sum(map(WordSegmentFreq,MotsOpti))/pMoy
# TODO remettre    PbaSyll=sum(map(WordSyllFreq,MotsOpti))/pMoyBiPhones
#    PbaOpti=[PbaPhono,PbaSyll]
    print "\n"
 #   print "Probas phonotactiques",PbaOpti
    print "Mots choisis"
    for i in WordDistOk:
        for wd in i:
            print wd
        print "\n"
    print "eval",ev
    print "\n"


