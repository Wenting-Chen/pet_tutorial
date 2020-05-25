import json
import numpy as np
import tempfile
import os
from . import merlict_c89_wrapper
from . import photon_source


EXAMPLE_SCENERY = {
    "functions": [
        {
            "name": "unity",
            "values": [
                    [200e-9, 1.0],
                    [1200e-9, 1.0]
                ]
        },
        {
            "name": "refraction_glass",
            "values": [
                    [200e-9, 1.49],
                    [1200e-9, 1.49]
                ]
        },
        {
            "name": "+infinity",
            "values": [
                    [200e-9, 9e3],
                    [1200e-9, 9e3]
                ]
        },
        {
            "name": "zero",
            "values": [
                    [200e-9, 0.0],
                    [1200e-9, 0.0]
                ]
        }
    ],
    "colors": [
        {"rgb": [22, 9, 255], "name": "blue"},
        {"rgb": [255, 91, 49], "name": "red"},
        {"rgb": [16, 255, 0], "name": "green"},
        {"rgb": [23, 23, 23], "name": "grey"}
    ],
    "media": [
        {
            "name": "vacuum",
            "refraction": "unity",
            "absorbtion": "+infinity"
        },
        {
            "name": "glass",
            "refraction": "refraction_glass",
            "absorbtion": "+infinity",
        }
    ],
    "default_medium": "vacuum",
    "surfaces": [
        {
            "name": "glass_blue",
            "material": "Transparent",
            "specular_reflection": "unity",
            "diffuse_reflection": "unity",
            "color": "blue"
        },
        {
            "name": "glass_red",
            "material": "Transparent",
            "specular_reflection": "unity",
            "diffuse_reflection": "unity",
            "color": "red"
        },
        {
            "name": "specular_mirror",
            "material": "Phong",
            "specular_reflection": "unity",
            "diffuse_reflection": "zero",
            "color": "green"
        },
        {
            "name": "perfect_absorber",
            "material": "Phong",
            "specular_reflection": "zero",
            "diffuse_reflection": "zero",
            "color": "grey"
        }
    ],
    "children": [
        {
            "type": "Frame",
            "id": 42,
            "pos": [0, 0, 1],
            "rot": {"repr": "tait_bryan", "xyz": [0, 0, 0]},
            "children": [
                {
                    "type": "Disc",
                    "id": 1,
                    "pos": [0, 0, -1],
                    "rot": {"repr": "tait_bryan", "xyz": [0, 0, 0]},
                    "radius": 1.0,
                    "surface": {
                        "inner": {"medium": "vacuum", "surface": "glass_blue"},
                        "outer": {"medium": "glass", "surface": "glass_red"}
                    }
                },
                {
                    "type": "Cylinder",
                    "id": 3,
                    "pos": [0, 0, 0],
                    "rot": {"repr": "tait_bryan", "xyz": [0, 0, 0]},
                    "radius": 1.0,
                    "length": 2.0,
                    "surface": {
                        "inner": {"medium": "glass", "surface": "glass_red"},
                        "outer": {"medium": "vacuum", "surface": "glass_blue"}
                    }
                },
                {
                    "type": "Disc",
                    "id": 2,
                    "pos": [0, 0, 1],
                    "rot": {"repr": "tait_bryan", "xyz": [0, 0, 0]},
                    "radius": 1.0,
                    "surface": {
                        "inner": {"medium": "vacuum", "surface": "glass_red"},
                        "outer": {"medium": "glass", "surface": "glass_blue"}
                    }
                }
            ]
        },
        {
            "type": "Disc",
            "id": 37,
            "pos": [0, 0, 5],
            "rot": {"repr": "tait_bryan", "xyz": [0, 0, 0]},
            "radius": 1.0,
            "surface": {
                "inner": {"medium": "vacuum", "surface": "specular_mirror"},
                "outer": {"medium": "vacuum", "surface": "perfect_absorber"}
            }
        },
        {
            "type": "Disc",
            "id": 47,
            "pos": [0, 0, -5],
            "rot": {"repr": "tait_bryan", "xyz": [0, 0.785, 0]},
            "radius": 2.0,
            "surface": {
                "inner": {"medium": "vacuum", "surface": "perfect_absorber"},
                "outer": {"medium": "vacuum", "surface": "specular_mirror"}
            }
        },
        {
            "type": "Sphere",
            "id": 12,
            "pos": [-5, 0, -5],
            "rot": {"repr": "tait_bryan", "xyz": [0, 0.785, 0]},
            "radius": 1.0,
            "surface": {
                "inner": {"medium": "vacuum", "surface": "perfect_absorber"},
                "outer": {"medium": "vacuum", "surface": "perfect_absorber"}
            }
        }
    ]
}

EXAMPLE_PHOTONS = photon_source.isotrop_point_source(
    emission_position=[0, 0, -4],
    num_photons=10000
)


def run(
    scenery=EXAMPLE_SCENERY,
    object_idx=47,
    photons=EXAMPLE_PHOTONS,
    random_seed=1337,
    max_interactions=100,
    tmp_dir='run_tmp'
):
    os.makedirs(tmp_dir, exist_ok=True)

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