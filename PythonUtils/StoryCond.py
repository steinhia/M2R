# -*- coding: utf-8 -*-
import numpy as np
import pickle
import csv
import ntpath


ListOfURL=['fyJR1Nd5bdYf.png',
'RXu0QM7rpAyU.png',
'Qgz50gtfWEKz.png',
'suiy1ohYtpMc.png',
'0b30ZuqmWz8O.png',
'n55EF0EPH3eh.png',
'UR7y2KDxGdkV.png',
'YvwxbuziPnUW.png',
'fYjGeVqjiINB.png',
'tLIgcDR9urkS.png',
'YEMx5pW9l952.png',
'XnQSXSzM0tU7']


# remplace l'URL par le numéro d'image
def replaceName(ligne):
    for i,case in enumerate(ligne):
        for j,name in enumerate(ListOfURL):
            if name in case:
                ligne[i]='img'+str(j)
    return ligne


# f(4)=1 : numero d'image -> numero d'histoire
def story2condition(filename,s):
    name=ntpath.basename(filename)
    cOrder=name[6:10]
    sOrder=name[12:16]
    c=cOrder[sOrder.index(str(s))]
    return c


# condition correspondant à l'histoire pour l'id correspondant
def s2c(idPart,sNum,permut):
    line=permut[idPart]
    res=-1
    for i in line:
        if i[0]==sNum:
            res=i[1]
    return res

def num2s(imgNum):
    return imgNum/3

# f('Tereinat')=3 : nom de PM -> numero du PM
def name2num(word):
    return NamesList.index(word)

# f(3)='Tereinat' : numero du PM -> nom du PM
def num2name(i):
    return NamesList[i]

# f('img3')='Tereinat' : nom de l'image -> nom du PM
def imgName2name(imgName):
    if imgName!='':
        num=int(imgName[3:])
        name=NamesList[num]
        return name
    return -1

# f('Tereinat')=1 : nom du PM -> numero d'histoire
def name2s(word):
    return num2s(name2num(word))

#f(3)='personnage'
def num2type(i):
    if i%3==0:
        return 'personnage'
    elif i%3==1:
        return 'maison'
    else:
        return 'vehicule'
def name2type(wd):
    i=NamesList.index(wd)
    return num2type(i)


# les histoires vont de 0 à 3, les mots de 0 à 11, les conditions de 0 à 3
# Bonnes réponses du test 
# noms de à à 11 correspondant aux images
NamesList=['Mielbete','Keimase','Sonistik','Tereinat','Ligete','Mattendich','Soltete','Madikten','Wecktellin','Lasgelich','Zulergen','Melare']
PhoneticList=['m_i_l_b_e_t_@','k_aI_m_a_s_@','z_o_n_i_s_t_i_k','t_e_r_aI_n_a_t','l_i_g_e_t_@','m_a_t_@_n_d_i_C','z_o_l_t_e_t_@','m_a_d_i_k_t_@','v_@_k_t_e_l_i_n','l_a_s_g_e_l_i_C','ts_u_l_@_r_g_@','m_e_l_a_r_@']




# liste des mots demandés pour l'identification (questions = mots, réponses = img)
IdentificationListNum=[2,1,4,0,10,5,7,3,11,6,8,9]
IdentificationListNumUnit=[1,2,0,3,4,5,6,8,7,10,9,11]
IdentificationList=map(num2name,IdentificationListNum)
IdentificationListUnit=map(num2name,IdentificationListNumUnit)

# liste des mots espérés pour la pour la dénomination (réponses, questions = img)
DenominationList=map(num2name,[0,1,2,6,7,8,3,4,5,9,10,11])
DenominationListUnit=map(num2name,[2,0,1,3,4,5,8,7,6,9,10,11])

# condition correspondant à l'histoire pour l'id correspondant
def s2c(idPart,sNum,permut):
    line=permut[idPart]
    res=-1
    for i in line:
        if i[0]==sNum:
            res=i[1]
    return res

# remplace l'URL par le numéro d'image
def replaceName(ligne):
    for i,case in enumerate(ligne):
        for j,name in enumerate(ListOfURL):
            if name in case:
                ligne[i]='img'+str(j)
    return ligne


# conditions de 0 à 3 pour les recall
# return [condition,order]
def num2CS(filename):
    name=ntpath.basename(filename)
    cOrder=name[6:10]
    sOrder=name[12:16]
    num=int(name[21:23])
    j=int(name[18])
    tab=[[6,8,10,12],[3,5,7,9]]
    if j<3 and num in tab[j-1]:
        index=int(tab[j-1].index(num))
        return [int(cOrder[index])-1,int(sOrder[index])-1]
    return [-1,-1]

def Order(order):
    s=''
    for i in order:
        s+=str(int(i)-1)
    return s
