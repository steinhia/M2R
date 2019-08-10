# -*- coding: utf-8 -*-
import csv
import operator
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

data=[]
# on ouvre le csv
with open('brut.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for i in reader:
        data.append(i)

# calcul des erreurs cumulées
# erreurs au score d'identification : case = condition ou histoire
def identifError(data,j,case):
    Err=[0,0,0,0]
    for ligne in data[1:]: # ligne 1 = titre des colonnes
        if int(ligne[1])==j and ligne[10]=='0': # j=jour
            Err[int(ligne[case])]+=1
    return Err

# calcul des errreurs par condition
def identifErrorC(data,j):
    return identifError(data,j,4) # dans brut.csv case n°4 = condition

# calcul des erreurs par histoire
def identifErrorS(data,j):
    return identifError(data,j,5) # dans brut.csv case n°5 = histoire


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
def denomError(data,j,case1,case2):
    Err=[0,0,0,0]
    for ligne in data[1:]:
        if int(ligne[1])==j :
            Err[int(ligne[case1])]+=float(ligne[case2])
    return Err


def denomErrorC(data,j):
    return denomError(data,j,4,13) # 13 = numéro de la case score en dénomination

def denomErrorS(data,j):
    return denomError(data,j,5,13)

# test de dénomination : distance avec le mot le plus proche (confusion)
def denomErrorConfC(data,j):
    return denomError(data,j,4,17) # 17 = case du score en confusion 

def denomErrorConfS(data,j):
    return denomError(data,j,5,17)


# erreurs par condition j1 pour l'identification
print "erreur par condition J1, dénomination"
print denomErrorC(data,1)
print "erreur par story J1,dénomination "
print denomErrorS(data,1),"\n"

print "erreur par condition J1, dénomination CONFUSION"
print denomErrorConfC(data,1)
print "erreur par story J1,dénomination CONFUSION"
print denomErrorConfS(data,1),"\n\n"

    
# erreurs par condition j2 pour l'identification
print "erreur par condition J2,dénomination "
print denomErrorC(data,2)
print "erreur par story J2,dénomination "
print denomErrorS(data,2),"\n"

print "erreur par condition J2,dénomination CONFUSION"
print denomErrorConfC(data,2)
print "erreur par story J2,dénomination CONFUSION"
print denomErrorConfS(data,2),"\n\n"

# erreurs par condition j3 pour l'identification
print "erreur par condition J3,dénomination "
print denomErrorC(data,3)
print "erreur par story J3,dénomination "
print denomErrorS(data,3),"\n"
# erreurs par condition j3 pour l'identification
print "erreur par condition J3,dénomination CONFUSION"
print denomErrorConfC(data,3)
print "erreur par story J3,dénomination CONFUSION"
print denomErrorConfS(data,3),"\n"



NamesList=['Mielbete','Keimase','Sonistik','Tereinat','Ligete','Mattendich','Soltete','Madikten','Wecktellin','Lasgelich','Zulergen','Melare']
PhoneticList=['m_i_l_b_e_t_@','k_aI_m_a_s_@','z_o_n_i_s_t_i_k','t_e_r_aI_n_a_t','l_i_g_e_t_@','m_a_t_@_n_d_i_C','z_o_l_t_e_t_@','m_a_d_i_k_t_@','v_@_k_t_e_l_i_n','l_a_s_g_e_l_i_C','ts_u_l_@_r_g_@','m_e_l_a_r_@']


# analyse des confusions en identification
def confusionImages(data,j):
    dico={}
    for i in range(-1,12):
        for k in range(12):
            if i!=k: # si i==k, pas de confusion, même image
                dico[str(i).zfill(2)+str(k).zfill(2)]=0 # clé = imgRepondu-Attendu
    for ligne in data[1:]:
        if ligne[10]=='0' : # si erreur 
            r1=NamesList.index(ligne[7]) # attendu
            r2=-1
            if ligne[9]!='-1': # si le participant a répondu (coché une case)
                r2=NamesList.index(ligne[9]) # repondu
            dico[str(r2).zfill(2)+str(r1).zfill(2)]+=1 # on incrémente le nb d'erreurs
    return dico

dico=confusionImages(data,2)
# on trie le dictionnaire
sorted_d = sorted(dico.items(), key=operator.itemgetter(1))
print sorted_d

