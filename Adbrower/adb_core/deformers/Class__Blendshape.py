
# -------------------------------------------------------------------
# Class Blendshape Module
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
# audreydb23@gmail.com
# -------------------------------------------------------------------

import sys
from functools import wraps

import maya.cmds as mc
import maya.mel as mel
import pymel.core as pm
from adbrower import flatList, undo


from maya.api import OpenMaya as om2
import maya.OpenMayaAnim as oma


def loadPlugin(plugin):
    if not mc.pluginInfo(plugin, query=True, loaded=True):
        try:
            mc.loadPlugin(plugin)
        except RuntimeError:
            pm.warning('could not load plugin {}'.format(plugin))

loadPlugin('adbMirrorBlsWeights__Command')


def getMDagPath(node):
    """
    Returns MDagPath of given nodepour invert les value
    """
    selList = om2.MSelectionList()
    selList.add(node)
    return selList.getDagPath(0)


def getMObject(node):
    """
    Returns MObject of given node
    """
    selList = om2.MSelectionList()
    selList.add(node)
    return selList.getDependNode(0)


def findBlendShape(_tranformToCheck):
    """
    Find the blendShape from a string
    @param _tranformToCheck: Needs to be a String!!
    """
    result = []
    if not (pm.objExists(_tranformToCheck)):
        return result
    validList = mel.eval('findRelatedDeformer("' + str(_tranformToCheck) + '")')
    if validList is None:
        return result
    for elem in validList:
        if pm.nodeType(elem) == 'blendShape':
            result.append(elem)
    return result


# -----------------------------------
# CLASS
# -----------------------------------

class Blendshape(object):
    def __init__(self,
                 bs_node=None,
                 ):

        self.bs_node = bs_node

        if isinstance(self.bs_node, list):
                self.bs_node = pm.PyNode(self.bs_node[0])


    def __repr__(self):
        return str('<{} \'{}\'>'.format(self.__class__.__name__, self.bs_node))

    @classmethod
    def create(cls, mesh, targets = [], name='blendShape', parallel=False, topology=True, foc=False):
        """
        Create a new empty blendshape node in the scene.

        @param str name: the name of the new blendshape node.
        @param str target: the name of the transform to attach the blendshape to.
        @param bool parallel: sets whether the blendshape runs in parallel to other deformers.
        @param bool topology: check whether topology matches between base and target meshes.
        @param bool foc: place new blendshape node at front of deformation chain.
        @return self
        """
        bs = pm.blendShape(mesh, parallel=parallel, tc=topology, foc=foc, n=name)[0]
        if targets is not []:
            for index, shape in enumerate(targets):
                pm.blendShape(bs, e=1, target=(mesh, index + 1, shape, 1))
                pm.setAttr('{}.weight[{}]'.format(bs, index + 1), 1)

        return cls(bs)

    @classmethod
    def findAll(cls):
        """ Return a BlendShape instance for every blendshape node in the scene. """
        all_blendshapes = []
        for blendshape_name in mc.ls(type='blendShape'):
            all_blendshapes.append(cls(blendshape_name))
        return all_blendshapes

    @classmethod
    def fromMesh(cls, mesh):
        """ Return the list of Blendshapes from selected mesh"""
        bls = findBlendShape(mesh)[0]
        return cls(bls)

    @classmethod
    def fromSelected(cls):
        """ Return the list of Blendshapes from selected mesh"""
        bls = flatList([findBlendShape(x) for x in pm.selected()])
        return [cls(bs) for bs in bls]

    @staticmethod
    def isCompnent(bs_name):
        """
        Returns True if supplied name works with BlendShape Class.
        @param str bs_name: name of a node to check
        @return bool
        """
        return pm.nodeType(bs_name) == 'blendShape'

    @property
    def mesh(self):
        transform = pm.blendShape(self.bs_node, q=1, g=1)[0]
        return pm.PyNode(transform).getTransform()

    @property
    def targets(self):
        targets = self.init_targets()
        if targets is not None:
            return targets.values()
        else:
            return []

    @property
    def targetNumber(self):
        return len(self.getTargets)

    @property
    def right_targets(self):
        right_targets = dict()
        _targetDict = self.init_targets()
        for index, alias in _targetDict.items():
            if alias[:2] == 'R_':
                right_targets[index] = alias
        return right_targets

    @property
    def left_targets(self):
        left_targets = dict()
        _targetDict = self.init_targets()
        for index, alias in _targetDict.items():
            if alias[:2] == 'L_':
                left_targets[index] = alias
        return left_targets


    @property
    def paintTargetIndex(self):
        paintTargetIndex = mc.getAttr('{}.inputTarget[0].paintTargetIndex'.format(self.bs_node))
        return paintTargetIndex


    def init_targets(self):
        if pm.objExists(self.bs_node):
            if pm.PyNode(self.bs_node).getTarget():
                return {i: pm.aliasAttr('{}.w[{}]'.format(self.bs_node, i), q=1) for i in
                        pm.getAttr('{}.w'.format(self.bs_node), multiIndices=1)}
            else:
                return None

    def get_target_index_by_alias(self, alias_name):
        for index, alias in self.targets.items():
            if alias == alias_name:
                return index
        return None


    def add_target(self, shape_to_add, value=1):
        """
        Add a shape as a target

        @target : String. Mesh getting the blendshape
        @shape_to_add : List. Shape to add to the target
        """
        numb_target = len(self.targets) + 1
        if numb_target == 0:
            numb_target = 1

        bls_node = self.bs_node
        for index, shape in enumerate(shape_to_add):
            pm.blendShape(bls_node, e=1, target=(self.mesh, index + numb_target, shape, 1))
            pm.setAttr('{}.weight[{}]'.format(self.bs_node, index + numb_target), value)
        sys.stdout.write('// Result: targets added // \n ')


    def flip_target(self, target_index, sa='X', ss=1):
        pm.blendShape(self.bs_node, e=1, ft=[0, target_index], sa=sa, ss=ss)


    def rebuild_target(self, target_index):
        return pm.sculptTarget(self.bs_node, e=1, r=1, t=target_index) or []


    def duplicate_target(self, target_index, name=None):
        new_index = mel.eval("blendShapeDuplicateTarget {} {};".format(self.bs_node, target_index))
        if name is None:
            name = '{}_DUPLICATE'.format(self.targets[target_index])
        pm.aliasAttr(name, '{}.w[{}]'.format(self.bs_node, new_index))
        return new_index


    def delete_target(self, shape_to_delete):
        for shape in shape_to_delete:
            target_index = self.get_target_index_by_alias(shape)
            mel.eval("blendShapeDeleteTargetGroup {} {};".format(self.bs_node, target_index))


    def mirror_left_to_right_targets(self, sa='X', ss=1):
        [self.delete_target([shape]) for shape in sorted(self.right_targets.values())]
        for target_index in sorted(self.left_targets.keys()):
            new_index = self.duplicate_target(target_index, name=self.targets[target_index].replace('L_', 'R_'))
            self.targets[int(new_index)] = self.targets[target_index].replace('L_', 'R_')
            self.flip_target(new_index, sa=sa, ss=ss)

    def get_weight_connection(self, index):
        return pm.listConnections('{}.w[{}]'.format(self.bs_node, index), s=1)


    @property
    def combo_targets(self):
        combo_shapes = dict()
        for target_index in self.targets.keys():
            connections = pm.listConnections('{}.w[{}]'.format(self.bs_node, target_index), s=1, d=0) or None
            if connections is not None:
                if pm.objectType(connections[0]) == 'combinationShape':
                    combo_shapes[self.targets[target_index]] = pm.listConnections(connections[0], s=1, d=0, p=1)
        return combo_shapes


    def set_combo_targets(self, combo_data):
        for combo_target_alias in combo_data.keys():
            for target_index in self.targets.keys():
                if combo_target_alias == self.targets[target_index]:
                    combination_node = pm.createNode('combinationShape', n='{}_CS'.format(combo_target_alias))
                    [pm.connectAttr(combo_data[combo_target_alias][i],
                                    '{}.inputWeight[{}]'.format(combination_node, i), f=1) for i in
                     xrange(len(combo_data[combo_target_alias]))]
                    pm.connectAttr('{}.outputWeight'.format(combination_node),
                                   '{}.{}'.format(self.bs_node, self.targets[target_index]), f=1)


    def getWeightMap(self, targetIndex = 'Auto'):
        """ Get Values of each vertex of a specific map

        Keyword Arguments:
            targetIndex {int} -- Index of the shape we want to query  (default: {0})

        Returns:
            List -- all weights values per vertex for the Base Weights Map and the Paint Target Weights
        """

        mObj = getMObject(str(self.bs_node))
        MeshDag = getMDagPath(str(self.mesh))
        blsDNode = om2.MFnDependencyNode(mObj)
        weightsPlug  = blsDNode.findPlug('inputTarget', True)
        numVerts = om2.MItMeshVertex(MeshDag).count()

        sl = om2.MSelectionList()
        sl.add("{}.inputTarget[0]".format(self.bs_node))
        weightlistIdxPlug = sl.getPlug(0)

        sl1 = om2.MSelectionList()
        sl1.add("{}.inputTarget[0].paintTargetWeights".format(self.bs_node))
        paintTargetWeightsPlug = sl1.getPlug(0)

        mc.getAttr('{0}.inputTarget[0].baseWeights[0:{1}]'.format(self.bs_node, numVerts))

        if paintTargetWeightsPlug.numElements() == 0:
            self.floodBls(self.mesh)

        if targetIndex != 'Auto':
            paintTargetIndexPlug = weightlistIdxPlug.child(4)
            paintTargetIndexPlug.setInt(targetIndex)
        else:
            pass

        baseWeigthtsList = []
        targetWeightList = []

        ## GET BASE WEIGHTS ATTRIBUTE
        baseWeights = weightlistIdxPlug.child(1)

        if baseWeights.numElements() > 2:
            for j in xrange(baseWeights.numElements()):
                baseWeightsPlugs = baseWeights.elementByLogicalIndex(j)
                baseWeightsValue =  baseWeightsPlugs.asFloat()
                baseWeigthtsList.append(baseWeightsValue)
        else:
            baseWeightsPlugs = baseWeights.elementByLogicalIndex(0)
            baseWeightsValue =  baseWeightsPlugs.asFloat()
            baseWeigthtsList += numVerts * [baseWeightsValue]

        ## GET PAINT TARGET WEIGHT ATTRIBUTE
        targetWeights = weightlistIdxPlug.child(3)

        if targetWeights.numElements() > 2:
            for j in xrange(targetWeights.numElements()):
                targetWeightsPlugs = targetWeights.elementByLogicalIndex(j)
                targetWeightsValue =  targetWeightsPlugs.asFloat()
                targetWeightList.append(targetWeightsValue)
        else:
            targetWeightsPlugs = targetWeights.elementByLogicalIndex(0)
            targetWeightsValue =  targetWeightsPlugs.asFloat()
            targetWeightList += numVerts * [targetWeightsValue]

        return baseWeigthtsList, targetWeightList


    def getWeightPlug(self, targetIndex='Auto'):
        """ Get the MPlugs of each vertex to be able to sets weights
        Keyword Arguments:
            targetIndex {int} -- Index of the shape we want to query  (default: {0})

        Returns:
            List -- MPlugs
        """
        mObj = getMObject(str(self.bs_node))
        MeshDag = getMDagPath(str(self.mesh))
        blsDNode = om2.MFnDependencyNode(mObj)
        weightsPlug  = blsDNode.findPlug('inputTarget', True)
        numVerts = om2.MItMeshVertex(MeshDag).count()

        sl = om2.MSelectionList()
        sl.add("{}.inputTarget[0]".format(self.bs_node))
        weightlistIdxPlug = sl.getPlug(0)

        sl1 = om2.MSelectionList()
        sl1.add("{}.inputTarget[0].paintTargetWeights".format(self.bs_node))
        paintTargetWeightsPlug = sl1.getPlug(0)

        mc.getAttr('{0}.inputTarget[0].baseWeights[0:{1}]'.format(self.bs_node, numVerts))
        if paintTargetWeightsPlug.numElements() == 0:
            self.floodBls(self.mesh)

        if targetIndex != 'Auto':
            paintTargetIndexPlug = weightlistIdxPlug.child(4)
            paintTargetIndexPlug.setInt(targetIndex)
        else:
            pass

        basePlugs = []
        targetPlugs = []

        ## GET BASE WEIGHTS ATTRIBUTE
        baseWeights = weightlistIdxPlug.child(1)

        if baseWeights.numElements() > 2:
            for j in xrange(baseWeights.numElements()):
                baseWeightsPlugs = baseWeights.elementByLogicalIndex(j)
                basePlugs.append(baseWeightsPlugs)
        else:
            baseWeightsPlugs = baseWeights.elementByLogicalIndex(0)
            basePlugs += numVerts * [baseWeightsPlugs]

        ## GET PAINT TARGET WEIGHT ATTRIBUTE
        targetWeights = weightlistIdxPlug.child(3)

        if targetWeights.numElements() > 2:
            for j in xrange(targetWeights.numElements()):
                targetWeightsPlugs = targetWeights.elementByLogicalIndex(j)
                targetPlugs.append(targetWeightsPlugs)
        else:
            targetWeightsPlugs = targetWeights.elementByLogicalIndex(0)
            targetPlugs += numVerts * [targetWeightsPlugs]

        return basePlugs, targetPlugs


    def setWeightMap(self, allPlugs, allWeights):
        """ Set new values to a map

        Arguments:
            allPlugs {List} -- Mplugs
            allWeights {List} -- Weights Values
        """
        for plug, value in zip(allPlugs, allWeights):
            plug.setFloat(value)


    def invertWeight(self, baseWeight=False):
        """Invert current Weight value of each vertex

        Keyword Arguments:
            baseWeight {Bool} -- To invert the base layer  (default: False)
        """
        mObj = getMObject(str(self.bs_node))
        MeshDag = getMDagPath(str(self.mesh))
        blsDNode = om2.MFnDependencyNode(mObj)
        weightsPlug  = blsDNode.findPlug('inputTarget', True)
        numVerts = om2.MItMeshVertex(MeshDag).count()

        sl = om2.MSelectionList()
        sl.add("{}.inputTarget[0]".format(self.bs_node))
        weightlistIdxPlug = sl.getPlug(0)

        sl1 = om2.MSelectionList()
        sl1.add("{}.inputTarget[0].paintTargetWeights".format(self.bs_node))
        paintTargetWeightsPlug = sl1.getPlug(0)

        mc.getAttr('{0}.inputTarget[0].baseWeights[0:{1}]'.format(self.bs_node, numVerts))

        if paintTargetWeightsPlug.numElements() == 0:
            self.floodBls(self.mesh)

        if baseWeight:
            ## GET BASE WEIGHTS ATTRIBUTE
            baseWeights = weightlistIdxPlug.child(1)

            for j in xrange(numVerts):
                baseWeightsPlugs = baseWeights.elementByLogicalIndex(j)
                baseWeightsValue =  baseWeightsPlugs.asFloat()
                baseWeightsPlugs.setFloat(1-baseWeightsValue)
        else:
            ## GET PAINT TARGET WEIGHT ATTRIBUTE
            targetWeights = weightlistIdxPlug.child(3)

            for j in xrange(numVerts):
                targetWeightsPlugs = targetWeights.elementByLogicalIndex(j)
                targetWeightsValue =  targetWeightsPlugs.asFloat()
                targetWeightsPlugs.setFloat(1-targetWeightsValue)


    def mirrorMap(self, center_edge, mirror_src='RIGHT'):
        """Mirror Weight Map

        Arguments:
            center_edge {String} -- Edge from with we separate Left from Right
            mirror_src {String} -- LEFT or RIGHT

        """
        mc.mirrorBlsWeights(ce=center_edge, side=mirror_src)


    @staticmethod
    def floodBls(transform):
        pm.select(transform, r=1)
        if len(pm.ls(sl=1)) == 0:
            pm.warning('Select a Mesh!')
        # if we're not currently in the paint skin weights tool context, get us into it
        if pm.currentCtx() != "artAttrBlendShapeContext":
            mel.eval("ArtPaintBlendShapeWeightsTool;")

        # first get the current settings so that the user doesn't have to switch back
        currOp = pm.artAttrCtx(pm.currentCtx(), q=1, selectedattroper=1)
        currValue = pm.artAttrCtx(pm.currentCtx(), q=1, value=1)

        # flood the current selection to zero
        # first set our tool to the selected operation and value
        pm.artAttrCtx(pm.currentCtx(), e=1, selectedattroper="absolute")
        pm.artAttrCtx(pm.currentCtx(), e=1, value=0)

        pm.artAttrCtx(pm.currentCtx(), e=1, clear=1)
        # # set the tools back to the way you found them
        pm.artAttrCtx(pm.currentCtx(), e=1, selectedattroper=currOp)
        pm.artAttrCtx(pm.currentCtx(), e=1, value=currValue)


class PI(object):
    def __init__(self, node):
        self._shape = None
        self._node = node

    @classmethod
    def findAll(cls):
        """ Return a bs instance for every cluster node in the scene. """
        all_pi = []
        for pi_name in pm.ls(type='poseInterpolator'):
            all_pi.append(cls(pi_name))
        return all_pi

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, value):
        if self.shape:
            self._node = value
        else:
            mc.error('The node is not a valid Pose Interpolator')

    @property
    def side(self):
        return self.node[:1]

    @property
    def shape(self):
        if mc.objectType(self.node) == 'transform':
            shape = mc.listRelatives(self.node, s=1)[0]
            if mc.objectType(shape) == 'poseInterpolator':
                return shape
            else:
                return None
        if mc.objectType(self.node) == 'poseInterpolator':
            self.shape = self.node
            self.node = mc.listRelatives(self.node, p=1)
            return self.shape
        return None

    @shape.setter
    def shape(self, value):
        self._shape = value

    @property
    def drivers(self):
        return mc.poseInterpolator(self.node, q=1, d=1)

    @property
    def poses_names(self):
        return mc.poseInterpolator(self.node, q=1, pn=1)

    @property
    def poses_string(self):
        poses_str = ''
        for pose in self.poses_names:
            poses_str += '"{}", '.format(pose)
        return poses_str

    def get_driver_twist_axis(self, driver_index):
        return mc.getAttr('{}.driver[{}].driverTwistAxis'.format(self.shape, driver_index))

    def set_driver_twist_axis(self, driver_index, value):
        return mc.setAttr('{}.driver[{}].driverTwistAxis'.format(self.shape, driver_index), value)

    @property
    def interpolation(self):
        return mc.getAttr('{}.interpolation'.format(self.shape))

    @interpolation.setter
    def interpolation(self, value):
        mc.setAttr('{}.interpolation'.format(self.shape), value)

    def mirror_driver(self, left_to_right=True):
        if left_to_right:
            for driver in self.drivers:
                new_driver_name = 'R_{}'.format(driver[2:])
                if not mc.objExists(new_driver_name):
                    driver_parent = mc.listRelatives(driver, p=1)[0]
                    target_parent = mc.listConnections('{}.target[0].targetParentMatrix'.format(
                        mc.listConnections(str(driver) + '.rotateX', s=1)[0]), s=1)[0]

                    mirrored_parent = driver_parent if driver_parent[:1] == 'C' else 'R_{}'.format(driver_parent[2:])
                    mirrored_target = target_parent if target_parent[:1] == 'C'else 'R_{}'.format(target_parent[2:])

                    self.createCorrectiveShapeDriver(new_driver_name, mirrored_target, mirrored_parent)
                else:
                    mc.warning('The mirrored driver: {}, already exists'.format(new_driver_name))

    def mirror(self):
        if self.side == 'L':
            opposite_pose_interpoltor = 'R_{}'.format(self.node[2:])
            self.mirror_driver()
            # delete the opposite  pose interpolator
            if mc.objExists(opposite_pose_interpoltor):
                mc.delete(opposite_pose_interpoltor)
            command = 'poseInterpolatorMirror("' + self.node + '", {%s},  "L_", "R_", 1, 1, 1);' % (
                self.poses_string[:-2])
            command.replace("''", '"')
            mirrored_pose_interpolator = PI(mel.eval(command))
            mirrored_pose_interpolator.interpolation = self.interpolation
            for i in xrange(len(self.drivers)):
                mirrored_pose_interpolator.set_driver_twist_axis(i, self.get_driver_twist_axis(i))

        elif self.side == 'R':
            opposite = 'L'
        else:
            mc.error('Side: {} not supported'.format(self.side))

    @staticmethod
    def createCorrectiveShapeDriver(target, parent):
        """
        Creates a joint under the parent, snapped and orient constrained to the target.
        This can be used to drive corrective shapes using local rotation.
        :param str nffame: driver name
        :param str target: target transform that drives the corrective shape
        :param str parent: parent transform
        :return str: driver
        """
        name = '{}_DRVR'.format(target)
        driver = mc.createNode('joint', skipSelect=True, name=name, parent=parent)
        mc.delete(mc.orientConstraint(target, driver))
        mc.makeIdentity(driver, apply=True, rotate=True)
        mc.orientConstraint(target, driver)
        return driver

    @staticmethod
    def _createPoseInterator(name=None, driver=None, control=None):
        """
        Create a new poseInterpolator.
        :param str name: component name
        :param str driver: driver (joint)
        :param str control: control that rotates the joint
        :return PoseInterpolator: component
        """
        node = driver + str('_DRVR')
        pose_node = mc.createNode('poseInterpolator', skipSelect=True, n='{}Shape'.format(node))

        # Connect to the manager to update the UI
        manager = 'poseInterpolatorManager'
        new_index = (mc.getAttr('{}.poseInterpolatorParent'.format(manager), multiIndices=True) or [-1])[-1] + 1
        mc.connectAttr(str(pose_node) + '.midLayerParent', ' poseInterpolatorManager.poseInterpolatorParent[{}]'.format(new_index))

        # Connect the joint
        if driver is not None:
            mc.connectAttr('{}.matrix'.format(driver), '{}.driver[0].driverMatrix'.format(node))
            mc.connectAttr('{}.jointOrient'.format(driver), '{}.driver[0].driverOrient'.format(node))
            mc.connectAttr('{}.rotateAxis'.format(driver), '{}.driver[0].driverRotateAxis'.format(node))
            mc.connectAttr('{}.rotateOrder'.format(driver), '{}.driver[0].driverRotateOrder'.format(node))

        # Connect the rotation of the controller
        if control is not None:
            for i, axis in enumerate('XYZ'):
                mc.connectAttr('{}.rotate{}'.format(control, axis), '{}.driver[0].driverController[{}]'.format(node, i))

    @staticmethod
    def createPoseInterator(target, parent):
        driver = createCorrectiveShapeDriver(target, parent)
        createPoseInterator(name='{}_PINT', driver=driver)


def mirror_left_to_right_poses(bs_node):
    bs = Blendshape(bs_node)
    combo_data = bs.combo_targets
    bs.mirror_left_to_right_targets()

    pose_interpolators = [PI(mc.listRelatives(pose_interpolator, p=1)[0]) for pose_interpolator in
                          mc.ls(typ='poseInterpolator')]
    [mc.delete(pose_interpolator.node) for pose_interpolator in pose_interpolators if pose_interpolator.side == 'R']
    left_pose_interpolators = [pose_interpolator for pose_interpolator in pose_interpolators if
                               pose_interpolator.side == 'L']
    [pose_interpolator.mirror() for pose_interpolator in left_pose_interpolators]
    bs.set_combo_targets(combo_data)


