# ------------------------------------------------------
# adbrower Module
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import sys
import traceback
from pprint import pprint

import maya.cmds as mc
import pymel.core as pm


class OrientJoint(object):
    """
    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_utils.rig_utils.Class__OrientJoint as adbOrient
    reload (adbOrient)

    comp = adbOrient.OrientJoint()
    comp.OrientAxis = 'Y'
    """

    def __init__(self,
                 sel=pm.selected(),
                 orientAxe='Y',
                 ):

        selection = [pm.PyNode(x) for x in sel]
        self.selection = selection
        self.orientAxe = orientAxe,

        # self.orientJoint()

    @property
    def jointToOrient(self):
        return self.selection

    @property
    def OrientAxis(self):
        return self.orientAxe[0]

    @OrientAxis.setter
    def OrientAxis(self, axis):
        self.orientAxe = axis
        self.orientJoint()
        sys.stdout.write('The joints were oriented with the {} axis \n'.format(axis))

    def orientJoint(self):
        if self.orientAxe[0] == 'Y':
            pm.select(self.selection)
            pm.joint(zso=1, ch=1, e=1, oj='yxz', secondaryAxisOrient='xdown')
            pm.select(cl=True)

            #Orient the last joint to the world#
            selLastJnt = pm.select(self.selection[-1])
            pm.joint(e=1, oj='none')
            pm.select(None)

        elif self.orientAxe[0] == 'y':
            pm.select(self.selection)
            pm.joint(zso=1, ch=1, e=1, oj='yxz', secondaryAxisOrient='xup')
            pm.select(cl=True)

            #Orient the last joint to the world#
            selLastJnt = pm.select(self.selection[-1])
            pm.joint(e=1, oj='none')
            pm.select(None)

        elif self.orientAxe[0] == 'X':
            pm.select(self.selection)
            pm.joint(zso=1, ch=1, e=1, oj='xyz', secondaryAxisOrient='xup')
            pm.select(cl=True)

            #Orient the last joint to the world#
            selLastJnt = pm.select(self.selection[-1])
            pm.joint(e=1, oj='none')
            pm.select(None)

        elif self.orientAxe[0] == 'x':
            pm.select(self.selection)
            pm.joint(zso=1, ch=1, e=1, oj='xyz', secondaryAxisOrient='xdown')
            pm.select(cl=True)

            #Orient the last joint to the world#
            selLastJnt = pm.select(self.selection[-1])
            pm.joint(e=1, oj='none')
            pm.select(None)

        else:
            raise ValueError('That Axis does not exist')


# comp = OrientJoint()
# print comp.OrientAxis
# comp.OrientAxis = 'x'

# comp.OrientAxis = 'y'

# print comp.OrientAxis
