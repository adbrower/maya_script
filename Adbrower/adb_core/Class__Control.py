# -------------------------------------------------------------------
# Class Control
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# -------------------------------------------------------------------

import pymel.core as pm

import ShapesLibrary as sl
import adb_core.Class__Transforms as adbTransform
import adbrower
reload(adbrower)

adb = adbrower.Adbrower()

from adbrower import changeColor, propScale
from CollDict import colordic

class Control(object):
    """
    Creating Control

    ## EXTERIOR CLASS BUILD
    #------------------------

        control = Control('test', sl.cube_shape, 5)

    """

    def __init__(self, name, shape, scale=1, parent=None, matchTransforms=(False, 0, 0)):
        self.name = name
        self._shape = shape
        self.scale = scale
        self.parent = parent
        self.matchTransforms = matchTransforms

        self.create()


    #===================
    # PROPERTIES
    #===================

    @property
    def shape(self):
        return (self._shape)

    @shape.setter
    def shape(self, name):
        sm = ShapeManagement([self.control])
        sm.shape = name


    @changeColor()
    def create(self):
        self.control = self._shape()
        pm.rename(self.control, self.name)
        adb.AutoSuffix([self.control])
        self.control.scale.set(self.scale, self.scale, self.scale)
        pm.makeIdentity(self.control, n=0, s=1, r=1, t=1, apply=True, pn=1)
        if self.matchTransforms[0] is not False:
            pm.matchTransform(self.control, self.matchTransforms[0], pos =self.matchTransforms[1], rot=self.matchTransforms[2] )

        if self.parent:
            pm.parent(self.control, self.parent)
        return self.control

    def freezeCvs(self):
        """ Freeze all the cvs of a curve """
        mc.DeleteHistory(self.control)
        cluster = pm.cluster(self.control)
        pm.delete(cluster)
        return self.control

    def resetCvs(self):
        curve_name = self.control.name()
        pm.rename(self.control, 'temp')
        shape = self.control.getShape()
        cvs_num = len(pm.PyNode(self.control).getCVs())

        for number in range(0, cvs_num):
            for axis in 'xyz':
                pm.setAttr('{}.controlPoints[{}].{}Value'.format(
                    shape, number, axis), 0)
        pm.rename(self.control, curve_name)

    def selectNurbsVertx(self):
        """ Select All cvs of selected nurbs curve """
        _shapes = pm.PyNode(self.control).getShapes()
        pm.select('{}.cv[:]'.format(_shapes[0]), add=True)
        for x in range(1, (len(_shapes))):
            pm.select('{}.cv[:]'.format(_shapes[x]), add=True)


    def scaleVertex(self, scale, valuePos=1.2, valueNeg=0.8):
        """
        @param scale : '+' / '-'
        """
        _shapes = pm.PyNode(self.control).getShapes()
        pm.select('{}.cv[:]'.format(_shapes[0]), r=True)
        for x in range(1, (len(_shapes))):
            pm.select('{}.cv[:]'.format(_shapes[x]), add=True)

        if scale == '+':
            pm.scale(valuePos, valuePos, valuePos, r=True)
        elif scale == '-':
            pm.scale(valueNeg, valueNeg, valueNeg, r=True)
        pm.select(self.control, r=True)


# -----------------------------------
# CLASS
# -----------------------------------


class ShapeManagement(object):
    """
    Shape Management Module
    Replace Shape according to the ShapesLibrary.py file. Mostly used for nurbs curve controls.

    @param subject: Single string or a list. Default value is pm.selected()

    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_core.Class__Control as CTL
    reload (CTL)

    sm = CTL.ShapeManagement()
    sm.shape = sl.diamond_shape
    """

    def __init__(self,
                 subject=pm.selected(),
                 ):

        self._nodeType = type(subject)
        if self._nodeType == str:
            self.subject = [pm.PyNode(subject)]
        else:
            self.subject = [pm.PyNode(x) for x in subject]

    @property
    def shape(self):
        return self.new_shape_getShape

    @shape.setter
    def shape(self, name):
        for ctrl in self.subject:
            self.replaceShape(old_ctrl=ctrl, new_ctrl=name)


    def replaceShape(self, old_ctrl=pm.selected(), new_ctrl=None):
        """
        Replacing shape function

        @param old_ctrl: The controller that you want to change the shape
        @param new_ctrl: The new shape you want to give to your old controller

        # TODO: Set the same color as the orignal controler and do a propScale??
        """

        original_ctl = old_ctrl
        colorSolver = pm.PyNode(original_ctl).overrideRGBColors.get()

        if colorSolver:
            color = pm.PyNode(original_ctl).overrideColorRGB.get()
        else:
            color = pm.PyNode(original_ctl).overrideColor.get()

        @propScale
        def createCtl():
            ctl =  new_ctrl()
            pm.PyNode(ctl).overrideEnabled.set(1)
            pm.PyNode(ctl).overrideRGBColors.set(colorSolver)
            if isinstance(color, int):
                pm.PyNode(ctl).overrideColor.set(color)
            else:
                pm.PyNode(ctl).overrideColorRGB.set(color)
            return ctl

        new_ctrl = createCtl()
        new_shape = new_ctrl

        # Duplicate source and move to target location
        new_shape_dup = pm.duplicate(new_shape, rc=True)[0]
        pm.matchTransform(new_shape_dup, original_ctl, pos=True, rot=True)

        # Parent source to target's parent
        pm.parent(new_shape_dup, original_ctl.getTransform())
        pm.makeIdentity(new_shape_dup, apply=True, t=1, r=1, s=1)

        # Get transforms and shapes of source and target
        self.new_shape_getShape = pm.PyNode(new_shape_dup).getShapes()
        original_ctl_getShapes = pm.PyNode(original_ctl).getShapes()

        for original, new in zip (original_ctl_getShapes, self.new_shape_getShape):
            pm.rename(new, original.name())

        # Parent shapes of source to target
        for srcShapes in self.new_shape_getShape:
            pm.parent(srcShapes, original_ctl, add=True, s=True)

        # Clean up
        pm.delete(new_shape_dup)
        pm.delete(original_ctl_getShapes)
        pm.delete(new_ctrl)

        return original_ctl



