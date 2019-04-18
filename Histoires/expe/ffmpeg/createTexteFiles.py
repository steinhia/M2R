
# -*- coding: utf-8 -*-
import math
import csv
import operator
import random
import os
import numpy as np
from collections import Counter
import codecs
import re
import time
from functools import partial
import pickle
import itertools
order=[1,2,3,4]


f=codecs.open("fichier.txt",encoding="utf-8")
l=f.read().encode('utf-8').splitlines()


orderList=list(itertools.permutations([1, 2, 3, 4]))
for order in orderList:
    newL=[]
    newL+=l[:2] # le début
    string="texte"
    for i in order :
        newL+=l[2+(i-1)*6:8+(i-1)*6]
        string+=str(i)
    newL+=l[26:]
    string+=".txt"
    f = open(string,"w")
    for i in newL:
        f.write(i+"\n")
