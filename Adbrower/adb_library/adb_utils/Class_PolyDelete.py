import pymel.core as pm
import maya.cmds as mc
import maya.mel as mel
from maya.api import OpenMaya as om2

import adb_core.Class__AddAttr as adbAttr
import adb_core.NameConv_utils as NC


class PolyDelete(object):
    def __init__(self,
                mesh,
                threshold = 0.5
                ):
        self.mesh = mesh
        self.threshold = threshold

        self.meshShape = pm.PyNode(self.mesh).getShape()
        ## Init Map
        adbAttr.NodeAttr.addPaintAttribute(str(self.meshShape), 'PolyDelete')


    def create(self):
        dupMesh = self.duplicateMesh()
        index_list = self.vertexFromMaps('PolyDelete', threshold=self.threshold)
        mesh_vertex = ['{}.vtx[{}]'.format(dupMesh, i) for i in index_list]
        pm.select(mesh_vertex, r=1)

        mel.eval("ConvertSelectionToFaces;")
        pm.selectType(objectComponent=1, allComponents=False)
        pm.selectType(objectComponent=1, polymeshFace=True)
        pm.mel.PolySelectConvert(1)

        all_faces = pm.selected()
        pm.delete(all_faces)
        pm.select(None)


    def duplicateMesh(self):
        dupMesh = mc.duplicate(self.mesh, name = '{}_temp'.format(self.mesh))[0]
        dupMesh_newName = NC.renameBasename(dupMesh, '{}PolyDelete'.format(NC.getBasename(self.mesh)))
        dupMesh = pm.rename(str(dupMesh_newName), dupMesh_newName.replace('_temp', ''))

        return dupMesh


    def vertexFromMaps(self, mapName, threshold=0.1):
        """
        Get all vertex number which the map value is not 0.0

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




#============================
#  BUILD
#============================

# PolyDelete =  PolyDelete('L__pSphere1__MSH')
# PolyDelete.create()