# ------------------------------------------------------
# Squash and Strech
# -- Method Rigger (Maya)
# -- Version 1.0.0
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import maya.cmds as mc
import adb_core.NameConv_utils as NC
import adb_core.ModuleBase as moduleBase
import pymel.core as pm
from adb_core.Class__Transforms import Transform
from adbrower import undo


class SquashStrechModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(SquashStrechModel, self).__init__()
        self.getFollicules = []
        self.getFolliGrp = []


class SquashStrech(moduleBase.ModuleBase):
    """
    Squash and Strech for a ribbon system

    Arguments:
        module_name {String} -- Name of the module
        ExpCtrl {String or None} -- Transform on which we add attributes settings. 
                                    Default: None, So it will be on the SETTINGS_GRP module group
        ribbon_ctrl {List} -- start and end for the distance calculation. Top first, then bottom
        jointList {List} -- List of the joints that will be squash and strech
        
        jointListA {Tuple (List, int)} -- Section A of jointList, exposant Value of the squash and strech
        jointListB {Tuple (List, int)} -- Section B of jointList, exposant Value of the squash and strech
        jointListC {Tuple (List, int)} -- Section C of jointList, exposant Value of the squash and strech

    example:
        import adb_utils.Class__SquashStretch_Ribbon as adb_ST_Ribbon
        reload(adb_utils.Class__SquashStretch_Ribbon)

        ribbonStretch = adb_ST_Ribbon.SquashStrech('Test',
                        ExpCtrl="cog_ctrl",
                        ribbon_ctrl=['L__Leg_Base_Hips__JNT', 'L__Leg_Base_Knee__JNT']

                        jointList=['L__Leg_upper_proxy_plane_end_0{}__GRP'.format(x + 1) for x in xrange(5)],
                        jointListA = ['L__Leg_upper_proxy_plane_end_01__GRP'],
                        jointListB = ['L__Leg_upper_proxy_plane_end_02__GRP', 'L__Leg_upper_proxy_plane_end_03__GRP', 'L__Leg_upper_proxy_plane_end_04__GRP'],
                        jointListC = ['L__Leg_upper_proxy_plane_end_05__GRP'],

                        expA=0,
                        expB=1.5,
                        expC=0,
                    )
        ribbonStretch.start()
        ribbonStretch.build()
    """

    def __init__(self,
                 module_name,
                 ExpCtrl     = None,
                 ribbon_ctrl = [],  # Top first, then bottom

                 jointList   = [],
                 jointListA  = ([], 0),
                 jointListB  = ([], 1.5),
                 jointListC  = ([], 0),
                 ):

        super(SquashStrech, self).__init__()

        self._MODEL = SquashStrechModel()

        self.NAME = module_name
        self.ExpCtrl = ExpCtrl
        self.jointList = jointList
        self.ribbon_ctrl = ribbon_ctrl

        if len(jointListA)>1:
            self.jointListA, self.expA = jointListA
            self.jointListB, self.expB = jointListB
            self.jointListC, self.expC = jointListC
        else:
            self.jointListA = jointListA
            self.jointListB = jointListB
            self.jointListC = jointListC

            self.expA = 0
            self.expB = 1.5
            self.expC = 0


    def __repr__(self):
        return str('{} : {} \n {}'.format(self.__class__.__name__, self.subject, self.__class__))

    # =========================
    # PROPERTY
    # =========================

    @property
    def getFolliGrp(self):
        return self._MODEL.getFolliGrp

    @property
    def getFollicules(self):
        """ Returns the follicules """
        return self._MODEL.getFollicules

    @getFollicules.setter
    def getFollicules(self, value):
        """ Returns the follicules """
        self._MODEL.getFollicules = value

    # =========================
    # METHOD
    # =========================

    def start(self, metaDataNode = 'network'):
        super(SquashStrech, self)._start(_metaDataNode = metaDataNode)

    def build(self):
        super(SquashStrech, self)._build()

        self.addExposant_attrs(self.expA, self.expB, self.expC)
        self.nodeData = self.CreateNodes()
        self.MakeConnections()
        self.JointConnections()
        self.setFinal_hiearchy()
        self.set_TAGS()

    def remove(self):
        self.removeSetup()

    # =========================
    # SOLVERS
    # =========================

    @undo
    def addExposant_attrs(self, expA, expB, expC):
        """Create the Exp Attribute on a selected Controler """
        if self.ExpCtrl is None:
            self.ExpCtrl = self.metaData_GRP

        if pm.objExists('{}.ExpA'.format(self.ExpCtrl)):
            pass
        else:
            pm.PyNode(self.ExpCtrl).addAttr('ExpA', keyable=True, dv=expA, at='double', min=0)
            pm.PyNode(self.ExpCtrl).addAttr('ExpB', keyable=True, dv=expB, at='double', min=0)
            pm.PyNode(self.ExpCtrl).addAttr('ExpC', keyable=True, dv=expC, at='double', min=0)


    @undo
    def CreateNodes(self):
        """Creation et settings de mes nodes"""

        pm.select(self.jointList, r=True)

        def createloc(sub=pm.selected()):
            """Creates locator at the Pivot of the object selected """

            locs = []
            for sel in sub:
                loc_align = pm.spaceLocator(n='{}__pos_loc__'.format(sel))
                locs.append(loc_align)
                pm.matchTransform(loc_align, sel, rot=True, pos=True)
                pm.select(locs, add=True)
            return locs

        posLocs = createloc([self.jointList[0], self.jointList[-1]])

        sp = (pm.PyNode(posLocs[0]).translateX.get(), pm.PyNode(posLocs[0]).translateY.get(), pm.PyNode(posLocs[0]).translateZ.get())
        ep = (pm.PyNode(posLocs[1]).translateX.get(), pm.PyNode(posLocs[1]).translateY.get(), pm.PyNode(posLocs[1]).translateZ.get())

        # create Distances Nodes
        self.DistanceLoc = pm.distanceDimension(sp=sp,  ep=ep)
        pm.rename(self.DistanceLoc, 'bendy_distDimShape')
        pm.rename(pm.PyNode(self.DistanceLoc).getParent(), 'bendy_distDim')
        distance = self.DistanceLoc.distance.get()
        pm.parent(self.DistanceLoc.getParent(), self.RIG_GRP)

        pm.parent(posLocs[0], self.ribbon_ctrl[0])
        pm.parent(posLocs[1], self.ribbon_ctrl[1])

        pm.rename(posLocs[0], 'distance_depart__{}'.format(NC.LOC))
        pm.rename(posLocs[1], 'distance_end__{}'.format(NC.LOC))

        posLocs[0].v.set(0)
        posLocs[1].v.set(0)
        self.DistanceLoc.getParent().v.set(0)

        # Creation des nodes Multiply Divide
        self.CurveInfoNode = pm.shadingNode('curveInfo', asUtility=1, n="IK_Spline_CurveInfo")
        self.Stretch_MD = pm.shadingNode('multiplyDivide', asUtility=1, n="StretchMult")
        self.Squash_MD = pm.shadingNode('multiplyDivide', asUtility=1, n="SquashMult")

        self.expA_MD = pm.shadingNode('multiplyDivide', asUtility=1, n="ExpA")
        self.expB_MD = pm.shadingNode('multiplyDivide', asUtility=1, n="ExpB")
        self.expC_MD = pm.shadingNode('multiplyDivide', asUtility=1, n="ExpC")

        # Settings des nodes Multiply Divide
        self.Stretch_MD.operation.set(2)
        self.Squash_MD.operation.set(2)

        self.expA_MD.operation.set(3)
        self.expA_MD.input1X.set(1)

        self.expB_MD.operation.set(3)
        self.expB_MD.input1X.set(1)

        self.expC_MD.operation.set(3)
        self.expC_MD.input1X.set(1)

        return self.expA_MD, self.expB_MD, self.expC_MD, self.Squash_MD,  self.Stretch_MD, self.CurveInfoNode, posLocs[0], posLocs[1]


    def create_scale_distance(self):
        distObjs_LIST_QDT = self.ribbon_ctrl

        distanceNode_shape = pm.distanceDimension(sp=(1, 1, 1), ep=(2, 2, 2))

        pm.rename(distanceNode_shape, 'bendy_scale_distDimShape')
        pm.rename(pm.PyNode(distanceNode_shape).getParent(), 'bendy_scale_distDim')

        distanceNode = (pm.PyNode(distanceNode_shape).getParent())

        end_point_loc = pm.listConnections(str(distanceNode_shape) + '.endPoint', source=True)[0]
        start_point_loc = pm.listConnections(str(distanceNode_shape) + '.startPoint', source=True)[0]

        pm.rename(start_point_loc, '{}_Dist__{}'.format(distObjs_LIST_QDT[0], NC.LOC))
        pm.rename(end_point_loc, '{}_Dist__{}'.format(distObjs_LIST_QDT[1], NC.LOC))

        pm.matchTransform(start_point_loc, distObjs_LIST_QDT[0])
        pm.matchTransform(end_point_loc, distObjs_LIST_QDT[1])

        [loc.v.set(0) for loc in [end_point_loc, start_point_loc]]

        self.scale_grp = pm.group(n='{}_scale__{}'.format(self.NAME, NC.GRP), w=True, em=True)
        pm.parent(distanceNode, start_point_loc, end_point_loc, self.scale_grp)
        self.scale_grp.v.set(0)

        return distanceNode_shape


    @undo
    def MakeConnections(self):

        self.scale_distanceNode = self.create_scale_distance()

        self.scale_distanceNode.distance >> self.Stretch_MD.input2X
        self.scale_distanceNode.distance >> self.Squash_MD.input1X

        ## Distance >> StretchMult
        self.DistanceLoc.distance >> self.Stretch_MD.input1X

        # StretchMult >> All scale X of each joint
        for each in self.jointList[1:-1]:
            self.Stretch_MD.outputX >> pm.PyNode(each).scaleX

        ## Distance >> SquashMult
        self.DistanceLoc.distance >> self.Squash_MD.input2X

        # SquashMult >> Exp A,B,C
        self.Squash_MD.outputX >> self.expA_MD.input1X
        self.Squash_MD.outputX >> self.expB_MD.input1X
        self.Squash_MD.outputX >> self.expC_MD.input1X

        # ExpCtrl >> Exp A,B,C
        pm.PyNode(self.ExpCtrl).ExpA >> self.expA_MD.input2X
        pm.PyNode(self.ExpCtrl).ExpB >> self.expB_MD.input2X
        pm.PyNode(self.ExpCtrl).ExpC >> self.expC_MD.input2X

        pm.PyNode(self.ExpCtrl).ExpA >> self.expA_MD.input2Y
        pm.PyNode(self.ExpCtrl).ExpB >> self.expB_MD.input2Y
        pm.PyNode(self.ExpCtrl).ExpC >> self.expC_MD.input2Y

        pm.PyNode(self.ExpCtrl).ExpA >> self.expA_MD.input2Z
        pm.PyNode(self.ExpCtrl).ExpB >> self.expB_MD.input2Z
        pm.PyNode(self.ExpCtrl).ExpC >> self.expC_MD.input2Z


    def JointConnections(self):
        """Connections on joints in Scale Y and Scale Z """

        expA_MD = "ExpA"
        expB_MD = "ExpB"
        expC_MD = "ExpC"

        for each in self.jointListA:
            pm.PyNode(expA_MD).outputX >> pm.PyNode(each).scaleY
            pm.PyNode(expA_MD).outputX >> pm.PyNode(each).scaleZ

        for each in self.jointListB:
            pm.PyNode(expB_MD).outputX >> pm.PyNode(each).scaleY
            pm.PyNode(expB_MD).outputX >> pm.PyNode(each).scaleZ

        for each in self.jointListC:
            pm.PyNode(expC_MD).outputX >> pm.PyNode(each).scaleY
            pm.PyNode(expC_MD).outputX >> pm.PyNode(each).scaleZ


    def setFinal_hiearchy(self):
        self.Do_not_touch_grp = pm.group(n=NC.NO_TOUCH, em=1, parent=self.RIG_GRP)
        pm.parent(self.scale_grp, self.Do_not_touch_grp)


    def set_TAGS(self):
        Transform(str(self.scale_grp)).addAttr(NC.TAG_GlOBAL_SCALE, '')


    def removeSetup(self):
        def breakConnection(sel='', attributes=['v']):
            """
            Break Connection
            @param attributes : list of different attribute:  ['tx','ty','tz','rx','ry','rz','sx','sy','sz', 'v']

            The default value is : ['v']
            """

            for att in attributes:
                attr = sel + '.' + att

                destinationAttrs = pm.listConnections(
                    attr, plugs=True, source=False) or []
                sourceAttrs = pm.listConnections(
                    attr, plugs=True, destination=False) or []

                for destAttr in destinationAttrs:
                    pm.disconnectAttr(attr, destAttr)
                for srcAttr in sourceAttrs:
                    pm.disconnectAttr(srcAttr, attr)

        for jnt in self.jointList:
            breakConnection(jnt, attributes=('sx', 'sy', 'sz'))
            [pm.setAttr('{}.{}'.format(jnt, attr)) for attr in ('sx', 'sy', 'sz')]

        [pm.deleteAttr("{}.{}".format(self.ExpCtrl, attr)) for attr in ('ExpA', 'ExpB', 'ExpC')]
        pm.delete(self.MOD_GRP)
        [pm.delete(node) for node in self.nodeData]