# ------------------------------------------------------
# Auto Rig Foot SetUp
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import sys
import os

import pymel.core as pm

import ShapesLibrary as sl
from CollDict import indexColor
import adbrower

adb = adbrower.Adbrower()

import adb_core.ModuleBase as moduleBase
import adb_core.Class__Control as Control
import adb_core.NameConv_utils as NC
import adb_core.Class__AddAttr as adbAttr
import adb_core.Class__Joint as Joint
import adb_core.Class__Locator as Locator
from adb_core.Class__Transforms import Transform

import adb_library.adb_utils.Func__Piston as adbPiston
import adb_library.adb_utils.Script__LocGenerator as locGen
import adb_library.adb_utils.Script__ProxyPlane as adbProxy
import adb_library.adb_utils.Class__FkShapes as adbFKShape

import adb_library.adb_modules.Module__Folli as adbFolli
import adb_library.adb_modules.Module__IkStretch as adbIkStretch
import adb_library.adb_modules.Module__SquashStretch_Ribbon as adbRibbon
import adb_library.adb_modules.Class__SpaceSwitch as SpaceSwitch

import adb_rigModules.RigBase as RigBase

reload(adbrower)
reload(sl)
reload(Joint)
reload(RigBase)
reload(adbAttr)
reload(adbFKShape)
reload(NC)
reload(moduleBase)
reload(adbIkStretch)
reload(Control)
reload(locGen)
reload(adbPiston)
reload(Locator)
reload(adbFolli)
reload(adbRibbon)
reload(SpaceSwitch)

#-----------------------------------
#  DECORATORS
#-----------------------------------

from adbrower import undo
from adbrower import changeColor
from adbrower import makeroot
from adbrower import lockAttr


#-----------------------------------
# CLASS
#-----------------------------------


class LimbFootModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(LimbFootModel, self).__init__()
        pass

DATA_WEIGHT_PATH = 'C:/Users/Audrey/Documents/maya/projects/Roller_Rigging_Project/data/skinWeights/'


class LimbFoot(moduleBase.ModuleBase):
    """
    """
    def __init__(self,
                 module_name=None,
                ):
        super(LimbFoot, self).__init__('')

        self.nameStructure = None
        self._MODEL = LimbFootModel()
        self.NAME = module_name


    def __repr__(self):
        return str('{} : {} \n {}'.format(self.__class__.__name__, self.subject, self.__class__))

    # =========================
    # METHOD
    # =========================

    def start(self, metaDataNode = 'transform'):
        super(LimbFoot, self)._start('', _metaDataNode = metaDataNode)

        # TODO: Create Guide Setup

    def build(self, GUIDES):
        """
        # TODO : Add Bank System
        # TODO : Automate walking cycle

        """
        super(LimbFoot, self)._build()

        self.RIG = RigBase.RigBase(rigName = self.NAME)
        self.starter_Foot = GUIDES
        self.side = NC.getSideFromPosition(GUIDES[0])

        if self.side == 'R':
            self.col_main = indexColor['fluoRed']
            self.col_layer1 = indexColor['darkRed']
            self.col_layer2 = indexColor['red']
            self.pol_vector_col = (0.5, 0.000, 0.000)
            self.sliding_knee_col = indexColor['darkRed']
        else:
            self.col_main = indexColor['fluoBlue']
            self.col_layer1 = indexColor['blue']
            self.col_layer2 = indexColor['lightBlue']
            self.sliding_knee_col = indexColor['blue']
            self.pol_vector_col = (0, 0.145, 0.588)

        self.nameStructure = {
                            'Side'    : self.side,
                            'Basename': 'Foot',
                            'Parts'   : ['Ankle', 'Ball', 'Toe', 'Heel'],
                            'Suffix'  : ''
                            }

        self.BUILD_MODULES = []


        # =================
        # BUILD

        self.create_foot_ctrl()
        self.footGroupSetup()


    def connect(self,
                legSpaceGroup = None,
                leg_ikHandle = 'L__Leg__IKHDL',
                leg_offset_ik_ctrl = 'L__Leg_IK_offset__CTRL',
                leg_ankle_fk_ctrl = 'L__Leg_Fk_Ankle__CTRL'):

        super(LimbFoot, self)._connect()

        self.connectFootToLeg(legSpaceGroup = legSpaceGroup,
                              leg_ikHandle = leg_ikHandle,
                              leg_offset_ik_ctrl = leg_offset_ik_ctrl,
                              leg_ankle_fk_ctrl = leg_ankle_fk_ctrl,
                              )

        self.addControls()
        self.setup_VisibilityGRP()
        self.cleanUpEmptyGrps()


        # Hiearchy
        for module in self.BUILD_MODULES:
            try:
                pm.parent(module.VISRULE_GRP, self.RIG.VISIBILITY_GRP)
            except:
                pass
            for grp in module.metaDataGRPS:
                pm.parent(grp, self.RIG.SETTINGS_GRP)
                grp.v.set(0)


    # =========================
    # SOLVERS
    # =========================

    # -------------------
    # BUILD SLOVERS
    # -------------------


    def create_foot_ctrl(self):
        self.Foot_MOD = moduleBase.ModuleBase()
        self.BUILD_MODULES += [self.Foot_MOD]
        self.Foot_MOD._start('{Side}__Foot'.format(**self.nameStructure),_metaDataNode = 'transform')
        pm.parent(self.Foot_MOD.metaData_GRP, self.RIG.SETTINGS_GRP)
        pm.parent(self.Foot_MOD.MOD_GRP, self.RIG.MODULES_GRP)

        @changeColor('index', col = self.col_main)
        @lockAttr(['sx', 'sy', 'sz' ])
        def create_ctrl():
            self.nameStructure['Suffix'] = NC.CTRL
            self.foot_ctrl = Control.Control(name='{Side}__{Basename}_Main__{Suffix}'.format(**self.nameStructure),
                                                shape = sl.foot_shape,
                                                scale=2,
                                                matchTransforms = (self.starter_Foot[1], 1,0)
                                                ).control

            Transform(self.foot_ctrl).pivotPoint = Transform(self.starter_Foot[0]).worldTrans
            adb.makeroot_func(self.foot_ctrl, suff='Offset', forceNameConvention=True)
            return self.foot_ctrl
        create_ctrl()

        moduleBase.ModuleBase.setupVisRule([self.foot_ctrl], self.Foot_MOD.VISRULE_GRP)
        pm.parent(self.foot_ctrl.getParent(), self.Foot_MOD.INPUT_GRP)


    def footGroupSetup(self):
        ## Create Attributes
        footAttr = adbAttr.NodeAttr([self.Foot_MOD.metaData_GRP])
        footAttr.addAttr('heelRoll', 0)
        footAttr.addAttr('heelSide', 0)
        footAttr.addAttr('heelTwist', 0)
        footAttr.addAttr('ballRoll', 0)
        footAttr.addAttr('toeRoll', 0)
        footAttr.addAttr('toeSide', 0)
        footAttr.addAttr('toeBend', 0)

        @changeColor('index', 2)
        def createJoints():
            points = [pm.PyNode(guide).getRotatePivot(space='world') for guide in self.starter_Foot]
            self.foot_chain = Joint.Joint.point_base(*points, name='{Side}__{Basename}'.format(**self.nameStructure), chain=True, padding=2)
            self.footAnkle_joint, self.footBall_joint, self.footToes_joint, self.footHeel_joint, = self.foot_chain.joints

            # Parenting the joints
            pm.parent(self.footHeel_joint,  self.footAnkle_joint)

            pm.PyNode(self.footAnkle_joint).rename('{Side}__{Basename}_{Parts[0]}'.format(**self.nameStructure))
            pm.PyNode(self.footBall_joint).rename('{Side}__{Basename}_{Parts[1]}'.format(**self.nameStructure))
            pm.PyNode(self.footToes_joint).rename('{Side}__{Basename}_{Parts[2]}'.format(**self.nameStructure))
            pm.PyNode(self.footHeel_joint).rename('{Side}__{Basename}_{Parts[3]}'.format(**self.nameStructure))
            adb.AutoSuffix(self.foot_chain.joints)

            ## orient joint
            if self.side == NC.RIGTH_SIDE_PREFIX:
                mirror_chain_1 = pm.mirrorJoint(self.footAnkle_joint, mirrorYZ=1)

                mirror_chain_3 = pm.mirrorJoint(mirror_chain_1[0], mirrorBehavior=1, mirrorYZ=1)
                pm.delete(mirror_chain_1,  self.footAnkle_joint)
                self.foot_chain =  Joint.Joint(mirror_chain_3)
                self.footAnkle_joint, self.footBall_joint, self.footToes_joint, self.footHeel_joint = self.foot_chain.joints

                pm.PyNode(self.footAnkle_joint).rename('{Side}__{Basename}_{Parts[0]}'.format(**self.nameStructure))
                pm.PyNode(self.footBall_joint).rename('{Side}__{Basename}_{Parts[1]}'.format(**self.nameStructure))
                pm.PyNode(self.footToes_joint).rename('{Side}__{Basename}_{Parts[2]}'.format(**self.nameStructure))
                pm.PyNode(self.footHeel_joint).rename('{Side}__{Basename}_{Parts[3]}'.format(**self.nameStructure))


            pm.parent(self.footAnkle_joint, self.Foot_MOD.OUTPUT_GRP)
            self.footOffsetGrp = self.createPivotGrps(self.footAnkle_joint, name='{Basename}_Offset'.format(**self.nameStructure))
            pm.makeIdentity(self.footOffsetGrp.getChildren(), n=0, t=1, apply=True, pn=1)
            adb.makeroot_func(self.footOffsetGrp, suff='Output', forceNameConvention=1)
            Transform(self.footOffsetGrp).pivotPoint = Transform(self.footAnkle_joint).worldTrans

            self.foot_chain.radius = 1.0
            self.nameStructure['Suffix'] = NC.VISRULE
            moduleBase.ModuleBase.setupVisRule([self.footAnkle_joint], self.Foot_MOD.VISRULE_GRP, '{Side}__{Basename}_JNT__{Suffix}'.format(**self.nameStructure), True)
            return self.foot_chain.joints



        # ============
        # Build
        # ============
        createJoints()


    def connectFootToLeg(self,
                 legSpaceGroup = None,
                 leg_ikHandle = None,
                 leg_offset_ik_ctrl = None,
                 leg_ankle_fk_ctrl = None,
                 ):

        # ik Foot Connect
        ikBlendGrp = self.createPivotGrps(leg_ikHandle, name='{Basename}_Pivots'.format(**self.nameStructure))
        Transform(ikBlendGrp).pivotPoint = Transform(self.footAnkle_joint).worldTrans
        adbAttr.NodeAttr.copyAttr(self.Foot_MOD.metaData_GRP, [self.foot_ctrl], forceConnection=True)
        [pm.setAttr('{}.{}'.format(self.foot_ctrl, attr), keyable=False) for attr in pm.listAttr(self.foot_ctrl, k=1, v=1, ud=1)]

        self.all_IKFK_attributes = self.setup_SpaceGRP(self.RIG.SPACES_GRP,
                            Ik_FK_attributeName =['{Side}_rotation_{Basename}'.format(**self.nameStructure),
                                                  '{Side}_translation_{Basename}'.format(**self.nameStructure)]
                                                )
        foot_ctrlBlendGrp = adb.makeroot_func(self.foot_ctrl, suff='blend', forceNameConvention=1)

        fk_loc = Locator.Locator.create(name='{Side}__{Basename}_blendFk__LOC'.format(**self.nameStructure)).locators
        pm.matchTransform(fk_loc, leg_ankle_fk_ctrl, pos=1, rot=0)
        pm.parent(fk_loc, leg_ankle_fk_ctrl)

        ik_loc = Locator.Locator.create(name='{Side}__{Basename}_blendIk__LOC'.format(**self.nameStructure)).locators
        pm.matchTransform(ik_loc, leg_offset_ik_ctrl)
        pm.parent(ik_loc, leg_offset_ik_ctrl)

        [pm.PyNode(loc[0]).v.set(0) for loc in [ik_loc, fk_loc]]

        self.footBlendSystem(ctrl_name = self.RIG.SPACES_GRP,
                blend_attribute = self.all_IKFK_attributes[0],
                result_joints = [foot_ctrlBlendGrp],
                ik_joints = ik_loc,
                fk_joints = fk_loc,
                lenght_blend = 1,
                )

        pm.parentConstraint(self.foot_ctrl, self.footOffsetGrp, mo=1)
        const = pm.pointConstraint([fk_loc, ik_loc, foot_ctrlBlendGrp], mo=1)
        fkWeight, ikWeight = pm.pointConstraint(const, q=1, weightAliasList  =1)
        pm.PyNode('{}.{}'.format(self.RIG.SPACES_GRP, self.all_IKFK_attributes[1])) >> pm.PyNode('{}.{}'.format(const, fkWeight))
        reverse=pm.shadingNode('reverse', asUtility=1)
        pm.PyNode('{}.{}'.format(self.RIG.SPACES_GRP, self.all_IKFK_attributes[1])) >> reverse.inputX
        reverse.outputX >> pm.PyNode('{}.{}'.format(const, ikWeight))


    # -------------------
    # CONNECT SLOVERS
    # -------------------

    @lockAttr(['sx', 'sy', 'sz'])
    def addControls(self):
        self.nameStructure['Suffix'] = NC.CTRL
        ball_CTRL = Control.Control(name='{Side}__{Basename}_Ball__{Suffix}'.format(**self.nameStructure),
                                shape = sl.pinX_shape,
                                scale=1,
                                matchTransforms = (self.footBall_joint, 1, 0),
                                parent=self.Foot_MOD.INPUT_GRP,
                                color=('index', self.col_layer2)
                                ).control
        adb.makeroot_func(ball_CTRL, suff='Offset', forceNameConvention=1)
        adb.matrixConstraint(self.footBall_joint, ball_CTRL.getParent(), mo=1)
        ball_CTRL.rx >> pm.PyNode(self.foot_ctrl.ballRoll)


        heel_CTRL = Control.Control(name='{Side}__{Basename}_Heel__{Suffix}'.format(**self.nameStructure),
                                shape = sl.ball2_shape,
                                scale=0.6,
                                matchTransforms = (self.footHeel_joint, 1, 0),
                                parent=self.Foot_MOD.INPUT_GRP,
                                color=('index', self.col_layer2)
                                ).control
        adb.makeroot_func(heel_CTRL, suff='Offset', forceNameConvention=1)
        adb.matrixConstraint(self.footHeel_joint, heel_CTRL.getParent(), mo=1)
        heel_CTRL.rx >> pm.PyNode(self.foot_ctrl.heelRoll)
        heel_CTRL.ry >> pm.PyNode(self.foot_ctrl.heelSide)
        heel_CTRL.rz >> pm.PyNode(self.foot_ctrl.heelTwist)


        toe_CTRL = Control.Control(name='{Side}__{Basename}_Toe__{Suffix}'.format(**self.nameStructure),
                                shape = sl.ball2_shape,
                                scale=0.4,
                                matchTransforms = (self.footToes_joint, 1, 0),
                                parent=self.Foot_MOD.INPUT_GRP,
                                color=('index', self.col_layer2)
                                ).control
        adb.makeroot_func(toe_CTRL, suff='Offset', forceNameConvention=1)
        adb.matrixConstraint(self.footToes_joint, toe_CTRL.getParent(), mo=1)
        toe_CTRL.rx >> pm.PyNode(self.foot_ctrl.toeRoll)
        toe_CTRL.ry >> pm.PyNode(self.foot_ctrl.toeSide)


        toeBend_CTRL = Control.Control(name='{Side}__{Basename}_ToeBend__{Suffix}'.format(**self.nameStructure),
                                shape = sl.cube_shape,
                                scale=0.6,
                                matchTransforms = (self.footBall_joint, 1, 0),
                                parent=self.Foot_MOD.INPUT_GRP,
                                color=('index', self.col_layer2)
                                ).control
        adb.makeroot_func(toeBend_CTRL, suff='Offset', forceNameConvention=1)
        adb.matrixConstraint(self.footBall_joint, toeBend_CTRL.getParent(), mo=1)
        toeBend_CTRL.rx >> pm.PyNode(self.foot_ctrl.toeBend)
        toeBend_CTRL.ry >> pm.PyNode(self.footBall_joint).ry


        return ball_CTRL, heel_CTRL, toe_CTRL, toeBend_CTRL

    def setup_VisibilityGRP(self):
        visGrp = adbAttr.NodeAttr([self.RIG.VISIBILITY_GRP])
        visGrp.AddSeparator(self.RIG.VISIBILITY_GRP, 'Joints')
        visGrp.addAttr('JNT', True)

        visGrp.AddSeparator(self.RIG.VISIBILITY_GRP, 'Controls')
        visGrp.addAttr('Main_CTRL', True)

        for attr in visGrp.allAttrs.keys():
            for module in self.BUILD_MODULES:
                for grp in module.VISRULE_GRP.getChildren():
                    shortName = NC.getBasename(grp).split('{Basename}_'.format(**self.nameStructure))[-1]
                    # print shortName.lower(), '-------------',  attr.lower()
                    if shortName.lower() in attr.lower():
                        pm.connectAttr('{}.{}'.format(visGrp.subject, attr), '{}.vis'.format(grp))


    def cleanUpEmptyGrps(self):
        for ModGrp in self.RIG.MODULES_GRP.getChildren():
            for grp in ModGrp.getChildren():
                if len(grp.getChildren()) is 0:
                    pm.delete(grp)


    # =========================
    # SLOTS
    # =========================

    def footBlendSystem(self,
                    ctrl_name = '',
                    blend_attribute = '',
                    result_joints = [],
                    ik_joints = [],
                    fk_joints = [],
                    lenght_blend = 1,
                    ):
            """
            Function to create an Ik - Fk rotation based script

            @param ctrl_name            : (str) Name of the control having the switch attribute
            @param blend_attribute      : (sr)  Name of blend attribute
            @param result_joints        : (list) List of result joints
            @param ik_joints            : (list) List of ik joints
            @param fk_joints            : (list) List of fk joints

            example:
            ik_fk_switch(ctrl_name = 'locator1',
                        blend_attribute = 'ik_fk_switch',
                        result_joints = ['result_01', 'result_02', 'result_03'],
                        ik_joints = ['ik_01', 'ik_02', 'ik_03'],
                        fk_joints = ['fk_01', 'fk_02', 'fk_03'],
                       )
            """
            ## add attribute message
            switch_ctrl = adbAttr.NodeAttr([ctrl_name])
            switch_ctrl.addAttr('lenght_blend', lenght_blend, keyable=False)

            # Creation of the remaps values and blendColor nodes
            RemapValueColl = [pm.shadingNode('remapValue',asUtility=1, n='{}__{}__{}'.format(self.side, NC.getBasename(x), NC.REMAP_VALUE_SUFFIX)) for x in result_joints]
            BlendColorColl_Rotate = [pm.shadingNode('blendColors', asUtility=1, n='{}__{}_rotate__{}'.format(self.side, NC.getBasename(x), NC.BLENDCOLOR_SUFFIX)) for x in result_joints]
            ## Connect the IK in the Color 2
            for oFK, oBlendColor in zip (fk_joints, BlendColorColl_Rotate):
                fkDecomp = pm.shadingNode('decomposeMatrix', asUtility=1, n='{}__Footrotate__DCPM'.format(self.side))
                pm.PyNode(oFK).worldMatrix[0] >> pm.PyNode(fkDecomp).inputMatrix
                pm.PyNode(fkDecomp).outputRotateX >> pm.PyNode(oBlendColor).color1R
                pm.PyNode(fkDecomp).outputRotateY>> pm.PyNode(oBlendColor).color1G
                pm.PyNode(fkDecomp).outputRotateZ >> pm.PyNode(oBlendColor).color1B

            ## Connect the FK in the Color 1
            for oIK, oBlendColor in zip (ik_joints,BlendColorColl_Rotate):
                ikDecomp = pm.shadingNode('decomposeMatrix', asUtility=1, n='{}__Footrotate__DCPM'.format(self.side))
                pm.PyNode(oIK).worldMatrix[0] >> pm.PyNode(ikDecomp).inputMatrix
                pm.PyNode(ikDecomp).outputRotateX >> pm.PyNode(oBlendColor).color2R
                pm.PyNode(ikDecomp).outputRotateY>> pm.PyNode(oBlendColor).color2G
                pm.PyNode(ikDecomp).outputRotateZ >> pm.PyNode(oBlendColor).color2B

            ## Connect the BlendColor node in the Blend joint chain
            for oBlendColor, oBlendJoint in zip (BlendColorColl_Rotate,result_joints):
                pm.PyNode(oBlendColor).outputR  >> pm.PyNode(oBlendJoint).rx
                pm.PyNode(oBlendColor).outputG  >> pm.PyNode(oBlendJoint).ry
                pm.PyNode(oBlendColor).outputB  >> pm.PyNode(oBlendJoint).rz

            for oBlendColor in BlendColorColl_Rotate:
                pm.PyNode(oBlendColor).blender.set(1)

            ## Connect the Remap Values to Blend Colors
            for oRemapValue,oBlendColor in zip (RemapValueColl, BlendColorColl_Rotate):
                pm.PyNode(oRemapValue).outValue >> pm.PyNode(oBlendColor).blender


            #=================================================================================================
            ## Connect the IK -FK Control to Remap Value
            blend_switch =  '{}.{}'.format(ctrl_name, blend_attribute)

            for each in RemapValueColl:
                pm.PyNode(blend_switch) >> pm.PyNode(each).inputValue
                pm.PyNode('{}.{}'.format(ctrl_name, switch_ctrl.attrName)) >> pm.PyNode(each).inputMax


    def createPivotGrps(self, joint, name, forceConnection=True):
        toeRoll = adb.makeroot_func(joint, suff='ToeRoll', forceNameConvention=True)
        ballRoll = adb.makeroot_func(joint, suff='BallRoll', forceNameConvention=True)
        heelRoll = adb.makeroot_func(joint, suff='HeelRoll', forceNameConvention=True)

        Transform(heelRoll).pivotPoint = Transform(self.footHeel_joint).worldTrans
        Transform(ballRoll).pivotPoint = Transform(self.footBall_joint).worldTrans
        Transform(toeRoll).pivotPoint = Transform(self.footToes_joint).worldTrans

        if forceConnection:
            ## connect Attributes
            pm.PyNode(self.Foot_MOD.metaData_GRP.heelRoll) >> heelRoll.rx
            pm.PyNode(self.Foot_MOD.metaData_GRP.ballRoll) >> ballRoll.rx
            pm.PyNode(self.Foot_MOD.metaData_GRP.toeRoll) >> toeRoll.rx

            pm.PyNode(self.Foot_MOD.metaData_GRP.heelSide) >> heelRoll.ry
            pm.PyNode(self.Foot_MOD.metaData_GRP.heelTwist) >> heelRoll.rz
            pm.PyNode(self.Foot_MOD.metaData_GRP.toeSide) >> toeRoll.ry


            self.nameStructure['Suffix'] = NC.MULTIPLY_DIVIDE_SUFFIX
            mult_node = pm.shadingNode('multiplyDivide', asUtility=1, n='{Side}__{Basename}_toeNegate__{Suffix}'.format(**self.nameStructure))
            self.nameStructure['Suffix'] = NC.PLUS_MIN_AVER_SUFFIX
            pma_node = pm.shadingNode('plusMinusAverage', asUtility=1, n='{Side}__{Basename}_toeNegate__{Suffix}'.format(**self.nameStructure))
            mult_node.input2X.set(-1)
            ballRoll.rx >> mult_node.input1X
            mult_node.outputX >> pma_node.input3D[0].input3Dx
            pm.PyNode(self.Foot_MOD.metaData_GRP.toeBend) >> pma_node.input3D[1].input3Dx
            pma_node.output3Dx >> self.footBall_joint.rx

        footOffsetGrp = adb.makeroot_func(toeRoll, suff='Offset', forceNameConvention=True)
        NC.renameBasename(footOffsetGrp, name)

        return footOffsetGrp


    def setup_SpaceGRP(self, transform, Ik_FK_attributeName=[]):
        switch_ctrl = adbAttr.NodeAttr([transform])
        for name in Ik_FK_attributeName:
            switch_ctrl.addAttr(name, 'enum',  eName = "IK:FK:")

        return Ik_FK_attributeName

# =========================
# BUILD
# =========================

# L_foot = LimbFoot(module_name='L__Foot')
# L_foot.build(['L__ankle_guide', 'L__ball_guide', 'L__toe_guide', 'L__heel_guide'])
# L_foot.connect()


