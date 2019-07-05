# -*- coding: utf-8 -*
import os, glob
import tgt
import stackprinter
import numpy as np
import matplotlib.pyplot as plt
path='../PythonUtils/'
stackprinter.set_excepthook(style='color')
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

# on extrait les positions des syllabes et les intervales des IPU
def getPoints(dico,syllables,intervals):
    points=[]
    # position des syllabes
    for pt in syllables:
        points.append(pt.time)
    IPU=[]
    # intervalle des ipu
    for i in intervals:
        if i.text=='sounding':
            IPU.append([i.start_time,i.end_time])
    dico[cle]=[points,IPU]
    return [points,IPU]

# on extrait le nombre de pauses, leur durée totale et la liste des pauses
def getPauses(intervals):
    nbPauses=0
    lenPauses=0
    Pauses=[]
    for i in intervals:
        nbPauses+=(i.text=='silent') # booléen, 1 si pause
        lenPauses=(i.text=='silent')*(i.end_time-i.start_time) # ajoute durée si pause
        if lenPauses>0: # liste des durées de pauses
            Pauses.append(lenPauses)
    return [nbPauses,sum(Pauses),Pauses]

# on extrait le nombre d'IPU, leur durée totale, la moyenne et la variance de la durée
def getSpeech(intervals):
    nbSpeech=0
    lenSpeech=0
    IPU=[]
    for i in intervals:
        nbSpeech+=(i.text=='sounding')
        lenSpeech+=(i.text=='sounding')*(i.end_time-i.start_time)
        if lenSpeech!=0:
            IPU.append(lenSpeech)
    return [nbSpeech,lenSpeech,np.mean(IPU),np.var(IPU)]

# liste des intervalles avec début, fin, durée, nbSyll, débit moyen
def getRates(points,intervals):
    rates=[]
    for annot in intervals:
        begin=annot.start_time
        end=annot.end_time
        # nombre de syllabes contenues dans cet intervalle
        nbSyll=sum([begin<x<end for x in points])
        rates.append([begin,end,end-begin,nbSyll,nbSyll/(end-begin)]) # liste de [debut, fin, débit]
    return rates

# SpeechRate et ArticulationRate moyens
# ArticulationRate prend pas en compte les silences, SR si.
def meanRates(rates):
    meanR=0;nbSR=0;nbAR=0
    for i in rates:
        meanR+=nbSyll
        nbSR+=i[2]
        if i[3]!=0: # nbSyll -> si partie voisée
            nbAR+=i[2]
    return [meanR/nbSR,meanR/nbAR,nbSR,nbAR] # SR, AR, nbIPU, nb d'intervalles totaux

# débit au cours du temps par fenêtre glissante
# pourrait implémenter un débit pas par fenêtre fixe de 10s, mais par nombre fixe de syllabes -> temps pour prononcer 10 syllabes par exemple
def calcDebit(points,intervals):
    # début et fin du fichier / du rappel libre
    fin=intervals[-1].end_time
    deb=intervals[0].start_time
    d=[] # liste contenant le débit au cours du temps
    for i in np.arange(deb,fin-10-deb,1):
        d.append(sum([i<syll<i+10 for syll in points])/10) # nb syllabes dans l'intervalle
    x=[i for i in range(len(d))] # abscisse pour ploter
    # on plot le débit au cours du temps
    plt.plot(x,d)
    plt.show()
    # moyenne et variance du débit
    return [np.mean(d),np.var(d)]


csvTab=[]
dico={} # cle = id+jour+c
dicoInd={}
firstLine=['nbSyll','nbPauses','meanPauses','varPauses','SpeechRate','ArticulationRate','SRAR','SpeakingDuration','FileDuration','SDFD','meanIPU','varIPU','meanDeb','varDeb']
for idNum in range(2,22):
    n=str(idNum)
    print("id",idNum)
    path='AudioList/id'+str(idNum).zfill(2)+'/Syll/'
    for filename in glob.glob(os.path.join(path, '*')):
        print(filename)
        [cond,story]=num2CS(filename)
        # pour l'instant on peut analyser le débit que par condition, quand cond!=-1
        cle=str(idNum).zfill(2)+str(jourF(filename))+str(cond)
        f=readTG(filename)
        # on extrait les tiers du textgrid
        syllables=f.get_tier_by_name('syllables').annotations
        intervals=f.get_tier_by_name('silences').annotations
        # liste des IPU
        [points,IPU]=getPoints(dico,syllables,intervals)
        # liste des pauses
        [nbPauses,lenPauses,Pauses]=getPauses(intervals)
        # calcul du débit
        [meanDeb,varDeb]=calcDebit(points,intervals)
        nbSyll=len(points)
        # histogramme des pauses pour visualiser, découper en phrases marche pas
        # car pas de séparation nette
        #plt.hist(Pauses)
        #plt.show()
        meanPauses=np.mean(Pauses)
        varPauses=np.var(Pauses)
        #print(np.mean(Pauses),np.var(Pauses))
        [nbSpeech,lenSpeech,meanIPU,varIPU]=getSpeech(intervals)
        rates=getRates(points,intervals)
        [SpeechRate,ArticulationRate,FileDuration,SpeakingDuration]=meanRates(rates)
        # pour les rappels libres à court terme, crée le csv avec tous les rates calculés
        if cond!=-1:
            createLigne(filename,csvTab,[nbSyll,nbPauses,meanPauses,varPauses,SpeechRate,ArticulationRate,SpeechRate/ArticulationRate,SpeakingDuration,FileDuration,SpeakingDuration/FileDuration,meanIPU,varIPU,meanDeb,varDeb])
# écrit le csv
WriteCSV(csvTab,firstLine,'csvFiles/brutSyll.csv')

# stocke la position des syllabes et les IPU pour l'utiliser dans la partie synchro
# voir calcul du dico dans getPoints
SavePkl('SyllablesPoints.pkl',dico)


