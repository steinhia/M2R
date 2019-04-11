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
'suiy1ohYtpMc.png',
'0b30ZuqmWz8O.png',
'n55EF0EPH3eh.png',
'UR7y2KDxGdkV.png',
'YvwxbuziPnUW.png',
'fYjGeVqjiINB.png',
'tLIgcDR9urkS.png',
'YEMx5pW9l952.png',
'XnQSXSzM0tU7']

# f(4)=1 : numero d'image -> numero d'histoire
def num2s(imgNum):
    return imgNum/3

# f('Tereinat')=3 : nom de PM -> numero du PM
def name2num(word):
    return NamesList.index(word)

# f(3)='Tereinat' : numero du PM -> nom du PM
def num2name(i):
    return NamesList[i]

# f('img3')='Tereinat' : nom de l'image -> nom du PM
def imgName2name(imgName):
    if imgName!='':
        num=int(imgName[3:])
        name=NamesList[num]
        return name
    return -1

# f('Tereinat')=1 : nom du PM -> numero d'histoire
def name2s(word):
    return num2s(name2num(word))

#f(3)='personnage'
def num2type(i):
    if i%3==0:
        return 'personnage'
    elif i%3==1:
        return 'maison'
    else:
        return 'vehicule'

# les histoires vont de 0 à 3, les mots de 0 à 11, les conditions de 0 à 3
# Bonnes réponses du test 
# noms de à à 11 correspondant aux images
NamesList=['Mielbete','Keimase','Sonistik','Tereinat','Ligete','Mattendich','Soltete','Madikten','Wecktellin','Lasgelich','Zulergen','Melare']

# liste des mots demandés pour l'identification (questions)
IdentificationListNum=[2,1,4,0,10,5,7,3,11,6,8,9]
IdentificationListNumUnit=[1,2,0,3,4,5,6,8,7,10,9,11]
IdentificationList=map(num2name,IdentificationListNum)
IdentificationListUnit=map(num2name,IdentificationListNumUnit)
IdentificationList1=map(num2name,[1,2,0])
IdentificationList2=map(num2name,[3,4,5])
IdentificationList3=map(num2name,[6,8,7])
IdentificationList4=map(num2name,[10,9,11])

# liste des mots espérés pour la pour la dénomination (réponses, questions = img)
DenominationList=map(num2name,[0,1,2,6,7,8,3,4,5,9,10,11])
DenominationList1=map(num2name,[2,0,1])
DenominationList2=map(num2name,[3,4,5])
DenominationList3=map(num2name,[8,7,6])
DenominationList4=map(num2name,[9,11,10])


# condition correspondant à l'histoire pour l'id correspondant
def s2c(idPart,sNum,permut):
    line=permut[idPart]
    res=-1
    for i in line:
        if i[0]==sNum:
            res=i[1]
    return res

# remplace l'URL par le numéro d'image
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
def IdentificationCond(tab,LN,idPart,permut,errDico):
    res=[0,0,0,0]
    resH=[0,0,0,0]
    for i,num in enumerate(tab):
        imgD=LN[i]
        nb=-1
        if num!='':
            nb=int(num[3:])
        if LN[i]!=int(nb): # image desiree, image selectionnee
            #if mini>=0 and maxi>=0:
            errDico[str(imgD).zfill(2)+str(nb).zfill(2)]+=1
            res[s2c(idPart,num2s(imgD),permut)]+=1
            resH[num2s(imgD)]+=1
        else:
            1#print "ok",nb,LN[i]
    return [res,resH,errDico]

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


def createLigne(ligne,permut,n=0):
    sujet=int(ligne[0])
    jour=ligne[1]
    ordre=permut[int(sujet)-1]
    ordreS="".join([str(a[0]) for a in ordre])
    ordreC="".join([str(a[1]) for a in ordre])
    # on s'interesse à l'identification : liste des noms rentres
    identNames=[]
    if len(ligne)>20:
        identNames=[imgName2name(name) for name in ligne[14:]]
    else:
        identNames=[imgName2name(name) for name in ligne[5:]]
    # on crée les lignes pour le tableau de résultat
    res=[]
    for i,name in enumerate(identNames):
        # boolean réussite/échec
        answer=''
        ordrei=i/3
        if len(ligne)>20:
            answer=IdentificationList[i]
        else:
            answer=IdentificationListUnit[i+n*3] 
            ordrei+=n
        b=(name==answer)
        # de 0 à 3, ordre temporel, pas histoire/condition
        story=ordrei
        condition=ordreC[ordreS.index(str(story))]
        # type : maison etc
        nameType=num2type(i)
        res.append([sujet,jour,str(ordreS),str(ordreC),story,condition,name,answer,b])
    return res


# on télécharge tout avec une virgule en séparateur
l=CsvReader('recall_test_v3.csv')
l1=CsvReader('recall_s1.csv')
l2=CsvReader('recall_s2.csv')
l3=CsvReader('recall_s3.csv')
l4=CsvReader('recall_s4.csv')
with open('Permut.pkl','rb') as f:
    permut=pickle.load(f)
# on remet tout de 0 à 3
for idi in permut:
    for i in idi:
        for j,case in enumerate(i):
            i[j]=case-1
dico={}
for i in range(1,20):
    dico[i]=[[] for j in range(6)]


# dico de confusion
errDico={}
for i in range(12):
    for j in range(-1,12):
        errDico[str(i).zfill(2)+str(j).zfill(2)]=0
# test entier
CSVTab=[]
for i,ligne in enumerate(l[1:]):
    ligne=replaceName(ligne)
    idPart=int(ligne[0])
    idTest=int(ligne[1])+2
    ident=Identification(ligne[14:],IdentificationList)
    [identCond,identHist,errDico]=IdentificationCond(ligne[14:],IdentificationListNum,idPart,permut,errDico)
    CSVTab+=createLigne(ligne,permut)
    dico[idPart][idTest]=[ligne[2:14],ligne[14:],0,ident,0,identCond,identHist]

# test unitaire : erreur dans le prévu
for i,ligne in enumerate(l1[1:]):
    ligne=replaceName(ligne)
    CSVTab+=createLigne(ligne,permut)
for i,ligne in enumerate(l2[1:]):
    ligne=replaceName(ligne)
    CSVTab+=createLigne(ligne,permut,1)
for i,ligne in enumerate(l3[1:]):
    ligne=replaceName(ligne)
    CSVTab+=createLigne(ligne,permut,2)
for i,ligne in enumerate(l4[1:]):
    ligne=replaceName(ligne)
    CSVTab+=createLigne(ligne,permut,3)


for i in CSVTab:
    1#print i,"\n"




# tests unitaires, jours 1 et 2
#dico=singleTest(l1,1,DenominationList,dico,0) # checker si bonnes listes
#dico=singleTest(l2,DenominationList1,DenominationList,dico,1)
#dico=singleTest(l3,DenominationList2,DenominationList,dico,2)
#dico=singleTest(l4,DenominationList,DenominationList,dico,3)

# test global, jours 2 et 3
condJ2=[0,0,0,0]
histJ2=[0,0,0,0]
condJ3=[0,0,0,0]
histJ3=[0,0,0,0]
nb2=0
nb3=0
for i in dico.keys():
    res=dico[i]
    resJ2=res[4]
    resJ3=res[5]
    if len(resJ2)>0: 
        nb2+=1
        condUnitJ2=resJ2[5]
        histUnitJ2=resJ2[6]
        for j in range(4):
            condJ2[j]+=condUnitJ2[j]
            histJ2[j]+=histUnitJ2[j]
    if len(resJ3)>0: 
        nb3+=1
        condUnitJ3=resJ3[5]
        histUnitJ3=resJ3[6]
        for j in range(4):
            condJ3[j]+=condUnitJ3[j]
            histJ3[j]+=histUnitJ3[j]
        if int(i)==5:
            print "cond puis hist j2"
            print condUnitJ3
            print histUnitJ3

print "test 2e jour : "+str(nb2)+ " participants "
print "effet par condition :",condJ2
print "effet par histoire",histJ2
print "\ntest 3e jour : "+str(nb3)+" participants "
print "effet par condition :",condJ3
print "effet par histoire",histJ3

sorted_d = sorted(errDico.items(), key=operator.itemgetter(1))
#print sorted_d

# confusions :
# entre noms de la même histoire ?
# entre noms de la même sorte ?
# entre noms se ressemblant ? -> distance moyenne entre les confusions
# entre formes se ressemblant ?
# par image (possibilité) ?
# par texte (question) ?
   
#with open('brut.csv', mode='w') as f:
#    writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#    writer.writerow(["id","jour","ordre histoires","ordre conditions","histoire","condition","reponse donnee","reponse attendue","evaluation"])
#    for i in CSVTab:
#        writer.writerow(i) 
