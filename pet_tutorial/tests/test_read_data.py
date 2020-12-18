#/usr/bin/env python
import json
import numpy as np
import tempfile
import os
from pet_tutorial import merlict_c89_wrapper
from pet_tutorial import photon_source
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib as mpl
from sklearn import metrics # Calinski-Harabasz Index
from sklearn.metrics import pairwise_distances 

NUM = 4

Thickness_loop = np.array([ 2.0, 2.1, 2.15, 2.2, 2.3, 2.4, 2.5, 2.59, 2.6, 2.7, 2.8, 2.9, 2.98, 3.0])

index = 14
CH_score = np.zeros(index)
SC_score = np.zeros(index)
N_GAMMA_RAYS = 150
N_ph = np.zeros(index)

for Th_id in range(index):
    LIGHT_GUIDE_THICKNESS = Thickness_loop[Th_id]*1e-3 

    data = np.loadtxt( "./data_R_collection/N%d_events_data%1.2fmm_4mmPM.dat"%(N_GAMMA_RAYS, Thickness_loop[Th_id]))
    R = np.loadtxt('./data_R_collection/N%d_R_%1.2fmm_4mmPM.dat'%(N_GAMMA_RAYS, Thickness_loop[Th_id]))

    RR1 = R[[ i in (0,1,4,5) for i in R[:,2]]]
    RR2 = R[[ i in (2,3,6,7) for i in R[:,2]]]
    RR3 = R[[ i in (8,9,12,13) for i in R[:,2]]]
    RR4 = R[[ i in (10,11,14,15) for i in R[:,2]]]

    plt.clf()
    for crystal_id in range(NUM*NUM):
        plt.plot(R[R[:,2]==crystal_id][:,0],R[R[:,2]==crystal_id][:,1],'.')

        plt.xlim(0,0.003051*NUM-1e-6)
        plt.ylim(0,0.003051*NUM-1e-6)
    N_ph[Th_id] = np.average(R[:,3])


    CH_score1 = metrics.calinski_harabasz_score(RR1[:,0:1], RR1[:,2]) 
    CH_score2 = metrics.calinski_harabasz_score(RR2[:,0:1], RR2[:,2]) 
    CH_score3 = metrics.calinski_harabasz_score(RR3[:,0:1], RR3[:,2]) 
    CH_score4 = metrics.calinski_harabasz_score(RR4[:,0:1], RR4[:,2]) 
    CH_score[Th_id] = (CH_score1+CH_score2+CH_score3+CH_score4)/4 # Calinski-Harabasz Index
    CH_score_all = metrics.calinski_harabasz_score(R[:,0:1],R[:,2])
    # SC_score1 = metrics.silhouette_score(RR1[:,0:1], RR1[:,2], metric='euclidean') #Silhouette Coefficient

    plt.title("d = %1.2fmm; <N_photons> = %d;\n CH score = %1.2f; CH score all = %1.2f"%(LIGHT_GUIDE_THICKNESS*1e3,np.average(R[:,3]),CH_score[Th_id],CH_score_all))
    #plt.savefig("photos/Flood_map_4mm_d_%1.2fmm_new.png"%(LIGHT_GUIDE_THICKNESS*1e3))
    plt.show()

plt.clf()
plt.plot(Thickness_loop[0:index],CH_score,'*')
plt.title("Light guide thickness-CH score diagramm")
plt.xticks(Thickness_loop)
#plt.savefig("photos/LG thickness-CH score for 2-3mm LG loop.png")
plt.show()

plt.clf()
plt.plot(Thickness_loop[0:index],N_ph,'.')
plt.title("Light guide thickness-Photon number diagramm")
plt.xticks(Thickness_loop)
#plt.savefig("photos/LG thickness-Photon number for 2-3mm LG loop.png")
plt.show()
