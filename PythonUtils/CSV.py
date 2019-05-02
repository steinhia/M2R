# -*- coding: utf-8 -*-
import csv
import os

path='../PythonUtils/'
exec(open(path+'StoryCond.py').read())

def CsvReader(name):
    with open(name, 'r') as f:
        reader = csv.reader(f)
        l = list(reader)
    return l

# écrit un csv, et aucune ligne en double
def WriteCSV(csvTab,firstLine,filename):
    with open(filename, mode='w') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(firstLine)
        listLines=[]
        for i in csvTab:
            if i not in listLines:
                writer.writerow(i) 
                listLines.append(i)


def createLigne(filename,csvTab,res):
    name=ntpath.basename(filename)
    cOrder=name[6:10]
    sOrder=name[12:16]
    num=int(name[21:23])
    sujet=int(name[2:4])
    jour=int(name[18])
    [c,s]=num2CS(name)
    ligne=[sujet,jour,"c "+Order(cOrder),"s "+ Order(sOrder),c,s]
    ligne+=res
    csvTab.append(ligne)
    return ligne

def readTG(filename):
    f=0
    cmd='file -i '+filename
    utf=os.popen(cmd).read()
    if 'utf-8' in utf:
        f=tgt.io.read_textgrid(filename,encoding='utf-8')
    if 'utf-16be' in utf:
        f=tgt.io.read_textgrid(filename,encoding='utf-16-be')
    return f
