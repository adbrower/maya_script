import sys
import pymel.core as pm
import maya.cmds as mc

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


def runThis():

  import adb_markingMenu
  adb_markingMenu.markingMenu()
  pm.layout('ShelfLayout', h=100, e=1)

  # import audrey_toolbox_V03
 

mc.evalDeferred(runThis) 









