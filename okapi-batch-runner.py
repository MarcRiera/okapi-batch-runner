import subprocess
import sys
import os
import re
import io
import glob
import configparser
from pathlib import Path

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


config = configparser.ConfigParser()
config.read(os.path.join(sys.path[0],"config.ini"))
rainbow = config["Options"]["rainbow_exec"]


list_projects = os.listdir(os.path.join(sys.path[0],"projects"))
project_folder = os.path.join(sys.path[0],"projects",select_item("Available projects:",list_projects))
project = os.path.join(project_folder,"project.rnb")

list_pipelines = [os.path.basename(x) for x in glob.glob(os.path.join(sys.path[0],"projects",project_folder,"*.pln"))]
pipeline = os.path.join(project_folder,select_item("Available pipelines:",list_pipelines))

subprocess.run([rainbow,"-p",project,"-pln",pipeline,"-np"])
