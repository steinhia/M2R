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
    for ann in annotations: # peut y avoir plusieurs mots dans 1 IPU
        txt=ann.text
        if 'pseudo' in txt.lower(): # oubli d'annotation
            print("transcription manquante ",filename)
        # si on arrête de mettre des _ dans la transcription, faut les détecter qd mm
        elif '_' in txt:
            txtSplit=txt.split() # spliter par espace, si plusieurs mots ex m_a m_a
            words+=txtSplit
            # on trouve les transcriptions avec un pb de _ (mal transcrit)
            for i in split_(txtSplit):
                for letter in i:
                    if len(letter)>1 and letter !='aI' and letter!='ts':
                        print("transcription fausse ",filename,i)
    return split_(words)



######## calcul des scores ########


# mise à jour des scores du rappel libre avec un mot
def findWord(PM_max, PM_add,nb_add,wd,l): # l = liste des 3 mots attendus, wd= 1mot
    # trouve le mot le plus proche
    # map(f,l) prend une fonction en argument -> f peut pas prendre d'argument
    # partial(edit_distance,wd) est la fonction e_d avec l'argument wd
    # calcule pour tout i in l, dist(i,wd) 
    lmap=[edit_distance(wd,i) for i in l] # liste des distances |wd-i| in  l2
    mini=min(lmap) # distance la plus petite 
    ind=lmap.index(mini) # index définit la case où on va changer le score 
    score=1-mini/8
    # s'il est assez proche, on l'ajoute aux scores cumulés
    # 0<d<8 -> 1-d/8 donne un score entre 0 et 1, 1 = bonne réponse, 8=nbMax phonèmes
    if score>0.7: # TODO changer valeur ??
        PM_add[ind]+=score # score cumulé
        nb_add[ind]+=1 # nombre de fois que le pseudo-mot est prononcé
    # score max, on l'ajoute s'il est meilleur que le meilleur
    if max(0,score)>PM_max[ind]:
        PM_max[ind]=score
    return [PM_max, PM_add,nb_add]

# calcul des scores à court terme pour tous les mots
def calcScoreShort(filename):
    # une case par pseudo-mot
    PM_max=[0,0,0];PM_add=[0,0,0];nb_add=[0,0,0]
    # mots attendus : sous liste des 12 mots
    a=(int(story))*3
    l2=l[a:a+3]
    # mots rappelés
    words=getWords(filename)
    # on calcule les scores pour chaque mot
    # gère pas le cas si confond personnage et voiture
    for wd in words:
        [PM_max, PM_add,nb_add]=findWord(PM_max, PM_add,nb_add,wd,l2) # score max, cumulé, nb
    PM_moy=[PM_add[i]/nb_add[i] if nb_add[i]>0 else 0 for i in range(3)] #score moyen
    return [PM_max,PM_add,PM_moy,nb_add]

# les scores s'étalent sur plusieurs fichiers -> dico cumulatif
def calcScoreLong(filename,dico_max,dico_add,dico_moy, dico_nb):
    # pour les recall longs, on reconnait le mot parmi tous
    # pour la clé, on garde le nom jusqu'à n01, pas les bis,tris,001 etc
    words=getWords(filename)
    name=ntpath.basename(filename) # nom sans le path
    recallname=name[:23] # clé pour le dico
    # initialisation des dicos max, cumulé, moyen si existe pas dans dico
    if recallname not in dico_max.keys():
        dico_max[recallname]=[0]*12 # score de mémoire max [0,0,0 ... *12]
        dico_add[recallname]=[0]*12 # score cumulé
        dico_moy[recallname]=[0]*12 # score moyen
        dico_nb[recallname]=[0]*12 # nombre de répétitions
    # calcule les scores
    for wd in words:
        [dico_max[recallname], dico_add[recallname],dico_nb[recallname]]=findWord(dico_max[recallname], dico_add[recallname],dico_nb[recallname], wd,l)
    dico_moy[recallname]=[dico_add[recallname][i]/dico_nb[recallname][i] if dico_nb[recallname][i]>0 else 0 for i in range(12)] #score moyen
    return [dico_max,dico_add,dico_moy, dico_nb]

######### main ###########"

# en français tu pourras enlever les '_'
# du coup pas besoin de transformer en tableau : string[i]
#  l [['m','i','l','b','e','t','@'], ....
print(PhoneticList)
l=split_(PhoneticList) # liste dans PythonUtils
csvTabCT=[]
csvTabLT=[]
[dico_max,dico_add,dico_moy, dico_nb]=[{},{},{},{}] # scores max, cumulés, moyens
for idNum in range(1,23):
    path='Resultats/id'+str(idNum).zfill(2)+'/' # zfill-> 01
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        [cond,story]=num2CS(filename)
        if cond!=-1: # court terme
            # calcule les scores de mémorisation
            [PM_max,PM_add,PM_moy,nb_add]=calcScoreShort(filename) # max, cumulé, moy, nb
            # une ligne par pseudo-mot -> 3 lignes pour 1 histoire/condition
            createLigne(filename,csvTabCT,[PM_max[0],PM_add[0],PM_moy[0], nb_add[0]]) #per
            createLigne(filename,csvTabCT,[PM_max[1],PM_add[1],PM_moy[1], nb_add[1]]) #mai
            createLigne(filename,csvTabCT,[PM_max[2],PM_add[2],PM_moy[2], nb_add[2]]) #véh
        else: # long terme
            # pour les recall longs, on reconnait le mot parmi la liste de 12 mots
            # stocké dans un dictionnaire car réparti sur plusieurs fichiers
            # si premier fichier (001) on crée une clé, sinon on met à jour
            [dico_max,dico_add,dico_moy,dico_nb]=calcScoreLong(filename,dico_max,dico_add,dico_moy,dico_nb)
    # on crée une ligne par histoire pour chaque fichier du dico (LT)
    # on trouve les pseudo-mots par histoire, on en déduit la condition

# on va créer 12 lignes -> 1 par pseudo-mot
lignei=[[] for i in range(12)] # on crée 12 lignes vides
for key,value in dico_max.items():
    for pm in range(12): # pm=pseudo-mot
        # on crée la ligne : max, cumulé, nb
        lignei[pm]=createLigne(key,csvTabLT,[value[pm],dico_add[key][pm],dico_moy[key][pm],dico_nb[key][pm]])
        # on assigne la condition correspondante le jour du court terme
        completeLigne(lignei[pm],key,int(pm/4))

# on écrit le csv en spécifiant les colonnes spécifiques à ce calcul (sans id etc)
firstLine=["scoreMax","scoreCumule","scoreMoyen","nbRepet"]
WriteCSV(csvTabCT,firstLine,'csvFiles/brutTranscriptionCT.csv')
WriteCSV(csvTabLT,firstLine,'csvFiles/brutTranscriptionLT.csv')

