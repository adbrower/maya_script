import maya.cmds as mc
import pymel.core as pm
import sys
import maya.mel as mel

#------------------------------------
# LAYER MANAGING
#------------------------------------


class MultiSkin(object):
    
    def __init__(self,
                final_mesh
                ):
                    

        self.final_mesh = pm.PyNode(final_mesh)      
        self.all_layers  = self.get_layers()        
        self.final_layer = self.get_final_layer()
        self.new_layer = None        
        self.all_skinCluster = self.getSkinCluster()
        self.all_skinCluster_dic = self.initialize_skin_cluster_dic()

    def add_shapes(self, shape_name=None):
        if shape_name:
            duplicated_mesh = pm.duplicate(self.final_mesh)[0]
            new_shape = pm.PyNode(duplicated_mesh).getShape()
            pm.parent(new_shape, self.final_mesh, add=1, s=1)
            pm.delete(duplicated_mesh)
            pm.rename(new_shape, shape_name)
            new_shape.v.set(0)
            return new_shape
        else:
            duplicated_mesh = pm.duplicate(self.final_mesh)[0]
            new_shape = pm.PyNode(duplicated_mesh).getShape()
            pm.parent(new_shape, self.final_mesh, add=1, s=1)
            pm.delete(duplicated_mesh)
            new_shape.v.set(0)
            return new_shape

            

    def get_layers(self):
        self.layer_index_dic ={}
        for i, layer in enumerate(self.final_mesh.getShapes(ni=1)[1:]):
            self.layer_index_dic.update({str(layer):i})
        
        return self.final_mesh.getShapes(ni=1)[1:] or []


    def get_final_layer(self):                
        shapes = self.final_mesh.getShapes(ni=1)
        return [x for x in shapes if pm.listConnections('{}.outMesh'.format(x), p=1) == []][0]


    def connect_layer(self, layer_to_connect, final_layer):    
        last_layer_connection = pm.listConnections('{}.inMesh'.format(self.final_layer), s=1, p=1) or []
        if last_layer_connection != []:
            pm.connectAttr(last_layer_connection[0], '{}.inMesh'.format(layer_to_connect), f=1)
        pm.connectAttr('{}.outMesh'.format(layer_to_connect), '{}.inMesh'.format(final_layer), f=1)


    def add_new_layer(self, layer_name=None):        
        if layer_name:
            self.new_layer = self.add_shapes(layer_name)
        else:
            self.new_layer  = self.add_shapes()                
        self.connect_layer(self.new_layer, self.final_layer)
        self.all_layers.append(self.new_layer)


    #------------------------------------
    #  CLUSTER CREATION
    #------------------------------------

    def cleanDuplicate(self):        
        duplicated_mesh = pm.duplicate(self.final_mesh)[0]
        all_shapes = pm.PyNode(duplicated_mesh).getShapes()
        [pm.delete(x) for x in all_shapes[1:]]
        pm.rename(duplicated_mesh, '{}__TEMP'.format(self.final_layer))
        duplicated_mesh.getShape().v.set(1)
        return duplicated_mesh
        

    def getSkinCluster(self):
        '''
        Find a SkinCluster from a transform        
        Returns the skinCluster node        
        '''
        result = []
        if not (pm.objExists(self.final_mesh)):
            return result
        validList = mel.eval('findRelatedDeformer("' + str(self.final_mesh) + '")')        
        if validList == None:
            return result        
        for elem in validList:
            if pm.nodeType(elem) == 'skinCluster':
                result.append(elem)
        pm.select(result, r = True)

        result_node = pm.selected()
        if result_node == []:
            return []
        elif len(result_node) > 1:
            return result_node or []
        else:
            return result_node


    def setPreBind(self, transform, custom_skinCluster=None):
        pm.select(transform, r=1)
        sel_type = (pm.selected()[0]).type()
        print sel_type
                
        if str(sel_type) == 'skinCluster':
            skinCluster = pm.PyNode(transform)
            all_binds_jnts =  [x for x in pm.listConnections(str(skinCluster)+'.matrix[*]', s=1)]
            print all_binds_jnts
            
            for joint in all_binds_jnts:
                translation_validator = list(pm.PyNode(joint).getTranslation())
                if translation_validator == [0.0, 0.0, 0.0]:
                    skinClusterPlugs = pm.listConnections(joint + ".worldMatrix[0]", type="skinCluster", p=1)
                    for skinClstPlug in skinClusterPlugs:
                        index = skinClstPlug.split('[')[-1].split(']')[0]
                        pm.connectAttr(joint.parentInverseMatrix, pm.PyNode(skinCluster).bindPreMatrix[index], f=1)
                else:
                    pm.warning('JOINTS DONT HAVE 0 TRANSLATIONS')

        elif str(sel_type) == 'joint':
            translation_validator = list(pm.PyNode(transform).getTranslation())
            if translation_validator == [0.0, 0.0, 0,0]:
                joint = pm.PyNode(transform)
                skinClusterPlugs = pm.listConnections(joint + ".worldMatrix[0]", type="skinCluster", p=1)
                for skinClstPlug in skinClusterPlugs:
                    skinCluster = pm.PyNode(skinClstPlug.split('.')[0])
                    index = skinClstPlug.split('[')[-1].split(']')[0]
                    pm.connectAttr(joint.parentInverseMatrix, pm.PyNode(skinCluster).bindPreMatrix[index], f=1)
            else:
                pm.warning('JOINTS DONT HAVE 0 TRANSLATIONS')

        elif isinstance (transform,list):   
            skinCluster = custom_skinCluster
            all_binds_jnts =  [x for x in pm.listConnections(str(skinCluster)+'.matrix[*]', s=1)]
            
            for joint, trans in zip(all_binds_jnts, transform):
                skinClusterPlugs = pm.listConnections(joint + ".worldMatrix[0]", type="skinCluster", p=1)
                for skinClstPlug in skinClusterPlugs:
                    index = skinClstPlug.split('[')[-1].split(']')[0]
                    pm.connectAttr(pm.PyNode(trans).parentInverseMatrix, pm.PyNode(skinCluster).bindPreMatrix[index], f=1)


    def initialize_skin_cluster_dic(self):
        cluster_dic = {}
        for cluster in self.getSkinCluster():            
            all_binds_jnts =  [str(x) for x in pm.listConnections(str(cluster)+'.matrix[*]', s=1)]
        
            cluster_dic.update({str(cluster):all_binds_jnts})
        return cluster_dic



    def add_skin_cluster(self, joints = [], layer_to_add = '', name = None):
        get_vis = pm.PyNode(layer_to_add).v.get()
        pm.PyNode(layer_to_add).v.set(1)
        if name:
            cluster = pm.skinCluster(joints, layer_to_add, tsb=True, name=name)
        else:
            cluster = pm.skinCluster(joints, layer_to_add, tsb=True)
        layer_to_add.v.set(get_vis)
        self.all_skinCluster.append(cluster)
        self.all_skinCluster_dic.update({str(cluster):str(joints)})

        if len(self.all_skinCluster) > 1:
            self.setPreBind(cluster) # Only prebind the additional layer


    def delete_skin_cluster(self, skinCluster):
        outputs_plug = pm.listConnections(pm.PyNode(skinCluster).outputGeometry, p=1)
        skinCluster_outputs = [str(x).split('.')[0] for x in outputs_plug]
        valid_skinCluster_outputs = [x for x in skinCluster_outputs if x in self.all_layers][0]
        
        if self.layer_index_dic[valid_skinCluster_outputs] - 1 < 0:
            index_valid = 0
            previous_layer= None
        else: 
            index_valid = self.layer_index_dic[valid_skinCluster_outputs] - 1
            previous_layer = self.all_layers[index_valid] 
            pm.PyNode(previous_layer).outMesh >> pm.PyNode(valid_skinCluster_outputs).inMesh

        pm.delete(skinCluster)


    def extractLayer(self, skinCluster=None):

        duplicated_mesh = self.cleanDuplicate()
        # duplicated_mesh = pm.duplicate(self.final_mesh)[0]
        # all_shapes = pm.PyNode(duplicated_mesh).getShapes()
        # [pm.delete(x) for x in all_shapes[1:]]
        # pm.rename(duplicated_mesh, '{}__TEMP'.format(self.final_layer))
        
        if skinCluster:
            pm.PyNode(skinCluster).outputGeometry[0] >> duplicated_mesh.inMesh
            

    def extractWeight(self, skinCluster_index= 0, target_mesh = None, _surfaceAssociation='closestPoint', _influenceAssociation=['oneToOne', 'oneToOne']):
        '''
        Extract a skin Cluster weights on a multi skin mesh
        Creates a new skinCluster with the same weights
        '''
        
        if target_mesh == None:
            _target_mesh = self.cleanDuplicate()
        else:
            _target_mesh = target_mesh

        
        skincluster = self.all_skinCluster[skinCluster_index]
        bind_joints = [x for x in pm.listConnections(str(skincluster)+'.matrix[*]', s=1)]

        ## Skinning
        pm.select(_target_mesh, r = 1)
        pm.select(bind_joints, add = True)
        mc.SmoothBindSkin()
        destination_skin =  [x for x in mel.eval('findRelatedDeformer("' + str(_target_mesh) + '")') if pm.nodeType(x) == 'skinCluster'][0]  

        # Copy Weight Skin        
        pm.select(self.final_mesh, r = True)
        pm.select(_target_mesh, add = True)     
        
        pm.copySkinWeights(ss=str(skincluster), ds = str(destination_skin), surfaceAssociation= _surfaceAssociation, influenceAssociation=_influenceAssociation, noMirror=1)   
        return(_target_mesh, destination_skin)
        
        
        
#------------------------------------
# Test
#------------------------------------

# aaa = MultiSkin('pSphere1')
# print aaa.all_skinCluster

# aaa.extractWeight(2)


# [aaa.add_new_layer(x) for x in ['test4', 'test5']] 

# print aaa.getSkinCluster()
# print aaa.all_skinCluster_dic.keys()
# print aaa.all_layers
# aaa.add_skin_cluster(['adb_joint02', 'adb_joint01'], aaa.all_layers[0], 'caca')
# aaa.add_skin_cluster(['adb_joint03', 'adb_joint04'], aaa.all_layers[1], 'toto')
# aaa.add_skin_cluster(['adb_joint05', 'adb_joint06'], aaa.all_layers[2])



# aaa.delete_skin_cluster('skinCluster2')

# print aaa.layer_index_dic['test2']



