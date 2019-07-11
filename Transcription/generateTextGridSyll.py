# -*- coding: utf-8 -*
from SpeechRate import myspsr,mysppaus,myspsyl,myspatc,myspst,myspod,mysptotal
import os,glob
import stackprinter
import ntpath
stackprinter.set_excepthook(style='color')

praatPath='/home/steinhia/Documents/Alex/Transcription/'
for idNum in range(1,22):
    path='/home/steinhia/Documents/Alex/Transcription/AudioList/id'+str(idNum).zfill(2)+'/'
    for filename in glob.glob(os.path.join(path, '*.wav')):
        [c,_]=num2CS(filename)
        wav=ntpath.basename(filename)[:-4] # nom sans le path et sans extension
        tot=mysptotal(wav,path,praatPath) # nom fichier wav, path vers wav, path praat
