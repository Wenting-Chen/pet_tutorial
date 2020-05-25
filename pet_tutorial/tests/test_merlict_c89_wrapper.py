import pet_tutorial
import numpy as np


def test_merlict_c89_wrapper():
    random_seed = 0
    np.random.seed(random_seed)

    isotrop_photons = pet_tutorial.photon_source.isotrop_point_source(
        num_photons=10000,
        emission_position=[0, 0, 0],
        wavelength_mean=433e-9,
        wavelength_std=10e-9
    )

    hit_table = pet_tutorial.scenery.run(
        scenery=pet_tutorial.scenery.EXAMPLE_SCENERY,
        object_idx=47,
        photons=isotrop_photons,
        random_seed=random_seed,
        max_interactions=100
    )

    assert hit_table.shape[0] > 0
    assert hit_table.shape[1] == 7
