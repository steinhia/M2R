# -*- coding: utf-8 -*
import tgt
import os, glob
import ntpath
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

def isUTF8(data):
    try:
        data.decode('UTF-8')
    except UnicodeDecodeError:
        return False
    else:
        return True

 #### on n'utilise pas ce fichier ########
cTab=[0,0,0,0];sTab=[0,0,0,0];nb=0;
cTabNb=[0,0,0,0];sTabNb=[0,0,0,0]
[c,s]=[0,0]
for idNum in range(1,5):
    cTab=[0,0,0,0];sTab=[0,0,0,0];nb=0;
    path='Resultats/id'+str(idNum)+'/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        #print filename
        f = open(filename, "r")
        goodTier=True
        rL=f.readlines()
        for n,i in enumerate(rL):
            if 'traduction' in i or 'commentaire' in i:
                goodTier=False
            if 'text' in i and goodTier:
                deb=i.index('"')
                # une case transcrite
                tab=i[deb+1:].replace('"','').replace(',',' ').replace('transcription',' ').split()
                n=len(tab)
                #print tab
                [c,s]=num2CS(filename)
                if c!='-1':
                    cTab[int(c)-1]+=n
                    sTab[int(s)-1]+=n
            cTabNb[int(c)-1]+=1
            sTabNb[int(s)-1]+=1
    print("c",cTab)
    print("c",cTabNb,'\n')
    print("s",sTab)
    print("s",sTabNb,'\n')



