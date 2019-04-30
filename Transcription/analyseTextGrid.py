# -*- coding: utf-8 -*
import tgt
import os, glob
import codecs
import ntpath
import csv
import numpy as np
import matplotlib.pyplot as plt
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

# on trouve le nombre de syllabes de chaque mot
f=codecs.open("german_lexicon.txt",encoding="utf-8")
l=f.read().splitlines()
dico={}
for i in l:
    line=str(i).split('\t')
    dico[line[0]]=line[1].count('-')+1
l1=['hm','im','oh','zur','beim','dass','vom','am','hab','nee','crew','na','nem','ne','nen','puh','uff','"m"','"V"','keit','te']
for i in l1:
    dico[i]=1
l2=['okay','ok','Filmteam','Alien','geschafft','Lasgich','happy','ärmel','düne','dschungel','Deko','Gleitschirm','bestaunt','Löchter','einën','Bubbel','Ufo']
for i in l2:
    dico[i]=2
l3=['Holzfäller','Grillparty','Soltete','Soldikte','Tireinat','Ligete','Sonistik','Tereinat','Keimate','Sodecktele','Keimase','SOnestik','Melare','Zulerge','Lasgelich','Welare','Sonestik','Somistik','Meidikte','Kalmate','Melerge','Lersgelich','behilfslich','ähliches','Fenchel']
for i in l3:
    dico[i]=3
l4=['dreickiges','blattförmigen']
for i in l4:
    dico[i]=4

def removeAnnot(mots):
    if any('{' in mot for mot in mots):
        indexDeb=[i for i in range(len(mots)) if '{' in mots[i]][0]
        indexFin=[i for i in range(len(mots)) if '}' in mots[i]]
        if len(indexFin)==0:
             indexFin=[i for i in range(len(mots)) if ')' in mots[i]][0]
        else:
            indexFin=indexFin[0]


        mots=mots[:indexDeb]+mots[min(indexFin+1,len(mots)):]
    if any('(' in mot for mot in mots):
        indexDeb=[i for i in range(len(mots)) if '(' in mots[i]][0]
        indexFin=[i for i in range(len(mots)) if ')' in mots[i]][0]
        mots=mots[:indexDeb]+mots[min(indexFin+1,len(mots)):]
    return mots

def cutWord(mot,dico):
    for i in range(1,len(mot)-1):
        mot1=mot[:i]
        mot2=mot[i:]
        nb=calcSyll(mot1,dico)+calcSyll(mot2,dico)
        if nb>1:
            return nb
    return 0

def calcSyll(mot,dico):
    if mot in dico.keys():
        return dico[mot]
    elif mot.lower() in dico.keys():
        return dico[mot.lower()]
    elif mot.capitalize() in dico.keys():
        return dico[mot.capitalize()]
    elif mot.replace('ss','ß') in dico.keys():
        return dico[mot.replace('ss','ß')]
    elif mot+'e' in dico.keys(): # ex hab -> habe
        return dico[mot+'e']
    elif mot[:-1] in dico.keys():
        return dico[mot[:-1]]
    elif mot[-2:]=="'s" and mot[:-2] in dico.keys(): # ex gab's -> gab
        return dico[mot[:-2]]
    elif mot[0]=="'" and mot[1:] in dico.keys():
        return dico[mot[1:]]
    elif "'" in mot and mot.replace("'","ei") in dico.keys():
        return dico[mot.replace("'","ei")]

    return 0

#def num2CS(filename):
#    name=ntpath.basename(filename)
#    cOrder=name[6:10]
#    sOrder=name[12:16]
#    num=int(name[21:23])
#    tab=[6,3,8,5,10,7,12,9]
#    if num in tab:
#        return [int(cOrder[int(tab.index(num)/2)]),int(sOrder[int(tab.index(num)/2)])]
#    return [-1,-1]
#
#def createLigne(filename,nbSyll,meanf,varf,csvTab):
#    name=ntpath.basename(filename)
#    cOrder=name[6:10]
#    sOrder=name[12:16]
#    num=int(name[21:23])
#    sujet=int(name[2:4])
#    jour=int(name[18])
#    [c,s]=num2CS(name)
#    csvTab.append([sujet,jour,cOrder,sOrder,c,s,nbSyll,meanf,varf])

def nbSyllOneAnnot(mots,dico):
    nbSyll=0
    for mot in mots:
        nb=calcSyll(mot,dico)
        if nb==0:
            nb=cutWord(mot,dico)
        if nb==0 and '_' not in mot:
                1#print(mot,mots)
        nbSyll+=nb
    return nbSyll

def completeFTab(cond,story,nbSyll,ann,fTab):
    if cond!=-1:
        c[int(cond)-1]+=nbSyll
        s[int(story)-1]+=nbSyll
    deb=int(ann.start_time*100);fin=int(ann.end_time*100)
    freq=0
    if fin>deb:
        freq=nbSyll*100/(fin-deb)
    else:
        freq=nbSyll
    for i in range(deb,min(len(fTab),fin+1)):
        fTab[i]=freq

def removeSpaces(fTab):
    b=next(x for x in range(len(fTab)) if fTab[x]!=0)
    e=max(index for index, item in enumerate(fTab) if item!=0)
    fTab=fTab[b:e+1]
    return fTab

def calcEffets(cond,story,fC,fS,varfC,varfS,ccount,scount):
    fC[cond-1]+=np.mean(fTab)
    fS[story-1]+=np.mean(fTab)
    varfC[cond-1]+=np.var(fTab)
    varfS[story-1]+=np.var(fTab)
    ccount[int(cond)-1]+=1
    scount[int(story)-1]+=1


def plotF(fTab):
    # plot de la fréquence au cours du temps
    x=[i for i in range(len(fTab))]
    plt.plot(x,fTab)
    #plt.show()

c=[0,0,0,0];s=[0,0,0,0];ccount=[0,0,0,0];scount=[0,0,0,0]
Special=['{','}','_','Anglais','(',')']
fC=[0,0,0,0];fS=[0,0,0,0]
varfC=[0,0,0,0];varfS=[0,0,0,0]
csvTab=[]
for idNum in range(7):
    path='Resultats/id'+str(idNum)+'/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        [cond,story]=num2CS(filename)
        if cond!=-1:
            nbCSV=0
            nbSyll=0
            f=tgt.io.read_textgrid(filename,encoding='utf-16-be')
            annotations=f.get_tier_by_name('transcription').annotations
            lenFile=int(annotations[-1].end_time*100)
            fTab=np.zeros(lenFile)
            for ann in annotations:
                t=ann.text.replace('transcription','').replace('.','').replace(',','')
                mots=t.split()
                mots=removeAnnot(mots)
                nbSyll=nbSyllOneAnnot(mots,dico)
                nbCSV+=nbSyll
                # on remplit le tableau de fréqunences 
                completeFTab(cond,story,nbSyll,ann,fTab)
            # on enlève les débuts et fins silencieux
            fTab=removeSpaces(fTab)
            # effets de la condition et de l'histoire
            calcEffets(cond,story,fC,fS,varfC,varfS,ccount,scount)
            # plot de fTab
            plotF(fTab)
            # création du csv
            createLigne(filename,csvTab,[nbCSV,np.mean(fTab),np.var(fTab)])
print("mots en condition",c)
print("mots en histoires ",s)
print("freq C",fC)
print("freq S",fS)
print("vfreq C",varfC)
print("vfreq S",varfS)

firstLine=["id","jour","ordre histoires","ordre conditions","histoire","condition","nbSyll","mean f", "var f"]
WriteCSV(csvTab,firstLine,'brutDebit.csv')


#with open('brutDebit.csv', mode='w') as f:
#    writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#    writer.writerow(["id","jour","ordre histoires","ordre conditions","histoire","condition","nbSyll","mean f", "var f"])
#    listLines=[]
#    for i in csvTab:
#        if i not in listLines:
#            writer.writerow(i) 
#        listLines.append(i)
