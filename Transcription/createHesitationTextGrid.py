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




for idNum in range(2):
    path='Resultats/id'+str(idNum)+'/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        [cond,story]=num2CS(filename)
        if cond!=-1:
            nbCSV=0
            nbSyll=0
            nbHesit=0
            f=readTG(filename)
            if 'Hesitations' in f.get_tier_names():
                hes=f.get_tier_by_name('Hesitations')
                hesitations=[]
                for i in hes:
                    hesitations.append(i.time)
                SavePkl('HesitationsPoints.pkl',hesitations)
