# -*- coding: utf-8 -*- 
import random
import pickle

# TODO import pour savepkl

# pour enregistrer l'ordre des permutations en pkl
def SavePkl(filename,data):
    name=filename[:-4]+'.pkl'
    output = open(name, 'wb')
    pickle.dump(data, output) # on stocke data dans le fichier name

# ordre peut être vu comme [a,b,c,d] qui respecte les 3 conditions
# on affecte [a,b,c,d] à [1,2,3,4]
# si [a,b,c,d]=[3,1,4,2], on respecte toujours les 3 conditions
#ordre choisi : s c
ordre=[[[2, 4], [4, 1], [1, 2], [3, 3]],
     [[4, 3], [1, 2], [2, 4], [3, 1]],   
     [[1, 1], [4, 4], [3, 2], [2, 3]], 
     [[1, 1], [3, 2], [4, 4], [2, 3]],
     [[3, 4], [4, 2], [2, 1], [1, 3]],
     [[4, 3], [1, 2], [3, 1], [2, 4]],
     [[2, 2], [4, 1], [3, 3], [1, 4]],
     [[1, 1], [2, 3], [4, 4], [3, 2]],
     [[4, 3], [3, 1], [2, 4], [1, 2]],
     [[2, 2], [3, 3], [1, 4], [4, 1]],
     [[4, 3], [2, 4], [3, 1], [1, 2]],
     [[3, 4], [2, 1], [4, 2], [1, 3]],
     [[2, 2], [1, 4], [3, 3], [4, 1]],
     [[4, 3], [2, 4], [1, 2], [3, 1]],
     [[3, 4], [1, 3], [4, 1], [2, 2]], 
     [[1, 1], [4, 2], [2, 3], [3, 4]], 
     [[2, 1], [3, 4], [1, 3], [4, 2]], 
     [[2, 1], [3, 4], [1, 3], [4, 2]], 
     [[1, 4], [3, 3], [4, 2], [2, 1]], 
     [[3, 2], [2, 1], [1, 3], [4, 4]], 
     [[3, 2], [1, 1], [2, 3], [4, 4]],
     [[4,4],[1,3],[2,2],[3,1]],
     [[3,2],[2,3],[4,1],[1,4]],
     [[2,2],[3,4],[1,1],[4,3]],
     [[1,4],[4,2],[3,3],[2,1]]
        ]


# equirepartition des histoires par condition
# par condition, le nombre de l'histoire i
# d[cond]=[s1,s2,s3,s4]
# cond = (1,2,3,4), histoire= liste
def createAssignCondStory(ordre):
    dico={1:[0,0,0,0],2:[0,0,0,0],3:[0,0,0,0],4:[0,0,0,0]}
    for part in ordre:
        for i in part:
            d=dico[int(i[1])] # on choisit la condition
            d[int(i[0])-1]+=1 # on incrémete l'histoire (commence à 0)
    return dico

#d[s]=[o1,o2,o3,o4]-> ordres 
# chaque élément du dico (d[s]) est le nbre d'apparitions des ordres pour l'histoire s
def createDicoS(ordre):
    # on regarde les effets d'ordre (la liste)  pour chaque histoire (1,2,3,4)
    dicoS={1:[0,0,0,0],2:[0,0,0,0],3:[0,0,0,0],4:[0,0,0,0]}
    for part in ordre: # part= [ [1,4], [4,2], [3,3], [2,1] ] -> 1 participant/1 ligne
        # couple = [1,4], i = position/ordre tmp du couple, ici 0 pour [1,4]
        for i,couple in enumerate(part): 
            d=dicoS[int(couple[0])] # on choisit l'histoire = 1 liste de longueur 4
            # ok car d est un pointeur -> ça met à jour la liste et le dico
            d[i]+=1 # on incrémente la position/ordre  i de l'histoire s
    return dicoS

#d[c]=[o1,o2,o3,o4]
def createDicoC(ordre):
    # on regarde les effets d'ordre pour chaque condition 
    dicoC={1:[0,0,0,0],2:[0,0,0,0],3:[0,0,0,0],4:[0,0,0,0]}
    for part in ordre:
        for i,couple in enumerate(part):
            d=dicoC[int(couple[1])] # on choisit la condition
            d[i]+=1 # on incrémente la position i de la condition c
    return dicoC

# évalue les permutations en analysant les dictionnaires
def evaluation(dicoS,dicoC,dico,printOK=False):
    evaluation=0
    for i in dicoS.values(): # i = 1 histoire
        for j in i: # une position/un ordre
            evaluation+=abs(j-5) # si 20 personnes, idéal = tout le monde à 5
    for i in dicoC.values():
        for j in i:
            evaluation+=abs(j-5)
    for i in dico.values():
        for j in i:
            evaluation+=abs(j-5)
    if printOK: # affiche les dictionnaires
        print "dicoS",dicoS,"\n","dicoC",dicoC,"\n","dicoAssignOC",dico,"\n"," eval",evaluation
    return evaluation

dico=createAssignCondStory(ordre) # dico d'assignation ordres-conditions
dicoC=createDicoC(ordre) # dico ordre des conditions
dicoS=createDicoS(ordre) # dico ordre des histoires
evalBest=evaluation(dicoS,dicoC,dico,True) # évalue les 3 conditions 

for i in ordre:
    print i
SavePkl('Permut.pkl',ordre)


