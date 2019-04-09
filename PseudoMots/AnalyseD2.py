# -*- coding: utf-8 -*-
import math
import distance
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
from dist import edit_distance
import pickle

# attention, on a transformé tous les 1 en 5, et tous les 2 en 9, E en e

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        try:
            yield line.encode('utf-8')
        except Exception as e:
            1

def openCSV(csvString,delim=''):
    with open(csvString) as csvfile:
        if delim==",":
            rd=csv.reader(utf_8_encoder(csvfile),delimiter=',')
        else:
            rd=csv.reader(utf_8_encoder(csvfile),delimiter=',')
        return rd


def extractWordsWithFreq(csvString):
    f=codecs.open(csvString,"r",encoding="utf-8")
    l = f.read().encode('utf-8').splitlines()
    freqList=[]
    for i,mot in enumerate(l):
        if len(mot)>0:
            freqList.append(mot.split())
    for i,elmt in enumerate(freqList):
        freqList[i][0]=freqList[i][0].replace('1','5')
        freqList[i][0]=freqList[i][0].replace('2','9')
        freqList[i][0]=freqList[i][0].replace('E','e')
    # on transforme les nombre en fréquence
    S=sum([float(x[1]) for x in freqList])
#    for elmt in freqList:
#        elmt[1]=float(elmt[1])/S
    return [x for x in freqList if x[1]>0]

def extractCVCVCVWords(csvString):
      # on extrait les mots de la base CVCVCV
    WordArray=[]
    # on récupère les syllabes avec leur fréquences
    with open(csvString) as csvfile:
        rd=csv.reader(utf_8_encoder(csvfile),delimiter=',')
        for row in rd:
            WordArray.append(row[0])
    return WordArray            
    
def extractAllWords(csvString):
    f=codecs.open(csvString,"r",encoding="utf-8")
    l = f.read().encode('utf-8').splitlines()
    for i,mot in enumerate(l):
        l[i]=mot[:-1]
    l=[x for x in l if len(x)>3 and len(x)<10]
    return l         


def transfoCSV(fSyll,WordsList,AllWordsList):
    for word in fSyll:
        word[0]=word[0].replace('1','5')
        word[0]=word[0].replace('2','9')
        word[0]=word[0].replace('E','e')
    fSyll=fusion(fSyll)
    # on retrie la liste
    fSyll=sorted(fSyll, key=operator.itemgetter(1),reverse=True)
    for i,word in enumerate(WordsList):
        WordsList[i]=word.replace('1','5')
        WordsList[i]=word.replace('2','9')
        WordsList[i]=word.replace('E','e')
    for i,word in enumerate(AllWordsList):
        AllWordsList[i]=word.replace('1','5')
        AllWordsList[i]=word.replace('2','9')
        AllWordsList[i]=word.replace('E','e')
    return [fSyll,WordsList,AllWordsList]


def fusion(Array):
    sArray=[]
    for x in Array:
        L= [a[0] for a in sArray]
        if x[0] not in L:
            sArray.append(x)
        else:
            sArray[L.index(x[0])][1]+=x[1]
    return sArray

def freqSyll(csvString):
    Array=[]
    # on récupère les syllabes avec leur fréquences
    with open(csvString) as csvfile:
        rd=csv.reader(utf_8_encoder(csvfile),delimiter=',')
        for row in rd:
            Array.append([row[0],float(row[1])])  
        # on les trie par fréquence
        SortedArray=[]
        SortedArray=sorted(Array, key=operator.itemgetter(1),reverse=True)
    return SortedArray 

def ListCV(csvString):
    SyllArray=[]
    # on récupère les CV
    with open(csvString) as csvfile:
        rd=csv.reader(utf_8_encoder(csvfile),delimiter=',')
        for row in rd:
            SyllArray.append(row[0])
    return list(set(SyllArray))

def SelectCV(SortedArray,SyllArray):
    # on ne garde que les CV
    dico={"V":[[],[]],"CV":[[],[]],"CVC":[[],[]]}
    for elmt in SortedArray:
        if elmt[0] in SyllArray:
            if len(elmt[0])==1:
                dico["V"][0].append(elmt[0])
                dico["V"][1].append(elmt[1])
            elif len(elmt[0])==2:
                dico["CV"][0].append(elmt[0])
                dico["CV"][1].append(elmt[1])
            else:
                dico["CVC"][0].append(elmt[0])
                dico["CVC"][1].append(elmt[1])
    for i in ["V","CV","CVC"]:
        dico[i][1]=np.array(dico[i][1])/sum(dico[i][1])
    return dico

def MotsTriphoneOk(mot,list3,Mots):
    if mot.count("*")==2:
        return False
    if mot[1]=="*":
        return False
    for i in range(0,len(mot)-2):
        tri=mot[i:i+3]
        if tri not in list3:
            return False
        if tri[1]=="*" and tri[0]==tri[2]:
            return False
    return True
    
def GenerateOneWord(Schema,dicoHisto,list3,Mots):
    histo=[[],[],[]]
    for i in range(3):
        histo[i]=dicoHisto[Schema[i]]
    word='' 
    for i in histo:
        word+=np.random.choice(i[0],1,p=i[1])[0] #indices,weights
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
    for i,schema in enumerate([["CV","CV","CV"],["V","CV","CVC"],["CV","CV","CVC"]]):
        Mots=[]
        for j in range(5000):
            mot=GenerateOneWord(schema,SyllHisto,list3,Mots)
            Mots.append(mot)
        MotsWithDist=map(WordWithPba,Mots)
        SortedMotsWithDist=sorted(MotsWithDist, key=operator.itemgetter(3),reverse=True)
        cpt=0
        for word in SortedMotsWithDist:
            res=True
            for j in range(3):
                for fWord in MotsOpti[i]:
                    if edit_distance(word[0],fWord)<2 or cpt>nb9:
                        res=False
            if res:
                MotsOpti[i].append(word[0])
                cpt+=1
    return MotsOpti
 
 # an=@,in=5,on=6,eu=9,j=Z,gn=N,ch=S
def createNaturalClasses():
# on met le schwa dans ouvert,semi-ouvert,ferme,arrondi,etire,voyAnt,voyPost,nasal,oral
# ok car prend en compte les classes contenant le schwa et pas la voyelle en question
# on a donc dist(*,voy)=0.55
# [voise,sourd,lieuAvant,Median,Posterieur,nasal,oral,occlusif,fricatif,liquide,ouvert,semi-ouvert,ferme,arrondi,etire,voyAnterieur,voyPosterieur]
    return ['bvdzZgRmnN','pftsSkl','pbmfv','tdnszl','kgNSZR','mnN@56*','pbtdlkgfvszSZRae9iOoyu*','ptkbdg','fsSvzZ','lR','@a*','Ooe659*','iyu*','yuoO@69*','iea5*','iye95a*','uoO@6*']


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
    # similarité par rapport à toute la base
    # simil grand quand ressemblance entre mots 
    #simil=map(lambda x:np.exp(-3*x),dList)
    #for i,dist in enumerate(simil):
    #    f=float(AllWordsList[i][1])
    #    if f!=0:
    #        simil[i]*=np.log(f*1000)
    #    else:
    #        simil[i]=0
    #similarite=sum(simil)
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
            WordDist[schema].append(calcOneDist(mot,AllWordsList))
    return WordDist

# évaluation au moment de choisir les 60 et lorsqu'on en garde que 36
def evalScore(tab,PositionalSegmentFreq):
    # liste des mots choisis
    liste=[x[0] for x in tab]
    simil=[x[1] for x in tab]
    WordsConcat=''.join(liste)
    freq=sum(map(WordSegmentFreq,liste))/len(liste)
    var=np.var(simil)
    return [var,freq]


def calculatePositionalSegmentFreq(WordsList):
    dico={};dicoBi={};
    # pas de frequence pour les triphones, mais on veut des sequences legales
    Sum6=0
    Sum7=0
    for i in ['R','a','e','l','s','i','*','t','d','k','p','O','@','m','n','y','6','v','u','f','b','Z','5','z','w','g','S','9','2','N','G','o','r','x']:
        dico[i]=[0.0]*7
    #S=sum([float(x[1]) for x in WordsList])
    for row in WordsList:
        freq=float(row[1])*100#besoin de nombres entiers pour que le log soit représentatif
        if freq>0:
            Sum6+=np.log10(freq)
            if len(row[0])==7:
                Sum7+=np.log10(freq)
            for i,pho in enumerate(row[0]):
                dico[pho][i]+=np.log10(freq)
            for i in range(len(row[0])-1):
                biphone=row[0][i:i+2]
                if not dicoBi.has_key(biphone):
                    dicoBi[biphone]=[0.0]*6
                dicoBi[biphone][i]+=np.log10(freq)
    for key, value in dico.iteritems():
        for i,letter in enumerate(value):
            if len(value)==6:
                value[i]/=Sum6
            else:
                value[i]/=Sum7
    for key, value in dicoBi.iteritems():
        for i,letter in enumerate(value):
            if len(value)==6:
                value[i]/=Sum6
            else:
                value[i]/=Sum7
    return [dico,dicoBi]

def findTriphones(AllWordsList):
    list3=[]
    for word in AllWordsList:
        for i in range(len(word[0])-2):
            list3.append(word[0][i:i+3])
    listFinal=list(set(list3))
    for i in listFinal:
        if list3.count(i)<100:
            listFinal.remove(i)
    return listFinal

def WordSegmentFreq(mot):
    res=0
    for i,pho in enumerate(mot):
        res+=PositionalSegmentFreq[pho][i]
    return res
    iist3=[]

# proba phonotactique d'un mot dans le dico
def WordSyllFreq(mot):
    res=0
    for i in range(len(mot)-1):
        bipho=mot[i:i+2]
        if bipho in PositionalSyllFreq.keys():
            res+=PositionalSyllFreq[bipho][i]
    return res


#### Main
nbSyllFinal=270 # première génération, 26cpar schéma, 78 en tout
nbSyllSelect=162 # on garde les moins proches de la base, 14 par schéma 
nbSyll=72 # taille de la liste finale, 8 par schéma
nbList=1
# mots de la base, 3 schémas
WordsList1=extractCVCVCVWords('MotsCV500.csv')
WordsList=extractWordsWithFreq('Mots3SchemasWithFreq.txt')
#on supprime les doublons
WordsList=[list(item) for item in set(tuple(row) for row in WordsList)]
# tous les mots de la base
AllWordsList=extractWordsWithFreq('BaseLexique/MotsFreq.txt')
AllWordsList=[list(item) for item in set(tuple(row) for row in AllWordsList)]
## On sélectionne les syllabes CV, V et CVC d'après les mots en CVCVCV etc
SyllArray=ListCV('Syllabes3Schemas.csv')
# liste des syllabes avec leur fréquence, séparée en 3 groupes
fSyll=freqSyll('FrequencesSyllabes.csv')
## on les associe avec leur fréquence, 3 histogrammes (dico)
HistoSyll=SelectCV(fSyll,SyllArray)

#histogrammes positionnel pour les contraintes phonotactiques
#[PositionalSegmentFreq,PositionalSyllFreq]=calculatePositionalSegmentFreq(WordsList)
#list3=findTriphones(AllWordsList)
#with open('histo.pkl', 'wb') as f:
#    pickle.dump([PositionalSegmentFreq,PositionalSyllFreq,list3], f, pickle.HIGHEST_PROTOCOL)

with open('histo.pkl', 'rb') as f:
    [PositionalSegmentFreq,PositionalSyllFreq,list3]=pickle.load(f)
# proba moyenne des mots de la base
pMoy=sum(map(WordSegmentFreq,[x[0] for x in WordsList]))/len(WordsList)
pMoyBiPhones=sum(map(WordSyllFreq,[x[0] for x in WordsList]))/len(WordsList)


# classes naturelles des phonemes
NaturalClasses=createNaturalClasses()

#[LegalSchwa,BeginSchwa]=LegSchwa(WordsList)

### génération des pseudos mots

#SyllHisto=SelectSyllHisto(CVArray,nbSyll)
# on veut générer plusieurs listes, avec une liste de syllabes différente à chaque fois
#for n in range(1):
#    # on génère une énorme liste avec phono ok, on choisit la sous liste qui min la variance 
#    t=time.time()
#    Mots=GeneratePM(HistoSyll,nbSyllFinal,list3,pMoy,pMoyBiPhones)
#    # on calcule les distances
#    WordDist=calcDist(Mots,AllWordsList,nbSyll)
#
#    # on sélectionne les mots les plus loin de la base pour chaque liste
#    WordDistOk=[[],[],[]]
#    for i,l in enumerate(WordDist):
#        WordDistOk[i]=sorted(WordDist[i],key=operator.itemgetter(1),reverse=True)
#    for i,l in enumerate(WordDistOk):
#        WordDistOk[i]=[x for x in WordDistOk[i] if x[1]!=0]
#
#    print "\n Liste exhaustive1 ",WordDistOk
#    for i,l in enumerate(WordDistOk):
#        WordDistOk[i]=l[:nbSyllSelect/9]
#
#    if True :
#        ErreurOpti=200000
#        for i in range(1): # on teste 100 sous-listes
#            SubList=[]
#            for j in range(3):
#                random.shuffle(WordDistOk[j])
#                SubList+=WordDistOk[j][:nbSyll/9]
#            ev=evalScore(SubList,PositionalSegmentFreq)
#            if ev[0]<ErreurOpti and ev[0]>0:
#                distOpti=list(SubList)
#                ErreurOpti=ev[0]
#                MotsOpti=list([x[0] for x in SubList])
#        PbaPhono=sum(map(WordSegmentFreq,MotsOpti))/pMoy
#        PbaSyll=sum(map(WordSyllFreq,MotsOpti))/pMoyBiPhones
#        PbaOpti=[PbaPhono,PbaSyll]
#        if ErreurOpti!=1500 or True:
#            print "\n"
#            print "Variance", ErreurOpti
#            print "Probas phonotactiques",PbaOpti
#            print "Mots choisis", MotsOpti
#            print "\n"
#            print "Avec distance ",distOpti
#        else:
#            print "pas de combinaison trouvée"
#
#
Mots=['R6d*R6', 'deR@du', 'nuviR*', 'mabevi', 'sisik6', 'dynyla', 'pal*vu', 'Zik*mi', 'k6femi',
 '@deRaZ', 'avuRis', '@lalin', 'aROlam', 'eRin@s', 'in*kad', 'aS*maZ', 'eR@ZiR', 
 'lin*Ris', 'mas*liR', 'del*RaZ', 'lak*ROn', 'deR@lis', 'vud*Ret'] 
Mots=[['6dilOS','afymOR',],['laRit@'],['eRin@s']]
print calcDist(Mots,AllWordsList,nbSyll)

