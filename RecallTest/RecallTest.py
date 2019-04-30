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

# calcul de la distance pour le test de dénomination 

#Voy=['a','e','y','i','o','u','@','9','2:','OY','aU','aI','2:6','e:6','o:6','y:6','96','E6','u:6','E:6','O:6','i:6','I6','O6','Y6','U6','a:6','a6']
#
## 6 n'est utilisé qu'en diphtongue, sinon remplacé par @R
## sinon 6 ne rentre pas dans les schémas CVCVCVC, statut ni de voyelle ni consonne
#Cons=['b','k','d','f','g','h','j','l','m','n','p','r','s','t','v','N','z','Z','C','ts','tS','dZ','S','x','?']
# # an=@,in=5,on=6,eu=9,j=Z,gn=N,ch=S
#def createNaturalClasses():
## on met le schwa dans ouvert,semi-ouvert,ferme,arrondi,etire,voyAnt,voyPost,nasal,oral
## ok car prend en compte les classes contenant le schwa et pas la voyelle en question
## on a donc dist(*,voy)=0.55
## [voise,sourd,lieuAvant,Median,Posterieur,nasal,oral,occlusif,fricatif,liquide,ouvert,semi-ouvert,ferme,arrondi,etire,voyAnterieur,voyPosterieur]
#    return ['bvdzZgRmnNjl','pftsSkxCh','pbmfv','tdnszlSZ','xCkgRNhj','mnN','ptkbdg','fsSvzZChxR','lj','a','oe@9','iyu','yuo9','iea@','iye@','uo','a9']
#NaturalClasses=createNaturalClasses()
#
#def _edit_dist_init(len1, len2):
#    lev = []
#    for i in range(len1):
#        lev.append([0] * len2)  # initialize 2D array to zero
#    for i in range(len1):
#        lev[i][0] = i  # column 0: 0,1,2,3,4,...
#    for j in range(len2):
#        lev[0][j] = j  # row 0: 0,1,2,3,4,...
#    return lev
#
#def phonemeDist(NaturalClasses,c1,c2):
#    n=0;n1=0;n2=0;
#    c1=c1.lower()[0]
#    c2=c2.lower()[0]
#    if c1==c2:
#        return 0
#    for s in NaturalClasses:
#        if c1 in s and c2 in s:
#            n+=1
#        elif c1 in s:
#            n1+=1
#        elif c2 in s:
#            n2+=1
#    if n+n1+n2!=0:
#        return float((n1+n2))/float((n+n1+n2))
#    return 1
#
#def _edit_dist_step(lev, i, j, s1, s2, substitution_cost=1.0/0.7):
#    c1 = s1[i - 1]
#    c2 = s2[j - 1]
#    # insertions ou deletions
#    # skipping a character in s1
#    a = lev[i - 1][j] + 1
#    # skipping a character in s2
#    b = lev[i][j - 1] + 1
#    # substitution
#    c = lev[i - 1][j - 1] + (substitution_cost*phonemeDist(NaturalClasses,c1,c2))
#    # pick the cheapest
#    lev[i][j] = min(a, b, c)
#
#
#def edit_distance(s1, s2, substitution_cost=1.0/0.7):
#    # set up a 2-D array
#    s1=[x for x in s1 if x!='.']
#    s2=[x for x in s2 if x!='.']
#    len1=len(s1);len2=len(s2)
#    lev=_edit_dist_init(len1+1,len2+1)
#    for i in range(len1):
#        for j in range(len2):
#            _edit_dist_step(lev,i+1,j+1,s1,s2,substitution_cost=substitution_cost)
#    return lev[len1][len2]
#
#ListOfURL=['fyJR1Nd5bdYf.png',
#'RXu0QM7rpAyU.png',
#'Qgz50gtfWEKz.png',
#'suiy1ohYtpMc.png',
#'0b30ZuqmWz8O.png',
#'n55EF0EPH3eh.png',
#'UR7y2KDxGdkV.png',
#'YvwxbuziPnUW.png',
#'fYjGeVqjiINB.png',
#'tLIgcDR9urkS.png',
#'YEMx5pW9l952.png',
#'XnQSXSzM0tU7']
#
#
## f(4)=1 : numero d'image -> numero d'histoire
#def num2s(imgNum):
#    return imgNum/3
#
## f('Tereinat')=3 : nom de PM -> numero du PM
#def name2num(word):
#    return NamesList.index(word)
#
## f(3)='Tereinat' : numero du PM -> nom du PM
#def num2name(i):
#    return NamesList[i]
#
## f('img3')='Tereinat' : nom de l'image -> nom du PM
#def imgName2name(imgName):
#    if imgName!='':
#        num=int(imgName[3:])
#        name=NamesList[num]
#        return name
#    return -1
#
## f('Tereinat')=1 : nom du PM -> numero d'histoire
#def name2s(word):
#    return num2s(name2num(word))
#
##f(3)='personnage'
#def num2type(i):
#    if i%3==0:
#        return 'personnage'
#    elif i%3==1:
#        return 'maison'
#    else:
#        return 'vehicule'
#def name2type(wd):
#    i=NamesList.index(wd)
#    return num2type(i)
#
#
## les histoires vont de 0 à 3, les mots de 0 à 11, les conditions de 0 à 3
## Bonnes réponses du test 
## noms de à à 11 correspondant aux images
#NamesList=['Mielbete','Keimase','Sonistik','Tereinat','Ligete','Mattendich','Soltete','Madikten','Wecktellin','Lasgelich','Zulergen','Melare']
#PhoneticList=['m_i_l_b_e_t_@','k_aI_m_a_s_@','z_o_n_i_s_t_i_k','t_e_r_aI_n_a_t','l_i_g_e_t_@','m_a_t_@_n_d_i_C','z_o_l_t_e_t_@','m_a_d_i_k_t_@','v_@_k_t_e_l_i_n','l_a_s_g_e_l_i_C','ts_u_l_@_r_g_@','m_e_l_a_r_@']
#
#
#
#
## liste des mots demandés pour l'identification (questions = mots, réponses = img)
#IdentificationListNum=[2,1,4,0,10,5,7,3,11,6,8,9]
#IdentificationListNumUnit=[1,2,0,3,4,5,6,8,7,10,9,11]
#IdentificationList=map(num2name,IdentificationListNum)
#IdentificationListUnit=map(num2name,IdentificationListNumUnit)
##IdentificationList1=map(num2name,[1,2,0])
##IdentificationList2=map(num2name,[3,4,5])
##IdentificationList3=map(num2name,[6,8,7])
##IdentificationList4=map(num2name,[10,9,11])
#
## liste des mots espérés pour la pour la dénomination (réponses, questions = img)
#DenominationList=map(num2name,[0,1,2,6,7,8,3,4,5,9,10,11])
#DenominationListUnit=map(num2name,[2,0,1,3,4,5,8,7,6,9,10,11])
##DenominationList1=map(num2name,[2,0,1])
##DenominationList2=map(num2name,[3,4,5])
##DenominationList3=map(num2name,[8,7,6])
##DenominationList4=map(num2name,[9,11,10])
#

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
        res.append([sujet,jour,'s '+str(ordreS),'c '+str(ordreC),story,nameType,condition,name,answer,b])

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
    CSVTab+=createLigneBrut(ligne,permut)
    dico[idPart][idTest]=[ligne[2:14],ligne[14:],0,ident,0,identCond,identHist]

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
                print transcription
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

firstLine=["id","jour","ordre histoires","ordre conditions","histoire","type","condition","reponse donnee","reponse attendue","evaluation","orthographe","transcription","reponse phonetique","distance","mot le plus proche","transcription","distance"]
WriteCSV(CSVTab,firstLine,'brut2.csv')


#with open('brut2.csv', mode='w') as f:
#    writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#    writer.writerow(["id","jour","ordre histoires","ordre conditions","histoire","type","condition","reponse donnee","reponse attendue","evaluation","orthographe","transcription","reponse phonetique","distance","mot le plus proche","transcription","distance"])
#    listLines=[]
#    for i in CSVTab:
#        if i not in listLines:
#            writer.writerow(i) 
#        listLines.append(i)
    
# confusions :
# entre noms de la même histoire ?
# entre noms de la même sorte ?
# entre noms se ressemblant ? -> distance moyenne entre les confusions
# entre formes se ressemblant ?
# par image (possibilité) ?
# par texte (question) ?
