import os,glob
import csv
import pickle
import matplotlib.pyplot as plt
import numpy as np
from numpy import mean,sqrt,diff
from scipy.signal import find_peaks
from scipy.signal import butter, filtfilt, hilbert
import scipy
from collections import defaultdict
import ntpath
from scipy import interpolate
from itertools import groupby, count
#import operator
from operator import itemgetter
import time
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
    n=str(num).zfill(2)
    return '../DataComplete/id'+str(n)+'/id'+str(n)+'j'+str(jr)+'/id'+str(n)+'j'+str(jr)+'_MocapCsv/'


# fréquence d'échantillonnage différente selon les fichiers
# crée un dictionnaire contenant la fréquence d'échantillonnage par fichier
def getSamplingRates():
    dico={}
    for idNum in range(1,22): # numéro du participant
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

def getSamplingRate(filename):
    csvName=filename[:-4]+'.csv'
    l=CsvReader(csvName)
    return(l[0][5]) # le sampling rate est sur le csv, 1ère ligne 6ème case

# parse tous les fichiers
# pour éviter des fichiers trop lourds, on ne garde que les marqueurs suffisamment 
# longs : ceux en dessous de 100 valeurs (<1s) n'apportent pas d'info 
# et tout stocker (les valeurs vides pour tous ceux-là) prend une place monstrueuse
def parseFile(filename):
    with open(filename, 'r') as csvFile:
        rd= np.array(list(csv.reader(csvFile))) # lecture du csv
    ind=['X','Y','Z']
    dico = defaultdict(list) # dictionnaire où la vaeur par défaut est []
    # on crée les listes de positions des rigid bodies
    for i in rd[7:]: # début des données
        for j,val in enumerate(i):
            # type = RigidBody, RB Marker, Marker
            # pos = X, Y, Z
            mType=rd[2][j];name=rd[3][j];pos=rd[6][j]
            # on garde soit les RB soit les marqueurs non labellisés, mais en Position
            # _ in name-> RB_Marker, on les veut pas, moins précis
            if rd[5][j]=='Position' and (('Rigid' in mType and '_' not in name) or ('Unlabeled' in name or mType=='Marker')) :
                # si clé existe pas, doit la créer
                if name not in dico.keys():
                    dico[name]=[[],[],[]]
                # ajoute valeur dans X Y ou Z
                dico[name][ind.index(pos)].append(val)
    # on ne garde que les marqueurs "assez longs"
    for key,val in dico.copy().items():
        if len(MVal(val[0]))<100:
            del dico[key]
    print(len(dico)," marqueurs détectés")
    return dico

# pour comparer la quantité de mouvements mains-dos, on parse le dos en particulier
def parseBack(filename):
    l=[]
    with open(filename, 'r') as csvFile:
        rd= np.array(list(csv.reader(csvFile)))
        for i in rd[7:]:
            for j,val in enumerate(i):
                mType=rd[2][j];name=rd[3][j];pos=rd[6][j];typ=rd[5][j]
                if val!='' and 'Rigid' in mType and typ=='Position' and '_' not in name and ('B' in name or '6' in name): # selon les fichiers, name='Back' ou 'RigidBody6'
                    l.append(float(val))
    return l




## parseur du fichier csv
# on parse tous les fichiers, même ceux sans vélo
def parseFiles():
    for jour in range(1,3):
        for idNum in range(1,22):
            num=str(idNum).zfill(2)
            path=getPath(idNum,jour)
            for filename in glob.glob(os.path.join(path,'*.csv')):
                print(filename)
                # parse tout
                dico=parseFile(filename)
                name=filename[:-4]+'_all.pkl'
                savePkl(name,dico)
                # le dos en particulier
                back=parseBack(filename)
                name_back=filename[:-4]+'_back.pkl'
                savePkl(name_back,back)




def savePkl(filename,data):
    output = open(filename, 'wb')
    pickle.dump(data, output)


def openPkl(filename):
    pkl_file = open(filename, 'rb')
    dico = pickle.load(pkl_file)
    return dico



################ gérer les '' (données manquantes) ############################

# pour [x,y,z] ou y : enlève les ''
def MVal(value):
    if len(value)==3:
        m=[[float(l) for l in value[k] if l!=''] for k in range(3)]
    else:
        m=[float(l) for l in value if l!='']
    return m

# indices min et max où des marqueurs sont détec
def getRangesLimit(im):
    groups=getRanges(im)
    for i,gp in enumerate(groups):
        groups[i]=[gp[0],gp[-1]]
    return groups

def getRanges(im):
    ranges=[]
    for _,g in groupby(enumerate(im),lambda x:x[0]-x[1]):
        group = (map(itemgetter(1),g))
        group = list(map(int,group))
        ranges.append(group)
    return ranges

def Im(m):
    if len(m)>0:
        im=[j for j,l in enumerate(m[0]) if l=='']
        return im
    return []

def M(m):
    if len(m)>0:
        im=[j for j,l in enumerate(m[0]) if l!='']
        return im
    return []

################ calculs liés aux cercles, distances .. ###############

def calc_R(xc, yc, zc,x,y,z):
    """ calculate the distance of each 3D points from the center (xc, yc, zc) """
    return sqrt((x - xc) ** 2 + (y - yc) ** 2 + (z - zc) ** 2)

def fitCircle(x,y,z,seuilR=0.01, seuilResidu=1):
    if len(x)>0:
        [xm,ym,zm] = [mean(x),mean(y),mean(z)]
        Ri       = calc_R(xm, ym, zm,x,y,z)
        R=-1
        if len(Ri)>0:
            R        = Ri.mean()
        residu   = sum((Ri - R)**2)
        dR=abs(R-0.08)
        circle=dR<seuilR and residu<seuilResidu
        return [circle,dR,residu]
    return [False,1000,10000]

def div(l,a):
    return [float(i)/float(a) for i in l]

################ plot ###############################


def plotID(dico,dico2={}):
    ax = plt.axes(projection='3d')
    for key,value in dico.items():
        [x,y,z]=[[float(l) for l in value[k] if l!=''] for k in range(3)]
        ax.plot3D(x,y,z)
    if dico2!={}:
        for key,value in dico2.items():
            [x,y,z]=[[float(l) for l in value[k] if l!=''] for k in range(3)]
            ax.plot3D(x,y,z)
    plt.show()


def plotMarker(value,val2=[],show=True):
    if len(value)==3:
        ax = plt.axes(projection='3d')
        [x,y,z]=[[float(l) for l in value[k] if l!=''] for k in range(3)]
        ax.plot3D(x,y,z,color='b')
    if val2!=[]:
        print("plot green",len(val2[0]))
        [x,y,z]=[[float(l) for l in val2[k] if l!=''] for k in range(3)]
        ax.plot3D(x,y,z,color='g')
    if show:
        plt.show()

def plotMarkerName(name,dico):
    for cle,val in dico.items():
        if name in cle:
            plotMarker(val)

def plotMarkerNameIDJN(name,idNum,jour,n):
    path=getPath(idNum,jour)
    fileNum='n'+str(n).zfill(2)
    for filename in glob.glob(os.path.join(path,'*_all.pkl')):
        if fileNum in filename:
            print(filename)
            dico=openPkl2(filename)
            print(dico.keys())
            plotMarkerName(name,dico)

def plot2dMarker(y1,sr=-1):
    y1=[float(y) if y!='' else 0 for y in y1]
    xy1=[h for h in range(len(y1))]
    if sr!=-1:
        xy1=[i/sr for i in xy1]
    plt.plot(xy1,y1)
    #plt.show()

def plot2dMarkerPeaks(y,peaks,sr=-1):
    y=[float(i) if i!='' else None for i in y]
    if sr==-1:
        xy=[h for h in range(len(y))]
    else:
        xy=[h/sr for h in range(len(y))]
    yp=[y[int(i*sr)] for i in peaks]
    plt.plot(xy,y)
    plt.scatter(peaks,yp,color='r')
    #plt.show()


def plotIDJN(num,jr,n=-1):
    num=str(num).zfill(2)
    path=getPath(num,jr)
    print(path)
    for filename in glob.glob(os.path.join(path,'*_bike.pkl')):
        if 'n'+str(n).zfill(2) in filename or n==-1:
            print(ntpath.basename(filename))
            bike=MVal(openPkl(filename))
            if bike!=[]:
                print("len ",len(bike[1]))
                print(fitCircle(bike[0],bike[1],bike[2]))
                plotMarker(bike)
            else:
                print("pas de marqueur velo")

# plot tous les marqueurs d'un fichier en particulier
def plotAllMarkers(num,jr,n=-1):
    num=str(num).zfill(2)
    path=getPath(num,jr)
    for filename in glob.glob(os.path.join(path,'*.pkl')):
        if '_all'in filename:
            if 'n'+str(n).zfill(2) in filename or n==-1:
                print(ntpath.basename(filename))
                dico=openPkl2(filename)
                ax = plt.axes(projection='3d')
                for _,v in dico.items():
                    [x,y,z]=MVal(v)
                    [circle,dR,residu]=fitCircle(x,y,z,0.03,100)
                    if len(x)>10 and circle:
                        print("R",dR,residu,len(x))
                    ax.plot3D(x,y,z)
                plt.show()


def xT(y):
    return [i for i in range(len(y))]

def plotX(y,col='',zord=-1):
    x=xT(y)
    if zord==-1:
        if col=='':
            plt.plot(x,y)
        else:
            plt.plot(x,y,color=col)
    else:
        if col=='':
            plt.plot(x,y,zord)
        else:
            plt.plot(x,y,color=col,zorder=zord)

def printEnveloppe(y,env,peaks,sr):
    yp=[env[int(i)] for i in peaks]
    xenv=[h/sr for h in range(len(env))]
    xy=[h/sr for h in range(len(y))]
    xpeaks=[i/sr for i in peaks]
    plt.plot(xy,y)
    plt.plot(xenv,env,'r')
    plt.scatter(xpeaks,yp,color='y',s=1,zorder=3)
    #plt.show()


def plotFFT(data):
    ps = np.abs(np.fft.fft(data))**2
    freqs = np.fft.fftfreq(len(data), 1/30)
    idx = np.argsort(freqs)
    plt.plot(freqs[idx], ps[idx])
    #plt.show()


def printScores(dico):
    print("scores : \n")
    for key,value in dico.items():
        [x,y,z]=MVal(value)
        [circle,dR,residu]=fitCircle(x,y,z)
        print("circle ?",circle,"key ",key,"dR ",dR," residu ",residu," len ",len(MVal(x)))
       

############ détection des marqueurs cycliques ##################



# détecte si la condition est vélo avec les mains ou les pieds
# pour cela, on compte les marqueurs cycliques parmi les rigid bodies des mains
def detectBike(dico):
    i=0
    for key,value in dico.items():
        # si pas marqueur, mais rigid body des mains 
        if ('Unlabeled' not in key and "bike" not in key and 'Marker' not in key and "pedal" not in key) and ('4' in key or '5' in key or 'H' in key):
            # rigid body
            v=MVal(value)
            [circle,dR,residu]=fitCircle(v[0],v[1],v[2],0.02,50)
            if circle: # incrémente le nombre de marqueurs circulaires
                i+=1
    # fichiers sans rigid body
    if 'Rigid Body 4' not in dico.keys() and 'LH' not in dico.keys():
        for key,value in dico.items():
            if ('Unlabeled' not in key and "pedal" not in key) and ('4' in key or '5' in key or 'H' in key):
                # rigid body, mais les 3 marqueurs
                v=MVal(value)
                # on est un peu moins exigeant pour les considérer comme cercles
                [circle,dR,residu]=fitCircle(v[0],v[1],v[2],0.03,50)
                if circle:
                    i+=1
        if i>=3: # 2 mains -> 6 marqueurs cycliques théoriquement
            return 3
        return 2 # si pas assez de marqueurs cycliques -> vélo
    if i>=2: # si juste les rgid bodies, besoin des 2 
        return 3
    return 2



# filtre passe bas
def filterL(data,sr):
    b, a = scipy.signal.butter(1, 1/3) # ordre du filtre et wc 1/10 = très coupé
    return scipy.signal.filtfilt(b,a, data)

# filtre passe haut
def filterH(data,sr):
    b, a = scipy.signal.butter(6, 1/3,btype='high') # ordre du filtre et wc
    return scipy.signal.filtfilt(b,a, data)

# enveloppe spectrale du signal
def calcEnveloppe(y,sr,dMin,prom=0.000002):
    h=hilbert(y)
    A= np.abs(h)
    # on fait un des 2, les 2 ? regarder ce que ça donne / la théorie
    A_smooth=filterL(A,sr)
    A_smooth = scipy.ndimage.filters.gaussian_filter(A, sr/10, mode='constant')
    # on trouve les pics de l'enveloppe
    peaks, _ = find_peaks(A_smooth,prominence=prom,width=50,distance=0.6*dMin)
    return [A_smooth,peaks]

def VariablesPeaks(f,peaks):
    fCenter=[float(i-np.mean(f)) for i in f]
    peaks2=[]
    for i,val in enumerate(fCenter):
        if abs(val)>0.1:
            print(val)
            peaks2.append(peaks[i])
            peaks2.append(peaks[i+1])
    return peaks2

# variabilité de la hauteur du pic -> renseigne sur les mouvements du vélo
def varZ(z):
    peaks, _ = find_peaks(z, prominence=0.01,width=10,distance=10)
    res=[]
    for i in peaks:
        res.append(z[i])
    return np.var(res)

# outliers locaux (glissement sur la pédale etc)
# T contient les durées des cycles
# outlier si t(i) / moy(t(i-1),t(i+1)) > 1.3 (valeur un peu arbitraire)
def delOutliers(T):
    n=len(T);T2=list(T);  # copie de la liste 1
    indices=[] # indices à enlever -> outliers
    for i,t in enumerate(T):
        if 0<i<(n-1) : # pour 0 et n-1, pas d'avant ou après
            q=abs(2*t/(T[i-1]+T[i+1])-1)
            if q>0.3:
                T2.remove(t)
                indices.append(i)
    return [T2,indices] # retourne la liste et les indices supprimés
        



# on détecte les pics haut 
# calcule la fréquence de pédalage du vélo
def CirclesFreq(bike,sr,cle):
    
    res=[];m=[];c=bike;
    if len(c)>0 :  # si on a réussi à détecter quelque chose
        # hauteur du vélo = y, on extrait les ârties sans '' avec MVal
        # TODO on enlève pas les masquages de début et fin avec ça ??
        x=MVal(c[0]);y=MVal(c[1]);z=MVal(c[2]);n=len(y);varFreq=[]
        # vitesses et accélérations par coordonnées
        dx=diff(x);dy=diff(y);dz=diff(z);
        ddx=diff(dx);ddy=diff(dy);ddz=diff(dz)
        # normes des vitesses et accélérations
        v=np.sqrt(np.square(dx)+np.square(dy)+np.square(dz))
        a=np.sqrt(np.square(ddx)+np.square(ddy)+np.square(ddz)) 
        # détection de pics  : paramètres ajustés en faisant des plot
        peaks, _ = find_peaks(y, height=0,prominence=0.01,width=10,distance=10)
        peaksv, _ = find_peaks(v,prominence=0.000001,width=sr/2,distance=sr)
        # pour faire un plot cohérent en t, divise par la fréquence d'échantillonnage
        peaks=div(list(peaks),sr);peaksv=div(peaksv,sr);peaksA=div(peaksA,sr);peaksvm=div(peaksvm,sr)
        
        #deb=calcDebit(y,peaks,sr)
        varz=varZ(z) # varZ donne un indice sur le glissement du vélo sur le sol
        # enveloppe spectrale : TODO à utiliser, pics de l'enveloppe ?
        [envA,peaksA]=calcEnveloppe(a,sr,100,prom=0.00001) 
        [envV,peaksV]=calcEnveloppe(v,sr,100,prom=0.00001)
        #printEnveloppe(a,envA,peaksA,sr)
        #plt.show()
        #plot2dMarkerPeaks(y,list(peaks),sr)
        #plt.show()
        #plot2dMarkerPeaks(a,peaksA)
        #plt.show()
        
        #plotX(v,'y',1)
        #scatterY=[hA_env[i] for i in peaksa]
        #plotX(a,'y',1)
        #plotX(hA_env,'r',2)
        #print(len(peaksa))
        #plt.scatter(peaksa,scatterY,s=20,zorder=3)
        #plt.show()
        #print("varf",varF)

       # TODO regarder moments significativement différents de la moyenne
       # peut être un événement local quand ralentit subitement
       # certains outliers : si on les enlève, ça donne quoi ?
        if varF>0.07:
            print("varf",varF)

            #peaksVar=VariablesPeaks(f,peaks)
            #print(peaksVar)
            #plot2dMarkerPeaks(y,peaksVar,sr)
            #print("verticale")
            #plot2dMarker(y,sr)
            #plt.show()

        T=diff(peaks);dMin=min(T)
        # si veut enlever les outliers locaux
        [T2,indices]=delOutliers(T)

        # calcul des valeurs analysées
        f=[1/i for i in T]
        # calcule pas un débit glissant sinon suite de 6 7 7 6 7 6 etc
        # + d'info dans les fréquences instantanées car événement très cyclique
        meanF=np.mean(f)
        varF=np.sqrt(np.var(f))
        #  en % de variation par rapport à la moyenne 
        # sans unité, peut donc comparer avec la variance/écart type du débit
        varFM=varF/meanF 
        varFN=varF/len(peaks)
        if len(f)>0 :
            res.append(sqrt(np.var(f)))
            m.append(mean(f))
            return [meanF,varF,varFN,varFM,peaks,peaksV,peaksA,varz]
    return [-1,-1,-1,-1,,[],[],[],-1]

#fig = plt.figure()






################## calculs sur les données ####################

# interpole les portions manquantes pas trop grandes
def interp(m,lim=150):
    if len(m)>0:
        im=Im(m)
        ranges=getRanges(im)
        for i in ranges:
            # sinon une interpolation ne suffit pas
            if len(i)<lim: 
                iok=[j for j,l in enumerate(m[0]) if l!=''] # ix,iy,iz
                mok=[[l for j,l in enumerate(m[k]) if l!=''] for k in range(3)] #x,y,z
                fok = [interpolate.interp1d(iok,mi,fill_value="extrapolate") for mi in mok]
                # valeurs manquantes
                [xm,ym,zm]=[foki(i) for foki in fok]
                # on remplit m
                for ind in range(len(m[0])):
                    if ind in i:
                        m[0][ind]=xm[i.index(ind)]
                        m[1][ind]=ym[i.index(ind)]
                        m[2][ind]=zm[i.index(ind)]
    return m


def keepCircles(dico,dRLim=0.01, residuLim=5):
    dicoR={} # pour sélectionner les compléments potentiels : moins strict
    dicoM={} # pour sélectionner le meilleur marqueur
    for key,value in dico.copy().items():
        [x,y,z]=MVal(value)
        [circle,dR,residu]= fitCircle(x,y,z,0.03,100)
        #print("key",key,circle)
        if not circle:
            del dico[key]
        else:
            dicoR[key]=[len(x),dR,residu]
            # on choisit le meilleur cercle
            if dR<dRLim and residu<residuLim and len(x)>0:
                dicoM[key]=[len(x),dR,residu]
    return [dicoM,dicoR]

def completeDico(filename,dico):
    dico =openPkl2(filename)
    bike=[]
    # on ne garde que les cercles dans dico, avec leurs caractéristiques dans dicoRM
    [dicoM,dicoR]=keepCircles(dico)
    # on ne relâche les contraintes que si aucun candidat ou candidat trop court
    if len(dicoM)==0 or dicoM[max(dicoM, key=dicoM.get)][0]<5000:
        [dicoM,dicoR]=keepCircles(dico,0.03,100)
        if len(dicoM)==0 or dicoM[max(dicoM, key=dicoM.get)][0]<5000:
            print("pas de marqueur circulaire : aucun candidat ")
            #printScores(dico)
            return []
    # si on a trouvé un marqueur, on le complète
    # on garde la longueur maximale, et le plus petit résidu
    maxi = dicoM[max(dicoM, key=dicoM.get)][0]
    for key,value in dicoM.copy().items():
        if maxi>0 and float(value[0])/float(maxi)<0.95: 
            del dicoM[key] # on garde que la longueur max (ou presque)
    dM=sorted(dicoM.items(), key=lambda k : k[1][2]) # plus petit résidu
    # meilleur marqueur 
    #printScores(dico)
    #print(dico.keys())
    #printScores(dico)
    #plotID(dico)
    key=dM[0][0];m=[]
    m=interp(dico[dM[0][0]]) # complétion par interpolation
    if len(M(m))<1000:
        print("pas de marqueur circulaire : candidat trop court",filename)
        printScores(dico)
    else:
        bike=m
        im=Im(m) # indices manquants
        if(len(im))>0:
            # on trouve le range qui pose probleme
            ranges=getRangesLimit(im) # ex [21,25] [29,35] ...
            dr=diff(ranges) # longueur des intervalles vides
            maxR=ranges[list(dr).index(max(dr))]
            dico1st={}
            for key,value in dico.items():
                ytmp=value[1]
                nnulTab=[m for m,unlab in enumerate(ytmp) if unlab!='']
                n0=nnulTab[0] # premier indice non nul
                nf=nnulTab[-1] # dernier indice non nul
                if n0>=maxR[0] and nf<=maxR[1]:
                    [n,R,residu]=dicoR[key]
                    if R<0.01 and residu <1:
                        dico1st[key]=[n0,nf]
                        v1=MVal(m);v2=MVal(value);
                        mV1=[np.mean(v1[0]),np.mean(v1[1]),np.mean(v1[2])]
                        mV2=[np.mean(v2[0]),np.mean(v2[1]),np.mean(v2[2])]
                        dMean=calc_R(mV1[0],mV1[1],mV1[2],mV2[0],mV2[1],mV2[2])
                        if dMean<0.1:
                            # on affecte le marqueur au marqueur principal
                            for ind0 in nnulTab:
                                m[0][ind0]=value[0][ind0]
                                m[1][ind0]=value[1][ind0]
                                m[2][ind0]=value[2][ind0]
            # on complete avec des 0 #TODO a voir
            if len(Im(m))>0:
                m=interp(m,500)
            if len(Im(m))>0:
                rangeLim=getRangesLimit(Im(m))
                print("marqueur pas complété",rangeLim)
                if len(rangeLim)==1:
                    # si pas trop long, au début ou à la fin
                    lim=rangeLim[0];deb=lim[0];fin=lim[1];n=len(MVal(m[1]))
                    if deb==0 and fin<5000 and n>10000:
                        for ind,val in enumerate(m[1]):
                            if val=='':
                                [m[0][ind],m[1][ind],m[2][ind]]=[0,0,0]
                    elif abs(len(m[1])-fin)<100 and n>10000:
                        for ind,val in enumerate(m[1]):
                            if val=='':
                                [m[0][ind],m[1][ind],m[2][ind]]=[0,0,0]
                    else:
                        print("marqueur pas complété au milieu",rangeLim)
                        plot2dMarker(m[1])
                        plotID(dico)
                        printScores(dico)
                        m=[]
            bike=m
    return bike

# on utilise les 2 dictionnaires pour créer le dictionnaire final à manipuler 
# on rajoute le marqueur circulaire
def completeDicos():
    for jour in range(1,3):
        for idNum in range(2,22):
            num=str(idNum).zfill(2)
            path=getPath(idNum,jour)
            print(path)
            for filename in glob.glob(os.path.join(path,'*_all.pkl')):
                print(filename)
                [c,s]=num2CS(filename)
                if c==2 or c==3 or (c==-1 and jourF(filename)==1 and ('n02' in filename or 'n03' in filename)):
                    pklName=filename.replace('_all','_bike')
                    print(pklName)
                    dico=openPkl2(filename)
                    bike=completeDico(filename,dico)
                    #plot2dMarker(bike[1])
                    if len(bike)==0:
                        plotID(dico)
                    bike=cutBeginEnd(bike)
                    plot2dMarker(bike[1])
                    plt.show()
                    #plotID(dico,dicoUnknown)
                    #plotMarker(dico["bike"])
                    #plot2dMarker(dico["bike"][0])
                    #plot2dMarker(dico["bike"][1])
                    #plot2dMarker(dico["bike"][2])
                    savePkl(pklName,bike)

# on coupe les débuts et fins où le signal n'est pas circulaire
def cutBeginEnd(bike):
    if len(bike)==3:
        [x,y,z]=[MVal(bike[k]) for k in range(3)]
        #plot2dMarker(bike[2])
        iDeb=0;iFin=len(bike[2])
        # on coupe le début
        ok=0 # après 5 cercles à la suite, on ne peut plus décider de couper
        for i in range(0,int(len(y)/2),100):
            [xtmp,ytmp,ztmp]=[a[i:i+300] for a in [x,y,z]]
            [circle,dR,residu]=fitCircle(xtmp,ytmp,ztmp,0.02,1)
            if not circle and ok<5:
                iDeb=i
                ok=0
            else : 
                ok+=1
        # on coupe la fin
        ok=0
        for i in range(len(y)-1,int(len(y)/2),-100):
            [xtmp,ytmp,ztmp]=[a[i-300:i] for a in [x,y,z]]
            [circle,dR,residu]=fitCircle(xtmp,ytmp,ztmp,0.02,1)
            if not circle:
                iFin=i
                ok=0
            else : 
                ok+=1
        if iFin-iDeb>5000:
            for n in range(3):
                for ind  in range(iDeb+150):
                    bike[n][ind]=0
                for ind  in range(iFin-150,-1):
                    bike[n][ind]=0
            #bike[0]=bike[0][iDeb+150:iFin-150] # pour être au milieu de l'intervalle 
            #bike[1]=bike[1][iDeb+150:iFin-150]
            #bike[2]=bike[2][iDeb+150:iFin-150]
            #plot2dMarker(bike[2])
            return bike
    print("après découpage, pas de sélection circulaire")
    return []

# TODO regarder plot des outliers
def baselineRecall():
    csv=CsvReader('brutMoCap.csv')
    dicoB={}
    # on récupère les baseline 
    for l in csv[1:]:
        # baseline
        if l[5]=='-1':
            if l[0] not in dicoB.keys():
                dicoB[l[0]]=[[-1,-1],[-1,-1]] # moy,var cond 3 et 4
            ind=int(l[4])-2
            dicoB[l[0]][ind]=l[6:]
    csvEnd=[]
    # on crée le nouveau csv avec recall/baseline
    for l in csv[1:]:
        if l[5]!='-1':
            ind=int(l[4])-2
            baseline=dicoB[l[0]][ind]
            if float(l[6])!=-1 and float(baseline[0])!=-1 :
                l[6]=(float(l[6])/float(baseline[0])-1)*100
                l[7]=(float(l[7])/float(baseline[1])-1)*100
                print(l[6],l[7])
                csvEnd.append(l)
    firstLine=["meanf rb","varf rb","a","a","a","a","a","a"]
    WriteCSV(csvEnd,firstLine,'brutMoCapBaseline.csv')


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
                [c,_]=num2CS(filename)
                cond=" pieds " if int(c)==2 else " mains " if int(c)==3 else "baseline"
                cle=num+str(jr)+str(c) # clé = participant-jour-condition
                # on ouvre le marqueur cyclique
                bike=openPkl(filename)
                # on récupère la fréquence d'échantillonnage du fichier
                csvName=filename[:-9]+'.csv'
                sr=float(dicoSR[csvName])
                PM=-1;ligne=[]
                # si on est en baseline, on doit détecter si c'est mains ou pieds
                # en france il faudra fixer un ordre précis
                if c==-1:
                    # on ouvre le dictionnaire contenant Tous les marqueurs
                    dicoName=filename.replace("bike","all")
                    dico=openPkl(dicoName)
                    # on regarde si la condition était baseline mains ou pieds
                    PM=detectBike(dico)
                    mp=" mains " if PM==3 else "pieds"
                # on calcule les paramètres intéressants
                [fMean,fVar,fVarN,fVarM,points,picsV,picsA,varz]=CirclesFreq(bike,sr,cle)
                # s'il n'y a pas eu de problème de détection, on crée une ligne du csv
                if fMean!=-1:
                    ligne=createLigne(filename,csvTab,[fMean,fVar,fVarN,fVarM,varz])
                    # on complète la condition pour la baseline, histoire à -1
                    if c==-1 :
                        ligne[4]=PM
                # on enregistre les pics de position, vitesse et A pour la synchro
                dicoPoints[cle]=[points,picsV,picsA]
    # on enregistre le dico des pics de P V et A dans un fichier pkl
    SavePkl('BikePoints.pkl',dicoPoints)


# on regarde où la détection n'a pas marché
def detectProblems():
    for idNum in range(1,21):
        for jr in range(1,3): # on ne regarde pas le jour 3
            num=str(idNum).zfill(2)
            path=getPath(idNum,jr)
            for filename in glob.glob(os.path.join(path,'*_bike.pkl')):
                # environnement pour le plot3D
                ax = plt.axes(projection='3d')
                # on ouvre le fichier contenant le marqueur cyclique
                bike=openPkl(filename)
                # s'il est inexistant ou trop court -> pb de détection
                if len(bike)==0 or len(bike[0])<2000:
                    print("\n pas de marqueur circulaire ", filename)
                    # on ouvre le dico avec tous les marqueurs pour regarder la scène
                    dicoName=filename.replace('bike','all')
                    dico=openPkl(dicoName)
                    name=ntpath.basename(filename)
                    tache=int(name[21:23]) # nxx
                    plotAllMarkers(idNum,jr,tache) # plot de tous les marqueurs
                    for _,v in dico.items():
                        if len(v)==3:
                            [x,y,z]=MVal(v)
                            ax.plot3D(x,y,z) # plot de tous les marqueurs
                    plt.show()




def delPklFiles(string):
    for idNum in range(1,22):
        for jr in range(1,3):
            num=str(idNum).zfill(2)
            path=getPath(idNum,jr)
            for filename in glob.glob(os.path.join(path,'*.pkl')):
                if string in filename:
                    os.remove(filename)

#dicoSR=getSamplingRates()
#SavePkl('sr.pkl',dicoSR)
dicoSR=OpenPkl('sr.pkl')
#delPklFiles('_db')
#plotIDJN(15,1)
#plotAllMarkers(1,1) #3
parseFiles()
#completeDicos()
#detectProblems()
#csvTab=[]
#analyseFiles(csvTab,dicoSR)
#firstLine=["mean f", "var f","varfn","varfm","varz"]
#WriteCSV(csvTab,firstLine,'brutMoCap.csv')
#baselineRecall()

#plotMarkerNameIDJN('L_pedal',15,1,8)



















