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

adb = adbrower.Adbrower()

from adbrower import changeColor
from CollDict import colordic

class Control(object):
    """
    Creating Control 
    
    example:
        
    control = Control('test', sl.cube_shape, 5)
  
    """

    def __init__(self, name, shape, scale=1, parent=None, matchTransforms=None):
        self.name = name
        self.shape = shape
        self.scale = scale
        self.parent = parent
        self.matchTransforms = matchTransforms

        self.create()
      
    
    @changeColor()
    def create(self):
        self.control = self.shape()
        pm.rename(self.control, self.name)
        adb.AutoSuffix([self.control])
        self.control.scale.set(self.scale, self.scale, self.scale)
        pm.makeIdentity(self.control, n=0, s=1, r=1, t=1, apply=True, pn=1)
        if self.matchTransforms:
            pm.matchTransform(self.control, self.matchTransforms, pos = True)
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


    

# ctrl = Control('test', sl.cube_shape, 5)
# ctrl.scaleVertex('+')