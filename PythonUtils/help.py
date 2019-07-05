import os, glob

########################### os, fichiers ######################

for filename in os.listdir(path):
    if 'neohir' in filename:
        os.rename(filename,'efr')

path='toto/'
for filename in glob.glob(os.path.join(path, '*.TextGrid')):
    print(filename)


f=codecs.open("file.txt",encoding="utf-8")
l=f.read().splitlines()



######### pkl ###################"

def SavePkl(filename,data):
    name=filename[:-4]+'.pkl'
    output = open(name, 'wb')
    pickle.dump(data, output)

def OpenPkl(filename):
    name=filename[:-4]+'.pkl'
    with open(name, 'rb') as f:
        data = pickle.load(f)
    return data

############ CSV #####################"

def CsvReader(name):
    with open(name, 'r') as f:
        reader = csv.reader(f)
        l = list(reader)
    return l

def WriteCSV(csvTab,firstLine,filename):
    with open(filename, mode='w') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(firstLine)
        for i in csvTab:
            writer.writerow(i)


############ string ###############

line=string.split('\t')
s=s.replace('-','_')
string.lower()
str(idNum).zfill(2)


###################### list #############
next(x for x in l if x!=0)



######################## plot ##################


############## dico #######
if key, val in dico.items()
if key in dico.keys()
if value in dico.values()
sorted_d=sorted(dico.items(), key=itemgetter(1), reverse=True) # trier par valeur
