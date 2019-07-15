# premier fichier

for i in range(6): # 0 à 6, 6 exclus
    print(i)


a=[0]*7
a=[i for i in range(7)]


a=[1,2,3,4,5]
a.append(12)
a=[i*2 for i in range(5)]
a=[i*0.5 for i in range(5)]

# pointeur
b=a
b[0]=5
print(a,b) # change 1, change le 2e, car pointeur vers l'adresse en mémoire
b=list(a) # 2 copies idnépendantes


length=len(a) # longueur de la lsite
for i in range(length):
    print(a[i])

for i in a:
    print(i)

for i,val in enumerate(a): # indice, valeur
    print(val)

for i1, i2 in zip(a,b): # même indice pour 2 listes
    print(i1,i2)

# ex liste des noms et des scores -> print un nom et son score sur chaque ligne
lNoms=["Mielbete","Sonistik"]
lScores=[1,2]
for i1,i2 in zip(lNoms,lScores):
    print(i1,i2)

a=[-2,3,-1,4]
ind=a.index(4) # indice du 4
print("indice",ind)

b=[0,0,0] # scores pour personnage, véhicule, maison
liste=["Mielbete","Sonistik","Madikte"]
# on sait que score de Mielbete =1
b[liste.index("Mielbete")]=1




c=list(map(abs,a)) # j'applique la fonction (par exemple abs) à tous les élmts de la liste
print(c)

def db(entier):
    return 2*entier

print(db(2))

# listes par compréhensions

d=[2*i for i in a]
d=[db(i) for i in a]


# string
fl=["1","2","3"] # float("2")

c=" je m'appelle machin "
print(c[2:8])
print(c+ " coucou")

# manipulation des string
idNum=1
print(str(idNum).zfill(2))
j=1
string="id"+str(idNum)+'/jour'+str(j)

TGName="blabla.TextGrid"
wavName=TGName.replace("TextGrid","wav")
print(TGName,wavName)


# dictionnaires
dico={}
dico={"stuhl":1,"Lasgelich":3}

#dico["stuhl"]=1
#dico["Lasgelich"]=3

print(dico.keys())
print(dico.values())
print(dico.items())

for cle,valeur in dico.items():
    print("cle = ",cle, " valeur = ", valeur)

wd="naana"
l=["kzjof","ef","kezjfio"]
l2=[edit_dist(wd,i) for i in l]
