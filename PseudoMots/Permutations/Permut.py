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
import itertools
import numpy as np
from itertools import islice



# 0 = mains libres, 1 = assis sur les mains
# 2 = vélo mains,   3 = vélo jambes


#
## on vérifie que dans chaque quadruplet, on ait une fois chaque histoire et chaque condition
#def verifyQuadriplet(l):
#    c=[i[0] for i in l]
#    s=[i[1] for i in l]
#    if tuple(c) not in list(itertools.permutations([0,1,2,3])):
#        print "erreur condition"
#    if tuple(s) not in list(itertools.permutations([0,1,2,3])):
#        print "erreur story"
#
#def verifyPermutation(resI):
#    res0=[[resI[i][j][0] for j in range(4)] for i in range(24)]
#    res1=[[resI[i][j][1] for j in range(4)] for i in range(24)]
#    e0=0;e1=0
#    for i in list(itertools.permutations([0,1,2,3])):
#        if list(i) not in res0:
#            e0+=1
#        if list(i) not in res1:
#            e1+=1
#    return [e0,e1]
#
#def verifyHistoCond(resI):
#    res=[[0 for i in range(4)] for j in range(4)]
#    for l in resI:
#        for i in l:
#            res[i[0]][i[1]]+=1
#    for l in res:
#        for i in l:
#            if i!=6:
#                return False
#    return True
#
#def eval(resI):
#    for i in resI:
#        verifyQuadriplet(i)
#    [e0,e1]=verifyPermutation(resI)
#    if e0!=0:
#        print "erreur condition : ",e0
#    if e1!=0:
#        print "erreur histoire : ",e1
#    condHisto=verifyHistoCond(resI)
#    if not condHisto:
#        print "erreur condition 3"
#    return [e0,e1]
#
#def nth_index(iterable, value, n):
#    matches = (idx for idx, val in enumerate(iterable) if val == value)
#    return next(islice(matches, n-1, n), None)
#
#def AppendList(a,ListOfList):
#    for i in ListOfList:
#        i.insert(0,a)
#    return ListOfList
#
#def sousMat(tab,i0,j0):
#    return [[tab[i][j] for j in range(len(tab)) if j!=j0] for i in range(len(tab[0])) if i!=i0]
#
#def generateQuadruplets(indicesList):
#    if len(indicesList)==1:
#        return indicesList
#    elif len(indicesList)>1:
#        # parcours par colonne
#        n=len(indicesList)
#        res=[]
#        for i in range(n):
#            res+=AppendList(indicesList[0][i],generateQuadruplets(sousMat(indicesList,0,i)))
#        return res
#
## liste trouvée à la main, par une méthode type sudoku
#
#tuples=[[0,'a'],[1,'b'],[2,'c'],[3,'d'],[1,'c'],[0,'d'],[3,'a'],[2,'b'],[2,'d'],[0,'b'],[1,'a'],[3,'c'],[3,'b'],[0,'c'],[1,'d'],[2,'a']]
#
#mat=[[0,1,2,3],
#    [0,2,1,3],
#    [0,2,3,1],
#    [0,3,1,2],
#    [0,3,2,1],
#    [0,1,3,2]]
#m1=list([[x+4 for x in y] for y in mat])
#m2=list([[x+8 for x in y] for y in mat])
#m3=list([[x+12 for x in y] for y in mat])
#
#matF=mat+m1+m2+m3
#
#
#
#for l in matF:
#    for i,nb in enumerate(l):
#        l[i]=tuples[nb]
## on transforme les lettres en chiffres -> beaucoup de combinaisons possibles!
#dico={'a':0,'b':2,'c':1,'d':3}
#for l in matF:
#    for i,nb in enumerate(l):
#        if isinstance(l[i][1],str):
#            l[i][1]=dico[nb[1]]
#
#
#for i in matF:
#    print i
#
#print "\n"
#random.shuffle(matF)
#for i in matF:
#    print i
#eval(matF)
#
#
#

# version récursive :
# on vérifie les conditions 1 et 3, puis on fait des échanges au sein d'un quadruplet



#tupleList=[]
#for i in range(16):
#    tupleList.append([i%4,i/4])
##a=np.reshape(tupleList,(4,4,2))
## pour ne pas manipuler les couples mais leurs indices
#indicesList=[range(4),range(4,8),range(8,12),range(12,16)]

## le but est de ne pas perturber les permutations de gauche ok, tout en changeant droite
## trouve la permutation de gauche correspondant au schéma
#def findPerm(i,res):
#    GList=[[res[k][j][0] for j in range(4)]for k in range(24)]
#    return nth_index(GList,GList[i],2)
#
#resI=generateQuadruplets(indicesList)
#res=[[tupleList[resI[i][j]] for j in range(4)] for i in range(24)]
#
##
## possibilités d'échange
#echg=[[0,1],[0,2],[0,3],[1,2],[3,1],[3,2]]
## ordre des changements
#ev=eval(res)
#for essai in range(10):
#    nL=range(24);random.shuffle(nL)
#    for num in range(24):
#        #random.shuffle(echg)
#        for i in echg :
#            #num=nL[n]
#            res[num][i[0]],res[num][i[1]]=res[num][i[1]],res[num][i[0]]
#            ind=findPerm(num,res)
#            res[ind][i[0]],res[ind][i[1]]=res[ind][i[1]],res[ind][i[0]]
#            evTmp=eval(res)
#            if evTmp[0]>0 or evTmp[1]>ev[1]:
#                # ancienne config
#                res[num][i[0]],res[num][i[1]]=res[num][i[1]],res[num][i[0]]
#                res[ind][i[0]],res[ind][i[1]]=res[ind][i[1]],res[ind][i[0]]
#            else:
#                #print "echg",essai,evTmp[1]
#                ev=list(evTmp)




a=[[[2, 4], [4, 1], [1, 2], [3, 3]],
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
[[3, 2], [2, 1], [4, 4], [1, 3]],
[[2, 2], [1, 4], [3, 3], [4, 1]],
[[4, 3], [2, 4], [1, 2], [3, 1]],
[[3, 4], [4, 2], [1, 3], [2, 1]],
[[4, 3], [3, 1], [1, 2], [2, 4]],
[[3, 4], [1, 3], [2, 1], [4, 2]],
[[3, 4], [1, 3], [4, 2], [2, 1]],
[[1, 1], [4, 4], [2, 3], [3, 2]],
[[2, 2], [1, 4], [4, 1], [3, 3]],
[[2, 2], [3, 3], [4, 1], [1, 4]],
[[3, 4], [2, 1], [1, 3], [4, 2]],
[[1, 1], [2, 3], [3, 2], [4, 4]],
[[1, 1], [3, 2], [2, 3], [4, 4]]]

with open('Permut.pkl','wb') as f:
    pickle.dump(a,f,pickle.HIGHEST_PROTOCOL)
