# -*- coding: utf-8 -*
import tgt
import os, glob
import codecs
import ntpath
import csv
from functools import partial
import stackprinter
stackprinter.set_excepthook(style='color')
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())




# i = histoire, on en déduit la condition
def completeLigne(ligne,filename,i):
        ligne[5]=i # histoire
        c=story2condition(filename,i)
        ligne[4]=c # condition

############# récupération des mots

#print les mots de idNum, jour, dans une condition précise, à court terme ou pas
def printWords(idNum,jour,cond,CT=True):
    for idRange in range(1,13):
        path='Resultats/id'+str(idRange).zfill(2)+'/'
        for filename in glob.glob(os.path.join(path, '*.TextGrid')):
            liste=['id'+str(idNum).zfill(2),'j'+str(jour)]
            # si c'est à la fois le bon participant et le bon jour
            if all(i in filename for i in liste):
                [c,_]=num2CS(filename)
                # si c'est la bonne condition et qu'on veut printer à court terme
                if c==cond and CT:
                    print(filename,'\n',getWords(filename),'\n')
                # si on veut long terme
                elif not CT and c==-1:
                    print(filename,'\n',getWords(filename),'\n')

# m_i_l -> [m,i,l] 
def split_(liste):
    for i,l in enumerate(liste):
        liste[i]=l.split('_')
    return liste

# récupère la liste de mots transcrits dans tout le fichier
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
            # on trouve les transcriptions avec un pb de _ (mal transcrit)
            for i in txtSplit:
                for letter in i:
                    if len(letter)>1 and letter !='aI' and letter!='ts':
                        print("transcription fausse ",filename,i)
    return split_(words)



######## calcul des scores ########


# mise à jour des scores du rappel libre avec un mot
def findWord(PM, PM_add,nb_add,wd,l):
    # trouve le mot le plus proche
    lmap=list(map(partial(edit_distance,wd),l))
    mini=min(lmap)
    ind=lmap.index(mini)
    # s'il est assez proche, on l'ajoute aux scores cumulés
    if 1-mini/8>0.7:
        PM_add[ind]+=1-mini/8
        nb_add[ind]+=1 # nombre de fois que le psedo-mot est prononcé
    # score max, on l'ajoute s'il est meilleur que le meilleur
    if max(0,1-mini/8)>PM[ind]:
        PM[ind]=1-mini/8
    return [PM, PM_add,nb_add]

# calcul des scores à court terme pour tous les mots
def calcScoreShort(filename):
    PM=[0,0,0];PM_add=[0,0,0];nb_add=[0,0,0]
    # mots attendus : sous liste des 12 mots
    a=(int(story))*3
    l2=l[a:a+3]
    # mots rappelés
    words=getWords(filename)
    # on calcule les scores pour chaque mot
    for wd in words:
        [PM, PM_add,nb_add]=findWord(PM, PM_add,nb_add,wd,l2) # score max, cumulé, nb
    PM_moy=[PM_add[i]/nb_add[i] if nb_add[i]>0 else 0 for i in range(3)] #score moyen
    return [PM,PM_add,PM_moy,nb_add]

# les scores s'étalent sur plusieurs fichiers -> dico cumulatif
def calcScoreLong(filename,dico,dico_add,dico_moy, dico_nb):
    # pour les recall longs, on reconnait le mot parmi tous
    # on garde le nom jusqu'à n01, pas les bis,tris,001 etc
    words=getWords(filename)
    name=ntpath.basename(filename) # nom sans le path
    recallname=path+name[:23]+name[-9:]
    # initialisation des dicos max, cumulé, moyen si existe pas dans dico
    if recallname not in dico.keys():
        dico[recallname]=[0]*12
        dico_add[recallname]=[0]*12
        dico_moy[recallname]=[0]*12
        dico_nb[recallname]=[0]*12
    # calcule les scores
    for wd in words:
        [dico[recallname], dico_add[recallname],dico_nb[recallname]]=findWord(dico[recallname], dico_add[recallname],dico_nb[recallname], wd,l)
    dico_moy[recallname]=[dico_add[recallname][i]/dico_nb[recallname][i] if dico_nb[recallname][i]>0 else 0 for i in range(12)] #score moyen
    return [dico,dico_add,dico_moy, dico_nb]

######### main ###########"

l=split_(PhoneticList) # liste dans PythonUtils
csvTabCT=[]
csvTabLT=[]
[dico,dico_add,dico_moy, dico_nb]=[{},{},{},{}] # scores max, cumulés, moyens
for idNum in range(1,22):
    path='Resultats/id'+str(idNum).zfill(2)+'/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        [cond,story]=num2CS(filename)
        if cond!=-1: # court terme
            # calcule les scores de mémorisation
            [PM,PM_add,PM_moy,nb_add]=calcScoreShort(filename) # max, cumulé, moy, nb
            # une ligne par histoire/condition
            createLigne(filename,csvTabCT,[PM[0],PM_add[0],PM_moy[0], nb_add[0]]) # 
            createLigne(filename,csvTabCT,[PM[1],PM_add[1],PM_moy[1], nb_add[1]]) 
            createLigne(filename,csvTabCT,[PM[2],PM_add[2],PM_moy[2], nb_add[2]]) 
        else:
            # pour les recall longs, on reconnait le mot parmi la liste de 12 mots
            # stocké dans un dictionnaire car réparti sur plusieurs fichiers
            [dico,dico_add,dico_moy,dico_nb]=calcScoreLong(filename,dico,dico_add,dico_moy,dico_nb)
    # on crée une ligne par histoire pour chaque fichier du dico (LT)
    # on trouve les pseudo-mots par histoire, on en déduit la condition

lignei=[[] for i in range(12)]
for key,value in dico.items():
    for hist in range(12):
        # on crée la ligne : max, cumulé, nb
        lignei[hist]=createLigne(key,csvTabLT,[value[hist],dico_add[key][hist],dico_moy[key][hist],dico_nb[key][hist]])
        # on assigne la condition correspondante le jour du court terme
        completeLigne(lignei[hist],key,int(hist/4))

# on écrit le csv en spécifiant les colonnes spécifiques à ce calcul (sans id etc)
firstLine=["scoreMax","scoreCumule","scoreMoyen","nbRepet"]
WriteCSV(csvTabCT,firstLine,'csvFiles/brutTranscriptionCT.csv')
WriteCSV(csvTabLT,firstLine,'csvFiles/brutTranscriptionLT.csv')

