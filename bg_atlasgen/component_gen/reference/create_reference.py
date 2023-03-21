import urllib.request

import imio


def allen_adult_mouse_stp(temporary_directory, name, resolution, url):
    filename = temporary_directory / f"{name}_{resolution}.nrrd"
    urllib.request.urlretrieve(url, filename)
    return imio.load_any(filename)


def kim_dev_mouse_p56_lsfm(temporary_directory, name, resolution, url):
    pass
