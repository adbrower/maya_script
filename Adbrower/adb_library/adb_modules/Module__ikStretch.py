# ------------------------------------------------------
# Ik Stretch Set Up
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

import adb_core.ModuleBase as moduleBase
reload(moduleBase)
import adb_core.NameConv_utils as NC


# self.NAME = 'ik_stretch'
# METADATA_grp_name = '{}_METADATA'.format(self.NAME)

class stretchyIKModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(stretchyIKModel, self).__init__()
        self.ikJnts = []
        self.startJnt= []
        self.hingeJnts = []
        self.endJnt = []
        self.stretchAxis = []
        self.ikHandle = []


class stretchyIK(moduleBase.ModuleBase):
    """
    Add stretch to any IK chain

    @param ik_joints: (list) List of Ik joints chain
    @param ik_ctrl: transform
    @scaleAxe: (string) Axis in which the joints will be scaled

    # example
    leg = stretchyIK('legIk',
                    ik_joints = ['joint1', 'joint2', 'joint3'],
                    ik_ctrl = 'ikHandle1__CTRL',
                    stretchAxis = 'Y' )

    leg.start()
    leg.build()
    """

    def __init__(self,  
                 module_name,
                 ik_joints=pm.selected(),
                 ik_ctrl=None,
                 stretchAxis='Y',
                 ):
        super(stretchyIK, self).__init__()

        self._MODEL = stretchyIKModel()
        self.CLASS_NAME = self.__class__.__name__
        self.NAME = module_name

        self._MODEL.ikJnts = ik_joints
        if isinstance(self._MODEL.ikJnts, list):
            self._MODEL.ikJnts = [pm.PyNode(x) for x in self._MODEL.ikJnts]

        self.stretchAxis = stretchAxis
        self.ik_ctrl = pm.PyNode(ik_ctrl)

        self._MODEL.getControls = self.ik_ctrl

    # =========================
    # PROPERTY
    # =========================

    @property
    def ikJnts(self):
        return self._MODEL.ikJnts

    @property
    def stretchAxis(self):
        return self._MODEL.stretchAxis

    @stretchAxis.setter
    def stretchAxis(self, axis):
        self._MODEL.stretchAxis = str(axis)

    @property
    def startJnt(self):
        self._MODEL.startJnt = self._MODEL.ikJnts[0]
        return self._MODEL.startJnt

    @property
    def hingeJnts(self):
        self._MODEL.hingeJnts = self._MODEL.ikJnts[1:-1]
        return self._MODEL.hingeJnts
    
    @property
    def endJnt(self):
        self._MODEL.endJnt = self._MODEL.ikJnts[-1]
        return self._MODEL.endJnt

    @property
    def ikHandle(self):
        self._MODEL.ikHandle = [x for x in pm.listConnections(str(pm.PyNode(self.startJnt)) + '.message', s=1,) if x != 'MayaNodeEditorSavedTabsInfo'][0]
        return (self._MODEL.ikHandle)

    @property
    def distanceNode(self):
        return self.distanceLoc

    @property
    def originalDistance(self):
        return self.orig_distance

    @property
    def prop_mdv(self):
        return(self.md_prp_node)

    @property
    def stretch_mdv(self):
        return(self.md_strech_node)

    @property
    def condition_node(self):
        return(self.cond_node)

    # =========================
    # METHOD
    # =========================

    def start(self, _metaDataNode = 'transform'):
        super(stretchyIK, self)._start(metaDataNode = _metaDataNode)  

        self.metaData_GRP.addAttr('Ik_Handle', at='message', keyable=False)
        self.metaData_GRP.addAttr('Ik_Distance', at='double', dv=0, keyable=False)
        self.metaData_GRP.addAttr('Original_joint_distance', at='double', dv=0, keyable=False)
        self.metaData_GRP.addAttr('Joint_Axis', dt='string',  keyable=False)

        self.metaData_GRP.addAttr('Connecting_Start_Joint', at='message',  keyable=False)
        self.metaData_GRP.addAttr('Connecting_End_Joint', at='message',  keyable=False)
        self.metaData_GRP.addAttr('Connecting_Hinge_Joint', dt='string',  keyable=False)

        self.metaData_GRP.addAttr('Distance_Node', at='message',  keyable=False)
        self.metaData_GRP.addAttr('Proportion_MDV_Node', at='message',  keyable=False)
        self.metaData_GRP.addAttr('Stretch_MDV_Node', at='message',  keyable=False)
        self.metaData_GRP.addAttr('Condition_Node', at='message',  keyable=False)

    
    def build(self):
        super(stretchyIK, self)._build()
        self.stretchyIKSetUp()

        self.setFinalHiearchy(
                        RIG_GRP_LIST=[self.distanceLoc.getParent(), self.posLoc[0]],
                        INPUT_GRP_LIST=[pm.PyNode(self.ik_ctrl).getParent()],
                        OUTPUT_GRP_LIST=[])

        self.set_metaData_GRP()

    # =========================
    # SOLVERS
    # =========================

    def stretchyIKSetUp(self):
        """
        Creates a stretch system for an arm or leg
        """

        # -----------------------------------
        # FUNCTION
        # -----------------------------------

        def createloc(sub=pm.selected()):
            """Creates locator at the Pivot of the object selected """
            locs = []
            for sel in sub:
                loc_align = pm.spaceLocator(n='{}__pos__LOC__'.format(sel))
                locs.append(loc_align)
                pm.matchTransform(loc_align, sel, rot=True, pos=True)
                pm.select(locs, add=True)
            return locs

        self.posLoc = createloc([self.startJnt, self.endJnt])

        sp = (pm.PyNode(self.posLoc[0]).translateX.get(), pm.PyNode(self.posLoc[0]).translateY.get(), pm.PyNode(self.posLoc[0]).translateZ.get())
        ep = (pm.PyNode(self.posLoc[1]).translateX.get(), pm.PyNode(self.posLoc[1]).translateY.get(), pm.PyNode(self.posLoc[1]).translateZ.get())

        # -----------------------------------
        # IK STRETCH BUILD
        # -----------------------------------

        # create Nodes
        self.distanceLoc = pm.distanceDimension(sp=sp,  ep=ep)
        self.orig_distance = self.distanceLoc.distance.get()

        # getMaxdistance
        def getMaxDistance():
            pm.parent(self.posLoc[1], self.endJnt)
            oriTranslate = self.ik_ctrl.getTranslation()
            pm.move(self.ik_ctrl, 0, -1000, 0)
            _max_distance = self.distanceLoc.distance.get()
            self.ik_ctrl.setTranslation(oriTranslate)
            return _max_distance

        max_distance = getMaxDistance()

        # condition node
        self.cond_node = pm.shadingNode('condition', asUtility=1, n='{}__{}'.format(self.NAME, NC.CONDITION_SUFFIX))
        self.cond_node.operation.set(3)
        self.cond_node.colorIfFalseR.set(1)
        self.cond_node.secondTerm.set(1)

        # multiply Divide strech
        self.md_strech_node = pm.shadingNode('multiplyDivide', asUtility=1, n='{}_strech__MD'.format(self.NAME, NC.MULTIPLY_DIVIDE_SUFFIX))
        self.md_strech_node.operation.set(1)

        # multiply Divide Scale Factor
        self.md_scale_node = pm.shadingNode('multiplyDivide', asUtility=1, n='{}_scaleFactor__{}'.format(self.NAME, NC.MULTIPLY_DIVIDE_SUFFIX))
        self.md_scale_node.operation.set(1)
        self.md_scale_node.input2X.set(max_distance)
        self.MOD_GRP.sx >> self.md_scale_node.input1X

        # multiply Divide proportion
        self.md_prp_node = pm.shadingNode('multiplyDivide', asUtility=1, n='{}_proportion__{}'.format(self.NAME, NC.MULTIPLY_DIVIDE_SUFFIX))
        self.md_prp_node.operation.set(2)
        # self.md_prp_node.input2X.set(max_distance)

        # parenting
        pm.parent(self.posLoc[1], self.ik_ctrl)

        # connections
        self.distanceLoc.distance >> self.md_prp_node.input1X

        self.md_prp_node.outputX >> self.cond_node.firstTerm
        self.md_prp_node.outputX >> self.cond_node.colorIfTrueR
        self.md_scale_node.outputX >> self.md_prp_node.input2X

        self.cond_node.outColorR >> self.md_strech_node.input1X
        self.cond_node.outColorR >> self.md_strech_node.input1Y

        self.md_strech_node.outputX >> pm.PyNode(self.startJnt) + '.scale' + str(self.stretchAxis)

        for joint in self.hingeJnts:
            self.md_strech_node.outputX >> pm.PyNode(joint) + '.scale' + str(self.stretchAxis)

        # Clean up
        self.posLoc[0].v.set(0)
        self.posLoc[1].v.set(0)
        self.distanceLoc.getParent().v.set(0)

    def set_metaData_GRP(self):
        pm.PyNode(self.ikHandle).translate >> self.metaData_GRP.Ik_Handle
        pm.PyNode(self.distanceNode).distance >> self.metaData_GRP.Ik_Distance
        pm.PyNode(self.distanceNode).distance >> self.metaData_GRP.Distance_Node

        pm.PyNode(self.startJnt).translate >> self.metaData_GRP.Connecting_Start_Joint
        pm.PyNode(self.endJnt).translate >> self.metaData_GRP.Connecting_End_Joint

        self.metaData_GRP.Connecting_Hinge_Joint.set(str([str(joint) for joint in self.hingeJnts]), lock=True)

        pm.PyNode(self.prop_mdv).message >> self.metaData_GRP.Proportion_MDV_Node
        pm.PyNode(self.stretch_mdv).message >> self.metaData_GRP.Stretch_MDV_Node
        pm.PyNode(self.condition_node).message >> self.metaData_GRP.Condition_Node

        self.metaData_GRP.Joint_Axis.set(self.stretchAxis, lock=True)
        self.metaData_GRP.Original_joint_distance.set(self.originalDistance, lock=True)

       

# leg = stretchyIK('legIk',
#                 ik_joints = ['joint1', 'joint2', 'joint3'],
#                 ik_ctrl = 'ikHandle1__CTRL',
#                 stretchAxis = 'Y' )

# leg.start()
# leg.build()

