# -*- coding: utf-8 -*
import tgt
import os, glob

for idNum in range(1):
    path='Resultats/id1/'
    for filename in glob.glob(os.path.join(path, '*.TextGridbis')):
        with open(filename, 'r') as f:
        # Read whole file into memory ignoring empty lines and lines consisting
        # solely of a single double quote.
            stg = [line.strip() for line in f.readlines()]
            f=tgt.io.read_long_textgrid(filename,stg)
        #except:
        #    print filename
