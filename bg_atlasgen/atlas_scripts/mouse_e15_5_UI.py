__version__ = "0"

import json
import time
import zipfile

from os import listdir
import pandas as pd
import numpy as np
import multiprocessing as mp

from rich.progress import track
from pathlib import Path

from bg_atlasapi import utils
from bg_atlasgen.mesh_utils import create_region_mesh, Region
from bg_atlasgen.wrapup import wrapup_atlas_from_data
from bg_atlasapi.structure_tree_util import get_structures_tree

from skimage import io
from magicgui import magicgui

PARALLEL = True


def download_atlas_files(download_dir_path, atlas_file_url,ATLAS_NAME):
    utils.check_internet_connection()

    atlas_files_dir = download_dir_path / ATLAS_NAME
    download_name=ATLAS_NAME+"_atlas.zip"
    destination_path = download_dir_path / download_name
    utils.retrieve_over_http(atlas_file_url, destination_path)

    with zipfile.ZipFile(destination_path, "r") as zip_ref:
        zip_ref.extractall(atlas_files_dir)

    return atlas_files_dir


def parse_structures(structures_file, root_id):
    df = pd.read_csv(structures_file)
    df = df.rename(columns={"Parent": "parent_structure_id"})
    df = df.rename(columns={"Region": "id"})
    df = df.rename(columns={"RegionName": "name"})
    df = df.rename(columns={"RegionAbbr": "acronym"})
    df = df.drop(columns=["Level"])
    no_items=df.shape[0]
    rgb_list=[[np.random.randint(0, 255),np.random.randint(0, 255),np.random.randint(0, 255)] for i in range(no_items)]

    #rgb_list=list(color for color in islice(combinations(range(200,255),3),no_items))
    #list(color for color in islice(product(range(200,255),repeat=3),no_items))

    rgb_list=pd.DataFrame(rgb_list,columns=['red','green','blue'])

    df["rgb_triplet"] = rgb_list.apply(lambda x: [x.red.item(), x.green.item(), x.blue.item()], axis=1)
    df["structure_id_path"] = df.apply(lambda x: [x.id], axis=1)
    structures = df.to_dict("records")
    structures = create_structure_hierarchy(structures, df, root_id)
    return structures


def create_structure_hierarchy(structures, df, root_id):
    for structure in structures:
        if structure["id"] != root_id:
            parent_id = structure["parent_structure_id"]
            while True:
                structure["structure_id_path"] = [parent_id] + structure[
                    "structure_id_path"
                ]
                if parent_id != root_id:
                    parent_id = int(
                        df[df["id"] == parent_id]["parent_structure_id"]
                    )
                else:
                    break
        else:
            structure["name"] = "root"
            structure["acronym"] = "root"

        del structure["parent_structure_id"]

    return structures


def create_meshes(download_dir_path, structures, annotated_volume, root_id):
    meshes_dir_path = download_dir_path / "meshes"
    meshes_dir_path.mkdir(exist_ok=True)

    tree = get_structures_tree(structures)
    
    labels = np.unique(annotated_volume).astype(np.int32)

    for key, node in tree.nodes.items():
        if key in labels:
            is_label = True
        else:
            is_label = False
        node.data = Region(is_label)
    
    # Mesh creation
    closing_n_iters = 2
    start = time.time()
    if PARALLEL:

        pool = mp.Pool(mp.cpu_count() - 2)

        try:
            pool.map(
                create_region_mesh,
                [
                    (
                        meshes_dir_path,
                        node,
                        tree,
                        labels,
                        annotated_volume,
                        root_id,
                        closing_n_iters,
                    )
                    for node in tree.nodes.values()
                ],
            )
        except mp.pool.MaybeEncodingError:
            pass
    else:
        for node in track(
            tree.nodes.values(),
            total=tree.size(),
            description="Creating meshes",
        ):
            create_region_mesh(
                (
                    meshes_dir_path,
                    node,
                    tree,
                    labels,
                    annotated_volume,
                    root_id,
                    closing_n_iters,
                )
            )

    print(
        "Finished mesh extraction in: ",
        round((time.time() - start) / 60, 2),
        " minutes",
    )
    return meshes_dir_path


def create_mesh_dict(structures, meshes_dir_path):
    meshes_dict = dict()
    structures_with_mesh = []
    for s in structures:
        # Check if a mesh was created
        mesh_path = meshes_dir_path / f'{s["id"]}.obj'
        if not mesh_path.exists():
            print(f"No mesh file exists for: {s}, ignoring it")
            continue
        else:
            # Check that the mesh actually exists (i.e. not empty)
            if mesh_path.stat().st_size < 512:
                print(f"obj file for {s} is too small, ignoring it.")
                continue

        structures_with_mesh.append(s)
        meshes_dict[s["id"]] = mesh_path

    print(
        f"In the end, {len(structures_with_mesh)} structures with mesh are kept"
    )
    return meshes_dict, structures_with_mesh

#Decorating using magicgui decorator so an interface can be generated
#Can we make it a single function instead of 2: one for UI and one for atlas??
@magicgui( header=dict(widget_type="Label",
                    label=f"<h3>Generate Brainglobe Atlas (Developmental Mouse Atlas)</h3>"),
            working_dir=dict(mode= 'd',value=Path.home(),label="Directory to save files"),
            ATLAS_NAME=dict(label="Enter name of atlas without any spaces"),
            ATLAS_LINK=dict(label="Enter link to information about atlas"),
            ORIENTATION=dict(label='Enter Orientation as a string as per bg-space format. <a href="https://github.com/brainglobe/bg-atlasapi">More info</a>'),
            RESOLUTION=dict(label='Enter Resolution in micrometers separated by a comma z,y,x or x,y,z'),
            CITATION=dict(label='Enter details of published paper/preprint where atlas was first described'),
            ROOT_ID = dict(label='Enter ID of the root (base) brain region in the hierarchy of brain regions',max=1000000000),
            ATLAS_FILE_URL = dict(label='Enter link to the download the Atlas'),
            ATLAS_PACKAGER = dict(label='Enter your name and details'),
            info=dict(widget_type="Label",
                label=f'<a href="https://github.com/brainglobe/bg-atlasapi">Brainglobe Atlas API</a>'),
            doc=dict(widget_type="Label",
            label=f'<a href="https://github.com">Documentation</a>'),
            call_button="Generate Atlas") #call_button="Generate Atlas"
def create_atlas(header, 
                working_dir:Path,
                ATLAS_NAME:str,
                SPECIES:str,
                ATLAS_LINK:str,
                CITATION:str,
                ORIENTATION:str,
                RESOLUTION:str,
                ROOT_ID:int,
                ATLAS_FILE_URL:str,
                ATLAS_PACKAGER:str,
                doc,
                info
                ):
    #Without magicgui, enter it as follows
    #ATLAS_NAME = "mouse_e15_5"
    #SPECIES = "Mus musculus"
    #ATLAS_LINK = "https://search.kg.ebrains.eu/instances/Dataset/51a81ae5-d821-437a-a6d5-9b1f963cfe9b"
    #CITATION = (
    #    "Young et al. 2021, https://doi.org/10.7554/eLife.61408"
    #)
    #ORIENTATION = "las"
    #RESOLUTION = (20, 16, 16)
    #ROOT_ID = 15564
    #ATLAS_FILE_URL = (
    #    "https://search.kg.ebrains.eu/proxy/export?container=https://object.cscs.ch/"
    #    "v1/AUTH_4791e0a3b3de43e2840fe46d9dc2b334/ext-d000025_3Drecon-ADMBA-E15pt5_pub"
    #)
    #ATLAS_PACKAGER = "Pradeep Rajasekhar, Walter and Eliza Hall Institute of Medical Research, Australia"
    
    #Make sure the orientation has three letters
    RESOLUTION=tuple(map(float, RESOLUTION.strip().split(',')))
    assert len(ORIENTATION)==3, "Orientation is not 3 characters, Got"+ORIENTATION
    assert len(RESOLUTION)==3, "Resolution is not correct, Got "+RESOLUTION
    assert ATLAS_FILE_URL, "No download link provided for atlas in ATLAS_FILE_URL"

    # Generated atlas path:
    working_dir = working_dir / "brainglobe_workingdir" / ATLAS_NAME
    working_dir.mkdir(exist_ok=True, parents=True)
    
    download_dir_path = working_dir / "downloads"
    download_dir_path.mkdir(exist_ok=True)

    # Download atlas files from link provided
    print("Downloading atlas from link: ",ATLAS_FILE_URL)
    atlas_files_dir = download_atlas_files(download_dir_path, ATLAS_FILE_URL,ATLAS_NAME)
    ## Load files
    
    structures_file = atlas_files_dir / ([f for f in listdir(atlas_files_dir) if "region_ids_ADMBA" in f][0])
    
    reference_file = atlas_files_dir / ([f for f in listdir(atlas_files_dir) if "atlasVolume.mhd" in f][0])

    annotations_file = atlas_files_dir / ([f for f in listdir(atlas_files_dir) if "annotation.mhd" in f][0])
    #segments_file = atlas_files_dir / "Segments.csv"
    
    annotated_volume = io.imread(annotations_file)
    template_volume = io.imread(reference_file)

    ## Parse structure metadata
    structures = parse_structures(structures_file, ROOT_ID)

    # save regions list json:
    with open(download_dir_path / "structures.json", "w") as f:
        json.dump(structures, f)


    # Create meshes:
    print(f"Saving atlas data at {download_dir_path}")
    meshes_dir_path = create_meshes(
        download_dir_path, structures, annotated_volume, ROOT_ID
    )

    meshes_dict, structures_with_mesh = create_mesh_dict(
        structures, meshes_dir_path
    )

    # Wrap up, compress, and remove file:
    print("Finalising atlas")
    output_filename = wrapup_atlas_from_data(
        atlas_name=ATLAS_NAME,
        atlas_minor_version=__version__,
        citation=CITATION,
        atlas_link=ATLAS_LINK,
        species=SPECIES,
        resolution=RESOLUTION,
        orientation=ORIENTATION,
        root_id=ROOT_ID,
        reference_stack=template_volume,
        annotation_stack=annotated_volume,
        structures_list=structures_with_mesh,
        meshes_dict=meshes_dict,
        working_dir=working_dir,
        atlas_packager=ATLAS_PACKAGER,
        hemispheres_stack=None,
        cleanup_files=False,
        compress=True,
        scale_meshes=True
    )

    return output_filename



if __name__ == "__main__":
    create_atlas.show(run=True)
