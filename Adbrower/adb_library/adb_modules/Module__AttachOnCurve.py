import sys
import traceback
import pymel.core as pm
import maya.cmds as mc
from pprint import pprint

from adbrower import changeColor, undo

import adb_core.ModuleBase as moduleBase
import adb_core.NameConv_utils as NC
import adb_core.Class__Joint as Joint

import adbrower
adb = adbrower.Adbrower()


class PointToCurveJntModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(PointToCurveJntModel, self).__init__()
        self.pointOnCurveNodes = []
        self.interval = None
        self.curve = None
        self.radius = 1


class PointToCurveJnt(moduleBase.ModuleBase):
    """
    Class that creates joints equally on a curve with point to curve node

    @param intervals: Integer. Number of joint to create
    @param curve: String. The curve used to create the joints. Default value is pm.selected().


    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_library.adb_modules.Module__AttachOnCurve as adb_PointonCurve
    reload(adb_PointonCurve)

    ptc = adb_PointonCurve.PointToCurveJnt('aaaa', 7, 'spineGuide__CRV')
    ptc.start()
    ptc.build()

    """

    def __init__(self,
                 module_name,
                 intervals = 3,
                 curve= None):
        super(PointToCurveJnt, self).__init__()

        self._MODEL = PointToCurveJntModel()

        self.CLASS_NAME = self.__class__.__name__
        self.NAME = module_name

        self._MODEL.interval = intervals
        self._MODEL.curve = curve
        self.Pos = []
        self._MODEL.radius = 1


    @property
    def pointOnCurveNodes(self):
        return self._MODEL.pointOnCurveNodes

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

    def start(self, metaDataNode = None):
        super(PointToCurveJnt, self)._start(self.NAME, _metaDataNode = metaDataNode)
        pass


    def build(self):
        super(PointToCurveJnt, self)._build()

        self.pointOnCurve_setup()
        self.setFinalHiearchy(RIG_GRP_LIST = [self._MODEL.curve],
                              INPUT_GRP_LIST = [x.getParent() for x in self._MODEL.getJoints],
                              OUTPUT_GRP_LIST = [],
                              )


    # =========================
    # SOLVERS
    # =========================


    def pointOnCurve_setup(self):
        self.Pos = []

        # Creation of all joints
        self._MODEL.getJoints = Joint.Joint.create(numb=self.interval, name='{}__{}'.format(self.NAME, NC.JOINT), rad=self._MODEL.radius, padding=2).joints
        for joint in self._MODEL.getJoints:
            pm.parent(joint, w=True)
            adb.makeroot_func(joint)

        # Creation of Point to Curve Nodes
        self._MODEL.pointOnCurveNodes = [pm.pointOnCurve(self._MODEL.curve, ch=True, top=True) for x in range(self._MODEL.interval)]

        for node, joint in zip(self._MODEL.pointOnCurveNodes, self._MODEL.getJoints):
            pm.PyNode(node).positionX >> (pm.PyNode(joint).getParent()).translateX
            pm.PyNode(node).positionY >> (pm.PyNode(joint).getParent()).translateY
            pm.PyNode(node).positionZ >> (pm.PyNode(joint).getParent()).translateZ

        # Find all position
        Nintervalls = self._MODEL.interval - 1
        for i in range(0, Nintervalls):
            factor = 1 / float((Nintervalls))
            oPos = factor * i
            self.Pos.append(oPos)
        self.Pos.append(1)

        for oPosition, oNode in zip(self.Pos, self._MODEL.pointOnCurveNodes):
            pm.PyNode(oNode).parameter.set(oPosition)

        pm.select(None)

    def deleteSetUp(self):
        """Delete the Set Up """
        for joint in self._MODEL.getJoint:
            pm.delete(joint.getParent())

        # # Delete Point On Curve
        # pm.refresh()
        # pm.delete(self._MODEL.pointOnCurveNodes)

    def rebuildCurve(self, number):
        """Rebuild the curve so the joints are more evenly placed """
        pm.rebuildCurve(self._MODEL.curve, rt=0, ch=0, end=1, d=3, kr=0, s=number, kcp=0, tol=0.1, kt=0, rpo=1, kep=1)
        sys.stdout.write('The Curve has been rebuild with {} vertex'.format(number))

    def add(self):
        """Add a joint """
        actual_intv = self.interval
        self.interval = actual_intv + 1

    def minus(self):
        """ Delete a joint"""
        actual_intv = self.interval
        self.interval = actual_intv - 1

