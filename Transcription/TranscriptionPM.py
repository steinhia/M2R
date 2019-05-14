
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
import stackprinter
stackprinter.set_excepthook(style='color')
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())




# i = histoire
def completeLigne(ligne,filename,i):
        ligne[5]=i # histoire
        c=story2condition(filename,i)
        ligne[4]=c # condition

############# récupération des mots

def printWords(idNum,jour,cond,CT=True):
    for idRange in range(1,13):
        path='Resultats/id'+str(idRange)+'/'
        for filename in glob.glob(os.path.join(path, '*.TextGrid')):
            liste=['id'+str(idNum).zfill(2),'j'+str(jour)]
            if all(i in filename for i in liste):
                [c,_]=num2CS(filename)
                if c==cond and CT:
                    print(filename,'\n',getWords(filename),'\n')
                elif not CT and c==-1:
                    print(filename,'\n',getWords(filename),'\n')

def split_(liste):
    for i,l in enumerate(liste):
        liste[i]=l.split('_')
    return liste

# récupère la liste de mots transcrits
def getWords(filename):
    f=readTG(filename)
    annotations=f.get_tier_by_name('commentaires').annotations
    words=[]
    for ann in annotations:
        txt=ann.text
        if 'pseudo' in txt: # oubli d'annotation
            print("transcription manquante ",filename)
        elif '_' in txt:
            txtSplit=txt.split()
            words+=txtSplit
            # on trouve les transcriptions avec un pb de _
            for i in txtSplit:
                for letter in i:
                    if len(letter)>1 and letter !='aI' and letter!='ts':
                        print("transcription fausse ",filename,i)
    return split_(words)



######## calcul des scores ########

def findWord(PM,wd,l):
    lmap=list(map(partial(edit_distance,wd),l))
    mini=min(lmap)
    ind=lmap.index(mini)
    if 1-mini/10>PM[ind]:
        PM[ind]=1-mini/10
    return PM


def findWord_add(PM_add,wd,l):
    lmap=list(map(partial(edit_distance,wd),l))
    mini=min(lmap)
    ind=lmap.index(mini)
    if 1-mini/10>0.5:
        PM_add[ind]+=1-mini/10
    return PM_add

def calcScoreShort(filename):
    PM=[0,0,0];PM_add=[0,0,0]
    # mots attendus
    a=(int(story))*3
    l2=l[a:a+3]
    words=getWords(filename)
    for wd in words:
        PM=findWord(PM,wd,l2)
        PM_add=findWord_add(PM_add,wd,l2)
    return [PM,PM_add]

# les scores s'étalent sur plusieurs fichiers -> dico cumulatif
def calcScoreLong(filename,dico,dico_add):
    # pour les recall longs, on reconnait le mot parmi tous
    # on garde le nom jusqu'à n01, pas les bis,tris,001 etc
    words=getWords(filename)
    name=ntpath.basename(filename)
    recallname=path+name[:23]+name[-9:]
    if recallname not in dico.keys():
        dico[recallname]=[0]*12
        dico_add[recallname]=[0]*12
    for wd in words:
        dico[recallname]=findWord(dico[recallname],wd,l)
        dico_add[recallname]=findWord_add(dico_add[recallname],wd,l)
    return [dico,dico_add]

######### main ###########"

l=split_(PhoneticList)
csvTabCT=[]
csvTabLT=[]
for idNum in range(1,13):
    path='Resultats/id'+str(idNum)+'/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        [cond,story]=num2CS(filename)
        if cond!=-1:
            [PM,PM_add]=calcScoreShort(filename)
            createLigne(filename,csvTabCT,[sum(PM),sum(PM_add)]) 
        else:
            # pour les recall longs, on reconnait le mot parmi tous
            # on garde le nom jusqu'à n01, pas les bis,tris,001 etc
            [dico,dico_add]=[{},{}]
            [dico,dico_add]=calcScoreLong(filename,dico,dico_add)
    # on crée une ligne par histoire pour chaque fichier du dico (LT)
    # on trouve les pseudo-mots par histoire, on en déduit la condition
    for key,value in dico.items():
        ligne1=createLigne(key,csvTabLT,[sum(value[:3]),sum(dico_add[key][:3])])
        completeLigne(ligne1,key,0)
        ligne2=createLigne(key,csvTabLT,[sum(value[3:6]),sum(dico_add[key][3:6])])
        completeLigne(ligne2,key,1)
        ligne3=createLigne(key,csvTabLT,[sum(value[6:9]),sum(dico_add[key][6:9])])
        completeLigne(ligne3,key,2)
        ligne4=createLigne(key,csvTabLT,[sum(value[9:]),sum(dico_add[key][9:])])
        completeLigne(ligne4,key,3)
firstLine=["score","scoreCumule"]
WriteCSV(csvTabCT,firstLine,'brutTranscriptionCT.csv')
WriteCSV(csvTabLT,firstLine,'brutTranscriptionLT.csv')

printWords(1,2,1,False)
