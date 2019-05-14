
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

c=[0,0,0,0];s=[0,0,0,0];ccount=[0,0,0,0];scount=[0,0,0,0]
Special=['{','}','_','Anglais','(',')']
fC=[0,0,0,0];fS=[0,0,0,0]
varfC=[0,0,0,0];varfS=[0,0,0,0]
csvTab=[]
dico={} # cle = id+jour+c
#TODO pas seulement quand -1
for idNum in range(1,18):
    path='AudioList/id'+str(idNum).zfill(2)+'/Syll/'
    for filename in glob.glob(os.path.join(path, '*')):
        [cond,story]=num2CS(filename)
        if cond!=-1:
            cle=str(idNum).zfill(2)+str(jourF(filename))+str(cond)
            f=readTG(filename)
            annotations=f.get_tier_by_name('syllables').annotations
            points=[]
            # get list of points
            for pt in annotations:
                points.append(pt.time)
            print(points,'\n')
            dico[cle]=points
SavePkl('SyllablesPoints.pkl',dico)
print(dico.keys())
