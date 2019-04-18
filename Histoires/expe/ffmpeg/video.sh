#!/bin/bash

for i in $(seq -w 1 4) 
do 
    for j in $(seq -w 1 4) 
    do 
        for k in $(seq -w 1 4) 
        do 
            for l in $(seq -w 1 4) 
            do 
                st=0
                for n in $i $j $k $l; do
                [ "$i" = "$n" ]
                st=$(( $? + st ))
            done
            if ! [[$i -eq $j]] 
            then
                echo "They were all the same"
            fi
                #if $i!=$j
                    #&& ["$i" != "$k"] && ["$i" != "$l"] && ["$j" != "$k"] && ["$j" != "$l"] && ["$k" != "$l"]
                #then
                #    echo $i$j$k$l; 
                #fi
            done;
        done;
    done; 
done;


#for i in $(seq 1 10);
#    for j in $(seq 1 10);
#        for k in $(seq 1 10);
#            for k in $(seq 1 10);
#                echo $i
#            
#
## on concatène les images
#ffmpeg -f concat -i fichier.txt -vsync vfr -pix_fmt yuv420p res.mp4
## on crée le fichier audio
#ffmpeg -i "concat:debut.mp3|story1.mp3|story2.mp3|story3.mp3|story4.mp3|fin.mp3" -acodec copy audio1234.mp3
### on génère la vidéo
#ffmpeg -i res.mp4 -i audio1234.mp3 -acodec copy res.avi
##






