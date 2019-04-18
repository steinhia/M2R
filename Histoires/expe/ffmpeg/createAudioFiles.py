# -*- coding: utf-8 -*-
import os
import itertools
import subprocess
import codecs
os.chdir('.')


orderList=list(itertools.permutations([1, 2, 3, 4]))

# on crée les fichiers texte
os.chdir('txtFiles/')
f=codecs.open("fichier.txt",encoding="utf-8")
l=f.read().encode('utf-8').splitlines()
for order in orderList:
    newL=[]
    newL+=l[:6] # le début
    string="texte"
    for i in order :
        newL+=l[6+(i-1)*6:12+(i-1)*6]
        string+=str(i)
    newL+=l[30:]
    string+=".txt"
    f = open(string,"w")
    for i in newL:
        f.write(i+"\n")
os.chdir('..')

# on crée le son
os.chdir('audioFiles/')
for order in orderList:
    string="concat:debut.mp3|"
    audios=''
    for i in order:
        string+="story"+str(i)+".mp3|"
        audios+=str(i)
    string+="fin.mp3"
    subprocess.call(['ffmpeg','-i',string,"-acodec","copy","audio"+audios+".mp3"])
os.chdir('..')

# on crée les vidéos muettes 
for order in orderList:
    stringV="txtFiles/texte"
    stringA="audioFiles/audio"
    stringR="videoMuteFiles/video"
    for i in order:
        stringV+=str(i)
        stringA+=str(i)
        stringR+=str(i)
    stringV+=".txt"
    stringA+=".mp3"
    stringR+=".avi"
    subprocess.call(['ffmpeg','-f','concat','-i',stringV,'-vsync','vfr','-pix_fmt','yuv420p',stringR])

# on crée les vidéos avec le son    
for order in orderList:
    stringV="videoMuteFiles/video"
    stringA="audioFiles/audio"
    stringR="videoFiles/video"
    for i in order:
        stringV+=str(i)
        stringA+=str(i)
        stringR+=str(i)
    stringV+=".avi"
    stringA+=".mp3"
    stringR+=".avi"
    subprocess.call(['ffmpeg','-i',stringV,"-i",stringA,"-acodec","copy",stringR])
