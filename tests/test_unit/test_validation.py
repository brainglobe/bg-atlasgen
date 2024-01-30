import os

import numpy as np
import pytest
from bg_atlasapi import BrainGlobeAtlas
from bg_atlasapi.config import get_brainglobe_dir

from bg_atlasgen.validate_atlases import (
    _assert_close,
    validate_atlas_files,
    validate_mesh_matches_image_extents,
    validate_mesh_structure_pairs,
)


@pytest.fixture
def atlas():
    """A fixture providing a low-res Allen Mouse atlas for testing.
    Tests assume this atlas is valid"""
    return BrainGlobeAtlas("allen_mouse_100um")


@pytest.fixture
def atlas_with_bad_reference_file():
    """A fixture providing an invalid version of Allen Mouse atlas for testing.
    The atlas will have a misnamed template file that won't be found by the API
    This fixture also does the clean-up after the test has run
    """
    good_name = get_brainglobe_dir() / "allen_mouse_100um_v1.2/reference.tiff"
    bad_name = (
        get_brainglobe_dir() / "allen_mouse_100um_v1.2/reference_bad.tiff"
    )
    os.rename(good_name, bad_name)
    yield BrainGlobeAtlas("allen_mouse_100um")
    os.rename(bad_name, good_name)


def test_validate_mesh_matches_image_extents(atlas):
    assert validate_mesh_matches_image_extents(atlas)


def test_validate_mesh_matches_image_extents_negative(mocker, atlas):
    flipped_annotation_image = np.transpose(atlas.annotation)
    mocker.patch(
        "bg_atlasapi.BrainGlobeAtlas.annotation",
        new_callable=mocker.PropertyMock,
        return_value=flipped_annotation_image,
    )
    with pytest.raises(
        AssertionError, match="differ by more than 10 times pixel size"
    ):
        validate_mesh_matches_image_extents(atlas)


def test_valid_atlas_files(atlas):
    assert validate_atlas_files(atlas)


def test_invalid_atlas_path(atlas_with_bad_reference_file):
    with pytest.raises(AssertionError, match="Expected file not found"):
        validate_atlas_files(atlas_with_bad_reference_file)


def test_assert_close():
    assert _assert_close(99.5, 8, 10)


def test_assert_close_negative():
    with pytest.raises(
        AssertionError, match="differ by more than 10 times pixel size"
    ):
        _assert_close(99.5, 30, 2)


def test_validate_mesh_structure_pairs_no_obj(atlas):
    """
    Tests if validate_mesh_structure_pairs function raises an error,
    when there is at least one structure in the atlas that doesn't have
    a corresponding obj file.

    True for: allen_mouse_100um (structure 545 doesn't have an obj file)
    False for: admba_3d_e11_5_mouse_16um (it has all pairs)

    """
    with pytest.raises(
        AssertionError,
        match="Structures with ID \[.*\] are in the atlas, but don't have a corresponding mesh file",
    ):
        validate_mesh_structure_pairs(atlas)


def test_validate_mesh_structure_pairs_not_in_atlas(atlas):
    """
        Tests if validate_mesh_structure_pairs function raises an error,
        when there is at least one orphan obj file (doesn't have a corresponding structure in the atlas)
    """
    with pytest.raises(
        AssertionError,
        match="Structures with IDs \[.*\] have a mesh file, but are not accessible through the atlas",
    ):
        validate_mesh_structure_pairs(atlas)