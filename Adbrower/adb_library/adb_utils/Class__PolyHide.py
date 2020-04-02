import pymel.core as pm
import maya.cmds as mc
import maya.mel as mel

import adb_core.Class__AddAttr as adbAttr
from maya.api import OpenMaya as om2


class PolyHide(object):
    def __init__(self,
                mesh,
                threshold = 0.5
                ):
        self.mesh = mesh
        self.threshold = threshold

        self.meshShape = pm.PyNode(self.mesh).getShape()
        ## Init Map
        adbAttr.NodeAttr.addPaintAttribute(str(self.meshShape), 'polyHide')


    def create(self):
        index_list = self.vertexFromMaps('polyHide', threshold=self.threshold)
        mesh_vertex = ['{}.vtx[{}]'.format(self.mesh, i) for i in index_list]
        pm.select(mesh_vertex, r=1)

        mel.eval("ConvertSelectionToFaces;")
        pm.selectType(objectComponent=1, allComponents=False)
        pm.selectType(objectComponent=1, polymeshFace=True)
        pm.mel.PolySelectConvert(1)

        all_faces = pm.selected()
        if pm.selected():
            self.add_material()
        pm.select(None)


    def vertexFromMaps(self, mapName, threshold=0.1):
        """Get all vertex number which the map value is not 0.0
        
        Returns:
            List -- List of all the index 
        """
        mSLmesh = om2.MGlobal.getSelectionListByName(self.mesh).getDependNode(0)
        dag = om2.MFnDagNode(mSLmesh).getPath()
        vert_iter = om2.MItMeshVertex(dag)
        vertCount = vert_iter.count()

        vertValue = mc.getAttr('{}.{}'.format(self.meshShape, mapName))

        vertFromMap = {}
        for index, value in enumerate(vertValue):
            if value > threshold:
                vertFromMap[index] = value
            else:
                pass

        return vertFromMap.keys()


    @staticmethod
    def add_material(mat_name='mat_Trans'):

        selection = pm.selected()
        if pm.objExists(mat_name):
            pm.hyperShade(assign=mat_name)

        else:
            matTrans = mc.shadingNode("lambert", asShader=True)
            pm.setAttr(matTrans + ".transparency",
                       (1,1,1), type='double3')
            pm.rename(matTrans, mat_name)
            pm.select(selection)
            pm.hyperShade(assign=mat_name)



#============================
#  BUILD
#============================

# polyHide =  PolyHide('pSphere1')
# polyHide.create()