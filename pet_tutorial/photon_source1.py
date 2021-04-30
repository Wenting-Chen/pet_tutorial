import numpy as np


SUPPORT_X = 0
SUPPORT_Y = 1
SUPPORT_Z = 2

DIRECTION_X = 3
DIRECTION_Y = 4
DIRECTION_Z = 5

WAVELENGTH = 6

def isotrop_point_source(
    num_photons,
    emission_position=[0, 0, 0],
    wavelength_mean=433e-9,
    wavelength_std=10e-9,
    random_seed=0
):
    np.random.seed(random_seed) 
    photons = np.zeros(shape=(num_photons, 7), dtype=np.float64)

    # support
    for dim in range(3):
        photons[:, SUPPORT_X+dim] = emission_position[dim]

    # direction
    for dim in range(3):
        photons[:, DIRECTION_X+dim] = np.random.uniform(
            low=-1,
            high=1,
            size=num_photons)
    norm_dir = np.linalg.norm(
        photons[:, DIRECTION_X:DIRECTION_Z+1],
        axis=1)
    for ph in range(num_photons):
        photons[ph, DIRECTION_X:DIRECTION_Z] /= norm_dir[ph]

    # wavelength
    photons[:, WAVELENGTH] = np.random.normal(
        loc=wavelength_mean,
        scale=wavelength_std,
        size=num_photons)

    return photons
