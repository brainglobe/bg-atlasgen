__version__ = "0"

from magicgui.widgets import ComboBox
from magicclass import magicclass, set_design,field
from pathlib import Path
import webbrowser
from skimage import io
import sys, glob, os
from importlib import import_module
import glob 
import os 
import bg_atlasgen.atlas_scripts

def gen_atlas_list():
    """Goes through the atlas scripts folder in bg-atlas and finds atlas generation scripts
       Looks for files with .py extension
       Ignores init and template (can be modified in the ignore_files list) 

    Returns:
        [list]: List of atlas generation scripts
    """    
    #add any files to ignore in the atlas scripts folder to this list
    ignore_files = ["__init__", "template"]
    atlas_scripts_path = os.path.dirname(bg_atlasgen.atlas_scripts.__file__)
    atlas_list = []
    for file in glob.glob(atlas_scripts_path+os.sep+"/*.py"):
        if (not(any(x in file for x in ignore_files))):
            atlas_list.append(os.path.splitext(os.path.basename(file))[0])
    return atlas_list



@magicclass(widget_type="mainwindow", name ="Brainglobe Atlas Generation",layout="vertical",popup_mode="below",close_on_run=True)
class atlasgen:
    #get list of atlases
    atlas_list = gen_atlas_list()
    #User input of parameters   
    working_dir = field(Path,name ="Directory to save files", options = {"mode":'d',"value" : Path.home()})
    atlas_choice = field(widget_type = ComboBox,name ="Choose Atlas generation script", options = {"choices" : atlas_list})
    atlas_name = field(str, name = "Enter name of atlas without any spaces",options = {"value" : "mouse_e15_5"})
    species = field(str, name = "Enter the species",options = {"value" : "Mus musculus"} )
    atlas_link = field(str, name = "Enter link to information about atlas",options = {"value" : "https://search.kg.ebrains.eu/instances/Dataset/51a81ae5-d821-437a-a6d5-9b1f963cfe9b"})
    atlas_file_location = field(str, name = "Enter link to the download the Atlas or a local directory with unzipped atlas files",options = {"value" : "https://data.kg.ebrains.eu/zip?container=https://object.cscs.ch/v1/AUTH_4791e0a3b3de43e2840fe46d9dc2b334/ext-d000025_3Drecon-ADMBA-E15pt5_pub"})
    atlas_orientation = field(str, name = "Enter Orientation as a string as per bg-space format. <a href='https://github.com/brainglobe/bg-atlasapi'>More info</a>",options = {"value" : "las"})
    resolution = field(str, name = "Enter Resolution in micrometers separated by a comma (z,y,x) or (x,y,z)",options = {"value" : "(20, 16, 16)"})
    citation = field(str, name = "Enter details of published paper/preprint where atlas was first described",options = {"value" : "Young et al. 2021, https://doi.org/10.7554/eLife.61408"})
    root_id = field(int, name = "Enter ID of the root (base) brain region in the hierarchy of brain regions", options = {"min":0,"max" :10000000,"value":15564})
    atlas_packager = field(str, name = "Enter your name and details (Atlas Packager)",options = {"value" : "Pradeep Rajasekhar, Walter and Eliza Hall Institute of Medical Research, Australia"})

    def Generate_Atlas(self):
        
        #Dynamic import of atlas module
        #module as a string based on user choice of atlas
        mod = "bg_atlasgen.atlas_scripts."+self.atlas_choice.value
        #get the create_atlas function from the atlas_generation script
        create_atlas = getattr(import_module(mod), 'create_atlas')

        ATLAS_FILE_URL = self.atlas_file_location.value
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

        create_atlas(ATLAS_NAME,
                     SPECIES,
                     ATLAS_LINK,
                     ATLAS_FILE_URL,
                     ORIENTATION,
                     RESOLUTION,
                     CITATION,
                     ROOT_ID,
                     ATLAS_PACKAGER,
                     working_dir)
        
        print("Atlas generated")              
        return 


        
    @set_design(text="Click to go to Brainglobe Atlas API ")
    def info(self):
        webbrowser.open('https://github.com/brainglobe/bg-atlasapi') 
    
    @set_design(text="Click to go to Atlas Documentation")
    def doc(self):
        webbrowser.open('https://docs.brainglobe.info/bg-atlasapi/adding-a-new-atlas') 


if __name__ == "__main__":
    ui = atlasgen()
    ui.show(run=True)