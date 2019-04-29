# -*- coding: utf-8 -*
import tgt
import os, glob
import ntpath

def isUTF8(data):
    try:
        data.decode('UTF-8')
    except UnicodeDecodeError:
        return False
    else:
        return True

def num2CS(filename):
    name=ntpath.basename(filename)
    cOrder=name[6:10]
    sOrder=name[12:16]
    num=int(name[21:23])
    tab=[6,3,8,5,10,7,12,9]
    if num in tab:
        return [cOrder[tab.index(num)/2],sOrder[tab.index(num)/2]]
    return [-1,-1]

cTab=[0,0,0,0];sTab=[0,0,0,0];nb=0;
cTabNb=[0,0,0,0];sTabNb=[0,0,0,0]
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
                # chaque mot pour pouvoir afficher les accents
            for i in tab:
                1#print i
                #print '\n'
    print "c",cTab
    print "c",cTabNb,'\n'
    print "s",sTab,
    print "s",sTabNb,'\n'



