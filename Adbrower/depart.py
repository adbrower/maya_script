from adbrower import lprint
from CollDict import colordic
from adb_utils.adb_script_utils.Pretty_DocString import doc_string
import adb_rig
import adb_utils
import CollDict
import adbrower
import ShapesLibrary as sl
import sys
import pymel.core as pm
import maya.cmds as mc
from pprint import pprint

riggingPythonPathList = [
    "C:/Users/Audrey/Google Drive/[SCRIPT]/python",
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_os_utils',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_rig',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_tools',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_utils',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_utils/adb_script_utils',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_utils/deformers',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_utils/rig_utils',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Exterior_scripts',
]

for riggingPythonPath in riggingPythonPathList:
    if riggingPythonPath not in sys.path:
        sys.path.append(riggingPythonPath)
    else:
        # print(riggingPythonPath + ' is already loaded')
        pass


# -----------------------------------
# IMPORT CUSTOM MODULES
# -----------------------------------


adb = adbrower.Adbrower()


# -----------------------------------
# Marking Menu
# -----------------------------------

# import adb_markingMenu
# reload(adb_markingMenu)
# adb_markingMenu.markingMenu()

# mc.evalDeferred('import adb_markingMenu; adb_markingMenu.markingMenu()')

# sys.stdout.write('Start up scripts set up \n')


# -----------------------------------
# RELOAD SCRIPTS
# -----------------------------------


# import sys
# to_delete = set()
# for mod_name in sys.modules:
#     if 'adb' in mod_name:
#         print mod_name
#         to_delete.add(mod_name)
#     if 'Adb' in mod_name:
#         print mod_name
#         to_delete.add(mod_name)
        
# for mod_name in to_delete:
#     if sys.modules[mod_name] is None:
#         sys.modules.pop(mod_name)
#     else:
#         del sys.modules[mod_name]
        
# sys.stdout.write('\nModule Reload \n')
