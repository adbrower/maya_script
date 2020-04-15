import sys

MAYA_PLUG_IN_PATH = os.environ["MAYA_PLUG_IN_PATH"].split(';')

riggingPythonPathList = [
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/plug-ins',
    'C:/Users/Audrey/Google Drive/[SCRIPT]/python/backUp/plug-ins',
]

for riggingPythonPath in riggingPythonPathList:
    if riggingPythonPath not in MAYA_PLUG_IN_PATH:
        MAYA_PLUG_IN_PATH.insert(0, riggingPythonPath)
    else:
        pass
os.environ["MAYA_PLUG_IN_PATH"] = ';'.join(MAYA_PLUG_IN_PATH)

