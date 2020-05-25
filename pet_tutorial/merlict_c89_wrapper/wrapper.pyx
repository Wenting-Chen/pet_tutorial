import numpy as np
import json
cimport numpy as np
cimport cython


cdef extern int c_json_scenery_to_merlict_scenery (
    char *json_in_path,
    char *merlict_out_path,
    char *octree_out_path)


def json_scenery_to_merlict_scenery(
    str json_in_path,
    str merlict_out_path,
    str octree_out_path
):
    cdef int rc = c_json_scenery_to_merlict_scenery(
        json_in_path.encode(),
        merlict_out_path.encode(),
        octree_out_path.encode())

    if rc <= 0:
        raise RuntimeError('Failed to convert json to merlict-scenery.')

    return


cdef extern int c_propagate(
        const unsigned int random_seed,
        const unsigned int max_interactions,
        const char *scenery_path,
        const char *octree_path,
        const int num_photons,
        const double *photons,
        const int final_object_index,
        int *num_hits,
        float *hit_table)


def propagate(
    str scenery_path,
    str octree_path,
    int object_idx,
    np.ndarray[double, ndim=2, mode="c"] photons not None,
    int random_seed=0,
    int max_interactions=100,
):
    assert photons.shape[1] == 7
    cdef int num_photons = photons.shape[0]

    cdef np.ndarray[double, mode = "c"] _photons = photons.flatten()

    cdef np.ndarray[float, mode = "c"] hit_table = np.zeros(
        shape=num_photons*7,
        dtype=np.float32)

    cdef int num_hits = 0

    cdef int rc = c_propagate(
        random_seed,
        max_interactions,
        scenery_path.encode(),
        octree_path.encode(),
        num_photons,
        &_photons[0],
        object_idx,
        &num_hits,
        &hit_table[0])

    if rc <= 0:
        raise RuntimeError('Failed to propagate photons in scenery.')

    out_table = hit_table.reshape((num_photons, 7))
    return out_table[0:num_hits, :]
