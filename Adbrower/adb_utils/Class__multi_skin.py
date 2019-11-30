import maya.cmds as mc
import pymel.core as pm
import sys
import maya.mel as mel

#------------------------------------
# LAYER MANAGING
#------------------------------------

TAG_EXTRACT = 'tag_Extract'
SUFFIX_EXCTACT = 'Extracted'

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

    def add_metaData_attribute(self, _transform, attr_name):
        pm.addAttr(_transform, at='message', ln=attr_name)

    
    @staticmethod
    def extract_TAGS(tag_name):
        extract = [str(x.split('.')[0]) for x in pm.ls('*.{}'.format(tag_name))]
        return extract        

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

    def cleanDuplicate(self, name = None):        
        duplicated_mesh = pm.duplicate(self.final_mesh)[0]
        all_shapes = pm.PyNode(duplicated_mesh).getShapes()
        [pm.delete(x) for x in all_shapes[1:]]
        if name:
            pm.rename(duplicated_mesh, name)
        else:
            pm.rename(duplicated_mesh, '{}__{}'.format(self.final_layer, SUFFIX_EXCTACT))
        duplicated_mesh.getShape().v.set(1)
        return duplicated_mesh
        

    def getSkinCluster(self):
        """
        Find a SkinCluster from a transform        
        Returns the skinCluster node        
        """
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
        """
        Extract a layer (mesh) from a multi skin mesh.
        Clean duplicate of the mesh but keeping the same skinCluster from the original
        """
        get_shape = str(pm.listConnections(pm.PyNode(skinCluster).outputGeometry[0], p=1)[0]).split('.')[0]

        duplicated_mesh = self.cleanDuplicate(name = '{}__{}'.format(get_shape, SUFFIX_EXCTACT))        
        if skinCluster:
            pm.PyNode(skinCluster).outputGeometry[0] >> duplicated_mesh.inMesh
            
        self.add_metaData_attribute(duplicated_mesh, TAG_EXTRACT)
        return str(duplicated_mesh)
            

    def extractWeight(self, skinCluster_index= 0, target_mesh = None, _surfaceAssociation='closestPoint', _influenceAssociation=['oneToOne', 'oneToOne']):
        """
        Extract a skin Cluster weights from a multi skin mesh
        Clean duplicate of the mesh and duplicates a new skinCluster with the same weights
        
        returns: duplicate mesh and duplicate skin cluster
        """
        
        if target_mesh == None:
            _target_mesh = self.cleanDuplicate()
        else:
            _target_mesh = target_mesh

        
        skincluster = self.all_skinCluster[skinCluster_index]
        destination_skin = pm.duplicate(skincluster, ic=1)[0]
        destination_skin.outputGeometry[0] >> _target_mesh.inMesh
        return(_target_mesh, destination_skin)
        

    def add_upper_deformers(self, target, layers_to_add =[], ):
        """
        Add lower layer deformation as blendshapes
        """
        
        new_order = []
        for layer in layers_to_add:
            get_vis = pm.PyNode(layer).v.get()
            pm.PyNode(layer).v.set(1)
            pm.blendShape(layer, target,  o = 'local', w = [(0, 1.0)], foc = False)
            pm.PyNode(layer).v.set(get_vis)
                    
        deformers_order = mel.eval('findRelatedDeformer("' + str(target) + '")')  
        skin_deformer = [x for x in deformers_order if pm.PyNode(x).type()=='skinCluster'][0]
        
        bls_deformer = [x for x in deformers_order if pm.PyNode(x).type()=='blendShape']                                
        new_order.append(skin_deformer)
        new_order.append(target)   

        for bls in bls_deformer:
            new_order.insert(1,bls)
            pm.reorderDeformers(new_order)
            new_order.remove(bls)
            
        return bls_deformer


    def delete_blendshapes(self, target):
        deformers_order = mel.eval('findRelatedDeformer("' + str(target) + '")')      
        bls_deformer = [x for x in deformers_order if pm.PyNode(x).type()=='blendShape'] 
        pm.delete(bls_deformer) 
        

        
#------------------------------------
# Test
#------------------------------------

# aaa = MultiSkin('pSphere1')


# aaa.extractWeight(-1)
# aaa.add_upper_deformers('pSphereShape1__TEMP', ['test2', 'test3'])

# pm.blendShape('test1', 'pSphereShape1__TEMP',  o = 'local', w = [(0, 1.0)], foc = False)


# [aaa.add_new_layer(x) for x in ['test4', 'test5']] 

# print aaa.getSkinCluster()
# print aaa.all_skinCluster_dic.keys()
# print aaa.all_layers
# aaa.add_skin_cluster(['adb_joint02', 'adb_joint01'], aaa.all_layers[0], 'caca')
# aaa.add_skin_cluster(['adb_joint03', 'adb_joint04'], aaa.all_layers[1], 'toto')
# aaa.add_skin_cluster(['adb_joint05', 'adb_joint06'], aaa.all_layers[2])



# aaa.delete_skin_cluster('skinCluster2')

# print aaa.layer_index_dic['test2']



