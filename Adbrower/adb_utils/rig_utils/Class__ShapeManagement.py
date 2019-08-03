# -------------------------------------------------------------------
# adb Class Shape Management
# -- Version 1.0.0
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
import ShapesLibrary as sl
from adbrower import changeColor

adb = adbrower.Adbrower()

# -----------------------------------
# CLASS
# -----------------------------------


class shapeManagement(object):
    """
    Shape Management Module
    Replace Shape according to the ShapesLibrary.py file. Mostly used for nurbs curve controls.

    @param subject: Single string or a list. Default value is pm.selected()

    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_utils.rig_utils.Class__ShapeManagement as adbShape
    reload (adbShape)

    sm = adbShape.shapeManagement()
    sm.shapes = sl.diamond_shape

    """

    def __init__(self,
                 subject=pm.selected(),
                 ):

        self._nodeType = type(subject)
        if self._nodeType == str:
            self.subject = [pm.PyNode(subject)]
        else:
            self.subject = [pm.PyNode(x) for x in subject]

        self.old_ctrl = None
        self.new_ctrl = None

        self.all_new_shape = []

    @property
    def shapes(self):
        return (self.all_new_shape)

    @shapes.setter
    def shapes(self, name):
        for ctrl in self.subject:
            self.replaceShape(old_ctrl=ctrl, new_ctrl=name)

    @changeColor()
    def replaceShape(self, old_ctrl=pm.selected(), new_ctrl=None):
        """
        Replacing shape function

        @param old_ctrl: The controller that you want to change the shape
        @param new_ctrl: The new shape you want to give to your old controller

        """
        self.old_ctrl = old_ctrl
        self.new_ctrl = new_ctrl()

        pm.select(self.old_ctrl, add=True)

        self.new_shape = pm.selected()[0]
        self.old_shape = pm.selected()[1]

        # Duplicate source and move to target location
        self.new_shape_dup = pm.duplicate(self.new_shape, rc=True)
        pm.matchTransform(self.new_shape_dup[0], self.old_shape, pos=True, rot=True)

        # Parent source to target's parent
        pm.parent(self.new_shape_dup, self.old_shape.getTransform())
        pm.makeIdentity(self.new_shape_dup, apply=True, t=1, r=1, s=1)

        # Get transforms and shapes of source and target
        self.new_shape_getShape = pm.PyNode(self.new_shape_dup[0]).getShapes()
        self.old_shape_getShape = pm.PyNode(self.old_shape).getShapes()

        # Parent shapes of source to target
        for srcShapes in self.new_shape_getShape:
            pm.parent(srcShapes, self.old_shape, add=True, s=True)

        # Clean up
        pm.delete(self.new_shape_dup)
        pm.delete(self.old_shape_getShape)
        pm.delete(self.new_ctrl)

        self.all_new_shape.append(self.old_shape)
        return self.all_new_shape


# sm = shapeManagement()
# sm.shapes = sl.double_pin_shape
