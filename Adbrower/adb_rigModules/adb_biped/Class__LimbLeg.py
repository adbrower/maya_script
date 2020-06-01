# ------------------------------------------------------
# Auto Rig Leg SetUp
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import sys

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
import adb_core.Class__Skinning as Skinning

import adb_rigModules.RigBase as RigBase
import adb_rigModules.adb_biped.Class__LimbFoot as LimbFoot

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
reload(LimbFoot)
reload(Skinning)

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

#TODO : Add rotationOrder attribute

class LimbLegModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(LimbLegModel, self).__init__()
        pass


DATA_WEIGHT_PATH = 'C:/Users/Audrey/Documents/maya/projects/Roller_Rigging_Project/data/skinWeights/'


class LimbLeg(moduleBase.ModuleBase):
    """
    """
    def __init__(self,
                module_name=None,
                ):
        super(LimbLeg, self).__init__('')

        self.nameStructure = None
        self._MODEL = LimbLegModel()
        self.NAME = module_name

    def __repr__(self):
        return str('{} : {} \n {}'.format(self.__class__.__name__, self.subject, self.__class__))


    # =========================
    # METHOD
    # =========================

    def start(self, metaDataNode = 'transform'):
        super(LimbLeg, self)._start('', _metaDataNode = metaDataNode)

        # TODO: Create Guide Setup

    def build(self, GUIDES):
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

        self.RIG = RigBase.RigBase(rigName = self.NAME)

        self.starter_Leg = GUIDES

        self.side = NC.getSideFromPosition(GUIDES[0])

        if self.side == 'R':
            self.col_main = indexColor['fluoRed']
            self.col_layer1 = indexColor['darkRed']
            self.pol_vector_col = (0.5, 0.000, 0.000)
            self.sliding_knee_col = indexColor['darkRed']
        else:
            self.col_main = indexColor['fluoBlue']
            self.col_layer1 = indexColor['blue']
            self.sliding_knee_col = indexColor['blue']
            self.pol_vector_col = (0, 0.145, 0.588)

        self.nameStructure = {
                            'Side'    : self.side,
                            'Basename': 'Leg',
                            'Parts'   : ['Hips', 'Knee', 'Ankle'],
                            'Suffix'  : ''
                            }

        self.BUILD_MODULES = []

        self.ikFk_MOD = None
        self.SLIDING_ELBOW_MOD = None
        self.DOUBLE_ELBOW_MOD = None
        self.RIBBON_MOD = None

        # =================
        # BUILD

        self.createResultLegJoints()
        self.ik_fk_system()
        self.stretchyLimb()
        self.slidingKnee()
        self.doubleKnee()
        self.ribbon(volumePreservation=True)

    def connect(self, buildFoot=(False, ['L__ankle_guide', 'L__ball_guide', 'L__toe_guide', 'L__heel_guide'])):
        super(LimbLeg, self)._connect()

        self.setup_VisibilityGRP()
        self.scalingUniform()
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
        
        buildFootStatus, buildFootStarter = buildFoot
        if buildFootStatus:
            L_foot = LimbFoot.LimbFoot(module_name='{Side}__Foot'.format(**self.nameStructure))
            L_foot.build(buildFootStarter)

            L_foot.connect(leg_ikHandle = self.leg_IkHandle,
                           leg_offset_ik_ctrl = self.leg_IkHandle_ctrl_offset,
                           leg_ankle_fk_ctrl = self.fkControls[-1],
                            )
            pm.PyNode('{}.{}'.format(self.RIG.SPACES_GRP, self.Ik_FK_attributeName)) >> pm.PyNode('{}.{}'.format(L_foot.RIG.SPACES_GRP, L_foot.all_IKFK_attributes[1]))


        self.loadSkinClustersWeights()
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

            mirror_chain_3 = pm.mirrorJoint(mirror_chain_1[0] ,mirrorBehavior=1, mirrorYZ=1)
            pm.delete(mirror_chain_1,mirror_chain_1,self.base_leg_joints)
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
            ## Setter le radius de mes joints ##
            for joint in self.ik_leg_joints:
                joint.radius.set(self.base_leg_joints[0].radius.get() + 0.4)

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
            ## Setter le radius de mes joints ##
            for joint in self.fk_leg_joints:
                joint.radius.set(self.base_leg_joints[0].radius.get() + 0.2)

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
        def CreateFkcontrols(radius = 3,
                    normalsCtrl=(0,1,0)):
            """Creates the FK controls on the Fk joint chain """
            FkShapeSetup = adbFKShape.FkShape(self.fk_leg_joints)
            FkShapeSetup.shapeSetup(radius, normalsCtrl)

            shapes = [ctl.getShape() for ctl in FkShapeSetup.controls]
            self.nameStructure['Suffix'] = NC.VISRULE
            visRuleGrp, attribute = moduleBase.ModuleBase.setupVisRule(shapes, self.ikFk_MOD.VISRULE_GRP, name='{Side}__{Basename}_Fk_CTRL__{Suffix}'.format(**self.nameStructure))
            return FkShapeSetup.controls


        def CreateIKcontrols(Ikshape = sl.cube_shape, exposant=1, pvShape = sl.ball_shape):
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
                                                 shape = Ikshape,
                                                 scale=0.8,
                                                 matchTransforms = (self.ik_leg_joints[-1], 1,0)
                                                 ).control
                moduleBase.ModuleBase.setupVisRule([_leg_IkHandle_ctrl], self.ikFk_MOD.VISRULE_GRP)
                return _leg_IkHandle_ctrl
            self.leg_IkHandle_ctrl = Ik_ctrl()[0]

            @makeroot('')
            @changeColor('index', col = self.col_main)
            def Ik_ctrl_offset():
                _leg_IkHandle_ctrl_offset = Control.Control(name='{Side}__{Basename}_IK_offset__{Suffix}'.format(**self.nameStructure),
                                 shape = Ikshape,
                                 scale = 0.6,
                                 parent = self.leg_IkHandle_ctrl,
                                 matchTransforms = (self.ik_leg_joints[-1], 1, 0)
                                 ).control
                moduleBase.ModuleBase.setupVisRule([_leg_IkHandle_ctrl_offset], self.ikFk_MOD.VISRULE_GRP)
                return _leg_IkHandle_ctrl_offset
            self.leg_IkHandle_ctrl_offset = Ik_ctrl_offset()[0]


            @lockAttr(att_to_lock = ['rx','ry','rz','sx','sy','sz'])
            @changeColor('rgb', col = self.pol_vector_col)
            @makeroot()
            def pole_vector_ctrl(name ='{Side}__{Basename}_PoleVector____{Suffix}'.format(**self.nameStructure)):
                pv_guide = adb.PvGuide(leg_IkHandle[0],self.ik_leg_joints[-2], exposant=exposant*distance)
                self.poleVectorCtrl = pvShape()

                pm.rename(self.poleVectorCtrl,name)
                last_point = pm.PyNode(pv_guide).getCVs()
                pm.move(self.poleVectorCtrl,last_point[-1])
                pm.poleVectorConstraint(self.poleVectorCtrl,leg_IkHandle[0] ,weight=1)

                def curve_setup():
                    pm.select(self.poleVectorCtrl, r=True)
                    pv_tip_jnt = adb.jointAtCenter()[0]
                    pm.rename(pv_tip_jnt, '{}__pvTip__{}'.format(self.side, NC.JOINT))
                    pm.parent(pv_tip_jnt, self.poleVectorCtrl)

                    _loc = pm.spaceLocator(p= adb.getWorldTrans([self.ik_leg_joints[-2]]))
                    mc.CenterPivot()
                    pm.select(_loc, r=True)
                    pv_base_jnt = adb.jointAtCenter()[0]
                    pm.delete(_loc)
                    pm.rename(pv_base_jnt, '{}__pvBase__{}'.format(self.side, NC.JOINT))
                    pm.skinCluster(pv_base_jnt , pv_guide, pv_tip_jnt)
                    pm.parent(pv_base_jnt, self.ik_leg_joints[1])
                    pm.setAttr(pv_guide.inheritsTransform, 0)
                    pm.setAttr(pv_guide.overrideDisplayType, 1)
                    [pm.setAttr('{}.drawStyle'.format(joint),  2) for joint in [pv_tip_jnt, pv_base_jnt]]
                    pm.parent(pv_guide, self.ikFk_MOD.RIG_GRP)
                    return pv_guide

                pv_guide = curve_setup()

                pm.parent(self.poleVectorCtrl, self.ikFk_MOD.INPUT_GRP)
                self.nameStructure['Suffix'] = NC.VISRULE
                moduleBase.ModuleBase.setupVisRule([self.poleVectorCtrl, pv_guide], self.ikFk_MOD.VISRULE_GRP, '{Side}__{Basename}_PoleVector_CTRL__{Suffix}'.format(**self.nameStructure), False)
                return self.poleVectorCtrl

            pole_vector_ctrl()

            ikSpaceSwitchWorldGrp = pm.group(n='{Side}__{Basename}_IK_SPACES_SWITCH_WORLD__GRP'.format(**self.nameStructure), em=1, parent=self.RIG.WORLD_LOC)
            ikSpaceSwitchWorldGrp.v.set(0)
            pm.matchTransform(ikSpaceSwitchWorldGrp, self.leg_IkHandle_ctrl_offset, pos=1, rot=1)
            self.povSpaceSwitch = SpaceSwitch.SpaceSwitch('{Side}__PoleVector'.format(**self.nameStructure),
                                                    spacesInputs =[self.leg_IkHandle_ctrl_offset, ikSpaceSwitchWorldGrp],
                                                    spaceOutput = self.poleVectorCtrl.getParent(),
                                                    maintainOffset = True,
                                                    attrNames = ['ankle', 'world'],)
            self.ikFk_MOD.metaDataGRPS += [self.povSpaceSwitch.metaData_GRP]

            pm.parent(leg_IkHandle[0], self.leg_IkHandle_ctrl_offset)
            pm.parent(self.leg_IkHandle_ctrl.getParent(), self.ikFk_MOD.INPUT_GRP)


        def makeConnections():
            self.Ik_FK_attributeName = self.setup_SpaceGRP(self.RIG.SPACES_GRP, Ik_FK_attributeName ='{Side}_{Basename}'.format(**self.nameStructure))

            self.blendSystem(ctrl_name = self.RIG.SPACES_GRP,
                            blend_attribute = self.Ik_FK_attributeName,
                            result_joints = self.base_leg_joints,
                            ik_joints = self.ik_leg_joints,
                            fk_joints = self.fk_leg_joints,
                            lenght_blend = 1,
                            )

            pm.parent(self.base_leg_joints[0], self.ikFk_MOD.OUTPUT_GRP)

        IkJointChain()
        FkJointChain()
        self.fkControls = CreateFkcontrols()
        CreateIKcontrols()
        makeConnections()

        visRuleGrp = moduleBase.ModuleBase.setupVisRule(self.base_leg_joints, self.ikFk_MOD.VISRULE_GRP, '{Side}__{Basename}_Result_JNT__{Suffix}'.format(**self.nameStructure), False)[0]

        pm.parent(self.ikFk_MOD.MOD_GRP, self.RIG.MODULES_GRP)
        Joint.Joint(self.base_leg_joints).radius = 6
        Joint.Joint(self.fk_leg_joints).radius = Joint.Joint(self.base_leg_joints).radius - 3
        Joint.Joint(self.ik_leg_joints).radius = Joint.Joint(self.base_leg_joints).radius - 4 


    def stretchyLimb(self):
        legIk_MOD = adbIkStretch.stretchyIK('{Side}__StretchylegIk'.format(**self.nameStructure),
                    ik_joints=self.ik_leg_joints,
                    ik_ctrl=self.leg_IkHandle_ctrl_offset,
                    stretchAxis='Y'
                    )
        legIk_MOD.start(metaDataNode='transform')
        legIk_MOD.metaDataGRPS += [legIk_MOD.metaData_GRP]
        self.BUILD_MODULES += [legIk_MOD]
        legIk_MOD.build()

        pm.parent((self.leg_IkHandle_ctrl_offset).getParent(), self.leg_IkHandle_ctrl)
        pm.parent(legIk_MOD.MOD_GRP, self.RIG.MODULES_GRP)


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
                hipSlidingKnee_CTL = Control.Control(name='{Side}__{Basename}_hip_slidingKnee'.format(**self.nameStructure),
                                shape=sl.locator_shape,
                                scale=1,
                                parent=self.SLIDING_KNEE_MOD.INPUT_GRP,
                                matchTransforms=(self.base_leg_joints[0], 1,0)
                                ).control
                return hipSlidingKnee_CTL

            @makeroot()
            def kneeSlidingKnee01_ctrl():
                kneeSlidingKnee01_CTL = Control.Control(name='{Side}__{Basename}_knee_slidingKnee_01'.format(**self.nameStructure),
                                shape=sl.locator_shape,
                                scale=1,
                                parent=self.SLIDING_KNEE_MOD.INPUT_GRP,
                                matchTransforms=(self.base_leg_joints[1], 1,0)
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
                kneeSlidingKnee02_CTL = Control.Control(name='{Side}__{Basename}_knee_slidingKnee'.format(**self.nameStructure),
                                shape=sl.locator_shape,
                                scale=1,
                                parent=self.SLIDING_KNEE_MOD.INPUT_GRP,
                                matchTransforms=(self.base_leg_joints[1], 1,0)
                                ).control
                return kneeSlidingKnee02_CTL

            @makeroot()
            def ankleSlidingKnee_ctrl():
                ankleSlidingKnee_CTL = Control.Control(name='{Side}__{Basename}_ankle_slidingKnee_01'.format(**self.nameStructure),
                                shape=sl.locator_shape,
                                scale=1,
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
        kneeSlidingKnee01_CTL.v.set(0)
        pm.parent(self.SLIDING_KNEE_MOD.getJoints, self.SLIDING_KNEE_MOD.OUTPUT_GRP)

        pm.parent(self.SLIDING_KNEE_MOD.MOD_GRP, self.RIG.MODULES_GRP)

        self.SLIDING_KNEE_MOD.getControls.append(kneeSlidingKnee01_CTL)
        self.SLIDING_KNEE_MOD.getResetControls.append(kneeSlidingKnee01_CTL.getParent())

        ## CONNECT
        ##--------------
        for jnt, ctl in zip(self.base_leg_joints, [hipSlidingKnee_CTL, kneeSlidingKnee01_CTL, ankleSlidingKnee_CTL]):
            pm.parentConstraint(jnt, ctl.getParent(), mo=True)

        moduleBase.ModuleBase.setupVisRule([self.SLIDING_KNEE_MOD.OUTPUT_GRP, self.SLIDING_KNEE_MOD.RIG_GRP], self.SLIDING_KNEE_MOD.VISRULE_GRP, '{Side}__{Basename}_SlidingKnee_JNT__{Suffix}'.format(**self.nameStructure), False)


    def doubleKnee(self):
        self.DOUBLE_KNEE_MOD = moduleBase.ModuleBase()
        self.DOUBLE_KNEE_MOD.hiearchy_setup('{Side}__DoubleKnee'.format(**self.nameStructure))
        self.BUILD_MODULES += [self.DOUBLE_KNEE_MOD]

        @makeroot()
        def doubleKnee_ctrl():
            doubleKnee_ctrl = Control.Control(name='{Side}__{Basename}_DoubleKnee'.format(**self.nameStructure),
                            shape=sl.locator_shape,
                            scale=1,
                            parent=self.DOUBLE_KNEE_MOD.INPUT_GRP,
                            matchTransforms=(baseJoint, 1,0),
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
        pm.move(topJoint[0], 0, 0.6, 0, r=1, os=1, wd=1)
        pm.move(botJoint[0], 0, -1.2, 0, r=1, os=1, wd=1)

        _multDivid = pm.shadingNode('multiplyDivide', asUtility=1,  n='{}__DoubleKneeRotation__{}'.format(self.side, NC.MULTIPLY_DIVIDE_SUFFIX))
        _multDivid.input2X.set(0.5)
        _multDivid.input2Y.set(0.5)
        _multDivid.input2Z.set(0.5)

        self.base_leg_joints[1].rx >>  _multDivid.input1X
        self.base_leg_joints[1].ry >>  _multDivid.input1Y
        self.base_leg_joints[1].rz >>  _multDivid.input1Z

        _multDivid.outputX >> baseJoint[0].rx
        _multDivid.outputY >> baseJoint[0].ry
        _multDivid.outputZ >> baseJoint[0].rz

        doubleKnee_CTL = doubleKnee_ctrl()[0]
        adb.lockAttr_func(doubleKnee_CTL, attributes=['ry', 'rx', 'rz', 'sx', 'sy', 'sz'])
        adb.matrixConstraint(str(doubleKnee_CTL), str(baseJoint[0]), channels='ts', mo=True)
        adb.matrixConstraint(str(self.base_leg_joints[0]), str(doubleKnee_CTL.getParent()), channels='trs', mo=True)

        pm.parent(baseJoint[0].getParent(), self.DOUBLE_KNEE_MOD.OUTPUT_GRP)
        self.DOUBLE_KNEE_MOD.getResetJoints = [baseJoint[0].getParent()]
        adb.matrixConstraint(str(self.base_leg_joints[0]), self.DOUBLE_KNEE_MOD.getResetJoints[0], channels='trs', mo=True)
        pm.parent(self.DOUBLE_KNEE_MOD.MOD_GRP, self.RIG.MODULES_GRP)

        if self.SLIDING_KNEE_MOD:
            pm.matchTransform(self.SLIDING_KNEE_MOD.getControls[1], topJoint, pos=1, rot=0)
            pm.matchTransform(self.SLIDING_KNEE_MOD.getControls[2], botJoint, pos=1, rot=0)

            pm.parentConstraint(topJoint, self.SLIDING_KNEE_MOD.getControls[1], mo=1)
            pm.parentConstraint(botJoint, self.SLIDING_KNEE_MOD.getControls[2], mo=1)

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
            upper_leg_squash_stretch = adbRibbon.SquashStrech('Upper_VolumePreservation',
                                                            ExpCtrl=None,
                                                            ribbon_ctrl=self.base_leg_joints[:2],  # Top first, then bottom

                                                            jointList = leg_folli_upper_end.getResetJoints,
                                                            jointListA = ([leg_folli_upper_end.getResetJoints[0]], 0),
                                                            jointListB = (leg_folli_upper_end.getResetJoints[1:-1],  1.5),
                                                            jointListC = ([leg_folli_upper_end.getResetJoints[-1]], 0),
                                                         )

            upper_leg_squash_stretch.start(metaDataNode='transform')
            self.RIBBON_MOD.metaDataGRPS += [upper_leg_squash_stretch.metaData_GRP]
            upper_leg_squash_stretch.build()

            lower_leg_squash_stretch = adbRibbon.SquashStrech('Lower_VolumePreservation',
                                                            ExpCtrl=None,
                                                            ribbon_ctrl=self.base_leg_joints[1:],  # Top first, then bottom

                                                            jointList = leg_folli_lower_end.getResetJoints,
                                                            jointListA = ([leg_folli_lower_end.getResetJoints[0]], 1),
                                                            jointListB = (leg_folli_lower_end.getResetJoints[1:-1],  1.5),
                                                            jointListC = ([leg_folli_lower_end.getResetJoints[-1]], 0),
                                                         )

            lower_leg_squash_stretch.start(metaDataNode='transform')
            self.RIBBON_MOD.metaDataGRPS += [lower_leg_squash_stretch.metaData_GRP]
            lower_leg_squash_stretch.build()

            pm.parent(upper_leg_squash_stretch.MOD_GRP, upperPartGrp)
            pm.parent(lower_leg_squash_stretch.MOD_GRP, lowerPartGrp)

            ## Scaling Connection
            for grp in [upper_leg_squash_stretch.MOD_GRP, lower_leg_squash_stretch.MOD_GRP]:
                adb.unlockAttr_func(grp, ['sx', 'sy', 'sz'])
                pm.PyNode(self.RIBBON_MOD.MOD_GRP).sx >> grp.sx
                pm.PyNode(self.RIBBON_MOD.MOD_GRP).sy >> grp.sy
                pm.PyNode(self.RIBBON_MOD.MOD_GRP).sz >> grp.sz

            return upper_leg_squash_stretch.MOD_GRP, lower_leg_squash_stretch.MOD_GRP


        #===========================
        # BUILD
        #===========================

        upper_proxy_plane = createProxyPlaneUpperPart('{Side}__Upper{Basename}_Base1__MSH'.format(**self.nameStructure), interval=4)
        lower_proxy_plane = createProxyPlaneLowerPart('{Side}__Lower{Basename}_Base1__MSH'.format(**self.nameStructure), interval=4)

        _folliculeVis = 0

        leg_folli_upper = adbFolli.Folli('{Side}__Upper{Basename}_Folli_Base1'.format(**self.nameStructure), 1, 5, radius = 0.5, subject = upper_proxy_plane)
        leg_folli_upper.start(metaDataNode='transform')
        self.RIBBON_MOD.metaDataGRPS += [leg_folli_upper.metaData_GRP]
        leg_folli_upper.build()
        leg_folli_upper.addControls(shape=sl.circleX_shape, scale=1.5, color=('index', self.col_layer1))
        leg_folli_upper.getFollicules = _folliculeVis

        leg_folli_lower = adbFolli.Folli('{Side}__Lower{Basename}_Folli_Base1'.format(**self.nameStructure), 1, 5, radius = 0.5, subject = lower_proxy_plane)
        leg_folli_lower.start(metaDataNode='transform')
        self.RIBBON_MOD.metaDataGRPS += [leg_folli_lower.metaData_GRP]
        leg_folli_lower.build()
        leg_folli_lower.addControls(shape=sl.circleX_shape, scale=1.5, color=('index', self.col_layer1))
        leg_folli_lower.getFollicules = _folliculeVis

        upper_proxy_plane_end = createProxyPlaneUpperPart('{Side}__Upper{Basename}_END__MSH'.format(**self.nameStructure), interval=20)
        lower_proxy_plane_end = createProxyPlaneLowerPart('{Side}__Lower{Basename}_END__MSH'.format(**self.nameStructure), interval=20)

        leg_folli_upper_end = adbFolli.Folli('{Side}__Upper{Basename}_Folli_END'.format(**self.nameStructure), 1, 5, radius = 0.5, subject = upper_proxy_plane_end)
        leg_folli_upper_end.start(metaDataNode='transform')
        self.RIBBON_MOD.metaDataGRPS += [leg_folli_upper_end.metaData_GRP]
        leg_folli_upper_end.build()
        leg_folli_upper_end.getFollicules = _folliculeVis

        leg_folli_lower_end = adbFolli.Folli('{Side}__Lower{Basename}_Folli_END'.format(**self.nameStructure), 1, 5, radius = 0.5, subject = lower_proxy_plane_end)
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
            addVolumePreservation()
        self.RIBBON_MOD.setFinalHiearchy(
                        OUTPUT_GRP_LIST = leg_folli_upper_end.getJoints + leg_folli_lower_end.getJoints,
                        INPUT_GRP_LIST = leg_folli_upper.getInputs + leg_folli_lower.getInputs,
                        )

        pm.parent(self.RIBBON_MOD.MOD_GRP, self.RIG.MODULES_GRP)

        # Hide Unused controls
        leg_folli_lower.getResetControls[0].v.set(0)
        leg_folli_upper.getResetControls[-1].v.set(0)

        moduleBase.ModuleBase.setupVisRule([self.RIBBON_MOD.OUTPUT_GRP], self.RIBBON_MOD.VISRULE_GRP, '{Side}__{Basename}_Ribbon_JNT__{Suffix}'.format(**self.nameStructure), True)
        moduleBase.ModuleBase.setupVisRule([self.RIBBON_MOD.INPUT_GRP], self.RIBBON_MOD.VISRULE_GRP, '{Side}__{Basename}_Ribbon_CTRL__{Suffix}'.format(**self.nameStructure), False)
        self.RIBBON_MOD.RIG_GRP.v.set(0)

        for each in [leg_folli_upper_end, leg_folli_lower_end]:
             Joint.Joint(each.getJoints).radius = 2
             adb.changeColor_func(Joint.Joint(each.getJoints).joints, 'index', 20)



    # -------------------
    # CONNECT SLOVERS
    # -------------------

    def cleanUpEmptyGrps(self):
        for ModGrp in self.RIG.MODULES_GRP.getChildren():
            for grp in ModGrp.getChildren():
                if len(grp.getChildren()) is 0:
                    pm.delete(grp)


    def scalingUniform(self):
            all_groups = [self.RIG.MODULES_GRP, self.RIG.MAIN_RIG_GRP]
            all_groups += self.RIG.MODULES_GRP.getChildren()
            for grp in all_groups:
                adb.unlockAttr_func(grp, ['sx', 'sy', 'sz'])

            for module in self.RIG.MODULES_GRP.getChildren():
                self.RIG.MAIN_RIG_GRP.sx >> module.sx
                self.RIG.MAIN_RIG_GRP.sy >> module.sy
                self.RIG.MAIN_RIG_GRP.sz >> module.sz

            ## negate Module__GRP scaling
            md_scaling = pm.shadingNode('multiplyDivide', asUtility=1,  n='{}__Scaling__{}'.format(self.side, NC.MULTIPLY_DIVIDE_SUFFIX))
            md_scaling.input1X.set(1)
            md_scaling.input1Y.set(1)
            md_scaling.input1Z.set(1)
            md_scaling.operation.set(2)

            self.RIG.MAIN_RIG_GRP.sx >> md_scaling.input2X
            self.RIG.MAIN_RIG_GRP.sy >> md_scaling.input2Y
            self.RIG.MAIN_RIG_GRP.sz >> md_scaling.input2Z

            md_scaling.outputX >> self.RIG.MODULES_GRP.sx
            md_scaling.outputY >> self.RIG.MODULES_GRP.sy
            md_scaling.outputZ >> self.RIG.MODULES_GRP.sz


    def setup_VisibilityGRP(self):
        visGrp = adbAttr.NodeAttr([self.RIG.VISIBILITY_GRP])
        visGrp.AddSeparator(self.RIG.VISIBILITY_GRP, 'Joints')
        visGrp.addAttr('IK_JNT', False)
        visGrp.addAttr('FK_JNT', False)
        visGrp.addAttr('Result_JNT', False)
        visGrp.addAttr('DoubleKnee_JNT', True)
        visGrp.addAttr('Ribbon_JNT', True)
        visGrp.AddSeparator(self.RIG.VISIBILITY_GRP, 'Controls')
        visGrp.addAttr('IK_CTRL', True)
        visGrp.addAttr('IK_Offset_CTRL', True)
        visGrp.addAttr('IK_PoleVector_CTRL', True)
        visGrp.addAttr('FK_CTRL', True)
        visGrp.addAttr('DoubleKnee_CTRL', True)
        visGrp.addAttr('Ribbon_CTRL', False)

        for attr in visGrp.allAttrs.keys():
            for module in self.BUILD_MODULES:
                for grp in module.VISRULE_GRP.getChildren():
                    shortName = NC.getBasename(grp).split('{Basename}_'.format(**self.nameStructure))[-1]
                    # print shortName.lower(), '-------------',  attr.lower()
                    if shortName.lower() in attr.lower():
                        pm.connectAttr('{}.{}'.format(visGrp.subject, attr), '{}.vis'.format(grp))


    def loadSkinClustersWeights(self):
        os.chdir(DATA_WEIGHT_PATH)
        for _file in os.listdir(DATA_WEIGHT_PATH):
            try:
                Skinning.Skinning.importWeights(DATA_WEIGHT_PATH, _file)
            except:
                pass


    # =========================
    # SLOTS
    # =========================


    def blendSystem(self,
                    ctrl_name = '',
                    blend_attribute = '',
                    result_joints = [],
                    ik_joints = [],
                    fk_joints = [],
                    lenght_blend = 1,
                    ):
            """
            # CBB: Add Blend Options for Rotate And Translate
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
            for oFK, oBlendColor in zip (fk_joints,BlendColorColl_Rotate):
                pm.PyNode(oFK).rx >> pm.PyNode(oBlendColor).color1R
                pm.PyNode(oFK).ry >> pm.PyNode(oBlendColor).color1G
                pm.PyNode(oFK).rz >> pm.PyNode(oBlendColor).color1B

            ## Connect the FK in the Color 1
            for oIK, oBlendColor in zip (ik_joints,BlendColorColl_Rotate):
                pm.PyNode(oIK).rx >> pm.PyNode(oBlendColor).color2R
                pm.PyNode(oIK).ry >> pm.PyNode(oBlendColor).color2G
                pm.PyNode(oIK).rz >> pm.PyNode(oBlendColor).color2B

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

            ## SCALE
            BlendColorColl_Scale = [pm.shadingNode('blendColors', asUtility=1, n='{}__{}_scale__{}'.format(self.side, NC.getBasename(x), NC.BLENDCOLOR_SUFFIX)) for x in result_joints]
            ## Connect the IK in the Color 2
            for oFK, oBlendColor in zip (fk_joints, BlendColorColl_Scale):
                pm.PyNode(oFK).sx >> pm.PyNode(oBlendColor).color1R
                pm.PyNode(oFK).sy >> pm.PyNode(oBlendColor).color1G
                pm.PyNode(oFK).sz >> pm.PyNode(oBlendColor).color1B

            ## Connect the FK in the Color 1
            for oIK, oBlendColor in zip (ik_joints, BlendColorColl_Scale):
                pm.PyNode(oIK).sx >> pm.PyNode(oBlendColor).color2R
                pm.PyNode(oIK).sy >> pm.PyNode(oBlendColor).color2G
                pm.PyNode(oIK).sz >> pm.PyNode(oBlendColor).color2B

            ## Connect the BlendColor node in the Blend joint chain
            for oBlendColor, oBlendJoint in zip (BlendColorColl_Scale, result_joints):
                pm.PyNode(oBlendColor).outputR  >> pm.PyNode(oBlendJoint).sx
                pm.PyNode(oBlendColor).outputG  >> pm.PyNode(oBlendJoint).sy
                pm.PyNode(oBlendColor).outputB  >> pm.PyNode(oBlendJoint).sz

            for oBlendColor in BlendColorColl_Scale:
                pm.PyNode(oBlendColor).blender.set(1)
            ## Connect the Remap Values to Blend Colors
            for oRemapValue,oBlendColor in zip (RemapValueColl, BlendColorColl_Scale):
                pm.PyNode(oRemapValue).outValue >> pm.PyNode(oBlendColor).blender

            ## Calculate Scale
            MDColl_Scale = [pm.shadingNode('multiplyDivide', asUtility=1, n='{}__{}_scale__{}'.format(self.side, NC.getBasename(x), NC.BLENDCOLOR_SUFFIX)) for x in result_joints]
            pm.PyNode(fk_joints[1]).sx >> pm.PyNode(MDColl_Scale[0]).input2X
            pm.PyNode(fk_joints[1]).sy >> pm.PyNode(MDColl_Scale[0]).input2Y
            pm.PyNode(fk_joints[1]).sz >> pm.PyNode(MDColl_Scale[0]).input2Z

            pm.PyNode(MDColl_Scale[0]).outputX >> pm.PyNode(BlendColorColl_Scale[1]).color1R
            pm.PyNode(MDColl_Scale[0]).outputY >> pm.PyNode(BlendColorColl_Scale[1]).color1G
            pm.PyNode(MDColl_Scale[0]).outputZ >> pm.PyNode(BlendColorColl_Scale[1]).color1B

            # ---
            pm.PyNode(fk_joints[0]).sx >> pm.PyNode(MDColl_Scale[0]).input1X
            pm.PyNode(fk_joints[0]).sy >> pm.PyNode(MDColl_Scale[0]).input1Y
            pm.PyNode(fk_joints[0]).sz >> pm.PyNode(MDColl_Scale[0]).input1Z

            pm.PyNode(fk_joints[1]).sx >> pm.PyNode(MDColl_Scale[1]).input1X
            pm.PyNode(fk_joints[1]).sy >> pm.PyNode(MDColl_Scale[1]).input1Y
            pm.PyNode(fk_joints[1]).sz >> pm.PyNode(MDColl_Scale[1]).input1Z

            pm.PyNode(fk_joints[2]).sx >> pm.PyNode(MDColl_Scale[1]).input2X
            pm.PyNode(fk_joints[2]).sy >> pm.PyNode(MDColl_Scale[1]).input2Y
            pm.PyNode(fk_joints[2]).sz >> pm.PyNode(MDColl_Scale[1]).input2Z

            pm.PyNode(MDColl_Scale[1]).outputX >> pm.PyNode(MDColl_Scale[0]).input2X
            pm.PyNode(MDColl_Scale[1]).outputY >> pm.PyNode(MDColl_Scale[0]).input2Y
            pm.PyNode(MDColl_Scale[1]).outputZ >> pm.PyNode(MDColl_Scale[0]).input2Z

            pm.PyNode(MDColl_Scale[0]).outputX >> pm.PyNode(BlendColorColl_Scale[2]).color1R
            pm.PyNode(MDColl_Scale[0]).outputY >> pm.PyNode(BlendColorColl_Scale[2]).color1G
            pm.PyNode(MDColl_Scale[0]).outputZ >> pm.PyNode(BlendColorColl_Scale[2]).color1B

           ## TRANSLATE
            BlendColorColl_Translate = [pm.shadingNode('blendColors', asUtility=1,
            n='{}__{}_translate__{}'.format(self.side, NC.getBasename(x), NC.BLENDCOLOR_SUFFIX))
            for x in result_joints]

            # Connect the IK in the Color 2
            all_adbmath_node = []
            for oFK, oBlendColor in zip (fk_joints, BlendColorColl_Translate):
                adbmath_node = pm.shadingNode('adbMath', asUtility=1, n='{}__{}_translate__MATH'.format(self.side, NC.getBasename(oFK)))
                all_adbmath_node.append(adbmath_node)
                pm.PyNode(adbmath_node).operation.set(2)

                pm.PyNode(oFK.getParent()).tx >> pm.PyNode(adbmath_node).input1[0]
                pm.PyNode(oFK.getParent()).ty >> pm.PyNode(adbmath_node).input1[1]
                pm.PyNode(oFK.getParent()).tz >> pm.PyNode(adbmath_node).input1[2]

                pm.PyNode(oFK).tx >> pm.PyNode(adbmath_node).input2[0]
                pm.PyNode(oFK).ty >> pm.PyNode(adbmath_node).input2[1]
                pm.PyNode(oFK).tz >> pm.PyNode(adbmath_node).input2[2]

                pm.PyNode(adbmath_node).output[0] >> pm.PyNode(oBlendColor).color1R
                pm.PyNode(adbmath_node).output[1] >> pm.PyNode(oBlendColor).color1G
                pm.PyNode(adbmath_node).output[2] >> pm.PyNode(oBlendColor).color1B

            multuplyDivide_node = pm.shadingNode('multiplyDivide', asUtility=1,  n='{}__reverse__{}'.format(self.side, NC.MULTIPLY_DIVIDE_SUFFIX))
            multuplyDivide_node.operation.set(1)
            multuplyDivide_node.input2X.set(1)
            multuplyDivide_node.input2Y.set(-1)
            multuplyDivide_node.input2Z.set(-1)

            fk_joints[0].tx >> multuplyDivide_node.input1X
            fk_joints[0].ty >> multuplyDivide_node.input1Y
            fk_joints[0].tz >> multuplyDivide_node.input1Z

            multuplyDivide_node.outputX >> all_adbmath_node[0].input2[0]
            multuplyDivide_node.outputY >> all_adbmath_node[0].input2[1]
            multuplyDivide_node.outputZ >> all_adbmath_node[0].input2[2]

            ## Connect the FK in the Color 1
            for oIK, oBlendColor in zip (ik_joints, BlendColorColl_Translate):
                pm.PyNode(oIK).tx >> pm.PyNode(oBlendColor).color2R
                pm.PyNode(oIK).ty >> pm.PyNode(oBlendColor).color2G
                pm.PyNode(oIK).tz >> pm.PyNode(oBlendColor).color2B

            ## Connect the BlendColor node in the Blend joint chain
            for oBlendColor, oBlendJoint in zip (BlendColorColl_Translate, result_joints):
                pm.PyNode(oBlendColor).outputR  >> pm.PyNode(oBlendJoint).tx
                pm.PyNode(oBlendColor).outputG  >> pm.PyNode(oBlendJoint).ty
                pm.PyNode(oBlendColor).outputB  >> pm.PyNode(oBlendJoint).tz

            for oBlendColor in BlendColorColl_Translate:
                pm.PyNode(oBlendColor).blender.set(1)

            ## Connect the Remap Values to Blend Colors
            for oRemapValue,oBlendColor in zip (RemapValueColl, BlendColorColl_Translate):
                pm.PyNode(oRemapValue).outValue >> pm.PyNode(oBlendColor).blender

            #=================================================================================================
            ## Connect the IK -FK Control to Remap Value
            blend_switch =  '{}.{}'.format(ctrl_name, blend_attribute)

            for each in RemapValueColl:
                pm.PyNode(blend_switch) >> pm.PyNode(each).inputValue
                pm.PyNode('{}.{}'.format(ctrl_name, switch_ctrl.attrName)) >> pm.PyNode(each).inputMax


    def setup_SpaceGRP(self, transform, Ik_FK_attributeName):
        switch_ctrl = adbAttr.NodeAttr([transform])
        switch_ctrl.addAttr(Ik_FK_attributeName, 'enum',  eName = "IK:FK:")
        adbAttr.NodeAttr.copyAttr(self.povSpaceSwitch.metaData_GRP, [self.RIG.SPACES_GRP], forceConnection=True)
        return Ik_FK_attributeName


# =========================
# BUILD
# =========================

L_leg = LimbLeg(module_name='L__Leg')
L_leg.build(['L__hip_guide', 'L__knee_guide', 'L__ankle_guide'])
L_leg.connect(buildFoot=(True, ['L__ankle_guide', 'L__ball_guide', 'L__toe_guide', 'L__heel_guide']))


# R_leg = LimbLeg(module_name='R__Leg')
# R_leg.build(['R__hip_guide', 'R__knee_guide', 'R__ankle_guide'])
# R_leg.connect()


