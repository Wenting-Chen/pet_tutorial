#include "merlict_c89/merlict_c89.h"

int c_json_scenery_to_merlict_scenery(
        const char *json_in_path,
        const char *scenery_out_path,
        const char *octree_out_path)
{
        struct mliScenery scenery = mliScenery_init();
        struct mliOcTree octree = mliOcTree_init();

        mli_check(
                mliScenery_malloc_from_json_path(&scenery, json_in_path),
                "Can not read scenery from json.");

        mli_check(
                mliOcTree_malloc_from_scenery(&octree, &scenery),
                "Failed to build octree from scenery.");

        mli_check(
                mliScenery_write_to_path(&scenery, scenery_out_path),
                "Failed to write merlict-scenery to file.");

        mli_check(
                mliOcTree_write_to_path(&octree, octree_out_path),
                "Failed to write octree to file.");

        mliOcTree_free(&octree);
        mliScenery_free(&scenery);
        return 1;
error:
        return 0;
}

int c_propagate(
        const unsigned int random_seed,
        const unsigned int max_interactions,
        const char *scenery_path,
        const char *octree_path,
        const int num_photons,
        const double *photons,
        const int final_object_index,
        int *num_hits,
        float *hit_table)
{
        struct mliMT19937 prng = mliMT19937_init(random_seed);
        struct mliScenery scenery = mliScenery_init();
        struct mliOcTree octree = mliOcTree_init();
        int i, j;

        (*num_hits) = 0;
        mli_check(
                mliScenery_read_from_path(&scenery, scenery_path),
                "Failed to read merlict-scenery from file.");

        mli_check(
                mliOcTree_read_and_malloc_from_path(&octree, octree_path),
                "Failed to read octree from file.");

        for (i = 0; i < num_photons; i++) {
                struct mliPhoton photon;
                struct mliDynPhotonInteraction history =
                        mliDynPhotonInteraction_init();
                struct mliPhotonInteraction final;
                j = i*(3+3+1);

                mli_check(mliDynPhotonInteraction_malloc(
                        &history,
                        max_interactions),
                        "Failed to malloc photon-history.");

                photon.ray = mliRay_set(
                        mliVec_set(
                                photons[j+0],
                                photons[j+1],
                                photons[j+2]),
                        mliVec_set(
                                photons[j+3],
                                photons[j+4],
                                photons[j+5]));
                photon.wavelength = photons[j+6];
                photon.simulation_truth_id = i;

                mli_check(mli_propagate_photon(
                        &scenery,
                        &octree,
                        &history,
                        &photon,
                        &prng,
                        max_interactions),
                        "Faild to propagate photon.");

                final = history.arr[history.dyn.size - 1];
                if (final.object_idx >= 0) {
                        int id_primitive = scenery.user_ids[final.object_idx];
                        if (id_primitive == final_object_index) {
                                int hi = (*num_hits)*7;
                                int h;
                                float total_time_of_flight = 0.0;

                                for (h = 0; h < history.dyn.size; h++) {
                                        double time_of_flight = 0.0;
                                        mli_check(mli_time_of_flight(
                                                &scenery,
                                                &history.arr[h],
                                                &photon,
                                                &time_of_flight),
                                                "Could not find time_of_flight"
                                        );
                                        total_time_of_flight += time_of_flight;
                                }

                                hit_table[hi + 0] = final.position_local.x;
                                hit_table[hi + 1] = final.position_local.y;
                                hit_table[hi + 2] = final.position_local.z;

                                hit_table[hi + 3] = final.position.x;
                                hit_table[hi + 4] = final.position.y;
                                hit_table[hi + 5] = final.position.z;

                                hit_table[hi + 6] = total_time_of_flight;

                                /*
                                mliDynPhotonInteraction_print(
                                        &history,
                                        &scenery);
                                */
                                (*num_hits) = (*num_hits) + 1;
                        }
                }

                mliDynPhotonInteraction_free(&history);
        }

        mliOcTree_free(&octree);
        mliScenery_free(&scenery);
        return 1;
error:
        return 0;
}