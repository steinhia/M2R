import os,glob
import csv
import pickle
#import matplotlib as plt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from numpy import mean,sqrt,diff
from scipy.signal import find_peaks
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

def getPath(num,jr):
    n=str(num).zfill(2)
    return '../DataComplete/id'+str(n)+'/id'+str(n)+'j'+str(jr)+'/id'+str(n)+'j'+str(jr)+'_MocapCsv/'



# parse les fichiers csv, extrait le marqueur le plus circulaire, l'interpole et éventuellement complète avec d'autres marqueurs
# enlève les débuts et fins de fichier non circulaire
# calcule la fréquence au cours du temps avec findpeak
# crée le fichier de données brutes


################ gérer les '' (données manquantes) ############################

# pour [x,y,z] ou y
def MVal(value):
    if len(value)==3:
        m=[[float(l) for l in value[k] if l!=''] for k in range(3)]
    else:
        m=[float(l) for l in value if l!='']
    return m

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

# détecte si la condition est vélo avec les mains ou les pieds
def detectBike(dico):
    i=0
    for key,value in dico.items():
        if 'Unlabeled' not in key and "bike" not in key:
            # rigid body
            v=MVal(value)
            [circle,dR,residu]=fitCircle(v[0],v[1],v[2],0.03,100)
            if circle:
                i+=1
    if i>=2:
        return 3
    return 2


# calcule la fréquence de pédalage du vélo
def CirclesFreq(bike):
    res=[];m=[];c=bike;
    if len(c)>0:
        y=MVal(c[1]);n=len(y);varFreq=[]
        #h=0 : pics >0, prominence : pas mini locaux hauteur, width : largeur min
        peaks, _ = find_peaks(y, height=0,prominence=0.02,width=30,distance=30)
        f=diff(peaks)
        if len(f)>0:
            res.append(sqrt(np.var(f)))
            m.append(mean(f))
            return [mean(res),mean(m)]
    return [-1,-1]

fig = plt.figure()





#################### plot ####################

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
    for filename in glob.glob(os.path.join(path,'*_2.pkl')):
        if fileNum in filename:
            print(filename)
            dico=openPkl2(filename)
            print(dico.keys())
            plotMarkerName(name,dico)

def plot2dMarker(y1,y2=[]):
    y1=[float(y) if y!='' else 0 for y in y1]
    y2=[float(y) if y!='' else 0 for y in y2]
    xy1=[h for h in range(len(y1))]
    plt.plot(xy1,y1)
    xy2=[h for h in range(len(y2))]
    plt.plot(xy2,y2)
    plt.show()


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


def plotAllMarkers(num,jr,n=-1):
    num=str(num).zfill(2)
    path=getPath(num,jr)
    for filename in glob.glob(os.path.join(path,'*.pkl')):
        if '_2'in filename:
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


def detectProblems():
    for idNum in range(1,21):
        for jr in range(1,3):
            num=str(idNum).zfill(2)
            path=getPath(idNum,jr)
            for filename in glob.glob(os.path.join(path,'*_bike.pkl')):
                ax = plt.axes(projection='3d')
                bike=openPkl(filename)
                if len(bike)==0 or len(bike[0])<2000:
                    print("\n pas de marqueur circulaire ", filename)
                    dicoName=filename.replace('bike','2')
                    dico=openPkl2(dicoName)
                    name=ntpath.basename(filename)
                    tache=int(name[21:23])
                    plotAllMarkers(idNum,jr,tache) 
                    for _,v in dico.items():
                        if len(v)==3:
                            [x,y,z]=MVal(v)
                            ax.plot3D(x,y,z)
                    plt.show()


def printScores(dico):
    print("scores : \n")
    for key,value in dico.items():
        [x,y,z]=MVal(value)
        [circle,dR,residu]=fitCircle(x,y,z)
        print("circle ?",circle,"key ",key,"dR ",dR," residu ",residu," len ",len(MVal(x)))
       



################### parse ################

def parseFile(filename):
    print(filename)
   # ax = plt.axes(projection='3d')
    with open(filename, 'r') as csvFile:
        rd= np.array(list(csv.reader(csvFile)))
    ind=['X','Y','Z']
    dico = defaultdict(list)
    # on crée les listes de positions des rigid bodies
    for i in rd[7:]:
        for j,val in enumerate(i):
            mType=rd[2][j];name=rd[3][j];pos=rd[6][j]
            if val!='' and 'Rigid' in mType and '_' not in name and rd[5][j]=='Position':
                if name not in dico.keys():
                    dico[name]=[[],[],[]]
                dico[name][ind.index(pos)].append(float(val))
            if 'Unlabeled' in name or mType=='Marker':
                if name not in dico:
                    dico[name]=[[],[],[]]
                dico[name][ind.index(pos)].append(val)   
    # on ne garde que les marqueurs "assez longs"
    print("len1",len(dico))
    for key,val in dico.copy().items():
        if len(MVal(val[0]))<100:
            del dico[key]
    print("len2",len(dico))
    return dico




# on parse les fichiers
## parseur du fichiers csv
def parseFiles():
    for jour in range(1,3):
        for idNum in range(1,21):
            num=str(idNum).zfill(2)
            path=getPath(idNum,jour)

            for filename in glob.glob(os.path.join(path,'*.csv')):
                dico=parseFile(filename)
                savePkl2(filename,dico)




def savePkl(filename,bike):
    name=filename[:-4]+'_bike.pkl'
    output = open(name, 'wb')
    pickle.dump(bike, output)

# dictionnaire entier
def savePkl2(filename,dico):
    name=filename[:-4]+'_2.pkl'
    output = open(name, 'wb')
    pickle.dump(dico, output)


# seulement le vélo
def openPkl(filename):
    name=filename[:-4]+'.pkl'
    pkl_file = open(name, 'rb')
    dico = pickle.load(pkl_file)
    return dico

# dictionnaire entier
def openPkl2(filename):
    name=filename
    pkl_file = open(name, 'rb')
    dico = pickle.load(pkl_file)
    return dico




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
        for idNum in range(1,21):
            num=str(idNum).zfill(2)
            path=getPath(idNum,jour)
            print(path)
            for filename in glob.glob(os.path.join(path,'*_2.pkl')):
                [c,s]=num2CS(filename)
                if c==2 or c==3 or (c==-1 and jourF(filename)==1 and ('n02' in filename or 'n03' in filename)):
                    pklName=filename.replace('_2','')
                    print(pklName)
                    dico=openPkl2(filename)
                    bike=completeDico(filename,dico)
                    if len(bike)==0:
                        plotID(dico)
                    bike=cutBeginEnd(bike)
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
            bike[0]=bike[0][iDeb+150:iFin-150] # pour être au milieu de l'intervalle 
            bike[1]=bike[1][iDeb+150:iFin-150]
            bike[2]=bike[2][iDeb+150:iFin-150]
            #plot2dMarker(bike[2])
            return bike
    print("après découpage, pas de sélection circulaire")
    return []


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
            #l[6]=(float(l[6])/float(dicoB[l[0]][ind][0])-1)*100
            #l[6]=(float(l[6])/float(dicoB[l[0]][ind][0])-1)*100
            baseline=dicoB[l[0]][ind]
            if float(l[6])!=-1 and float(baseline[0])!=-1 :
                l[6]=(float(l[6])/float(baseline[0])-1)*100
                l[7]=(float(l[7])/float(baseline[1])-1)*100
                csvEnd.append(l)
    firstLine=["meanf rb","varf rb"]
    WriteCSV(csvEnd,firstLine,'brutMoCapBaseline.csv')


# on analyse les résultats
def analyseFiles(csvTab):
    for idNum in range(1,21):
        for jr in range(1,3):
            print("id",idNum," jour",jr)
            num=str(idNum).zfill(2)
            path=getPath(idNum,jr)
            # on detecte les passages à vide de vélo
            for filename in glob.glob(os.path.join(path,'*_bike.pkl')):
                print(ntpath.basename(filename))
                bike=openPkl(filename)
                [fVar,fMean]=CirclesFreq(bike)
                ligne=createLigne(filename,csvTab,[fMean,fVar])
                # pour la baseline, affectation de la condition, histoire à -1
                [c,s]=num2CS(filename)
                if c==-1:
                    dicoName=filename.replace("bike","2")
                    dico=openPkl2(dicoName)
                    PM=detectBike(dico)
                    ligne[4]=PM
                #plotID(dico)

def delPklFiles(string):
    for idNum in range(1,21):
        for jr in range(1,3):
            num=str(idNum).zfill(2)
            path=getPath(idNum,jr)
            for filename in glob.glob(os.path.join(path,'*.pkl')):
                if string in filename:
                    os.remove(filename)

#delPklFiles('_db')
#plotIDJN(15,1)
#plotAllMarkers(16,1) #3
#parseFiles()
#completeDicos()
#detectProblems()
csvTab=[]
analyseFiles(csvTab)
firstLine=["mean f", "var f"]
WriteCSV(csvTab,firstLine,'brutMoCap.csv')
baselineRecall()

#plotMarkerNameIDJN('L_pedal',15,1,8)



















