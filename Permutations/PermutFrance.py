# -*- coding: utf-8 -*- 
import random
import pickle
import itertools

# pour enregistrer l'ordre des permutations en pkl
def SavePkl(filename,data):
    name=filename[:-4]+'.pkl'
    output = open(name, 'wb')
    pickle.dump(data, output)

#ordre choisi : s c

ordre= [
[[4, 3], [2, 4], [1, 2], [3, 1]],
[[2, 2], [1, 4], [3, 3], [4, 1]],
[[4, 3], [1, 2], [2, 4], [3, 1]],
[[3, 4], [4, 2], [1, 3], [2, 1]],
[[3, 4], [1, 3], [4, 2], [2, 1]],
[[1, 1], [2, 3], [4, 4], [3, 2]],
[[3, 4], [4, 2], [2, 1], [1, 3]],
[[1, 1], [4, 4], [2, 3], [3, 2]],
[[1, 1], [3, 2], [2, 3], [4, 4]],
[[2, 2], [4, 1], [3, 3], [1, 4]],
[[1, 1], [2, 3], [3, 2], [4, 4]],
[[1, 1], [4, 4], [3, 2], [2, 3]],
[[3, 4], [2, 1], [4, 2], [1, 3]],
[[4, 3], [3, 1], [1, 2], [2, 4]],
[[2, 2], [4, 1], [1, 4], [3, 3]],
[[2, 2], [3, 3], [4, 1], [1, 4]],
[[3, 4], [2, 1], [1, 3], [4, 2]],
[[4, 3], [3, 1], [2, 4], [1, 2]],
[[2, 2], [1, 4], [4, 1], [3, 3]],
[[4, 3], [1, 2], [3, 1], [2, 4]],
[[1, 1], [3, 2], [4, 4], [2, 3]],
[[2, 2], [3, 3], [1, 4], [4, 1]],
[[3, 4], [1, 3], [2, 1], [4, 2]],
[[4, 3], [2, 4], [3, 1], [1, 2]],
]

# equirepartition des histoires par condition
# par condition, le nombre de l'histoire i
# d[cond]=[s1,s2,s3,s4]
def createOrdreCond(ordre, max=-1):
    dico={1:[0,0,0,0],2:[0,0,0,0],3:[0,0,0,0],4:[0,0,0,0]}
    if max==-1:
        max=len(ordre)
    for part in ordre[:max]:
        for i in part:
            d=dico[int(i[1])] # on choisit la condition
            d[int(i[0])-1]+=1 # on incrémete l'histoire (commence à 0)
    return dico

#d[s]=[o1,o2,o3,o4] 
# chaque élément du dico (d[s]) est le nbre d'apparitions des ordres pour l'histoire s
def createDicoS(ordre, max=-1):
    # on regarde les effets d'ordre pour chaque histoire 
    dicoS={1:[0,0,0,0],2:[0,0,0,0],3:[0,0,0,0],4:[0,0,0,0]}
    if max==-1:
        max=len(ordre)
    for part in ordre[:max]: # part= [ [1,4], [4,2], [3,3], [2,1] ] -> 1 participant
        for i,couple in enumerate(part): # couple = [1,4]
            d=dicoS[int(couple[0])] # on choisit l'histoire
            d[i]+=1 # on incrémente la position i de l'histoire s
    return dicoS

#d[c]=[o1,o2,o3,o4]
def createDicoC(ordre, max=-1):
    # on regarde les effets d'ordre pour chaque condition 
    dicoC={1:[0,0,0,0],2:[0,0,0,0],3:[0,0,0,0],4:[0,0,0,0]}
    if max==-1:
        max=len(ordre)
    for part in ordre[:max]:
        for i,couple in enumerate(part):
            d=dicoC[int(couple[1])] # on choisit la condition
            d[i]+=1 # on incrémente la position i de la condition c
    return dicoC

# évalue les permutations en analysant les dictionnaires : avec un nombre précis, TODO
def evaluation(dicoS,dicoC,dico,printOK=False,val=6):
    evaluation=0
    for i in dicoS.values():
        for j in i:
            evaluation+=abs(j-val) # si 20 personnes, idéal = tout le monde à 5
    for i in dicoC.values():
        for j in i:
            evaluation+=abs(j-val)
    for i in dico.values():
        for j in i:
            evaluation+=abs(j-val)
    if printOK: # affiche les dictionnaires
        print "dicoS",dicoS,"\n","dicoC",dicoC,"\n","dicoAssignOC",dico,"\n"," eval",evaluation
    return evaluation

dico=createOrdreCond(ordre) # dico d'assignation ordres-conditions
dicoC=createDicoC(ordre) # dico ordre des conditions
dicoS=createDicoS(ordre) # dico ordre des histoires
evalBest=evaluation(dicoS,dicoC,dico,True) # évalue les 3 conditions 

# on change l'ordre des participants pour être plus équilibré en milieu de session
#perm24=list(itertools.permutations([i for i in range(24)]))
perm24=[i for i in range(24)]
perm24Best=list(perm24)
evalBest=1000


#for i in range(500000000):
#    random.shuffle(perm24)
#    ordreTmp=[ordre[i] for i in perm24]
#    # contrebalancement au bout de 12
#    dico12=createOrdreCond(ordreTmp,12) # dico d'assignation ordres-conditions
#    dicoC12=createDicoC(ordreTmp,12) # dico ordre des conditions
#    dicoS12=createDicoS(ordreTmp,12) # dico ordre des histoires
#    eval12=evaluation(dicoS12,dicoC12,dico12,False,3) # évalue les 3 conditions 
#    # contrebalancement au bout de 16
#    dico16=createOrdreCond(ordreTmp,16) # dico d'assignation ordres-conditions
#    dicoC16=createDicoC(ordreTmp,16) # dico ordre des conditions
#    dicoS16=createDicoS(ordreTmp,16) # dico ordre des histoires
#    eval16=evaluation(dicoS16,dicoC16,dico16,False,4) # évalue les 3 conditions 
#    # contrebalancement au bout de 20
#    dico20=createOrdreCond(ordreTmp,20) # dico d'assignation ordres-conditions
#    dicoC20=createDicoC(ordreTmp,20) # dico ordre des conditions
#    dicoS20=createDicoS(ordreTmp,20) # dico ordre des histoires
#    eval20=evaluation(dicoS20,dicoC20,dico20,False,5) # évalue les 3 conditions 
#    evalTmp=eval20+eval16+eval12
#    if evalTmp<evalBest:
#        evalBest=evalTmp
#        perm24Best=list(perm24)
#print("best",evalBest)
#print(perm24Best)

# ordre où tout est équilibré au bout de 12 participants
Perm12=[3, 13, 6, 17, 1, 8, 5, 18, 10, 4, 23, 14, 0, 15, 12, 9, 16, 7, 21, 22, 20, 19, 11, 2]
# équilibré à 16
Perm16=[8, 18, 10, 5, 22, 3, 0, 23, 13, 20, 9, 1, 14, 4, 17, 6, 19, 21, 15, 16, 2, 7, 12, 11]
# à 20
Perm20=[1, 12, 19, 23, 14, 4, 3, 17, 13, 2, 18, 16, 6, 8, 21, 10, 11, 5, 7, 15, 20, 0, 9, 22]
# à 16 et 20
Perm1620=[16, 13, 14, 9, 11, 2, 0, 15, 8, 1, 20, 22, 4, 6, 5, 23, 18, 3, 17, 10, 7, 12, 21, 19]
# équilibré à 16 et 20, quasi équilibré à 12
PermSum=[17, 18, 10, 4, 22, 11, 16, 0, 9, 15, 2, 20, 14, 3, 23, 8, 12, 19, 21, 7, 6, 5, 13, 1]


# ordre équilibré à 16, 20 et 24 et presque à 12
ordre=[ordre[i] for i in PermSum]

# si on veut étendre à plus de participants, il suffit de garder la même liste en appliquant une permutation de [1,2,3,4] -> ...
perm1=[1,0,3,2]
perm2=[3,2,1,0]
perm3=[2,3,0,1]

# listes suivantes
ordre1=[[ [perm1[i-1]+1,perm1[j-1]+1] for i,j in part] for part in ordre]
ordre2=[[ [perm2[i-1]+1,perm2[j-1]+1] for i,j in part] for part in ordre]
ordre3=[[ [perm3[i-1]+1,perm3[j-1]+1] for i,j in part] for part in ordre]




print("24 premiers participants : ")
for i in ordre:
    print i
print(" 2e liste de 24")
for i in ordre1:
    print i
print(" 3e liste de 24")
for i in ordre2:
    print i
print(" 4e liste de 24")
for i in ordre3:
    print i

dico=createOrdreCond(ordre+ordre1+ordre2+ordre3) # dico d'assignation ordres-conditions
dicoC=createDicoC(ordre+ordre1+ordre2+ordre3) # dico ordre des conditions
dicoS=createDicoS(ordre+ordre1+ordre2+ordre3) # dico ordre des histoires
print "dicoS",dicoS,"\n","dicoC",dicoC,"\n","dicoAssignOC",dico,"\n"
SavePkl('PermutFrance.pkl',ordre+ordre1+ordre2+ordre3)


