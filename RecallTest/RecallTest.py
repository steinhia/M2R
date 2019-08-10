# -*- coding: utf-8 -*-
import csv
import os
import pickle
import csv
from itertools import islice
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

# ligne fait partie d'un csv recallTest ou recalltest_s1 etc
# on prend un test d'un participant et on crée les lignes csv correspondantes
# ligne entrée = [idPart, jour, nom1, nom2, nom3, img1, img2, img3] ou nom*12, img*12
# on va créer 3 ou 12 lignes dans le csv : une pour chaque pseudo-mot
def createLigneBrut(ligne,permut,n=0):

    # extraction des données relatives au sujet
    sujet=int(ligne[0])
    jour=int(ligne[1])
    # les tableaux commencent à 0 : id1 = permut[0]
    ordre=permut[int(sujet)-1] # permut commence à 0 
    # ordre=[[s,c],[s,c],[s,c],[s,c]]
    # join transforme une liste en string avec un séparateur ""
    ordreS="".join([str(a[0]) for a in ordre]) # a[0] = premier élmt de chaque couple
    ordreC="".join([str(a[1]) for a in ordre])


    # sépare en résultats d'identification et dénomination : crée 2 listes
    # ident : [Soltete, Lasgelich, Melare] -> vrais noms correspondant aux images
    # denom : [ laskelisch, , maltese] -> réponses orthographiques
    identNames=[];denomNames=[]
    # si test groupé
    if len(ligne)>20:
        # le framaform retourne le nom des images
        identNames=[imgName2name(name) for name in ligne[14:]]
        denomNames=[name for name in ligne[2:14]]
    # si test séparé par histoire
    else:
        identNames=[imgName2name(name) for name in ligne[5:]]
        denomNames=[name for name in ligne[2:5]]


    # on s'interesse à l'identification : liste des noms rentres
    res=[]
    for i,name in enumerate(identNames): #noms répondus
        answer='' # réponse attendue orthographique
        if len(ligne)>20:
            answer=IdentificationList[i] # liste de 12 des tests groupés
        else:
            # identNames de longueur 3 -> faut se placer à la bonne histoire
            answer=IdentificationListUnit[i+n*3] # liste de 12 des tests séparés
        Panswer=PhoneticList[NamesList.index(answer)] # réponsePhonétique attendue 
        # boolean réussite/échec -> réponse donnée (identNames) == attendue (answer) ?
        b=int((name==answer))
        # on récupère l'histoire à partir de la réponse attendue
        # peut pas juste prendre i car il correspond à la i-ème histoire Temporelle
        story=name2s(answer)
        # condition correspondante
        condition=ordreC[ordreS.index(str(story))]
        # type : maison etc
        nameType=name2type(answer)
        # liste = une ligne du fichier brut : 1 pseudo-mot
        res.append([sujet,jour,'c '+str(ordreC),'s '+str(ordreS),condition,story,nameType,answer,Panswer,name,b])

    # dénomination ensuite : on complete la liste
    for i,name in enumerate(denomNames):
        if name!='':
            answer='' # bonne réponse
            # pour le test groupé
            if len(ligne)>20:
                answer=DenominationList[i]
            # pour le test séparé
            else:
                answer=DenominationListUnit[i+n*3] # pour se place à la bonne hist 
            # on cherche la bonne ligne : résultat identif et denom sur la même ligne
            for j,l in enumerate(res):
                if l[7]==answer: # si même réponse attendue
                    l.append(name)
    return res # res = 3 listes : une pour chaque pseudo-mot
# ex [21, 1, c 1023, s 2013, 3, 3, maison, 'Lasgelich', 'Lasgelich', 1, 'melare' ]
#     id  j                  c   s  type    ident cible    repondu   ok?  denom


# on télécharge tout avec une virgule en séparateur : fonction dans PythonUtils
l=CsvReader('recall_test.csv')
l1=CsvReader('recall_s1_24.csv')
l2=CsvReader('recall_s2_24.csv')
l3=CsvReader('recall_s3_24.csv')
l4=CsvReader('recall_s4_24.csv')

# ordre des histoires, conditions et assignations
OpenPkl('../Permutations/Permut.pkl')

# on remet tout de 0 à 3
for idi in permut:
    for i in idi:
        for j,case in enumerate(i):
            i[j]=case-1

# on crée csvTab sans s'occuper des transcriptions phonétiques déjà dans brut.csv
# test entier
CSVTab=[]
for i,ligne in enumerate(l[1:]): # on enlève le header
    # remplace l'URL par le numéro d'image : dans StoryCond
    ligne=replaceName(ligne)
    # crée les lignes du csvBrut correspondant à cette ligne du framaform
    CSVTab+=createLigneBrut(ligne,permut)

# test unitaire 
for i,ligne in enumerate(l1[1:]):
    ligne=replaceName(ligne)
    CSVTab+=createLigneBrut(ligne,permut)
for i,ligne in enumerate(l2[1:]):
    ligne=replaceName(ligne)
    CSVTab+=createLigneBrut(ligne,permut,1)
for i,ligne in enumerate(l3[1:]):
    ligne=replaceName(ligne)
    CSVTab+=createLigneBrut(ligne,permut,2)
for i,ligne in enumerate(l4[1:]):
    ligne=replaceName(ligne)
    CSVTab+=createLigneBrut(ligne,permut,3)

dMax=8   
# on ouvre le fichier brut.csv existant pour récupérer les transcriptions existantes
# et donc compléter csvTab
if os.path.isfile('brut.csv'): 
    with open('brut.csv','r') as f:
        r=csv.reader(f)
        # [idNum,jour,c 1023, s3021, 1, 3, type, orthoCible, phonCible, identRep, ok?, rep ortho]
        # après transcription, + [transcPhon, 0<score<1, scoreBinaire]
        #                      + [mot+procheOrtho, mot+prchePhono, score]
        for l in islice(r,1,None):
            # réponse correcte phonétique -> phonCible
            PRep=l[8]
            # si on trouve une transcription phonétique
            if len(l)>=13 and l[12]!='':
                transcription=l[12]
                # on parcourt tout le tableauBrut pour trouver la bonne ligne
                for csvLigne in CSVTab:
                    strLigne=map(str,csvLigne)
                    if l[:8]==strLigne[:8]: # on complète la ligne de csvTab
                        csvLigne.append(transcription)
                        # calcul de la distance avec la bonne réponse
                        # transcription et mot cible en tableau phonétique
                        transTab=transcription.split('_') # transcription
                        PRepTab=PRep.split('_') # réponse attendue phonétique
                        # distance entre les 2 mots/tableaux : 8-dist(a,b) : dMax=8
                        d=max(0,dMax-edit_distance(transTab,PRepTab))
                        # on stocke le score entre 0 et 1 et le score binaire
                        csvLigne+=[d/dMax,int(d==dMax)] #bool : rep correcte ?
                        # calcul de la distance minimale
                        dConf=0;Pconf='';
                        # liste des réponses phonétiques pour détecter confusions
                        for Pname in PhoneticList:
                            PTab=Pname.split('_')
                            tmp=dMax-edit_distance(transTab,PTab) # score à maximiser
                            if tmp>dConf:
                                Pconf=Pname;dConf=tmp; # Pconf = forme phonétique
                        conf=NamesList[PhoneticList.index(Pconf)] # orthographe
                        csvLigne+=[conf,Pconf,dConf/dMax] # stocke ortho,phono, score
                    else: # si pas de transcription phonétique, met chaine vide
                        csvLigne+=''
for csvLigne in CSVTab:
    # si pas de réponse orthographique 
    if len(csvLigne)<=11 :
        csvLigne+=['','',0,0,'','',0] # rép ortho, phono, score, confusion O+P+score
    # si réponse ortho, pas phono (pas encore transcrit)
    elif (len(csvLigne)==12 and csvLigne[11]!='') or (len(csvLigne)>=13 and csvLigne[12]=='')   :
        csvLigne+=['',0,0,'','',0] # rép phono, score, confusion O+P+score

# écriture du csv
firstLine=["type","reponse attendue","reponse phonetique","reponse donnée","evaluation","orthographe","transcription","score","scoreBinaire","mot le plus proche","transcription","score"]
WriteCSV(CSVTab,firstLine,'brut.csv')

