import getpass
import os
import shutil

USERNAME = getpass.getuser()
PATH_WINDOW = 'C:/Users/'+ USERNAME + '/AppData/Roaming'
PATH_LINUX = '/home/'+ USERNAME
FOLDER_NAME = '.config/adb_Setup/pyc_scripts'


def move_pyc(source_path):
    def finalPath():
        if not os.path.exists(PATH_LINUX):
            pass
        else:
            return PATH_LINUX
        if not os.path.exists(PATH_WINDOW):
            pass
        else:
            return PATH_WINDOW
    final_path = finalPath()

    os.chdir(final_path)
    try:
        os.makedirs(FOLDER_NAME)
    except:
        pass

    if os.path.exists(final_path + '/' + FOLDER_NAME + '/'):
        pass
    else:
        os.chdir(final_path + '/' +  FOLDER_NAME)


    os.chdir(source_path)
    for file in os.listdir(os.getcwd()):
        file_name, file_ext = (os.path.splitext(file))
        # print (file_name), (file_ext)
        if file_ext == ('.pyc'):
            shutil.move((source_path+'/'+file_name+file_ext), final_path + '/' +  FOLDER_NAME )
        else:
            pass

    # ---------------------
    # Delete
    # ---------------------

    os.chdir(final_path + '/' +  FOLDER_NAME)
    for f in os.listdir(os.getcwd()):

        file_name, file_ext = (os.path.splitext(f))
        # print (file_name), (file_ext)

        if file_ext == ('.pyc'):
            os.remove(f)
        else:
            pass


# ## Work Clean Up
# #----------------------

# move_pyc('/home/adeschamps/maya/scripts/python/Adbrower')
# move_pyc('/home/adeschamps/maya/scripts/python/Adbrower/adb_rig')
# move_pyc('/home/adeschamps/maya/scripts/python/Adbrower/adb_tools')
# move_pyc('/home/adeschamps/maya/scripts/python/Adbrower/adb_utils')
# move_pyc('/home/adeschamps/maya/scripts/python/Adbrower/adb_utils/adb_script_utils')
# move_pyc('/home/adeschamps/maya/scripts/python/Adbrower/adb_utils/rig_utils')
# move_pyc('/home/adeschamps/maya/scripts/python/Adbrower/adb_utils/deformers')
# move_pyc('/home/adeschamps/maya/scripts/python/Archives')
# move_pyc('/home/adeschamps/maya/scripts/python')


## Home Clean Up
##----------------------

move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_rig')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_tools')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_utils')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_pyQt')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_utils/adb_script_utils')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_utils/rig_utils')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_utils/deformers')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_os_utils')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script//archives')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/')
