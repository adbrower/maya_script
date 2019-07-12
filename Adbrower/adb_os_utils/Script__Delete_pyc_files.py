
import os
from datetime import datetime
import shutil
import getpass

userName = getpass.getuser()         
path_window = 'C:/Users/'+ userName + '/AppData/Roaming'
path_linux = '/home/'+ userName 
folder_name ='.config/adb_Setup/pyc_scripts'

def move_pyc(source_path):
    def finalPath():
        if not os.path.exists(path_linux):
            pass
        else:
            return path_linux   
       
        if not os.path.exists(path_window):
            pass              
        else:
            return path_window      
    final_path = finalPath() 

    os.chdir(final_path)        
    try:
        os.makedirs(folder_name)        
    except :
        pass          
        
    if os.path.exists(final_path + '/' + folder_name + '/'): 
        pass
    else:
        os.chdir(final_path + '/' +  folder_name)
   

    os.chdir(source_path)
    for f in os.listdir(os.getcwd()):

        file_name, file_ext = (os.path.splitext(f))
        # print (file_name), (file_ext)

        if file_ext == ('.pyc'):
            shutil.move((source_path+'/'+file_name+file_ext), final_path + '/' +  folder_name )
        else:
            pass

    # ---------------------
    # Delete
    # ---------------------

    os.chdir(final_path + '/' +  folder_name)
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

move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/Adbrower')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/Adbrower/adb_rig')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/Adbrower/adb_tools')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/Adbrower/adb_utils')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/Adbrower/adb_pyQt')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/Adbrower/adb_utils/adb_script_utils')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/Adbrower/adb_utils/rig_utils')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/Adbrower/adb_utils/deformers')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/Adbrower/adb_os_utils')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python/archives')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/python')

## git folder
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/git_projects/maya_script/Adbrower')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/git_projects/maya_script/Adbrower/adb_rig')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/git_projects/maya_script/Adbrower/adb_tools')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/git_projects/maya_script/Adbrower/adb_utils')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/git_projects/maya_script/Adbrower/adb_pyQt')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/git_projects/maya_script/Adbrower/adb_utils/adb_script_utils')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/git_projects/maya_script/Adbrower/adb_utils/rig_utils')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/git_projects/maya_script/Adbrower/adb_utils/deformers')
move_pyc('C:/Users/Audrey/Google Drive/[SCRIPT]/git_projects/maya_script/Adbrower/adb_os_utils')

