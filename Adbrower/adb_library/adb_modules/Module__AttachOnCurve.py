import sys
import traceback
import pymel.core as pm
import maya.cmds as mc
from pprint import pprint

import adbrower
adb = adbrower.Adbrower()


class PointToCurveJnt(object):
    """
    Class that creates joints equally on a curve with point to curve node

    @param intervals: Integer. Number of joint to create
    @param curve: String. The curve used to create the joints. Default value is pm.selected().


    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_utils.rig_utils.Class__AttachOnCurve as adb_PointonCurve
    reload(adb_PointonCurve)

    poc = adb_PointonCurve.PointToCurveJnt(20, sel=pm.selected())
    """

    def __init__(self, intervals, sel=pm.selected()):
        self._interval = intervals
        self._curve = sel
        self.all_jnts = []
        self.all_pointOnCurve_nodes = []
        self.Pos = []
        self._radius = 1

        self.build()

    @property
    def getJoints(self):
        return self.all_jnts

    @property
    def nodes(self):
        return self.all_pointOnCurve_nodes

    @property
    def getCurve(self):
        return self._curve

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, number):
        try:
            self._interval = number
            self.deleteSetUp()
            self.build()
            sys.stdout.write('New intervals: {}'.format(number))

        except IndexError:
            sys.stdout.write('New intervals: {}'.format(number))

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, rad):
        for joint in self.getJoints:
            joint.radius.set(rad)

        self._radius = rad

    def build(self):
        """ Build system"""
        self.all_jnts = []
        self.all_pointOnCurve_nodes = []
        self.Pos = []

        # Creation of all joints
        self.all_jnts = [pm.joint(rad=self._radius) for x in range(self._interval)]
        for joint in self.all_jnts:
            pm.parent(joint, w=True)
            adb.makeroot_func(joint)

        # Creation of Point to Curve Nodes
        self.all_pointOnCurve_nodes = [pm.pointOnCurve(self._curve, ch=True, top=True) for x in range(self._interval)]

        for node, joint in zip(self.all_pointOnCurve_nodes, self.all_jnts):
            pm.PyNode(node).positionX >> (pm.PyNode(joint).getParent()).translateX
            pm.PyNode(node).positionY >> (pm.PyNode(joint).getParent()).translateY
            pm.PyNode(node).positionZ >> (pm.PyNode(joint).getParent()).translateZ

        # Find all position
        Nintervalls = self._interval - 1
        for i in range(0, Nintervalls):
            factor = 1 / float((Nintervalls))
            oPos = factor * i
            self.Pos.append(oPos)
        self.Pos.append(1)

        for oPosition, oNode in zip(self.Pos, self.all_pointOnCurve_nodes):
            pm.PyNode(oNode).parameter.set(oPosition)

        pm.select(None)

        # # Delete Point On Curve
        # pm.refresh()
        # pm.delete(self.all_pointOnCurve_nodes)

    def deleteSetUp(self):
        """Delete the Set Up """
        for joint in self.all_jnts:
            pm.delete(joint.getParent())

    def rebuildCurve(self, number):
        """Rebuild the curve so the joints are more evenly placed """
        pm.rebuildCurve(self._curve, rt=0, ch=0, end=1, d=3, kr=0, s=number, kcp=0, tol=0.1, kt=0, rpo=1, kep=1)
        sys.stdout.write('The Curve has been rebuild with {} vertex'.format(number))

    def add(self):
        """Add a joint """
        actual_intv = self.interval
        self.interval = actual_intv + 1

    def minus(self):
        """ Delete a joint"""
        actual_intv = self.interval
        self.interval = actual_intv - 1


# ptc = PointToCurveJnt(13)

# ptc.radius = 0.2


# nodes = ptc.all_pointOnCurve_nodes


# jnts =['L_lowerEyeLid_01', 'L_lowerEyeLid_02', 'L_lowerEyeLid_03', 'L_lowerEyeLid_04', 'L_lowerEyeLid_05', 'L_lowerEyeLid_06', 'L_lowerEyeLid_07', 'L_lowerEyeLid_08', 'L_lowerEyeLid_09', 'L_lowerEyeLid_010', 'L_lowerEyeLid_011', 'L_lowerEyeLid_012', 'L_lowerEyeLid_013']


# for each, node in zip(jnts, nodes) :
#     pm.matchTransform('cpConstraintIn', each, pos=1)
#     par = pm.PyNode('nearestPointOnCurve1').parameter.get()
#     pm.PyNode(node).parameter.set(par)
