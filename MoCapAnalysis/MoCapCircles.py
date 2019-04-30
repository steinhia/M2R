import os
import matplotlib as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt
import csv
from collections import defaultdict
import pickle
from scipy.signal import find_peaks
import ntpath
from numpy import *
from scipy import optimize
import os,glob
from matplotlib.mlab import find
from itertools import groupby, count
from scipy.interpolate import RegularGridInterpolator
from numpy import linspace, zeros, array
from scipy import interpolate
import operator
import time
from itertools import groupby
from operator import itemgetter
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

# parse les fichiers csv, extrait le marqueur le plus circulaire, l'interpole et éventuellement complète avec d'autres marqueurs
# enlève les débuts et fins de fichier non circulaire
# calcule la fréquence au cours du temps avec findpeak
# crée le fichier de données brutes

# TODO détecter si c'est les mains ou les pieds

# conditions de 1 à 4 pour les recall
# return [condition,order]
#def num2CS(filename):
#    name=ntpath.basename(filename)
#    cOrder=name[6:10]
#    sOrder=name[12:16]
#    num=int(name[21:23])
#    j=int(name[18])
#    tab=[[6,8,10,12],[3,5,7,9]]
#    if num in tab[j-1]:
#        index=int(tab[j-1].index(num))
#        return [cOrder[index],sOrder[index]]
#    return [-1,-1]

def calcMem():
    data=[]
    with open('../RecallTest/brut.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for i in reader:
            data.append(i)
    Mem=[0]*20
    ECJ=[0,0,0,0]
    for ligne in data[1:]:
        idNum=ligne[0]
        jour=ligne[1]
        mem=ligne[13]
        if int(jour)==2 and int(ligne[6])==3:
            Mem[int(idNum)-1]+=round(float(mem))
    return(Mem)


# pour [x,y,z] ou y
def MVal(value):
    if len(value)==3:
        m=[[float(l) for l in value[k] if l!=''] for k in range(3)]
    else:
        m=[float(l) for l in value if l!='']
    return m


def calc_R(xc, yc, zc,x,y,z):
    """ calculate the distance of each 3D points from the center (xc, yc, zc) """
    return sqrt((x - xc) ** 2 + (y - yc) ** 2 + (z - zc) ** 2)

def fitCircle(x,y,z):
    [xm,ym,zm] = [mean(x),mean(y),mean(z)]
    center = xm, ym, zm
    Ri       = calc_R(xm, ym, zm,x,y,z)
    R        = Ri.mean()
    residu   = sum((Ri - R)**2)
    return [R,residu,xm,ym,zm]

def detectCircle(dico):
    bike=dico["bike"]
    if len(bike)==3:
        return "bike"
    # problème : pas de marqueur circulaire
    else:
            for i in dico.keys():
                t=dico[i]
            n=len(t[0])
            x=t[0];y=t[1];z=t[2]
            [R,residu,xm,ym,zm]=fitCircle(x,y,z)
            resNorm=residu/(R**2)
            # on ne garde que les rigid bodies des mains
            if (('4' in i or '5' in i) or ('LH' in i or 'RH' in i)) and abs(R-0.08)<0.02 and resNorm<1000:
                l.append(i)

def detectBike(dico):
    i=0
    for key,value in dico.items():
        if 'Unlabeled' not in key and "bike" not in key:
            # rigid body
            v=MVal(value)
            [R,residu,xm,ym,zm]=fitCircle(v[0],v[1],v[2])
            if abs(R-0.08)<0.03 and residu<100:
                i+=1
    if i>=2:
        return 4
    return 3


# N = tau, décalage temporel, donc i>N, on calcule la fct de i à i+M
# M nombre de points utilisés pour calculer l'auto-corrélation
# renvoie une fct de N, cad l'autocorrélation à chaque décalage
# le maximum renvoie le moment le plus corrélé, ie la fréquence temporelle
# doit évaluer ça à différents moments pour trouver la variation de cette fréquence
def autocorrel(x,N,i,M):
    C = np.zeros(N)
    for k in range(i,i+M):
        for n in range(N):
            C[n] += x[k]*x[k-n]
    return C/M 

# y donne les meilleurs résultats
# objectif : trouver un pic d'auto corrélation -> indice du pic donne fréq du signal
# à faire à intervalles réguliers pour trouver la % de fréquence au cours du temps
def AutoCorrelationCircles(circles,dico,printData=False):
    res=[]
    m=[]
    for i in circles:
        c=dico[i]
        y=c[1][1000:]
        n=len(y)
        varFreq=[]
        for t in range(2000,n-20,1000):
            yauto=autocorrel(y,2000,t,20)
            peaks, _ = find_peaks(yauto, height=0,prominence=0.01)
            #print("peak auto",peaks[:20])
            f=diff(peaks) # approximation de T
            n_peaks=len(peaks)
            varFreq.append(np.mean(f))
            if printData:
                xauto=[j for j in range(len(yauto))]
                xsignal=[j for j in range(len(y))]
                print("signal")
                plt.plot(xsignal,y)
                plt.show()
                print("auto correl")
                plt.plot(xauto,yauto)
                plt.show()
        res.append(math.sqrt(np.var(varFreq)))
        m.append(np.mean(f))
    if len(res)>0:
        return [np.mean(res),np.mean(m)]
    return [-1,-1]

def CirclesFreq(dico):
    res=[];m=[]
    if "bike" in dico.keys():
        c=dico["bike"];
        if len(c)>0:
            y=c[1];n=len(y);varFreq=[]
            #h=0 : pics >0, prominence : pas mini locaux hauteur, width : largeur min
            peaks, _ = find_peaks(y, height=0,prominence=0.02,width=30,distance=30)
            f=diff(peaks)
            res.append(math.sqrt(np.var(f)))
            m.append(np.mean(f))
            return [np.mean(res),np.mean(m)]
    return [-1,-1]

fig = plt.figure()

def parseFile(filename):
    print(filename)
   # ax = plt.axes(projection='3d')
    with open(filename, 'r') as csvFile:
        rd= np.array(list(csv.reader(csvFile)))
    ind=['X','Y','Z']
    dico = defaultdict(list)
    dicoUnknown = defaultdict(list)
    # on crée les listes de positions des rigid bodies
    for i in rd[7:]:
        for j,val in enumerate(i):
            mType=rd[2][j];name=rd[3][j];pos=rd[6][j]
            if val!='' and 'Rigid' in mType and '_' not in name and rd[5][j]=='Position':
                if name not in dico.keys():
                    dico[name]=[[],[],[]]
                dico[name][ind.index(pos)].append(float(val))
            if 'Unlabeled' in name:
                if name not in dicoUnknown.keys():
                    dicoUnknown[name]=[[],[],[]]
                dicoUnknown[name][ind.index(pos)].append(val)    
    return [dico,dicoUnknown]




# on parse les fichiers
## parseur du fichiers csv
def parseFiles():
    for jour in range(1,3):
        for idNum in range(1,10):
            num=str(idNum).zfill(2)
            path='../DataComplete/id'+num+'/id'+num+'j'+str(jour)+'/id'+num+'j'+str(jour)+'_MocapCsv/'
            for filename in glob.glob(os.path.join(path,'*n02.csv')):
                [dico2,dico2Unknown]=parseFile(filename)
                savePkl(filename,[dico2,dico2Unknown])
            for filename in glob.glob(os.path.join(path,'*n03.csv')):
                [dico3,dico3Unknown]=parseFile(filename)
                savePkl(filename,[dico3,dico3Unknown])
            for filename in glob.glob(os.path.join(path,'*.csv')):
                [c,s]=num2CS(filename)
                if c=='4':
                    [dico4,dico4Unknown]=parseFile(filename)
                    savePkl(filename,[dico4,dico4Unknown])
                if c=='3':
                    [dico3,dico3Unknown]=parseFile(filename)
                    savePkl(filename,[dico3,dico3Unknown])

def getRangesLimit(im1):
    groups=getRanges(im1)
    for i,gp in enumerate(groups):
        groups[i]=[gp[0],gp[-1]]
    return groups

def getRanges(im1):
    ranges=[]
    for k,g in groupby(enumerate(im1),lambda x:x[0]-x[1]):
        group = (map(itemgetter(1),g))
        group = list(map(int,group))
        ranges.append(group)
    return ranges

def Im(m):
    im=[j for j,l in enumerate(m[0]) if l=='']
    return im
def M(m):
    im=[j for j,l in enumerate(m[0]) if l!='']
    return im

# interpole les portions manquantes pas trop grandes
def interp(m):
    im=Im(m)
    ranges=getRanges(im)
    for i in ranges:
        # sinon une interpolation ne suffit pas
        if len(i)<30: 
            iok=[j for j,l in enumerate(m[0]) if l!=''] # ix,iy,iz
            mok=[[l for j,l in enumerate(m[k]) if l!=''] for k in range(3)] #x,y,z
            fok = [interpolate.interp1d(iok,mi,fill_value="extrapolate") for mi in mok]
            # valeurs manquantes
            [xm,ym,zm]=[foki(i) for foki in fok]
            # on remplit m
            for ind,val in enumerate(m[0]):
                if ind in i:
                    m[0][ind]=xm[i.index(ind)]
                    m[1][ind]=ym[i.index(ind)]
                    m[2][ind]=zm[i.index(ind)]
    return m




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

def plotMarker(value,val2=[]):
    if len(value)==3:
        ax = plt.axes(projection='3d')
        [x,y,z]=[[float(l) for l in value[k] if l!=''] for k in range(3)]
        ax.plot3D(x,y,z,color='b')
    if val2!=[]:
        print("plot green",len(val2[0]))
        [x,y,z]=[[float(l) for l in val2[k] if l!=''] for k in range(3)]
        ax.plot3D(x,y,z,color='g')
    plt.show()

def plot2dMarker(y1,y2=[]):
    y1=[float(y) if y!='' else 0 for y in y1]
    y2=[float(y) if y!='' else 0 for y in y2]
    xy1=[h for h in range(len(y1))]
    plt.plot(xy1,y1)
    xy2=[h for h in range(len(y2))]
    plt.plot(xy2,y2)
    plt.show()



def completeDico(filename,dico,dicoUnknown):
    print(filename)
    pkl_file = open(filename, 'rb')
    [dico,dicoUnknown] = pickle.load(pkl_file)
    #a = pickle.load(pkl_file)
    #print(a.keys())
    dicoCopy=dicoUnknown.copy()
    dicoR={} # pour sélectionner les compléments potentiels
    dicoM={} # pour sélectionner le meilleur marqueur
    # on en garde que les cercles
    for key,value in dicoUnknown.copy().items():
        [x,y,z]=[[float(l) for l in value[k] if l!=''] for k in range(3)]
        [R,residu,xm,ym,zm]= fitCircle(x,y,z)
        dR=abs(R-0.08)
        if dR>0.03 or residu >50:
            del dicoUnknown[key]
        else:
            dicoR[key]=[len(value[0])-len(Im(value)),dR,residu]
            # on choisit le meilleur cercle
            if dR<0.01 and residu<10:
                dicoM[key]=[len(value[0])-len(Im(value)),dR,residu]
    d=sorted(dicoR.items(), key=lambda k : k[1][0]*(k[1][1]<0.02),reverse=True)
    if len(dicoM)==0:
        print("pas de marqueur circulaire",filename)
        #ax = plt.axes(projection='3d')
        #plotID(dico,dicoCopy)
    else:
        # on garde la longueur maximale, et le plus petit résidu
        maxi = dicoM[max(dicoM, key=dicoM.get)][0]
        for key,value in dicoM.copy().items():
            if value[0]!=maxi:
                del dicoM[key]
        dM=sorted(dicoM.items(), key=lambda k : k[1][2]) # plus petit résidu
        # meilleur marqueur 
        m1=interp(dicoUnknown[dM[0][0]])
        if len(M(m1))<1000:
            print("pas de marqueur circulaire",filename)
        else:
            dico["bike"]=m1
            im1=Im(m1)
            if(len(im1))>0:
                #print("interpolation pas complète",filename,len(im1))
                #plotID(dico,dicoCopy)
                # on trouve le range qui pose probleme
                ranges=getRangesLimit(im1)
                dr=diff(ranges)
                maxR=ranges[list(dr).index(max(dr))]
                dico1st={}
                for key,value in dicoUnknown.copy().items():
                    ytmp=value[1]
                    nnulTab=[m for m,unlab in enumerate(ytmp) if unlab!='']
                    n0=nnulTab[0] # premier indice non nul
                    nf=nnulTab[-1] # dernier indice non nul
                    if n0>=maxR[0] and nf<=maxR[1]:
                        [n,R,residu]=dicoR[key]
                        if R<0.01 and residu <1:
                            dico1st[key]=[n0,nf]
                            v1=MVal(m1);v2=MVal(value);
                            mV1=[np.mean(v1[0]),np.mean(v1[1]),np.mean(v1[2])]
                            mV2=[np.mean(v2[0]),np.mean(v2[1]),np.mean(v2[2])]
                            dMean=calc_R(mV1[0],mV1[1],mV1[2],mV2[0],mV2[1],mV2[2])
                            if dMean<0.1:
                                # on affecte le marqueur au marqueur principal
                                for ind0 in nnulTab:
                                    m1[0][ind0]=value[0][ind0]
                                    m1[1][ind0]=value[1][ind0]
                                    m1[2][ind0]=value[2][ind0]
                # on complete avec des 0
                for k in range(3):
                    for ind,data in enumerate(m1[k]):
                        if data=='':
                            m1[k][ind]=0
                dico["bike"]=m1
                            #print("correspondance entre 2 marqueurs",len(Im(m1)))
                            #print(dicoR[key],'\n',dico1st[key])
                            #plot2dMarker(m1[1],value[1])
    return dico

# on coupe les débuts et fins où le signal n'est pas circulaire
def cutBeginEnd(dico):
    if "bike" in dico.keys():
        bike=dico["bike"]
        if len(bike)==3:
            [x,y,z]=[MVal(bike[k]) for k in range(3)]
            iDeb=0;iFin=-1
            # on coupe le début
            for i in range(0,int(len(y)/2),100):
                [xtmp,ytmp,ztmp]=[a[i:i+300] for a in [x,y,z]]
                [R,residu,xm,ym,zm]=fitCircle(xtmp,ytmp,ztmp)
                if abs(R-0.08)>0.03 or residu>1:
                    iDeb=i
            # on coupe la fin
            for i in range(len(y)-1,int(len(y)/2),-100):
                [xtmp,ytmp,ztmp]=[a[i:i-300] for a in [x,y,z]]
                [R,residu,xm,ym,zm]=fitCircle(xtmp,ytmp,ztmp)
                if abs(R-0.08)>0.03 or residu>1:
                    iFin=i
            bike[0]=bike[0][iDeb:iFin]
            bike[1]=bike[1][iDeb:iFin]
            bike[2]=bike[2][iDeb:iFin]
    return dico


# on utilise les dictionnaires pour créer le dictionnaire final à manipuler
def completeDicos():
    for jour in range(1,3):
        for idNum in range(1,10):
            num=str(idNum).zfill(2)
            path='../DataComplete/id'+num+'/id'+num+'j'+str(jour)+'/id'+num+'j'+str(jour)+'_MocapCsv/'
            for filename in glob.glob(os.path.join(path,'*.pkl')):
                #[dico,dicoUnknown]=openPkl2(filename)
                dico={};dicoUnknown={}
                dico=completeDico(filename,dico,dicoUnknown)
                dico=cutBeginEnd(dico)
                #plotMarker(dico["bike"])
                #plot2dMarker(dico["bike"][0])
                #plot2dMarker(dico["bike"][1])
                #plot2dMarker(dico["bike"][2])
                savePkl(filename,dico)



def savePkl(filename,dico):
    name=filename[:-3]+'pkl'
    output = open(name, 'wb')
    pickle.dump(dico, output)
    print(filename)

def openPkl(filename):
    name=filename[:-3]+'pkl'
    pkl_file = open(name, 'rb')
    dico = pickle.load(pkl_file)
    return dico


def openPkl2(filename):
    name=filename[:-3]+'pkl'
    pkl_file = open(name, 'rb')
    [dico1,dico2] = pickle.load(pkl_file)
    return [dico1,dico2]


# on analyse les résultats
def analyseFiles(csvTab):
    score=[0]*20
    for jour in range(1,3):
        for idNum in range(1,10):
            print("id",idNum)
            num=str(idNum).zfill(2)
            path='../DataComplete/id'+num+'/id'+num+'j'+str(jour)+'/id'+num+'j'+str(jour)+'_MocapCsv/'
            scoreMute=0
            scoreSpeech=0
            # on detecte les passages à vide de vélo
            for filename in glob.glob(os.path.join(path,'*.pkl')):
                print(filename)
                dico=openPkl(filename)
                [fVar,fMean]=CirclesFreq(dico)
                PM=detectBike(dico)
                createLigne(filename,csvTab,[fMean,fVar,PM])
                if fVar!=-1:
                    1#print("name ",filename)
                    #print("f var ",fVar)
                    #print("f mean ",fMean)
                #print("fVar ",fVar)
                if ('03.pkl'  in filename or '02.pkl' in filename) and fVar!=-1:
                    scoreMute=fVar
                if '03.pkl' not  in filename and '02.pkl' not in filename and fVar!=-1:
                    scoreSpeech=fVar

            print("idNum ",idNum,scoreMute,scoreSpeech)
            if scoreSpeech!=0:
                score[idNum-1]=scoreSpeech/scoreMute
            else:
                score[idNum-1]=-1
            print("\n")
        return csvTab

# TODO pondère par la longueur du fichier ??
#def createLigne(filename,meanf,varf,csvTab,PM=-1):
#    name=ntpath.basename(filename)
#    cOrder=name[6:10]
#    sOrder=name[12:16]
#    num=int(name[21:23])
#    sujet=int(name[2:4])
#    jour=int(name[18])
#    [c,s]=num2CS(name)
#    if c==-1:
#        c=PM
#    csvTab.append([sujet,jour,sOrder,cOrder,s,c,meanf,varf])
#
#def createCSV(csvTab):
#    with open('brutMoCap.csv', mode='w') as f:
#        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#        writer.writerow(["id","jour","ordre histoires","ordre conditions","histoire","condition","mean f", "var f"])
#        listLines=[]
#        for i in csvTab:
#            if i not in listLines:
#                writer.writerow(i) 
#            listLines.append(i)
#parseFiles()
#completeDicos()
csvTab=[]
csvTab=analyseFiles(csvTab)
firstLine=["id","jour","ordre histoires","ordre conditions","histoire","condition","mean f", "var f"]
WriteCSV(csvTab,firstLine,'brutMoCap2.csv')
#plt.show()
#mem=calcMem()
#print(mem,var)
#for i,val in enumerate(var):
#    if val>0 and val!=-1:
#        plt.scatter(val,mem[i])
#plt.show()


tabM=[]
tabV=[]
with open('brutMoCap.csv', mode='r') as f:
    r=csv.reader(f,delimiter=',')
    for i in r:
        if i[6]!='mean f':
            tabM.append(float(i[6]))
            tabV.append(float(i[7]))
plt.scatter(tabM,tabV)
plt.show()
# TODO faire tableau brut :
# pour les 2 jours, faire la moyenne et la variance de la fréq quand y a du vélo
