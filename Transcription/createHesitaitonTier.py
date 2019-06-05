from functools import partial
import pickle
import scipy.io
import tgt
from scipy.io import wavfile
from itertools import groupby, count
import os, glob
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

for idNum in range(1,22):
    path='Resultats/id'+str(idNum).zfill(2)+'/'
    pathSyll='AudioList/id'+str(idNum).zfill(2)+'/Syll/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        print(filename)
        syllName=pathSyll+ntpath.basename(filename)+'_syll'
        f=readTG(filename)
        fSyll=readTG(syllName)
        if 'syllables' not in f.get_tier_names():
            syllables=fSyll.get_tier_by_name('syllables')
            f.add_tier(syllables)
            tgt.io.write_to_file(f,filename)
