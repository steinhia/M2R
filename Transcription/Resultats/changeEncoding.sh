# encodage de depart
encodeFrom='utf-16'
# encodage voulu
encodeTo='utf-8'
# application du script sur les fichiers *.php
for filename in ` find . -type f -name *.TextGrid`
do  
    var=$(file -i $filename)
    if [[ $var == *utf-16* ]]; then
        echo $filename
        iconv -f $encodeFrom -t $encodeTo $filename -o $filename
    fi
    # sauvegarde du fichier source
    #mv $filename $filename.save
    done
    #iconv -f $encodeFrom -t $encodeTo $filename -o $filename
