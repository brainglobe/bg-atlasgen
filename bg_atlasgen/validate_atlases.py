"""Script to validate atlases"""


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

    assert atlas_path.is_dir(), f"Atlas path {atlas_path} not found"
    expected_files = [
        "annotation.tiff",
        "reference.tiff",
        "metadata.json",
        "structures.json",
    ]
    for expected_file_name in expected_files:
        expected_path = Path(atlas_path / expected_file_name)
        assert (
            expected_path.is_file()
        ), f"Expected file not found at {expected_path}"

    meshes_path = atlas_path / "meshes"
    assert meshes_path.is_dir(), f"Meshes path {meshes_path} not found"
    return True


def _assert_close(mesh_coord, annotation_coord, pixel_size, diff_tolerance=10):
    """
    Helper function to check if the mesh and the annotation coordinate
    are closer to each other than an arbitrary tolerance value times the pixel size.
    The default tolerance value is 10.
    """
    assert abs(mesh_coord - annotation_coord) <= diff_tolerance * pixel_size, (
        f"Mesh coordinate {mesh_coord} and annotation coordinate {annotation_coord}",
        f"differ by more than {diff_tolerance} times pixel size {pixel_size}",
    )
    return True


def validate_mesh_matches_image_extents(atlas: BrainGlobeAtlas):
    """Checks if the mesh and the image extents are similar"""

    root_mesh = atlas.mesh_from_structure("root")
    annotation_image = atlas.annotation
    resolution = atlas.resolution

    # minimum and maximum values of the annotation image (z, y, x)
    z_range, y_range, x_range = np.nonzero(annotation_image)
    z_min, z_max = np.min(z_range), np.max(z_range)
    y_min, y_max = np.min(y_range), np.max(y_range)
    x_min, x_max = np.min(x_range), np.max(x_range)

    # minimum and maximum values of the annotation image scaled by the atlas resolution
    z_min_scaled, z_max_scaled = z_min * resolution[0], z_max * resolution[0]
    y_min_scaled, y_max_scaled = y_min * resolution[1], y_max * resolution[1]
    x_min_scaled, x_max_scaled = x_min * resolution[2], x_max * resolution[2]

    # z, y and x coordinates of the root mesh (extent of the whole object)
    mesh_points = root_mesh.points
    z_coords, y_coords, x_coords = (
        mesh_points[:, 0],
        mesh_points[:, 1],
        mesh_points[:, 2],
    )

    # minimum and maximum coordinates of the root mesh
    z_min_mesh, z_max_mesh = np.min(z_coords), np.max(z_coords)
    y_min_mesh, y_max_mesh = np.min(y_coords), np.max(y_coords)
    x_min_mesh, x_max_mesh = np.min(x_coords), np.max(x_coords)

    # checking if root mesh and image are on the same scale
    _assert_close(z_min_mesh, z_min_scaled, resolution[0])
    _assert_close(z_max_mesh, z_max_scaled, resolution[0])
    _assert_close(y_min_mesh, y_min_scaled, resolution[1])
    _assert_close(y_max_mesh, y_max_scaled, resolution[1])
    _assert_close(x_min_mesh, x_min_scaled, resolution[2])
    _assert_close(x_max_mesh, x_max_scaled, resolution[2])

    return True


def open_for_visual_check():
    pass


def validate_checksum():
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


# list to store the validation functions
all_validation_functions = [
    validate_atlas_files,
    validate_mesh_matches_image_extents,
    open_for_visual_check,
    validate_checksum,
    check_additional_references,
    validate_atlas,
]

# list to store atlas specific parameters for all validation function
all_validation_function_parameters = []

# list to store the errors of the failed validations
failed_validations = []
successful_validations = []


for atlas_name, version in get_all_atlases_lastversions().items():
    validation_function_parameters = [
        # validate_atlas_files(atlas_path: Path)
        (Path(get_brainglobe_dir() / f"{atlas_name}_v{version}"),),
        # validate_mesh_matches_image_extents(atlas: BrainGlobeAtlas)
        (BrainGlobeAtlas(atlas_name),),
        # open_for_visual_check()
        (),
        # validate_checksum()
        (),
        # check_additional_references()
        (),
        # validate_atlas(atlas_name, version)
        (atlas_name, version),
    ]
    # all_validation_function_parameters.append(validation_function_parameters)

    for i, validation_function in enumerate(all_validation_functions):
        try:
            validation_function(*validation_function_parameters[i])
            successful_validations.append((atlas_name, validation_function))
        except AssertionError as error:
            failed_validations.append((atlas_name, validation_function, error))


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