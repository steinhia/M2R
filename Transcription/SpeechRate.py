import parselmouth
from parselmouth.praat import call, run_file
import glob
import pandas as pd
import numpy as np
import scipy
from scipy.stats import binom
from scipy.stats import ks_2samp
from scipy.stats import ttest_ind
import os



def calcul(m,p,praatPath,z3N,z4N):
    sound=p+"/"+m+".wav"
    sourcerun=praatPath+"myspsolution.praat"
    path=p+"/"
    try:
        objects= run_file(sourcerun, -20, 2, 0.3, "yes",sound,path, 80, 400, 0.01, capture_output=True)
        #print (objects[0]) # This will print the info from the sound object, and objects[0] is a parselmouth.Sound object
        z1=str( objects[1]) # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
        z2=z1.strip().split()
        z3=int(z2[z3N]) # will be the integer number 10
        z4=float(z2[z4N]) # will be the floating point number 8.3
    except:
        z3=0
        print ("Try again the sound of the audio was not clear")
    return z3 

# nbSyll TODO
def myspsyl(m,p,praatPath):
    return calcul(m,p,praatPath,0,3)

# calcule le nombre de pauses dans le fichier TODO
# m=wav file, p=path to audio, praatPath=..
def mysppaus(m,p,praatPath):
    return calcul(m,p,praatPath,1,3)

# speechrate moyen TODO
def myspsr(m,p,praatPath):
    return calcul(m,p,praatPath,2,3)

# articulation rate
def myspatc(m,p,praatPath):
    return calcul(m,p,praatPath,3,3)
# speaking duration TODO
def myspst(m,p,praatPath):
    return calcul(m,p,praatPath,4,3)

# t total avec pauses
def myspod(m,p,praatPath):
    return calcul(m,p,praatPath,5,3)

# ratio temps parole/temps total
def myspbala(m,p,praatPath):
    return calcul(m,p,praatPath,6,3)

# f0 mean
def myspf0mean(m,p,praatPath):
    return calcul(m,p,praatPath,7,3)

# f0 standard deviation
def myspf0sd(m,p,praatPath):
    return calcul(m,p,praatPath,8,3)

# f0 mediane
def myspf0med(m,p,praatPath):
    return calcul(m,p,praatPath,9,3)

# f0 min
def myspf0min(m,p,praatPath):
    return calcul(m,p,praatPath,10,10)

# f0 max
def myspf0max(m,p,praatPath):
    return calcul(m,p,praatPath,11,11)

# 25th quantile of f0 distribution
def myspf0q25(m,p,praatPath):
    return calcul(m,p,praatPath,12,11)

# 75th quantile of f0 distribution
def myspf0q75(m,p,praatPath):
    return calcul(m,p,praatPath,13,11)

# tout
def mysptotal(m,p,praatPath):
    sound=p+"/"+m+".wav"
    sourcerun=praatPath+"myspsolution.praat"
    path=p+"/"
    try:
        objects= run_file(sourcerun, -20, 2, 0.3, "yes",sound,path, 80, 400, 0.01, capture_output=True)
        #print (objects[0]) # This will print the info from the sound object, and objects[0] is a parselmouth.Sound object
        z1=str( objects[1]) # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
        z2=z1.strip().split()
        z3=np.array(z2)
        z4=np.array(z3)[np.newaxis]
        z5=z4.T
    #    dataset=pd.DataFrame({"number_ of_syllables":z5[0,:],"number_of_pauses":z5[1,:],"rate_of_speech":z5[2,:],"articulation_rate":z5[3,:],"speaking_duration":z5[4,:],
    #                      "original_duration":z5[5,:],"balance":z5[6,:],"f0_mean":z5[7,:],"f0_std":z5[8,:],"f0_median":z5[9,:],"f0_min":z5[10,:],"f0_max":z5[11,:],
    #                      "f0_quantile25":z5[12,:],"f0_quan75":z5[13,:]})
    except:
        z5=0
        print ("Try again the sound of the audio was not clear")
    return z5

# ...
def mysppron(m,p,praatPath):
    sound=p+"/"+m+".wav"
    sourcerun=praatPath+"myspsolution.praat"
    path=p+"/"
    try:
        objects= run_file(sourcerun, -20, 2, 0.3, "yes",sound,path, 80, 400, 0.01, capture_output=True)
        print (objects[0]) # This will print the info from the sound object, and objects[0] is a parselmouth.Sound object
        z1=str( objects[1]) # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
        z2=z1.strip().split()
        z3=int(z2[13]) # will be the integer number 10
        z4=float(z2[14]) # will be the floating point number 8.3
        db= binom.rvs(n=10,p=z4,size=10000)
        a=np.array(db)
        b=np.mean(a)*100/10
        print ("Pronunciation_posteriori_probability_score_percentage= :%.2f" % (b))
    except:
        print ("Try again the sound of the audio was not clear")
    return z3
