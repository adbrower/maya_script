import pymel.core as pm
from collections import OrderedDict


def find_vertexInfluences(prunes = False, prune_value = 0.01000, formating = False):
    
    selection = pm.selected()
    print selection

    def find_single_vertexInfluences(vtx, _formating = formating):
        """
        Returns a dictionnary of the influences of a vertex         
        """
        _influenceDic = {}
        mesh_transform = pm.PyNode(vtx.split('.')[0]).getTransform()
        skin_cluster = pm.mel.eval('findRelatedSkinCluster {}'.format(str(mesh_transform)))
        influences_joints = pm.skinPercent(skin, vtx,  query = True, transform = None)
        value = pm.skinPercent(skin, vtx, query = True, value = True)
        value_format = ['{:.8f}'.format(val) for val in value]
        
        if _formating == False:
            for influence, val in zip (influences_joints, value):
                _influenceDic[str(influence)] = val
                
            influenceDic = OrderedDict(sorted(_influenceDic.items(), key=lambda x: x[1], reverse=False))    
            
        elif _formating == True:
            for influence, val in zip (influences_joints, value_format):
                _influenceDic[str(influence)] = val
                
            influenceDic = OrderedDict(sorted(_influenceDic.items(), key=lambda x: x[1], reverse=False)) 

        print '\n'
        print (vtx)
        for item in influenceDic.items(): print (' --- {}'.format(item))                    
        print ('Number of influences : {}'.format(len(influenceDic)))
        
        # return influenceDic

        
    def prune_influence(_vertex):
        mesh_transform = pm.PyNode(_vertex.split('.')[0]).getTransform()
        skin_cluster = pm.mel.eval('findRelatedSkinCluster {}'.format(str(mesh_transform)))
        influences_joints = pm.skinPercent(skin, _vertex,  query = True, transform = None)
        value = pm.skinPercent(skin, _vertex, query = True, value = True)
        
        pm.skinPercent(skin_cluster, _vertex, pruneWeights = prune_value)
        
    for vertex in selection:
        vert_name = vertex.split('.vtx')[0]
        vert_number = vertex.split('[')[-1].split(':')[0].split(']')[0]        
        single_vert = '{}.vtx[{}]'.format(vert_name, vert_number)

        if prunes == True:
            prune_influence(single_vert)
        else:
            pass
        
                
        find_single_vertexInfluences(single_vert, _formating = formating)


# find_vertexInfluences(prunes = True)    
# find_vertexInfluences()    
