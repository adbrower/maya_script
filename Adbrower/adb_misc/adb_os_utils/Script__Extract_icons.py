import maya.cmds as cmds

ICONS_FOLDER = 'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_misc/adb_icons/'

for item in cmds.resourceManager(nf='deleteActive.png'):
    cmds.resourceManager(s=(item, "{}{}".format(ICONS_FOLDER, item)))
