# -*- coding: utf-8 -*-
import os
import itertools
import subprocess
os.chdir('.')

# on crée le son
orderList=list(itertools.permutations([1, 2, 3, 4]))
#for order in orderList:
#    string="concat:debut.mp3|"
#    audios=''
#    for i in order:
#        string+="story"+str(i)+".mp3|"
#        audios+=str(i)
#    string+="fin.mp3"
#    subprocess.call(['ffmpeg','-i',string,"-acodec","copy","audio"+audios+".mp3"])


## on crée les vidéos muettes 
#for order in orderList:
#    stringV="../txtFiles/texte"
#    stringA="audio"
#    stringR="../videoMuteFiles/video"
#    for i in order:
#        stringV+=str(i)
#        stringA+=str(i)
#        stringR+=str(i)
#    stringV+=".txt"
#    stringA+=".mp3"
#    stringR+=".avi"
#    subprocess.call(['ffmpeg','-f','concat','-i',stringV,'-vsync','vfr','-pix_fmt','yuv420p',stringR])

    
for order in orderList:
    stringV="../videoMuteFiles/video"
    stringA="audio"
    stringR="../videoFiles/video"
    for i in order:
        stringV+=str(i)
        stringA+=str(i)
        stringR+=str(i)
    stringV+=".avi"
    stringA+=".mp3"
    stringR+=".avi"
    subprocess.call(['ffmpeg','-i',stringV,"-i",stringA,"-acodec","copy",stringR])
    #ffmpeg -i res.mp4 -i audio1234.mp3 -acodec copy res.avi
