# -*- coding: utf-8 -*
import tgt
import os, glob
import csv
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

###### enlève les commentaires et les 'transcription' en trop pour traiter les fichiers

for idNum in range(13,20):
    path='Resultats/id'+str(idNum)+'/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        print(filename)
        f=readTG(filename)
        #f=tgt.io.read_textgrid(filename,encoding='utf-16-be')
        annotC=[]
        if 'commentaires' in f.get_tier_names():
            annotC=f.get_tier_by_name('commentaires').annotations
        else:
            annotC=f.get_tier_by_name('commentaire').annotations
        annotT=f.get_tier_by_name('transcription').annotations
        lenFile=int(annotT[-1].end_time*100)
        tierComm=tgt.core.IntervalTier(0,lenFile,'commentaires')
        tierTrans=tgt.core.IntervalTier(0,lenFile,'transcription')
        for ann in annotC:
            t=ann.text.replace('commentaire','')
            debut=ann.start_time;fin=ann.end_time
            a=tgt.core.Annotation(debut,fin,t)
            tierComm.add_annotation(a)
        for ann in annotT:
            t=ann.text.replace('transcription','').replace('.','').replace(',',' ')
            debut=ann.start_time;fin=ann.end_time
            a=tgt.core.Annotation(debut,fin,t)
            tierTrans.add_annotation(a)
        #print(tierComm)
        # on crée le textGrid
        txtGrid=tgt.core.TextGrid('a')
        txtGrid.add_tier(tierTrans)
        txtGrid.add_tier(tierComm)
        tgt.io.write_to_file(txtGrid,filename)
