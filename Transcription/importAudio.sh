cd ~/Documents/Alex/Data/Audio/
array=("*j1-n06*.wav" "*j1-n08*.wav" "*j1-n10*.wav" "*j1-n12*.wav" "*j2-n01*.wav" "*j2-n03*.wav" "*j2-n05*.wav" "*j2-n07*.wav" "*j2-n09*.wav" "*j3-n01*.wav")
for i in `seq 10 15`
do
    # numero de l'id
    num=$(printf "%02d" $i)
    if [ -d "id$num" ]; then
        cd id$num/j3/

        for j in "${array[@]}"; do 
            if test $(find -name $j | wc -c) -ne 0; then
                files=( $(find -name "$j") )
                for file in "${files[@]}"; do
                    name=$(basename $file)
                    echo $name,$file
                    cp $file ~/Documents/Alex/Transcription/AudioList/id$num/$name
                        #dirName=${name::-4}
                        #if [ ! -d "$dirName" ]; then
                        #   mkdir ~/Documents/Alex/Transcription/AudioList/id$i/$dirNam
                        # copier les bons fichiers
                        ##fi
            done
            fi
        done
        cd ../..
    fi
done
