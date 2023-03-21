from tifffile import imwrite


def write_to_compressed_tiff(output_file, array_data, compression="deflate"):
    imwrite(output_file, array_data, compression=compression)
