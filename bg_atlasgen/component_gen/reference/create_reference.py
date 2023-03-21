import imio
from bg_atlasapi import utils

from bg_atlasgen.utils.image import write_to_compressed_tiff


def allen_adult_mouse_stp(
    temporary_directory, name, resolution, url, orientation
):
    filename = temporary_directory / f"{name}_{resolution}.nrrd"
    utils.retrieve_over_http(url, filename)
    load_reorient_save(filename, orientation)


def kim_dev_mouse_p56_lsfm(
    temporary_directory, name, resolution, url, orientation
):
    filename = temporary_directory / f"{name}_{resolution}.nii.gz"
    utils.retrieve_over_http(url, filename)
    load_reorient_save(filename, orientation)


def load_reorient_save(filename, orientation, suffix=".tiff"):
    image = imio.load_any(filename)
    # TODO: reorient image
    write_to_compressed_tiff(
        filename.with_suffix("").with_suffix(suffix), image
    )
