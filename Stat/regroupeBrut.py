import matplotlib.pyplot as plt
import math
from mpl_toolkits.mplot3d import Axes3D
path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())


brutMoCapBaseline=CsvReader('../MoCapAnalysis/brutMoCapBaseline.csv')
brutMoCap=CsvReader('../MoCapAnalysis/brutMoCap.csv')
brutRecall=CsvReader('../RecallTest/brut.csv')
brutDebit=CsvReader('../Transcription/brutDebit.csv')
brutSyll=CsvReader('../Transcription/brutSyll.csv')
brutTranscriptionCT=CsvReader('../Transcription/brutTranscriptionCT.csv')
#print(brutMoCap)
#print(brutRecall)
#print(brutDebit)
#print(brutTranscriptionCT)

# clé = id + jour + condition
def keyName(i):
    return i[0].zfill(2)+i[1]+i[4]

def completeDico(dico,brut,indices,nDebut,nFin):
    for i in brut[1:]:
        key=keyName(i)
        if key not in dico.keys():
            dico[key]=i[:6]+['']*(nDebut-6)
        # la portion de ligne à récupérer
        for indice in indices:
            dico[key].append(i[indice])
    # toutes les lignes doivent finir avec le même nombre de lignes
    fillX(dico,nFin)

def fillX(dico,nFin):
    for i in dico.values():
        fill=int(nFin-len(i))
        i+=['']*fill



firstLine=['PM oral','nbSyll','debit moyen','variance debit','identification','dénomination','nb0','nb1','freq moy pédalage/baseline','variance pédalage/baseline','freq moy pédalage','variance pédalage','nbSyllAudio','nbPauses','SpeechRate','ArticulationRate','SpeakingDuration','originalDuration']
dico={}
# pour tout retrouver, on crée un dico avec comme clé id-jour-condition
completeDico(dico,brutTranscriptionCT,[6],6,7)
completeDico(dico,brutDebit,range(6,9),7,10)


# pour le recall, on additionne les scores en dénomination et en identification
# on fait un mélange de court terme et long terme TODO a changer
for i in brutRecall[1:]:
    key=keyName(i)
    if key not in dico.keys():
        dico[key]=i[:6]+['']*4
    dK=dico[key]
    print(dK)
    print(i)
    if len(dK)==10:
        dK+=[0,0,0,0] # nombre de 0 et de 1 pour la dénomination
    dK[10]+=1 if i[9]=='False' else 0
    d=float(i[13])
    dK[11]+=d
    print("d",d)
    if d==0:
        dK[12]+=1
    elif abs(d-1)<0.05:
        dK[13]+=1


# pour la mocap, on prend les scores freqCondition/freqBaseline
completeDico(dico,brutMoCapBaseline,range(6,8),14,16)

## puis les scores bruts, mais pas pendant la baseline
for i in brutMoCap[1:]:
    if i[5]!='-1':
        key=keyName(i)
        if key not in dico.keys():
            dico[key]=i[:6]+['']*10
        # la portion de ligne à récupérer
        for indice in range(6,8):
            dico[key].append(i[indice])
## toutes les lignes doivent finir avec le même nombre de lignes
fillX(dico,18)

# on rajoute l'analyse de l'audio sans transcription
completeDico(dico,brutSyll,range(6,12),20,28)



csvTab=[]
for i in dico.values():
    #print(i)
    csvTab.append(i)

WriteCSV(csvTab,firstLine,'brutResume.csv')

# ensuite on analyse les résultats

#[x,y]=[[],[]]
#brutResume=CsvReader('brutResume.csv')
#for line in brutResume[1:]:
#    if len(line)>=16 and line[16]!='' and line[7]!='':
#        x.append(float(line[16]))
#        y.append(float(line[7]))
#
#plt.scatter(x,y)
#plt.show()
