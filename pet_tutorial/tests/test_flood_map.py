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
from sklearn.metrics import pairwise_distances # can be cancelled?

NUM = 4


Thickness_loop = np.linspace(0.0020, 0.0030, num=11)


index = 11
CH_score = np.zeros(index)
SC_score = np.zeros(index)
N_GAMMA_RAYS = 150
N_ph = np.zeros(index)
ytop = np.zeros(index)
ybot = np.zeros(index)
N_stdev = np.zeros(index)
N_sem = np.zeros(index)
CH_sem = np.zeros(index)
for Th_id in range(index):
    LIGHT_GUIDE_THICKNESS = Thickness_loop[Th_id]

    data = np.loadtxt("./data_R_collection/N150/N%d_events_data%1.2fmm_4mmPM.dat"%(N_GAMMA_RAYS, Thickness_loop[Th_id]*1000))
    R = np.loadtxt("./data_R_collection/N150/N%d_R_%1.2fmm_4mmPM.dat"%(N_GAMMA_RAYS, Thickness_loop[Th_id]*1000))

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
    N_stdev[Th_id] = np.std(R[:,3])
    N_sem[Th_id] = np.std(R[:,3])/np.sqrt(np.size(R[:,3]))

    CH_score1 = metrics.calinski_harabasz_score(RR1[:,0:2], RR1[:,2]) 
    CH_score2 = metrics.calinski_harabasz_score(RR2[:,0:2], RR2[:,2]) 
    CH_score3 = metrics.calinski_harabasz_score(RR3[:,0:2], RR3[:,2]) 
    CH_score4 = metrics.calinski_harabasz_score(RR4[:,0:2], RR4[:,2]) 
    CH_score[Th_id] = (CH_score1+CH_score2+CH_score3+CH_score4)/4 # Calinski-Harabasz Index
    CH_score_all = metrics.calinski_harabasz_score(R[:,0:2],R[:,2])
    CHmax = max(CH_score1,CH_score2,CH_score3,CH_score4) 
    CHmin = min(CH_score1,CH_score2,CH_score3,CH_score4)
    CH_sem[Th_id] = np.std([CH_score1,CH_score2,CH_score3,CH_score4])/2
    # plt.title("d = %1.7fmm; <N_photons> = %d;\n CH score = %1.3f; CH score all = %1.3f"%(LIGHT_GUIDE_THICKNESS,np.average(R[:,3]),CH_score[Th_id],CH_score_all))
    # plt.savefig("photos/N10_big/Flood_map_4mm_d_%1.7fmm_%d.png"%(LIGHT_GUIDE_THICKNESS,Th_id))
    plt.show()
    ytop[Th_id] = CHmax - CH_score[Th_id]
    ybot[Th_id] = CH_score[Th_id]-CHmin


error_range = [CH_sem,CH_sem]
x = Thickness_loop
y = CH_score
plt.clf()
plt.errorbar(x*1000,y,yerr=error_range,fmt='o',ecolor='hotpink',
			elinewidth=3,ms=5,mfc='wheat',mec='salmon',capsize=3)
plt.xlabel("Light guide thickness [mm]")
plt.ylabel("CH index")
plt.ylim(0,max(y)+1000)
#plt.savefig("photos/LG thickness-CH score_homogenous ticks, index_max = %d, Gamma rays=%d.png"%(index, N_GAMMA_RAYS))
plt.show()


plt.clf()
error_range_N = [N_sem,N_sem]
plt.errorbar(x*1000,N_ph,yerr=error_range_N,fmt='.',ecolor='blue',
			elinewidth=3,ms=5,mfc='wheat',mec='salmon',capsize=3)
# plt.title("Light guide thickness-Photon number diagramm")
plt.ylim(250,1000)
plt.xticks(Thickness_loop*1000)
plt.xlabel('Light guide thickness [mm]')
plt.ylabel('Average photon number')
#plt.savefig("photos/LG thickness-Photon number_homogenous ticks, index_max = %d, Gamma rays=%d.png"%(index, N_GAMMA_RAYS))
plt.show()
