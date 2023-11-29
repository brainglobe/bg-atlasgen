"""Script to validate atlases"""

import json
import os
from pathlib import Path

import numpy as np
from bg_atlasapi import BrainGlobeAtlas
from bg_atlasapi.config import get_brainglobe_dir
from bg_atlasapi.list_atlases import (
    get_all_atlases_lastversions,
    get_atlases_lastversions,
)
from bg_atlasapi.update_atlases import update_atlas


def validate_atlas_files(atlas_path: Path):
    """Checks if basic files exist in the atlas folder"""

    assert atlas_path.exists(), f"Atlas path {atlas_path} not found"
    expected_files = [
        "annotation.tiff",
        "reference.tiff",
        "metadata.json",
        "structures.json",
        "meshes",
    ]
    for expected_file_name in expected_files:
        expected_path = Path(atlas_path / expected_file_name)
        assert (
            expected_path.exists()
        ), f"Expected file not found at {expected_path}"
    return True


def _assert_close(mesh_coord, annotation_coord, pixel_size):
    """Helper function to check if the mesh and the annotation coordinate are closer to each other than 10 times the pixel size"""
    assert (
        abs(mesh_coord - annotation_coord) <= 10 * pixel_size
    ), f"Mesh coordinate {mesh_coord} and annotation coordinate {annotation_coord} differ by more than 10 times pixel size {pixel_size}"
    return True


def validate_mesh_matches_image_extents(atlas: BrainGlobeAtlas):
    """Checks if the mesh and the image extents are similar"""

    root_mesh = atlas.mesh_from_structure("root")
    annotation_image = atlas.annotation
    resolution = atlas.resolution

    z_range, y_range, x_range = np.nonzero(annotation_image)
    z_min, z_max = np.min(z_range), np.max(z_range)
    y_min, y_max = np.min(y_range), np.max(y_range)
    x_min, x_max = np.min(x_range), np.max(x_range)

    mesh_points = root_mesh.points
    z_coords, y_coords, x_coords = (
        mesh_points[:, 0],
        mesh_points[:, 1],
        mesh_points[:, 2],
    )
    z_min_mesh, z_max_mesh = np.min(z_coords), np.max(z_coords)
    y_min_mesh, y_max_mesh = np.min(y_coords), np.max(y_coords)
    x_min_mesh, x_max_mesh = np.min(x_coords), np.max(x_coords)

    z_min_scaled, z_max_scaled = z_min * resolution[0], z_max * resolution[0]
    y_min_scaled, y_max_scaled = y_min * resolution[1], y_max * resolution[1]
    x_min_scaled, x_max_scaled = x_min * resolution[2], x_max * resolution[2]

    _assert_close(z_min_mesh, z_min_scaled, resolution[0])
    _assert_close(z_max_mesh, z_max_scaled, resolution[0])
    _assert_close(y_min_mesh, y_min_scaled, resolution[1])
    _assert_close(y_max_mesh, y_max_scaled, resolution[1])
    _assert_close(x_min_mesh, x_min_scaled, resolution[2])
    _assert_close(x_max_mesh, x_max_scaled, resolution[2])

    return True


def open_for_visual_check(atlas):
    pass


def validate_checksum(atlas):
    pass


def check_additional_references():
    # check additional references are different, but have same dimensions
    pass


def validate_atlas(atlas_name, version):
    """Validates the latest version of a given atlas"""

    print(atlas_name, version)
    atlas = BrainGlobeAtlas(atlas_name)
    updated = get_atlases_lastversions()[atlas_name]["updated"]
    if not updated:
        update_atlas(atlas_name)
    atlas_path = Path(get_brainglobe_dir()) / f"{atlas_name}_v{version}"
    assert validate_atlas_files(
        atlas_path
    ), f"Atlas file {atlas_path} validation failed"
    assert validate_mesh_matches_image_extents(
        atlas
    ), "Atlas object validation failed"


def validate_mesh_structure_pairs(atlas_path: Path):
    json_path = Path(atlas_path / "structures.json")
    obj_path = Path(atlas_path / "meshes")

    with open(json_path, "r") as file:
        json_file = json.load(file)
    obj_file_list = [
        file for file in os.listdir(obj_path) if file.endswith(".obj")
    ]

    target_key = "id"
    id_numbers = [item[target_key] for item in json_file if target_key in item]

    [f"{num}.obj" for num in id_numbers if f"{num}.obj" in obj_file_list]
    missing_files = [
        num for num in id_numbers if f"{num}.obj" not in obj_file_list
    ]

    print(f"IDs without corresponding obj files: {missing_files}")


if __name__ == "__main__":
    valid_atlases = []
    invalid_atlases = []
    for atlas_name, version in get_all_atlases_lastversions().items():
        try:
            validate_atlas(atlas_name, version)
            valid_atlases.append(atlas_name)
        except AssertionError as e:
            invalid_atlases.append((atlas_name, e))
            continue

    print("Summary")
    print("### Valid atlases ###")
    print(valid_atlases)
    print("### Invalid atlases ###")
    print(invalid_atlases)
