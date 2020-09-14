# ------------------------------------------------------
# Auto Rig Foot SetUp
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import json
import sys
import os
import ConfigParser
import ast

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

import adb_library.adb_modules.Class__SpaceSwitch as SpaceSwitch

import adb_rigModules.RigBase as rigBase
import adb_rigModules.ModuleGuides as moduleGuides

# reload(adbrower)
# reload(sl)
# reload(Joint)
# reload(adbAttr)
# reload(NC)
# reload(moduleBase)
# reload(Control)
# reload(Locator)
# reload(SpaceSwitch)
# reload(rigBase)
# reload(moduleBase)
# reload(moduleGuides)

#-----------------------------------
#  DECORATORS
#-----------------------------------

from adbrower import undo, changeColor, makeroot, lockAttr

#-----------------------------------
# CLASS
#-----------------------------------


class LimbFootModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(LimbFootModel, self).__init__()
        pass

DATA_WEIGHT_PATH = 'C:/Users/Audrey/Documents/maya/projects/Roller_Rigging_Project/data/skinWeights/'
CONFIG_PATH = 'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_rigModules/adb_biped'

os.chdir(CONFIG_PATH)
with open("BipedConfig.json", "r") as f:
    BIPED_CONFIG = json.load(f)

class LimbFoot(rigBase.RigBase):
    """
    """
    def __init__(self,
                 module_name=None,
                 config = BIPED_CONFIG
                ):
        super(LimbFoot, self).__init__(module_name, _metaDataNode=None)

        self.nameStructure = None
        self._MODEL = LimbFootModel()
        self.NAME = module_name
        self.config = config


    def __repr__(self):
        return str('{} : {} \n {}'.format(self.__class__.__name__, self.MAIN_RIG_GRP, self.__class__))

    # =========================
    # METHOD
    # =========================

    def start(self):
        Gankle, Gball, Gtoe, Gheel = [moduleGuides.ModuleGuides.createFkGuide(prefix='{}_{}'.format(self.NAME, part)) for part in ['Ankle', 'Ball', 'Toe', 'Heel']]
        for guide in [Gankle, Gball, Gtoe, Gheel]:
            pm.parent(guide.guides, self.STARTERS_GRP)

        pm.PyNode(Gankle.guides[0]).translate.set(0, 2.5, 0)
        pm.PyNode(Gball.guides[0]).translate.set(0, 0.5, 2)
        pm.PyNode(Gtoe.guides[0]).translate.set(0, 0.5, 4)
        pm.PyNode(Gheel.guides[0]).translate.set(0, 0.5, -0.8)

        self.curve_setup(Gankle.guides[0], Gball.guides[0])
        self.curve_setup(Gball.guides[0], Gtoe.guides[0])
        self.curve_setup(Gankle.guides[0], Gheel.guides[0])

        self.footGuides = moduleGuides.ModuleGuides(self.NAME.upper(), [Gankle.guides[0], Gball.guides[0], Gtoe.guides[0], Gheel.guides[0]], self.DATA_PATH)
        readPath = self.footGuides.DATA_PATH + '/' + self.footGuides.RIG_NAME + '__GLOC.ini'
        if os.path.exists(readPath):
            self.readData = self.footGuides.readData(readPath)
            for guide in self.footGuides.guides:
                _registeredAttributes = ast.literal_eval(self.readData.get(str(guide), 'registeredAttributes'))
                for attribute in _registeredAttributes:
                    try:
                        pm.setAttr('{}.{}'.format(guide, attribute), ast.literal_eval(self.readData.get(str(guide), str(attribute))))
                    except NoSectionError:
                        pass

        pm.select(None)

    def build(self, GUIDES=None):
        """
        # TODO : Add Bank System
        # TODO : Automate walking cycle

        """
        super(LimbFoot, self)._build()

        if GUIDES is None:
            GUIDES = self.footGuides.guides

        self.starter_Foot = GUIDES
        self.side = NC.getSideFromPosition(GUIDES[0])

        if self.side == 'L':
            self.col_main = indexColor[self.config["COLORS"]['L_col_main']]
            self.col_layer1 = indexColor[self.config["COLORS"]['L_col_layer1']]
            self.col_layer2 = indexColor[self.config["COLORS"]['L_col_layer2']]
            self.pol_vector_col = indexColor[self.config["COLORS"]['L_col_poleVector']]
        elif self.side == 'R':
            self.col_main = indexColor[self.config["COLORS"]['R_col_main']]
            self.col_layer1 = indexColor[self.config["COLORS"]['R_col_layer1']]
            self.col_layer2 = indexColor[self.config["COLORS"]['R_col_layer2']]
            self.pol_vector_col = indexColor[self.config["COLORS"]['R_col_poleVector']]
        else:
            self.col_main = indexColor[self.config["COLORS"]['C_col_main']]
            self.col_layer1 = indexColor[self.config["COLORS"]['C_col_layer1']]
            self.sliding_elbow_col = indexColor[self.config["COLORS"]['C_col_layer2']]
            self.pol_vector_col = indexColor[self.config["COLORS"]['C_col_layer2']]

        self.nameStructure = {
                            'Side'    : self.side,
                            'Basename': 'Foot',
                            'Parts'   : ['Ankle', 'Ball', 'Toe', 'Heel'],
                            'Suffix'  : ''
                            }

        self.BUILD_MODULES = []


        # =================
        # BUILD

        self.Foot_MOD = moduleBase.ModuleBase()
        self.BUILD_MODULES += [self.Foot_MOD]
        self.Foot_MOD._start('{Side}__Foot'.format(**self.nameStructure),_metaDataNode = 'transform')
        pm.parent(self.Foot_MOD.metaData_GRP, self.SETTINGS_GRP)
        pm.parent(self.Foot_MOD.MOD_GRP, self.MODULES_GRP)

        self.footGroupSetup()
        self.create_foot_ctrl()

    def connect(self,
                legSpaceGroup = None,
                leg_ikHandle = [],
                leg_offset_ik_ctrl = [],
                leg_ankle_ik_joint = [],
                leg_ankle_fk_ctrl = []
                ):

        super(LimbFoot, self)._connect()

        self.connectFootToLeg(legSpaceGroup = legSpaceGroup,
                              leg_ikHandle = leg_ikHandle,
                              leg_offset_ik_ctrl = leg_offset_ik_ctrl,
                              leg_ankle_ik_joint = leg_ankle_ik_joint,
                              leg_ankle_fk_ctrl = leg_ankle_fk_ctrl,
                              )

        self.addControls()
        self.setup_VisibilityGRP()
        self.cleanUpEmptyGrps()


        # Hiearchy
        for module in self.BUILD_MODULES:
            try:
                pm.parent(module.VISRULE_GRP, self.VISIBILITY_GRP)
            except:
                pass
            for grp in module.metaDataGRPS:
                pm.parent(grp, self.SETTINGS_GRP)
                grp.v.set(0)

        Transform(self.MODULES_GRP).pivotPoint = Transform(self.foot_ctrl).worldTrans


    # =========================
    # SOLVERS
    # =========================

    # -------------------
    # BUILD SLOVERS
    # -------------------


    def create_foot_ctrl(self):
        @changeColor('index', col = self.col_main)
        @lockAttr(['sx', 'sy', 'sz' ])
        def create_ctrl():
            self.nameStructure['Suffix'] = NC.CTRL
            self.foot_ctrl = Control.Control(name='{Side}__{Basename}_Main__{Suffix}'.format(**self.nameStructure),
                                                shape = sl.sl[self.config['CONTROLS']['Foot']['shape']],
                                                scale=self.config['CONTROLS']['Foot']['scale'],
                                                matchTransforms = (self.starter_Foot[1], 1,0)
                                                ).control
            pm.matchTransform(self.foot_ctrl, self.footAnkle_joint, pos=0, rot=1)
            if self.side == NC.LEFT_SIDE_PREFIX:
                pm.PyNode(self.foot_ctrl).sx.set(-1)
                pm.makeIdentity(self.foot_ctrl, n=0, s=1, apply=True, pn=1)

            Transform(self.foot_ctrl).pivotPoint = Transform(self.footAnkle_joint).worldTrans
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
            pm.PyNode(self.footAnkle_joint).rename('{Side}__{Basename}_{Parts[0]}_END'.format(**self.nameStructure))
            pm.PyNode(self.footBall_joint).rename('{Side}__{Basename}_{Parts[1]}_END'.format(**self.nameStructure))
            pm.PyNode(self.footToes_joint).rename('{Side}__{Basename}_{Parts[2]}_END'.format(**self.nameStructure))
            pm.PyNode(self.footHeel_joint).rename('{Side}__{Basename}_{Parts[3]}_END'.format(**self.nameStructure))
            adb.AutoSuffix(self.foot_chain.joints)

            pm.parent(self.footAnkle_joint, self.Foot_MOD.OUTPUT_GRP)
            self.footOffsetGrp = self.createPivotGrps(self.footAnkle_joint, name='{Basename}_Offset'.format(**self.nameStructure))

            ## orient joint
            if self.side == NC.RIGTH_SIDE_PREFIX:
                mirror_chain_1 = pm.mirrorJoint(self.footAnkle_joint, mirrorYZ=1)
                mirror_chain_3 = pm.mirrorJoint(mirror_chain_1[0], mirrorBehavior=1, mirrorYZ=1)
                pm.delete(self.footAnkle_joint, mirror_chain_1)
                self.foot_chain =  Joint.Joint(mirror_chain_3)
                self.footAnkle_joint, self.footBall_joint, self.footToes_joint, self.footHeel_joint = self.foot_chain.joints

                pm.PyNode(self.footAnkle_joint).rename('{Side}__{Basename}_{Parts[0]}_END'.format(**self.nameStructure))
                pm.PyNode(self.footBall_joint).rename('{Side}__{Basename}_{Parts[1]}_END'.format(**self.nameStructure))
                pm.PyNode(self.footToes_joint).rename('{Side}__{Basename}_{Parts[2]}_END'.format(**self.nameStructure))
                pm.PyNode(self.footHeel_joint).rename('{Side}__{Basename}_{Parts[3]}_END'.format(**self.nameStructure))
                adb.AutoSuffix(self.foot_chain.joints)

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
                 leg_ankle_ik_joint = None,
                 leg_ankle_fk_ctrl = None,
                 ):
        # TODO: ADD SPACE SWITCH TO PIN THE FOOT WHEN IS ON STRETCHY LIMB OR NOT
        # ik Foot Connect

        ikBlendGrp = self.createPivotGrps(leg_ikHandle, name='{Basename}_Pivots'.format(**self.nameStructure))
        Transform(ikBlendGrp).pivotPoint = Transform(self.footAnkle_joint).worldTrans
        adbAttr.NodeAttr.copyAttr(self.Foot_MOD.metaData_GRP, [self.foot_ctrl], forceConnection=True)
        [pm.setAttr('{}.{}'.format(self.foot_ctrl, attr), keyable=False) for attr in pm.listAttr(self.foot_ctrl, k=1, v=1, ud=1)]

        foot_ctrlBlendGrp = adb.makeroot_func(self.foot_ctrl, suff='blend', forceNameConvention=1)

        fk_loc = Locator.Locator.create(name='{Side}__{Basename}_blendFk__LOC'.format(**self.nameStructure)).locators
        pm.matchTransform(fk_loc, leg_ankle_fk_ctrl, pos=1, rot=0)
        pm.parent(fk_loc, leg_ankle_fk_ctrl)

        ik_loc = Locator.Locator.create(name='{Side}__{Basename}_blendIk__LOC'.format(**self.nameStructure)).locators
        pm.matchTransform(ik_loc, leg_offset_ik_ctrl)
        pm.parent(ik_loc, leg_offset_ik_ctrl)

        [pm.PyNode(loc[0]).v.set(0) for loc in [ik_loc, fk_loc]]

        # ==================================================
        # CREATE SPACE SWITCH

        self.footSpaceSwitchTrans = SpaceSwitch.SpaceSwitch('{Side}__Translation_Foot'.format(**self.nameStructure),
                                        spacesInputs =[ik_loc[0], fk_loc[0]],
                                        spaceOutput = foot_ctrlBlendGrp,
                                        maintainOffset = True,
                                        attrNames = ['Ik', 'Fk'])
        self.footSpaceSwitchTrans_attribute = self.footSpaceSwitchTrans.NAME
        self.Foot_MOD.metaDataGRPS += [self.footSpaceSwitchTrans.metaData_GRP]
        adbAttr.NodeAttr.copyAttr(self.footSpaceSwitchTrans.metaData_GRP, [self.SPACES_GRP], forceConnection=True)

        self.footSpaceSwitchRot = SpaceSwitch.SpaceSwitch('{Side}__Rotation_Foot'.format(**self.nameStructure),
                                        spacesInputs =[ik_loc[0], fk_loc[0]],
                                        spaceOutput = foot_ctrlBlendGrp,
                                        maintainOffset = True,
                                        channels='r',
                                        attrNames = ['Ik', 'Fk'])
        self.footSpaceSwitchRot_attribute = self.footSpaceSwitchRot.NAME
        self.Foot_MOD.metaDataGRPS += [self.footSpaceSwitchRot.metaData_GRP]
        adbAttr.NodeAttr.copyAttr(self.footSpaceSwitchRot.metaData_GRP, [self.SPACES_GRP], forceConnection=True)

        try:
            self.footStretchSpaceSwitch = SpaceSwitch.SpaceSwitch('{Side}__Stretch_Foot'.format(**self.nameStructure),
                                    spacesInputs =[leg_ankle_ik_joint, leg_offset_ik_ctrl],
                                    spaceOutput = ik_loc[0],
                                    maintainOffset = False,
                                    channels='t',
                                    attrNames = ['Off', 'On'])
            self.footStretchSpaceSwitch_attribute = self.footStretchSpaceSwitch.NAME
            self.Foot_MOD.metaDataGRPS += [self.footStretchSpaceSwitch.metaData_GRP]
            adbAttr.NodeAttr.copyAttr(self.footStretchSpaceSwitch.metaData_GRP, [self.SPACES_GRP], forceConnection=True)
        except:
            pass

        pm.parentConstraint(self.foot_ctrl, self.footOffsetGrp, mo=1)

    # -------------------
    # CONNECT SLOVERS
    # -------------------

    @lockAttr(['sx', 'sy', 'sz'])
    def addControls(self):
        self.nameStructure['Suffix'] = NC.CTRL
        ball_CTRL = Control.Control(name='{Side}__{Basename}_Ball__{Suffix}'.format(**self.nameStructure),
                                shape = sl.sl[self.config['CONTROLS']['Foot_Ball']['shape']],
                                scale = self.config['CONTROLS']['Foot_Ball']['scale'],
                                matchTransforms = (self.footBall_joint, 1, 0),
                                parent=self.Foot_MOD.INPUT_GRP,
                                color=('index', self.col_layer2)
                                ).control
        if self.side == NC.RIGTH_SIDE_PREFIX:
            ball_CTRL.sx.set(-1)
            pm.makeIdentity(ball_CTRL, n=0, s=1, apply=True, pn=1)

        adb.makeroot_func(ball_CTRL, suff='Offset', forceNameConvention=1)
        adb.matrixConstraint(self.footBall_joint, ball_CTRL.getParent(), mo=1)
        ball_CTRL.rx >> pm.PyNode(self.foot_ctrl.ballRoll)

        heel_CTRL = Control.Control(name='{Side}__{Basename}_Heel__{Suffix}'.format(**self.nameStructure),
                                shape = sl.sl[self.config['CONTROLS']['Foot_Heel']['shape']],
                                scale=self.config['CONTROLS']['Foot_Heel']['scale'],
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
                                shape = sl.sl[self.config['CONTROLS']['Foot_Toe']['shape']],
                                scale=self.config['CONTROLS']['Foot_Toe']['scale'],
                                matchTransforms = (self.footToes_joint, 1, 0),
                                parent=self.Foot_MOD.INPUT_GRP,
                                color=('index', self.col_layer2)
                                ).control
        adb.makeroot_func(toe_CTRL, suff='Offset', forceNameConvention=1)
        adb.matrixConstraint(self.footToes_joint, toe_CTRL.getParent(), mo=1)
        toe_CTRL.rx >> pm.PyNode(self.foot_ctrl.toeRoll)
        toe_CTRL.ry >> pm.PyNode(self.foot_ctrl.toeSide)


        toeBend_CTRL = Control.Control(name='{Side}__{Basename}_ToeBend__{Suffix}'.format(**self.nameStructure),
                                shape = sl.sl[self.config['CONTROLS']['Foot_ToeBend']['shape']],
                                scale=self.config['CONTROLS']['Foot_ToeBend']['scale'],
                                matchTransforms = (self.footBall_joint, 1, 0),
                                parent=self.Foot_MOD.INPUT_GRP,
                                color=('index', self.col_layer2)
                                ).control
        adb.makeroot_func(toeBend_CTRL, suff='Offset', forceNameConvention=1)
        adb.matrixConstraint(self.footBall_joint, toeBend_CTRL.getParent(), mo=1)
        toeBend_CTRL.rx >> pm.PyNode(self.foot_ctrl.toeBend)
        toeBend_CTRL.ry >> pm.PyNode(self.footBall_joint).ry

        self.nameStructure['Suffix'] = NC.VISRULE
        moduleBase.ModuleBase.setupVisRule([ball_CTRL, heel_CTRL, toe_CTRL, toeBend_CTRL], self.Foot_MOD.VISRULE_GRP, '{Side}__{Basename}_Extras_CTRL__{Suffix}'.format(**self.nameStructure), True)
        return ball_CTRL, heel_CTRL, toe_CTRL, toeBend_CTRL


    def setup_VisibilityGRP(self):
        visGrp = adbAttr.NodeAttr([self.VISIBILITY_GRP])
        visGrp.AddSeparator(self.VISIBILITY_GRP, 'Joints')
        visGrp.addAttr('{Side}_{Basename}_JNT'.format(**self.nameStructure), True)

        visGrp.AddSeparator(self.VISIBILITY_GRP, 'Controls')
        visGrp.addAttr('{Side}_{Basename}_Main_CTRL'.format(**self.nameStructure), True)
        visGrp.addAttr('{Side}_{Basename}_Extras_CTRL'.format(**self.nameStructure), True)

        for attr in visGrp.allAttrs.keys():
            for module in self.BUILD_MODULES:
                for grp in module.VISRULE_GRP.getChildren():
                    shortName = NC.getBasename(grp).split('{Basename}_'.format(**self.nameStructure))[-1]
                    # print shortName.lower(), '-------------',  attr.lower()
                    if shortName.lower() in attr.lower():
                        pm.connectAttr('{}.{}'.format(visGrp.subject, attr), '{}.vis'.format(grp))


    def cleanUpEmptyGrps(self):
        for ModGrp in self.MODULES_GRP.getChildren():
            for grp in ModGrp.getChildren():
                if len(grp.getChildren()) is 0:
                    pm.delete(grp)


    # =========================
    # SLOTS
    # =========================


    @changeColor('index', col=2)
    def curve_setup(self, basePoint, endPoint):
        baseJoint = Joint.Joint.point_base(pm.PyNode(basePoint).getRotatePivot(space='world'), name='{}__{}'.format(NC.getNameNoSuffix(basePoint), NC.JOINT)).joints[0]
        endJoint = Joint.Joint.point_base(pm.PyNode(endPoint).getRotatePivot(space='world'), name='{}__{}'.format(NC.getNameNoSuffix(endPoint),  NC.JOINT)).joints[0]
        pm.parent(baseJoint, basePoint)
        pm.parent(endJoint, endPoint)

        starPointPos = pm.xform(basePoint, q=1, ws=1, t=1)
        endPointPos = pm.xform(endPoint, q=1, ws=1, t=1)
        [pm.PyNode(joint).v.set(0) for joint in [baseJoint, endJoint]]

        starting_locs = [baseJoint, endJoint]
        pos = [pm.xform(x, ws=True, q=True, t=True) for x in starting_locs]
        knot = []
        for i in range(len(starting_locs)):
            knot.append(i)
        _curve = pm.curve(p=pos, k=knot, d=1, n='{}_{}_CRV'.format(self.NAME, NC.getNameNoSuffix(baseJoint)))
        pm.skinCluster(baseJoint , _curve, endJoint)
        pm.setAttr(_curve.inheritsTransform, 0)
        pm.setAttr(_curve.template, 1)
        pm.parent(_curve, pm.PyNode(basePoint))
        return _curve


    def createPivotGrps(self, joint, name, forceConnection=True):
        toeRoll = adb.makeroot_func(joint, suff='ToeRoll', forceNameConvention=True)
        ballRoll = adb.makeroot_func(joint, suff='BallRoll', forceNameConvention=True)
        heelRoll = adb.makeroot_func(joint, suff='HeelRoll', forceNameConvention=True)

        Transform(heelRoll).pivotPoint = Transform(self.footHeel_joint).worldTrans
        Transform(ballRoll).pivotPoint = Transform(self.footBall_joint).worldTrans
        Transform(toeRoll).pivotPoint = Transform(self.footToes_joint).worldTrans

        if self.side == NC.RIGTH_SIDE_PREFIX:
            pm.makeIdentity(toeRoll, n=0, r=1, apply=True, pn=1)

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



# =========================
# BUILD
# =========================

# L_foot = LimbFoot(module_name='L__Foot')
# L_foot.start()
# L_foot.build()
# L_foot.connect()


# R_foot = LimbFoot(module_name='R__Foot')
# R_foot.build(['R__ankle_guide', 'R__ball_guide', 'R__toe_guide', 'R__heel_guide'])
