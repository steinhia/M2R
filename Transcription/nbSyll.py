# -*- coding: utf-8 -*
import os, glob
import tgt
import stackprinter
import codecs
import numpy as np
import matplotlib.pyplot as plt
path='../PythonUtils/'
stackprinter.set_excepthook(style='color')
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
l1=['hm','im','oh','zur','beim','dass','vom','am','hab','nee','crew','na','nem','ne','nen','puh','uff','"m"','"V"','keit','te','Tipps','stûck','New','York','ups','"L"','"S"']
for i in l1:
    dico[i]=1
l2=['okay','ok','Filmteam','Alien','geschafft','Lasgich','happy','ärmel','düne','dschungel','Deko','Gleitschirm','bestaunt','Löchter','einën','Bubbel','Ufo','Fenchel','spîral','Dikte']
for i in l2:
    dico[i]=2
l3=['Holzfäller','Grillparty','Soltete','Soldikte','Tireinat','Ligete','Sonistik','Tereinat','Keimate','Sodecktele','Keimase','SOnestik','Melare','Zulerge','Lasgelich','Welare','Sonestik','Somistik','Meidikte','Kalmate','Melerge','Lersgelich','behilfslich','ähliches','Mergawe','Mandete','Tereimat','Sudete','Zudete','Sodete','Beinchen','Zelerge','Tereineit','Wecktolin','Lasgerich']
for i in l3:
    dico[i]=3
l4=['dreickiges','blattförmigen','kontruieren','Gelaskela','halbrundförmig','Ausstülpungen','Astförmige']
for i in l4:
    dico[i]=4



def removePair(mots,deb,fin):
    # on enlève les couples dans le même mot
    test=['}',')',']']
    for i,mot in enumerate(mots.copy()):
        if deb in mot and any(brace in mot for brace in test):
            mots.remove(mot)
    if any(deb in mot for mot in mots):
        indexDeb=[i for i in range(len(mots)) if deb in mots[i]][0]
        indexFin=[i for i in range(len(mots)) if fin in mots[i]]
        # paire incongruente { ] etc
        if len(indexFin)==0:
            indexFin=-1
            for brace in test:
                if any(brace in mot for mot in mots):
                    indexFin=[i for i in range(len(mots)) if brace in mots[i]][0]
        else:
            indexFin=indexFin[0]
        mots=mots[:indexDeb]+mots[min(indexFin+1,len(mots)):]
    return mots

def removeAnnot(mots):
    mots=removePair(mots,'{','}')
    mots=removePair(mots,'(',')')
    mots=removePair(mots,'[',']')
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

def nbSyllOneAnnot(mots,dico):
    nbSyll=0
    for mot in mots:
        nb=calcSyll(mot,dico)
        if nb==0:
            nb=cutWord(mot,dico)
        if nb==0 and '_' not in mot:
                print("mot inconnu ",mot,mots)
        nbSyll+=nb
    return nbSyll

def nbHesitations(mots):
    nb=0
    for i in mots:
        if 'hm' in i.lower():
            nb+=1
    return nb
            

def completeFTab(cond,story,nbSyll,ann,fTab):
    if cond!=-1:
        c[int(cond)]+=nbSyll
        s[int(story)]+=nbSyll
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
    fC[cond]+=np.mean(fTab)
    fS[story]+=np.mean(fTab)
    varfC[cond]+=np.var(fTab)
    varfS[story]+=np.var(fTab)
    ccount[int(cond)]+=1
    scount[int(story)]+=1


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
for idNum in range(18):
    path='Resultats/id'+str(idNum)+'/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        [cond,story]=num2CS(filename)
        if cond!=-1:
            nbCSV=0
            nbSyll=0
            nbHesit=0
            f=readTG(filename)
            annotations=f.get_tier_by_name('transcription').annotations
            lenFile=int(annotations[-1].end_time*100)
            fTab=np.zeros(lenFile)
            for ann in annotations:
                t=ann.text.replace('transcription','').replace('.','').replace(',','')
                mots=t.split()
                mots=removeAnnot(mots)
                nbSyll=nbSyllOneAnnot(mots,dico)
                nbCSV+=nbSyll
                nbHesit+=nbHesitations(mots)
                # on remplit le tableau de fréqunences 
                completeFTab(cond,story,nbSyll,ann,fTab)
            # on enlève les débuts et fins silencieux
            fTab=removeSpaces(fTab)
            # effets de la condition et de l'histoire
            calcEffets(cond,story,fC,fS,varfC,varfS,ccount,scount)
            # plot de fTab
            #plotF(fTab)
            #plt.show()
            # création du csv
            createLigne(filename,csvTab,[nbCSV,np.mean(fTab),np.var(fTab),nbHesit])
print("mots en condition",c)
print("mots en histoires ",s)
print("freq C",fC)
print("freq S",fS)
print("vfreq C",varfC)
print("vfreq S",varfS)

firstLine=["nbSyll","mean f", "var f","nbHesit"]
WriteCSV(csvTab,firstLine,'brutDebit.csv')


