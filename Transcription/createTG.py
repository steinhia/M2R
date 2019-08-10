# -*- coding: utf-8 -*-
import os
import scipy.io
import tgt
from scipy.io import wavfile
from itertools import groupby, count
path='../PythonUtils/' # pour importer fichiers extérieurs
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

def as_range(iterable): # not sure how to do this part elegantly
    l = list(iterable)
    if len(l) > 1:
        return [l[0], l[-1]]
    else:
        return [l[0],l[0]]

# crée les 2 annotations
def create2Annotations(debut,fin):
    a1=tgt.core.Annotation(debut,fin,'transcription') # instanciation d'une annot
    a2=tgt.core.Annotation(debut,fin,'commentaire') # instanciation
    return [a1,a2]

# ajoute une annotation aux 2 tiers
def add2Annotations(ann,T1,T3):
    tierTranscription.add_annotation(ann[0]) # utilisation de la fonction
    tierComm.add_annotation(ann[1]) # idem
    

for idNum in range(24,25):
    path='AudioList/id'+str(idNum).zfill(2)+'/'
    MatPath=path+'Mat/'
    for filename in glob.glob(os.path.join(path, '*.wav')):
        # nom du fichier en enlevant le path : basename
        matName=MatPath+os.path.basename(filename)[:-3]+'mat'
        txtGName=filename[:-3]+'TextGrid'
        exists = os.path.isfile(txtGName) # regarde si TextGrid existe déjà
        # création des TextGrid, mais on les écrase pas
        if not exists: 
            # on importe le signal
            fs, data = wavfile.read(filename)
            lenData=len(data)
            # on importe la détection de parties voisées
            Matfile = scipy.io.loadmat(matName)
            mat=Matfile['vadout']
            # on importe des [0 0 0 1 1 1 1 0 0]
            mat=[i[0] for i in mat]
            lenDetection=len(mat)
            # on fait un resample car le detect voice est échantillé à 10 ms
            r=float(lenData)/(float(lenDetection)*float(fs))
            # on met ça dans le format début-fin
            # obtient ex 12 13 14 18 19 20
            indicesTab=[i for i in range(len(mat)) if mat[i]==1] # récupère indices à 1
            # obtient ex 12-14 18-20
            GB=groupby(indicesTab, lambda n, c=count(): n-next(c))
            intervals=[as_range(g) for _, g in groupby(indicesTab, key=lambda n, c=count(): n-next(c))]
            # on applique le resample
            intervals=[[i*r,j*r] for i,j in intervals]
            for i in range(1,len(intervals)-1):
                # on élargit un peu l'intervalle pour que ce soit plus écoutable
                intervals[i][0]=max(intervals[i-1][1],intervals[i][0]-0.2)
                intervals[i][1]=min(intervals[i+1][0],intervals[i][1]+0.2)
        
            # on crée le textGrid
            txtGrid=tgt.core.TextGrid('essai.TextGrid') # création/instanciation
            tierTranscription=tgt.core.IntervalTier(0,lenData/fs,'transcription') #c/i
            tierComm=tgt.core.IntervalTier(0,lenData/fs,'commentaires') #c/i
        
            # on crée les annotations
            for I in intervals: # on parcourt tous les intervalles
                ann=create2Annotations(I[0],I[1]) # on crée une annot pour chaque tier
                add2Annotations(ann,tierTranscription,tierComm) # on les ajoute aux T
            txtGrid.add_tier(tierTranscription) # fonction pour ajouter un tier au TG
            txtGrid.add_tier(tierComm) # ajoute tierComm au txtGrid
            # on écrit le textgrid    
            tgt.io.write_to_file(txtGrid, txtGName)




