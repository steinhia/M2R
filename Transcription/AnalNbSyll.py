# -*- coding: utf-8 -*
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

l=CsvReader('brutDebit.csv')

# crée le tableau nbSyll mainsLibres - AutreCondition
tab=[];tab2=[]
for i in l[1:]:
# on garde tout sauf mains libres
    if i[4]!='0':
        tab.append(i)
# mains libres
    else:
        tab2.append(i)

for ligne in tab2:
    for l2 in tab:
        # si bon jour et bon participant, on fait mainsLibres-autreCondition
        if ligne[0]==l2[0] and ligne[1]==l2[1]:
            l2[6]=int(l2[6])-int(ligne[6])

firstLine=['nbSyll','nbPauses','meanPauses','varPauses'] 
WriteCSV(tab,firstLine,'brutNbSyll.csv')
