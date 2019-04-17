# -*- coding: utf-8 -*
import tgt
from scipy.io import wavfile
import os, glob
#from textgrid import TextGrid,  Interval, Point
#import textgrid #import TextGrid,  Interval, Point


def toUTF8(f):
    sourceEncoding = "binary"
    targetEncoding = "utf-8"
    source = open(f)
    target = open(f,"w")
    target.write(unicode(source.read(), sourceEncoding).encode(targetEncoding))


for idNum in range(7,8):#16):
    path='AudioList/id'+str(idNum).zfill(2)+'/'
    for filename in glob.glob(os.path.join(path, '*.TextGrid')):
        f=0
        #toUTF8(filename)
        wavName=filename[:-8]+'wav'
        if 'bis' not in filename:
            try:
                f=tgt.io.read_textgrid(filename)
            except:
                print "lecture impossible ",filename
            if f!=0:
                tr=f.get_tier_by_name('transcription')
                co2=tgt.core.IntervalTier(tr.start_time,tr.end_time, name='commentaire')
                for iv in tr:
                    ann=tgt.core.Annotation(iv.start_time,iv.end_time,'commentaire')
                    co2.add_annotation(ann)
                txtGrid=tgt.core.TextGrid()
                txtGrid.add_tier(tr)
                txtGrid.add_tier(co2)
                nameBis=filename[:-9]+'bis'+'.TextGrid'
                os.remove(filename)
                try:
                    tgt.io.write_to_file(txtGrid, filename)
                except:
                    print "écriture impossible ",filename

