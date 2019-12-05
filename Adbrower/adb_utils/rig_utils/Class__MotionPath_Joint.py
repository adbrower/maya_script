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

import adbrower
import maya.cmds as mc
import pymel.core as pm

adb = adbrower.Adbrower()

# -----------------------------------
# CLASS
# -----------------------------------


class MotionPathJnt(object):
    """
    Class that creates joints equally on a curve with motion path node

    @param intervals: Integer. Number of joint to create
    @param curve: String. The curve used to create the joints. Default value is pm.selected().


    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_utils.Class__MotionPath_Joint as adbMPJ
    reload(adbMPJ)

    mpj = adbMPJ.MotionPathJnt(20)


    """

    def __init__(self, invervals, curve=pm.selected()):
        self._interval = invervals
        self._curve = curve
        self.all_jnts = []
        self.all_motionPath = []
        self.Pos = []
        self._radius = 1

        self.build()

    @property
    def getJoints(self):
        return self.all_jnts

    @property
    def motionPaths(self):
        return self.all_motionPath

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
        self.all_motionPath = []
        self.Pos = []

        self.all_jnts = [pm.joint(rad=self._radius) for x in range(self._interval)]
        for _joint in self.all_jnts:
            pm.parent(_joint, w=True)
            adb.makeroot_func(_joint)
            
            double_linears_nodes = []
            _motionPathNode = pm.pathAnimation(self._curve,_joint.getParent(), upAxis='y', fractionMode=True,
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

            self.all_motionPath.append(_motionPathNode)
            
        # New interval value for the Function
        Nintervalls = self._interval - 1

        for i in range(0, Nintervalls):
            factor = 1 / float((Nintervalls))
            oPos = factor * i
            self.Pos.append(oPos)
        self.Pos.append(1)

        for oPosition, oMotionPath in zip(self.Pos, self.all_motionPath):
            pm.PyNode(oMotionPath).uValue.set(oPosition)

        _dup = pm.duplicate(self.all_jnts[-1])

        # delete animation
        for path in self.all_motionPath:
            _motion_uvalue_node = [x for x in pm.listConnections(path + '.uValue', s=1)]
            pm.delete(_motion_uvalue_node)

        for joint in self.all_jnts:
            joint.jointOrientX.set(0)
            joint.jointOrientY.set(0)
            joint.jointOrientZ.set(0)

            joint.rx.set(0)
            joint.ry.set(0)
            joint.rz.set(0)

        pm.select(None)

        # Cleaning the scene
        pm.delete(_dup)

        # Delete Motion Path
        # pm.delete(self.all_motionPath)

    def deleteSetUp(self):
        """Delete the Set Up """
        for joint in self.all_jnts:
            pm.delete(joint.getParent())

    def add(self):
        """Add a joint """
        actual_intv = self.interval
        self.interval = actual_intv + 1

    def minus(self):
        """ Delete a joint"""
        actual_intv = self.interval
        self.interval = actual_intv - 1


# mpj = MotionPathJnt(5)
# mpj.radius = 0.2
