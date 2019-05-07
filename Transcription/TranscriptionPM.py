
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
from functools import partial

path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())


def getWords(annotations):
    words=[]
    # on crée la liste des mots
    for ann in annotations:
        txt=ann.text
        if 'pseudo' in txt:
            print("transcription manquante ",filename)
        elif '_' in txt:
            words+=txt.split()
    return words

def split_(liste):
    for i,l in enumerate(liste):
        liste[i]=l.split('_')
    return liste

def findWord(PM,wd,l):
    lmap=list(map(partial(edit_distance,wd),l))
    mini=min(lmap)
    ind=lmap.index(mini)
    if mini/10<PM[ind]:
        PM[ind]=mini/10
    return PM

def completeLigne(ligne,filename,i):
        ligne[5]=i
        c=story2condition(filename,i)
        ligne[4]=c


l=split_(PhoneticList)
csvTabCT=[]
csvTabLT=[]
dico={}
for idNum in range(1,6):
    path='Resultats/id'+str(idNum)+'/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        [cond,story]=num2CS(filename)
        if cond!=-1:
            # pour les recall courts, on choisit le mot parmi 3
            PM=[1,1,1]
            f=readTG(filename)
            annotations=f.get_tier_by_name('commentaires').annotations
            # on trouve les mots correspondant à l'histoire, on les transforme en tab
            words=split_(getWords(annotations))
            # mots attendus
            a=(int(story))*3
            l2=l[a:a+3]
            # 3 évaluations
            for wd in words:
                PM=findWord(PM,wd,l2)
            createLigne(filename,csvTabCT,[sum(PM)]) 
        else:
            # pour les recall longs, on reconnait le mot parmi tous
            # on garde le nom jusqu'à n01, pas les bis,tris,001 etc
            name=ntpath.basename(filename)
            recallname=path+name[:23]+name[-9:]
            annotations=f.get_tier_by_name('commentaires').annotations
            words=split_(getWords(annotations))
            if recallname not in dico.keys():
                dico[recallname]=[1]*12
            for wd in words:
                dico[recallname]=findWord(dico[recallname],wd,l)
    # on crée une ligne par histoire pour chaque fichier du dico
    for key,value in dico.items():
        ligne1=createLigne(key,csvTabLT,[sum(value[:3])])
        completeLigne(ligne1,key,1)
        ligne2=createLigne(key,csvTabLT,[sum(value[3:6])])
        completeLigne(ligne2,key,2)
        ligne3=createLigne(key,csvTabLT,[sum(value[6:9])])
        completeLigne(ligne3,key,3)
        ligne4=createLigne(key,csvTabLT,[sum(value[9:])])
        completeLigne(ligne4,key,4)
firstLine=["score"]
WriteCSV(csvTabCT,firstLine,'brutTranscriptionCT.csv')
WriteCSV(csvTabLT,firstLine,'brutTranscriptionLT.csv')
