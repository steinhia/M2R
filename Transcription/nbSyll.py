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
# on rajoute des mots au dictionnaire : pseudo-mots, fautes de frappe etc
# li correspond aux mots de i syllabes
for i in l:
    line=str(i).split('\t')
    dico[line[0]]=line[1].count('-')+1
l1=['hm','im','oh','zur','beim','dass','vom','am','hab','nee','crew','na','nem','ne','nen','puh','uff','"m"','"V"','keit','te','Tipps','stûck','New','York','ups','"L"','"S"','cool','"Tik"','"ja','"sie"',"ncoh"]
for i in l1:
    dico[i]=1
l2=['okay','ok','Filmteam','Alien','geschafft','Lasgich','happy','ärmel','düne','dschungel','Deko','Gleitschirm','bestaunt','Löchter','einën','Bubbel','Ufo','Fenchel','spîral','Dikte','Fahrwerk','bräuchte','Matretsch','platziert','proppen','Spîtzen']
for i in l2:
    dico[i]=2
l3=['Holzfäller','Grillparty','Soltete','Soldikte','Tireinat','Ligete','Sonistik','Tereinat','Keimate','Sodecktele','Keimase','SOnestik','Melare','Zulerge','Lasgelich','Welare','Sonestik','Somistik','Meidikte','Kalmate','Melerge','Lersgelich','behilfslich','ähliches','Mergawe','Mandete','Tereimat','Sudete','Zudete','Sodete','Beinchen','Zelerge','Tereineit','Wecktolin','Lasgerich','Melawe','Zugunste','Megenda','Migete','Sunistik','Tiejenat','Melagisch','Matreschke','Preneite','förmigen','sympatisch','U-Boot-Schiff','Zergine','Somete','Kalmari','Sonete','Meitendich',"anbilten"]
for i in l3:
    dico[i]=3
l4=['dreickiges','blattförmigen','kontruieren','Gelaskela','halbrundförmig','Ausstülpungen','Astförmige','dreiekigen']
for i in l4:
    dico[i]=4


# enlève les parties entre {} etc
def removePair(mots,deb,fin):
    # on enlève les couples congruents ou non (} dans un même mot (et donc même indice)
    test=['}',')',']']
    for i,mot in enumerate(mots.copy()):
        if deb in mot and any(brace in mot for brace in test):
            mots.remove(mot)
    # s'il existe un mot contenant {,[,(
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
        # on enlève les mots contenus entre les 2 signes
        mots=mots[:indexDeb]+mots[min(indexFin+1,len(mots)):]
    return mots

# enlève les parties entre {}, [] ou () avec erreurs ({] par ex)
def removeAnnot(mots):
    mots=removePair(mots,'{','}')
    mots=removePair(mots,'(',')')
    mots=removePair(mots,'[',']')
    return mots

# coupe le mot au milieu pour voir si les 2 mots existent milchkuh -> milch kuh
def cutWord(mot,dico):
    for i in range(1,len(mot)-1):
        mot1=mot[:i]
        mot2=mot[i:]
        nb=calcSyll(mot1,dico)+calcSyll(mot2,dico)
        if nb>1:
            return nb
    return 0

# return le nombre de syllabes d'un mot avec les cas particuliers
def calcSyll(mot,dico):
    if mot in dico.keys():
        return dico[mot]
    elif mot.lower() in dico.keys():
        return dico[mot.lower()]
    elif mot.capitalize() in dico.keys():
        return dico[mot.capitalize()]
    # en allemand les ss et ß sont interchangeables
    elif mot.replace('ss','ß') in dico.keys():
        return dico[mot.replace('ss','ß')]
    elif mot+'e' in dico.keys(): # ex hab -> habe
        return dico[mot+'e']
    # en allemand on enlève souvent la dernière lettre
    elif mot[:-1] in dico.keys(): 
        return dico[mot[:-1]]
    elif mot[-2:]=="'s" and mot[:-2] in dico.keys(): # ex gab's -> gab
        return dico[mot[:-2]]
    # il peut manquer 1 lettre + ' à la fin
    elif mot[0]=="'" and mot[1:] in dico.keys():
        return dico[mot[1:]]
    # so'n -> soein 
    elif "'" in mot and mot.replace("'","ei") in dico.keys():
        return dico[mot.replace("'","ei")]
    return 0

# calcule le nombre de syllabes contenus dans un IPU (une annotation)
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

# hésitations sous forme de ja, ok, hm, genau, und
def nbHesitations(mots):
    nb=0
    for i in mots:
        # on garde les hm ou les (und, ja, genau isolés)
        if ('hm' in i.lower()) or (('und' in i.lower() or 'ja' in i.lower() or 'genau' in i.lower()) and len(mots)<=2):
            nb+=1
    return nb
            
# pour calculer le débit (plus utilisé) -> on le complète avec 1 annotation
# débit sous forme de plateau pour chaque IPU
def completeFTab(cond,story,nbSyll,ann,fTab):
    # pour avoir le nombre de syllabes par histoire et condition
    if cond!=-1:
        c[int(cond)]+=nbSyll # c, s en variables globales 
        s[int(story)]+=nbSyll
    # on calcule un point par seconde dans fTab -> arrondi des points déb et fin
    deb=int(ann.start_time*100);fin=int(ann.end_time*100)
    freq=0
    # calcule la fréquence/le débit à affecter à un IPU
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

# effets de la condition et de l'histoire sur TODO
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

c=[0,0,0,0];s=[0,0,0,0];ccount=[0,0,0,0];scount=[0,0,0,0]
Special=['{','}','_','Anglais','(',')']
fC=[0,0,0,0];fS=[0,0,0,0]
varfC=[0,0,0,0];varfS=[0,0,0,0]
csvTab=[]
dicoHes={}
for idNum in range(22):
    path='Resultats/id'+str(idNum).zfill(2)+'/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        [cond,story]=num2CS(filename)
        cle=filename2key(filename) # cle dans les dicos, pour avoir un nom court
        # on fait ces analyses seulement pour les rappels séparés
        if cond!=-1:
            nbCSV=0 # nb total qu'on mettra dans le csv
            nbHesit=0 
            f=readTG(filename)
            annotations=f.get_tier_by_name('transcription').annotations
            lenFile=int(annotations[-1].end_time*100)
            fTab=np.zeros(lenFile) # tableau servant à calculer le débit (obsolète)
            for ann in annotations:
                # on enlève les 'transcription' en trop
                t=ann.text.replace('transcription','').replace('.','').replace(',','')
                # on split chaque IPU en une liste de mots
                mots=t.split()
                mots=removeAnnot(mots)
                # nombre de syllabes pour 1 IPU
                nbSyll=nbSyllOneAnnot(mots,dico)
                nbCSV+=nbSyll
                # on incrémente nbHesit avec le nombre d'hésitations de l'IPU courant
                nbHesit+=nbHesitations(mots)
                # on remplit le tableau de fréquences/débit (plus utilisé)
                completeFTab(cond,story,nbSyll,ann,fTab)
            # on analyse les hésitations
            hesitations=f.get_tier_by_name('Hes')
            [hmP,hmD,undP,undD]=[[],[],[],[]]
            # on calcule les positions et durées des hésitations
            for i in hesitations:
                t=i.text
                if t=='hm':
                    hmP.append(float(i.start_time)) # position
                    hmD.append(float(i.end_time-i.start_time)) # durée
                if t=='und':
                    undP.append(float(i.start_time))
                    undD.append(float(i.end_time-i.start_time))
            dicoHes[cle]=[hmP,hmD,undP,undD]
            # on enlève les débuts et fins silencieux
            fTab=removeSpaces(fTab)
            # effets de la condition et de l'histoire
            calcEffets(cond,story,fC,fS,varfC,varfS,ccount,scount)
            # plot de fTab
            #plotF(fTab)
            #plt.show()
            # création des lignes du csv
            createLigne(filename,csvTab,[nbCSV,np.mean(fTab),np.var(fTab),nbHesit,nbHesit/nbCSV])

# on enregistre ici les infos des hésitations, et on analyse la synchro avec le vélo dans synchro.py
print(dicoHes.keys())
SavePkl('Hes.pkl',dicoHes)
print("mots en condition",c)
print("mots en histoires ",s)
print("freq C",fC)
print("freq S",fS)
print("vfreq C",varfC)
print("vfreq S",varfS)

# écriture du csv : fonction writeCSV dans PythonUtils
firstLine=["nbSyll","mean f", "var f","nbHesit","propHesit"]
WriteCSV(csvTab,firstLine,'csvFiles/brutDebit.csv')


