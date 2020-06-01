# -------------------------------------------------------------------
# adb Class FK SHAPE SET UP
# -- Version 1.0.0
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# -------------------------------------------------------------------

import adbrower
import pymel.core as pm
from adbrower import changeColor, flatList, makeroot
import adb_core.NameConv_utils as NC

adb = adbrower.Adbrower()

# -----------------------------------
# CLASS
# -----------------------------------


class FkShape(object):
    """
    Class thats creates a Fk Shape Setup on joints

    @oaram listJoint: List. Joints on which we run the script. Default value is pm.selected().

    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_utils.Class__FkShapes as adbFkShape
    reload (adbFkShape)

    fk = adbFkShape.FkShape(pm.selected())
    fk.shapeSetup()
    """

    def __init__(self, listJoint=pm.selected()):
        self.listJoint = listJoint
        self.controls = None
        self._curve = None

    @property
    def getJointsGrp(self):
        parent = [pm.PyNode(x).getParent() for x in self.getJoints]
        parent_list = flatList(parent)
        return parent_list

    @property
    def getJoints(self):
        return self.controls

    @property
    def cradidus(self):
        return self._radius

    @cradidus.setter
    def cradidus(self, rad):
        self.deleteSetup()
        self._radius = rad
        self.shapeSetup()
        self._radius = rad

    @property
    def jradius(self):
        return self._radius

    @jradius.setter
    def jradius(self, rad):
        for joint in self.getJoints:
            pm.PyNode(joint).radius.set(rad)
        self._radius = rad

    @property
    def getNormals(self):
        return self.normalsCtrl

    @getNormals.setter
    def getNormals(self, norm):
        self.deleteSetup()
        self.normalsCtrl = norm
        self.shapeSetup()
        self.normalsCtrl = norm

    @changeColor()
    @makeroot()
    def shapeSetup(self,  _radius=1, normalsCtrl=(1, 0, 0)):
        """
        Fk chain setUp by parenting the shape to the joint

        @param _radius: Interger. Radius of the circle controller
        @param normalsCtrl: Tuple. Normals value of the circle controller
        """

        self._radius = _radius
        self.normalsCtrl = normalsCtrl

        subject = [pm.PyNode(x) for x in self.listJoint]

        def CreateCircles():
            CurveColl = []
            for joint in subject:
                myname = '{}'.format(joint)
                new_name = '{}{}__{}'.format(NC.getSideFromName(myname), NC.getBasename(myname), NC.CTRL)
                self._curve = pm.circle(nr=self.normalsCtrl, r=self._radius)
                pm.matchTransform(self._curve, joint, pos=1, rot=1)

                curveShape = pm.PyNode(self._curve[0]).getShape()
                CurveColl.extend(self._curve)
                tras = pm.xform(joint, ws=True, q=True, t=True)
                pivot = pm.xform(joint, ws=True, q=True, rp=True)

                pm.xform(self._curve, ws=True, t=tras, rp=pivot)
                pm.parent(curveShape, joint, r=True, s=True)
                pm.delete(self._curve)
                pm.rename(joint, new_name)
                pm.setAttr('{}.radius'.format(joint), keyable=False, channelBox=False)
            return(subject)

        controls = CreateCircles()
        self.controls = controls
        return(controls)

    def deleteSetup(self):
        """Delete the Setup"""
        groups = self.getJointsGrp
        pm.parent(self.getJoints, w=True)
        pm.delete(groups)
        child = [x.getChildren() for x in self.getJoints]
        children = flatList(child)
        pm.delete(children)
        adb.ChainParent(self.getJoints)
        for joint in self.getJoints:
            pm.PyNode(joint).rename(str(joint).replace('_fk__ctrl__', '__jnt__'))


# fk = FkShape(pm.selected())
# fk.shapeSetup(_radius = 5, normalsCtrl = (0,1,0))
