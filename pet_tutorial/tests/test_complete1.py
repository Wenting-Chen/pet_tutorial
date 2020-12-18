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

#with open("edit_orig.json", "r") as my_file:

#with open("edit1_4mm.json", "r") as my_file: # 4mm
# with open("edit1_4mmPM.json", "r") as my_file: #  3mm
#     SINGLE_LYSO_SCENERY = json.load(my_file)

# initial input parameters
NUM = 4 #crystal nunmber each line
disk_num = 2 #silicon PM each line
#Thickness_loop = np.array([ 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0]) #loop over Thickness of Light Guide
#Thickness_loop = np.array([0.85, 1.1, 1.3, 1.6, 1.8, 1.9, 2.1,2.15,  2.2, 2.3, 2.35, 2.4, 2.45, 2.55, 2.6, 2.7, 2.8, 2.9])
Thickness_loop = np.array([2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0])

#calculated parameters
disk_orig = ((0.003051*NUM-1e-6)-4e-3*disk_num)/(disk_num*2)
#disk_orig = ((0.003051*NUM-1e-6)-3e-3*disk_num)/(disk_num*2)


for Th_id in range(1,2,1):
    LIGHT_GUIDE_THICKNESS = Thickness_loop[Th_id]*1e-3 #in mm

    with open("edit1_4mmPM_new.json", "r") as my_file: #  3mm
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

    SINGLE_LYSO_SCENERY['children'][3]["pos"]=[disk_orig,disk_orig, -LIGHT_GUIDE_THICKNESS+1e-6]

    #
    for disk_id in range(disk_num*disk_num-1):
        DISK_SCENERY = SINGLE_LYSO_SCENERY['children'][3]['children'][0].copy()
        DISK_SCENERY['id'] = 9991+disk_id
        disk_x = (1+disk_id)%disk_num
        disk_y = (1+disk_id)//disk_num
        DISK_SCENERY['pos']= [(0.004+2*disk_orig)*disk_x,(0.004+2*disk_orig)*disk_y,0]
        #DISK_SCENERY['pos']= [(0.003+2*disk_orig)*disk_x,(0.003+2*disk_orig)*disk_y,0]
        SINGLE_LYSO_SCENERY['children'][3]['children'].append(DISK_SCENERY)
    #
    with open('fine_4mmPM_complete_scenery%1.0f.json'%(Th_id),'wt') as net_file:
        json.dump(SINGLE_LYSO_SCENERY,net_file,indent=4)



    RANDOM_SEED = 1 #Problem in loop!!?? 
    MAX_INTERACTIONS = 100 #1000

    # photon src at center of lyso cube
    QUANTUM_EFFICIENCY = 0.25
    N_PHOTONS_LYSO = 17000 
    N_PHOTONS = int(17000 * QUANTUM_EFFICIENCY)
    CENTER_POINT_SRC = photon_source.isotrop_point_source(
        emission_position=[0.005, -0.025, 0.005],    # change to random position ???
        num_photons=N_PHOTONS  # close to saint gobain data sheet for 511keV LYSO
    )

    def run(
        scenery=SINGLE_LYSO_SCENERY,
        object_idx=999,  # the disk beneath
        photons=CENTER_POINT_SRC,       # change to random position ???
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


    steps = 3
    z_start = -0.01
    z_stop = 0.01

    count = 0

    n_bins = 200
    x_start = -0.05
    x_stop = np.fabs(x_start)
    binsx=np.linspace(x_start,x_stop,n_bins+1)
    binsy=binsx

    x_crystal_max = 0.00305
    y_crystal_max = 0.00305
    z_crystal_max = 0.015

    N_GAMMA_RAYS = 150 #100 later
    plot_z_max = 8000/10*N_GAMMA_RAYS

    # loop N_GAMMA_RAYS times over all crystals, get random hits inside them
    data = np.zeros([N_GAMMA_RAYS*NUM*NUM,disk_num*disk_num+1],dtype=int)
    index = 0

    import tqdm

    for gamma_ray_id in tqdm.tqdm(range(N_GAMMA_RAYS)):
        for cryid in range(0,NUM*NUM,1): # attention: must add crystal_x = 0 and crystal_y=0 later
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
            for ri in range(1,disk_num*disk_num+1,1): #5 = disk_num*disk_num+1
                mr_x+=data[data[:,0]==crystal_id][gamma_id][ri]*block_edge*((ri-1)%2*2+1)
                mr_y+=data[data[:,0]==crystal_id][gamma_id][ri]*block_edge*((ri-1)//2*2+1)
            mass=np.sum(data[data[:,0]==crystal_id][gamma_id][1:disk_num*disk_num+1])
            R[crystal_id*N_GAMMA_RAYS+gamma_id]=[mr_x/mass,mr_y/mass,crystal_id,mass]

    # plt.clf()
    # for crystal_id in range(NUM*NUM):
    #     plt.plot(R[R[:,2]==crystal_id][:,0],R[R[:,2]==crystal_id][:,1],'.')

    # plt.xlim(0,0.003051*NUM-1e-6)
    # plt.ylim(0,0.003051*NUM-1e-6)
    # plt.title("d = %1.2f /mm; <N_photons> = %d"%(LIGHT_GUIDE_THICKNESS*1e3,np.average(R[:,3])))
    # plt.show()

    np.savetxt("./data_R_collection/N%d_events_data%1.2fmm_4mmPM.dat"%(N_GAMMA_RAYS, Thickness_loop[Th_id]), data)
    np.savetxt('./data_R_collection/N%d_R_%1.2fmm_4mmPM.dat'%(N_GAMMA_RAYS, Thickness_loop[Th_id]), R)
