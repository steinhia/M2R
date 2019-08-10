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
from functools import partial
import pickle

path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())




# attention, on a transformé tous les 1 en 5, et tous les 2 en 9, E en e

# renvoie True ou False pour indiquer si les triphones du mot sont plausibles
def MotsTriphoneOk(mot,list3):
    # en allemand, pas de schwa, seulement un allophone de è 
    for i in range(0,len(mot)-2): # i = position dans le mot, triphone->arrêt -2
        tri=mot[i:i+3] # triphone à tester
        if tuple(tri) not in list3[i]: # on regarde la liste correspondante
            return False # s'il n'est pas dedans on renvoie faux
    return True # on renvoie vrai si tous les triphones sont ok
 
# on ne peut pas faire des histogrammes de tuples, on choisit l'indice et pas la syll
# on a 3 histogrammes de syllabes selon CV CVC 
# on génère un mot selon les distrib de fréquences de la langue allemande
# on génère un mot trisyllabique du schéma considéré
def GenerateOneWord(Schema,dicoHisto,list3,Mots):
    histo=[[],[],[]] # un histogramme par syllabe du schéma
    for i in range(3):
        # les clés de dicoHisto sont "CV" "CVC"
        # histo[i] = ex dicoHisto["CV"] = [[syll,f],[syll,f]...]
        # Schema=["CV","CV","CVC"] -> schema[i]="CV"
        histo[i]=dicoHisto[Schema[i]] # 3 histogrammes pour les 3 syllabes
    word=[]
    for i in histo: # chacune des 3 distrib (ex CV puis CV puis CVC) -> on génère 1 sy
        n=len(i) # on va choisir random entre 0 et n-1 -> on génère l'index de la syll
        pb=[l[1] for l in i] # distribution de proba
        pb=[j/sum(pb) for j in pb] # on normalise les poids
        word+=list(i[np.random.choice(range(n),1,p=pb)[0]][0]) #indices,weights
    # attention si un jour boucle infinie en changeant un paramètre : fct récursive
    if not MotsTriphoneOk(word,list3): # si mot non conforme
        return GenerateOneWord(Schema,dicoHisto,list3,Mots) #on regénère
    return word

# pour 1 mot considéré, renvoie la proba phonotactique : phoneme*biphone
def WordWithPba(mot):
    PbaPhono=WordSegmentFreq(mot) # proba positionnelle du phonème
    PbaBiphone=WordBiphoneFreq(mot) # du biphone
    return [mot,PbaPhono,PbaBiphone,PbaPhono*PbaBiphone]

# génère la liste des pseudo-mots
def GeneratePM(SyllHisto,nbMotsPhono,list3,pMoy,pMoyBiPhones,printWords=False):
     # on génère les pseudo mots, puis on garde les + probables
    MotsOpti=[[],[],[]]   
    # on génère les schémas 1 par 1
    for i,schema in enumerate([["CV","CV","CVC"],["CV","CVC","CVC"],["CVC","CV","CVC"]]):
        print "schema " + str(i) + " : " + str(schema) # on affiche le schéma en cours
        Mots=[] # liste des mots à remplir
        for j in range(20): # on va générer 5000 mots
            mot=GenerateOneWord(schema,SyllHisto,list3,Mots) # on génère un mot
            Mots.append(mot) # on l'ajoute à la liste
        MotsWithPba=map(WordWithPba,Mots) # on calcule les probas phonotactiques
        # on trie la liste selon pba pho*biphone pour ne garder que les plus probables
        SortedMotsWithPba=sorted(MotsWithPba, key=operator.itemgetter(3),reverse=True)
        cpt=0
        # on a trié et mis en haut les plus grandes probas phonotactiques
        # maintenant on sélectionne les mots qu'on va garder
        for word in SortedMotsWithPba: # liste des mots potentiels
            keep=True # booleen : on garde le mot pour la liste finale ?
            if cpt>=nbMotsPhono: # nombre de mots qu'on veut garder
                keep=False # si on en a déjà gardé assez, on garde pas celui là
            else: # on le garde si il est pas trop proche d'un autre mot gardé
                for j in range(3): # mot schéma 2 doit pas ressembler à 1 mot schéma 1
                    for fWord in MotsOpti[j]: # on parcourt la liste des mots gardés
                        # s'il est trop proche d'un mot sélectionné -> garde pas
                        if edit_distance(word[0],fWord)<3:
                            keep=False
            if keep: # si on le garde, on l'ajoute à la liste des mots sélectionnés
                MotsOpti[i].append(word[0]) # i= schéma en cours
                cpt+=1
        if printWords:
            print "Après selection phonotactique, les " + str(nbMotsPhono) + " mots retenus sont : " # début de la sélection des pseudo-mots
            for wd in MotsOpti[i]:
                print("".join(wd))
    return MotsOpti
 

# ce qui est important, c'est la ressemblance avec un mot en particulier,
# pas la similarité avec la base (formule somme(exp(-dij)))
# calcule la plus courte distance entre mot et un mot du dictionnaire
# renvoie [mot, distance, mot le plus proche]
def calcOneDist(mot,AllWordsList):
    # distance entre le mot et tous les mots de la base
    Wds=[x[0] for x in AllWordsList]
    dList=[edit_distance(mot,i) for i in Wds]
    # distance minimale
    dMin=min(dList)
    # mot du dictionnaire qui minimise la distance au PM en entrée
    neighbor=AllWordsList[dList.index(dMin)][0]
    for x in AllWordsList :
        # si c'est un mot suffisamment long (a est inclus dans bcp de mots)
        # inclus dans le pseudo-mot, ou si le pseudo-mot est inclus dans le mot
        # di dictionnaire -> distance à 0 -> trop proches, on va pas le garder
        if (len(x[0])>3 and x[0] in mot and x[1]>1) or (mot in x[0] and x[1]>1):
            neighbor=x[0]
            dMin=0
    return([mot,dMin,neighbor])
    

# calcule la liste des distance entre les pseudo-mots générés et la base
def calcDist(Mots,AllWordsList,printWords=False):
    if printWords:
        print("distance des mots à la base : ")
    # on calcule leur distance avec la base
    WordDist=[[],[],[]] # 3 schémas
    for schema in range(3):
        if printWords:
            print "schema "+str(schema)
        for mot in Mots[schema] :# pseudo-mots d'un certain schéma
            d=calcOneDist(mot,AllWordsList) # calcul de la distance à la base
            if (d[1]>=1 and d[1] <=2.0): # on print ceux à distance entre 1 et 2
                1#print d
            WordDist[schema].append(d) # on les ajoute tous
            if printWords:
                print "".join(d[0])," proche de ","".join(d[2]), " : d = ",str(d[1])
    return WordDist

# évaluation au moment de choisir les 60 et lorsqu'on en garde que 36
def evalScore(tab,PositionalSegmentFreq):
    # liste des mots choisis
    liste=[[x[0] for x in t] for t in tab]
    liste=liste[0]+liste[1]+liste[2] # on transforme liste3Schémas en 1 liste
    simil=[[x[1] for x in t] for t in tab] # liste des distances
    simil=simil[0]+simil[1]+simil[2] # en 1 seule liste
    f=0
    for i in liste: # on parcourt tous les mots
        f+=WordSegmentFreq(i) # on évalue la proba phonotactiue positionnelle
    f/=len(liste)
    var=np.var(simil) # on évalue la variance de la distance à la base 
    return [var,f] # si veut des mots similaires

# calcule la proba phonotactique des phonèmes d'un mot
# à partir du dictionnaire PositionalSegmentFreq
def WordSegmentFreq(mot):
    res=0
    mot=[ i for i in mot if i!='.'] # on enlève les . du mot
    for i,pho in enumerate(mot): # pour chaque phonème pho, position i
        res+=PositionalSegmentFreq[pho][i] # on ajoute sa probabilité à cete pos i
    return res # comme c'est des log fréquences, on ajoute simplement les probas

# proba phonotactique biphone d'un mot dans le dico
# proba se multiplient, ici logprobas -> on ajoute
def WordBiphoneFreq(mot):
    res=0
    mot=[ i for i in mot if i!='.'] # on enlève les . du mot
    for i in range(len(mot)-1):
        bipho=tuple(mot[i:i+2]) # on extrait le biphone
        if bipho in PositionalBiphoneFreq.keys(): # s'il fait partie des biphones
            res+=PositionalBiphoneFreq[bipho][i] # on rajoute la proba biphone
        else:
            return 0 
    return res


#### Main





with open('germanWords.pkl','rb') as f:
    [WordsList,AllWordsList,PositionalSegmentFreq,PositionalBiphoneFreq,list3,HistoSyll]=pickle.load(f)
# pour ALLWL, on a juste besoin de l'écriture
# proba moyenne des mots du dictionnaire
pMoy=float(sum(map(WordSegmentFreq,[x[0] for x in WordsList])))/float(len(WordsList))
pMoyBiPhones=float(sum(map(WordBiphoneFreq,[x[0] for x in WordsList])))/float(len(WordsList))

# classes naturelles des phonemes : dans PythonUtils
NaturalClasses=createNaturalClasses()

### génération des pseudos mots

nbMotsPhono=4 # première génération, nombre de mots par schéma
nbMotsDist=2 # taille de la liste finale, après sélection par la distance

for n in range(1):
    # génère la liste aléatoirement, on sélectionne avec les probas phonotactiques, 
    # renvoie des mots assez loin les uns des autres
    Mots=GeneratePM(HistoSyll,nbMotsPhono,list3,pMoy,pMoyBiPhones,True)
    

    # on calcule les distances des mots au dictionnaire
    # on garde les mots entre distance 1 et 2 
    # on sélectionne les mots les plus loin de la base pour chaque liste
    WordDist=calcDist(Mots,WordsList,True)
    WordDistOk=[[],[],[]] # liste de 3 schémas contenant [[mot,dist,neighbor],[m,d,n]..
    # on trie les 3 listes de WordDist (3 schémas)pour avoir les plus grandes distances
    for i,l in enumerate(WordDist):
        WordDistOk[i]=sorted(WordDist[i],key=operator.itemgetter(1),reverse=True)
    # on garde seulement les distances entre 1 et 2
    for i,l in enumerate(WordDistOk):
        WordDistOk[i]=[x for x in WordDistOk[i] if x[1]>=1 and x[1]<=2]
    # on obtient donc une liste triée par distance décroissante avec 1<=d<=2
    # on garde seulement certains mots : les nbMotsDist premiers
    for i,l in enumerate(WordDistOk):
        WordDistOk[i]=WordDistOk[i][:nbMotsDist]
    # liste choisie : on rassemble en une lsite et on garde que les mots
    MotsOpti=WordDistOk[0]+WordDistOk[1]+WordDistOk[2] # plus une liste par schéma
    MotsOpti=[i[0] for i in MotsOpti] # pour avoir juste le mot, pas la distance
    print("MO",MotsOpti)
    # probas pour cette liste
    PbaPhono=sum([WordSegmentFreq(mot) for mot in MotsOpti])/(pMoy*len(MotsOpti))
    PbaBiphone=sum([WordBiphoneFreq(mot) for mot in MotsOpti])/(pMoyBiPhones*len(MotsOpti))
    PbaOpti=[PbaPhono,PbaBiphone]
    print "\n"
    print "Probas phonotactiques",PbaOpti
    print "\n"


