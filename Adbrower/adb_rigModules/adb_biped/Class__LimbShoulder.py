# ------------------------------------------------------
# Auto Rig Shoulder SetUp
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import json
import sys
import os
import adb_core.NameConv_utils as NC
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

import adb_library.adb_utils.Script__PoseReader as PoseReader
import adb_library.adb_modules.Class__SpaceSwitch as SpaceSwitch

import adb_rigModules.RigBase as rigBase
import adb_rigModules.ModuleGuides as moduleGuides

# reload(adbrower)
# reload(sl)
# reload(Joint)
# reload(adbAttr)
reload(NC)
# reload(Control)
# reload(Locator)
# reload(SpaceSwitch)
reload(PoseReader)
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

AUTO_CLAVICULE_CONFIG = {
    # color : key : position : value
    'red' : {
            0 : (0.0 , 0.5),
            1 : (0.5 , 0.5),
            2 : (1.0 , 0.5),
            },

    'green' : {
            0 : (0.0 , 0.3),
            1 : (0.5 , 0.5),
            2 : (0.75 , 0.8),
            3 : (1.0 , 0.82),
            },

    'blue' : { # UP / DOWN
            0 : (0 , 0.45),
            1 : (0.5 , 0.5),
            2 : (0.75 , 0.75),
            3 : (1.0 , 0.8),
                        }
                    }


class LimbShoudlerModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(LimbShoudlerModel, self).__init__()
        pass

DATA_WEIGHT_PATH = 'C:/Users/Audrey/Documents/maya/projects/Roller_Rigging_Project/data/skinWeights/'
CONFIG_PATH = 'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_rigModules/adb_biped'

os.chdir(CONFIG_PATH)
with open("BipedConfig.json", "r") as f:
    BIPED_CONFIG = json.load(f)

class LimbShoudler(rigBase.RigBase):
    """
    """
    def __init__(self,
                 module_name=None,
                 config = BIPED_CONFIG
                ):
        super(LimbShoudler, self).__init__(module_name, _metaDataNode=None)

        self.nameStructure = None
        self._MODEL = LimbShoudlerModel()
        self.NAME = module_name
        self.config = config


    def __repr__(self):
        return str('{} : {} \n {}'.format(self.__class__.__name__, self.MAIN_RIG_GRP, self.__class__))

    # =========================
    # METHOD
    # =========================

    def start(self):
        Gclavicule, Gshoulder = [moduleGuides.ModuleGuides.createFkGuide(prefix='{}_{}'.format(self.NAME, part)) for part in ['Clavicule', 'Shoulder']]
        for guide in [Gclavicule, Gshoulder]:
            pm.parent(guide.guides, self.STARTERS_GRP)

        pm.PyNode(Gclavicule.guides[0]).translate.set(0, 0, 0)
        pm.PyNode(Gshoulder.guides[0]).translate.set(2, 0, 0)

        self.curve_setup(Gclavicule.guides[0], Gshoulder.guides[0])

        self.shoulderGuides = moduleGuides.ModuleGuides(self.NAME.upper(), [Gclavicule.guides[0], Gshoulder.guides[0]], self.DATA_PATH)
        readPath = self.shoulderGuides.DATA_PATH + '/' + self.shoulderGuides.RIG_NAME + '__GLOC.ini'
        if os.path.exists(readPath):
            self.loadData = self.shoulderGuides.loadData(readPath)
            for guide in self.shoulderGuides.guides:
                _registeredAttributes = ast.literal_eval(self.loadData.get(str(guide), 'registeredAttributes'))
                for attribute in _registeredAttributes:
                    try:
                        pm.setAttr('{}.{}'.format(guide, attribute), ast.literal_eval(self.loadData.get(str(guide), str(attribute))))
                    except :
                        pass

        pm.select(None)

    def build(self, GUIDES=None):
        """
        """
        super(LimbShoudler, self)._build()

        if GUIDES is None:
            GUIDES = self.shoulderGuides.guides

        self.starter_Shoulder = GUIDES
        self.side = NC.getSideFromPosition(GUIDES[-1])

        if self.side == 'L':
            self.col_main = indexColor[self.config["COLORS"]['L_col_main']]
            self.col_layer1 = indexColor[self.config["COLORS"]['L_col_layer1']]
        elif self.side == 'R':
            self.col_main = indexColor[self.config["COLORS"]['R_col_main']]
            self.col_layer1 = indexColor[self.config["COLORS"]['R_col_layer1']]
        else:
            self.col_main = indexColor[self.config["COLORS"]['C_col_main']]
            self.col_layer1 = indexColor[self.config["COLORS"]['C_col_layer1']]
            self.sliding_elbow_col = indexColor[self.config["COLORS"]['C_col_layer2']]
            self.pol_vector_col = indexColor[self.config["COLORS"]['C_col_layer2']]

        self.nameStructure = {
                            'Side'    : self.side,
                            'Basename': 'Shoulder',
                            'Parts'   : ['Clavicule', 'Shoulder' ,'Scapula'],
                            'Suffix'  : ''
                            }

        self.BUILD_MODULES = []

        self.shoulder_MOD = None
        self.AUTO_CLAVICULE_MOD = None


        # =================
        # BUILD

        self.shoulder_MOD = moduleBase.ModuleBase()
        self.BUILD_MODULES += [self.shoulder_MOD]
        self.shoulder_MOD._start('{Side}__Shoulder'.format(**self.nameStructure) ,_metaDataNode = 'transform')
        pm.parent(self.shoulder_MOD.metaData_GRP, self.SETTINGS_GRP)
        pm.parent(self.shoulder_MOD.MOD_GRP, self.MODULES_GRP)

        self.createJoints()
        self.create_clavicule_ctrl()
        self.ikSetup()
        self.autoClavicule(
                      arm_ik_joints = ['{Side}__Arm_Ik_Shoulder__JNT'.format(**self.nameStructure), '{Side}__Arm_Ik_Elbow__JNT'.format(**self.nameStructure), '{Side}__Arm_Ik_Wrist__JNT'.format(**self.nameStructure)],
                      poleVector_ctl = '{Side}__Arm_PoleVector__CTRL'.format(**self.nameStructure),
                      arm_ik_offset_ctrl = '{Side}__Arm_IK_offset__CTRL'.format(**self.nameStructure),
                      )

    def connect(self,
                 arm_result_joint = [],
                 arm_ik_joint = [],
                 arm_fk_joint_parent = [],
                 arm_spaceGrp = [],
                ):

        super(LimbShoudler, self)._connect()

        self.connectShoulderToArm(arm_result_joint = arm_result_joint,
                                arm_ik_joint = arm_ik_joint,
                                arm_fk_joint_parent = arm_fk_joint_parent,
                                arm_spaceGrp = arm_spaceGrp,
                                )


        self.setup_VisibilityGRP()
        self.setup_SettingGRP()
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

        Transform(self.MODULES_GRP).pivotPoint = Transform(self.starter_Shoulder[0]).worldTrans

    # =========================
    # SOLVERS
    # =========================

    # -------------------
    # BUILD SLOVERS
    # -------------------

    @changeColor('index', 2)
    def createJoints(self):
        points = [pm.PyNode(guide).getRotatePivot(space='world') for guide in self.starter_Shoulder]
        self.shoulder_chain = Joint.Joint.point_base(*points, name='{Side}__{Basename}'.format(**self.nameStructure), chain=True, padding=2)
        self.clavicule_joint, self.shoulder_joint, = self.shoulder_chain.joints

        pm.PyNode(self.clavicule_joint).rename('{Side}__{Basename}_{Parts[0]}_END'.format(**self.nameStructure))
        pm.PyNode(self.shoulder_joint).rename('{Side}__{Basename}_{Parts[1]}_END'.format(**self.nameStructure))
        adb.AutoSuffix(self.shoulder_chain.joints)

        ## orient joint
        if self.side == NC.RIGTH_SIDE_PREFIX:
            mirror_chain_1 = pm.mirrorJoint(self.clavicule_joint, mirrorYZ=1)
            Joint.Joint(mirror_chain_1).orientAxis = '-Y'

            mirror_chain_3 = pm.mirrorJoint(mirror_chain_1[0], mirrorBehavior=1, mirrorYZ=1)
            pm.delete(mirror_chain_1,  self.clavicule_joint)
            self.shoulder_chain =  Joint.Joint(mirror_chain_3)
            self.clavicule_joint, self.shoulder_joint, = self.shoulder_chain.joints

            pm.PyNode(self.clavicule_joint).rename('{Side}__{Basename}_{Parts[0]}_END'.format(**self.nameStructure))
            pm.PyNode(self.shoulder_joint).rename('{Side}__{Basename}_{Parts[1]}_END'.format(**self.nameStructure))
            adb.AutoSuffix(self.shoulder_chain.joints)
        else:
            self.shoulder_chain.orientAxis = '-Y'

        pm.parent(self.clavicule_joint, self.shoulder_MOD.OUTPUT_GRP)
        self.shoulderOffsetGrp = adb.makeroot_func(self.clavicule_joint, suff='Offset', forceNameConvention=True)

        self.shoulder_chain.radius = self.config['JOINTS']["Result_JNT"]['radius']
        self.nameStructure['Suffix'] = NC.VISRULE
        moduleBase.ModuleBase.setupVisRule([self.clavicule_joint], self.shoulder_MOD.VISRULE_GRP, '{Side}__{Basename}_Clavicule_JNT__{Suffix}'.format(**self.nameStructure), True)

        return self.shoulder_chain.joints


    def create_clavicule_ctrl(self):
        @changeColor('index', col = self.col_main)
        @lockAttr(['tx', 'ty', 'tz', 'ry' ,'sx', 'sy', 'sz'])
        def create_ctrl():
            self.nameStructure['Suffix'] = NC.CTRL
            self.clavicule_ctrl_class = Control.Control(name='{Side}__{Basename}_{Parts[0]}__{Suffix}'.format(**self.nameStructure),
                                                shape = sl.sl[self.config['CONTROLS']['Clavicule']['shape']],
                                                scale=self.config['CONTROLS']['Clavicule']['scale'],
                                                matchTransforms = (self.clavicule_joint, 1, 1),
                                                parent=self.shoulder_MOD.INPUT_GRP
                                                )
            self.clavicule_ctrl = self.clavicule_ctrl_class.control
            if self.side == NC.RIGTH_SIDE_PREFIX:
                self.clavicule_ctrl.sy.set(-1)
            adb.makeroot_func(self.clavicule_ctrl, suff='Offset', forceNameConvention=True)
            self.clavicule_ctrl.rz.set(self.config['CONTROLS']['Clavicule']['rotation_degree'])
            pm.makeIdentity(self.clavicule_ctrl, n=0, r=1, apply=True, pn=1)
            self.clavicule_ctrl_class.addRotationOrderAttr()
            return self.clavicule_ctrl
        create_ctrl()

        moduleBase.ModuleBase.setupVisRule([self.clavicule_ctrl], self.shoulder_MOD.VISRULE_GRP)


    def ikSetup(self):
        @changeColor('index', col = self.col_layer1)
        @lockAttr(['sx', 'sy', 'sz'])
        def create_ik_ctrl():
            self.nameStructure['Suffix'] = NC.CTRL
            self.shoulder_ik_ctrl_class = Control.Control(name='{Side}__{Basename}_{Parts[1]}__{Suffix}'.format(**self.nameStructure),
                                                shape=sl.sl[self.config['CONTROLS']['Shoulder']['shape']],
                                                scale=self.config['CONTROLS']['Shoulder']['scale'],
                                                matchTransforms = (self.shoulder_joint, 1, 0),
                                                parent=self.shoulder_MOD.INPUT_GRP
                                                )

            self.shoulder_ik_ctrl = self.shoulder_ik_ctrl_class.control
            adb.makeroot_func(self.shoulder_ik_ctrl, suff='Offset', forceNameConvention=True)
            return self.shoulder_ik_ctrl
        create_ik_ctrl()

        self.nameStructure['Suffix'] = NC.IKHANDLE_SUFFIX
        shoulder_IkHandle, shoulder_IkHandle_effector = pm.ikHandle(n='{Side}__{Basename}__{Suffix}'.format(**self.nameStructure), sj=self.clavicule_joint, ee=self.shoulder_joint)
        shoulder_IkHandle.v.set(0)
        pm.parent(shoulder_IkHandle, self.shoulder_ik_ctrl)

        pm.parentConstraint(self.clavicule_ctrl, self.shoulder_ik_ctrl.getParent(), mo=1)
        adb.breakConnection(self.shoulder_ik_ctrl.getParent(), ['rx', 'ry', 'rz'])


    def autoClavicule(self,
                      arm_ik_joints = [],
                      poleVector_ctl = [],
                      arm_ik_offset_ctrl = [],
                        ):


        self.AUTO_CLAVICULE_MOD = moduleBase.ModuleBase()
        self.AUTO_CLAVICULE_MOD._start('{Side}__AutoClavicule'.format(**self.nameStructure) ,_metaDataNode = 'transform')
        self.BUILD_MODULES += [self.AUTO_CLAVICULE_MOD]
        pm.parent(self.AUTO_CLAVICULE_MOD.metaData_GRP, self.SETTINGS_GRP)
        pm.parent(self.AUTO_CLAVICULE_MOD.MOD_GRP, self.MODULES_GRP)

        autoClaviculeGrp = adbAttr.NodeAttr([self.AUTO_CLAVICULE_MOD.metaData_GRP])
        autoClaviculeGrp.addAttr('Toggle', True)
        autoClaviculeGrp.addAttr('RemapNode', 'message')

        def ik_chain_duplicate():
            self.ik_AutoShoulder_joint = [pm.duplicate(joint, parentOnly=True)[0] for joint in arm_ik_joints]
            pm.parent(self.ik_AutoShoulder_joint[-1], self.ik_AutoShoulder_joint[-2])
            pm.parent(self.ik_AutoShoulder_joint[-2], self.ik_AutoShoulder_joint[0])

            pm.PyNode(self.ik_AutoShoulder_joint[0]).rename('{Side}__Auto{Basename}_Ik_Shoulder'.format(**self.nameStructure))
            pm.PyNode(self.ik_AutoShoulder_joint[1]).rename('{Side}__Auto{Basename}_Ik_Elbow'.format(**self.nameStructure))
            pm.PyNode(self.ik_AutoShoulder_joint[2]).rename('{Side}__Auto{Basename}_Ik_Wrist'.format(**self.nameStructure))
            adb.AutoSuffix(self.ik_AutoShoulder_joint)

            self.nameStructure['Suffix'] = NC.IKHANDLE_SUFFIX
            autoShoulder_IkHandle, autoShoulder_IkHandle_effector = pm.ikHandle(n='{Side}__Auto{Basename}__{Suffix}'.format(**self.nameStructure), sj=self.ik_AutoShoulder_joint[0], ee=self.ik_AutoShoulder_joint[-1])
            autoShoulder_IkHandle.v.set(0)
            self.autoShoulder_IkHandle = autoShoulder_IkHandle
            adb.makeroot_func(self.autoShoulder_IkHandle)
            pm.poleVectorConstraint(poleVector_ctl, autoShoulder_IkHandle, weight=1)


            self.AUTO_CLAVICULE_MOD.setFinalHiearchy(RIG_GRP_LIST = [self.autoShoulder_IkHandle.getParent()],
                                OUTPUT_GRP_LIST = [self.ik_AutoShoulder_joint[0]]
                                )

            adb.matrixConstraint(arm_ik_offset_ctrl, self.autoShoulder_IkHandle.getParent())
            pm.parent(self.AUTO_CLAVICULE_MOD.MOD_GRP, self.MODULES_GRP)
            self.nameStructure['Suffix'] = NC.VISRULE
            moduleBase.ModuleBase.setupVisRule([self.ik_AutoShoulder_joint[0]], self.AUTO_CLAVICULE_MOD.VISRULE_GRP, name='{Side}__{Basename}_IK_JNT__{Suffix}'.format(**self.nameStructure), defaultValue=False)


        def claviculeSetup():
            autoShoulder_grp = adb.makeroot_func(self.clavicule_ctrl, suff='AutoClavicule', forceNameConvention=True)
            self.nameStructure['Suffix'] = NC.MULTIPLY_DIVIDE_SUFFIX
            autoShoulder_toggle  = pm.shadingNode('multiplyDivide', au=True, n='{Side}__Auto{Basename}_toggle__{Suffix}'.format(**self.nameStructure))
            self.nameStructure['Suffix'] = NC.REMAP_COLOR_SUFFIX
            autoShoulder_remapNode  = pm.shadingNode('remapColor', au=True, n='{Side}__Auto{Basename}__{Suffix}'.format(**self.nameStructure))
            autoShoulder_remapNode.outColorR >> self.AUTO_CLAVICULE_MOD.metaData_GRP.RemapNode

            if self.side == 'L':
                autoShoulder_remapNode.inputMin.set(-90)
                autoShoulder_remapNode.inputMax.set(90)
                autoShoulder_remapNode.outputMin.set(-45)
                autoShoulder_remapNode.outputMax.set(45)
            elif self.side == 'R':
                autoShoulder_remapNode.inputMin.set(90)
                autoShoulder_remapNode.inputMax.set(-90)
                autoShoulder_remapNode.outputMin.set(-45)
                autoShoulder_remapNode.outputMax.set(45)

            for color in AUTO_CLAVICULE_CONFIG.keys():
                for points in AUTO_CLAVICULE_CONFIG[color].keys():
                    pm.PyNode('{}.{}[{}].{}_Interp'.format(autoShoulder_remapNode, color, str(points), color)).set(3)
                    pm.PyNode('{}.{}[{}].{}_Position'.format(autoShoulder_remapNode, color,  str(points), color)).set(AUTO_CLAVICULE_CONFIG[color][points][0])
                    pm.PyNode('{}.{}[{}].{}_FloatValue'.format(autoShoulder_remapNode, color, str(points), color)).set(AUTO_CLAVICULE_CONFIG[color][points][1])

            ## Connection
            claviculePoseReader = PoseReader.poseReader(name='{Side}__Clavicule'.format(**self.nameStructure),
                                  driver=self.AUTO_CLAVICULE_MOD.OUTPUT_GRP,
                                  target=self.ik_AutoShoulder_joint[0],
                                  upPostion=(0,10,0),
                                  targetPosition=(10,0,0),
                                  )

            # add choice node for switching between Fk and IK arm
            targetPoseReaderGrp = claviculePoseReader['targetGrp']
            decomposeMatrixNode =  pm.listConnections('{}.rx'.format(targetPoseReaderGrp), plugs=False, destination=False)[0]

            self.shoulderChoice = pm.createNode('choice', n='{Side}__Auto{Basename}Choice__CH'.format(**self.nameStructure))
            decomposeMatrixNode.outputRotate >> self.shoulderChoice.input[0]
            decomposeMatrixNode.outputRotateX // targetPoseReaderGrp.rotateX
            decomposeMatrixNode.outputRotateY // targetPoseReaderGrp.rotateY
            decomposeMatrixNode.outputRotateZ // targetPoseReaderGrp.rotateZ
            pm.PyNode('{Side}__Arm_Fk_Shoulder__CTRL'.format(**self.nameStructure)).rotate >> self.shoulderChoice.input[1]

            if self.side == NC.LEFT_SIDE_PREFIX:
               self.shoulderChoice.output >> targetPoseReaderGrp.rotate
            else:
                shoulderTemp = pm.group(n='{}__ShoulderTemp__GRP'.format(NC.RIGTH_SIDE_PREFIX), em=1)
                self.shoulderChoice.output >> shoulderTemp.rotate
                mult = pm.createNode('multiplyDivide', n='{}__inverseShoulder__{}'.format(NC.RIGTH_SIDE_PREFIX, NC.MULTIPLY_DIVIDE_SUFFIX))
                mult.input2X.set(-1)
                mult.input2Y.set(-1)
                mult.input2Z.set(-1)
                shoulderTemp.rotate >> mult.input1
                mult.output >> targetPoseReaderGrp.rotate

            # connect Clavicule to the shoulder
            claviculePoseReader['mainPoseReaderOutput'][0].rx >> autoShoulder_toggle.input1X
            claviculePoseReader['mainPoseReaderOutput'][0].ry >> autoShoulder_toggle.input1Y
            claviculePoseReader['mainPoseReaderOutput'][0].rz >> autoShoulder_toggle.input1Z

            autoShoulder_toggle.outputX >> autoShoulder_remapNode.colorR
            autoShoulder_toggle.outputY >> autoShoulder_remapNode.colorG
            autoShoulder_toggle.outputZ >> autoShoulder_remapNode.colorB

            autoShoulder_remapNode.outColorR >> autoShoulder_grp.rx
            autoShoulder_remapNode.outColorG >> autoShoulder_grp.ry
            autoShoulder_remapNode.outColorB >> autoShoulder_grp.rz

            self.AUTO_CLAVICULE_MOD.metaData_GRP.Toggle >> autoShoulder_toggle.input2X
            self.AUTO_CLAVICULE_MOD.metaData_GRP.Toggle >> autoShoulder_toggle.input2Y
            self.AUTO_CLAVICULE_MOD.metaData_GRP.Toggle >> autoShoulder_toggle.input2Z


        # ============================
        # BUILD
        # ============================
        ik_chain_duplicate()
        claviculeSetup()

    # -------------------
    # CONNECT SLOVERS
    # -------------------

    def connectShoulderToArm(self,
                 arm_result_joint = None,
                 arm_ik_joint = None,
                 arm_fk_joint_parent = None,
                 arm_spaceGrp = None,
                 ):

        pm.pointConstraint(self.shoulder_joint, arm_ik_joint, mo=True)
        pm.pointConstraint(self.shoulder_joint, arm_fk_joint_parent, mo=True)
        pm.pointConstraint(self.shoulder_joint, arm_result_joint, mo=True)
        # connect Arm Space to the choice node
        self.nameStructure['Node'] = arm_spaceGrp
        pm.connectAttr('{Node}.{Side}_Arm_IK_FK'.format(**self.nameStructure), '{}.selector'.format(self.shoulderChoice))


    def setup_VisibilityGRP(self):
        visGrp = adbAttr.NodeAttr([self.VISIBILITY_GRP])
        visGrp.AddSeparator(self.VISIBILITY_GRP, 'Joints')
        visGrp.addAttr('{Side}_{Basename}_Clavicule_JNT'.format(**self.nameStructure), True)
        visGrp.addAttr('{Side}_{Basename}_IK_JNT'.format(**self.nameStructure), False)

        visGrp.AddSeparator(self.VISIBILITY_GRP, 'Controls')
        visGrp.addAttr('{Side}_{Basename}_Clavicule_CTRL'.format(**self.nameStructure), True)

        for attr in visGrp.allAttrs.keys():
            for module in self.BUILD_MODULES:
                for grp in module.VISRULE_GRP.getChildren():
                    shortName = NC.getBasename(grp).split('{Basename}_'.format(**self.nameStructure))[-1]
                    if shortName.lower() in attr.lower():
                        try:
                            pm.connectAttr('{}.{}'.format(visGrp.subject, attr), '{}.vis'.format(grp))
                        except:
                            pass


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


    def setup_SpaceGRP(self, transform, Ik_FK_attributeName=[]):
        switch_ctrl = adbAttr.NodeAttr([transform])
        for name in Ik_FK_attributeName:
            switch_ctrl.addAttr(name, 'enum',  eName = "IK:FK:")

        return Ik_FK_attributeName


    def setup_SettingGRP(self):
        setting_ctrl = adbAttr.NodeAttr([self.SETTINGS_GRP])
        adbAttr.NodeAttr.copyAttr(self.AUTO_CLAVICULE_MOD.metaData_GRP, [self.SETTINGS_GRP],  nicename='{Side}_AutoClavicule'.format(**self.nameStructure), forceConnection=True)


# =========================
# BUILD
# =========================

# L_Shoulder = LimbShoudler(module_name='L__Shoulder')
# L_Shoulder.start()
# L_Shoulder.build()
# L_Shoulder.connect()


