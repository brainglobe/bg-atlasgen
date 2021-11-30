__version__ = "0"


from magicclass import magicclass, set_design,field
from pathlib import Path
import webbrowser
from skimage import io
from os import listdir
import json

from bg_atlasgen.wrapup import wrapup_atlas_from_data
#atlas specific imports
from bg_atlasgen.atlas_scripts.mouse_e15_5 import download_atlas_files, create_meshes,create_mesh_dict, parse_structures

@magicclass(widget_type="mainwindow", name ="Brainglobe Atlas Generation",layout="vertical",popup_mode="below",close_on_run=True)
class atlasgen:
    working_dir = field(Path,name ="Directory to save files", options = {"mode":'d',"value" : Path.home()})
    atlas_name = field(str, name = "Enter name of atlas without any spaces",options = {"value" : "mouse_e15_5"})
    species = field(str, name = "Enter the species",options = {"value" : "Mus musculus"} )
    atlas_link = field(str, name = "Enter link to information about atlas",options = {"value" : "https://search.kg.ebrains.eu/instances/Dataset/51a81ae5-d821-437a-a6d5-9b1f963cfe9b"})
    atlas_file_url = field(str, name = "Enter link to the download the Atlas",options = {"value" : "https://search.kg.ebrains.eu/proxy/export?container=https://object.cscs.ch/v1/AUTH_4791e0a3b3de43e2840fe46d9dc2b334/ext-d000025_3Drecon-ADMBA-E15pt5_pub"})
    atlas_orientation = field(str, name = "Enter Orientation as a string as per bg-space format. <a href='https://github.com/brainglobe/bg-atlasapi'>More info</a>",options = {"value" : "las"})
    resolution = field(str, name = "Enter Resolution in micrometers separated by a comma (z,y,x) or (x,y,z)",options = {"value" : "(20, 16, 16)"})
    citation = field(str, name = "Enter details of published paper/preprint where atlas was first described",options = {"value" : "Young et al. 2021, https://doi.org/10.7554/eLife.61408"})
    root_id = field(int, name = "Enter ID of the root (base) brain region in the hierarchy of brain regions", options = {"min":0,"max" :10000000,"value":15564})
    atlas_file_url = field(str, name = "Enter link to the download the Atlas",options = {"value" : "https://search.kg.ebrains.eu/proxy/export?container=https://object.cscs.ch/v1/AUTH_4791e0a3b3de43e2840fe46d9dc2b334/ext-d000025_3Drecon-ADMBA-E15pt5_pub"})
    atlas_packager = field(str, name = "Enter your name and details (Atlas Packager)",options = {"value" : "Pradeep Rajasekhar, Walter and Eliza Hall Institute of Medical Research, Australia"})

    def Generate_Atlas(self):
        ATLAS_FILE_URL = self.atlas_file_url.value
        ATLAS_LINK = self.atlas_link.value
        RESOLUTION = self.resolution.value
        RESOLUTION=tuple(map(float, RESOLUTION.strip("()").replace(" ","").split(',')))
        ORIENTATION = self.atlas_orientation.value
        ATLAS_NAME = self.atlas_name.value
        ROOT_ID = self.root_id.value
        CITATION = self.citation.value
        SPECIES = self.species.value
        ATLAS_PACKAGER = self.atlas_packager.value
        working_dir = self.working_dir.value
        
               
        assert len(ORIENTATION)==3, "Orientation is not 3 characters, Got"+self.atlas_orientation.value
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

        print ("Done. Atlas generated at: ",output_filename)
        return output_filename


        
    @set_design(text="Click to go to Brainglobe Atlas API ")
    def info(self):
        webbrowser.open('https://github.com/brainglobe/bg-atlasapi') 
    
    @set_design(text="Click to go to Atlas Documentation (Placeholder) ")
    def doc(self):...
        #webbrowser.open('https://github.com/brainglobe/bg-atlasapi') 

if __name__ == "__main__":
    ui = atlasgen()
    ui.show(run=True)