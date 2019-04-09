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
import csv


ListOfURL=['fyJR1Nd5bdYf.png',
'RXu0QM7rpAyU.png',
'Qgz50gtfWEKz.png',
'UR7y2KDxGdkV.png',
'YvwxbuziPnUW.png',
'fYjGeVqjiINB.png',
'suiy1ohYtpMc.png',
'0b30ZuqmWz8O.png',
'n55EF0EPH3eh.png',
'tLIgcDR9urkS.png',
'YEMx5pW9l952.png',
'XnQSXSzM0tU7']


# Bonnes réponses du test 
# noms correspondant aux images
ListOfNames=['Mielbete','Keimase','Sonistik','Soltete','Madikten','Wecktellin','Tereinat','Ligete','Mattendich','Lasgelich','Zulergen','Melare']
ListOfNames1=['Sonistik','Mielbete','Keimase']
ListOfNames2=['Tereinat','Ligete','Mattendich']
ListOfNames3=['Wecktelin','Madikten','Soltete']
ListOfNames4=['Lasgelich','Melare','Zulerge']

# questions : quels mots sont demandés
ListOfNumbers=[2,1,7,0,10,8,4,6,11,3,5,9]
ListOfNumbers1=[1,2,0]
ListOfNumbers2=[6,7,8]
ListOfNumbers3=[3,5,4]
ListOfNumbers4=[10,9,11]

# number to story
def n2s(imgNum):
    dico={0:1,1:1,2:1,3:3,4:3,5:3,6:2,7:2,8:2,9:4,10:4,11:4}
    return dico[imgNum]
# name to story
def name2num(word):
    dico={'Keimase':1,'Sonistik':2,'Mielbeten':0,'Ligete':7,'Mattendich':8,'Tereinat':6,'Madikten':4,'Wecktellin':5,'Soltete':3,'Zulergen':10,'Melare':11,'Lasgelich':9}
def name2story(word):
    dico={'Keimase':1,'Sonistik':1,'Mielbeten':1,'Ligete':2,'Mattendich':2,'Tereinat':2,'Madikten':3,'Wecktellin':3,'Soltete':3,'Zulergen':4,'Melare':4,'Lasgelich':4}


def s2c(idPart,sNum,permut):
    line=permut[idPart-1]
    res=-1
    for i in line:
        if i[0]==sNum:
            res=i[1]
    return res


def replaceName(ligne):
    for i,case in enumerate(ligne):
        for j,name in enumerate(ListOfURL):
            if name in case:
                ligne[i]='img'+str(j)
    return ligne

def Identification(tab,LN):
    res=0
    for i,num in enumerate(tab):
        if num=='':
            res+=1
        # on compare numero d'image voulu et trouvé
        elif LN[i]!=int(num[3:]):
            res+=1
    return res


# C 0:mains libres, 1:mains contraintes, 2:bike pieds, 3:bike mains
def IdentificationCond(tab,LN,idPart,permut):
    res=[0,0,0,0]
    resH=[0,0,0,0]
    for i,num in enumerate(tab):
        nb=-1
        if num!='':
            nb=int(num[3:]) 
        if LN[i]!=int(nb): # image desiree, image selectionnee
            res[s2c(idPart,n2s(LN[i]),permut)-1]+=1
            resH[n2s(LN[i])-1]+=1
            if idPart==4:
                1#print num,LN[i]-1
    return [res,resH]

def CsvReader(name):
    with open(name, 'rb') as f:
        reader = csv.reader(f)
        l = list(reader)
    return l

def singleTest(liste,LN,LNm,dico,num):
    for i,ligne in enumerate(liste[1:]):
        idPart=int(ligne[0])
        ligne=replaceName(ligne)
        ident=Identification(ligne[5:],LN)
        dico[idPart][num]=[ligne[2:5],ligne[5:],0,ident]
    return dico

# on télécharge tout avec une virgule en séparateur
# long test
l=CsvReader('recall_test_v3.csv')
l1=CsvReader('recall_s1.csv')
l2=CsvReader('recall_s2.csv')
l3=CsvReader('recall_s3.csv')
l4=CsvReader('recall_s4.csv')
with open('Permut.pkl','rb') as f:
    permut=pickle.load(f)

dico={}
for i in range(1,20):
    dico[i]=[[] for j in range(6)]


# simple score
for i,ligne in enumerate(l[1:]):
    ligne=replaceName(ligne)
    idPart=int(ligne[0])
    idTest=int(ligne[1])+2
    ident=Identification(ligne[14:],ListOfNumbers)
    [identCond,identHist]=IdentificationCond(ligne[14:],ListOfNumbers,idPart,permut)
    dico[idPart][idTest]=[ligne[2:14],ligne[14:],0,ident,0,identCond,identHist]

dico=singleTest(l1,ListOfNumbers1,ListOfNames,dico,0)
dico=singleTest(l2,ListOfNumbers2,ListOfNames,dico,1)
dico=singleTest(l3,ListOfNumbers3,ListOfNames,dico,2)
dico=singleTest(l4,ListOfNumbers4,ListOfNames,dico,3)
cond=[0,0,0,0]
hist=[0,0,0,0]
for i in dico.keys():
    res=dico[i]
    resUnit=res[4]
    if len(resUnit)>0: 
        condUnit=resUnit[5]
        histUnit=resUnit[6]
        for j in range(4):
            cond[j]+=condUnit[j]
            hist[j]+=histUnit[j]
print cond
print hist
