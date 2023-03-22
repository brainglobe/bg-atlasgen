import logging

import bg_space as bg
import imio
from bg_atlasapi import utils

from bg_atlasgen.utils.image import write_to_compressed_tiff


def allen_adult_mouse_stp(
    temporary_directory, name, resolution, url, orientation, atlas_template
):
    filename = temporary_directory / f"{name}_{resolution}.nrrd"
    download_and_resave_image(
        url, filename, orientation, atlas_template["ATLAS_ORIENTATION"]
    )


def kim_dev_mouse_p56_lsfm(
    temporary_directory, name, resolution, url, orientation, atlas_template
):
    filename = temporary_directory / f"{name}_{resolution}.nii.gz"
    download_and_resave_image(
        url, filename, orientation, atlas_template["ATLAS_ORIENTATION"]
    )


def download_and_resave_image(url, filename, orientation, final_orientation):
    logging.debug(f"Downloading {url} to {filename}")
    utils.retrieve_over_http(url, filename)
    load_reorient_save(filename, orientation, final_orientation)


def load_reorient_save(
    filename, orientation, final_orientation, suffix=".tiff"
):
    logging.debug(f"Loading {filename}")
    image = imio.load_any(filename)
    logging.debug(
        f"Reorienting image from {orientation} to {final_orientation}"
    )
    image = bg.map_stack_to(orientation, final_orientation, image)
    output_filename = filename.with_suffix("").with_suffix(suffix)
    logging.debug(f"Saving image to {output_filename}")
    write_to_compressed_tiff(output_filename, image)
