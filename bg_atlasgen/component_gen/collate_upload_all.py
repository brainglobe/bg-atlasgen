import tempfile
from pathlib import Path

from bg_atlasapi import utils
from fancylog import fancylog

import bg_atlasgen as package_to_log
from bg_atlasgen.component_gen.reference import collate_references

TMPDIR_PREFIX = "bg_atlasgen_"
DEBUG = True

SAVE_DIR = Path.home() / "bg_atlasgen"


def collate_all(save_dir, debug=False):
    save_dir.mkdir(exist_ok=True, parents=True)
    fancylog.start_logging(
        save_dir,
        package_to_log,
        verbose=debug,
        timestamp=True,
    )
    utils.check_internet_connection()
    tmp_path = Path(tempfile.mkdtemp(prefix=TMPDIR_PREFIX))
    print(f"Created temporary directory: {tmp_path}")
    collate_references.create_all_references(tmp_path, debug=debug)


if __name__ == "__main__":
    collate_all(SAVE_DIR, debug=DEBUG)
