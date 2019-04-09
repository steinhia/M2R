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

def as_range(iterable): # not sure how to do this part elegantly
    l = list(iterable)
    if len(l) > 1:
        return [l[0], l[-1]]
    else:
        return [l[0],l[0]]


def create3Annotations(debut,fin):
    a1=tgt.core.Annotation(debut,fin,'transcription')
    a2=tgt.core.Annotation(debut,fin,'traduction')
    a3=tgt.core.Annotation(debut,fin,'commentaire')
    return [a1,a2,a3]

def add3Annotations(ann,T1,T2,T3):
    tierTranscription.add_annotation(ann[0])
    tierTraduction.add_annotation(ann[1])
    tierComm.add_annotation(ann[2])
    

for idNum in range(1,16):
    path='AudioList/id4/'#+str(idNum)+'/'
    MatPath=path+'Mat/'
    for filename in glob.glob(os.path.join(path, '*.wav')):
        name='id04-c1243-s1342-j3-n01.wav'
        matName=MatPath+os.path.basename(name)[:-3]+'mat'
        txtGName=filename[:-3]+'TextGrid'
        exists = os.path.isfile(txtGName) 
        if not exists: # on les écrase pas
            # on importe le signal
            fs, data = wavfile.read(filename)
            lenData=len(data)
            # on importe la détection de parties voisées
            file = scipy.io.loadmat(matName)
            mat=file['vadout']
            mat=[i[0] for i in mat]
            lenDetection=len(mat)
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
            tierTranscription=tgt.core.IntervalTier(0,lenData,'transcription')
            tierTraduction=tgt.core.IntervalTier(0,lenData,'traduction')
            tierComm=tgt.core.IntervalTier(0,lenData,'commentaires')
        
            # on crée les annotations
            for I in intervals:
                ann=create3Annotations(I[0],I[1])
                add3Annotations(ann,tierTranscription,tierTraduction,tierComm)
            txtGrid.add_tier(tierTranscription)
            txtGrid.add_tier(tierTraduction)
            txtGrid.add_tier(tierComm)
    
            tgt.io.write_to_file(txtGrid, txtGName)




