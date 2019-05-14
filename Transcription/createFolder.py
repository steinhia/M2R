import os
path='/home/steinhia/Documents/Alex/Transcription/AudioList/'
for i in range(1,22):
    pathid=path+'id'+str(i).zfill(2)+'/'
    if os.path.exists(pathid):
        if not os.path.exists(pathid+'Syll'):
            os.makedirs(pathid+'Syll')
