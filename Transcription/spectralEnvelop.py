# -*- coding: utf-8 -*
import os, glob
import stackprinter
import numpy as np
import scipy
import math
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, hilbert, find_peaks
path='../PythonUtils/'
stackprinter.set_excepthook(style='color')
from scipy.io import wavfile

exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())


def xT(y):
    return [i for i in range(len(y))]

def plotX(y,col='',zord=-1):
    x=xT(y)
    if zord==-1:
        if col=='':
            plt.plot(x,y)
        else:
            plt.plot(x,y,color=col)
    else:
        if col=='':
            plt.plot(x,y,zord)
        else:
            plt.plot(x,y,color=col,zorder=zord)
        

csvTab=[]
cpt=0
sigma=0.3;fs2=1000
for idNum in range(12):
    path='AudioList/id'+str(idNum).zfill(2)+'/'
    for filename in glob.glob(os.path.join(path, '*.wav')):
        [cond,story]=num2CS(filename)
        if story!=-1 and cpt<1:
            print(filename)
            # on lit le fichier
            fs, data = wavfile.read(filename)
            # on sous échantillonne
            len2=int(len(data)/fs*fs2)
            data2 = scipy.signal.resample(data,len2)
            # on calcule l'enveloppe et on la lisse
            h=hilbert(data2)
            A= np.abs(h)
            A_smooth = scipy.ndimage.filters.gaussian_filter(A, sigma*fs2, mode='constant')
            # on trouve les pics de l'enveloppe 
            hA=hilbert(A_smooth)
            hA_env=np.abs(hA)
            peaks, _ = find_peaks(hA_env, height=0,prominence=100,width=30,distance=30)
            scatterY=[hA_env[i] for i in peaks]
            print(peaks)
            plotX(data2,'y',1)
            plotX(hA_env,'r',2)
            plt.scatter(peaks,scatterY,s=20,zorder=3)
            plt.show()

            createLigne(filename,csvTab,[0])
            cpt+=1
firstLine=[]
WriteCSV(csvTab,firstLine,'brutDebit.csv')
