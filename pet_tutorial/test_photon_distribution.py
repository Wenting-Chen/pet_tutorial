#/usr/bin/env python
import json
import numpy as np
import tempfile
import os
from pet_tutorial import merlict_c89_wrapper
from pet_tutorial import photon_source1
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib as mpl
import tqdm

from sklearn import metrics # Calinski-Harabasz Index
from sklearn.metrics import pairwise_distances 

# initial input parameters

NUM = 4 #crystal nunmber each line
disk_num = 2 #silicon PM each line
PM_edge = 4e-3          #Silicon PM size
x_crystal_max = 0.00305 #crystal size x
y_crystal_max = 0.00305 #crystal size y
z_crystal_max = 0.015   #crystal height
N_GAMMA_RAYS = 1

Thickness_LG = 0.0022


#calculated parameters
disk_orig = ((0.003051*NUM-1e-6)-PM_edge*disk_num)/(disk_num*2)
LIGHT_GUIDE_THICKNESS = Thickness_LG


#build the scenery of PMT with lattice structure
with open("onecrystal_0.0022_edit1.json", "r") as my_file:
    SINGLE_LYSO_SCENERY = json.load(my_file)



RANDOM_SEED = 0 
MAX_INTERACTIONS = 100 #1000

# photon src at center of lyso cube
QUANTUM_EFFICIENCY = 0.25
N_PHOTONS_LYSO = 17000 
N_PHOTONS = int(17000 * QUANTUM_EFFICIENCY)
CENTER_POINT_SRC = photon_source1.isotrop_point_source(
    emission_position=[(0.003051*NUM-1e-6)/2,(0.003051*NUM-1e-6)/2, z_crystal_max/2],   
    num_photons=N_PHOTONS,  # close to saint gobain data sheet for 511keV LYSO
    random_seed=0
)

def run(
    scenery=SINGLE_LYSO_SCENERY,
    object_idx=9990,  # the disk beneath
    photons=CENTER_POINT_SRC,    
    random_seed=RANDOM_SEED,
    max_interactions=MAX_INTERACTIONS,
):
    with tempfile.TemporaryDirectory(prefix="pet_tutorial_") as tmp_dir:

        with open(os.path.join(tmp_dir, "scenery.json"), "wt") as f:
            f.write(json.dumps(scenery, indent=4))

        merlict_c89_wrapper.wrapper.json_scenery_to_merlict_scenery(
            json_in_path=os.path.join(tmp_dir, "scenery.json"),
            merlict_out_path=os.path.join(tmp_dir, "scenery.mli"),
            octree_out_path=os.path.join(tmp_dir, "scenery.octree.mli")
        )


        intersection_table = merlict_c89_wrapper.wrapper.propagate(
            scenery_path=os.path.join(tmp_dir, "scenery.mli"),
            octree_path=os.path.join(tmp_dir, "scenery.octree.mli"),
            object_idx=object_idx,
            photons=photons,
            random_seed=random_seed,
            max_interactions=max_interactions
        )

        return intersection_table

# loop N_GAMMA_RAYS times over all crystals, get random hits inside them
# data = np.zeros([N_GAMMA_RAYS*NUM*NUM,disk_num*disk_num+1],dtype=int)
data = np.zeros([1,disk_num*disk_num+1],dtype=int)
index = 0
gamma_ray_id = 0


# for cryid in range(4):
cryid = 15
plt.clf()   
for gamma_ray_id in range(1):
    # for sipmid in range(0,disk_num*disk_num,1):
    seed_index=RANDOM_SEED+cryid*disk_num*disk_num+gamma_ray_id*NUM*NUM*disk_num*disk_num # always the same for a single hit, but increases when changing from crystal to crystal
    np.random.seed(seed_index)
    crystal_x =(cryid)%NUM
    crystal_y =(cryid)//NUM

    x_emit = np.random.rand()*x_crystal_max+0.003051*crystal_x
    y_emit = np.random.rand()*y_crystal_max+0.003051*crystal_y
    z_emit = np.random.rand()*z_crystal_max
    POINT_SRC = photon_source1.isotrop_point_source(emission_position=[x_emit,y_emit,z_emit],num_photons=N_PHOTONS,random_seed=seed_index)
    for sipmid in range(0,disk_num*disk_num,1):
        run_data = run(
            scenery=SINGLE_LYSO_SCENERY,
            object_idx=9990+sipmid,
            photons=POINT_SRC,
            random_seed=seed_index,#use random number generator
            max_interactions=MAX_INTERACTIONS)
        
        plt.plot(run_data[:,0]*1000,run_data[:,1]*1000,'b.')
        #whereemit[sipmid+cryid*disk_num*disk_num+gamma_ray_id*NUM*NUM*disk_num*disk_num]=[x_emit,y_emit,z_emit,sipmid,cryid,gamma_ray_id]
        n_photons_hit_sipm = len(run_data[:,0])
        data[index][0] = cryid
        data[index][sipmid+1] = n_photons_hit_sipm
        # print(n_photons_hit_sipm)
    index = index+1
plt.xlim(0,(0.003051*NUM-1e-6)*1000)
plt.ylim(0,(0.003051*NUM-1e-6)*1000)
plt.xlabel("Position x [mm]")
plt.ylabel("Position y [mm]")
plt.show()
    
# plt.clf()
# plt.hist(data[:,1],bins=15,ec = 'black')
# plt.vlines(np.average(data[:,1]),0,10,'r')
# plt.title('average%1.1f, max%1.1f, min%1.1f, var%1.3f' %(np.average(data[:,1]),np.max(data[:,1]),np.min(data[:,1]),np.var(data[:,1])))
# plt.savefig("photos/photon_table/new/Zemit%1.6f_Maxint%d_hist%1.4f_crys%d_sipm1.png"%(z_emit,MAX_INTERACTIONS,LIGHT_GUIDE_THICKNESS,cryid))
# plt.show()

# plt.clf()
# plt.hist(data[:,2],bins=15,ec = 'black')
# plt.vlines(np.average(data[:,2]),0,10,'r')
# plt.title('average%1.1f, max%1.1f, min%1.1f, var%1.3f' %(np.average(data[:,2]),np.max(data[:,2]),np.min(data[:,2]),np.var(data[:,2])))
# plt.savefig("photos/photon_table/new/Zemit%1.6f_Maxint%d_hist%1.4f_crys%d_sipm2.png"%(z_emit,MAX_INTERACTIONS,LIGHT_GUIDE_THICKNESS,cryid))
# plt.show()

# plt.clf()
# plt.hist(data[:,3],bins=20,ec = 'black')
# plt.vlines(np.average(data[:,3]),0,10,'r')
# plt.title('average%1.1f, max%1.1f, min%1.1f, var%1.3f' %(np.average(data[:,3]),np.max(data[:,3]),np.min(data[:,3]),np.var(data[:,3])))
# plt.savefig("photos/photon_table/new/Zemit%1.6f_Maxint%d_hist%1.4f_crys%d_sipm3.png"%(z_emit,MAX_INTERACTIONS,LIGHT_GUIDE_THICKNESS,cryid))
# plt.show()

# plt.clf()
# plt.hist(data[:,4],bins=20,ec = 'black')
# plt.vlines(np.average(data[:,4]),0,10,'r')
# plt.title('average%1.1f, max%1.1f, min%1.1f, var%1.3f' %(np.average(data[:,4]),np.max(data[:,4]),np.min(data[:,4]),np.var(data[:,4])))
# plt.savefig("photos/photon_table/new/Zemit%1.6f_Maxint%d_hist%1.4f_crys%d_sipm4.png"%(z_emit,MAX_INTERACTIONS,LIGHT_GUIDE_THICKNESS,cryid))
# plt.show()

# np.savetxt("./photos/photon_table/new/Zemit%1.6f_Maxint%d_Data_%dsamp_%1.4f_crystal%d.dat"%(z_emit,MAX_INTERACTIONS,gamma_ray_id+1,Thickness_LG,cryid), data)
