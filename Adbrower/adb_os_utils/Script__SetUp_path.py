import getpass
import os
import ConfigParser

# path = '/on/work/adbrower/.config'


def createIniFile():
    userName = getpass.getuser()     
    path_window = 'C:/Users/'+ userName + '/AppData/Roaming'
    path_linux = '/on/work/'+ userName + '/Desktop/'
    folder_name ='.config/adb_Setup'
    file_name = 'test_config.ini'


    def finalPath():
        if not os.path.exists(path_linux):
            # print('path linux does NOT extist')
            pass
        else:
            # print('path linux does extist')   
            return path_linux   
       
        if not os.path.exists(path_window):
            # print('path window does NOT extist') 
            pass              
        else:
            # print('path window does extist')
            return path_window      

    final_path = finalPath() 

    os.chdir(final_path)        
    try:
        os.makedirs(folder_name)        
    except :
        pass          
        
    if os.path.exists(final_path + '/' + folder_name + '/' + file_name): 
        # print ('file exist')
        pass
    else:
        os.chdir(final_path + '/' +  folder_name)
        # print(os.getcwd())

       
    file_ini = open(file_name, 'w+')
    file_ini.write('[general]\n')
    file_ini.write("source_mesh_data: 'simon'\n")
    file_ini.write("target_mesh_data: 'audrey'\n")
    file_ini.write("search_data: @non\n")
    file_ini.write("replace_data: @non\n")
    file_ini.write("target_jnts_data: @non\n")
    
    file_ini.close()
    
    return file_ini 


createIniFile()