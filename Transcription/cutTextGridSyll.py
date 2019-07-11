# -*- coding: utf-8 -*
import os, glob
import tgt
import stackprinter
path='../PythonUtils/'
stackprinter.set_excepthook(style='color')
exec(open(path+'StoryCond.py').read())
exec(open(path+'Dist.py').read())
exec(open(path+'CSV.py').read())

def deleteAnnot(fSyll,name,mini,maxi):
    tier=fSyll.get_tier_by_name(name) # silence ou syllables
    times=[] # annotations à supprimer
    for annot in tier:
        begin=annot.start_time
        end=annot.end_time
        length=end-begin
        # on gère l'overlapping : si dépasse un tout petit peu, garde
        # on choisit celles qu'on va supprimer (on supprime pas dans le parcours)
        # pour supprimer, il faut que la partie qui dépasse représente plus 
        # de 30% de la longueur de l'intervalle
        if length>0 and ((end>maxi and (end-maxi)/length>0.3) or (begin<mini and (mini-begin)/length>0.3)):
            times.append(begin)
        elif length==0 and (end>maxi or begin<mini):
            times.append(begin)
    # on les supprime
    for begin in times:
         tier.delete_annotation_by_start_time(begin)
    return tier


# ouvre les textgrid_syll annotés avec le nombre de syllabes, coupe le début et la fin pour enlever le dialogue avec l'expérimentateur
for idNum in range(1,22):
    pathSyll='AudioList/id'+str(idNum).zfill(2)+'/Syll/'
    path='AudioList/id'+str(idNum).zfill(2)+'/'
    for filename in glob.glob(os.path.join(pathSyll, '*.TextGrid_syll')):
        # textgrid avec les positions de syllabes
        fSyll=readTG(filename)
        # textgrid avec la transcription -> donne le début et la fin
        name=ntpath.basename(filename)[:-5] # nom sans le syll et sans le path
        f=readTG(path+name)
        if f!=0 : # la lecture a marché
            print(filename)
            annot=f.get_tier_by_name('transcription').annotations
            # on trouve les première et dernière annotations du textgrid annoté
            mini=annot[0].start_time
            maxi=annot[-1].end_time
            # on choisit manuellement ce qu'on supprime 
            syllTier=deleteAnnot(fSyll,'syllables',mini,maxi) # positions des syll
            silencesTier=deleteAnnot(fSyll,'silences',mini,maxi) # intervalles
            # on crée le nouveau textgrid en enlevant début et fin
            txtGrid=tgt.core.TextGrid()
            # on rajoute les tier au textgrid
            txtGrid.add_tier(syllTier)
            txtGrid.add_tier(silencesTier)
            # on écrit le textgrid
            tgt.io.write_to_file(txtGrid,filename)
