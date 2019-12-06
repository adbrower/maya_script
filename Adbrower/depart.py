import sys
from pprint import pprint

import pymel.core as pm
import maya.cmds as mc

from adbrower import lprint
from adb_library.adb_utils.Pretty_DocString import doc_string
import adbrower


riggingPythonPathList = [
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_core',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_core/deformers',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_library',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_library/adb_modules',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_library/adb_utils',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_misc',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_misc/adb_icons',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_rigModules',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_rigModules/adb_biped',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_tools',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_tools/adb_pyQt',
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

import adb_markingMenu
adb_markingMenu.markingMenu()

mc.evalDeferred('import adb_markingMenu; adb_markingMenu.markingMenu()')

sys.stdout.write('Start up scripts set up \n')


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
