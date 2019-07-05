# -*- coding: utf-8 -*
import tgt
from scipy.io import wavfile
import os, glob
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

# on ne fusionne les intervalles manuellement que pour transcription, ce fichier calque commentaires dessus

for idNum in range(25,26):#16):
    path='AudioList/id'+str(idNum).zfill(2)+'/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        print(filename)
        wavName=filename[:-8]+'wav'
        f=readTG(filename)
        if f!=0:
            # get tier transcription
            tr=f.get_tier_by_name('transcription')
            # crée tier commentaires
            co2=tgt.core.IntervalTier(tr.start_time,tr.end_time, name='commentaires')
            for iv in tr:
                # on crée les annotations
                ann=tgt.core.Annotation(iv.start_time,iv.end_time,'commentaire')
                co2.add_annotation(ann)
            # on crée le nouveau textgrid
            txtGrid=tgt.core.TextGrid()
            txtGrid.add_tier(tr)
            txtGrid.add_tier(co2)
            # on l'enlève si il existe déjà
            os.remove(filename)
            try:
                tgt.io.write_to_file(txtGrid, filename)
            except:
                print "écriture impossible ",filename

