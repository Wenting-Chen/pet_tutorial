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
import tqdm


# initial input parameters
NUM = 4 #crystal nunmber each line
disk_num = 2 #silicon PM each line
Thickness_loop = np.array([2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0]) #in mm #Thickness_loop = np.array([2.1, 2.15, 2.6, 2.59, 2.98, 3.0])

PM_edge = 4e-3
x_crystal_max = 0.00305 #crystal edge
y_crystal_max = 0.00305
z_crystal_max = 0.015
N_GAMMA_RAYS = 150 


#calculated parameters
disk_orig = ((0.003051*NUM-1e-6)-PM_edge*disk_num)/(disk_num*2)


for Th_id in range(11):
    LIGHT_GUIDE_THICKNESS = Thickness_loop[Th_id]*1e-3 

    with open("edit1_4mmPM_new.json", "r") as my_file:
        SINGLE_LYSO_SCENERY = json.load(my_file)

    ###### 
    for cryid in range(NUM*NUM-1):
        LYSO_SCENERY = SINGLE_LYSO_SCENERY['children'][0].copy()
        LYSO_SCENERY['id'] = 3+cryid*2
        cry_x = (1+cryid)%NUM
        cry_y = (1+cryid)//NUM
        LYSO_SCENERY['pos']= [0.003051*cry_x,0.003051*cry_y,0]
        SINGLE_LYSO_SCENERY['children'].append(LYSO_SCENERY)

        LYSO_SCENERY = SINGLE_LYSO_SCENERY['children'][1].copy()
        LYSO_SCENERY['id'] = 4+cryid*2
        LYSO_SCENERY['pos']= [0.003051*cry_x,0.003051*cry_y,0]
        
        SINGLE_LYSO_SCENERY['children'].append(LYSO_SCENERY)

    assert(SINGLE_LYSO_SCENERY['children'][2]['id']==888)
    SINGLE_LYSO_SCENERY['children'][2]["vertices"]=[
                [0, 0, 0],
                [0.003051*NUM-1e-6, 0, 0],
                [0, 0.003051*NUM-1e-6, 0],
                [0.003051*NUM-1e-6, 0.003051*NUM-1e-6, 0],
                [0, 0, -LIGHT_GUIDE_THICKNESS],
                [0.003051*NUM-1e-6, 0, -LIGHT_GUIDE_THICKNESS],
                [0, 0.003051*NUM-1e-6, -LIGHT_GUIDE_THICKNESS],                
                [0.003051*NUM-1e-6, 0.003051*NUM-1e-6, -LIGHT_GUIDE_THICKNESS]
    ]

    SINGLE_LYSO_SCENERY['children'][3]["pos"]=[disk_orig,disk_orig, -LIGHT_GUIDE_THICKNESS+1e-6] #SiPM inside Light guide, 1 micrometer gap

    #
    for disk_id in range(disk_num*disk_num-1):
        DISK_SCENERY = SINGLE_LYSO_SCENERY['children'][3]['children'][0].copy()
        DISK_SCENERY['id'] = 9991+disk_id
        disk_x = (1+disk_id)%disk_num
        disk_y = (1+disk_id)//disk_num
        DISK_SCENERY['pos']= [(PM_edge+2*disk_orig)*disk_x,(PM_edge+2*disk_orig)*disk_y,0]
        SINGLE_LYSO_SCENERY['children'][3]['children'].append(DISK_SCENERY)
    #
    #with open('fine_4mmPM_new_complete_scenery%1.0f.json'%(Th_id),'wt') as net_file:
    #    json.dump(SINGLE_LYSO_SCENERY,net_file,indent=4)



    RANDOM_SEED = 1 
    MAX_INTERACTIONS = 100 

    # photon src at center of lyso cube
    QUANTUM_EFFICIENCY = 0.25
    N_PHOTONS_LYSO = 17000 
    N_PHOTONS = int(17000 * QUANTUM_EFFICIENCY)
    CENTER_POINT_SRC = photon_source.isotrop_point_source(
        emission_position=[0.005, 0.005, 0.005],    
        num_photons=N_PHOTONS  # close to saint gobain data sheet for 511keV LYSO
    )

    def run(
        scenery=SINGLE_LYSO_SCENERY,
        object_idx=999,  # the disk beneath
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
    data = np.zeros([N_GAMMA_RAYS*NUM*NUM,disk_num*disk_num+1],dtype=int)
    index = 0

    for gamma_ray_id in tqdm.tqdm(range(N_GAMMA_RAYS)):
        for cryid in range(0,NUM*NUM,1): 
            for sipmid in range(0,disk_num*disk_num,1):
                np.random.seed(RANDOM_SEED+cryid+gamma_ray_id) # always the same for a single hit, but increases when changing from crystal to crystal
                
                crystal_x = (cryid)%NUM
                crystal_y =(cryid)//NUM
                x_emit = np.random.rand()*x_crystal_max+0.003051*crystal_x
                y_emit = np.random.rand()*y_crystal_max+0.003051*crystal_y
                z_emit = np.random.rand()*z_crystal_max
                POINT_SRC = photon_source.isotrop_point_source(emission_position=[x_emit,y_emit,z_emit],num_photons=N_PHOTONS)
                run_data = run(
                    scenery=SINGLE_LYSO_SCENERY,
                    object_idx=9990+sipmid,
                    photons=POINT_SRC,
                    random_seed=RANDOM_SEED,
                    max_interactions=MAX_INTERACTIONS)

                n_photons_hit_sipm = len(run_data[:,0])
                data[index][0] = cryid
                data[index][sipmid+1] = n_photons_hit_sipm

            index=index+1

    #flood map
    block_edge=(0.003051*NUM-1e-6)/2/disk_num
    R = np.zeros([N_GAMMA_RAYS*NUM*NUM,4])

    for crystal_id in range(NUM*NUM):
        for gamma_id in range(N_GAMMA_RAYS):
            mr_x = 0
            mr_y = 0
            for ri in range(1,disk_num*disk_num+1,1): 
                mr_x+=data[data[:,0]==crystal_id][gamma_id][ri]*block_edge*((ri-1)%2*2+1)
                mr_y+=data[data[:,0]==crystal_id][gamma_id][ri]*block_edge*((ri-1)//2*2+1)
            mass=np.sum(data[data[:,0]==crystal_id][gamma_id][1:disk_num*disk_num+1])
            R[crystal_id*N_GAMMA_RAYS+gamma_id]=[mr_x/mass,mr_y/mass,crystal_id,mass]


    np.savetxt("./data_R_collection/N%d_new_events_data%1.2fmm_4mmPM.dat"%(N_GAMMA_RAYS, Thickness_loop[Th_id]), data)
    np.savetxt('./data_R_collection/N%d_new_R_%1.2fmm_4mmPM.dat'%(N_GAMMA_RAYS, Thickness_loop[Th_id]), R)
