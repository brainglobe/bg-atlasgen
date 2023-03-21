from importlib.resources import open_text

import yaml

from bg_atlasgen.component_gen import config
from bg_atlasgen.component_gen.reference import create_reference


def create_all_references(tmp_path, debug=False):
    reference_data = load_all_reference_info()
    for reference in reference_data:
        print(f"Creating reference images for: {reference}")
        resolutions = reference_data[reference]["resolution"]

        if debug:
            # For speed, only run with one resolution
            resolution = max(resolutions)
            run_reference_generation(
                tmp_path,
                reference,
                resolution,
                resolutions[resolution],
                reference_data[reference]["orientation"],
            )
        else:
            for resolution in resolutions:
                run_reference_generation(
                    tmp_path,
                    reference,
                    resolution,
                    resolutions[resolution],
                    reference_data[reference]["orientation"],
                )


def load_all_reference_info():
    with open_text(config, "references.yaml") as file:
        data = yaml.safe_load(file)
        return data


def run_reference_generation(
    tmp_path, reference, resolution, url, orientation
):
    print(f"Creating reference: {reference} at resolution: {resolution}")
    function = getattr(create_reference, reference)
    result = function(tmp_path, reference, resolution, url, orientation)
    return result


if __name__ == "__main__":
    create_all_references()
