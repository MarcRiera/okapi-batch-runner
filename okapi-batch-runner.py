import subprocess
import sys
import os
import glob
import configparser
import xml.etree.ElementTree as ET
from pathlib import Path

# Function for selection lists
def select_item(welcome_text, items):
    print(welcome_text+"\n")
    for i, item in enumerate(items):
        print('{}. {}'.format(i + 1, item))
    try:
        selected = input("\nSelect an option by typing its number (1-{}): ".format(len(items)))
        result = items[int(selected) - 1]
        return result
    except KeyboardInterrupt:
        print('User requested to exit')
        exit()
    except ValueError:
        print('Error! Please enter only one number')
        exit()
    except IndexError:
        print('Error! Please enter one number between 1-{}'.format(len(items)))
        exit()

# Function to get the correct filter for a file
def get_filter(path):
    extension = os.path.splitext(path)[1][1:]
    if (extension == ""):
        return extension
    else:
        if (extension in project_config["Filters"]):
            return project_config["Filters"][extension]
        else:
            if (extension in config["Filters"]):
                return config["Filters"][extension]
            else:
                return ""


# Load config
config = configparser.ConfigParser()
config.read(os.path.join(sys.path[0],"config.ini"))
rainbow = config["Options"]["rainbow_exec"]

# Get work directories (ignore 0, which is this Python script)
work_directories = sys.argv[1:]

# Load project
list_projects = os.listdir(os.path.join(sys.path[0],"projects"))
project_dir = os.path.join(sys.path[0],"projects",select_item("Available projects:",list_projects))
project = os.path.join(project_dir,"project.rnb")

# Load project config
project_config = configparser.ConfigParser()
project_config.read(os.path.join(project_dir,"project.ini"))

# Load pipeline
list_pipelines = [os.path.basename(x) for x in glob.glob(os.path.join(sys.path[0],"projects",project_dir,"*.pln"))]
pipeline = os.path.join(project_dir,select_item("Available pipelines:",list_pipelines))

# Build list of files to be processed
files = []
files_root = os.getcwd()

for directory in work_directories:
    if any(Path(directory).rglob('*.*')):
        for translationfile in Path(directory).rglob('*.*'):
            if (translationfile.is_file()):
                filter = get_filter(translationfile)
                if (filter != ""):
                    relpath = os.path.relpath(translationfile,files_root)
                    files.append((relpath,filter))

# Parse project
project_tree = ET.parse(project)
project_tree_root = project_tree.getroot()
fileset = project_tree_root.find("./fileSet[@id='1']")
fileset_root = project_tree_root.find("./fileSet[@id='1']/root")
parameters = project_tree_root.find("./parametersFolder")

# Set the parameters folder to the one defined in the config
fileset_root.set("useCustom","1")
fileset_root.text = config["Options"]["custom_filters_folder"]

# Set the root of the first fileset to the working folder
fileset_root.set("useCustom","1")
fileset_root.text = files_root

# Add files to first fileset
for item in files:
    new=ET.Element("fi",attrib={"fs":item[1]})
    new.text=str(item[0])
    fileset.append(new)

# Write temporary custom project file for Okapi Rainbow
project_tree.write("temp_project.rnb",encoding="UTF-8",xml_declaration=True)

# Run Okapi Rainbow with the temporary project and the selected pipeline
subprocess.run([rainbow,"-p","temp_project.rnb","-pln",pipeline,"-np"])

# Remove temporary project file after executing the pipeline
os.remove("temp_project.rnb") 
