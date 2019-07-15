# -*- coding: utf-8 -*-
import csv
import os

####### fonctions utilisées pour la suite ############"
### TODO import ###########

# récupérer le jour du nom de fichier
def jourF(filename):
    name=ntpath.basename(filename)
    j=int(name[18])
    return j
    

# conditions de 0 a 3 pour les recall, j de 1 a 3
# return [condition,order]
def name2CS(filename):
    name=ntpath.basename(filename)
    cOrder=Order(name[6:10])
    sOrder=Order(name[12:16])
    num=int(name[21:23])
    j=int(name[18])
    tab=[[6,8,10,12],[3,5,7,9]]
    if j<3 and num in tab[j-1]:
        index=int(tab[j-1].index(num))
        return [int(cOrder[index]),int(sOrder[index])]
    return [-1,-1]


# replace l'ordre entre 0 et 3
def Order(order):
    if '4' in order:
        s=''
        for i in order:
            s+=str(int(i)-1)
        return s
    return order


################ PKL ###############


# enregistrer pkl pour échanger des données entre fichiers
def SavePkl(filename,data):
    name=filename[:-4]+'.pkl'
    output = open(name, 'wb')
    pickle.dump(data, output)

# ouvrir pkl pour récupérer les données
def OpenPkl(filename):
    name=filename[:-4]+'.pkl'
    with open(name, 'rb') as f:
        data = pickle.load(f)
    return data


############################# CSV ##############################

# lit le fichier csv
def CsvReader(name):
    with open(name, 'r') as f:
        reader = csv.reader(f)
        l = list(reader)
    return l

# ecrit un csv
# firstline est seulement le complément de la première ligne
# par défaut, il y a déjà lineBegin
def WriteCSV(csvTab,firstLine,filename):
    lineBegin=["id","jour","ordre conditions","ordre histoires","condition","histoire"]
    lineBegin+=firstLine
    with open(filename, mode='w') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(lineBegin) # écrit une ligne : les en-tête
        for i in csvTab:
            writer.writerow(i) # écrit une ligne


# rajoute une ligne à csvTab à partir des données de res, et renvoie cette ligne
def createLigne(filename,csvTab,res):
    name=ntpath.basename(filename) # nom sans path
    cOrder=name[6:10] # ordre des conditions
    sOrder=name[12:16] # ordre des histoires
    num=int(name[21:23]) # nxx
    sujet=int(name[2:4]) # idxx
    jour=int(name[18]) # jx
    [c,s]=name2CS(name) # condition et histoire du fichier
    ligne=[sujet,jour,"c "+Order(cOrder),"s "+ Order(sOrder),c,s] # début de ligne
    ligne+=res # données à stocker
    csvTab.append(ligne) # on rajoute la ligne au tableau
    return ligne


################## TEXTGRID ########################

# lit le textgrid en fonction de l'encodage du fichier
def readTG(filename):
    f=0 # comme il est défini ici, il existera encore en sortant de la boucle if
    cmd='file -i '+filename # commande shell "file -i filename" -> I sous MacOS
    utf=os.popen(cmd).read() # résultat de la commande shell : string contient encodage
    if 'utf-8' in utf: # si le fichier est encodé en utf-8
        f=tgt.io.read_textgrid(filename,encoding='utf-8') # renvoie f, objet TextGrid
    if 'utf-16be' in utf:
        f=tgt.io.read_textgrid(filename,encoding='utf-16-be')
    if 'us-ascii' in utf:
        f=tgt.io.read_textgrid(filename,encoding='us-ascii')
    return f
