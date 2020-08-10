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
from adb_core.Class__AddAttr import NodeAttr
import adbrower
adb = adbrower.Adbrower()

from adbrower import undo


class SquashStrechModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(SquashStrechModel, self).__init__()
        self.getFollicules = []
        self.getFolliGrp = []
        self.getScaleGrp = []


class SquashStrech(moduleBase.ModuleBase):
    """
    Squash and Strech for a ribbon system

    Arguments:
        module_name {String} -- Name of the module
        UsingCurve {Bool} -- using the curve lenght. Otherwise use a in between distance
        ExpCtrl {String or None} -- Transform on which we add attributes settings.
                                    Default: None, So it will be on the METADATA_GRP module group
        ribbon_ctrl {List} -- start and end for the distance calculation. Top first, then bottom
        jointList {List} -- List of the joints that will be squash and strech

        jointListA {Tuple (List, int)} -- Section A of jointList, exposant Value of the squash and strech
        jointListB {Tuple (List, int)} -- Section B of jointList, exposant Value of the squash and strech
        jointListC {Tuple (List, int)} -- Section C of jointList, exposant Value of the squash and strech

    example:
        import adb_library.adb_modules.Module__SquashStretch_Ribbon as adb_ST_Ribbon
        reload(adb_ST_Ribbon)

        ribbonStretch = adb_ST_Ribbon.SquashStrech('Test',
                        ExpCtrl="cog_ctrl",
                        ribbon_ctrl=['L__Leg_Base_Hips__JNT', 'L__Leg_Base_Knee__JNT'],

                        jointList=['L__Leg_upper_proxy_plane_end_0{}__GRP'.format(x + 1) for x in xrange(5)],
                        jointListA = ['L__Leg_upper_proxy_plane_end_01__GRP'],
                        jointListB = ['L__Leg_upper_proxy_plane_end_02__GRP', 'L__Leg_upper_proxy_plane_end_03__GRP', 'L__Leg_upper_proxy_plane_end_04__GRP'],
                        jointListC = ['L__Leg_upper_proxy_plane_end_05__GRP'],
                    )
        ribbonStretch.start()
        ribbonStretch.build()
    """

    def __init__(self,
                 module_name,
                 usingCurve  = False,
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
        self.usingCurve = usingCurve
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
    def getScaleGrp(self):
        return self._MODEL.getScaleGrp

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
        super(SquashStrech, self)._start(self.NAME, _metaDataNode = metaDataNode)

        metaData_GRP_attribute = NodeAttr([self.metaData_GRP])
        metaData_GRP_attribute.addAttr('Toggle', True)
        metaData_GRP_attribute.addAttr('jointList', 'string')

        self.metaData_GRP.jointList.set(str([str(joint) for joint in self.jointList]), lock=True)


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
        def createloc(sub):
            """Creates locator at the Pivot of the object selected """

            locs = []
            for sel in sub:
                loc_align = pm.spaceLocator(n='{}__pos_loc__'.format(sel))
                locs.append(loc_align)
                pm.matchTransform(loc_align, sel, rot=True, pos=True)
                pm.select(locs, add=True)
            return locs

        self.CurveInfoNode = None
        posLocs = []
        if self.usingCurve:
            self.spineLenghtCurve = adb.createCurveFrom(self.jointList, curve_name='{}_lenght__CRV'.format(self.NAME))
            pm.parent(self.spineLenghtCurve, self.RIG_GRP)
            self.CurveInfoNode = pm.shadingNode('curveInfo', asUtility=1, n='{}_CurveInfo'.format(self.NAME))

        else:
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
        self.Stretch_MD = pm.shadingNode('multiplyDivide', asUtility=1, n="StretchMult")
        self.Squash_MD = pm.shadingNode('multiplyDivide', asUtility=1, n="SquashMult")

        self.expA_MD = pm.shadingNode('multiplyDivide', asUtility=1, n="{}_ExpA".format(self.NAME))
        self.expB_MD = pm.shadingNode('multiplyDivide', asUtility=1, n="{}_ExpB".format(self.NAME))
        self.expC_MD = pm.shadingNode('multiplyDivide', asUtility=1, n="{}_ExpC".format(self.NAME))

        # blendColor node Toggle
        self.toggle_node = pm.shadingNode('blendColors', asUtility=1, n='{}_Toggle__{}'.format(self.NAME, NC.BLENDCOLOR_SUFFIX))
        self.toggle_node.blender.set(1)

        # Settings des nodes Multiply Divide
        self.Stretch_MD.operation.set(2)
        self.Squash_MD.operation.set(2)

        self.expA_MD.operation.set(3)
        self.expA_MD.input1X.set(1)

        self.expB_MD.operation.set(3)
        self.expB_MD.input1X.set(1)

        self.expC_MD.operation.set(3)
        self.expC_MD.input1X.set(1)

        return self.expA_MD, self.expB_MD, self.expC_MD, self.Squash_MD,  self.Stretch_MD, self.CurveInfoNode, posLocs


    def create_scale_distance(self):
        self._MODEL.getScaleGrp = [adb.makeroot_func(grp, suff='scale', forceNameConvention=True) for grp in self.jointList]
        for grp in self._MODEL.getScaleGrp:
            self.MOD_GRP.sx >> grp.sx
            self.MOD_GRP.sy >> grp.sy
            self.MOD_GRP.sz >> grp.sz

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

        if self.usingCurve:
            (pm.PyNode(self.spineLenghtCurve).getShape()).worldSpace[0] >> self.CurveInfoNode.inputCurve
            self.CurveInfoNode.arcLength >> self.Stretch_MD.input1X
            self.CurveInfoNode.arcLength >> self.Squash_MD.input2X
        else:
            ## Distance >> StretchMult
            self.DistanceLoc.distance >> self.Stretch_MD.input1X
            for each in self.jointList[1:-1]:
                self.Stretch_MD.outputX >> pm.PyNode(each).scaleX
            self.DistanceLoc.distance >> self.Squash_MD.input2X

        # SquashMult >> Exp A,B,C
        self.Squash_MD.outputX >> self.expA_MD.input1X
        self.Squash_MD.outputX >> self.expB_MD.input1X
        self.Squash_MD.outputX >> self.expC_MD.input1X

        # ExpCtrl >> Exp A,B,C
        pm.PyNode(self.ExpCtrl).ExpA >> self.toggle_node.color1R
        pm.PyNode(self.ExpCtrl).ExpB >> self.toggle_node.color1G
        pm.PyNode(self.ExpCtrl).ExpC >> self.toggle_node.color1B
        self.metaData_GRP.Toggle >> self.toggle_node.blender

        self.toggle_node.color2R.set(0)
        self.toggle_node.color2G.set(0)
        self.toggle_node.color2B.set(0)

        self.toggle_node.outputR >> self.expA_MD.input2X
        self.toggle_node.outputG >> self.expB_MD.input2X
        self.toggle_node.outputB >> self.expC_MD.input2X

        self.toggle_node.outputR >> self.expA_MD.input2Y
        self.toggle_node.outputG >> self.expB_MD.input2Y
        self.toggle_node.outputB >> self.expC_MD.input2Y

        self.toggle_node.outputR >> self.expA_MD.input2Z
        self.toggle_node.outputG >> self.expB_MD.input2Z
        self.toggle_node.outputB >> self.expC_MD.input2Z


    def JointConnections(self):
        """Connections on joints in Scale Y and Scale Z """
        for each in self.jointListA:
            pm.PyNode(self.expA_MD).outputX >> pm.PyNode(each).scaleY
            pm.PyNode(self.expA_MD).outputX >> pm.PyNode(each).scaleZ

        for each in self.jointListB:
            pm.PyNode(self.expB_MD).outputX >> pm.PyNode(each).scaleY
            pm.PyNode(self.expB_MD).outputX >> pm.PyNode(each).scaleZ

        for each in self.jointListC:
            pm.PyNode(self.expC_MD).outputX >> pm.PyNode(each).scaleY
            pm.PyNode(self.expC_MD).outputX >> pm.PyNode(each).scaleZ


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