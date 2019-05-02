path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())


brutMoCap=CsvReader('../MoCapAnalysis/brutMoCap.csv')
brutRecall=CsvReader('../RecallTest/brut.csv')
brutDebit=CsvReader('../Transcription/brutDebit.csv')
brutTranscriptionCT=CsvReader('../Transcription/brutTranscriptionCT.csv')
#print(brutMoCap)
#print(brutRecall)
#print(brutDebit)
#print(brutTranscriptionCT)

def keyName(i):
    return i[0].zfill(2)+i[1]+i[4]

def completeDico(dico,brut,indices,n):
    # toutes les lignes doivent finir avec le même nombre de lignes
    for i in brut[1:]:
        key=keyName(i)
        if key not in dico.keys():
            dico[key]=i[:6]
        for indice in indices:
            dico[key].append(i[indice])
    fillX(dico,n)

def fillX(dico,n):
    for i in dico.values():
        fill=int(n-len(i))
        i+=['X']*fill



firstLine=['id','jour','ordre conditions','ordre histoires','condition','histoire','PM oral','nbSyll','debit moyen','variance debit','identification','dénomination']
dico={}
# pour tout retrouver, on crée un dico avec comme clé id-jour-condition
completeDico(dico,brutTranscriptionCT,[6],7)
completeDico(dico,brutDebit,range(6,9),10)


# TODO mettre histoire en format 0 3 !!!!!!!!!
# pour le recall, on additionne les scores en dénomination et en identification
# on fait un mélange de court terme et long terme
for i in brutRecall[1:]:
    key=keyName(i)
    if key not in dico.keys():
        dico[key]=i[:6]
        dico[key]+=['X','X','X','X']
    dK=dico[key]
    if len(dK)==10:
        dK+=[0,0]
    dK[10]+=1 if i[9]=='False' else 0
    dK[11]+=float(i[13])

csvTab=[]
for i in dico.values():
    print(i)
    csvTab.append(i)

WriteCSV(csvTab,firstLine,'brutResume.csv')
