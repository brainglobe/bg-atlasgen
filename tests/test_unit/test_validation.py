from pathlib import Path

import pytest
from bg_atlasapi import BrainGlobeAtlas
from bg_atlasapi.config import get_brainglobe_dir

from bg_atlasgen.validate_atlases import validate_atlas_files


def test_valid_atlas_files():
    _ = BrainGlobeAtlas("allen_mouse_100um")
    atlas_path = Path(get_brainglobe_dir()) / "allen_mouse_100um_v1.2"
    assert validate_atlas_files(atlas_path)


def test_invalid_atlas_path():
    atlas_path = Path.home()
    with pytest.raises(AssertionError, match="Expected file not found"):
        validate_atlas_files(atlas_path)
