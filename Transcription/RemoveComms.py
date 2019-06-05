# -*- coding: utf-8 -*
import tgt
import os, glob
import csv
from scipy.io import wavfile
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

# TODO ajouter et pas recréer
###### enlève les commentaires et les 'transcription' en trop pour traiter les fichiers

for idNum in range(1,22):
    path='Resultats/id'+str(idNum).zfill(2)+'/'
    pathAudio='AudioList/id'+str(idNum).zfill(2)+'/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        audioName=pathAudio+ntpath.basename(filename)[:-8]+'wav'
        fs, data = wavfile.read(audioName)
        t_end=len(data)/fs # bonne longueur de fichier
        print(filename)
        f=readTG(filename)
        annotC=[];annotS=[]
        annotC=f.get_tier_by_name('commentaires').annotations
        annotT=f.get_tier_by_name('transcription').annotations
        lenFile=int(annotT[-1].end_time*100)
        tierComm=tgt.core.IntervalTier(0,t_end,'commentaires')
        tierTrans=tgt.core.IntervalTier(0,t_end,'transcription')
        for ann in annotC:
            t=ann.text.replace('commentaire','')
            debut=ann.start_time;fin=ann.end_time
            a=tgt.core.Annotation(debut,fin,t)
            tierComm.add_annotation(a)
        for ann in annotT:
            t=ann.text.replace('transcription','').replace('.','').replace(',',' ').replace('Hm','hm').replace('Und','und').replace('Ja','ja').replace('Genau','genau')
            debut=ann.start_time;fin=ann.end_time
            a=tgt.core.Annotation(debut,fin,t)
            tierTrans.add_annotation(a)
        #print(tierComm)
        # on crée le textGrid
        txtGrid=tgt.core.TextGrid('a')
        txtGrid.add_tier(tierTrans)
        txtGrid.add_tier(tierComm)
        tierHes=-1
        if 'Hes' not in f.get_tier_names():
            tierHes=tgt.core.IntervalTier(0,t_end,'Hes')
        else:
            annotH=f.get_tier_by_name('Hes').annotations
            tierHes=tgt.core.IntervalTier(0,t_end,'Hes')
            for ann in annotH:
                tierHes.add_annotation(ann)
        txtGrid.add_tier(tierHes)
        tgt.io.write_to_file(txtGrid,filename)
