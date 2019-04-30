
# -*- coding: utf-8 -*
import tgt
import os, glob
import codecs
import ntpath
import csv
import numpy as np
import matplotlib.pyplot as plt
import sys
import runpy
import ntpath
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())


def createLigne(filename,nbSyll,meanf,varf,csvTab):
    name=ntpath.basename(filename)
    cOrder=name[6:10]
    sOrder=name[12:16]
    num=int(name[21:23])
    sujet=int(name[2:4])
    jour=int(name[18])
    [c,s]=num2CS(name)
    csvTab.append([sujet,jour,cOrder,sOrder,c,s,nbSyll,meanf,varf])


for idNum in range(6,7):
    path='Resultats/id'+str(idNum)+'/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        print(filename)
        [cond,story]=num2CS(filename)
        if cond!=-1:
            nbCSV=0
            nbSyll=0
            #f=tgt.io.read_textgrid(filename,encoding='utf-16-be')
            #annotations=f.get_tier_by_name('transcription').annotations
            #lenFile=int(annotations[-1].end_time*100)
            #fTab=np.zeros(lenFile)
            #for ann in annotations:
            #    t=ann.text.replace('transcription','').replace('.','').replace(',','')
            #    mots=t.split()
            #    mots=removeAnnot(mots)
            #    nbSyll=nbSyllOneAnnot(mots,dico)
            #    nbCSV+=nbSyll
            #    # on remplit le tableau de fréqunences 
            #    completeFTab(cond,story,nbSyll,ann,fTab)
