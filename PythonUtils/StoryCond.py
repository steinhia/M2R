# -*- coding: utf-8 -*-
import numpy as np
import pickle
import csv
import ntpath
import os,glob



############## gère les images en lien avec les histoires

# portion d'URL des images, leur indice donnera le numéro d'image
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
# parcourt chaque ligne et regarde si détecte une URL du tableau
# dans ce cas, on la remplace par l'index de l'image dans le tableau
# ça donne des numéros d'image -> + pratique à lire
def replaceName(ligne):
    for i,case in enumerate(ligne): # récupère l'indice et le string dans la ligne
        for j,name in enumerate(ListOfURL): # index et nom de l'image
            if name in case: # si portion nom incluse dans nom de l'image
                ligne[i]='img'+str(j) # on remplace par imgx
    return ligne


#attention seulement python2, en python 3 division entière pas comme ça
def num2s(imgNum):
    return imgNum/3 # numéro de l'histoire à partir du numéro de l'image

############### gère les listes de mots


# f('Tereinat')=3 : nom de PM -> numero du PM
def name2num(word):
    return NamesList.index(word)

# f(3)='Tereinat' : numero du PM -> nom du PM
def num2name(i):
    return NamesList[i]

# les histoires vont de 0 à 3, les mots de 0 à 11, les conditions de 0 à 3
# Bonnes réponses du test 
# noms de 0 à 11 correspondant aux images
NamesList=['Mielbete','Keimase','Sonistik','Tereinat','Ligete','Mattendich','Soltete','Madikten','Wecktellin','Lasgelich','Zulergen','Melare'] 
PhoneticList=['m_i_l_b_e_t_@','k_aI_m_a_s_@','z_o_n_i_s_t_i_k','t_e_r_aI_n_a_t','l_i_g_e_t_@','m_a_t_@_n_d_i_C','z_o_l_t_e_t_@','m_a_d_i_k_t_@','v_@_k_t_e_l_i_n','l_a_s_g_e_l_i_C','ts_u_l_@_r_g_@','m_e_l_a_r_@']


# liste des mots demandés pour l'identification (questions = mots, réponses = img)
IdentificationListNum=[2,1,4,0,10,5,7,3,11,6,8,9] 
IdentificationListNumUnit=[1,2,0,3,4,5,6,8,7,10,9,11] # tests unitaires dans ordre !=
IdentificationList=map(num2name,IdentificationListNum) # pour avoir liste de noms
IdentificationListUnit=map(num2name,IdentificationListNumUnit)

# liste des mots espérés pour la pour la dénomination (réponses, questions = img)
DenominationList=map(num2name,[0,1,2,6,7,8,3,4,5,9,10,11]) 
DenominationListUnit=map(num2name,[2,0,1,3,4,5,8,7,6,9,10,11])




# f('img3')='Tereinat' : nom de l'image -> nom du PM
def imgName2name(imgName):
    if imgName!='': # pour prendre 3:, doit vérifier que c'est possible
        num=int(imgName[3:]) # extrait le numéro de l'image
        name=NamesList[num] # en déduit le nom du pseudo-mot
        return name
    return -1 # si '' -> aucun nom de pseudo-mot

# f('Tereinat')=1 : nom du PM -> numero d'histoire
def name2s(word):
    return num2s(name2num(word))

#f(3)='personnage' : numéro du PM (de 0 à 11) -> type du pseudo-mot
def num2type(i):
    if i%3==0: # modulo = %
        return 'personnage'
    elif i%3==1:
        return 'maison'
    else:
        return 'vehicule'

# f('Mielbete')='personnage'
def name2type(wd):
    i=NamesList.index(wd)
    return num2type(i)


################## story cond à partir de l'ordre des permutations

# utilise la liste des permutations
# condition correspondant à l'histoire pour l'id correspondant
def s2c(idPart,sNum,permut):
    line=permut[idPart]
    res=-1
    for i in line:
        if i[0]==sNum:
            res=i[1]
    return res



############### story cond à partir du nom de fichier
# replace l'ordre entre 0 et 3
def Order(order):
    if '4' in order: # ordre = 4123 -> changement que si format 1-4
        s=''
        for i in order:
            s+=str(int(i)-1) # renvoie ordre = 3012
        return s
    return order

# ex story2condition("id01-c4123-s2413-...",3)=0 -> numéros entre 0 et 3
def story2condition(filename,s):
    name=ntpath.basename(filename) # nom sans path
    cOrder=Order(name[6:10]) # ordre des conditions et 0 et 3
    sOrder=Order(name[12:16]) # idem
    c=cOrder[sOrder.index(str(s))] # si story=histoire1 temporel -> condition 1 tmp
    return int(c)

# ex s 1234, c 3412 2 = 2e -> prend le 2e dans c, cad 4
def condition2story(filename,c):
    name=ntpath.basename(filename)
    cOrder=Order(name[6:10])
    sOrder=Order(name[12:16])
    s=sOrder[cOrder.index(str(c))]
    return int(s)


# conditions de 0 à 3 pour les recall, j de 1 à 3
# les baseline sont en condition, story = -1 -> sait pas juste avec le nom du fichier
# return [condition,order]
def name2CS(filename):
    name=ntpath.basename(filename) # nom sans le path
    cOrder=Order(name[6:10]) # ordre des conditions entre 0 et 3
    sOrder=Order(name[12:16])
    num=int(name[21:23]) # nxx
    j=int(name[18]) #jx
    # tab[0] -> j1, tab[1] -> j2
    tab=[[6,8,10,12],[3,5,7,9]] # nom des fichiers recall j1 et j2
    if j<3 and num in tab[j-1]: # j3 : condition,story = -1, j1/2 n quelconque aussi
        index=int(tab[j-1].index(num)) # ex num=6,j=1-> tab[0].index(6)=0 -> ordre tmp 
        return [int(cOrder[index]),int(sOrder[index])] # cOrder[0],sOrder[0]
    return [-1,-1]

# jour inclus dans le nom
def jourF(filename):
    name=ntpath.basename(filename)
    j=int(name[18])
    return j

# création d'une clé (utilisée dans plusieurs dictionnaires) pour avoir un nom court
def filename2key(filename):
    name=ntpath.basename(filename) # nom sans path
    num=name[2:4] # numéro id
    jr=int(name[18]) # jour
    [c,_]=name2CS(filename) # condition
    cle=str(num).zfill(2)+str(jr)+str(c) # cle = id+jour+condition
    return cle

# retrouve le nom de fichier à partir de la clé
# parcourt les fichiers, génère la clé, regarde si c'est la clé attendue
# TODO changer path pour Helene
def key2filename(key):
    idNum=key[:2] # retrouve le numéro du participant avec la clé -> bon dossier
    path='/home/steinhia/Documents/Alex/Transcription/AudioList/id'+str(idNum).zfill(2)+'/'
    for filename in glob.glob(os.path.join(path, '*.wav')): # parcourt les fichiers wav
        if str(filename2key(filename))==str(key): # si la clé du nom est celle cherchée
                return filename # on retourne ce nom
    return -1
