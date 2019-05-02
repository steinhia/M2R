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
from itertools import islice
import panda as pd
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())


#def singleTest(liste,LN,LNm,dico,num):
#    for i,ligne in enumerate(liste[1:]):
#        idPart=int(ligne[0])
#        ligne=replaceName(ligne)
#        ident=Identification(ligne[5:],LN)
#        dico[idPart][num]=[ligne[2:5],ligne[5:],0,ident]
#    return dico

# on prend un test d'un participant et on crée les lignes csv correspondantes
def createLigneBrut(ligne,permut,n=0):
    sujet=int(ligne[0])
    jour=ligne[1]
    ordre=permut[int(sujet)-1]
    ordreS="".join([str(a[0]) for a in ordre])
    ordreC="".join([str(a[1]) for a in ordre])
    identNames=[];denomNames=[]
    if len(ligne)>20:
        identNames=[imgName2name(name) for name in ligne[14:]]
        denomNames=[name for name in ligne[2:14]]
    else:
        identNames=[imgName2name(name) for name in ligne[5:]]
        denomNames=[name for name in ligne[2:5]]


    # on s'interesse à l'identification : liste des noms rentres
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
        # on récupère l'histoire à partir de la réponse attendue
        story=name2s(answer)
        # condition ocrrespondante
        condition=ordreC[ordreS.index(str(story))]
        # type : maison etc
        nameType=name2type(answer)
        res.append([sujet,jour,'c '+str(ordreC),'s '+str(ordreS),condition,story,nameType,name,answer,b])

    # dénomination ensuite : on complete la liste
    for i,name in enumerate(denomNames):
        if name!='':
            ordrei=i/3
            answer=''
            if len(ligne)>20:
                answer=DenominationList[i]
            else:
                answer=DenominationListUnit[i+n*3] 
                ordrei+=n
            # on cherche la bonne ligne
            for j,l in enumerate(res):
                if l[8]==answer:
                    l.append(name)
    return res


# on télécharge tout avec une virgule en séparateur
l=CsvReader('recall_test.csv')
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
#errDico={}
#for i in range(12):
#    for j in range(-1,12):
#        errDico[str(i).zfill(2)+str(j).zfill(2)]=0

# test entier
CSVTab=[]
for i,ligne in enumerate(l[1:]):
    ligne=replaceName(ligne)
    CSVTab+=createLigneBrut(ligne,permut)
    #dico[idPart][idTest]=[ligne[2:14],ligne[14:],0,ident,0,identCond,identHist]

# test unitaire 
for i,ligne in enumerate(l1[1:]):
    ligne=replaceName(ligne)
    CSVTab+=createLigneBrut(ligne,permut)
for i,ligne in enumerate(l2[1:]):
    ligne=replaceName(ligne)
    CSVTab+=createLigneBrut(ligne,permut,1)
for i,ligne in enumerate(l3[1:]):
    ligne=replaceName(ligne)
    CSVTab+=createLigneBrut(ligne,permut,2)
for i,ligne in enumerate(l4[1:]):
    ligne=replaceName(ligne)
    CSVTab+=createLigneBrut(ligne,permut,3)



# tests unitaires, jours 1 et 2
#dico=singleTest(l1,1,DenominationList,dico,0) # checker si bonnes listes
#dico=singleTest(l2,DenominationList1,DenominationList,dico,1)
#dico=singleTest(l3,DenominationList2,DenominationList,dico,2)
#dico=singleTest(l4,DenominationList,DenominationList,dico,3)

# test global, jours 2 et 3
#condJ2=[0,0,0,0]
#histJ2=[0,0,0,0]
#condJ3=[0,0,0,0]
#histJ3=[0,0,0,0]
#nb2=0
#nb3=0
#for i in dico.keys():
#    res=dico[i]
#    resJ2=res[4]
#    resJ3=res[5]
#    if len(resJ2)>0: 
#        nb2+=1
#        condUnitJ2=resJ2[5]
#        histUnitJ2=resJ2[6]
#        for j in range(4):
#            condJ2[j]+=condUnitJ2[j]
#            histJ2[j]+=histUnitJ2[j]
#    if len(resJ3)>0: 
#        nb3+=1
#        condUnitJ3=resJ3[5]
#        histUnitJ3=resJ3[6]
#        for j in range(4):
#            condJ3[j]+=condUnitJ3[j]
#            histJ3[j]+=histUnitJ3[j]
#        if int(i)==5:
#            print "cond puis hist j2"
#            print condUnitJ3
#            print histUnitJ3
#
#print "test 2e jour : "+str(nb2)+ " participants "
#print "effet par condition :",condJ2
#print "effet par histoire",histJ2
#print "\ntest 3e jour : "+str(nb3)+" participants "
#print "effet par condition :",condJ3
#print "effet par histoire",histJ3
#
#sorted_d = sorted(errDico.items(), key=operator.itemgetter(1))
#print sorted_d
# on rajoute les transcriptions phonétiques (test de dénomination)


   
# on ouvre le fichier csv existant pour récupérer les transcriptions existantes
if os.path.isfile('brut.csv'): 
    with open('brut.csv','r') as f:
        r=csv.reader(f)
        for l in islice(r,1,None):
            # réponse correcte
            PRep=PhoneticList[NamesList.index(l[8])]
            # si on trouve une transcription
            if len(l)>=12 and l[11]!='':
                transcription=l[11]
                for csvLigne in CSVTab:
                    strLigne=map(str,csvLigne)
                    if l[:8]==strLigne[:8]:
                        csvLigne.append(transcription)
                        # calcul de la distance avec la bonne réponse
                        d=10
                        transTab=transcription.split('_')
                        PRepTab=PRep.split('_')
                        d=min(10,edit_distance(transTab,PRepTab))
                        csvLigne+=[PRep,d]
                        # calcul de la distance minimale
                        dConf=10;Pconf='';
                        for Pname in PhoneticList:
                            PTab=Pname.split('_')
                            tmp=edit_distance(transTab,PTab)
                            if tmp<dConf:
                                Pconf=Pname;dConf=tmp;
                        conf=NamesList[PhoneticList.index(Pconf)]
                        csvLigne+=[conf,Pconf,dConf]
                    else:
                        csvLigne+=''
for csvLigne in CSVTab:
    rep=PhoneticList[NamesList.index(csvLigne[8])]
    if len(csvLigne)<=10 or (len(csvLigne)>=11 and csvLigne[10]==''):
        csvLigne+=['','',rep,10,'','',10]
    elif (len(csvLigne)==11 and csvLigne[10]!='') or (len(csvLigne)>=12 and (csvLigne[11]=='' or csvLigne[11]==''))   :
        csvLigne+=['',rep,10,'','',10]
firstLine=["id","jour","ordre histoires","ordre conditions","histoire","condition","type","reponse donnee","reponse attendue","evaluation","orthographe","transcription","reponse phonetique","distance","mot le plus proche","transcription","distance"]
WriteCSV(CSVTab,firstLine,'brut.csv')

