# -*- coding: utf-8 -*
import tgt
import os, glob

exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())


nb=0
tps=0
import tgt
from scipy.io import wavfile
import os, glob

for idNum in range(16):
    tps=0
    path='AudioList/id'+str(idNum).zfill(2)+'/'
    for filename in glob.glob(os.path.join(path, '*.wav')):
        wavName=filename[:-8]+'wav'
        fs, data = wavfile.read(filename)
        t=float(len(data))/float(fs)
        tps+=t
    print("id"+str(idNum)+'/ ' + str(tps/60))                

