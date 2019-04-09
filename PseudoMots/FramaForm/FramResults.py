
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


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        try:
            yield line.encode('utf-8')
        except Exception as e:
            1

def openCSV(csvString,delim=''):
    with open(csvString) as csvfile:
        if delim==",":
            rd=csv.reader(utf_8_encoder(csvfile),delimiter=',')
        else:
            rd=csv.reader(utf_8_encoder(csvfile),delimiter=',')
        return rd


def extractWordsWithFreq(csvString):
    f=codecs.open(csvString,"r",encoding="utf-8")
    l = f.read().encode('utf-8').splitlines()


#f=codecs.open("association_mots_images.ods","r",encoding="utf-8")
#l = f.read().encode('utf-8').splitlines()
#with open("association_mots_images.ods") as csvfile:
#    rd=csv.reader(utf_8_encoder(csvfile),delimiter=' ')
#    for i in rd :
#        print i
#

ListOfURL=['fyJR1Nd5bdYf.png',
'RXu0QM7rpAyU.png',
'Qgz50gtfWEKz.png',
'UR7y2KDxGdkV.png',
'YvwxbuziPnUW.png',
'fYjGeVqjiINB.png',
'suiy1ohYtpMc.png',
'0b30ZuqmWz8O.png',
'n55EF0EPH3eh.png',
'tLIgcDR9urkS.png',
'YEMx5pW9l952.png',
'EJjP4l0L4MO8.png']

def transfo(l):
    res=[]
    for i,string in enumerate(l):
        for j,s in enumerate(ListOfURL):
            if s in string:
                l[i]=j+1
        res.append(l[i])
    return res



f=codecs.open("nonwords_selection.csv","r",encoding="utf-8")
l = f.read().encode('utf-8').splitlines()



res=[]
for i in l:
    res.append(i.split('\t'))# y avait un |3:], pourquoi ??? TODO
WordList=res[0][0:len(res[0]):2]
WordList=WordList[:45]
dico1={} # V CV CVC
dico2={} # CV CV CV
dico3={} # CV CV CVC



for wd in WordList[:15]:
    dico1[wd]=[[],[],[]]
for wd in WordList[15:30]:
    dico2[wd]=[[],[],[]]
for wd in WordList[30:45]:
    dico3[wd]=[[],[],[]]

for i in range(1,len(res)):
    # scores
    for wd,score in zip(WordList[:15],res[i][0:30:2]):
        if score.isdigit():
            dico1[wd][0].append(int(score))
    # voisins
    for wd,mot in zip(WordList[:15],res[i][1:30:2]):
        if score!='' and score !="":
            dico1[wd][1].append(mot.lower())
    # images
    for wd,imgN in zip(WordList[:15],res[i][90:105]):
        if imgN!='' :
            dico1[wd][2].append(int(imgN[3:]))

for i in range(1,len(res)):
    for wd,score in zip(WordList[15:30],res[i][30:60:2]):
        if score.isdigit():
            dico2[wd][0].append(int(score))
    for wd,mot in zip(WordList[15:30],res[i][31:60:2]):
        dico2[wd][1].append(mot.lower())
    for wd,imgN in zip(WordList[15:30],res[i][105:120]):
        if imgN!='' :
            dico2[wd][2].append(int(imgN[3:]))

for i in range(1,len(res)):
    for wd,score in zip(WordList[30:],res[i][60:90:2]):
        if score.isdigit():
            dico3[wd][0].append(int(score))
    for wd,mot in zip(WordList[30:],res[i][61:90:2]):
        dico3[wd][1].append(mot.lower())
    for wd,imgN in zip(WordList[30:],res[i][120:len(res[i])]):
        if imgN!='' :
            dico3[wd][2].append(int(imgN[3:]))
#
## pour les images, on calcule la fréquence d'association de chaque image
#imgFreq=[0 for i in range(12)]
#for key, value in dico1.iteritems():
#    imges=value[2]
#    for i in imges:
#        if i!='':
#            imgFreq[int(i)-1]+=1
#for key, value in dico2.iteritems():
#    imges=value[2]
#    for i in imges:
#        if i!='':
#            imgFreq[int(i)-1]+=1
#for key, value in dico3.iteritems():
#    imges=value[2]
#    for i in imges:
#        if i!='':
#            imgFreq[int(i)-1]+=1
##print [x/float(sum(imgFreq)) for x in imgFreq]
#
# histogrammes
for key, value in dico1.iteritems():
    #moyennage des scores
    value[0]=np.mean(value[0])
    # histogrammes des images
    value[1]=[x for x in value[1] if x!='']
    value[2]=[x for x in value[2] if x!='']
    # nb occurrences de chaque string
    value[1]=list(Counter(value[1]).most_common(1)[0])
    # nb occurrences de chaque image : si max > 2, pb ?
    #value[2]=max(np.histogram(value[2],bins=range(13))[0]) 
    value[2]=list(Counter(value[2]).most_common(1)[0])
    value[2][0]='img'+str(value[2][0])
for key, value in dico2.iteritems():
    value[0]=np.mean(value[0])
    value[1]=[x for x in value[1] if x!='']
    value[2]=[x for x in value[2] if x!='']
    value[1]=list(Counter(value[1]).most_common(1)[0])
    value[2]=list(Counter(value[2]).most_common(1)[0])
    value[2][0]='img'+str(value[2][0])
for key, value in dico3.iteritems():
    value[0]=np.mean(value[0])
    value[1]=[x for x in value[1] if x!='']
    value[2]=[x for x in value[2] if x!='']
    value[1]=list(Counter(value[1]).most_common(1)[0])
    value[2]=list(Counter(value[2]).most_common(1)[0])
    value[2][0]='img'+str(value[2][0])



dico1 = { k : v for k,v in dico1.iteritems() if v[1][1]<3 and int(v[2][1])<4}
dico2 = { k : v for k,v in dico2.iteritems() if v[1][1]<3 and int(v[2][1])<4}
dico3 = { k : v for k,v in dico3.iteritems() if v[1][1]<3 and int(v[2][1])<4}
sorted_dico1=sorted(dico1.items(), key=operator.itemgetter(1),reverse=True)
sorted_dico2=sorted(dico2.items(), key=operator.itemgetter(1),reverse=True)
sorted_dico3=sorted(dico3.items(), key=operator.itemgetter(1),reverse=True)
for i in sorted_dico1:
    print i
print "\n"
for i in sorted_dico2:
    print i
print "\n"
for i in sorted_dico3:
    print i


