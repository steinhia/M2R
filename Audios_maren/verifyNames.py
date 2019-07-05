import os, glob

def checkName(name,j,idNum,cnum,snum):
    jMax=[14,9,1]
    if len(name)<27:
        print("nom trop court ",name)
    else :
        if name[0:2]!="id":
            print("id mal écrit ",name)
        elif not name[2:4].isdigit() or name[2:4]!=idNum:
            print("numéro participant mal écrit/faux ", name)
        elif name[4:6]!="-c":
            print("-c mal écrit ", name)
        # s'ils sont tous entre 1 et 4
        elif any( x not in ['1','2','3','4'] for x in name[6:10]):
           print("ordre des conditions mal écrit", name)
        # s'ils sont tous là
        elif any( x not in name[6:10] for x in ['1','2','3','4'] ):
            print("ordre des conditions mal écrit", name)
        elif cnum!=-1 and cnum!=name[6:10]:
            print("ordre des conditions changeant, attendu "+str(cnum)+" ", name)
        elif name[10:12]!="-s":
            print("-s mal écrit ", name)
        # entre 0 et 4
        elif any( x not in ['1','2','3','4'] for x in name[12:16]):
            print("ordre des histoires mal écrit", name)
        # tous là
        elif any( x not in name[12:16] for x in ['1','2','3','4'] ):
            print("ordre des histoires mal écrit", name)
        elif snum!=-1 and snum!=name[12:16]:
            print("ordre des histoires changeant, attendu "+str(snum)+" ", name)
        elif name[16:19]!="-j"+str(j):
            print("-jx mal écrit, attendu j"+str(j)+" ", name)
        elif name[19:21]!="-n":
            print("-n mal écrit ", name)
        elif (not name[21:23].isdigit()):
            print("mauvais numéro nx ", name)
        elif int(name[21:23])>jMax[j-1]:
            print("numéro nx trop grand ", name)
        if cnum==-1 and name[6:10].isdigit():
            cnum=name[6:10]
            snum=name[12:16]
    return [cnum,snum]

def checkList(liste,j):
    # on regarde s'il manque des fichiers
    jMax=[14,9,1]
    FM=False
    for i in range(1,jMax[j-1]+1):
        if not any( 'n'+str(i).zfill(2) in f for f in liste):
            FM=True
    if FM:
        print('fichiers manquants, liste des fichiers j' +str(j)+' :')
        for f in liste:
            print(f)


# il faut être placé dans Audio-Maren
for i in range(1,37):
    idNum=str(i).zfill(2)
    idStr='id'+idNum
    [cnum,snum]=[-1,-1]
    if os.path.isdir(idStr):
        print(idStr)
        os.chdir(idStr)
        for j in range(1,4):
            os.chdir('j'+str(j))
            filenameList=os.listdir()
            checkList(filenameList,j)
            for name in filenameList:
                if os.path.isfile(name):
                    [cnum,snum]=checkName(name,j,idNum,cnum,snum)
            os.chdir('..')
        os.chdir('..')

