import os,glob
import csv
import pickle
#import matplotlib as plt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from numpy import mean,sqrt,diff
from scipy.signal import find_peaks
from collections import defaultdict
import ntpath
from operator import itemgetter
import time
from sklearn.linear_model import LinearRegression
import math
from scipy.stats import chisquare
import matplotlib.cm as cm
from scipy import stats
pathUtils='../PythonUtils/'
exec(open(pathUtils+'StoryCond.py').read())
exec(open(pathUtils+'Dist.py').read())
exec(open(pathUtils+'CSV.py').read())


dicoMoCap=OpenPkl('/home/steinhia/Documents/Alex/MoCapAnalysis/BikePoints.pkl')
dicoAudio=OpenPkl('/home/steinhia/Documents/Alex/Transcription/SyllablesPoints.pkl')
dicoHes=OpenPkl('/home/steinhia/Documents/Alex/Transcription/Hes.pkl')
dicoResume={}


def calcPhase(a,points):
    if points!=[]:
        miniList=[ i for i in points if i<a]
        maxiList=[ i for i in points if i>=a]
        if miniList!=[] and maxiList!=[]:
            mini=min(miniList, key=lambda x:abs(x-a))
            maxi=min(maxiList, key=lambda x:abs(x-a))
            phase=(a-mini)/(maxi-mini)#*2*math.pi*10
            return phase
    return -1

def calcStrob(aList,points):
    strob=[]
    for a in aList:
        phase=calcPhase(a,points)
        if phase!=-1:
            strob.append(phase)
    return strob

def plotLines(IPU,a=0):
    for x,y in IPU:
        plt.plot([x,y],[a,a],color='b')


def plotPoints(x,yval=0):
    y=[yval for i in x]
    plt.scatter(x,y,s=1)

def plot1D(y):
    x=[i for i in range(len(y))]
    plt.plot(x,y)
    plt.show()

def plotVerticalLines(IPU):
    for x,y in IPU:
        plt.plot([x,x],[0,4],color='g')

def syllDeb(IPU,syllables):
    syllD=[]
    for deb,fin in IPU:
        tmp=[i>deb for i in syllables]
        if True in tmp:
            syllD.append(syllables[tmp.index(True)])
    return syllD

def plotIPUdeb(IPU,syllables):
    syllD=syllDeb(IPU,syllables)
    for x in syllD:
        plt.plot([x,x],[0,4],color='g')
        


def plotData(IPU,syllables,picP,picV,picA):
    plotLines(IPU,0)
    plotPoints(syllables,1)
    plotPoints(picP,2)
    plotPoints(picV,3)
    plotPoints(picA,4)
    #plotVerticalLines(IPU)
    plotIPUdeb(IPU,syllables)
    plt.ylim((-5,10))
    plt.show()


# radii=hauteur des barres
# width=largeur des barres
def plotCircHistogram(radii):
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)

    N = len(radii)
    theta = np.arange(0.0, 2*np.pi, 2*np.pi/N) # liste des bins
    radii = 10*np.random.rand(N) # valeur renvoyée par l'histogramme
    width = np.pi/4*np.random.rand(N)
    bars = ax.bar(theta, radii, width=width, bottom=0.0)
    for r,bar in zip(radii, bars):
        bar.set_facecolor(plt.cm.jet(r/10.))
        bar.set_alpha(0.5)
    plt.show()


def circHisto(phase):
    #plt.style.use('seaborn')
    phase=[i*2*np.pi for i in phase]
    bins = 16
    fig = plt.figure()
    ax = fig.add_subplot(1, 2, 1)
    polar_ax = fig.add_subplot(1, 2, 2, projection="polar")

    # Plot "standard" histogram
    ax.hist(phase, bins=bins)
    # Fiddle with labels and limits
    ax.set_xlim([0, 2*np.pi])
    ax.set_xticks([0, np.pi/2,np.pi,3*np.pi/2,2*np.pi])
    ax.set_xticklabels([ r'$0$',r'$\pi/2$', r'$\pi$',r'$3\pi/2$',r'$2 \pi$'])

    # bin data for our polar histogram
    count, bines = np.histogram(phase,bins=bins)
    # Plot polar histogram
    width = (2*np.pi) /bins
    polar_ax.bar(bines[:-1], count,width,align='edge')
    # Fiddle with labels and limits
    polar_ax.set_xticks([0, np.pi/2,np.pi,3*np.pi/2])
    polar_ax.set_xticklabels([ r'$0$',r'$\pi/2$', r'$\pi$',r'$3\pi/2$'])
    polar_ax.set_rlabel_position(90)

    fig.tight_layout()
    plt.show()

# limite autour de 0.5
def detectHesitations(dicoHes):
    dico2={}
    for key,value in dicoHes.items():
        [hmP,hmD,undP,undD]=value
        [hmP2,hmD2,undP2,undD2,HPos]=[[],[],[],[],[]]
        if hmP!=[]:
            print(key2filename(key))
            for i,dur in enumerate(hmD):
                HPos.append(hmP[i])
                if dur>0.2:
                    hmP2.append(hmP[i])
                    hmD2.append(hmD[i])
            for i,dur in enumerate(undD):
                HPos.append(undP[i])
                if dur>0.5:
                    undP2.append(undP[i])
                    undD2.append(undD[i])
        dico2[key]=[hmP2,hmD2,undP2,undD2,HPos]
    return dico2
#            plt.hist(hmD)
#            plt.show()
#            plt.hist(undD)
#            plt.show()




csvTab=[]
firstLine=['nbCycles parole/mocap']


# Mocap, on échantillonne à 200HZ
for key,value in dicoMoCap.items():
    if '-' not in key:
        if key not in dicoResume.keys():
            dicoResume[key]=[[],[],[]]
        dicoResume[key][0]=value # pics de position, vitesse, accélération

# pour l'audio, les points sont en secondes
for key,value in dicoAudio.items():
    if key in dicoResume.keys():
        dicoResume[key][1]=value # syllabes et IPU

Hes=detectHesitations(dicoHes)
print(Hes)
for key,value in Hes.items():
    if key in dicoResume.keys():
        dicoResume[key][2]=value # positions des hésitations



# pas sur le début mais sur la syllabe suivant le début de l'ipu
# on crée le csv : rapport entre les nbs de cycles
phaseTab=[]
for key,value in dicoResume.items():
    # value[0] = données Mocap, value[0][0] = pics de position
    # si on a les données de position et d'audio
    if value[0][0]!=[] and value[1][0]!=[]:
        cond=" pieds" if key[3]=='2' else " mains"
        print("id"+key[:2]+" jour "+key[2]+" condition "+key[3] +cond)
        filename=key2filename(key)
        #syllables=value[1][0]
        #IPU=value[1][1]
        #IPUdeb=[i[0] for i in IPU]
        #IPUdeb=syllDeb(IPU,syllables)
        #IPUfin=[i[1] for i in IPU]
        picP=value[0][0]
        HesitP=value[2][0]
        UndP=value[2][2]
        HP=value[2][4]

        #picV=value[0][1]
        #picA=value[0][2]
        #val=len(syllables)/len(picP)
        #print("len",val)
        if HP!=[]:
            phase=calcStrob(HP,picP) # phase de la mocap à chaque syllabe
            phase=calcStrob(IPUdeb,picA) # phase de la mocap à chaque syllabe
            plot1D(phase)
            #plotData(IPU,syllables,picP,picV,picA)
            #phase=calcStrob(IPUdeb,picA) # phase de la mocap à chaque syllabe
            #phase1=calcStrob(IPUdeb,picV) # phase de la mocap à chaque syllabe
            #phase2=calcStrob(IPUdeb,picP) # phase de la mocap à chaque syllabe
            #phaseTab+=phase2
            #unif=chisquare(phase1)
            unif=stats.kstest(phase, 'uniform')
            #print(len(phase))
            print(unif)
            #print(phase)
            circHisto(phase)
            #createLigne(filename,csvTab,[val])
            #print(max(value[0]),max(value[1]),'\n')
#WriteCSV(csvTab,firstLine,'brutSynchro.csv')
#circHisto(phaseTab)

