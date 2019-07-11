# -*- coding: utf-8 -*
import tgt
import os, glob
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

for idNum in range(23,24):
    path='Resultats/id'+str(idNum).zfill(2)+'/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        print(filename)
        # on lit le textgrid
        f=readTG(filename)
        t_end=f.end_time
        # on récupère les tier
        annotC=f.get_tier_by_name('commentaires').annotations
        annotT=f.get_tier_by_name('transcription').annotations
        # on enlève le mot 'commentaire'
        for ann in annotC:
            t=ann.text.replace('commentaire','')
            ann.text=t
        # on enlève 'transcription', la ponctuation  + hésitations en minuscule
        for ann in annotT:
            t=ann.text.replace('transcription','').replace('.','').replace(',',' ').replace('Hm','hm').replace('Und','und').replace('Ja','ja').replace('Genau','genau')
            ann.text=t
        # s'il existe pas, on crée le tier hésitations (analyse synchro, en cours)
        if 'Hes' not in f.get_tier_names():
            tierHes=tgt.core.IntervalTier(0,t_end,'Hes')
            f.add_tier(tierHes)
        tgt.io.write_to_file(f,filename,encoding='utf-8')
