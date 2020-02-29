
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
        if bs_node:
            self.bs_node = pm.PyNode(bs_node)
            self.targets = self.init_targets()
        else:
            bs_node = None

    def __repr__(self):
        return str('<{} \'{}\'>'.format(self.__class__.__name__, self.bs_node))

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
    def getTransform(self):
        transform = pm.blendShape(self.bs_node, q=1, g=1)[0]
        return pm.PyNode(transform).getTransform()

    @property
    def getTargets(self):
        all_targets = self.init_targets()
        return all_targets.values()

    @property
    def getTargetsNumber(self):
        return len(self.getTargets)

    @property
    def right_targets(self):
        right_targets = dict()
        for index, alias in self.targets.items():
            if alias[:2] == 'R_':
                right_targets[index] = alias
        return right_targets

    @property
    def left_targets(self):
        left_targets = dict()
        for index, alias in self.targets.items():
            if alias[:2] == 'L_':
                left_targets[index] = alias
        return left_targets

    def create(self, name=None, target=None,  parallel=False, topology=True, foc=False):
        """
        Create a new empty blendshape node in the scene.

        @param str name: the name of the new blendshape node.
        @param str target: the name of the transform to attach the blendshape to.
        @param bool parallel: sets whether the blendshape runs in parallel to other deformers.
        @param bool topology: check whether topology matches between base and target meshes.
        @param bool foc: place new blendshape node at front of deformation chain.
        @return self
        """
        self.target = target
        if not name:
            name = self.name
        shape = pm.PyNode(self.target).getShape()
        self.bs = pm.blendShape(shape, parallel=parallel, tc=topology, foc=foc, n=name)[0]
        return self.bs

    def init_targets(self):
        if pm.objExists(self.bs_node):
            return {i: pm.aliasAttr('{}.w[{}]'.format(self.bs_node, i), q=1) for i in
                    pm.getAttr('{}.w'.format(self.bs_node), multiIndices=1)}

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

        numb_target = len(self.getTargets)
        if numb_target == 0:
            numb_target = 1

        bls_node = self.bs_node
        for index, shape in enumerate(shape_to_add):
            pm.blendShape(bls_node, e=1, target=(self.getTransform, index + numb_target, shape, 1))
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
    import pprint
    pprint.pprint(bs.targets)
    pose_interpolators = [PI(mc.listRelatives(pose_interpolator, p=1)[0]) for pose_interpolator in
                          mc.ls(typ='poseInterpolator')]
    [mc.delete(pose_interpolator.node) for pose_interpolator in pose_interpolators if pose_interpolator.side == 'R']
    left_pose_interpolators = [pose_interpolator for pose_interpolator in pose_interpolators if
                               pose_interpolator.side == 'L']
    [pose_interpolator.mirror() for pose_interpolator in left_pose_interpolators]
    bs.set_combo_targets(combo_data)


