# ------------------------------------------------------
# Ik Stretch Set Up
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import sys

import maya.cmds as mc
import pymel.core as pm

import adb_core.ModuleBase as moduleBase
import adb_core.NameConv_utils as NC
import adbrower
adb = adbrower.Adbrower()


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
    import adb_library.adb_modules.Module__IkStretch as adbIkStretch
    reload(adbIkStretch)

    leg = adbIkStretch.stretchyIK('legIk',
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
                 poleVector_ctrl=None
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
        self.poleVector_ctrl = pm.PyNode(poleVector_ctrl)

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

    def start(self, metaDataNode = 'transform'):
        super(stretchyIK, self)._start(self.NAME, _metaDataNode = metaDataNode)

        self.metaData_GRP.addAttr('Toggle', at='bool', keyable=True, dv=True)
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

        self.metaData_GRP.addAttr('Maximum_Toggle', at='bool', dv=0,  keyable=True)
        self.metaData_GRP.addAttr('Maximum_Factor', at='float', dv=1.3, min=1, max=20, keyable=True)


    def build(self):
        super(stretchyIK, self)._build()
        self.stretchyIKSetUp()
        self.maximumSetup()

        self.setFinalHiearchy(
                        RIG_GRP_LIST=[self.distanceLoc.getParent(), self.posLoc[0], self.posLoc[1].getParent()],
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
                loc_align = pm.spaceLocator(n='{}_Distance__{}'.format(NC.getNameNoSuffix(sel), NC.LOC))
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
            oriTranslate = self.ik_ctrl.getTranslation()
            pm.move(self.ik_ctrl, -1000, -1000, 0)
            _max_distance = self.distanceLoc.distance.get()
            self.ik_ctrl.setTranslation(oriTranslate)
            return _max_distance

        max_distance = getMaxDistance() + 0.2

        # condition node
        self.cond_node = pm.shadingNode('condition', asUtility=1, n='{}_cond_{}'.format(self.NAME, NC.CONDITION_SUFFIX))
        self.cond_node.operation.set(3)
        self.cond_node.colorIfFalseR.set(1)
        self.cond_node.secondTerm.set(1)

        # blendColor node Toggle
        self.toggle_node = pm.shadingNode('blendColors', asUtility=1, n='{}_Toggle__{}'.format(self.NAME, NC.BLENDCOLOR_SUFFIX))
        self.toggle_node.blender.set(1)

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

        adb.makeroot_func(self.posLoc[1], suff='OFFSET', forceNameConvention=1)

        # connections
        self.distanceLoc.distance >> self.toggle_node.color1R
        self.toggle_node.outputR >> self.md_prp_node.input1X

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


    def maximumSetup(self):
        # DUPLICATED IK JOINT CHAIN
        self.ik_NonStretch_joint = [pm.duplicate(joint, parentOnly=True)[0] for joint in self.ikJnts]
        pm.parent(self.ik_NonStretch_joint[-1], self.ik_NonStretch_joint[-2])
        pm.parent(self.ik_NonStretch_joint[-2], self.ik_NonStretch_joint[0])

        [pm.PyNode(jnt).rename('{}_NonStetch__{}'.format(NC.getNameNoSuffix(jnt), NC.JOINT)) for jnt in self.ik_NonStretch_joint]

        nonStretch_IkHandle, nonStretch_IkHandle_effector = pm.ikHandle(n='{}_NonStetch__{}'.format(self.NAME, NC.IKHANDLE_SUFFIX), sj=self.ik_NonStretch_joint[0], ee=self.ik_NonStretch_joint[-1])
        nonStretch_IkHandle.v.set(0)
        self.nonStretch_IkHandle = nonStretch_IkHandle
        adb.makeroot_func(self.nonStretch_IkHandle)
        pm.poleVectorConstraint(self.poleVector_ctrl, nonStretch_IkHandle, weight=1)
        adb.matrixConstraint(self.ik_ctrl, self.nonStretch_IkHandle.getParent())
        self.setFinalHiearchy(RIG_GRP_LIST = [self.nonStretch_IkHandle.getParent(), self.ik_NonStretch_joint[0]])

        # MAXIMUM NODES
        self.decompStart_node = pm.shadingNode('decomposeMatrix', asUtility=1, n='{}_startVec__{}'.format(self.NAME, NC.DECOMPOSEMAT_SUFFIX))
        self.decompEnd_node = pm.shadingNode('decomposeMatrix', asUtility=1, n='{}_endVec__{}'.format(self.NAME, NC.DECOMPOSEMAT_SUFFIX))
        self.md_max_node = pm.shadingNode('multiplyDivide', asUtility=1, n='{}_maxFactor__{}'.format(self.NAME, NC.MULTIPLY_DIVIDE_SUFFIX))
        self.clam_node = pm.shadingNode('clamp', asUtility=1, n='{}_max__{}'.format(self.NAME, NC.CLAMP_SUFFIX))
        self.initialVec_node = pm.shadingNode('plusMinusAverage', asUtility=1, n='{}_initalVec__{}'.format(self.NAME, NC.PLUS_MIN_AVER_SUFFIX))
        self.initialVec_node.operation.set(2)
        self.addVec_node = pm.shadingNode('plusMinusAverage', asUtility=1, n='{}_addVect__{}'.format(self.NAME, NC.PLUS_MIN_AVER_SUFFIX))
        self.maximumToggle_node = pm.shadingNode('blendColors', asUtility=1, n='{}_maximumToggle__{}'.format(self.NAME, NC.PLUS_MIN_AVER_SUFFIX))

        # connections maximum system
        self.ik_NonStretch_joint[-1].worldMatrix[0] >> self.decompStart_node.inputMatrix
        self.ik_ctrl.worldMatrix[0] >> self.decompEnd_node.inputMatrix
        self.decompStart_node.outputTranslate >> self.md_max_node.input1
        self.decompEnd_node.outputTranslate >> self.initialVec_node.input3D[0]
        self.decompStart_node.outputTranslate >> self.initialVec_node.input3D[1]
        self.initialVec_node.output3D >> self.addVec_node.input3D[0]
        self.decompStart_node.outputTranslate >> self.addVec_node.input3D[1]
        self.addVec_node.output3D >> self.clam_node.input
        self.md_max_node.output >> self.clam_node.max
        self.clam_node.output >> self.maximumToggle_node.color1
        self.decompEnd_node.outputTranslate >> self.maximumToggle_node.color2
        self.maximumToggle_node.output >> self.posLoc[1].getParent().translate


    def set_metaData_GRP(self):
        pm.PyNode(self.ikHandle).translate >> self.metaData_GRP.Ik_Handle
        pm.PyNode(self.distanceNode).distance >> self.metaData_GRP.Ik_Distance
        pm.PyNode(self.distanceNode).distance >> self.metaData_GRP.Distance_Node
        self.metaData_GRP.Toggle >> self.toggle_node.blender

        pm.PyNode(self.startJnt).translate >> self.metaData_GRP.Connecting_Start_Joint
        pm.PyNode(self.endJnt).translate >> self.metaData_GRP.Connecting_End_Joint

        self.metaData_GRP.Connecting_Hinge_Joint.set(str([str(joint) for joint in self.hingeJnts]), lock=True)

        pm.PyNode(self.prop_mdv).message >> self.metaData_GRP.Proportion_MDV_Node
        pm.PyNode(self.stretch_mdv).message >> self.metaData_GRP.Stretch_MDV_Node
        pm.PyNode(self.condition_node).message >> self.metaData_GRP.Condition_Node

        self.metaData_GRP.Joint_Axis.set(self.stretchAxis, lock=True)
        self.metaData_GRP.Original_joint_distance.set(self.originalDistance, lock=True)

        toggle_mult = pm.shadingNode('multDoubleLinear', asUtility=1)
        self.metaData_GRP.Maximum_Toggle >> toggle_mult.input1
        self.toggle_node.blender >> toggle_mult.input2
        toggle_mult.output >> self.maximumToggle_node.blender

        self.metaData_GRP.Maximum_Factor >> self.md_max_node.input2X
        self.metaData_GRP.Maximum_Factor >> self.md_max_node.input2Y
        self.metaData_GRP.Maximum_Factor >> self.md_max_node.input2Z


# leg = stretchyIK('legIk',
#                 ik_joints = ['joint1', 'joint2', 'joint3'],
#                 ik_ctrl = 'ikHandle1__CTRL',
#                 stretchAxis = 'Y' )

# leg.start()
# leg.build()
