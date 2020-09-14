# ------------------------------------------------------
# Auto Rig Leg SetUp
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
import maya.cmds as mc

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
import adb_library.adb_utils.Functions_AutoPoleVectorSystem as AutoPoleVector
import adb_library.adb_utils.Script__LocGenerator as locGen
import adb_library.adb_utils.Script__ProxyPlane as adbProxy

import adb_library.adb_modules.Module__Folli as adbFolli
import adb_library.adb_modules.Module__IkStretch as adbIkStretch
import adb_library.adb_modules.Module__SquashStretch_Ribbon as adbRibbon
import adb_library.adb_modules.Class__SpaceSwitch as SpaceSwitch
import adb_core.Class__Skinning as Skinning

import adb_rigModules.RigBase as rigBase
import adb_rigModules.ModuleGuides as moduleGuides
import adb_rigModules.adb_biped.Class__LimbFoot as LimbFoot

# reload(adbrower)
# reload(sl)
# reload(Joint)
# reload(adbAttr)
# reload(NC)
# reload(adbIkStretch)
# reload(Control)
# reload(locGen)
# reload(adbPiston)
# reload(Locator)
# reload(adbFolli)
# reload(adbRibbon)
# reload(SpaceSwitch)
# reload(Skinning)
# reload(AutoPoleVector)
# reload(rigBase)
# reload(moduleBase)
# reload(moduleGuides)
reload(LimbFoot)

#-----------------------------------
#  DECORATORS
#-----------------------------------

from adbrower import undo, changeColor, makeroot, lockAttr

#-----------------------------------
# CLASS
#-----------------------------------

#TODO : Add rotationOrder attribute
#TODO : Add Twist rotation on joints

class LimbLegModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(LimbLegModel, self).__init__()
        pass


DATA_WEIGHT_PATH = 'C:/Users/Audrey/Documents/maya/projects/Roller_Rigging_Project/data/skinWeights/'
CONFIG_PATH = 'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_rigModules/adb_biped'

os.chdir(CONFIG_PATH)
with open("BipedConfig.json", "r") as f:
    BIPED_CONFIG = json.load(f)


class LimbLeg(rigBase.RigBase):
    """
    import adb_rigModules.adb_biped.Class__LimbLeg as LimbLeg
    """
    def __init__(self,
                module_name=None,
                config = BIPED_CONFIG
                ):
        super(LimbLeg, self).__init__(module_name, _metaDataNode=None)

        self.nameStructure = None
        self._MODEL = LimbLegModel()
        self.NAME = module_name
        self.config = config

    def __repr__(self):
        return str('{} : {} \n {}'.format(self.__class__.__name__, self.MAIN_RIG_GRP, self.__class__))


    # =========================
    # METHOD
    # =========================

    def start(self, buildFootStatus = False):
        self.buildFootStatus = buildFootStatus
        self.side = NC.getSideFromName(self.NAME)

        Ghips, Gknee, Gankle = [moduleGuides.ModuleGuides.createFkGuide(prefix='{}_{}'.format(self.NAME, part)) for part in ['Hips', 'Knee', 'Ankle']]
        for guide in [Ghips, Gknee, Gankle]:
            pm.parent(guide.guides, self.STARTERS_GRP)

        pm.PyNode(Ghips.guides[0]).translate.set(0, 4, 0)
        pm.PyNode(Gknee.guides[0]).translate.set(0, 2, 0.5)
        pm.PyNode(Gankle.guides[0]).translate.set(0, 0, 0)

        self.curve_setup(Ghips.guides[0], Gknee.guides[0])
        self.curve_setup(Gknee.guides[0], Gankle.guides[0])

        self.legGuides = moduleGuides.ModuleGuides(self.NAME.upper(), [Ghips.guides[0], Gknee.guides[0], Gankle.guides[0]], self.DATA_PATH)
        readPath = self.legGuides.DATA_PATH + '/' + self.legGuides.RIG_NAME + '__GLOC.ini'
        if os.path.exists(readPath):
            self.readData = self.legGuides.readData(readPath)
            for guide in self.legGuides.guides:
                _registeredAttributes = ast.literal_eval(self.readData.get(str(guide), 'registeredAttributes'))
                for attribute in _registeredAttributes:
                    try:
                        pm.setAttr('{}.{}'.format(guide, attribute), ast.literal_eval(self.readData.get(str(guide), str(attribute))))
                    except NoSectionError:
                        pass

        if self.buildFootStatus:
            self.FootRig = LimbFoot.LimbFoot(module_name='{}__Foot'.format(*self.side), config=self.config)
            self.FootRig.start()


        pm.select(None)

    def build(self, GUIDES=None):
        """
        @param GUIDE: List of 3

         Get starting Info
             - Side Info

        CREATE BASE CHAIN

         Ik-FK SWITCH SYSTEM
             - Create IK-FK Switch Control
             - Create Ik Controls & system
             - Create Fk Controls & system
             - Create blend

         STRETCHY LIMB
             - IK Handle

        RIBBON

         SLIDING KNEE
             - Create control
        """
        super(LimbLeg, self)._build()

        if GUIDES is None:
            GUIDES = self.legGuides.guides

        self.starter_Leg = GUIDES
        self.side = NC.getSideFromPosition(GUIDES[0])

        if self.side == 'L':
            self.col_main = indexColor[self.config["COLORS"]['L_col_main']]
            self.col_layer1 = indexColor[self.config["COLORS"]['L_col_layer1']]
            self.sliding_knee_col = indexColor[self.config["COLORS"]['L_col_layer2']]
            self.pol_vector_col = indexColor[self.config["COLORS"]['L_col_poleVector']]
        elif self.side == 'R':
            self.col_main = indexColor[self.config["COLORS"]['R_col_main']]
            self.col_layer1 = indexColor[self.config["COLORS"]['R_col_layer1']]
            self.sliding_knee_col = indexColor[self.config["COLORS"]['R_col_layer2']]
            self.pol_vector_col = indexColor[self.config["COLORS"]['R_col_poleVector']]
        else:
            self.col_main = indexColor[self.config["COLORS"]['C_col_main']]
            self.col_layer1 = indexColor[self.config["COLORS"]['C_col_layer1']]
            self.sliding_elbow_col = indexColor[self.config["COLORS"]['C_col_layer2']]
            self.pol_vector_col = indexColor[self.config["COLORS"]['C_col_layer2']]

        self.nameStructure = {
                            'Side'    : self.side,
                            'Basename': 'Leg',
                            'Parts'   : ['Hips', 'Knee', 'Ankle'],
                            'Suffix'  : ''
                            }

        self.BUILD_MODULES = []

        self.ikFk_MOD = None
        self.SLIDING_KNEE_MOD = None
        self.DOUBLE_KNEE_MOD = None
        self.RIBBON_MOD = None

        # =================
        # BUILD

        self.createResultLegJoints()
        self.ik_fk_system()
        self.stretchyLimb()
        self.slidingKnee()
        self.doubleKnee()
        self.ribbon(volumePreservation=True)

        if self.buildFootStatus:
            self.FootRig.build()

    def connect(self):
        super(LimbLeg, self)._connect()

        self.setup_VisibilityGRP()
        self.setup_SettingGRP()
        self.scalingUniform()
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

        if self.buildFootStatus:
            self.FootRig.connect(
                                leg_ikHandle = self.leg_IkHandle,
                                leg_offset_ik_ctrl = self.leg_IkHandle_ctrl_offset,
                                leg_ankle_ik_joint = self.legIk_MOD.ik_NonStretch_joint[-1],
                                leg_ankle_fk_ctrl = self.fkControls[-1],
                                )

            # connect leg space switch to foot
            pm.PyNode('{}.{}'.format(self.SPACES_GRP, self.Ik_FK_attributeName)) >> pm.PyNode('{}.{}'.format(self.FootRig.SPACES_GRP, self.FootRig.footSpaceSwitchTrans_attribute))
            pm.PyNode('{}.{}'.format(self.SPACES_GRP, self.Ik_FK_attributeName)) >> pm.PyNode('{}.{}'.format(self.FootRig.SPACES_GRP, self.FootRig.footSpaceSwitchRot_attribute))
            self.legIk_MOD.metaData_GRP.Toggle >> pm.PyNode('{}.{}'.format(self.FootRig.SPACES_GRP, self.FootRig.footStretchSpaceSwitch_attribute))

        Transform(self.MODULES_GRP).pivotPoint = Transform(self.base_leg_joints[0]).worldTrans
        # rigBase.loadSkinClustersWeights()

    # =========================
    # SOLVERS
    # =========================

    # -------------------
    # BUILD SLOVERS
    # -------------------

    def createResultLegJoints(self):
        """
        Create basic 3 joints base leg chain
        """
        pm.select(None)
        self.base_leg_joints = [pm.joint() for x in range(len(self.starter_Leg))]
        for joint in self.base_leg_joints:
            pm.parent(joint, w=True)

        for joint, guide in zip(self.base_leg_joints, self.starter_Leg):
            pm.matchTransform(joint,guide, pos=True)

        ## Parenting the joints
        for oParent, oChild in zip(self.base_leg_joints[0:-1], self.base_leg_joints[1:]):
            pm.parent(oChild, None)
            pm.parent(oChild, oParent)

        pm.PyNode(self.base_leg_joints[0]).rename('{Side}__{Basename}_Result_{Parts[0]}'.format(**self.nameStructure))
        pm.PyNode(self.base_leg_joints[1]).rename('{Side}__{Basename}_Result_{Parts[1]}'.format(**self.nameStructure))
        pm.PyNode(self.base_leg_joints[2]).rename('{Side}__{Basename}_Result_{Parts[2]}'.format(**self.nameStructure))

        adb.AutoSuffix(self.base_leg_joints)

        ## orient joint
        if self.side == NC.RIGTH_SIDE_PREFIX:
            mirror_chain_1 = pm.mirrorJoint(self.base_leg_joints[0], mirrorYZ=1)
            Joint.Joint(mirror_chain_1).orientAxis = 'Y'

            mirror_chain_3 = pm.mirrorJoint(mirror_chain_1[0] , mirrorBehavior=1, mirrorYZ=1)
            pm.delete(mirror_chain_1,mirror_chain_1, self.base_leg_joints)
            self.base_leg_joints = [pm.PyNode(x) for x in mirror_chain_3]

            pm.PyNode(self.base_leg_joints[0]).rename('{Side}__{Basename}_Result_{Parts[0]}'.format(**self.nameStructure))
            pm.PyNode(self.base_leg_joints[1]).rename('{Side}__{Basename}_Result_{Parts[1]}'.format(**self.nameStructure))
            pm.PyNode(self.base_leg_joints[2]).rename('{Side}__{Basename}_Result_{Parts[2]}'.format(**self.nameStructure))
            adb.AutoSuffix(self.base_leg_joints)
        else:
            Joint.Joint(self.base_leg_joints).orientAxis = 'Y'


    def ik_fk_system(self):
        """
        Create an IK-FK blend system
        """

        self.ikFk_MOD = moduleBase.ModuleBase()
        self.ikFk_MOD.hiearchy_setup('{Side}__Ik_FK'.format(**self.nameStructure))
        self.BUILD_MODULES += [self.ikFk_MOD]

        @changeColor('index', 3)
        def IkJointChain():
            self.ik_leg_joints = pm.duplicate(self.base_leg_joints)
            pm.PyNode(self.ik_leg_joints[0]).rename('{Side}__{Basename}_Ik_{Parts[0]}'.format(**self.nameStructure))
            pm.PyNode(self.ik_leg_joints[1]).rename('{Side}__{Basename}_Ik_{Parts[1]}'.format(**self.nameStructure))
            pm.PyNode(self.ik_leg_joints[2]).rename('{Side}__{Basename}_Ik_{Parts[2]}'.format(**self.nameStructure))
            adb.AutoSuffix(self.ik_leg_joints)

            pm.parent(self.ik_leg_joints[0], self.ikFk_MOD.RIG_GRP)

            self.nameStructure['Suffix'] = NC.VISRULE
            moduleBase.ModuleBase.setupVisRule(self.ik_leg_joints, self.ikFk_MOD.VISRULE_GRP, '{Side}__{Basename}_Ik_JNT__{Suffix}'.format(**self.nameStructure), False)

            return self.ik_leg_joints


        @changeColor('index', 28)
        def FkJointChain():
            self.fk_leg_joints = pm.duplicate(self.base_leg_joints)
            pm.PyNode(self.fk_leg_joints[0]).rename('{Side}__{Basename}_Fk_{Parts[0]}'.format(**self.nameStructure))
            pm.PyNode(self.fk_leg_joints[1]).rename('{Side}__{Basename}_Fk_{Parts[1]}'.format(**self.nameStructure))
            pm.PyNode(self.fk_leg_joints[2]).rename('{Side}__{Basename}_Fk_{Parts[2]}'.format(**self.nameStructure))
            adb.AutoSuffix(self.fk_leg_joints)

            self.nameStructure['Suffix'] = NC.VISRULE
            visRuleGrp, attribute = moduleBase.ModuleBase.setupVisRule([self.fk_leg_joints[0]], self.ikFk_MOD.VISRULE_GRP, name='{Side}__{Basename}_Fk_JNT__{Suffix}'.format(**self.nameStructure), defaultValue = False)
            adb.breakConnection(self.fk_leg_joints[0], attributes=['v'])
            self.fk_leg_joints[0].v.set(1)
            self.nameStructure['Suffix'] = NC.REMAP_VALUE_SUFFIX
            _remapValue = pm.shadingNode('remapValue', asUtility=1, n='{Side}__{Basename}_Fk_visRule__{Suffix}'.format(**self.nameStructure))
            _remapValue.outputMin.set(2)
            _remapValue.outputMax.set(0)
            pm.connectAttr('{}.{}'.format(visRuleGrp, attribute), '{}.inputValue'.format(_remapValue))
            for bone in self.fk_leg_joints:
                pm.connectAttr('{}.outValue'.format(_remapValue), '{}.drawStyle'.format(bone))
            pm.parent(self.fk_leg_joints[0], self.ikFk_MOD.RIG_GRP)
            return self.fk_leg_joints


        def createIKFKSwitchControl():
            """Swtich Control options """

            self.ikfk_ctrl = sl.ik_fk_shape()
            if self.side == NC.RIGTH_SIDE_PREFIX:
                _shapes = pm.PyNode(self.ikfk_ctrl).getShapes()

                pm.select('{}.cv[:]'.format(_shapes[0]))
                pm.select('{}.cv[:]'.format(_shapes[1]), add=True)
                pm.select('{}.cv[:]'.format(_shapes[2]), add=True)
                pm.select('{}.cv[:]'.format(_shapes[3]), add=True)

                pm.move(-3, 0, 0, r=1, os=1, wd=1)
            else:
                pass

            pm.matchTransform(self.ikfk_ctrl,self.base_leg_joints[-1], pos=True)
            adb.makeroot_func(self.ikfk_ctrl)

            CtrlName = '{Side}__{Basename}_Options'.format(**self.nameStructure)
            self.ikfk_ctrl.rename(CtrlName)
            adb.AutoSuffix([self.ikfk_ctrl])
            self.ikfk_ctrl.addAttr('IK_FK_Switch', keyable=True, attributeType='enum', en="IK:FK")


        @changeColor('index', col = self.col_main )
        def CreateFkcontrols():
            """Creates the FK controls on the Fk joint chain """
            FkShapeSetup = Control.Control.fkShape(joints=self.fk_leg_joints,
                                                    shape=sl.sl[self.config['CONTROLS']['FK_Control']['shape']],
                                                    scale=self.config['CONTROLS']['FK_Control']['scale'],
                                                    )

            shapes = [ctl.getShape() for ctl in FkShapeSetup]
            self.nameStructure['Suffix'] = NC.VISRULE
            visRuleGrp, attribute = moduleBase.ModuleBase.setupVisRule(shapes, self.ikFk_MOD.VISRULE_GRP, name='{Side}__{Basename}_Fk_CTRL__{Suffix}'.format(**self.nameStructure))
            return FkShapeSetup


        def CreateIKcontrols():
            """
            Create the IK handle setup on the IK joint chain
            """
            self.nameStructure['Suffix'] = NC.IKHANDLE_SUFFIX
            leg_IkHandle = pm.ikHandle(n='{Side}__{Basename}__{Suffix}'.format(**self.nameStructure), sj=self.ik_leg_joints[0], ee=self.ik_leg_joints[-1])
            leg_IkHandle[0].v.set(0)
            self.leg_IkHandle = leg_IkHandle[0]

            vec1 = self.base_leg_joints[0].getTranslation(space='world') # "hips"
            vec2 = self.base_leg_joints[1].getTranslation(space='world') # "knee"
            vec3 = self.base_leg_joints[2].getTranslation(space='world') # "ankle"

            # 1. Calculate a "nice distance" based on average of the two bone lengths.
            legLength = (vec2-vec1).length()
            kneeLength = (vec3-vec2).length()
            distance = (legLength + kneeLength) * 0.5

            @makeroot('')
            @changeColor('index', col = self.col_main)
            def Ik_ctrl():
                self.nameStructure['Suffix'] = NC.CTRL
                _leg_IkHandle_ctrl = Control.Control(name='{Side}__{Basename}_IK__{Suffix}'.format(**self.nameStructure),
                                                 shape=sl.sl[self.config['CONTROLS']['IK_Control']['shape']],
                                                 scale=self.config['CONTROLS']['IK_Control']['scale'],
                                                 matchTransforms = (self.base_leg_joints[-1], 1, 0)
                                                 ).control
                moduleBase.ModuleBase.setupVisRule([_leg_IkHandle_ctrl], self.ikFk_MOD.VISRULE_GRP)
                return _leg_IkHandle_ctrl
            self.leg_IkHandle_ctrl = Ik_ctrl()[0]

            @makeroot('')
            @changeColor('index', col = self.col_main)
            def Ik_ctrl_offset():
                _leg_IkHandle_ctrl_offset = Control.Control(name='{Side}__{Basename}_IK_Offset__{Suffix}'.format(**self.nameStructure),
                                 shape = sl.sl[self.config['CONTROLS']['IK_Control_Offset']['shape']],
                                 scale = self.config['CONTROLS']['IK_Control_Offset']['scale'],
                                 parent = self.leg_IkHandle_ctrl,
                                 matchTransforms = (self.base_leg_joints[-1], 1, 0)
                                 ).control
                moduleBase.ModuleBase.setupVisRule([_leg_IkHandle_ctrl_offset], self.ikFk_MOD.VISRULE_GRP)
                return _leg_IkHandle_ctrl_offset
            self.leg_IkHandle_ctrl_offset = Ik_ctrl_offset()[0]

            @lockAttr(att_to_lock = ['rx','ry','rz','sx','sy','sz'])
            @changeColor('index', col = self.pol_vector_col)
            @makeroot()
            def pole_vector_ctrl(name ='{Side}__{Basename}_PoleVector____{Suffix}'.format(**self.nameStructure)):
                pv_guide = adb.PvGuide(leg_IkHandle[0],self.ik_leg_joints[-2], exposant=self.config['CONTROLS']['PoleVector_Control']['exposant']*distance)
                self.poleVectorCtrl = Control.Control(name=name,
                                 shape = sl.sl[self.config['CONTROLS']['PoleVector_Control']['shape']],
                                 scale = self.config['CONTROLS']['PoleVector_Control']['scale'],
                                 ).control
                last_point = pm.PyNode(pv_guide).getCVs()
                pm.move(self.poleVectorCtrl, last_point[-1])
                pm.poleVectorConstraint(self.poleVectorCtrl, leg_IkHandle[0], weight=1)

                def curve_setup():
                    pm.select(self.poleVectorCtrl, r=True)
                    pv_tip_jnt = adb.jointAtCenter()[0]
                    pm.rename(pv_tip_jnt, '{Side}__{Basename}pvTip__{Suffix}'.format(**self.nameStructure))
                    pm.parent(pv_tip_jnt, self.poleVectorCtrl)

                    _loc = pm.spaceLocator(p= adb.getWorldTrans([self.ik_leg_joints[-2]]))
                    mc.CenterPivot()
                    pm.select(_loc, r=True)
                    self.pv_base_jnt = adb.jointAtCenter()[0]
                    pm.delete(_loc)
                    self.nameStructure['Suffix'] = NC.JOINT
                    pm.rename(self.pv_base_jnt, '{Side}__{Basename}pvBase__{Suffix}'.format(**self.nameStructure))
                    pm.skinCluster(self.pv_base_jnt , pv_guide, pv_tip_jnt)
                    pm.matchTransform(self.pv_base_jnt, self.ik_leg_joints[1])
                    pm.parent(self.pv_base_jnt, self.ik_leg_joints[1])
                    pm.setAttr(pv_guide.inheritsTransform, 0)
                    pm.setAttr(pv_guide.overrideDisplayType, 1)
                    [pm.setAttr('{}.drawStyle'.format(joint),  2) for joint in [pv_tip_jnt, self.pv_base_jnt]]
                    pm.parent(pv_guide, self.ikFk_MOD.RIG_GRP)
                    return pv_guide

                pv_guide = curve_setup()

                pm.parent(self.poleVectorCtrl, self.ikFk_MOD.INPUT_GRP)
                self.nameStructure['Suffix'] = NC.VISRULE
                moduleBase.ModuleBase.setupVisRule([self.poleVectorCtrl, pv_guide], self.ikFk_MOD.VISRULE_GRP, '{Side}__{Basename}_PoleVector_CTRL__{Suffix}'.format(**self.nameStructure), False)
                return self.poleVectorCtrl

            pole_vector_ctrl()

            # ==================================================
            # CREATE SPACE SWITCH PV CONTROL

            # AUTO SPACE
            autPoleVectorGrp, autPoleVectorSpaceLoc = AutoPoleVector.autoPoleVectorSystem(prefix=self.NAME,
                                 ikCTL = self.leg_IkHandle_ctrl_offset,
                                 ikJointChain = self.ik_leg_joints,
                                 poleVectorCTL = self.poleVectorCtrl,
                                 )
            [pm.setAttr('{}.r{}'.format(self.ik_leg_joints[2], axis), 0) for axis in 'xyz']
            pm.parent(autPoleVectorGrp, self.ikFk_MOD.INPUT_GRP)

            autPoleVectorGrpEnd = pm.createNode('transform', n='{Side}__{Basename}_PV_SPACES_SWITCH_AUTO__GRP'.format(**self.nameStructure))
            pm.matchTransform(autPoleVectorGrpEnd, self.poleVectorCtrl)
            pm.parent(autPoleVectorGrpEnd, self.SPACES_GRP)
            pm.parentConstraint(autPoleVectorSpaceLoc.getChildren()[0], autPoleVectorGrpEnd, mo=True)

            # WORLD SPACE
            ikSpaceSwitchWorldGrp = pm.group(n='{Side}__{Basename}_PV_SPACES_SWITCH_WORLD__GRP'.format(**self.nameStructure), em=1, parent=self.WORLD_LOC)
            pm.matchTransform(ikSpaceSwitchWorldGrp, self.poleVectorCtrl, pos=1, rot=1)
            ikSpaceSwitchWorldGrp.v.set(0)

            # MAIN CTRL SPACE
            ikSpaceSwitchMainCTRLGrp = pm.group(n='{Side}__{Basename}PV_SPACES_SWITCH_MAINCTRL__GRP'.format(**self.nameStructure), em=1, parent=self.MAIN_CTRL_LOC)
            ikSpaceSwitchMainCTRLGrp.v.set(0)
            pm.matchTransform(ikSpaceSwitchMainCTRLGrp, self.poleVectorCtrl, pos=1, rot=1)

            # ANKLE SPACE
            ikSpaceSwitcAnkleGrp = pm.group(n='{Side}__{Basename}_PV_SPACES_SWITCH_ANKLE__GRP'.format(**self.nameStructure), em=1, parent=self.SPACES_GRP)
            pm.matchTransform(ikSpaceSwitcAnkleGrp, self.poleVectorCtrl, pos=1, rot=1)
            pm.parentConstraint(self.leg_IkHandle_ctrl_offset, ikSpaceSwitcAnkleGrp, mo=True)

            self.povSpaceSwitch = SpaceSwitch.SpaceSwitch('{Side}__PoleVector'.format(**self.nameStructure),
                                                    spacesInputs =[autPoleVectorGrpEnd, ikSpaceSwitcAnkleGrp, ikSpaceSwitchWorldGrp, ikSpaceSwitchWorldGrp],
                                                    spaceOutput = self.poleVectorCtrl.getParent(),
                                                    maintainOffset = False,
                                                    attrNames = ['auto', 'ankle', 'mainCTRL', 'world'])
            self.ikFk_MOD.metaDataGRPS += [self.povSpaceSwitch.metaData_GRP]

            # ==================================================
            # CREATE SPACE SWITCH FOR IK CTRL

            # WORLD SPACE
            ikSpaceSwitchWorldGrpLeg = pm.group(n='{Side}__{Basename}_IK_SPACES_SWITCH_WORLD__GRP'.format(**self.nameStructure), em=1, parent=self.WORLD_LOC)
            ikSpaceSwitchWorldGrp.v.set(0)
            pm.matchTransform(ikSpaceSwitchWorldGrpLeg, self.leg_IkHandle_ctrl_offset, pos=1, rot=1)

            # MAIN CTRL SPACE
            ikSpaceSwitchMainCTRLGrpLeg = pm.group(n='{Side}__{Basename}PV_SPACES_SWITCH_MAINCTRL__GRP'.format(**self.nameStructure), em=1, parent=self.MAIN_CTRL_LOC)
            ikSpaceSwitchMainCTRLGrpLeg.v.set(0)
            pm.matchTransform(ikSpaceSwitchMainCTRLGrpLeg, self.leg_IkHandle_ctrl_offset, pos=1, rot=1)

            # HIPS SPACE
            self.ikSpaceSwitchHipsdGrp = pm.group(n='{Side}__{Basename}_IK_SPACES_SWITCH_HIPS__GRP'.format(**self.nameStructure), em=1, parent=self.SPACES_GRP)
            pm.matchTransform(self.ikSpaceSwitchHipsdGrp, self.leg_IkHandle_ctrl, pos=1, rot=1)

            self.ikLegSpaceSwitch = SpaceSwitch.SpaceSwitch('{Side}__{Basename}_IK'.format(**self.nameStructure),
                                                    spacesInputs =[ikSpaceSwitchMainCTRLGrpLeg, ikSpaceSwitchWorldGrpLeg, self.ikSpaceSwitchHipsdGrp],
                                                    spaceOutput = self.leg_IkHandle_ctrl.getParent(),
                                                    maintainOffset = False,
                                                    attrNames = ['mainCTRL', 'world', 'hips'])
            self.ikFk_MOD.metaDataGRPS += [self.ikLegSpaceSwitch.metaData_GRP]


            pm.parent(leg_IkHandle[0], self.leg_IkHandle_ctrl_offset)
            pm.parent(self.leg_IkHandle_ctrl.getParent(), self.ikFk_MOD.INPUT_GRP)


        def makeConnections():
            self.Ik_FK_attributeName = self.setup_SpaceGRP(self.SPACES_GRP, Ik_FK_attributeName ='{Side}_{Basename}_IK_FK'.format(**self.nameStructure))
            for index, part in zip(xrange(3), self.nameStructure['Parts']):
                self.nameStructure['Suffix'] = part
                legSpaceSwitch = SpaceSwitch.SpaceSwitch('{Side}__{Basename}_{Suffix}IKFK'.format(**self.nameStructure),
                                 spacesInputs =[self.ik_leg_joints[index], self.fk_leg_joints[index]],
                                 spaceOutput = self.base_leg_joints[index],
                                 maintainOffset = True,
                                 channels='trs',
                                 attrNames = ['Ik', 'Fk'])

                pm.connectAttr('{}.{}'.format(self.SPACES_GRP, self.Ik_FK_attributeName), '{}.{}'.format(legSpaceSwitch.metaData_GRP, legSpaceSwitch.NAME))
                self.ikFk_MOD.metaDataGRPS += [legSpaceSwitch.metaData_GRP]

            pm.parent(self.base_leg_joints[0], self.ikFk_MOD.OUTPUT_GRP)

        IkJointChain()
        FkJointChain()
        self.fkControls = CreateFkcontrols()
        CreateIKcontrols()
        makeConnections()

        visRuleGrp = moduleBase.ModuleBase.setupVisRule(self.base_leg_joints, self.ikFk_MOD.VISRULE_GRP, '{Side}__{Basename}_Result_JNT__{Suffix}'.format(**self.nameStructure), False)[0]

        pm.parent(self.ikFk_MOD.MOD_GRP, self.MODULES_GRP)
        Joint.Joint(self.base_leg_joints).radius = self.config['JOINTS']["Result_JNT"]['radius']
        Joint.Joint(self.fk_leg_joints).radius = self.config['JOINTS']["FK_JNT"]['radius']
        Joint.Joint(self.ik_leg_joints).radius = self.config['JOINTS']["IK_JNT"]['radius']


    def stretchyLimb(self):
        self.legIk_MOD = adbIkStretch.stretchyIK('{Side}__StretchylegIk'.format(**self.nameStructure),
                    ik_joints=self.ik_leg_joints,
                    ik_ctrl=self.leg_IkHandle_ctrl_offset,
                    poleVector_ctrl=self.poleVectorCtrl,
                    stretchAxis='Y'
                    )
        self.legIk_MOD.start(metaDataNode='transform')
        self.legIk_MOD.metaDataGRPS += [self.legIk_MOD.metaData_GRP]
        self.legIk_MOD.metaData_GRP.Toggle.set(self.config['ATTRIBUTES']["StretchyLimb"])
        self.BUILD_MODULES += [self.legIk_MOD]

        self.legIk_MOD.build()
        pm.pointConstraint(self.ik_leg_joints[0], self.legIk_MOD.posLoc[0], mo=True)
        pm.parent((self.leg_IkHandle_ctrl_offset).getParent(), self.leg_IkHandle_ctrl)
        pm.parent(self.legIk_MOD.MOD_GRP, self.MODULES_GRP)


    def slidingKnee(self):
        self.SLIDING_KNEE_MOD = moduleBase.ModuleBase()
        self.SLIDING_KNEE_MOD.hiearchy_setup('{Side}__SlidingKnee'.format(**self.nameStructure))
        self.BUILD_MODULES += [self.SLIDING_KNEE_MOD]

        def createUpperPart():
            topLocs = locGen.locGenerator(2, str(self.base_leg_joints[0]), str(self.base_leg_joints[1]))
            points = []
            points.append(pm.PyNode(self.base_leg_joints[0]).getRotatePivot(space='world'))
            points += [pm.PyNode(x).getRotatePivot() for x in topLocs]
            points.append(pm.PyNode(self.base_leg_joints[1]).getRotatePivot(space='world'))
            pm.delete(topLocs)

            topJointsPiston = Joint.Joint.point_base(*points, name='{Side}__{Basename}_upperPiston'.format(**self.nameStructure), padding=2).joints
            adb.AutoSuffix(topJointsPiston)

            topJoints = Joint.Joint.point_base(*points, name='{Side}__{Basename}_upperSlidingKnee'.format(**self.nameStructure), padding=2).joints
            adb.AutoSuffix(topJoints)
            self.SLIDING_KNEE_MOD.getJoints += topJoints

            @makeroot()
            def hipSlidingKnee_ctrl():
                hipSlidingKnee_CTL = Control.Control(name='{Side}__{Basename}_{Parts[0]}_slidingKnee'.format(**self.nameStructure),
                                shape=sl.sl[self.config['CONTROLS']['Sliding_Knee_Hip']['shape']],
                                scale=self.config['CONTROLS']['Sliding_Knee_Hip']['scale'],
                                parent=self.SLIDING_KNEE_MOD.INPUT_GRP,
                                matchTransforms=(self.base_leg_joints[0], 1,0)
                                ).control
                return hipSlidingKnee_CTL

            @makeroot()
            def kneeSlidingKnee01_ctrl():
                kneeSlidingKnee01_CTL = Control.Control(name='{Side}__{Basename}_{Parts[1]}_slidingKnee_01'.format(**self.nameStructure),
                                shape=sl.sl[self.config['CONTROLS']['Sliding_Knee_Knee_01']['shape']],
                                scale=self.config['CONTROLS']['Sliding_Knee_Knee_01']['scale'],
                                parent=self.SLIDING_KNEE_MOD.INPUT_GRP,
                                matchTransforms=(self.base_leg_joints[1], 1,0),
                                color = ('index', self.col_layer1)
                                ).control
                return kneeSlidingKnee01_CTL

            hipSlidingKnee_CTL = hipSlidingKnee_ctrl()[0]
            kneeSlidingKnee01_CTL = kneeSlidingKnee01_ctrl()[0]

            pm.parent(topJointsPiston[0], self.SLIDING_KNEE_MOD.RIG_GRP)
            pm.parent(topJointsPiston[-1], self.SLIDING_KNEE_MOD.RIG_GRP)

            pm.parentConstraint(hipSlidingKnee_CTL, topJointsPiston[0], mo=1)
            pm.parentConstraint(kneeSlidingKnee01_CTL, topJointsPiston[-1], mo=1)

            pistons_pairs = [
                [topJointsPiston[0], topJointsPiston[1], kneeSlidingKnee01_CTL],
                [topJointsPiston[3], topJointsPiston[2], hipSlidingKnee_CTL],
            ]

            ## create piston system
            for pairs in pistons_pairs:
                adbPiston.createPiston(*pairs)

            ## connect the 2 joint chain together
            for pistonJnt, jnt in zip(topJointsPiston, topJoints):
                adb.matrixConstraint(str(pistonJnt), str(jnt), channels='t', mo=True)

            for jnt in topJoints:
                adb.matrixConstraint(str(self.base_leg_joints[0]), str(jnt), channels='rs', mo=True)

            return hipSlidingKnee_CTL, kneeSlidingKnee01_CTL


        def createLowerPart():
            lowLocs = locGen.locGenerator(2, str(self.base_leg_joints[1]), str(self.base_leg_joints[2]))
            points = []
            points.append(pm.PyNode(self.base_leg_joints[1]).getRotatePivot(space='world'))
            points += [pm.PyNode(x).getRotatePivot() for x in lowLocs]
            points.append(pm.PyNode(self.base_leg_joints[2]).getRotatePivot(space='world'))

            lowerJointsPiston = Joint.Joint.point_base(*points, name='{Side}__{Basename}_lowerPiston'.format(**self.nameStructure), padding=2).joints
            adb.AutoSuffix(lowerJointsPiston)

            lowerJoints = Joint.Joint.point_base(*points, name='{Side}__{Basename}_lowerSlidingKnee'.format(**self.nameStructure), padding=2).joints
            adb.AutoSuffix(lowerJoints)
            self.SLIDING_KNEE_MOD.getJoints += lowerJoints

            @makeroot()
            def kneeSlidingKnee02_ctrl():
                kneeSlidingKnee02_CTL = Control.Control(name='{Side}__{Basename}_{Parts[1]}_slidingKnee_02'.format(**self.nameStructure),
                                shape=sl.sl[self.config['CONTROLS']['Sliding_Knee_Knee_02']['shape']],
                                scale=self.config['CONTROLS']['Sliding_Knee_Knee_02']['scale'],
                                parent=self.SLIDING_KNEE_MOD.INPUT_GRP,
                                matchTransforms=(self.base_leg_joints[1], 1,0)
                                ).control
                return kneeSlidingKnee02_CTL

            @makeroot()
            def ankleSlidingKnee_ctrl():
                ankleSlidingKnee_CTL = Control.Control(name='{Side}__{Basename}_{Parts[2]}_slidingKnee'.format(**self.nameStructure),
                                shape=sl.sl[self.config['CONTROLS']['Sliding_Knee_ankle']['shape']],
                                scale=self.config['CONTROLS']['Sliding_Knee_ankle']['scale'],
                                parent=self.SLIDING_KNEE_MOD.INPUT_GRP,
                                matchTransforms=(self.base_leg_joints[2], 1,0)
                                ).control
                return ankleSlidingKnee_CTL

            kneeSlidingKnee02_CTL = kneeSlidingKnee02_ctrl()[0]
            ankleSlidingKnee_CTL = ankleSlidingKnee_ctrl()[0]

            pm.parent(lowerJointsPiston[0], self.SLIDING_KNEE_MOD.RIG_GRP)
            pm.parent(lowerJointsPiston[-1], self.SLIDING_KNEE_MOD.RIG_GRP)

            pm.parentConstraint(kneeSlidingKnee02_CTL, lowerJointsPiston[0], mo=1)
            pm.parentConstraint(ankleSlidingKnee_CTL, lowerJointsPiston[-1], mo=1)

            pistons_pairs = [
                [lowerJointsPiston[0], lowerJointsPiston[1], ankleSlidingKnee_CTL],
                [lowerJointsPiston[3], lowerJointsPiston[2], kneeSlidingKnee02_CTL],
            ]

            for pairs in pistons_pairs:
                adbPiston.createPiston(*pairs)

            ## connect the 2 joint chain together
            for pistonJnt, jnt in zip(lowerJointsPiston, lowerJoints):
                adb.matrixConstraint(str(pistonJnt), str(jnt), channels='t', mo=True)

            for jnt in lowerJoints:
                adb.matrixConstraint(str(self.base_leg_joints[1]), str(jnt), channels='rs', mo=True)

            pm.delete(lowLocs)

            return kneeSlidingKnee02_CTL, ankleSlidingKnee_CTL

        ## BUILD
        ##-------------
        hipSlidingKnee_CTL, kneeSlidingKnee01_CTL = createUpperPart()
        kneeSlidingKnee02_CTL, ankleSlidingKnee_CTL = createLowerPart()

        [self.SLIDING_KNEE_MOD.getControls.append(ctl) for ctl in [hipSlidingKnee_CTL, kneeSlidingKnee01_CTL, kneeSlidingKnee02_CTL, ankleSlidingKnee_CTL]]
        [ctl.v.set(0) for ctl in self.SLIDING_KNEE_MOD.getControls if ctl is not kneeSlidingKnee01_CTL]
        pm.parent(kneeSlidingKnee02_CTL.getParent(), kneeSlidingKnee01_CTL)
        pm.parent(self.SLIDING_KNEE_MOD.getJoints, self.SLIDING_KNEE_MOD.OUTPUT_GRP)

        pm.parent(self.SLIDING_KNEE_MOD.MOD_GRP, self.MODULES_GRP)

        self.SLIDING_KNEE_MOD.getControls.append(kneeSlidingKnee01_CTL)
        self.SLIDING_KNEE_MOD.getResetControls.append(kneeSlidingKnee01_CTL.getParent())

        ## CONNECT
        ##--------------
        for jnt, ctl in zip(self.base_leg_joints, [hipSlidingKnee_CTL, kneeSlidingKnee01_CTL, ankleSlidingKnee_CTL]):
            pm.parentConstraint(jnt, ctl.getParent(), mo=True)

        pm.parent(self.pv_base_jnt, kneeSlidingKnee01_CTL)
        moduleBase.ModuleBase.setupVisRule([self.SLIDING_KNEE_MOD.OUTPUT_GRP, self.SLIDING_KNEE_MOD.RIG_GRP], self.SLIDING_KNEE_MOD.VISRULE_GRP, '{Side}__{Basename}_SlidingKnee_JNT__{Suffix}'.format(**self.nameStructure), False)


    def doubleKnee(self):
        self.DOUBLE_KNEE_MOD = moduleBase.ModuleBase()
        self.DOUBLE_KNEE_MOD.hiearchy_setup('{Side}__DoubleKnee'.format(**self.nameStructure))
        self.BUILD_MODULES += [self.DOUBLE_KNEE_MOD]

        @makeroot()
        def doubleKnee_ctrl():
            doubleKnee_ctrl = Control.Control(name='{Side}__{Basename}_DoubleKnee'.format(**self.nameStructure),
                            shape=sl.sl[self.config['CONTROLS']['Double_Knee']['shape']],
                            scale=self.config['CONTROLS']['Double_Knee']['scale'],
                            parent=self.DOUBLE_KNEE_MOD.INPUT_GRP,
                            matchTransforms=(baseJoint, 1, 0),
                            color = ('index', self.col_layer1)
                            ).control
            return doubleKnee_ctrl

        baseJoint = Joint.Joint.create(name='{Side}__{Basename}_baseDoubleKnee'.format(**self.nameStructure)).joints
        topJoint = Joint.Joint.create(name='{Side}__{Basename}_topDoubleKnee'.format(**self.nameStructure)).joints
        botJoint = Joint.Joint.create(name='{Side}__{Basename}_botDoubleKnee'.format(**self.nameStructure)).joints
        self.DOUBLE_KNEE_MOD.getJoints += baseJoint
        self.DOUBLE_KNEE_MOD.getJoints += topJoint
        self.DOUBLE_KNEE_MOD.getJoints += botJoint
        [adb.AutoSuffix(jnt) for jnt in [baseJoint, topJoint, botJoint]]
        [pm.matchTransform(jnt, self.base_leg_joints[1], pos=1, rot=1) for jnt in [baseJoint, topJoint, botJoint]]
        pm.parent(topJoint[0], baseJoint[0])
        pm.parent(botJoint[0], topJoint[0])
        adb.makeroot_func(baseJoint[0], 'offset', forceNameConvention = True)

        if self.side == 'L':
            pm.move(topJoint[0], 0, 0.6, 0, r=1, os=1, wd=1)
            pm.move(botJoint[0], 0, -1.2, 0, r=1, os=1, wd=1)
        else:
            pm.move(topJoint[0], 0, -0.6, 0, r=1, os=1, wd=1)
            pm.move(botJoint[0], 0, 1.2, 0, r=1, os=1, wd=1)

        _multDivid = pm.shadingNode('multiplyDivide', asUtility=1,  n='{}__DoubleKneeRotation__{}'.format(self.side, NC.MULTIPLY_DIVIDE_SUFFIX))
        _multDivid.input2X.set(0.5)
        _multDivid.input2Y.set(0.5)
        _multDivid.input2Z.set(0.5)

        self.base_leg_joints[1].rx >> _multDivid.input1X
        self.base_leg_joints[1].ry >> _multDivid.input1Y
        self.base_leg_joints[1].rz >> _multDivid.input1Z

        _multDivid.outputX >> baseJoint[0].rx
        _multDivid.outputY >> baseJoint[0].ry
        _multDivid.outputZ >> baseJoint[0].rz

        doubleKnee_CTL = doubleKnee_ctrl()[0]
        pm.matchTransform(doubleKnee_CTL, topJoint[0], pos=0, rot=1)
        adb.lockAttr_func(doubleKnee_CTL, attributes=['ry', 'rx', 'rz', 'sx', 'sz'])
        adb.matrixConstraint(str(doubleKnee_CTL), str(baseJoint[0]), channels='t', mo=True)
        adb.matrixConstraint(str(doubleKnee_CTL), str(topJoint[0]), channels='s', mo=True)
        adb.matrixConstraint(str(self.base_leg_joints[0]), str(doubleKnee_CTL.getParent()), channels='t', mo=True)

        # TODO: ADD SPACE SWITCH TO PIN THE KNEE

        pm.parent(baseJoint[0].getParent(), self.DOUBLE_KNEE_MOD.OUTPUT_GRP)
        self.DOUBLE_KNEE_MOD.getResetJoints = [baseJoint[0].getParent()]
        adb.matrixConstraint(str(self.base_leg_joints[0]), self.DOUBLE_KNEE_MOD.getResetJoints[0], channels='trs', mo=True)
        pm.parent(self.DOUBLE_KNEE_MOD.MOD_GRP, self.MODULES_GRP)
        pm.parent(self.pv_base_jnt, doubleKnee_CTL)

        if self.SLIDING_KNEE_MOD:
            [pm.PyNode(ctrl).v.set(0) for ctrl in self.SLIDING_KNEE_MOD.getControls]
            pm.matchTransform(self.SLIDING_KNEE_MOD.getControls[1], botJoint, pos=1, rot=0)
            pm.matchTransform(self.SLIDING_KNEE_MOD.getControls[2], topJoint, pos=1, rot=0)

            pm.parentConstraint(topJoint, self.SLIDING_KNEE_MOD.getControls[2], mo=1)
            pm.parentConstraint(botJoint, self.SLIDING_KNEE_MOD.getControls[1], mo=1)

        self.DOUBLE_KNEE_MOD.getControls = [doubleKnee_CTL]
        moduleBase.ModuleBase.setupVisRule([self.DOUBLE_KNEE_MOD.OUTPUT_GRP], self.DOUBLE_KNEE_MOD.VISRULE_GRP, '{Side}__{Basename}_DoubleKnee_JNT__{Suffix}'.format(**self.nameStructure), False)
        moduleBase.ModuleBase.setupVisRule([self.DOUBLE_KNEE_MOD.INPUT_GRP], self.DOUBLE_KNEE_MOD.VISRULE_GRP, '{Side}__{Basename}_DoubleKnee_CTRL__{Suffix}'.format(**self.nameStructure), False)
        self.DOUBLE_KNEE_MOD.RIG_GRP.v.set(0)


    def ribbon(self, volumePreservation=True):
        self.RIBBON_MOD = moduleBase.ModuleBase()
        self.RIBBON_MOD.hiearchy_setup('{Side}__Ribbon'.format(**self.nameStructure))
        self.BUILD_MODULES += [self.RIBBON_MOD]
        self.RIBBON_MOD.RIG_GRP.inheritsTransform.set(0)

        def createProxyPlaneUpperPart(name, interval=4):
            locs = locGen.locGenerator(interval, str(self.base_leg_joints[0]), str(self.base_leg_joints[1]))
            first_loc = Locator.Locator.point_base(pm.PyNode(self.base_leg_joints[0]).getRotatePivot(space='world')).locators[0]
            last_loc = Locator.Locator.point_base(pm.PyNode(self.base_leg_joints[1]).getRotatePivot(space='world')).locators[0]
            locs.insert(0, first_loc)
            locs.append(last_loc)
            upper_proxy_plane = adbProxy.plane_proxy(locs, name , 'x')
            pm.delete(locs)
            pm.polyNormal(upper_proxy_plane, ch=1, userNormalMode=0, normalMode=0)
            pm.select(None)

            return upper_proxy_plane

        def createProxyPlaneLowerPart(name, interval=4):
            locs = locGen.locGenerator(interval, str(self.base_leg_joints[1]), str(self.base_leg_joints[2]))
            first_loc = Locator.Locator.point_base(pm.PyNode(self.base_leg_joints[1]).getRotatePivot(space='world')).locators[0]
            last_loc = Locator.Locator.point_base(pm.PyNode(self.base_leg_joints[2]).getRotatePivot(space='world')).locators[0]
            locs.insert(0, first_loc)
            locs.append(last_loc)
            lower_proxy_plane = adbProxy.plane_proxy(locs, name, 'x')
            pm.delete(locs)
            pm.polyNormal(lower_proxy_plane, ch=1, userNormalMode=0, normalMode=0)
            pm.select(None)

            return lower_proxy_plane

        def addVolumePreservation():
            self.upper_leg_squash_stretch = adbRibbon.SquashStrech('{Side}__{Basename}Upper_VolumePreservation'.format(**self.nameStructure),
                                                            ExpCtrl=None,
                                                            ribbon_ctrl=self.base_leg_joints[:2],  # Top first, then bottom

                                                            jointList = leg_folli_upper_end.getResetJoints,
                                                            jointListA = (leg_folli_upper_end.getResetJoints[0:2], self.config["ATTRIBUTES"]['StretchyLegUpperExp'][0]),
                                                            jointListB = (leg_folli_upper_end.getResetJoints[2:-1], self.config["ATTRIBUTES"]['StretchyLegUpperExp'][1]),
                                                            jointListC = ([leg_folli_upper_end.getResetJoints[-1]], self.config["ATTRIBUTES"]['StretchyLegUpperExp'][2]),
                                                         )

            self.upper_leg_squash_stretch.start(metaDataNode='transform')
            self.RIBBON_MOD.metaDataGRPS += [self.upper_leg_squash_stretch.metaData_GRP]
            self.upper_leg_squash_stretch.build()

            self.lower_leg_squash_stretch = adbRibbon.SquashStrech('{Side}__{Basename}Lower_VolumePreservation'.format(**self.nameStructure),
                                                            ExpCtrl=None,
                                                            ribbon_ctrl=self.base_leg_joints[1:],  # Top first, then bottom

                                                            jointList = leg_folli_lower_end.getResetJoints,
                                                            jointListA = ([leg_folli_lower_end.getResetJoints[0]], self.config["ATTRIBUTES"]['StretchyLegLowerExp'][0]),
                                                            jointListB = (leg_folli_lower_end.getResetJoints[1:-1], self.config["ATTRIBUTES"]['StretchyLegLowerExp'][1]),
                                                            jointListC = ([leg_folli_lower_end.getResetJoints[-1]], self.config["ATTRIBUTES"]['StretchyLegLowerExp'][2]),
                                                         )

            self.lower_leg_squash_stretch.start(metaDataNode='transform')
            self.RIBBON_MOD.metaDataGRPS += [self.lower_leg_squash_stretch.metaData_GRP]
            self.lower_leg_squash_stretch.build()

            pm.parent(self.upper_leg_squash_stretch.MOD_GRP, upperPartGrp)
            pm.parent(self.lower_leg_squash_stretch.MOD_GRP, lowerPartGrp)

            ## Scaling Connection
            for grp in [self.upper_leg_squash_stretch.MOD_GRP, self.lower_leg_squash_stretch.MOD_GRP]:
                adb.unlockAttr_func(grp, ['sx', 'sy', 'sz'])
                pm.PyNode(self.RIBBON_MOD.MOD_GRP).sx >> grp.sx
                pm.PyNode(self.RIBBON_MOD.MOD_GRP).sy >> grp.sy
                pm.PyNode(self.RIBBON_MOD.MOD_GRP).sz >> grp.sz

            return self.upper_leg_squash_stretch.MOD_GRP, self.lower_leg_squash_stretch.MOD_GRP


        #===========================
        # BUILD
        #===========================

        upper_proxy_plane = createProxyPlaneUpperPart('{Side}__Upper{Basename}_Base1__MSH'.format(**self.nameStructure), interval=4)
        lower_proxy_plane = createProxyPlaneLowerPart('{Side}__Lower{Basename}_Base1__MSH'.format(**self.nameStructure), interval=4)

        _folliculeVis = 0
        folli_radius = self.config['JOINTS']["Follicule_JNT"]['radius']

        leg_folli_upper = adbFolli.Folli('{Side}__Upper{Basename}_Folli_Base1'.format(**self.nameStructure), 1, 5, radius=folli_radius, subject = upper_proxy_plane)
        leg_folli_upper.start(metaDataNode='transform')
        self.RIBBON_MOD.metaDataGRPS += [leg_folli_upper.metaData_GRP]
        leg_folli_upper.build()
        leg_folli_upper.addControls(shape=sl.circleX_shape, scale=1.5, color=('index', self.col_layer1))
        leg_folli_upper.getFollicules = _folliculeVis

        leg_folli_lower = adbFolli.Folli('{Side}__Lower{Basename}_Folli_Base1'.format(**self.nameStructure), 1, 5, radius=folli_radius, subject = lower_proxy_plane)
        leg_folli_lower.start(metaDataNode='transform')
        self.RIBBON_MOD.metaDataGRPS += [leg_folli_lower.metaData_GRP]
        leg_folli_lower.build()
        leg_folli_lower.addControls(shape=sl.circleX_shape, scale=1.5, color=('index', self.col_layer1))
        leg_folli_lower.getFollicules = _folliculeVis

        upper_proxy_plane_end = createProxyPlaneUpperPart('{Side}__Upper{Basename}_END__MSH'.format(**self.nameStructure), interval=20)
        lower_proxy_plane_end = createProxyPlaneLowerPart('{Side}__Lower{Basename}_END__MSH'.format(**self.nameStructure), interval=20)

        leg_folli_upper_end = adbFolli.Folli('{Side}__Upper{Basename}_Folli_END'.format(**self.nameStructure), 1, 5, radius=folli_radius, subject = upper_proxy_plane_end)
        leg_folli_upper_end.start(metaDataNode='transform')
        self.RIBBON_MOD.metaDataGRPS += [leg_folli_upper_end.metaData_GRP]
        leg_folli_upper_end.build()
        leg_folli_upper_end.getFollicules = _folliculeVis

        leg_folli_lower_end = adbFolli.Folli('{Side}__Lower{Basename}_Folli_END'.format(**self.nameStructure), 1, 5, radius=folli_radius, subject = lower_proxy_plane_end)
        leg_folli_lower_end.start(metaDataNode='transform')
        self.RIBBON_MOD.metaDataGRPS += [leg_folli_lower_end.metaData_GRP]
        leg_folli_lower_end.build()
        leg_folli_lower_end.getFollicules = _folliculeVis

        # ## Assign SkinCluster
        # pm.select(upper_proxy_plane, self.SLIDING_KNEE_MOD.getJoints[:4], r = True)
        # mc.SmoothBindSkin()
        # pm.select(lower_proxy_plane, self.SLIDING_KNEE_MOD.getJoints[4:], r = True)
        # mc.SmoothBindSkin()

        upperPartGrp = pm.group(n='{Side}__Upper{Basename}__GRP'.format(**self.nameStructure), parent=self.RIBBON_MOD.RIG_GRP, em=1)
        lowerPartGrp = pm.group(n='{Side}__Lower{Basename}__GRP'.format(**self.nameStructure), parent=self.RIBBON_MOD.RIG_GRP, em=1)

        pm.parent([leg_folli_upper.MOD_GRP,  leg_folli_upper_end.MOD_GRP, upper_proxy_plane, upper_proxy_plane_end], upperPartGrp)
        pm.parent([leg_folli_lower.MOD_GRP,  leg_folli_lower_end.MOD_GRP, lower_proxy_plane, lower_proxy_plane_end], lowerPartGrp)

        if volumePreservation:
            addVolumePreservationMod = addVolumePreservation()
            # pm.parent(addVolumePreservationMod.MOD_GRP, self.MODULES_GRP)

        self.RIBBON_MOD.setFinalHiearchy(
                        OUTPUT_GRP_LIST = leg_folli_upper_end.getJoints + leg_folli_lower_end.getJoints,
                        INPUT_GRP_LIST = leg_folli_upper.getInputs + leg_folli_lower.getInputs,
                        )

        pm.parent(self.RIBBON_MOD.MOD_GRP, self.MODULES_GRP)

        # Hide Unused controls
        leg_folli_lower.getResetControls[0].v.set(0)
        leg_folli_upper.getResetControls[-1].v.set(0)

        moduleBase.ModuleBase.setupVisRule([self.RIBBON_MOD.OUTPUT_GRP], self.RIBBON_MOD.VISRULE_GRP, '{Side}__{Basename}_Macro_JNT__{Suffix}'.format(**self.nameStructure), True)
        moduleBase.ModuleBase.setupVisRule([self.RIBBON_MOD.INPUT_GRP], self.RIBBON_MOD.VISRULE_GRP, '{Side}__{Basename}_Macro_CTRL__{Suffix}'.format(**self.nameStructure), False)
        self.RIBBON_MOD.RIG_GRP.v.set(0)

        for each in [leg_folli_upper_end, leg_folli_lower_end]:
             Joint.Joint(each.getJoints).radius = self.config['JOINTS']["Macro_JNT"]['radius']
             adb.changeColor_func(Joint.Joint(each.getJoints).joints, 'index', 20)



    # -------------------
    # CONNECT SLOVERS
    # -------------------

    def cleanUpEmptyGrps(self):
        for ModGrp in self.MODULES_GRP.getChildren():
            for grp in ModGrp.getChildren():
                if len(grp.getChildren()) is 0:
                    pm.delete(grp)


    def scalingUniform(self):
            all_groups = [self.MODULES_GRP, self.MAIN_RIG_GRP]
            all_groups += self.MODULES_GRP.getChildren()
            for grp in all_groups:
                adb.unlockAttr_func(grp, ['sx', 'sy', 'sz'])

            for module in self.MODULES_GRP.getChildren():
                self.MAIN_RIG_GRP.sx >> module.sx
                self.MAIN_RIG_GRP.sy >> module.sy
                self.MAIN_RIG_GRP.sz >> module.sz

            ## negate Module__GRP scaling
            md_scaling = pm.shadingNode('multiplyDivide', asUtility=1,  n='{}__Scaling__{}'.format(self.side, NC.MULTIPLY_DIVIDE_SUFFIX))
            md_scaling.input1X.set(1)
            md_scaling.input1Y.set(1)
            md_scaling.input1Z.set(1)
            md_scaling.operation.set(2)

            self.MAIN_RIG_GRP.sx >> md_scaling.input2X
            self.MAIN_RIG_GRP.sy >> md_scaling.input2Y
            self.MAIN_RIG_GRP.sz >> md_scaling.input2Z

            md_scaling.outputX >> self.MODULES_GRP.sx
            md_scaling.outputY >> self.MODULES_GRP.sy
            md_scaling.outputZ >> self.MODULES_GRP.sz


    def setup_VisibilityGRP(self):
        visGrp = adbAttr.NodeAttr([self.VISIBILITY_GRP])
        visGrp.AddSeparator(self.VISIBILITY_GRP, 'Joints')
        visGrp.addAttr('{Side}_{Basename}_IK_JNT'.format(**self.nameStructure), self.config['VISRULES']['IK_JNT'])
        visGrp.addAttr('{Side}_{Basename}_FK_JNT'.format(**self.nameStructure), self.config['VISRULES']['FK_JNT'])
        visGrp.addAttr('{Side}_{Basename}_Result_JNT'.format(**self.nameStructure), self.config['VISRULES']['Result_JNT'])
        visGrp.addAttr('{Side}_{Basename}_DoubleKnee_JNT'.format(**self.nameStructure), self.config['VISRULES']['DoubleKnee_JNT'])
        visGrp.addAttr('{Side}_{Basename}_Macro_JNT'.format(**self.nameStructure), self.config['VISRULES']['Macro_JNT'])
        visGrp.AddSeparator(self.VISIBILITY_GRP, 'Controls')
        visGrp.addAttr('{Side}_{Basename}_IK_CTRL'.format(**self.nameStructure), self.config['VISRULES']['IK_CTRL'])
        visGrp.addAttr('{Side}_{Basename}_IK_Offset_CTRL'.format(**self.nameStructure), self.config['VISRULES']['IK_Offset_CTRL'])
        visGrp.addAttr('{Side}_{Basename}_IK_PoleVector_CTRL'.format(**self.nameStructure), self.config['VISRULES']['IK_PoleVector_CTRL'])
        visGrp.addAttr('{Side}_{Basename}_FK_CTRL'.format(**self.nameStructure), self.config['VISRULES']['FK_CTRL'])
        visGrp.addAttr('{Side}_{Basename}_DoubleKnee_CTRL'.format(**self.nameStructure), self.config['VISRULES']['DoubleKnee_CTRL'])
        visGrp.addAttr('{Side}_{Basename}_Macro_CTRL'.format(**self.nameStructure), self.config['VISRULES']['Macro_CTRL'])

        for attr in visGrp.allAttrs.keys():
            for module in self.BUILD_MODULES:
                for grp in module.VISRULE_GRP.getChildren():
                    shortName = NC.getBasename(grp).split('{Basename}_'.format(**self.nameStructure))[-1]
                    # print shortName.lower(), '-------------',  attr.lower()
                    if shortName.lower() in attr.lower():
                        pm.connectAttr('{}.{}'.format(visGrp.subject, attr), '{}.vis'.format(grp))



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


    def setup_SpaceGRP(self, transform, Ik_FK_attributeName):
        space_ctrl = adbAttr.NodeAttr([transform])
        space_ctrl.addAttr(Ik_FK_attributeName, 'enum',  eName = "IK:FK:")
        adbAttr.NodeAttr.copyAttr(self.povSpaceSwitch.metaData_GRP, [self.SPACES_GRP], forceConnection=True)
        adbAttr.NodeAttr.copyAttr(self.ikLegSpaceSwitch.metaData_GRP, [self.SPACES_GRP], forceConnection=True)
        return Ik_FK_attributeName


    def setup_SettingGRP(self):
        setting_ctrl = adbAttr.NodeAttr([self.SETTINGS_GRP])
        adbAttr.NodeAttr.copyAttr(self.legIk_MOD.metaData_GRP, [self.SETTINGS_GRP],  nicename='{Side}_{Basename}Stretchy'.format(**self.nameStructure), forceConnection=True)
        setting_ctrl.AddSeparator([self.SETTINGS_GRP], 'VolumePreservation')

        adbAttr.NodeAttr.copyAttr(self.upper_leg_squash_stretch.metaData_GRP, [self.SETTINGS_GRP], nicename='{Side}_{Basename}Upper'.format(**self.nameStructure), forceConnection=True)
        adbAttr.NodeAttr.copyAttr(self.lower_leg_squash_stretch.metaData_GRP, [self.SETTINGS_GRP], nicename='{Side}_{Basename}Lower'.format(**self.nameStructure), forceConnection=True)



# =========================
# BUILD
# =========================

# L_leg = LimbLeg(module_name='L__Leg')
# L_leg.start(buildFootStatus = True)
# L_leg.build()
# L_leg.connect()


# R_leg = LimbLeg(module_name='R__Leg')
# R_leg.build(['R__hip_guide', 'R__knee_guide', 'R__ankle_guide'])
# R_leg.connect()




# ====================================================
# EXPORT STARTER
# L_leg.legGuides.exportData()
# L_leg.FootRig.footGuides.exportData()

