# -*- coding: utf-8 -*
import tgt
import os, glob


def isUTF8(data):
    try:
        data.decode('UTF-8')
    except UnicodeDecodeError:
        return False
    else:
        return True



nb=0
tps=0
#for idNum in range(1):
#    path='Resultats/id1/'
#    for filename in glob.glob(os.path.join(path, '*.TextGridbis')):
#        f = open(filename, "r")
#        goodTier=True
#        rL=f.readlines()
#        for n,i in enumerate(rL):
#            if 'traduction' in i:
#                goodTier=False
#            if 'text' in i and goodTier:
#                deb=i.index('"')
#                tab=i[deb+1:].replace('"','').replace(',',' ').split()
#                nb+=len(tab)
#print nb
#

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
#path='Resultats/id1/'
#for filename in glob.glob(os.path.join(path, '*.TextGrid')):
#    with open(filename, 'rb') as source_file:
#        with open(filename+'bis', 'w+b') as dest_file:
#            contents = source_file.read()
#            dest_file.write(contents.decode('utf-16').encode('utf-8'))

#            if 'xmin' in i :
#                print "text"
#            1#print "a",i.split(),"a"
#
#        try:
#            f=tgt.io.read_textgrid(filename,encoding='utf-8')
#        except:
#            print filename
