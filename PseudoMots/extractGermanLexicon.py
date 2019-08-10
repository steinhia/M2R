# -*- coding: utf-8 -*-
import operator
import numpy as np
import codecs
import pickle

# on va extraire le dictionnaire ainsi que les dictionnaires utilisés pour évaluer les contraintes phonotactiques

# on calcule les probas phonotactiques des phonèmes et des biphones
# renvoie dico (phonèmes) et dicoBI (biphones)
# clé = phonème/biphone, valeur = fréquence
# itère sur tous les mots de 3 syll du dictionnaire, pas seulement des schémas gardés
def calculatePositionalSegmentFreq(WordsList):
    dico={};dicoBi={};
    # pas de frequence pour les triphones, mais on veut des sequences legales
    Sum=1 # initialisée à 1 car on prend des log
    # on parcourt la liste de mots, contenant mot, transcription phonétique, fréq ..
    for row in WordsList: # row=[mot,freq]
        # besoin de nombres entiers pour que le log soit représentatif -> *100
        freq=float(row[1])*100
        if freq>0:
            logFreq=np.log10(freq)
            Sum+=logFreq # on calcule pas la fréquence mais son log
            wd=[ l for l in row[0] if l!='.'] # on enlève les . de la transcription
            for i,pho in enumerate(wd): # on parcourt les phonèmes du mot, wd=1 mot
                if not dico.has_key(pho): # clé inexistante
                    # probabilité d'apparaitre en position p, p de 0 à 14
                    # on crée une liste de longueur 15 dico[pho]
                    dico[pho]=[0.0]*15 # on la crée : grand tableau pour mots longs
                dico[pho][i]+=logFreq # dico[phonème][position]+=log de la fréquence
            for i in range(len(wd)-1):
                biphone=tuple(wd[i:i+2]) # tuple = un peu comme liste mais non mutable
                if not dicoBi.has_key(biphone):
                    dicoBi[biphone]=[0.0]*15
                dicoBi[biphone][i]+=logFreq
    # on transforme ça en probabilité en divisant par la somme totale
    for key, value in dico.items():
        for i,letter in enumerate(value): # value= les 15 cases
            if value[i]>0 and Sum>0:
                value[i]/=Sum
    for key, value in dicoBi.iteritems():
        for i,letter in enumerate(value):
            if value[i]>0 and Sum>0:
                value[i]/=Sum
    return [dico,dicoBi]

def findTriphones(AllWordsList): 
    # on crée une liste de triphones possibles pour chaque position
    listPoss=[[],[],[],[],[],[],[],[]]
    # on parcourt tout le dictionnaire allemand
    for l in AllWordsList:
        # on extrait le mot en enlevant les . : triphones peu importe les syllabes
        word=[ x for x in l[0] if x!='.'] 
        for i in range(min(8,len(word)-2)): # on parcourt les triphones du mot
            # on ajoute chaque triphone à la bonne liste : position du triphone
            listPoss[i].append(tuple(word[i:i+3])) 
    # on garde seulement les triphones plausibles, apparaissant + de 10 fois
    listFinal=[[],[],[],[],[],[],[],[]]
    for j in range(8): # 8 positions
        for i in listPoss[j]: # liste des possibilités pos j
            if listPoss[j].count(tuple(i))>10 and tuple(i) not in listFinal[j]:
                listFinal[j].append(tuple(i))
    return listFinal

# extrait le schéma ex CV.CV.CVC à partir du mot contenant les . 
def schema(mot,Voy,Cons):
    schema=''
    for letter in mot: # on itère sur chaque lettre
        if letter in Voy: # si c'est une voyelle
            schema+='V'
        elif letter in Cons:
            schema+='C'
        elif letter==".": # pour mettre le . dans le schéma
            schema+="."
    return schema

# on prend un mot du dictionnaire et on simplifie/regroupe certains phonèmes
# a court/long = a
def simplify(mot):
    if '?' in mot:
        mot.remove('?')
    for i,pho in enumerate(mot):
        # on simplifie les voyelles simples (tense, relax, longues)
        if pho in ['a:','a~',]:
            mot[i]='a' # on remplace pho par 'a'
        if pho in ['E','e:','e','E:']:
            mot[i]='e'
        if pho in ['y:','Y']:
            mot[i]='y'
        if pho in ['i:','I']:
            mot[i]='i'
        if pho in ['o','o:','O']:
            mot[i]='o'
        if pho in ['U','u:']:
            mot[i]='u'
        # on remplace 6 par @r ex mehr
        if pho=='6':
            mot=mot[:i]+['@','r']+mot[i+1:]
    return mot


with open('germanWords.pkl','rb') as lexicon:
    [WordsList,AllWordsList,d,db,list3,dicoSyll]=pickle.load(lexicon)

# on ouvre le fichier contenant le dictionnaire
f=codecs.open("german_lexicon.txt",encoding="utf-8")
# on le lit ligne par ligne, on le transforme en tableau de lignes
l=f.read().encode('utf-8').splitlines()

# liste des voyelles contenues dans le dictionnaire -> nous on va la réduire
Voy=['a:','a','a~','E','e:','e','E:','y:','Y','y','i:','i','I','o','o:','O','U','u:','u','@','9','6','2:','?','OY','aU','aI','2:6','e:6','o:6','y:6','96','E6','u:6','E:6','O:6','i:6','I6','O6','Y6','U6','a:6','a6']

# liste des consonnes contenues dans le dictionnaire -> nous on va la réduire
Cons=['b','k','d','f','g','h','j','l','m','n','p','r','s','t','v','N','z','Z','C','ts','tS','dZ','S','x','?']



### on veut trouver la médiane des longueurs de mots en allemand : 3
#WordLength=[]
#for i in l: # on parcourt la liste des lignes du dictionnaire
#    t=i.split() # on split par espace  : une ligne = 1 mot et ses caractéristiques
#    if float(t[-1])!=0.0: # on regarde la fréquence du mot : on garde que les !=0
#        WordLength.append((1+t[1].count('-'))) # on y rajoute la longueur de ce mot
## print(np.median(WordLength))







## on veut trouver les schémas les plus fréquents pour les mots de 3 syll
## on commence par garder les mots de 3 syllabes

## on trouve les 3 schémas les plus fréquents :
## CV.CV.CVC : zumachen
## CVC.CV.CVC : weggeben
## CV.CVC.CVC : bemerken



AllWordsList=[]
WordsList=[]
dicoSchema={}
for i in l: # lignes du dictionnaire ex 'Insolenz' 'In-so-lenz' I n s .  CatGramm freq
    t=i.split() # une ligne splitée en tableau
    f=float(t[-1]) # fréquence du mot
    cat=t[-2] # catégorie grammaticale du mot
    # mot=après 1 (mot + mot tiret) et avant les 2 dernières infos (cat et freq) 
    mot =[x for i,x in enumerate(t) if i>1 and i<len(t)-2] # mot en liste, pas string 
    # simplifications au niveau du code phonétique
    mot=simplify(mot)
    # on extrait le schéma du mot
    sch=schema(mot,Voy,Cons)
    # on le met dans le dico s'il a 3 syllabes
    if f!=0 and t.count('.')==2:
        # on incrémente le nombre de mots du schéma du mot courant de 1 ou f ?????
        dicoSchema[sch] = dicoSchema.get(sch, 0) + f # 0 valeur par défaut si existe x 
        WordsList.append([mot,f]) # crée liste des mots de 3 syll avec leur fréq
    if f!=0.0:
        AllWordsList.append([mot,f]) # crée liste de tous les mots avec leur fréq


SchemaOk=[] # liste des schémas retenus
# on trie le dictionnaire pour obtenir les 3 schémas les + fréquents
# trier par operator.itemgetter(0): trier par cle, itemgette(1) : trier par valeur
# reverse = True : du plus grand au plus petit
# comme c'est trié, ça devient une liste, on garde les 3 premiers
SchemaOk=sorted(dicoSchema.items(),key=operator.itemgetter(1),reverse=True)[:3]
print(SchemaOk)





###### calculs sur les fréquences des mots, syllabes, phonèmes etc ##########


# on crée les dicos des probas phonotactiques avec la liste des mots de 3 syllabes
# on peut le faire avec la liste de tous les mots
[d,db]=calculatePositionalSegmentFreq(WordsList)
# on crée la liste des triphones plausibles avec tous les mots
list3=findTriphones(WordsList)


# on veut extraire la fréquence des syllabes != phonèmes/biphones
# on prend chaque mot et on incrémente les fréq des 3 syllabes correspondantes
dicoS={}
for i in WordsList: # on parcourt les mots de 3 syllabes
    wd=i[0] # le mot : liste contenant des . 
    # fonction split existe pas pour les listes -> transforme en string, split
    # puis retransforme en liste
    # ['aI','.','b','i'] -> 'aI,.,b,i'->(.) ['aI,',',b,i'] ->(,) [['aI'],['b','i']]
    split1=','.join(wd).split('.') # on le transforme en string pour le spliter avec .
    # liste = 1 mot splité en syllabes-> liste, syll = liste de phonèmes
    # ex [['y'],['b','r','i'],['g','@','n','s']]
    splitWd=[[syll for syll in sp.split(',') if syll!=''] for sp in split1] 
    f=i[1] # sa fréquence
    if f!=0: # si mot a une fréquence non nulle :
        a=schema(wd,Voy,Cons) # on calcule son schéma
        if a in ['CV.CV.CVC','CVC.CV.CVC','CV.CVC.CVC']: # si c'est un des 3 retenus
            if wd.count('.')>2: # print si problème de cohérence nbSyll dans le dico 
                print wd # mots de + de 3 syllabes
            if len(splitWd)==3: # mot ok si 3 syllabes détectées
                for syll in splitWd: # on ajoute la fréq de chaque syllabe au dico 
                    dicoS[tuple(syll)]=dicoS.get(tuple(syll),0)+f # 0 valeur par défaut


# dico contenant les fréquences des 2 schémas
dicoSyll={"CV":[],"CVC":[]}
for i in dicoS.items(): # TODO
    syll=i[0]
    f=float(i[1])
    # pour chaque schéma, liste des syllabes et de leur fréquence
    dicoSyll[schema(syll,Voy,Cons)].append([syll,f]) 



# on stocke les différentes données calculées
#with open('germanWords.pkl','wb') as f:
#    pickle.dump([WordsList,AllWordsList,d,db,list3,dicoSyll],f,pickle.HIGHEST_PROTOCOL)
