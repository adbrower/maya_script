import shutil
import sys
from datetime import datetime
import os
import time
from collections import OrderedDict


def delete_folder(folder_name, source_path):
    """ Deletes all 'mod' forlders in the source_path"""

    all_new_paths = []
    paths_with_mod = []
    os.chdir(source_path)

    for folder in os.listdir(os.getcwd()):
        ori_path = os.getcwd() + '/' + folder + '/'
        new_path = ori_path + folder_name
        all_new_paths.append(new_path)

    ## Find all path with mod folders         
    paths_with_mod = [x for x in all_new_paths if os.path.exists(x)]

    ## Removes all the mod folders
    for _path in paths_with_mod:
        shutil.rmtree(_path)
        
    sys.stdout.write('All \'{}\' folders has been deleted in : {}\n'.format(folder_name,source_path))
        



#==================================================================================



def all_assets_in_path(source_path):
    """find all asset in path_with_files"""

    assets_list = [x for x in os.listdir(source_path)]
    return assets_list
    

def find_scene_data(source_path, type_order, _print = False, rig_srig = None, rig_name = None):
    os.chdir(source_path)

    path_with_files = []
    path_with_noFiles = []
    all_scenes = []
    scene_path_dic = {}

    timeData_scenes = []
    size_scenes = []

    for dirpath, dirnames, filenames, in os.walk(source_path):
        if dirnames == []:
            path_with_files.append(dirpath)

    ## Find path with no Maya scene
    for path in path_with_files:    
        for dirpath, dirnames, filenames, in os.walk(path):
            if filenames == []:
                path_with_noFiles.append(dirpath)                     
                

    # Get each scene with they respected path                
    if rig_name != None:
        path_with_files = [x for x in path_with_files 
                           if x == x.replace(x.split('/')[6], rig_name)                        
                           ]    
    else:
        pass

    path_with_files_rig_srig = []
    if rig_srig != None:
        try:
            path_with_files_temp = [x for x in path_with_files 
                               if x == x.replace(x.split('/')[7], rig_srig)                        
                               ]
            
            path_with_files_rig_srig = [path for path in path_with_files_temp if os.path.exists(path)]
            path_with_files = path_with_files_rig_srig
        except:
            pass

    for path in path_with_files:
       os.chdir(path)       
       for scene in os.listdir(os.getcwd()):
           all_scenes.append(scene)
           scene_path_dic.update({scene:path})

    ## Get the time of each scene
    
    scene_date_dic = {}
    scene_size_dic = {}
    for scene in scene_path_dic:
        os.chdir(scene_path_dic[scene])
        filesize = '{:,}'.format((os.stat(scene).st_size))
        size_scenes.append(filesize)
        lastmodified = os.path.getmtime(scene)
        time_data = (datetime.fromtimestamp(lastmodified))
        timeData_scenes.append(time_data)

        scene_size_dic.update({filesize:scene})
        scene_date_dic.update({time_data:scene})
   
    scene_date_ordered_dic = OrderedDict(sorted(scene_date_dic.items(), reverse=False))
    scene_size_ordered_dic = OrderedDict(sorted(scene_size_dic.items(), reverse=False))


    def date_sorted():
        print ('FILES SORTED BY DATES :')
        print('{}/{}'.format(source_path,rig_name))
        for date, scene in zip (scene_date_ordered_dic.keys(), scene_date_ordered_dic.values()):
            print '    {}..............{}\n'.format(date, scene)
        print('\n')
    
    def size_sorted():
        print ('FILES SORTED BY SIZE :')
        print('{}/{}'.format(source_path,rig_name))
        for size, scene in zip (scene_size_ordered_dic.keys(), scene_size_ordered_dic.values()):
            print '    {} bytes..............{}\n'.format(size, scene)
        print('\n')

    dic_type = {
                'date': date_sorted,
                'size': size_sorted,
                }

    if _print == True :   
        dic_type[type_order]()
    elif _print == False :  
        pass
    
    if type_order == 'size':
        return(scene_size_ordered_dic, path_with_files)
    elif type_order == 'date':
        return(scene_date_ordered_dic, path_with_files)



def find_data_to_delete():
    """Find files to delete"""
    path = data[1]
    all_files = data[0].values()

    if len(all_files)>5:        
        file_to_keep = all_files[-3:] ## 3 most recent        
        file_to_delete = list(set(all_files)-set(file_to_keep))
        
        print ('FILES TO DELETE :')
        for date,file in zip (data[0].keys(), file_to_delete):
            print ('    {}.....{}'.format(date,file))            
        return (file_to_delete, path)
    else:
        print ('There is {} maya scenes'.format(len(data[0])))



def delete_func():  
    """ Functions deletings older maya scenes"""         
    find_data_to_delete_var = find_data_to_delete()
    os.chdir(find_data_to_delete_var[1])
    
    for file in find_data_to_delete_var[0]:
        os.remove(file)

    sys.stdout.write('Files has been deleted')        


def delete_empty_path(source_path, type = 'print'):
    """ Functions deletings path with no maya scenes"""   
    os.chdir(source_path)

    path_with_files = []
    path_with_noFiles = []
    for dirpath, dirnames, filenames, in os.walk(source_path):
        if dirnames == []:
            path_with_files.append(dirpath)

    ## Find path with no Maya scene
    for path in path_with_files:    
        for dirpath, dirnames, filenames, in os.walk(path):
            if filenames == []:
                path_with_noFiles.append(dirpath)  

    print ('EMPTY PATHS :')    
    for _path in path_with_noFiles:
        if type == 'print':
            print ('    {}'.format(_path) )   
        elif type == 'delete':# 
            shutil.rmtree(_path)
            sys.stdout.write('Empty paths has been deleted')      
    


def cleanUp_files_Batch(source_path, rig_srig, _print = False, kill = None):
    """ Delete oldest files except last 3 in a batch"""
    all_data_dic = {}
    all_asset = all_assets_in_path(source_path)
    # all_asset = [1]

    for asset in all_asset:
        data = find_scene_data(source_path, 'date', _print, rig_srig, asset )
        all_files = data[0].values()
        _path = data[1]
        
        ## find_data_to_delete
        if len(all_files)>3:        
            file_to_keep = all_files[-3:] ## 3 most recent        
            file_to_delete = list(set(all_files)-set(file_to_keep))
            
            print ('FILES TO DELETE :')
           
            for i in _path:
                print ('Path: {}'.format(i))
                os.chdir(i)         
            for date,file in zip (data[0].keys(), file_to_delete):
                print ('   >>> {}.....{}'.format(date,file))                 
                if kill == 'delete':
                    os.remove(file)
                                      
                elif kill == None:
                    pass                                   
            print ('\n===================================================== \n')
        else:
            # print ('Path: {}'.format(i))
            # print ('No scenes to delete : There is {} maya scenes'.format(len(data[0])))
            # print ('\n===================================================== \n')
            pass

    if kill == 'delete':
        sys.stdout.write('\nFiles has been deleted')
    else:
        pass



# ==============================================================================================


## rendering folder
# delete_folder('ren','/on/work/adbrower/playmo/sht')

## modeling folder
# delete_folder('mod', '/on/work/adbrower/playmo/set')
# delete_folder('mod', '/on/work/adbrower/playmo/bld')
# delete_folder('mod', '/on/work/adbrower/playmo/veh')
# delete_folder('mod', '/on/work/adbrower/playmo/veg')
# delete_folder('mod', '/on/work/adbrower/playmo/prp')


# # CleaUp Files in Batch
# cleanUp_files_Batch('/on/work/adbrower/playmo/prp', 'rig', False, kill=None)



### SINGLE FILE #####
# find_scene_data('/on/work/adbrower/playmo/sht', 'date', True, 'rig', 'cagea' )           

# delete_empty_path('/on/work/adbrower/playmo/veh')


