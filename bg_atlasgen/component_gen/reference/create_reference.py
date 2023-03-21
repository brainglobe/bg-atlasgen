import imio
from bg_atlasapi import utils


def allen_adult_mouse_stp(temporary_directory, name, resolution, url):
    filename = temporary_directory / f"{name}_{resolution}.nrrd"
    utils.retrieve_over_http(url, filename)
    imio.load_any(filename)


def kim_dev_mouse_p56_lsfm(temporary_directory, name, resolution, url):
    filename = temporary_directory / f"{name}_{resolution}.nii.gz"
    utils.retrieve_over_http(url, filename)
    imio.load_any(filename)
