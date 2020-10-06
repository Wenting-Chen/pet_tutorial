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

with open("cube_disk.json", "r") as my_file:
    SINGLE_LYSO_SCENERY = json.load(my_file)

RANDOM_SEED = 1
MAX_INTERACTIONS = 100

# photon src at center of lyso cube
N_PHOTONS = 17000
CENTER_POINT_SRC = photon_source.isotrop_point_source(
    emission_position=[0.005, 0.005, 0.005],
    num_photons=N_PHOTONS  # close to saint gobain data sheet for 511keV LYSO
)

def run(
    scenery=SINGLE_LYSO_SCENERY,
    object_idx=3,  # the disk beneath
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

steps = 21
z_start = -1e-9
#z_start = -3e-9
#z_stop = 0.01
z_start = -0.01
z_stop = -1e-9
count = 0

n_bins = 200
x_start = -0.05
x_stop = np.fabs(x_start)
binsx=np.linspace(x_start,x_stop,n_bins+1)
binsy=binsx

x_crystal_max = 0.01
y_crystal_max = 0.01
z_crystal_max = 0.01

N_GAMMA_RAYS = 3
plot_z_max = 8000/10*N_GAMMA_RAYS

#create directory for new photos #29.09.20
#path = "./photos"
#os.mkdir(path)


# loop over multiple z position
for z_position in np.linspace(z_start,z_stop,steps):
    np.random.seed(RANDOM_SEED)
    data = []
    
    for gamma_ray_number in range(N_GAMMA_RAYS):
        SINGLE_LYSO_SCENERY["children"][2]["pos"][2] = z_position
        x_emit = x_crystal_max/2
        y_emit = y_crystal_max/2
        z_emit = z_crystal_max/2
        #x_emit = np.random.rand()*x_crystal_max
        #y_emit = np.random.rand()*y_crystal_max
        #z_emit = np.random.rand()*z_crystal_max
        CENTER_POINT_SRC = photon_source.isotrop_point_source(emission_position=[x_emit,y_emit,z_emit],num_photons=N_PHOTONS)

        data.append(run(
            scenery=SINGLE_LYSO_SCENERY,
            object_idx=3,
            photons=CENTER_POINT_SRC,
            random_seed=RANDOM_SEED,
            max_interactions=MAX_INTERACTIONS))

    data = np.vstack(data)


    # plot some
    plt.clf()
    plt.hist2d(data[:,0],data[:,1],bins=[binsx,binsy],norm=mpl.colors.LogNorm(1,plot_z_max))
    #plt.hist2d(data[:,0],data[:,1],bins=[binsx,binsy])
    ax = plt.gca()
    ax.set(aspect='equal')
    ax.add_patch(
        patches.Rectangle(
            xy=(-x_crystal_max/2, -y_crystal_max/2),  # point of origin.
            width=x_crystal_max,
            height=y_crystal_max,
            linewidth=1,
            color='red',
            fill=False
        )
    )
    plt.title("crystal:10x10x10mm^3, guide_z:%02.01f mm"%(z_position*1000))
    plt.colorbar()
    plt.tight_layout()
    plt.savefig("photos/newz%02d.png"%count)
    count+=1