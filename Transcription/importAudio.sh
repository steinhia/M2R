# récupère les bons fichiers dans Audio_Maren pour les copier dans AudioList

# crée les dossiers dans AudioList
cd AudioList/
for i in `seq 1 25`; do
    num=$(printf "%02d" $i)
    mkdir -p id$num
    # crée le dossier mat
    mkdir -p id$num/Mat
    # crée le dossier Syll
    mkdir -p id$num/Syll
done
# tous les audios
cd ~/Documents/Alex/Audios_maren/

# fichiers à récupérer : patterns
Narray=("*j1-n06*.wav" "*j1-n08*.wav" "*j1-n10*.wav" "*j1-n12*.wav" "*j2-n01*.wav" "*j2-n03*.wav" "*j2-n05*.wav" "*j2-n07*.wav" "*j2-n09*.wav" "*j3-n01*.wav")

# on récupère les fichiers dans Audio_Maren et on copie dans AudioList
for i in `seq 22 25`
do
    # numero de l'id
    num=$(printf "%02d" $i)
    if [ -d "id$num" ]; then
        # numero du jour
        for jour in `seq 1 3`; do
            cd id$num/j$jour/
            # tous les fichiers du jour j de l'id i
            for pattern in "${Narray[@]}"; do 
                # si un fichier match le pattern courant
                if test $(find -name "$pattern" | wc -c) -ne 0; then
                    files=($(find -name "$pattern"))
                    # liste des fichiers à copier
                    for file in "${files[@]}"; do
                        name=$(basename $file)
                        echo $name
                        # copier les bons fichiers
                        cp $file ~/Documents/Alex/Transcription/AudioList/id$num/$name
                    done
                fi
            done
            cd ../..
        done
        fi
done

