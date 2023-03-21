import tempfile
from pathlib import Path

from bg_atlasgen.component_gen.reference import collate_references

TMPDIR_PREFIX = "bg_atlasgen_"
DEBUG = True


def collate_all(debug=False):
    tmp_path = Path(tempfile.mkdtemp(prefix=TMPDIR_PREFIX))
    print(f"Created temporary directory: {tmp_path}")
    collate_references.create_all_references(tmp_path, debug=debug)


if __name__ == "__main__":
    collate_all(DEBUG)
