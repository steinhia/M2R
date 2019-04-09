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

def calculatePositionalSegmentFreq(WordsList):
    dico={};dicoBi={};
    # pas de frequence pour les triphones, mais on veut des sequences legales
    Sum=1
    for row in WordsList:
        freq=float(row[1])*100#besoin de nombres entiers pour que le log soit représentatif
        if freq>0:
            Sum+=np.log10(freq)
            wd=[ l for l in row[0] if l!='.']
            for i,pho in enumerate(wd):
                if not dico.has_key(pho):
                    dico[pho]=[0.0]*15
                dico[pho][i]+=np.log10(freq)
            for i in range(len(wd)-1):
                biphone=tuple(wd[i:i+2])
                if not dicoBi.has_key(biphone):
                    dicoBi[biphone]=[0.0]*15
                dicoBi[biphone][i]+=np.log10(freq)
    for key, value in dico.iteritems():
        for i,letter in enumerate(value):
            if value[i]>0 and Sum>0:
                value[i]/=Sum
    for key, value in dicoBi.iteritems():
        for i,letter in enumerate(value):
            if value[i]>0 and Sum>0:
                value[i]/=Sum
    return [dico,dicoBi]

def findTriphones(AllWordsList): 
    list3=[[],[],[],[],[],[],[],[]]
    for l in AllWordsList:
        word=[ x for x in l[0] if x!='.']
        for i in range(min(8,len(word)-2)):
            if i==0 and word[0]=='g' and word[1]=='@':
                print word
            list3[i].append(tuple(word[i:i+3]))
    listFinal=[[],[],[],[],[],[],[],[]]
    for i in range(8):
        listFinal[i]=list(set(list3[i]))
    listFinal2=[[],[],[],[],[],[],[],[]]
    for j in range(8):
        for i in listFinal[j]:
            if list3[j].count(tuple(i))>10:
                listFinal2[j].append(tuple(i))
    return listFinal2

def schema(mot,Voy,Cons):
    schema=''
    for letter in mot:
        if letter in Voy:
            schema+='V'
        elif letter in Cons:
            schema+='C'
        elif letter==".":
            schema+="."
    return schema

def simplify(mot):
    if '?' in mot:
        mot.remove('?')
    for i,pho in enumerate(mot):
        # on simplifie les voyelles simples (tense, relax, longues)
        if pho in ['a:','a~',]:
            mot[i]='a'
        if pho in ['E','e:','e','E:']:
            mot[i]='e'
        if pho in ['y:','Y']:
            mot[i]='y'
        if pho in ['i:','I']:
            mot[i]='i'
        if pho in ['o','o:','O']:
            mot[i]='o'
        if pho in ['U','u:']:
            mot[i]='u'
        # on remplace 6 par @r
        if pho=='6':
            mot=mot[:i]+['@','r']+mot[i+1:]
        # on supprime les coups de glotte : pas de paire minimale
    return mot


#with open('germanWords.pkl','rb') as f:
#    [WordsList,AllWordsList,d,db,list3,dicoSyll]=pickle.load(f)
# pour éviter les \xc, au lieu de print l, for i in l : print i
f=codecs.open("german_lexicon.txt",encoding="utf-8")
l=f.read().encode('utf-8').splitlines()
Voy=['a:','a','a~','E','e:','e','E:','y:','Y','y','i:','i','I','o','o:','O','U','u:','u','@','9','6','2:','?','OY','aU','aI','2:6','e:6','o:6','y:6','96','E6','u:6','E:6','O:6','i:6','I6','O6','Y6','U6','a:6','a6']

# 
Cons=['b','k','d','f','g','h','j','l','m','n','p','r','s','t','v','N','z','Z','C','ts','tS','dZ','S','x','?']
#
### on veut trouver la médiane des longuers de mots en allemand : 3
#WordLength=[]
#for i in l:
#    t=i.split()
#    if float(t[-1])!=0.0:
#        WordLength.append((1+t[1].count('-')))
##
## on veut trouver les schémas les plus fréquents pour les mots de 3 syll
## on commence par garder les mots de 3 syllabes
Syll3Words=[]
AllWordsList=[]
WordsList=[]
dico={}
## on trouve les 3 schémas les plus fréquents :
## CV.CV.CVC : vorsagen
## CVC.CV.CVC : zuwandern, weggeben, sublimen
## CV.CVC.CVC : subaltern
#






for i in l:
    t=i.split()
    f=float(t[-1])
    cat=t[-2]
    mot =[x for i,x in enumerate(t) if i>1 and i<len(t)-2]
    # si 6 est tout seul, on le remplace par @ r
    mot=simplify(mot)
    sch=schema(mot,Voy,Cons)
    if f!=0 and t.count('.')==2:
        dico[sch] = dico.get(sch, 0) + 1
        WordsList.append([mot,f])
    if f!=0.0:
        AllWordsList.append([mot,f])
    Syll3Words.append([t[0],mot,sch,cat])
SchemaOk=[]
MotsSchemaOk=[]
for key in sorted(dico.items(),key=operator.itemgetter(1),reverse=True)[:3]:
    SchemaOk.append(key)
    

for i in Syll3Words:
    if i[2] in [x[0] for x in SchemaOk] and cat=='NN':
        MotsSchemaOk.append(i)

[d,db]=calculatePositionalSegmentFreq(WordsList)
list3=findTriphones(AllWordsList)


for i in range(8):
    print len(list3[i])
# on veut extraire la fréquence des syllabes 
dicoS={}
for i in WordsList:
    wd=i[0]
    f=i[1]
    if f!=0:
        a=schema(wd,Voy,Cons)
        if a in ['CV.CV.CVC','CVC.CV.CVC','CV.CVC.CVC']:
            syll=[]
            if wd.count('.')>2:
                print wd
            for num in range(2):
                if '.' in wd:
                    ind=wd.index('.')
                    syll.append(wd[:ind])
                    wd=wd[ind+1:]
            syll.append(wd)
            if len(syll)==3:
                for s in syll:
                    dicoS[tuple(s)]=dicoS.get(tuple(s),0)+f

#
# à la fin, on veut 2 dico de listes
dicoSyll={"CV":[],"CVC":[]}
for i in dicoS.items(): # TODO
    syll=i[0]
    f=float(i[1])
    dicoSyll[schema(syll,Voy,Cons)].append([syll,f])
#with open('germanWords.pkl','wb') as f:
#    pickle.dump([WordsList,AllWordsList,d,db,list3,dicoSyll],f,pickle.HIGHEST_PROTOCOL)
