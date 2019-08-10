import os,glob
from mpl_toolkits.mplot3d import Axes3D
import csv
import pickle
import matplotlib.pyplot as plt
import numpy as np
from numpy import mean,sqrt,diff
from scipy.signal import find_peaks
from scipy.signal import butter, filtfilt, hilbert
import scipy
import ntpath
from scipy import interpolate
from itertools import groupby, count
from operator import itemgetter
pathUtils='../PythonUtils/'
exec(open(pathUtils+'StoryCond.py').read())
exec(open(pathUtils+'Dist.py').read())
exec(open(pathUtils+'CSV.py').read())






# parse les fichiers csv, extrait le marqueur le plus circulaire, l'interpole et éventuellement complète avec d'autres marqueurs
# enlève les débuts et fins de fichier non circulaire
# calcule la fréquence au cours du temps avec findpeak
# crée le fichier de données brutes




################### parsing / gestion des fichiers ################

# path pour accéder au dossier mocap d'un participant au jour j
def getPath(num,jr):
    n=str(num).zfill(2) # zfill -> écriture en 2 chiffres  24->24   2->02
    return '../DataComplete/id'+str(n)+'/id'+str(n)+'j'+str(jr)+'/id'+str(n)+'j'+str(jr)+'_MocapCsv/'

def getSamplingRate(filename):
    csvName=filename[:-4]+'.csv' # si jamais filename est en pkl, je change l'extension
    l=CsvReader(csvName)
    return(l[0][5]) # le sampling rate est sur le csv, 1ère ligne 6ème case

# fréquence d'échantillonnage différente selon les fichiers
# crée un dictionnaire contenant la fréquence d'échantillonnage par fichier
def getSamplingRates():
    dico={}
    for idNum in range(1,26): # numéro du participant
        for jr in range(1,3): # jour
            num=str(idNum).zfill(2) # pour être au format 01
            path=getPath(idNum,jr)
            # on fait la liste de tous les csv dans le dossier path
            for filename in glob.glob(os.path.join(path,'*.csv')):
                print(filename)
                # on extrait son sampling rate
                sr=getSamplingRate(filename)
                # on stocke l'information dans le dictionnaire
                dico[filename]=sr
    return dico


# parse tous les fichiers, y compris les moments où un marqueur n'est pas détecté ('')
# pour éviter des fichiers trop lourds, on ne garde que les marqueurs suffisamment 
# longs : ceux en dessous de 100 valeurs (env <1s) n'apportent pas d'info 
# et tout stocker (y compris les '') prend une place monstrueuse
# clé=nom du marqueur, valeur = 3 listes des positions X Y et Z
def parseFile(filename):
    with open(filename, 'r') as csvFile:
        rd= np.array(list(csv.reader(csvFile))) # lecture du csv
    ind=['X','Y','Z']
    dico = {} 
    # on crée les listes de positions des rigid bodies et des marqueurs
    for i in rd[7:]: # début des données à la 8e ligne
        for j,val in enumerate(i): # i = ligne, j=numéro colonne, val=valeur ds csv
            # type = RigidBody, RB Marker, Marker
            # pos = X, Y, Z
            mType=rd[2][j];name=rd[3][j];pos=rd[6][j]
            # on garde soit les RB soit les marqueurs non labellisés, mais en Position
            # _ in name-> RB_Marker, on les veut pas, moins précis, on veut barycentres
            # si 'marker' in name, c'est surement un rigidbody marker
            if rd[5][j]=='Position' and (('Rigid' in mType and '_' not in name) or ('Unlabeled' in name or (mType=='Marker' and 'Marker' not in name))) :
                # si clé existe pas, doit la créer
                if name not in dico.keys():
                    dico[name]=[[],[],[]] # pour les positions X Y Z -> 3 listes
                if val!='':
                    val=float(val)
                # ajoute valeur dans X Y ou Z : pos vaut X Y ou Z -> indice 0 1 ou 2
                # dico[name] = 1 marqueur, dico[name][i] = X Y ou Z de ce marqueur
                dico[name][ind.index(pos)].append(val)
    # on ne garde que les marqueurs "assez longs"
    # on parcourt la copie du dictionnaire parce que parcourir et supprimer -> :/
    for key,val in dico.copy().items():
        # val[0] toujours la même longueur, mais FVal enlève les cases vides
        if len(FVal(val[0]))<100: # TODO FVal met 0 ??????
            del dico[key]
    print(len(dico)," marqueurs détectés")
    return dico

# pour comparer la quantité de mouvements mains-dos, on parse le dos en particulier
def parseBack(filename):
    l=[[],[],[]]
    ind=['X','Y','Z']
    with open(filename, 'r') as csvFile:
        rd= np.array(list(csv.reader(csvFile)))
        for i in rd[7:]:
            for j,val in enumerate(i):
                mType=rd[2][j];name=rd[3][j];pos=rd[6][j];typ=rd[5][j]
                if 'Rigid' in mType and typ=='Position' and '_' not in name and ('B' in name or '6' in name): # selon les fichiers, name='Back' ou 'RigidBody6'
                    if val!='':
                        l[ind.index(pos)].append(float(val))
                    else :
                        l[ind.index(pos)].append('')
    return l




## parseur du fichier csv
# on parse tous les fichiers, même ceux sans vélo
def parseFiles():
    for jour in range(1,3):
        for idNum in range(1,26):
            num=str(idNum).zfill(2)
            path=getPath(idNum,jour)
            for filename in glob.glob(os.path.join(path,'*.csv')):
                print(filename)
                # parse tout
                dico=parseFile(filename)
                name=filename[:-4]+'_all.pkl'
                SavePkl(name,dico)
                # le dos en particulier
                back=parseBack(filename)
                name_back=filename[:-4]+'_back.pkl'
                SavePkl(name_back,back)




# supprime les fichiers pkl contenant string : utile de manière ponctuelle
def delPklFiles(string): # ex string = _2 -> pour supprimer tous les id... _2.pkl
    for idNum in range(1,22):
        for jr in range(1,3):
            num=str(idNum).zfill(2)
            path=getPath(idNum,jr)
            for filename in glob.glob(os.path.join(path,'*.pkl')):
                if string in filename:
                    print(filename)
                    os.remove(filename) # supprime les fichiers


################ gérer les '' (données manquantes) ############################

# pour [x,y,z] ou y : enlève les '', on ne garde que les float
def FVal(value):
    if len(value)==3:
        f=[[float(l) for l in value[k] if l!='']  for k in range(3)]
    else:
        f=[float(l) for l in value if l!='']
    return f

# on remplace les '' par des 0 pour garder la synchronisation temporelle
def FVal0(value):
    if len(value)==3:
        f=[[float(l) if l!='' else 0 for l in value[k]]  for k in range(3)]
    else:
        f=[float(l) if l!=''  else 0 for l in value]
    return f
# renvoie les débuts et fins d'intervalles de masquage

def getRangesLimit(im):
    groups=getRanges(im)
    for i,gp in enumerate(groups):
        groups[i]=[gp[0],gp[-1]] #gp[0]=début, gp[-1]=fin
    return groups


# renvoie les intervalles manquants à partir de tous les indices
def getRanges(im): #im = indices manquants (fonction Im ci-dessous)
    ranges=[]
    for _,g in groupby(enumerate(im),lambda x:x[0]-x[1]):
        group = (map(itemgetter(1),g))
        group = list(map(int,group))
        ranges.append(group)
    return ranges



# m marqueur : liste de longueur 3 (x y z) avec x liste
# indices manquants (marqueurs masqués)
def Im(m):
    if len(m)>0:
         # on parcourt les x, les données manquantes le sont pour x, y et z à la fois
        im=[j for j,l in enumerate(m[0]) if l=='']
        return im
    return []

# indices avec des données float 
def IF(m):
    if len(m)>0:
        iF=[j for j,l in enumerate(m[0]) if l!='']
        return iF
    return []

################ plot ###############################

# tab des x correspondant à un y, indices calculés selon la fréquence d'échant.
def xT(y,sr=-1):
    if sr==-1:
        return [i for i in range(len(y))]
    return [i/sr for i in range(len(y))]




### plots de tout le fichier #####

### 3D ####

ax = plt.axes(projection='3d')
# le pb est peut être plus au niveau des plot -> ax 3D, ax en variable globale ?? non
# sinon pb plot 2d
# plot3D d'un marqueur à partir de sa trajectoire
def plotMarker(value,show=True):
    ax = plt.axes(projection='3d')
    if len(value)==3:
        [x,y,z]=FVal(value)
        ax.plot3D(x,y,z)
    if show:
        plt.show()

# plot de la scène 3D à partir du dictionnaire
# plotMarker -> show=False pour afficher la fenêtre seulement après avoir ploté
# tous les marqueurs
def plotID(dico):
    for key,value in dico.items():
        plotMarker(value,False)
    plt.show()

# plot de la scène 3D à partir du idNum, jour et numéro de la tâche
def plotAllMarkers(num,jr,n=-1):
    num=str(num).zfill(2)
    path=getPath(num,jr)
    for filename in glob.glob(os.path.join(path,'*_all.pkl')):
        if 'n'+str(n).zfill(2) in filename or n==-1:
            print(ntpath.basename(filename)) # nom fichier sans le path
            dico=OpenPkl(filename)
            plotID(dico)

# plot3D du marqueur velo
def plotBike(num,jr,n=-1):
    num=str(num).zfill(2)
    path=getPath(num,jr)
    print(path)
    for filename in glob.glob(os.path.join(path,'*_bike.pkl')):
        if 'n'+str(n).zfill(2) in filename or n==-1:
            print(ntpath.basename(filename))
            bike=FVal(OpenPkl(filename)) # enlever les ''
            if bike!=[]:
                print("len ",len(bike[1])) # axe y vertical
                print(fitCircle(bike[0],bike[1],bike[2]))
                plotMarker(bike)
            else:
                print("pas de marqueur velo")



# plot marqueur de la scène d'un certain nom
def plotMarkerName(name,idNum,jour,n):
    path=getPath(idNum,jour)
    fileNum='n'+str(n).zfill(2)
    for filename in glob.glob(os.path.join(path,'*_all.pkl')):
        if fileNum in filename:
            print(filename)
            dico=OpenPkl(filename)
            for cle,val in dico.items():
                if name in cle:
                    plotMarker(val) # plot le marker du nom name

# on regarde où la détection n'a pas marché
def detectProblems():
    for idNum in range(1,21):
        for jr in range(1,3): # on ne regarde pas le jour 3
            num=str(idNum).zfill(2)
            path=getPath(idNum,jr)
            for filename in glob.glob(os.path.join(path,'*_bike.pkl')):
                # on ouvre le fichier contenant le marqueur cyclique
                bike=OpenPkl(filename)
                # s'il est inexistant ou trop court -> pb de détection
                if len(bike)==0 or len(bike[0])<2000:
                    print("\n pas de marqueur circulaire ", filename)
                    # on ouvre le dico avec tous les marqueurs pour regarder la scène
                    dicoName=filename.replace('bike','all')
                    dico=OpenPkl(dicoName)
                    name=ntpath.basename(filename) # nom sans le path
                    tache=int(name[21:23]) # nxx
                    plotAllMarkers(idNum,jr,tache) # plot de tous les marqueurs
                    plt.show()

#### 2D ###

# plot2D d'un marqueur à partir de la trajectoire
def plot2dMarker(y,sr=-1,show=True):
    y=FVal(y)
    xy= xT(y,sr) # crée le vecteur abscisse
    plt.plot(xy,y)
    if show:
        plt.show()

# plot2D d'un marqueur +pics à partir de la trajectoire
def plot2dMarkerPeaks(y,peaks,sr=-1,show=True,zorder=2):
    plot2dMarker(y,sr,False)
    yp=[y[int(i*sr)] for i in peaks] # position des pics (indices dans peaks)
    # zorder = ordre de plot (point avant lignes ou l'inverse)
    plt.scatter(peaks,yp,color='r',zorder=zorder) # plot de points
    if show:
        plt.show()

# plot l'enveloppe spectrale du signal avec les pics de l'enveloppe
# prend en argument le signal, son enveloppe, les pics, gère juste l'affichage
def plotEnveloppe(y,env,peaks,sr):
    plot2dMarkerPeaks(y,sr,show=False,zorder=3)
    yp=[env[int(i)] for i in peaks] # hauteur de l'env aux indices des pics
    xenv=[h/sr for h in range(len(env))] # liste abscisse y pour les plot
    plt.plot(xenv,env,'r') # plot son eveloppe
    plt.show()


## autre ###

# plot la fft d'un signal (non utilisé)
def plotFFT(data):
    ps = np.abs(np.fft.fft(data))**2 #y
    freqs = np.fft.fftfreq(len(data), 1/30) #t
    idx = np.argsort(freqs)
    plt.plot(freqs[idx], ps[idx])
    #plt.show()

# print les scores de circularité de tous les marqueurs
def printCircleScores(dico):
    print("scores : \n")
    for key,value in dico.items():
        [x,y,z]=FVal(value)
        [circle,dR,residu]=fitCircle(x,y,z)
        print("circle ?",circle,"key ",key,"dR ",dR," residu ",residu," len ",len(FVal(x)))
 
##################### calculs sur les données ################

# renvoie une liste de distances :
# pour chaque point de la liste, distance entre centre et le point
def calc_R(xc, yc, zc,x,y,z):
    """ calculate the distance of each 3D points from the center (xc, yc, zc) """
    return sqrt((x - xc) ** 2 + (y - yc) ** 2 + (z - zc) ** 2)

# pour un marqueur x,y,z = liste de 3 listes, calcule un indice de circularité
# renvoie boolean:cercle ?, rayon, résidu
def fitCircle(x,y,z,seuilR=0.01, seuilResidu=1):
    if len(x)>0:
        [xm,ym,zm] = [mean(x),mean(y),mean(z)] # si cercle, xm etc = centre théorique
        # si cercle parfait, dstance toujours la même
        Ri       = calc_R(xm, ym, zm,x,y,z) # distance au centre pour chaque point
        R=-1
        if len(Ri)>0:
            R        = Ri.mean() # moyenne des distances au centre : rayon empirique
        residu   = sum((Ri - R)**2) # somme des résidus : variance
        dR=abs(R-0.08) # rayon velo environ 0.08 -> on regarde la différence avec 0.08
        # on décide (arbitrairement) d'un seuil d'acceptabilité pour rayon et résidu
        circle=dR<seuilR and residu<seuilResidu # circle = boolean 
        return [circle,dR,residu]
    return [False,1000,10000]

# division terme à terme de l par le scalaire a : retourne une liste
def div(l,a):
    return [float(i)/float(a) for i in l]

# filtre passe bas
def filterL(data,sr):
    # wc = proportion à garder -> 1/10 = très coupé
    b, a = scipy.signal.butter(1, 1/3) # ordre du filtre et wc : fréq de coupure
    return scipy.signal.filtfilt(b,a, data)

# filtre passe haut
def filterH(data,sr):
    b, a = scipy.signal.butter(6, 1/3,btype='high') # ordre du filtre et wc
    return scipy.signal.filtfilt(b,a, data)

# enveloppe spectrale du signal : norme de la transformée de hilbert
# puis on smooth
def calcEnveloppe(y,sr,dMin,prom=0.000002):
    h=hilbert(y) # transformée de hilbert
    A= np.abs(h) # module
    # TODO on fait un des 2, lequel ? regarder ce que ça donne / la théorie
    A_smooth=filterL(A,sr)
    A_smooth = scipy.ndimage.filters.gaussian_filter(A, sr/10, mode='constant')
    # on trouve les pics de l'enveloppe
    peaks, _ = find_peaks(A_smooth,prominence=prom,width=50,distance=0.6*dMin)
    return [A_smooth,peaks]

# variabilité de la hauteur du pic z (horiz) -> renseigne sur les mouvements du vélo
def varZ(z):
    # _ : variable renvoyée par find_peaks pas stockée en mémoire
    peaks, _ = find_peaks(z, prominence=0.01,width=10,distance=10)
    A=[z[i] for i in peaks] # amplitude des pics
    return np.var(A)

# détecte les pics outliers (pics de y = hauteur du vélo) : loin de la moyenne
# peaks contient la coordonnée x des pics
def VariablesPeaks(f,peaks):
    fCenter=[float(i-np.mean(f)) for i in f]
    pi=[peaks[i] for i,val in enumerate(fCenter) if abs(val)>0.1]
    pi1=[peaks[i+1] for i,val in enumerate(fCenter) if abs(val)>0.1]
    return pi+pi1

# outliers locaux (glissement sur la pédale etc)
# T contient les durées des cycles
# outlier si t(i) / moy(t(i-1),t(i+1)) > 1.3 (valeur un peu arbitraire)
def delOutliers(T):
    n=len(T);T2=list(T);  # copie de la liste 1 -> on va lui enlever les outliers
    indices=[] # indices à enlever -> outliers
    for i,t in enumerate(T):
        if 0<i<(n-1) : # pour 0 et n-1, peut pas comparer avec avant et après
            q=abs(2*t/(T[i-1]+T[i+1])-1)
            if q>0.3:
                T2.remove(t)
                indices.append(i)
    return [T2,indices] # retourne la liste et les indices supprimés
        
# interpole les portions manquantes pas trop grandes
def interp(m,lim=150):
    if len(m)>0:
        im=Im(m) # indices manquants
        ranges=getRanges(im) # intervalles à problème
        for i in ranges:
            # si intervalle masqué trop grand, une interpolation ne suffit pas
            if len(i)<lim: # si l'intervalle est pas trop grand 
                # indice le même pour les 3, mais valeurs différentes
                iok=[j for j,l in enumerate(m[0]) if l!=''] # ix=iy=iz : le temps
                mok=[[l for j,l in enumerate(m[k]) if l!=''] for k in range(3)] #x,y,z
                # on fait 3 interpolations 1D
                # moki = x puis y puis z
                fok = [interpolate.interp1d(iok,moki,fill_value="extrapolate") for moki in mok]
                # valeurs manquantes : on les met dans une liste
                [xm,ym,zm]=[l(i) for l in fok] # fOK = 3 listes 
                # on remplit m
                for ind in range(len(m[0])):
                    if ind in i: # indice dans i = indice dans xm,ym,zm
                        m[0][ind]=xm[i.index(ind)]
                        m[1][ind]=ym[i.index(ind)]
                        m[2][ind]=zm[i.index(ind)]
    return m


############ détection des marqueurs cycliques ##################

# renvoie un dictionnaire contenant les marqueurs remplissant les critères
def keepCircles(dico,dRLim=0.01, residuLim=5):
    dicoM={} # pour sélectionner le meilleur marqueur
    for key,value in dico.copy().items(): # dico=liste de tous les marqueurs
        # on enlève les '', pourrait améliorer ça, gérer masquages et détection
        [x,y,z]=FVal(value) 
        # on calcule la 'circularité'  
        [circle,dR,residu]= fitCircle(x,y,z,dRLim,residuLim) 
        if circle:
            # on stocke les cercles correspondant aux critères
            if dR<dRLim and residu<residuLim and len(x)>0:
                dicoM[key]=[len(x),dR,residu]
    return dicoM

# détecte si la condition est vélo avec les mains ou les pieds
# pour cela, on compte les marqueurs cycliques parmi les rigid bodies des mains
def detectBaseline(dico):
    i=0 # compteur des marqueurs cycliques
    for key,value in dico.items(): # tous les marqueurs + rigid bodies
        # si pas marqueur, mais rigid body des mains 
        # 4 et 5 = rigid bodies des mains, H = hands si renommé
        if ('Unlabeled' not in key and "bike" not in key and 'Marker' not in key and "pedal" not in key) and ('4' in key or '5' in key or 'H' in key):
            # rigid body
            v=FVal(value)
            [circle,dR,residu]=fitCircle(v[0],v[1],v[2],0.02,50)
            if circle: # incrémente le nombre de marqueurs circulaires
                i+=1
    # fichiers sans rigid body : on prend en compte les marqueurs rigid bodies
    if 'Rigid Body 4' not in dico.keys() and 'LH' not in dico.keys():
        for key,value in dico.items():
            if ('Unlabeled' not in key and "pedal" not in key) and ('4' in key or '5' in key or 'H' in key):
                # rigid body, mais les 3 marqueurs
                v=FVal(value)
                # on est un peu moins exigeant pour les considérer comme cercles
                [circle,dR,residu]=fitCircle(v[0],v[1],v[2],0.03,50)
                if circle:
                    i+=1
        if i>=3: # 2 mains -> 6 marqueurs cycliques théoriquement
            return 3 # mains
        return 2 # si pas assez de marqueurs cycliques -> vélo
    if i>=2: # si juste les rgid bodies, besoin des 2 
        return 3 # mains
    return 2 # pieds


def detectBike(filename,dico):
    print(filename)
    dico =OpenPkl(filename) # dico contenant tous les marqueurs, clé = nom
    bike=[]
    # on ne garde que les cercles dans dicoM, avec leurs caractéristiques
    dicoM=keepCircles(dico)
    # on ne relâche les contraintes que si aucun candidat ou candidat trop court
    # dicoM[x]=[len,dR,residu] -> max renvoie la clé du plus long marqueur
    # [0] car dicoM retourne [len,dR,residu] et on veut juste len
    if len(dicoM)==0 or dicoM[max(dicoM, key=dicoM.get)][0]<5000:
        dicoM=keepCircles(dico,0.03,100) # relâche les contraintes
        if len(dicoM)==0 or dicoM[max(dicoM, key=dicoM.get)][0]<5000:
            print("pas de marqueur circulaire : aucun candidat ")
            return []
    # si on a trouvé un marqueur, on va la compléter
    # on garde la longueur maximale, et le plus petit résidu
    maxi = dicoM[max(dicoM, key=dicoM.get)][0] # int
    # on supprime les marqueurs trop courts
    for key,value in dicoM.copy().items():  # tous les marqueurs circulaires
        if maxi>0 and float(value[0])/float(maxi)<0.95: 
            del dicoM[key] # on garde que la longueur max (ou presque)
    # key=.... k[1]->valeur (k[0]->cle) k[1][2]-> trie par résidu
    # key = fonction_pour_trier -> lambda = syntaxe pour définir une fonction
    # en plein milieu d'une ligne : lambda qui a k renvoie k[1][2]
    # attention key pour trier != key de dictionnaire
    dM=sorted(dicoM.items(), key=lambda k : k[1][2]) # trie -> plus petit résidu
    # clé du meiller marqueur (2e marqueur =dM[0], sa clé = dM[0][0] )
    cle=dM[0][0];m=[]
    bike=interp(dico[cle]) # complétion par interpolation
    if len(IF(bike))<1000:
        print("pas de marqueur circulaire : candidat trop court",filename)
        printCircleScores(dico)
    else:
        im=Im(bike) # indices manquants après interpolation
        if(len(im))>0:
            # on trouve le range qui pose probleme
            ranges=getRangesLimit(im) # ex [21,25] [29,35] ...
            dr=diff(ranges) # longueur des intervalles où le marqueur est masqué
            maxR=ranges[list(dr).index(max(dr))] # intervalle le plus long
            # on cherche un autre marqueur inclus dans cet intervalle
            for key,value in dico.items():
                ytmp=value[1] # y de ce marqueur potentiel
                nnulTab=[m for m,unlab in enumerate(ytmp) if unlab!='']
                n0=nnulTab[0] # premier indice non nul
                nf=nnulTab[-1] # dernier indice non nul
                # si ce marqueur potentiel est iclus dans l'intervalle à pb
                if key in dicoM.keys() and n0>=maxR[0] and nf<=maxR[1]:
                    [_,R,residu]=dicoM[key] # on va vérifier si ça peut matcher
                    if R<0.01 and residu <1: # complète que si partie circulaire
                        # bike = marqueur à veut compléter, value=marqueur potentiel
                        v1=FVal(bike);v2=FVal(value);
                        # position moyenne du marqueur vélo : centre du cercle
                        mV1=[np.mean(v1[0]),np.mean(v1[1]),np.mean(v1[2])]
                        # position moyenne du marqueur potentiel
                        mV2=[np.mean(v2[0]),np.mean(v2[1]),np.mean(v2[2])]
                        # distance entre les 2 points (pas listes)
                        dMean=calc_R(mV1[0],mV1[1],mV1[2],mV2[0],mV2[1],mV2[2])
                        if dMean<0.1:
                            # on affecte le marqueur au marqueur principal
                            for ind0 in nnulTab:
                                for j in range(3):
                                    bike[j][ind0]=value[j][ind0]
            if len(Im(bike))>0:
                bike=interp(bike,500) # refait interpolation sur intervalle + large
            if len(Im(bike))>0:
                rangeLim=getRangesLimit(Im(bike))# intervalles à problèmes
                print("marqueur pas complété entièrement",rangeLim)
                if len(rangeLim)==1:
                    lim=rangeLim[0];deb=lim[0];fin=lim[1];n=len(FVal(bike[1]))
                    # si marqueur trop court ou non complété au milieu
                    # cad si ni - fin des problèmes avant 5000
                    # - debut des problemes 5000 avant la fin
                    if n<10000 or not (fin<5000 or abs(len(bike[1])-deb)<5000):
                        print("marqueur pas complété au milieu : écarté",rangeLim)
                        plot2dMarker(bike[1])
                        plotID(dico)
                        bike=[]
    plotMarker(bike)
    return bike


# on ouvre les dictionnaire contenant tous les marqueurs
# pour en extraire les marqueurs cycliques
# seulement pour les fichiers où le participant pédale
def detectBikes():
    print("détection du marqueur du vélo à partir de tous les marqueurs")
    for jour in range(1,3):
        for idNum in range(1,21):
            num=str(idNum).zfill(2)
            path=getPath(idNum,jour)
            for filename in glob.glob(os.path.join(path,'*_all.pkl')):
                [c,s]=name2CS(filename) # condition story
                # on ouvre soit les conditions de pédalage soit la baseline J1
                # baseline = n02 ou n03 J1
                if c==2 or c==3 or (c==-1 and jourF(filename)==1 and ('n02' in filename or 'n03' in filename)):
                    # cle=nom du marqueur, valeur=trajectoire du marqueur
                    dico=OpenPkl(filename) # dico de toute la scène/tous les marqueurs
                    # on extrait le vélo à partir du fichier brut parsé
                    bike=detectBike(filename,dico)
                    # problème avec le marqueur : longueur nulle
                    if len(bike)==0:
                        plotID(dico) # plot3D de la scène : dico = tous les marqueurs
                    # on coupe le début et la fin : portions non cycliques
                    bike=cutBeginEnd(bike)
                    # on stocke le marqueur cyclique 
                    pklName=filename.replace('_all','_bike')
                    SavePkl(pklName,bike)
                    # plots possibles pour visualiser les données
                    #plot2dMarker(bike[1]) # plot du y : hauteur du vélo, pas z!!!!
                    #plotMarker(dico["bike"]) # plot en 3D
                    #plt.show() # pour afficher la figure

# on détecte les pics haut 
# calcule la fréquence de pédalage du vélo -> mean, var
# TODO pour synchro faut utiliser FVal0
def CirclesFreq(bike,sr,cle): # bike = marqueur en 3D
    
    c=bike;
    if len(c)>0 :  # si on a réussi à détecter quelque chose
        # hauteur du vélo = y, on extrait les parties sans '' avec FVal
        # attention pour étudier synchro faut utiliser FVal0 -> remplace '' par 0
        [x,y,z]=[FVal(i) for i in c]
        n=len(y)
        # vitesses et accélérations par coordonnées
        dx=diff(x);dy=diff(y);dz=diff(z);
        ddx=diff(dx);ddy=diff(dy);ddz=diff(dz)
        # normes des vitesses et accélérations
        v=np.sqrt(np.square(dx)+np.square(dy)+np.square(dz))
        a=np.sqrt(np.square(ddx)+np.square(ddy)+np.square(ddz)) 
        # détection de pics  : paramètres ajustés en faisant des plot
        peaks, _ = find_peaks(y, height=0,prominence=0.01,width=10,distance=10)
        peaksv, _ = find_peaks(v,prominence=0.000001,width=sr/2,distance=sr)
        peaksa, _ = find_peaks(a,prominence=0.000001,width=sr/2,distance=sr)
        # pour faire un plot cohérent en t, divise par la fréquence d'échantillonnage
        peaks=div(list(peaks),sr);peaksv=div(peaksv,sr);peaksa=div(peaksa,sr);
        
        varz=varZ(z) # varZ donne un indice sur le glissement du vélo sur le sol
        # enveloppe spectrale : TODO à utiliser éventuellement, pics de l'enveloppe ?
        [envA,peaksA]=calcEnveloppe(a,sr,100,prom=0.00001) 
        [envV,peaksV]=calcEnveloppe(v,sr,100,prom=0.00001)
        
        # plots possibles
        #plotEnveloppe(a,envA,peaksA,sr)
        #plt.show()
        #plot2dMarkerPeaks(y,list(peaks),sr)
        #plt.show()

       # TODO regarder moments significativement différents de la moyenne
       # peut être un événement local quand ralentit subitement -> pseudo-mot, hésit ?
       # ou ce sont certains outliers : si on les enlève, ça donne quoi ?
        #peaksVar=VariablesPeaks(f,peaks) # loin de la moyenne
        #print(peaksVar)
        #plot2dMarkerPeaks(y,peaksVar,sr)

        T=diff(peaks); # durée pic à pic : longueur d'un cycle
        # si veut enlever les outliers locaux
        [T2,indices]=delOutliers(T) # renvoie une lsite sans outliers + indices suppr

        # calcul des valeurs analysées
        f=[1/i for i in T] # fréquences instantnées
        # calcule pas un débit glissant sinon suite de 6 7 7 6 7 6 etc
        # + d'info dans les fréquences instantanées car événement très cyclique
        meanF=np.mean(f)
        stdF=np.sqrt(np.var(f)) # attention écart type pas variance
        #  en % de variation par rapport à la moyenne 
        # sans unité, peut donc comparer avec la variance/écart type du débit
        stdFM=stdF/meanF 
        stdFN=stdF/len(peaks)
            # peaksV, peaksA sont les pics de l'enveloppe, peut aussi décider
            # d'utiliser les pics du la vitesse et A
            return [meanF,varF,varFN,varFM,peaks,peaksV,peaksA,varz]
    return [-1,-1,-1,-1,[],[],[],-1]


# on coupe les débuts et fins où le signal n'est pas circulaire
def cutBeginEnd(bike):
    if len(bike)==3: # si la détection a bien fonctionné
        [x,y,z]=FVal0(bike) # 0 à la place des '' pour garder la synchro
        iDeb=0;iFin=len(bike[2]) # indices de début et fin
        # on coupe le début
        nbCycles=0 # après 5 cercles successifs, on est définitivement en pédalage
        # donc si y a un pb au milieu, on va pas décaler le début à après ça
        for i in range(0,int(len(y)/2),100): # on va que jusque la moitié
            [xtmp,ytmp,ztmp]=[a[i:i+300] for a in [x,y,z]] # cercle sur cette portion ?
            [circle,dR,residu]=fitCircle(xtmp,ytmp,ztmp,0.02,1)
            if not circle and nbCycles<5: # si pas un cercle et qu'on en a pas atteint 5
                iDeb=i # on décale l'indice du début
                nbCycles=0 # on retourne à la case départ, portion non circulaire
            else :  # incrémente le nombre de cycles déjà passés
                nbCycles+=1
        # on coupe la fin : même principe qu'avant 
        nbCycles=0
        for i in range(len(y)-1,int(len(y)/2),-100):
            [xtmp,ytmp,ztmp]=[a[i-300:i] for a in [x,y,z]]
            [circle,dR,residu]=fitCircle(xtmp,ytmp,ztmp,0.02,1)
            if not circle and nbCycles<5:
                iFin=i
                nbCycles=0
            else : 
                nbCycles+=1
        # si après découpage, la trajectoire est assez longue
        if iFin-iDeb>5000:
            for n in range(3):
                # on affecte 0 aux indices de début et fin pour garder la synchro
                for ind  in range(iDeb+150):
                    bike[n][ind]=0 #bike[n] = x y ou z
                for ind  in range(iFin-150,-1):
                    bike[n][ind]=0
            return bike
    print("après découpage, pas de sélection circulaire")
    return []


# on analyse les trajectoires des marqueurs cycliques
def analyseFiles(csvTab,dicoSR):
    dicoPoints={}
    for idNum in range(2,22):
        for jr in range(1,3):
            num=str(idNum).zfill(2)
            path=getPath(idNum,jr)
            print(path)
            # on a préalablement stocké le marqueur cyclique retenu dans un pkl
            for filename in glob.glob(os.path.join(path,'*_bike.pkl')):
                [c,_]=name2CS(filename)
                cond=" pieds " if int(c)==2 else " mains " if int(c)==3 else "baseline"
                cle=num+str(jr)+str(c) # clé = participant-jour-condition
                # on ouvre le marqueur cyclique
                bike=OpenPkl(filename)
                # on récupère la fréquence d'échantillonnage du fichier
                csvName=filename.replace('_bike.pkl','.csv')
                sr=float(dicoSR[csvName]) # dico de la fréq d'échantillonnage
                PM=-1;ligne=[]
                # on calcule les paramètres intéressants
                [fMean,fVar,fVarN,fVarM,points,picsV,picsA,varz]=CirclesFreq(bike,sr,cle)
                # s'il n'y a pas eu de problème de détection, on crée une ligne du csv
                if fMean!=-1:
                    ligne=createLigne(filename,csvTab,[fMean,fVar,fVarN,fVarM,varz])
                    # si on est en baseline, on doit détecter si c'est mains ou pieds
                    # en france il faudra fixer un ordre précis
                    # on complète la condition pour la baseline, 
                    # histoire à -1 pour qu'on sache que c'est une baseline
                    if c==-1 :
                        # on ouvre le dictionnaire contenant Tous les marqueurs
                        dicoName=filename.replace("bike","all")
                        dico=OpenPkl(dicoName)
                        # on regarde si la condition était baseline mains ou pieds
                        PM=detectBaseline(dico)
                        mp=" mains " if PM==3 else "pieds"
                        ligne[4]=PM
                # on enregistre les pics de position, vitesse et A pour la synchro
                dicoPoints[cle]=[points,picsV,picsA]
    # on enregistre le dico des pics de P V et A dans un fichier pkl
    SavePkl('BikePoints.pkl',dicoPoints)


# on crée le csv avec % variation baseline -> recall
def baselineRecall():
    csv=CsvReader('brutMoCap.csv')
    dicoB={}
    # on récupère les baseline 
    for l in csv[1:]: # on commence après les headers
        if l[5]=='-1':# baseline = histoire à -1, condition à la cond correspondante
            if l[0] not in dicoB.keys(): # 2 passes, car 2 conditions (pieds,mains)
                dicoB[l[0]]=[[-1,-1],[-1,-1]] # moy,var des conditions cond 3 et 4
            ind=int(l[4])-2 # conditions 2 et 3, indices 0 et 1 dans le tableau
            dicoB[l[0]][ind]=l[6:]
    csvEnd=[]
    # on crée le nouveau csv avec recall/baseline, donc on cherche les recall
    for l in csv[1:]:
        if l[5]!='-1': # histoire -1 = baseline, on cherche les recall
            ind=int(l[4])-2
            baseline=dicoB[l[0]][ind]
            if float(l[6])!=-1 and float(baseline[0])!=-1 :
                l[6]=(float(l[6])/float(baseline[0])-1)*100 # (recall/baseline-1)*100
                l[7]=(float(l[7])/float(baseline[1])-1)*100
                csvEnd.append(l[:8]) # on veut pas la fin de la liste, juste moy,var
    firstLine=["meanf rb","varf rb"]
    WriteCSV(csvEnd,firstLine,'brutMoCapBaseline.csv') # on écrit le csv





ax = plt.axes(projection='3d')
#dicoSR=getSamplingRates()
#SavePkl('sr.pkl',dicoSR)
dicoSR=OpenPkl('sr.pkl')
#parseFiles()
detectBikes()
#detectProblems()
#csvTab=[]
#analyseFiles(csvTab,dicoSR)

# on écrit le csv
#firstLine=["mean f", "var f","varfn","varfm","varz"]
#WriteCSV(csvTab,firstLine,'brutMoCap.csv')
baselineRecall()


# plot que tu peux faire pour regarder les données
#plotBike(15,1)
#plotAllMarkers(1,1) #3
#plotMarkerName('L_pedal',15,1,8)

















