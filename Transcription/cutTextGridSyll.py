# -*- coding: utf-8 -*
import os, glob
import tgt
import stackprinter
import codecs
import numpy as np
import matplotlib.pyplot as plt
path='../PythonUtils/'
stackprinter.set_excepthook(style='color')
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

def deleteAnnot(fSyll,name,mini,maxi):
    tier=fSyll.get_tier_by_name(name)
    times=[]
    for annot in tier:
        begin=annot.start_time
        end=annot.end_time
        length=end-begin
        # on gère l'overlapping : si dépasse un tout petit peu, garde
        if length>0 and ((end>maxi and (end-maxi)/length>0.3) or (begin<mini and (mini-begin)/length>0.3)):
            times.append(begin)
        elif length==0 and (end>maxi or begin<mini):
            times.append(begin)
    for begin in times:
         tier.delete_annotation_by_start_time(begin)
    return tier


# ouvre les textgrid_syll annotés avec le nombre de syllabes, coupe le début et la fin pour enlever le dialogue avec l'expérimentateur
for idNum in range(1,22):
    pathSyll='AudioList/id'+str(idNum).zfill(2)+'/Syll/'
    path='AudioList/id'+str(idNum).zfill(2)+'/'
    for filename in glob.glob(os.path.join(pathSyll, '*.TextGrid_syll')):
        [cond,story]=num2CS(filename)
        name=ntpath.basename(filename)[:-5]
        fSyll=readTG(filename)
        f=readTG(path+name)
        # on trouve les première et dernière annotations du textgrid annoté
        if f!=0 :
            print(filename)
            annot=f.get_tier_by_name('transcription').annotations
            mini=annot[0].start_time
            maxi=annot[-1].end_time
            # on crée le nouveau textgrid en enlevant début et fin
            txtGrid=tgt.core.TextGrid('essai.TextGrid')
            # on choisit manuellement ce qu'on supprime pour affiner les conditions
            syllTier=deleteAnnot(fSyll,'syllables',mini,maxi)
            silencesTier=deleteAnnot(fSyll,'silences',mini,maxi)
            txtGrid.add_tier(syllTier)
            txtGrid.add_tier(silencesTier)
            tgt.io.write_to_file(txtGrid,filename)
