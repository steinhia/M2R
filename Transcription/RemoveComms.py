# -*- coding: utf-8 -*
import tgt
import os, glob
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

###### enlève les commentaires et les 'transcription' en trop pour traiter les fichiers

for idNum in range(1,22):
    path='Resultats/id'+str(idNum).zfill(2)+'/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        print(filename)
        # on lit le textgrid
        f=readTG(filename)
        t_end=f.end_time
        # on récupère les tier
        annotC=f.get_tier_by_name('commentaires').annotations
        annotT=f.get_tier_by_name('transcription').annotations
        tierComm=tgt.core.IntervalTier(0,t_end,'commentaires')
        tierTrans=tgt.core.IntervalTier(0,t_end,'transcription')
        # on enlève le mot 'commentaire'
        for ann in annotC:
            t=ann.text.replace('commentaire','')
            debut=ann.start_time;fin=ann.end_time
            a=tgt.core.Annotation(debut,fin,t)
            tierComm.add_annotation(a)
        # on enlève le mot 'transcription', la ponctuation et on met toutes les hésitations en minuscule
        for ann in annotT:
            t=ann.text.replace('transcription','').replace('.','').replace(',',' ').replace('Hm','hm').replace('Und','und').replace('Ja','ja').replace('Genau','genau')
            debut=ann.start_time;fin=ann.end_time
            a=tgt.core.Annotation(debut,fin,t)
            tierTrans.add_annotation(a)
        # on crée le textGrid
        txtGrid=tgt.core.TextGrid('a')
        txtGrid.add_tier(tierTrans)
        txtGrid.add_tier(tierComm)
        tierHes=-1
        # s'il existe pas, on crée le tier hésitations (analyse synchro, en cours)
        if 'Hes' not in f.get_tier_names():
            tierHes=tgt.core.IntervalTier(0,t_end,'Hes')
        else:
            tierHes=f.get_tier_by_name('Hes')
        txtGrid.add_tier(tierHes)
        tgt.io.write_to_file(txtGrid,filename)
