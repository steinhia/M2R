# -*- coding: utf-8 -*
import os, glob
import tgt
import stackprinter
import codecs
import numpy as np
import matplotlib.pyplot as plt
path='../PythonUtils/'
stackprinter.set_excepthook(style='color')
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())


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


def getPauses(intervals):
    nbPauses=0
    lenPauses=0
    Pauses=[]
    for i in intervals:
        nbPauses+=(i.text=='silent')
        lenPauses+=(i.text=='silent')*(i.end_time-i.start_time)
        Pauses.append(lenPauses)
    return [nbPauses,lenPauses,Pauses]

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

# liste des intervalles avec leur débit IPUpectif
def getRates(points,intervals):
    rates=[]
    for annot in intervals:
        begin=annot.start_time
        end=annot.end_time
        nbSyll=sum([begin<x<end for x in points])
        rates.append([begin,end,nbSyll/(end-begin)])
    return rates

def meanRates(rates):
    meanR=0;nbSR=0;nbAR=0
    for i in rates:
        dur=i[1]-i[0]
        meanR+=dur*i[2]
        nbSR+=dur
        if i[2]!=0:
            nbAR+=dur
    return [meanR/nbSR,meanR/nbAR,nbSR,nbAR]


def calcDebit(points,intervals):
    fin=intervals[-1].end_time
    deb=intervals[0].start_time
    d=[]
    for i in np.arange(deb,fin-10-deb,1):
        d.append(sum([i<syll<i+10 for syll in points])) # nb de syllabes dans l'iv
    x=[i for i in range(len(d))]
    d=[i/10 for i in d]
    #plt.plot(x,d)
    #plt.show()
    return [np.mean(d),np.var(d)]
 
def calcDebit2(points):
    T=np.diff(points)
    f=[1/i for i in T]
    return [np.mean(f),np.var(f)]

def plotSubjectResult():
    return 0

def plotIndividualsResults(dico):
    dicoInd={}
    for cle,valeur in dico.items():
        print(cle)
        SR=valeur[0]
        AR=valeur[1]
        SRAR=[i/j for i,j in zip(SR,AR)]
        FD=valeur[2]
        SD=valeur[3]
        nbSyll=valeur[4]
        nbPauses=valeur[5]
        x=[i for i in range(4)]
        plt.plot(x,SRAR)
        plt.show()
        

# TODO
def calcDebitVariable(points,intervals):
    a=1
    nbSyll=10
    fin=intervals[-1].end_time
   # deb=intervals[0].start
    d=[]
    for i in np.arange(0,fin-5,1/a):
        d.append(sum([i<syll<i+5 for syll in points])) # nb de syllabes dans l'iv
    #x=[i/a for i in range(len(d))]
    #plt.plot(x,d)
    #plt.show()
    return d

# nbsyll,nbPauses,SpeechRate,ArticulationRate,SpeakingDuration,originalDuration
csvTab=[]
dico={} # cle = id+jour+c
dicoInd={}
firstLine=['nbSyll','nbPauses','SpeechRate','ArticulationRate','SRAR','SpeakingDuration','FileDuration','SDFD','meanIPU','varIPU','meanDeb','varDeb','meanDeb2','varDeb2']
for idNum in range(1,22):
    n=str(idNum)
    print("id",idNum)
    path='AudioList/id'+str(idNum).zfill(2)+'/Syll/'
    for filename in glob.glob(os.path.join(path, '*')):
        #print(filename)
        [cond,story]=num2CS(filename)
        # pour l'instant on peut analyser le débit que par condition, quand cond!=-1
        cle=str(idNum).zfill(2)+str(jourF(filename))+str(cond)
        print(key2filename(cle))
        f=readTG(filename)
        syllables=f.get_tier_by_name('syllables').annotations
        intervals=f.get_tier_by_name('silences').annotations
        [points,IPU]=getPoints(dico,syllables,intervals)
        [meanDeb,varDeb]=calcDebit(points,intervals)
        [meanDeb2,varDeb2]=calcDebit2(points)
        print(calcDebit2(points))
        #dico[cle].append(deb)
        nbSyll=len(points)
        [nbPauses,lenPauses,Pauses]=getPauses(intervals)
        # histogramme pour découper en phrases : :/
        #plt.hist(Pauses)
        #plt.show()
        [nbSpeech,lenSpeech,meanIPU,varIPU]=getSpeech(intervals)
        rates=getRates(points,intervals)
        [SpeechRate,ArticulationRate,FileDuration,SpeakingDuration]=meanRates(rates)
        if cond!=-1:
            if str(idNum) not in dicoInd.keys():
                dicoInd[n]=[[-1 for i in range(4)] for i in range(6)]
            dicoInd[n][0][cond]=SpeechRate
            dicoInd[n][1][cond]=ArticulationRate
            dicoInd[n][2][cond]=FileDuration
            dicoInd[n][3][cond]=SpeakingDuration
            dicoInd[n][4][cond]=nbSyll
            dicoInd[n][5][cond]=nbPauses
        #print(SpeechRate/ArticulationRate)
        if cond!=-1:
            createLigne(filename,csvTab,[nbSyll,nbPauses,SpeechRate,ArticulationRate,SpeechRate/ArticulationRate,SpeakingDuration,FileDuration,SpeakingDuration/FileDuration,meanIPU,varIPU,meanDeb,varDeb,meanDeb2,varDeb2])
WriteCSV(csvTab,firstLine,'brutSyll.csv')
SavePkl('SyllablesPoints.pkl',dico)
plotIndividualsResults(dicoInd)
#print(dico.keys())
#print(dico)
