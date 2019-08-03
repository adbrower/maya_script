# -------------------------------------------------------------------
# Class Skinning Module
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# -------------------------------------------------------------------

import sys
import pymel.core as pm
import maya.cmds as mc
from functools import wraps
import maya.mel as mel
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import math

from adbrower import flatList
from adbrower import undo


# -----------------------------------
# FUNCTIONS
# -----------------------------------


def getSkinCluster(_transform):
    """
    Find a SkinCluster from a transform
    Returns the skinCluster node
    """
    result = []
    if not (pm.objExists(_transform)):
        return result
    validList = mel.eval('findRelatedDeformer("' + str(_transform) + '")')
    if validList is None:
        return result
    for elem in validList:
        if pm.nodeType(elem) == 'skinCluster':
            result.append(elem)
    pm.select(result, r=True)
    result_node = pm.selected()
    if len(result_node) > 1:
        return result_node
    else:
        return result_node[0]


def getBindJoints(_transform):
    """
    Find all bind joints from a mesh with a skin cluster
    Returns: List of joints
    """
    _skinCls = getSkinCluster(_transform)
    all_binds_jnts = [x for x in pm.listConnections(str(_skinCls) + '.matrix[*]', s=1)]
    return all_binds_jnts


def resetSkinnedJoints(joint):
    """
    Reset skin deformation for selected joint(s)
    @param Joints.
    """

    # Get connected skinCluster nodes
    skinClusterPlugs = pm.listConnections(joint + ".worldMatrix[0]", type="skinCluster", p=1)
    if skinClusterPlugs:
        # for each skinCluster connection
        for skinClstPlug in skinClusterPlugs:
            index = skinClstPlug.split('[')[-1].split(']')[0]
            skinCluster = pm.PyNode(skinClstPlug.split('.')[0])
            curInvMat = mc.getAttr(joint + ".worldInverseMatrix")
            preBind_connections = pm.listConnections(skinCluster + ".bindPreMatrix[*]", type="joint", p=1) or []
            _preBind_sources = pm.listConnections(skinCluster + ".bindPreMatrix[*]", type="joint", s=1)
            preBind_sources = [x for x in _preBind_sources if joint in _preBind_sources]
            if preBind_sources != []:
                pm.disconnectAttr(pm.PyNode(joint).parentInverseMatrix, skinCluster.bindPreMatrix[index])
                pm.setAttr(skinCluster + ".bindPreMatrix[{}]".format(index), type="matrix", *curInvMat)
                pm.warning('PreBind Attriubte had connections :  {}'.format(preBind_connections))
            else:
                pm.setAttr(skinCluster + ".bindPreMatrix[{}]".format(index), type="matrix", *curInvMat)

    else:
        print("No skinCluster attached to {0}".format(joint))

# -----------------------------------
# CLASS
# -----------------------------------


class Skinning(object):
    """
    A Module containing multiples skinning methods

    @param _node: Single string or a list. Default value is pm.selected()

    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_utils.Class__Skinning as skin
    reload (skin)
    """

    def __init__(self,
                 _tranformToCheck=pm.selected(),
                 ):

        self._tranformToCheck = _tranformToCheck

    def getSkinCluster(self):
        """
        Find a SkinCluster from a transform
        Returns the skinCluster node
        """
        result = []
        if not (pm.objExists(self._tranformToCheck)):
            return result
        validList = mel.eval('findRelatedDeformer("' + str(self._tranformToCheck) + '")')
        if validList is None:
            return result
        for elem in validList:
            if pm.nodeType(elem) == 'skinCluster':
                result.append(elem)
        pm.select(result, r=True)

        result_node = pm.selected()
        if len(result_node) > 1:
            return result_node
        else:
            return result_node[0]

    def getBindJoints(self, skinCluster_index=0):
        """
        Find all bind joints from a mesh with a skin cluster
        Returns: List of joints
        """
        _skinCls = self.getSkinCluster()
        if isinstance(_skinCls, list):
            _skinCls = self.getSkinCluster()[skinCluster_index]
        else:
            _skinCls = self.getSkinCluster()
        all_binds_jnts = [x for x in pm.listConnections(str(_skinCls) + '.matrix[*]', s=1)]
        return all_binds_jnts

    @staticmethod
    def setPreBind(transform, custom_skinCluster=None):
        pm.select(transform, r=1)

        if isinstance(pm.selected()[0], pm.nodetypes.SkinCluster):
            skinCluster = pm.PyNode(transform)
            all_binds_jnts = [x for x in pm.listConnections(str(skinCluster) + '.matrix[*]', s=1)]

            for joint in all_binds_jnts:
                translation_validator = list(pm.PyNode(joint).getTranslation())
                if translation_validator == [0.0, 0.0, 0, 0]:
                    skinClusterPlugs = pm.listConnections(joint + ".worldMatrix[0]", type="skinCluster", p=1)
                    for skinClstPlug in skinClusterPlugs:
                        index = skinClstPlug.split('[')[-1].split(']')[0]
                        pm.connectAttr(joint.parentInverseMatrix, pm.PyNode(skinCluster).bindPreMatrix[index], f=1)
                else:
                    pm.warning('JOINTS DONT HAVE 0 TRANSLATIONS')

        if isinstance(pm.selected()[0], pm.nodetypes.Joint):
            translation_validator = list(pm.PyNode(transform).getTranslation())
            if translation_validator == [0.0, 0.0, 0, 0]:
                joint = pm.PyNode(transform)
                skinClusterPlugs = pm.listConnections(joint + ".worldMatrix[0]", type="skinCluster", p=1)
                for skinClstPlug in skinClusterPlugs:
                    skinCluster = pm.PyNode(skinClstPlug.split('.')[0])
                    index = skinClstPlug.split('[')[-1].split(']')[0]
                    pm.connectAttr(joint.parentInverseMatrix, pm.PyNode(skinCluster).bindPreMatrix[index], f=1)
            else:
                pm.warning('JOINTS DONT HAVE 0 TRANSLATIONS')

        elif isinstance(transform, list):
            skinCluster = custom_skinCluster
            all_binds_jnts = [x for x in pm.listConnections(str(skinCluster) + '.matrix[*]', s=1)]

            for joint, trans in zip(all_binds_jnts, transform):
                skinClusterPlugs = pm.listConnections(joint + ".worldMatrix[0]", type="skinCluster", p=1)
                for skinClstPlug in skinClusterPlugs:
                    index = skinClstPlug.split('[')[-1].split(']')[0]
                    pm.connectAttr(pm.PyNode(trans).parentInverseMatrix, pm.PyNode(skinCluster).bindPreMatrix[index], f=1)

    @staticmethod
    @undo
    def solveBtwn():
        def _getWeights(skcls):
            selList = om.MSelectionList()
            selList.add(skcls)
            skcls = om.MObject()
            selList.getDependNode(0, skcls)
            skclsFn = oma.MFnSkinCluster(skcls)
            infDags = om.MDagPathArray()
            skclsFn.influenceObjects(infDags)
            infIds = {}
            infs = {}
            for index in xrange(infDags.length()):
                infPath = infDags[index].fullPathName()
                infId = int(skclsFn.indexForInfluenceObject(infDags[index]))
                infIds[infId] = index
                infs[infId] = infDags[index].partialPathName()

            weightListPlug = skclsFn.findPlug('weightList')
            weightsPlug = skclsFn.findPlug('weights')
            weightListAttr = weightListPlug.attribute()
            weightsAttr = weightsPlug.attribute()
            weightsInfIds = om.MIntArray()

            weights = {}
            for vId in xrange(weightListPlug.numElements()):
                vWeights = {}
                weightsPlug.selectAncestorLogicalIndex(vId, weightListAttr)
                weightsPlug.getExistingArrayAttributeIndices(weightsInfIds)

                infPlug = om.MPlug(weightsPlug)
                for infId in weightsInfIds:
                    infPlug.selectAncestorLogicalIndex(infId, weightsAttr)
                    try:
                        # if weight value is pretty much 0, skip
                        value = infPlug.asDouble()
                        if value > 0.000000001:
                            vWeights[infId] = value
                    except KeyError:
                        pass
                weights[vId] = vWeights
            return weights, infs

        def getId(name):
            return int(name.split('[')[1].split(']')[0])

        def getDistance(start, end):
            startPos = pm.xform(start, q=True, ws=True, t=True)
            endPos = pm.xform(end, q=True, ws=True, t=True)
            vector = [0, 0, 0]
            vector[0] = endPos[0] - startPos[0]
            vector[1] = endPos[1] - startPos[1]
            vector[2] = endPos[2] - startPos[2]
            return math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)

        def interp(start, end, ratio):
            span = end - start
            return start + (span * ratio)

        def interpWeights(start, end, vert, infs, weights, skincluster):
            if isinstance(skincluster, str):
                if pm.nodeType(skincluster) != 'skinCluster':
                    return "Error: '%s' is not a skin cluster." % skincluster, None
                skincluster = pm.PyNode(skincluster)
            if isinstance(skincluster, pm.PyNode):
                if type(skincluster) != pm.nt.SkinCluster:
                    return "Error: '%s' is not a skin cluster." % skincluster, None

            skincluster.envelope.set(0)

            infIds = set(())
            if isinstance(start, pm.nt.Joint):
                startWeights = {infs[start.name()]: 1.0}
            else:
                startWeights = weights[getId(start.name())]
            if isinstance(end, pm.nt.Joint):
                endWeights = {infs[end.name()]: 1.0}
            else:
                endWeights = weights[getId(end.name())]

            print(start, end, startWeights, endWeights)

            for infId in startWeights:
                infIds.add(infId)
            for infId in endWeights:
                infIds.add(infId)
            infIds = list(infIds)

            fromStart = getDistance(start, vert)
            toEnd = getDistance(vert, end)
            total = fromStart + toEnd
            startRatio = fromStart / total

            for infId in infIds:
                if infId not in startWeights.keys():
                    startValue = 0
                else:
                    startValue = startWeights[infId]
                if infId not in endWeights.keys():
                    endValue = 0
                else:
                    endValue = endWeights[infId]
                pm.setAttr(skincluster.weightList[getId(vert.name())].weights[infId], interp(startValue, endValue, startRatio))
            skincluster.envelope.set(1)

        def _figureOutSelectionOrder(vertices):
            geo = vertices[0].split('.')[0]
            sel_list = om.MSelectionList()
            sel_list.add(geo)
            mesh = om.MObject()
            sel_list.getDependNode(0, mesh)
            vertex_iter = om.MItMeshVertex(mesh)
            util = om.MScriptUtil()
            util.createFromInt(0, 0)
            prev_index = util.asIntPtr()
            vert_indices = []
            vert_set = set([])
            for vertex in vertices:
                index = int(vertex.split('.vtx[')[1].split(']')[0])
                vert_indices.append(index)
                vert_set.add(index)
            lookup = {}
            connected_verts = om.MIntArray()
            for index in vert_indices:
                vertex_iter.setIndex(index, prev_index)
                vertex_iter.getConnectedVertices(connected_verts)
                lookup[index] = set(connected_verts)

            items = {}
            start = None
            end = None
            for index, connects in lookup.items():
                verts = vert_set & connects
                if len(verts) == 1:
                    if start is None:
                        start = index
                    if end is None:
                        end = index
                for vert in verts:
                    try:
                        items[vert].append(index)
                    except KeyError:
                        items[vert] = []
                        items[vert].append(index)
            order = [start]
            prev = None
            for _ in range(len(items.keys()) - 1):
                index = order[-1]
                verts = items[index]

                if prev is None:
                    order.append(verts[0])
                else:
                    verts.remove(prev)
                    order.append(verts[0])
                prev = index
            return ['%s.vtx[%s]' % (geo, vert) for vert in order]

        def solveBetween():
            selection = pm.ls(os=True, fl=True)
            if not len(selection):
                return "Error: Nothing Selected."

            start = None
            end = None
            mods = []
            selection = [pm.PyNode(v) for v in _figureOutSelectionOrder([v.name() for v in selection])]
            for index, item in enumerate(selection):
                if index == 0:
                    start = item
                elif index == (len(selection) - 1):
                    end = item
                else:
                    mods.append(item)

            shape = mods[0].node()
            geo = pm.listRelatives(shape, p=True)[0]
            skclss = pm.ls(pm.listHistory(geo), type='skinCluster')
            if len(skclss) == 0:
                return "Error: geo has no skin cluster"
            skcls = skclss[0]
            weights, infs = _getWeights('{}'.format(skcls))
            infs = dict([(inf, vert_id) for vert_id, inf in infs.items()])
            for mod in mods:
                for infId in weights[getId(mod.name())].keys():
                    pm.setAttr(skcls.weightList[getId(mod.name())].weights[infId], 0)
                interpWeights(start, end, mod, infs, weights, skcls)
        solveBetween()

    @undo
    def conform_weights(self):
        """
        It conforms the weights of the selected vertices. The selection needs to be vertices of a mesh and
        the mesh should have attached a skinCluster.

        Returns:

        """
        weights_data = dict()
        selection = mc.ls(sl=1, fl=1)
        mc.select(cl=1)
        for component in selection:
            if mc.objectType(component, i='mesh'):
                mesh = mc.listRelatives(component, p=1)[0]
                for skn in mc.ls(typ='skinCluster'):
                    if mc.skinCluster(skn, q=1, g=1)[0] == mesh:
                        for influence, weight in zip(mc.skinCluster(skn, inf=1, q=1),
                                                     mc.skinPercent(skn, component, q=1, v=1)):
                            if weight != 0 and influence in weights_data.keys():
                                weights_data[influence] += weight
                            elif weight != 0 and influence not in weights_data.keys():
                                weights_data[influence] = weight
                            else:
                                pass
                        break
        transformation_value = [(influence, weight / len(selection)) for influence, weight in weights_data.items()]
        for component in selection:
            mc.skinPercent(skn, component, transformValue=transformation_value)

    def verifyJntsSkin(self, sign_to_split='_', left_side='L', right_side='R'):
        """
        Verify if the same amount of joint on the Left side are skinned to the Right side to exexute a proper mirror
        """

        all_jnts = self.getBindJoints()

        L_jnts_Len = len([x for x in all_jnts if x.split(sign_to_split)[0] == left_side])
        R_jnts_Len = len([x for x in all_jnts if x.split(sign_to_split)[0] == right_side])

        L_jnts = [x for x in all_jnts if x.split(sign_to_split)[0] == left_side] or []
        R_jnts = [x for x in all_jnts if x.split(sign_to_split)[0] == right_side] or []

        L_jnts_rev = [str(x).replace(x.split(sign_to_split)[0] + sign_to_split, '{}{}'.format(right_side, sign_to_split)) for x in L_jnts] or []
        R_jnts_rev = [str(x).replace(x.split(sign_to_split)[0] + sign_to_split, '{}{}'.format(left_side, sign_to_split)) for x in R_jnts] or []

        inexistant = []

        if L_jnts == []:
            pm.warning(' left side joints not existing!')

        if R_jnts == []:
            pm.warning(' right side joints not existing!')

        if L_jnts_Len == 0 or R_jnts_Len == 0:
            return
        for jnts in L_jnts_rev:
            value = jnts in all_jnts
            if value is False:
                inexistant.append(jnts)
            else:
                pass
        for jnts in R_jnts_rev:
            value = jnts in all_jnts
            if value is False:
                inexistant.append(jnts)
            else:
                pass
        if L_jnts_Len == R_jnts_Len:
            sys.stdout.write('// Result: Equals joints skinned  //')
        else:
            pm.select(inexistant, r=True)
            pm.warning(str('{} missing!!'.format(inexistant)).replace('u\'', "'"))

    def lockAll_Weight(self,):
        all_jnts = self.getBindJoints()
        for jnt in all_jnts:
            pm.setAttr('{}.liw'.format(jnt), 1)

    def unlockAll_Weight(self):
        all_jnts = self.getBindJoints()
        for jnt in all_jnts:
            pm.setAttr('{}.liw'.format(jnt), 0)

    def lock_weights(self, joints):
        for jnt in joints:
            pm.setAttr('{}.liw'.format(jnt), 1)

    def unlock_weights(self, joints):
        for jnt in joints:
            pm.setAttr('{}.liw'.format(jnt), 0)

    def floodWeight(self, transform, joint, value=1, op="absolute"):
        pm.select(transform, r=1)
        if len(pm.ls(sl=1)) == 0:
            pm.warning('Select a Mesh!')
        # if we're not currently in the paint skin weights tool context, get us into it
        if pm.currentCtx() != "artAttrSkinContext":
            mel.eval("ArtPaintSkinWeightsTool;")
        # first get the current settings so that the user doesn't have to switch back
        currOp = pm.artAttrSkinPaintCtx(pm.currentCtx(), q=1, selectedattroper=1)
        currValue = pm.artAttrSkinPaintCtx(pm.currentCtx(), q=1, value=1)
        # flood the current selection to zero
        # first set our tool to the selected operation and value
        pm.artAttrSkinPaintCtx(pm.currentCtx(), e=1, selectedattroper=op)
        pm.artAttrSkinPaintCtx(pm.currentCtx(), e=1, value=value)
        # change set joint
        mel.eval('string $selecJoint = "%s";' % joint)
        mel.eval('artSkinInflListChanging $selecJoint 1;')
        mel.eval('artSkinInflListChanged artAttrSkinPaintCtx;')
        # flood the tool
        pm.artAttrSkinPaintCtx(pm.currentCtx(), e=1, clear=1)
        # # set the tools back to the way you found them
        pm.artAttrSkinPaintCtx(pm.currentCtx(), e=1, selectedattroper=currOp)
        pm.artAttrSkinPaintCtx(pm.currentCtx(), e=1, value=currValue)

    def addInfluencese(self, joints):
        """
        Add joint to a skin cluster and default weight is 0.
        """
        bind_joints = self.getBindJoints() or []
        sknCls = self.getSkinCluster()
        for joint in joints:
            try:
                pm.skinCluster(sknCls, ai=joint, dr=0.1, wt=0, e=1, lw=True)
            except RuntimeError:
                pass

    def copyWeight(self, target_mesh, _surfaceAssociation='closestPoint', _influenceAssociation=['oneToOne', 'oneToOne']):
        """
        Maya Copy Weight set up between 2 meshes
        """
        sources_mesh_jnts = self.getBindJoints() or []

        # Skinning
        pm.select(target_mesh, r=1)
        pm.select(sources_mesh_jnts, add=True)
        mc.SmoothBindSkin()

        # Copy Weight Skin
        pm.select(self._tranformToCheck, r=True)
        pm.select(target_mesh, add=True)
        pm.copySkinWeights(surfaceAssociation=_surfaceAssociation, influenceAssociation=_influenceAssociation, noMirror=1)

    def extractWeight(self, target_mesh, skinCluster_index=0, _surfaceAssociation='closestPoint', _influenceAssociation=['oneToOne', 'oneToOne']):
        """
        Extract a skin Cluster weights on a multi skin mesh
        Creates a new skinCluster with the same weights
        """

        skincluster_list = self.getSkinCluster()
        skincluster = skincluster_list[skinCluster_index]
        bind_joints = self.getBindJoints(skinCluster_index)

        # Skinning
        pm.select(target_mesh, r=1)
        pm.select(bind_joints, add=True)
        mc.SmoothBindSkin()
        destination_skin = str(getSkinCluster(target_mesh))

        # Copy Weight Skin
        pm.select(self._tranformToCheck, r=True)
        pm.select(target_mesh, add=True)

        pm.copySkinWeights(ss=str(skincluster), ds=destination_skin, surfaceAssociation=_surfaceAssociation, influenceAssociation=_influenceAssociation, noMirror=1)

    def transferMeshSkinWeights(self, target_mesh, target_joints):
        """
        Transfer skin from a mesh to another with new set of joints

        @param target_mesh: str or list. transform receving the skin weights
        @param target_joints: list.  list of joints bind to the target mesh
        """
        source_joints = self.getBindJoints()
        self.copyWeight(target_mesh)
        self.addInfluencese(target_mesh, target_joints)

        for source_jnt, target_jnt in zip(source_joints, target_joints):
            # lock all targets mesh's joints
            all_jnts = getBindJoints(target_mesh)
            for jnt in all_jnts:
                pm.setAttr('{}.liw'.format(jnt), 1)
            self.unlock_weights([source_jnt])
            self.unlock_weights([target_jnt])
            self.floodWeight(target_mesh, str(target_jnt), value=1, op="absolute")
        target_sknCls = getSkinCluster(target_mesh)
        [pm.skinCluster(target_sknCls, e=1, ri=x) for x in source_joints]  # Remove unused joints

    def transferJointWeights(self, source_joints, target_joints):
        """
        Transfer skin from a joint list to another on the same mesh

        @param source_joints: list. list of joints with original skin weights
        @param target_joints: list  new list of joints receving the skin weights

        """
        target_mesh = self._tranformToCheck
        for source_jnt, target_jnt in zip(source_joints, target_joints):
            self.lockAll_Weight()
            self.unlock_weights([source_jnt])
            self.unlock_weights([target_jnt])
            self.floodWeight(target_mesh, str(target_jnt), value=1, op="absolute")
        self.lockAll_Weight()
        sys.stdout.write('Transfer complete! \n ')

    def find_replacement_joints(self, search='L', replace='R_', _custom=False):
        skin_cluster = self.getSkinCluster()
        original_jnts = self.getBindJoints()
        if _custom:
            replace_skin_joints = _custom
        else:
            replace_skin_joints = [x.replace(search, replace) for x in original_jnts]
        return replace_skin_joints

    def mirrorSkinWeight(self,
                         target_mesh,
                         _mirrorMode='YZ',
                         _surfaceAssociation='closestPoint',
                         _influenceAssociation=['oneToOne', 'oneToOne'],
                         custom=False,
                         search='L',
                         replace='R_'
                         ):

        self.replace_skin_joints = self.find_replacement_joints(search=search, replace=replace, _custom=custom)

        pm.select(None)
        pm.select(self.replace_skin_joints)
        pm.select(target_mesh, add=True)
        mc.SmoothBindSkin()

        pm.select(None)
        pm.select(self._tranformToCheck, add=True)
        pm.select(target_mesh, add=True)

        if _mirrorMode == 'YZ':
            arguments = [" -mirrorMode YZ -surfaceAssociation " + _surfaceAssociation + "-influenceAssociation " + _influenceAssociation[0] + " -influenceAssociation " + _influenceAssociation[1]]
            pm.mel.doMirrorSkinWeightsArgList(2, arguments)

        if _mirrorMode == 'XY':
            arguments = [" -mirrorMode XY -surfaceAssociation " + _surfaceAssociation + "-influenceAssociation " + _influenceAssociation[0] + " -influenceAssociation " + _influenceAssociation[1]]
            pm.mel.doMirrorSkinWeightsArgList(2, arguments)

        if _mirrorMode == 'XZ':
            arguments = [" -mirrorMode XZ -surfaceAssociation " + _surfaceAssociation + "-influenceAssociation " + _influenceAssociation[0] + " -influenceAssociation " + _influenceAssociation[1]]
            pm.mel.doMirrorSkinWeightsArgList(2, arguments)


# -----------------------------------
#   IN CLASS BUILD
# -----------------------------------


# node = Skinning('pSphere1')
# print node.getSkinCluster()
# node.extractWeight('pSphere2', 2)


# Skinning.setPreBind('toto')
