cd ~/Documents/Alex/Data/Helene/
array=("*j1-n06*.wav" "*j1-n08*.wav" "*j1-n10*.wav" "*j1-n12*.wav" "*j2-n01*.wav" "*j2-n03*.wav" "*j2-n05*.wav" "*j2-n07*.wav" "*j2-n09*.wav" "*j3-n01*.wav")
for i in `seq 1 10`
do
    if [ -d "id$i" ]; then
        cd id$i/Audio/
        for j in "${array[@]}"; do 
            if test $(find -name $j | wc -c) -ne 0; then
                files=( $(find -name "$j") )
                for file in "${files[@]}"; do
                    name=$(basename $file)
                    cp $file ~/Documents/Alex/Transcription/AudioList/id$i/$name
                        #dirName=${name::-4}
                        #if [ ! -d "$dirName" ]; then
                        #   mkdir ~/Documents/Alex/Transcription/AudioList/id$i/$dirNam
                        # copier les bons fichiers
                        #fi
            done
            fi
        done
        cd ../..
    fi
done
