# -------------------------------------------------------------------
# Class Control
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# -------------------------------------------------------------------

import pymel.core as pm
import maya.cmds as mc

import ShapesLibrary as sl
import adb_core.NameConv_utils as NC
import adb_core.Class__AddAttr as adbAttr
import adbrower

adb = adbrower.Adbrower()

from adbrower import changeColor, propScale, makeroot
from CollDict import indexColor


class Control(adbAttr.NodeAttr):
    """
    Creating Control

    ## EXTERIOR CLASS BUILD
    #------------------------
        import adb_core.Class__Control as CTL

        control = CTL.Control('test', sl.cube_shape, 5)

        # TODO:  add movable Pivot setup
    """
    def __init__(self, name, shape, scale=1, parent=None, matchTransforms=(False, 0, 0), color=('index', 21), rotateAxis = None):
        self.name = name
        self._shape = shape
        self._scale = scale
        self.parent = parent
        self.matchTransforms = matchTransforms
        self._color = color
        self.rotateAxis = rotateAxis

        self.control = self.create()

        super(Control, self).__init__(self.control)

    #===================
    # PROPERTIES
    #===================

    @classmethod
    @makeroot(suf='Offset', forceNameConvention=True)
    def fkShape(cls, joints=[], name = None, shape=sl.circleX_shape , scale=1, color=('index', 18)):
        """
        Returns:
            List: List of Joints from Joint Class
        """
        fk_joint = []
        for joint in joints:
            ctrl = cls(joint, shape=shape, scale=scale, color=color)
            tras = pm.xform(joint, ws=True, q=True, t=True)
            pivot = pm.xform(joint, ws=True, q=True, rp=True)
            pm.xform(ctrl.control, ws=True, t=tras, rp=pivot)
            pm.parent(ctrl.control.getShape(), joint, relative=True, shape=True)
            pm.delete(ctrl.control)
            if name:
                pm.rename(joint, name)
                joint = adb.AutoSuffix([joint])
            else:
                joint = adb.AutoSuffix([joint])
            fk_joint.append(joint)
        return fk_joint

    @property
    def shape(self):
        return (self._shape)

    @shape.setter
    def shape(self, name):
        sm = ShapeManagement([self.control])
        sm.shape = name

    @property
    def color(self):
        return (self._color)

    @color.setter
    def color(self, color_value):
        adb.changeColor_func(self.control, *color_value)
        pm.select(None)
        return (color_value)

    @property
    def scale(self):
        return (self._scale)

    @scale.setter
    def scale(self, scale_value):
            if scale_value > 0:
                self.scaleVertex('+', valuePos=scale_value)
            else:
                self.scaleVertex('-', valuePos=scale_value)


    def create(self):
        self.control = self._shape()
        pm.rename(self.control, self.name)
        adb.AutoSuffix([self.control])
        adb.changeColor_func(self.control, *self._color)
        if isinstance(self.scale, int) or isinstance(self.scale, float):
            self.control.scale.set(self._scale, self._scale, self._scale)
        else:
            self.control.scale.set(*self._scale)

        pm.makeIdentity(self.control, n=0, s=1, r=1, t=1, apply=True, pn=1)
        if self.matchTransforms[0] is not False:
            pm.matchTransform(self.control, self.matchTransforms[0], pos =self.matchTransforms[1], rot=self.matchTransforms[2])

        if self.parent:
            pm.parent(self.control, self.parent)

        if self.rotateAxis:
            self.rotateVertex(self.rotateAxis)

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


    def rotateVertex(self, axis):
        dup = pm.duplicate(self.control, st=1)[0]
        pm.parent(dup, world=1)
        _shapes = pm.PyNode(self.control).getShapes()

        if axis == 'x' or 'X':
            pm.rotate(dup, 90,0,0, r=1, os=1)
            pm.makeIdentity(dup, n=0, s=1, r=1, t=1, apply=True, pn=1)

        elif axis == 'y' or 'Y':
            pm.rotate(dup, 0,90,0, r=1, os=1)
            pm.makeIdentity(dup, n=0, s=1, r=1, t=1, apply=True, pn=1)

        elif axis == 'z' or 'Z':
            pm.rotate(dup, 0,0,90, r=1, os=1)
            pm.makeIdentity(dup, n=0, s=1, r=1, t=1, apply=True, pn=1)

        # Duplicate source and move to target location
        new_shape_dup = pm.duplicate(dup, rc=True)
        pm.matchTransform(new_shape_dup[0], self.control, pos=True, rot=True)

        # Parent source to target's parent
        pm.parent(new_shape_dup, self.control.getTransform())
        pm.makeIdentity(new_shape_dup, apply=True, t=1, r=1, s=1)

        # Get transforms and shapes of source and target
        new_shape_getShape = pm.PyNode(new_shape_dup[0]).getShapes()
        old_shape_getShape = pm.PyNode(self.control).getShapes()

        # Parent shapes of source to target
        for srcShapes in new_shape_getShape:
            pm.parent(srcShapes, self.control, add=True, s=True)

        # ## Clean up
        pm.delete(new_shape_dup)
        pm.delete(old_shape_getShape)
        pm.delete(dup)


    def addRotationOrderAttr(self):
        pm.addAttr(self.control, ln="rotationOrder",
                    en="xyz:yzx:zxy:xzy:yxz:zyx:", at="enum")
        pm.setAttr((str(self.control) + ".rotationOrder"),
                    e=1, keyable=True)
        pm.connectAttr((str(self.control) + ".rotationOrder"),
                        (str(self.control) + ".rotateOrder"))

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



