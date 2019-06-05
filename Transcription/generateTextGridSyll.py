# -*- coding: utf-8 -*
from SpeechRate import myspsr,mysppaus,myspsyl,myspatc,myspst,myspod,mysptotal
import os,glob
import stackprinter
import ntpath
stackprinter.set_excepthook(style='color')

path='../PythonUtils/'
exec(open(path+'CSV.py').read())


praatPath='/home/steinhia/Documents/Alex/Transcription/'
csvTab=[]
firstLine=['nbSyll','nbPauses','SpeechRate','ArticulationRate','SpeakingDuration','originalDuration']
for idNum in range(1,22):
    path='/home/steinhia/Documents/Alex/Transcription/AudioList/id'+str(idNum).zfill(2)+'/'
    for filename in glob.glob(os.path.join(path, '*.wav')):
        [c,_]=num2CS(filename)
        if 'env' not in filename :
            name=ntpath.basename(filename)
            print(filename)
            wav=name[:-4]
            tot=mysptotal(wav,path,praatPath)
#            nbSyll=tot[0][0]
#            nbPauses=tot[1][0]
#            SpeechRate=tot[2][0]
#            ArticulationRate=tot[3][0]
#            SpeakingDuration=tot[4][0]
#            originalDuration=tot[5][0]
 #           createLigne(filename,csvTab,[nbSyll,nbPauses,SpeechRate,ArticulationRate,SpeakingDuration,originalDuration])
print("csvTab",csvTab)
#WriteCSV(csvTab,firstLine,'brutDebitAudio.csv')
