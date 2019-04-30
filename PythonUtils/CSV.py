# -*- coding: utf-8 -*-
import csv
import os

def CsvReader(name):
    with open(name, 'rb') as f:
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
    ligne=[sujet,jour,cOrder,sOrder,c,s]
    ligne+=res
    csvTab.append(res)
