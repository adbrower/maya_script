# -------------------------------------------------------------------
# Creating joints on a curve
# -- Version 2.0.0
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# -------------------------------------------------------------------

import sys
import traceback
from pprint import pprint

import maya.cmds as mc
import pymel.core as pm

import adb_core.ModuleBase as moduleBase
reload(moduleBase)
import adbrower

adb = adbrower.Adbrower()


# -----------------------------------
# CLASS
# -----------------------------------

class MotionPathJntModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(MotionPathJntModel, self).__init__()
        self.motionPaths = []
        self.interval = None
        self.curve = None
        self.radius = 1

class MotionPathJnt(moduleBase.ModuleBase):
    """
    Class that creates joints equally on a curve with motion path node

    @param intervals: Integer. Number of joint to create
    @param curve: String. The curve used to create the joints. Default value is pm.selected().


    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_utils.Class__MotionPath_Joint as adbMPJ
    reload(adbMPJ)

    mpj = MotionPathJnt('test', 5, 'curve1')
    mpj.start()
    mpj.build()

    """
    def __init__(self, 
                module_name,
                invervals, 
                curve=pm.selected()):
        super(MotionPathJnt, self).__init__()

        self._MODEL = MotionPathJntModel()

        self.CLASS_NAME = self.__class__.__name__
        self.NAME = module_name

        self._MODEL.interval = invervals
        self._MODEL.curve = curve
        self._MODEL.radius = 1

    # =========================
    # PROPERTY
    # =========================

    @property
    def motionPaths(self):
        return self._MODEL.motionPaths

    @property
    def curve(self):
        return self._MODEL.curve

    @property
    def interval(self):
        return self._MODEL.interval

    @interval.setter
    def interval(self, number):
        try:
            self._MODEL.interval = number
            self.deleteSetUp()
            self.build()
            sys.stdout.write('New intervals: {}'.format(number))

        except IndexError:
            sys.stdout.write('New intervals: {}'.format(number))

    @property
    def radius(self):
        return self._MODEL.radius

    @radius.setter
    def radius(self, rad):
        for joint in self.getJoints:
            joint.radius.set(rad)
        self._MODEL.radius = rad

    # =========================
    # METHOD
    # =========================

    def start(self, _metaDataNode = 'transform'):
        super(MotionPathJnt, self)._start(metaDataNode = _metaDataNode)  

    def build(self):
        super(MotionPathJnt, self)._build()

        self.motionPath_setup()
        self.setFinalHiearchy(RIG_GRP_LIST = [self._MODEL.curve],
                              INPUT_GRP_LIST = [x.getParent() for x in self._MODEL.getJoints],
                              OUTPUT_GRP_LIST = [],
                              )

    # =========================
    # SOLVERS
    # =========================

    def motionPath_setup(self):
        pos = []
        self._MODEL.getJoints = [pm.joint(rad=self._MODEL.radius) for x in range(self._MODEL.interval)]
        for _joint in self._MODEL.getJoints:
            pm.parent(_joint, w=True)
            adb.makeroot_func(_joint)
            
            double_linears_nodes = []
            _motionPathNode = pm.pathAnimation(self._MODEL.curve,_joint.getParent(), upAxis='y', fractionMode=True,
                                               worldUpType="vector",
                                               inverseUp=False, inverseFront=False, follow=True, bank=False, followAxis='x',
                                               worldUpVector=(0, 1, 0))

            ## Delete double Linear nodes
            for axis in 'xyz':
                double_linear = pm.listConnections(_motionPathNode + '.{}Coordinate'.format(axis))[0]
                double_linears_nodes.append(double_linear)

            pm.delete(double_linears_nodes)
            
            for axis in 'xyz':
                pm.cycleCheck(e=1)
                pm.connectAttr('{}.{}Coordinate'.format(_motionPathNode, axis), '{}.t{}'.format(_joint.getParent(), axis), f=1)

            self._MODEL.motionPaths.append(_motionPathNode)
            
        # New interval value for the Function
        Nintervalls = self._MODEL.interval - 1

        for i in range(0, Nintervalls):
            factor = 1 / float((Nintervalls))
            oPos = factor * i
            pos.append(oPos)
        pos.append(1)

        for oPosition, oMotionPath in zip(pos, self._MODEL.motionPaths):
            pm.PyNode(oMotionPath).uValue.set(oPosition)

        _dup = pm.duplicate(self._MODEL.getJoints[-1])

        # delete animation
        for path in self._MODEL.motionPaths:
            pm.cutKey(path)

        for joint in self._MODEL.getJoints:
            joint.jointOrient.set(0, 0, 0)
            joint.translate.set(0, 0, 0)

        pm.select(None)

        # Cleaning the scene
        pm.delete(_dup)

    def deleteMotionPathNodes(self):
        pm.delete(self._MODEL.motionPaths)

    def deleteSetUp(self):
        """Delete the Set Up """
        for joint in self._MODEL.getJoints:
            pm.delete(joint.getParent())

    def add(self):
        """Add a joint """
        actual_intv = self.interval
        self.interval = actual_intv + 1

    def minus(self):
        """ Delete a joint"""
        actual_intv = self.interval
        self.interval = actual_intv - 1

# mpj = MotionPathJnt('test', 5, 'curve1')
# mpj.start()
# mpj.build()

