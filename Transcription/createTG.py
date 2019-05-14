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
import scipy.io
import tgt
from scipy.io import wavfile
from itertools import groupby, count
import os, glob
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

def as_range(iterable): # not sure how to do this part elegantly
    l = list(iterable)
    if len(l) > 1:
        return [l[0], l[-1]]
    else:
        return [l[0],l[0]]

# crée les 3 tiers
def create3Annotations(debut,fin):
    a1=tgt.core.Annotation(debut,fin,'transcription')
    a2=tgt.core.Annotation(debut,fin,'traduction')
    a3=tgt.core.Annotation(debut,fin,'commentaire')
    return [a1,a2,a3]

# ajoute une annotation
def add3Annotations(ann,T1,T3):
    tierTranscription.add_annotation(ann[0])
    #tierTraduction.add_annotation(ann[1])
    tierComm.add_annotation(ann[2])
    

for idNum in range(17,22):
    path='AudioList/id'+str(idNum).zfill(2)+'/'
    MatPath=path+'Mat/'
    for filename in glob.glob(os.path.join(path, '*.wav')):
        #name='id07-c2134-s2431-j1-n06.wav'
        #filename=path+name
        matName=MatPath+os.path.basename(filename)[:-3]+'mat'
        txtGName=filename[:-3]+'TextGrid'
        exists = os.path.isfile(txtGName) 
        if not exists or True: # on les écrase pas
            # on importe le signal
            fs, data = wavfile.read(filename)
            lenData=len(data)
            # on importe la détection de parties voisées
            file = scipy.io.loadmat(matName)
            mat=file['vadout']
            # on importe des [0 0 0 1 1 1 1 0 0]
            mat=[i[0] for i in mat]
            lenDetection=len(mat)
            # on fait un resemple car le detect voice est échantillé à 10 ms
            r=float(lenData)/(float(lenDetection)*float(fs))
            # on met ça dans le format début-fin
            indicesTab=[i for i in range(len(mat)) if mat[i]==1]
            GB=groupby(indicesTab, lambda n, c=count(): n-next(c))
            intervals=[as_range(g) for _, g in groupby(indicesTab, key=lambda n, c=count(): n-next(c))]
            intervals=[[i*r,j*r] for i,j in intervals]
            for i in range(1,len(intervals)-1):
                intervals[i][0]=max(intervals[i-1][1],intervals[i][0]-0.2)
                intervals[i][1]=min(intervals[i+1][0],intervals[i][1]+0.2)
        
            # on crée le textGrid
            txtGrid=tgt.core.TextGrid('essai.TextGrid')
            tierTranscription=tgt.core.IntervalTier(0,lenData/fs,'transcription')
            tierComm=tgt.core.IntervalTier(0,lenData/fs,'commentaires')
        
            # on crée les annotations
            for I in intervals:
                ann=create3Annotations(I[0],I[1])
                add3Annotations(ann,tierTranscription,tierComm)
            txtGrid.add_tier(tierTranscription)
            #txtGrid.add_tier(tierTraduction)
            txtGrid.add_tier(tierComm)
    
            tgt.io.write_to_file(txtGrid, txtGName)
            tgt.io.read_textgrid(txtGName)




