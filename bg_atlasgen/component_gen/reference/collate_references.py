import logging

from bg_atlasgen.component_gen.reference import create_reference
from bg_atlasgen.utils.config import load_config


def create_all_references(tmp_path, atlas_template, debug=False):
    reference_data = load_config("references.yaml")
    for reference in reference_data:
        logging.info(f"Creating reference images for: {reference}")
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
                atlas_template,
            )
        else:
            for resolution in resolutions:
                run_reference_generation(
                    tmp_path,
                    reference,
                    resolution,
                    resolutions[resolution],
                    reference_data[reference]["orientation"],
                    atlas_template,
                )


def run_reference_generation(
    tmp_path, reference, resolution, url, orientation, atlas_template
):
    logging.info(
        f"Creating reference: {reference} at resolution: {resolution}"
    )
    function = getattr(create_reference, reference)
    result = function(
        tmp_path, reference, resolution, url, orientation, atlas_template
    )
    return result


if __name__ == "__main__":
    create_all_references()
