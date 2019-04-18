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
from itertools import islice
import panda as pd
import csv
import matplotlib.pyplot as plt

data=[]
with open('brut.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for i in reader:
        data.append(i)

def identifErrorC(data,j):
    ECJ=[0,0,0,0]
    for ligne in data[1:]:
        if int(ligne[1])==j and ligne[9]=='False':
            ECJ[int(ligne[6])]+=1
    return ECJ

def identifErrorS(data,j):
    ECJ=[0,0,0,0]
    for ligne in data[1:]:
        if int(ligne[1])==j and ligne[9]=='False':
            ECJ[int(ligne[4])]+=1
    return ECJ


# test d'identification

# erreurs par condition j1 pour l'identification
print "erreur par condition J1, identification"
print identifErrorC(data,1)
print "erreur par story J1, identification"
print identifErrorS(data,1),"\n"
    
# erreurs par condition j2 pour l'identification
print "erreur par condition J2, identification"
print identifErrorC(data,2)
print "erreur par story J2, identification"
print identifErrorS(data,2),"\n"

# erreurs par condition j3 pour l'identification
print "erreur par condition J3, identification"
print identifErrorC(data,3)
print "erreur par story J3, identification"
print identifErrorS(data,3),"\n"


# test de dénomination

def denomErrorC(data,j):
    ECJ=[0,0,0,0]
    for ligne in data[1:]:
        if int(ligne[1])==j :
            ECJ[int(ligne[6])]+=float(ligne[13])
    return ECJ
def denomErrorS(data,j):
    ECJ=[0,0,0,0]
    for ligne in data[1:]:
        if int(ligne[1])==j :
            ECJ[int(ligne[4])]+=float(ligne[13])
    return ECJ


# erreurs par condition j1 pour l'identification
print "erreur par condition J1, dénomination"
print denomErrorC(data,1)
print "erreur par story J1,dénomination "
print denomErrorS(data,1),"\n"
    
# erreurs par condition j2 pour l'identification
print "erreur par condition J2,dénomination "
print denomErrorC(data,2)
print "erreur par story J2,dénomination "
print denomErrorS(data,2),"\n"

# erreurs par condition j3 pour l'identification
print "erreur par condition J3,dénomination "
print denomErrorC(data,3)
print "erreur par story J3,dénomination "
print denomErrorS(data,3),"\n"




NamesList=['Mielbete','Keimase','Sonistik','Tereinat','Ligete','Mattendich','Soltete','Madikten','Wecktellin','Lasgelich','Zulergen','Melare']
PhoneticList=['m_i_l_b_e_t_@','k_aI_m_a_s_@','z_o_n_i_s_t_i_k','t_e_r_aI_n_a_t','l_i_g_e_t_@','m_a_t_@_n_d_i_C','z_o_l_t_e_t_@','m_a_d_i_k_t_@','v_@_k_t_e_l_i_n','l_a_s_g_e_l_i_C','ts_u_l_@_r_g_@','m_e_l_a_r_@']


# analyse des confusions en identification
def confusionImages(data,j):
    dico={}
    for i in range(-1,12):
        for k in range(12):
            if i!=k:
                dico[str(i).zfill(2)+str(k).zfill(2)]=0
    for ligne in data[1:]:
        if ligne[9]=='False' : #and (ligne[1]==str(j) or True):
            r1=NamesList.index(ligne[8]) # attendu
            r2=-1
            if ligne[7]!='-1':
                r2=NamesList.index(ligne[7]) # donne
            dico[str(r2).zfill(2)+str(r1).zfill(2)]+=1
    return dico

dico=confusionImages(data,2)
sorted_d = sorted(dico.items(), key=operator.itemgetter(1))
print sorted_d

res=[]
# on plot la confusion
for v in dico.values():
    res.append(v)
x=[i for i in range(len(res))]
print x,res
fig = plt.figure()
plt.bar(x, res, width=0.8, color='b' )


