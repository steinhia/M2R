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
f=codecs.open("german_lexicon.txt",encoding="utf-8") # f pour fichier
l=f.read().splitlines() # une case par ligne du fichier
dico={}
# on rajoute des mots au dictionnaire : pseudo-mots, fautes de frappe etc
# li correspond aux mots de i syllabes
for i in l:
    line=str(i).split('\t')
    dico[line[0]]=line[1].count('-')+1
l1=['hm','im','oh','zur','beim','dass','vom','am','hab','nee','crew','na','nem','ne','nen','puh','uff','"m"','"V"','keit','te','Tipps','stûck','New','York','ups','"L"','"S"','cool','"Tik"','"ja','"sie"',"ncoh","huch",'"Su"','"K"']
for i in l1:
    dico[i]=1
l2=['okay','ok','Filmteam','Alien','geschafft','Lasgich','happy','ärmel','düne','dschungel','Deko','Gleitschirm','bestaunt','Löchter','einën','Bubbel','Ufo','Fenchel','spîral','Dikte','Fahrwerk','bräuchte','Matretsch','platziert','proppen','Spîtzen',"Ärmchen","freundet","Skateboard","koration"]
for i in l2:
    dico[i]=2
l3=['Holzfäller','Grillparty','Soltete','Soldikte','Tireinat','Ligete','Sonistik','Tereinat','Keimate','Sodecktele','Keimase','SOnestik','Melare','Zulerge','Lasgelich','Welare','Sonestik','Somistik','Meidikte','Kalmate','Melerge','Lersgelich','behilfslich','ähliches','Mergawe','Mandete','Tereimat','Sudete','Zudete','Sodete','Beinchen','Zelerge','Tereineit','Wecktolin','Lasgerich','Melawe','Zugunste','Megenda','Migete','Sunistik','Tiejenat','Melagisch','Matreschke','Preneite','förmigen','sympatisch','U-Boot-Schiff','Zergine','Somete','Kalmari','Sonete','Meitendich',"anbilten","Suline","Mielbete","Wecktellin","Solistik","Mattendisch","Sultete","gelandend","Resisseur","Mielage","Velozit","Melbete","Madikt","Madikten","Darsteller","Mattendrich","Mälare","Mattendix","Milbete","Zerlare","Lichteinfluss","Litende"]
for i in l3:
    dico[i]=3
l4=['dreickiges','blattförmigen','kontruieren','Gelaskela','halbrundförmig','Ausstülpungen','Astförmige','dreiekigen','dreeickigen',"dekorativ","lichtempfindlich","lichtempfindllich","Aufblasfunktion","wegzuscheuchen","Weckteli","Malerge","rauszufinden","dreiecksförmig","Fahruntersatz","rumzureisen","ungesehen","bogenförmig","Unterstûtzung","Darstellerin","Bohrmaschine","Tereinaten","gewundenen","spîralförmig","geordneten","lichtempflindlich"]
for i in l4:
    dico[i]=4
l5=["beziehungsweise","Schneckenhausförmig","Außeerirdischen","Außererirdische","Außereridische","quadratförmiges","schneckenhausförmig","Vorwärtskommweise","Kameraleuten","tropfenförmiges","schraubenförmig","weiterzuhelfen","Außeriridische","Außeridischen"]
for i in l5:
    dico[i]=5
l6=["zusammengebappte","hineinzugelangen","regentropfenförmig","Fortbewegungsmitel","entgegenzuwirken"]
for i in l6:
    dico[i]=6
l7=["Karamelkarawane","aerodynamische","Au◊erirdischengruppe","Außerridischengruppe","Sprungfortbewegungsmittel","aerodymamische"]
for i in l7:
    dico[i]=7

# si trouve une fin correspondante, ok, sinon cherche un autre symbole de fin ds test
# cherche d'abord une fin correspondante pour gérer les cas où on  a [{..} .. (..)..]
# enlève les parties entre {} etc
def removePair(mots,deb,fin):
    # on enlève les couples congruents ou non (} dans un même mot (et donc même indice)
    test=['}',')',']']
    for i,mot in enumerate(mots.copy()): # i,mot = indice, valeur
        if deb in mot and any(brace in mot for brace in test): # any=si au moins 1
            mots.remove(mot)
    # s'il existe un mot contenant {,[,(
    if any(deb in mot for mot in mots):
        # liste des indices contenant accolade (au sens large)  ouvrante (deb)
        indexDeb=[i for i in range(len(mots)) if deb in mots[i]][0]
        # on est pas sûr qu'il y ait l'accolade fermante correspondante (erreur ?)
        indexFin=[i for i in range(len(mots)) if fin in mots[i]]
        # paire incongruente { ] 
        if len(indexFin)==0:
            indexFin=-1
            # si on trouve pas l'accolade congruente, on teste toutes les autres 
            # dans la liste test
            for brace in test:
                # s'il existe une accolade fermante quelconque de test dans mots
                if any(brace in mot for mot in mots): 
                    indexFin=[i for i in range(len(mots)) if brace in mots[i]][0]
        else:
            indexFin=indexFin[0]
        # on enlève les mots contenus entre les 2 signes
        mots=mots[:indexDeb]+mots[min(indexFin+1,len(mots)):]
    return mots

# enlève les parties entre {}, [] ou () avec erreurs ({] par ex)
def removeNotes(mots):
    mots=removePair(mots,'{','}')
    mots=removePair(mots,'(',')')
    mots=removePair(mots,'[',']')
    return mots

# coupe le mot au milieu pour voir si les 2 mots existent milchkuh -> milch kuh
def cutWord(mot,dico):
    for i in range(1,len(mot)-1):
        mot1=mot[:i] # i exclus
        mot2=mot[i:] # i inclus
        nb1=calcSyll(mot1,dico)
        nb2=calcSyll(mot2,dico)
        if nb1>0 and nb2>0:
            return nb1+nb2
    return 0

# à la fin, fautes usuelles à l'oral prises en compte
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
    # il peut manquer 1 lettre + ' à la fin 'ne
    elif mot[0]=="'" and mot[1:] in dico.keys():
        return dico[mot[1:]]
    # so'n -> soein 
    elif "'" in mot and mot.replace("'","ei") in dico.keys():
        return dico[mot.replace("'","ei")]
    return 0

# calcule le nombre de syllabes contenus dans un IPU (une annotation)
def nbSyllOneAnnot(mots,dico):
    nbSyll=0
    for mot in mots: # parcourt la liste de mots
        nb=calcSyll(mot,dico) # nbSyll contenues dans un seul mot
        if nb==0: # mot pas dans le dico
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
        # si sont dans IPU dans plus 2 mots, und,ja,genau pas hésitations
        if ('hm'==i.lower()) or (('und'==i.lower() or 'ja'==i.lower() or 'genau'==i.lower()) and len(mots)<=2):
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

def plotF(fTab):
    # plot de la fréquence au cours du temps
    x=[i for i in range(len(fTab))]
    plt.plot(x,fTab)


#### main : analyse des résultats

c=[0,0,0,0];s=[0,0,0,0];ccount=[0,0,0,0];scount=[0,0,0,0]
Special=['{','}','_','Anglais','(',')']
fC=[0,0,0,0];fS=[0,0,0,0]
varfC=[0,0,0,0];varfS=[0,0,0,0]
csvTab=[]
dicoHes={}
for idNum in range(26):
    path='Resultats/id'+str(idNum).zfill(2)+'/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        # num2CS dans Python Utils (StoryCOnd), calcule condition/story ac filename
        [cond,story]=num2CS(filename)
        # filename2key dans StoryCond, dans PythonUtils/
        cle=filename2key(filename) # cle dans les dicosHesit , pour avoir un nom court
        # on fait ces analyses seulement pour les rappels séparés
        if cond!=-1: # -1 pour les rappels groupés/non spérés par condition
            nbCSV=0 # nb total de syllabes qu'on mettra dans le csv
            nbHesit=0 
            f=readTG(filename)
            annotations=f.get_tier_by_name('transcription').annotations
            lenFile=int(annotations[-1].end_time*100)
            fTab=np.zeros(lenFile) # tableau servant à calculer le débit (obsolète)
            for ann in annotations:
                t=ann.text
                # on split 1 IPU/annotation en une liste de mots
                mots=t.split() # split par espace
                # on enlève les parties non utilisées ex {B} pour bruit
                mots=removeNotes(mots)
                # nombre de syllabes pour 1 IPU
                nbSyll=nbSyllOneAnnot(mots,dico) # dico[mot]=nbSyllabes(mot)
                nbCSV+=nbSyll
                # on incrémente nbHesit avec le nombre d'hésitations de l'IPU courant
                nbHesit+=nbHesitations(mots)
                # on remplit le tableau de débit (plus utilisé)
                completeFTab(cond,story,nbSyll,ann,fTab)
            # on analyse les hésitations : analyse de synchro
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
            # plot de fTab
            #plotF(fTab)
            #plt.show()
            # création des lignes du csv
            createLigne(filename,csvTab,[nbCSV,np.mean(fTab),np.var(fTab),nbHesit,nbHesit/nbCSV])

# on enregistre ici les infos des hésitations, et on analyse la synchro avec le vélo dans synchro.py
#print(dicoHes.keys())

SavePkl('Hes.pkl',dicoHes)
# une ligne par fichier du jour 1 ou 2
# écriture du csv : fonction writeCSV dans PythonUtils CSV.py
firstLine=["nbSyll","mean f", "var f","nbHesit","propHesit"]
WriteCSV(csvTab,firstLine,'csvFiles/brutDebit.csv')


