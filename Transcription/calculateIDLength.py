# -*- coding: utf-8 -*
import tgt
import os, glob
import stackprinter
from scipy.io import wavfile
stackprinter.set_excepthook(style='color')
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())


nb=0
tps=0
s=0
# calcule le temps de parole pour chaque participant
for idNum in range(1,26):
    tps=0
    path='AudioList/id'+str(idNum).zfill(2)+'/'
    if idNum!=17:
        for filename in glob.glob(os.path.join(path, '*.wav')):
            wavName=filename[:-8]+'wav'
            # ouvre le fichier audio
            fs, data = wavfile.read(filename)
            t=float(len(data))/float(fs)
            tps+=t
        s+=tps
        # print tps par participant
        print("id"+str(idNum)+'/ ' + str(tps/60))                
# temps total
print(str(s/60))                

