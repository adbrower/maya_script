# ------------------------------------------------------
# Auto Rig Spine SetUp
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
import adb_core.Class__Skinning as Skinning
from adb_core.Class__Transforms import Transform

import adb_library.adb_utils.Script__LocGenerator as locGen
import adb_library.adb_utils.Script__ProxyPlane as adbProxy
import adb_library.adb_modules.Module__Folli as adbFolli
import adb_library.adb_modules.Module__SquashStretch_Ribbon as adbRibbon
import adb_library.adb_modules.Module__Slide as Slide
import adb_library.adb_modules.Class__SpaceSwitch as SpaceSwitch
import adb_library.adb_modules.Module__AttachOnCurve as pointOnCurve

import adb_rigModules.RigBase as rigBase
import adb_rigModules.ModuleGuides as moduleGuides

# reload(adbrower)
# reload(sl)
# reload(Joint)
# reload(adbAttr)
# reload(NC)
# reload(Control)
# reload(locGen)
# reload(Locator)
# reload(adbFolli)
# reload(adbRibbon)
# reload(SpaceSwitch)
# reload(pointOnCurve)
# reload(Slide)
# reload(Skinning)
# reload(adbProxy)
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

FkVARIABLE_CONFIG = {
    # color : key : position : value
    'remap' : {
            0 : (0.0 , 0.0),
            1 : (0.5 , 1.0),
            2 : (1.0 , 0.0),
            },
                    }


DATA_WEIGHT_PATH = 'C:/Users/Audrey/Documents/maya/projects/Roller_Rigging_Project/data/skinWeights/'
CONFIG_PATH = 'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_rigModules/adb_biped'

os.chdir(CONFIG_PATH)
with open("BipedConfig.json", "r") as f:
    BIPED_CONFIG = json.load(f)


class LimbSpineModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(LimbSpineModel, self).__init__()
        pass


class LimbSpine(rigBase.RigBase):
    """
    """
    def __init__(self,
                 module_name=None,
                 config = BIPED_CONFIG
                ):
        super(LimbSpine, self).__init__(module_name, _metaDataNode=None)

        self.nameStructure = None
        self._MODEL = LimbSpineModel()
        self.NAME = module_name
        self.config = config


    def __repr__(self):
        return str('{} : {} \n {}'.format(self.__class__.__name__, self.MAIN_RIG_GRP, self.__class__))

    # =========================
    # METHOD
    # =========================

    @undo
    def start(self, jointNumber=7):
        def spineGuideCurve():
            _ctrl = pm.curve(p=[[0.0000, 13.9516, 0.4714], [0.0000, 14.0435, 0.4840], [0.0000, 14.4707, 0.5526], [0.0000, 15.7496, 0.7265], [0.0000, 17.1387, 0.6106], [0.0000, 18.1458, 0.7250], [0.0000, 18.6555, 0.8777]],
                            k=[0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 4.0, 4.0],
                            d=3,
                            n="spineGuide__CRV",
                            )
            return _ctrl
        spineGuideCurve = spineGuideCurve()
        spineGuideCurve = pm.rebuildCurve(spineGuideCurve, rt=0, ch=0, end=1, d=3, kr=0, s=4)

        ## FreezeCvs
        mc.DeleteHistory(spineGuideCurve)
        cluster = pm.cluster(spineGuideCurve)
        pm.delete(cluster)

        pointOnCurveJoint = pointOnCurve.PointToCurveJnt('{}_PointOnCurve'.format(self.NAME), jointNumber, spineGuideCurve)
        pointOnCurveJoint.start()
        pointOnCurveJoint.build()

        pm.parent(pointOnCurveJoint.MOD_GRP, self.STARTERS_GRP)
        [pm.delete(grp) for grp in [pointOnCurveJoint.VISRULE_GRP, pointOnCurveJoint.OUTPUT_GRP]]

        Gspine = [moduleGuides.ModuleGuides.createFkGuide(prefix='{}_{}'.format(self.NAME, joint+1)).guides[0] for joint in xrange(jointNumber)]
        for guide in Gspine:
            pm.parent(guide, self.STARTERS_GRP)

        for guide, joint in zip(Gspine, pointOnCurveJoint.getJoints):
            pm.matchTransform(guide, joint, pos=1, rot=0)

        self.spineGuides = moduleGuides.ModuleGuides(self.NAME.upper(), Gspine, self.DATA_PATH)
        readPath = self.spineGuides.DATA_PATH + '/' + self.spineGuides.RIG_NAME + '__GLOC.ini'
        if os.path.exists(readPath):
            self.loadData = self.spineGuides.loadData(readPath)
            for guide in self.spineGuides.guides:
                _registeredAttributes = ast.literal_eval(self.loadData.get(str(guide), 'registeredAttributes'))
                for attribute in _registeredAttributes:
                    try:
                        pm.setAttr('{}.{}'.format(guide, attribute), ast.literal_eval(self.loadData.get(str(guide), str(attribute))))
                    except NoSectionError:
                        pass

        pm.select(None)

    def build(self, GUIDES=None):
        """
        """
        super(LimbSpine, self)._build()

        if GUIDES is None:
            GUIDES = self.spineGuides.guides

        self.starter_Spine = GUIDES
        self.side = 'C'

        self.col_main = indexColor[self.config["COLORS"]['C_col_main']]
        self.col_layer1 = indexColor[self.config["COLORS"]['C_col_layer1']]
        self.col_layer2 = indexColor[self.config["COLORS"]['C_col_layer2']]

        self.nameStructure = {
                            'Side'    : self.side,
                            'Basename': 'Spine',
                            'Parts'   : ['Hips', 'Belly', 'Chest'],
                            'Suffix'  : ''
                            }

        self.BUILD_MODULES = []
        self.RESULT_MOD = None
        self.REVERSE_MOD = None
        self.FKVARIABLE_MOD = None

        # =================
        # BUILD

        self.createResultSystem()
        self.FKVARIABLE_MOD = self.createVariableFkSystem()

        self.createReverseSystem(self.spine_chain_joints)
        self.createFkRegularCTRLS()

        self.createIkSystem()
        self.createHipsMainCTRL()
        self.createChestMainCTRL()

    def connect(self):
        super(LimbSpine, self)._connect()

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

        Transform(self.MODULES_GRP).pivotPoint = Transform(self.spine_chain_joints[0]).worldTrans
        # self.loadSkinClustersWeights()


    # =========================
    # SOLVERS
    # =========================

    # -------------------
    # BUILD SLOVERS
    # -------------------

    def createResultSystem(self):

        @changeColor('index', col = (22))
        def createResultJoints():
            self.RESULT_MOD = moduleBase.ModuleBase()
            self.RESULT_MOD.hiearchy_setup('{Side}__Result'.format(**self.nameStructure))
            self.BUILD_MODULES += [self.RESULT_MOD]
            pm.parent(self.RESULT_MOD.MOD_GRP, self.MODULES_GRP)

            points = [pm.PyNode(guide).getRotatePivot(space='world') for guide in self.starter_Spine]
            self.spine_chain = Joint.Joint.point_base(*points, name='{Side}__{Basename}_Result'.format(**self.nameStructure), chain=True, padding=2)
            self.spine_chain_joints = self.spine_chain.joints
            adb.AutoSuffix(self.spine_chain.joints)

            Joint.Joint(self.spine_chain_joints).orientAxis = 'Y'
            self.spine_chain.radius = self.config['JOINTS']["Result_JNT"]['radius']
            return self.spine_chain_joints

        # =========================
        # BUILD RESULT SYSTEM
        # =========================
        createResultJoints()
        self.RESULT_MOD.setFinalHiearchy(INPUT_GRP_LIST=[self.spine_chain_joints[0]])


    def createFkRegularCTRLS(self):
        self.RESULT_MOD.getJoints = []
        for joint in self.spine_chain_joints:
            ctrl = Control.Control(name=joint.replace(NC.JOINT, NC.CTRL),
                                            shape = sl.sl[self.config['CONTROLS']['Spine_FK_Reg']['shape']],
                                            scale=self.config['CONTROLS']['Spine_FK_Reg']['scale'],
                                            matchTransforms = (False, 1,0),
                                            color=('index', 21)
                                            )

            for att in ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'radius']:
                pm.PyNode(joint).setAttr(att, lock=True,
                                        channelBox=False, keyable=False)

            self.RESULT_MOD.getJoints.append(joint)
            pm.parent(ctrl.control.getShape(), joint, relative=True, shape=True)
            pm.delete(ctrl.control)
            pm.rename(joint, NC.getNameNoSuffix(joint))
            adb.AutoSuffix([joint])

        self.nameStructure['Suffix'] = NC.VISRULE
        shapes = [x.getShape() for x in self.spine_chain_joints]
        moduleBase.ModuleBase.setupVisRule(shapes, self.RESULT_MOD.VISRULE_GRP, '{Side}__{Basename}_FK_CTRL__{Suffix}'.format(**self.nameStructure), False)
        self.setupVisRule(self.spine_chain_joints, self.RESULT_MOD.VISRULE_GRP, '{Side}__{Basename}_FK_JNT__{Suffix}'.format(**self.nameStructure), False)

        return self.RESULT_MOD.getJoints


    def createReverseSystem(self, spine_joint_connect):
        self.REVERSE_MOD = moduleBase.ModuleBase()
        self.REVERSE_MOD.hiearchy_setup('{Side}__Reverse'.format(**self.nameStructure))
        self.BUILD_MODULES += [self.REVERSE_MOD]
        pm.parent(self.REVERSE_MOD.MOD_GRP, self.MODULES_GRP)

        @changeColor('index', col = (20))
        def createReverseJoints():
            revJnt = pm.duplicate(self.spine_chain_joints)
            [pm.rename(x, x.replace('Result', 'Reverse').replace('1__JNT','')) for x in revJnt]
            self.reverse_spine_chain = Joint.Joint(revJnt)
            self.reverse_spine_chain.radius = self.spine_chain.radius - 1
            self.reverse_spine_chain_joints = self.reverse_spine_chain.joints
            adb.AutoSuffix(self.reverse_spine_chain_joints)

            ## Parenting the joints
            [pm.parent(x, world=True) for x in self.reverse_spine_chain_joints]
            rev_spine_jnts_reverse = self.reverse_spine_chain_joints[::-1]
            for oParent, oChild in zip(rev_spine_jnts_reverse[:-1], rev_spine_jnts_reverse[1:]):
                pm.parent(oChild, None)
                pm.parent(oChild, oParent)

            return self.reverse_spine_chain_joints


        def create_offset_grps():
            reverse_rotation_grp = [adb.makeroot_func(subject=x, suff = 'Rotation', forceNameConvention=True) for x in self.reverse_spine_chain_joints[::-1]]
            reverse_rotationOffset_grp = [adb.makeroot_func(subject=x, suff = 'Offset', forceNameConvention=True) for x in reverse_rotation_grp]
            [pm.matchTransform(grp, jnt) for grp, jnt in zip (reverse_rotationOffset_grp, self.spine_chain_joints[::-1])]

            [x.rotateOrder.set(5) for x in reverse_rotation_grp]
            [x.rotateOrder.set(5) for x in reverse_rotationOffset_grp]


        def createFkReverseCTRLS():
            self.REVERSE_MOD.getJoints = []
            for joint in self.reverse_spine_chain_joints:
                rev_ctrl = Control.Control(name=joint.replace(NC.JOINT, NC.CTRL),
                                                shape = sl.sl[self.config['CONTROLS']['Spine_FK_Rev']['shape']],
                                                scale=self.config['CONTROLS']['Spine_FK_Rev']['scale'],
                                                matchTransforms = (False, 1,0),
                                                color=('index', 20),
                                                )
                self.REVERSE_MOD.getJoints.append(joint)
                pm.parent(rev_ctrl.control.getShape(), joint, relative=True, shape=True)
                pm.delete(rev_ctrl.control)
                pm.rename(joint, NC.getNameNoSuffix(joint))
                adb.AutoSuffix([joint])

                adb.lockAttr_func(joint, ['sx', 'sy', 'sz', 'radius'])

            self.nameStructure['Suffix'] = NC.VISRULE
            shapes = [x.getShape() for x in self.reverse_spine_chain_joints]
            moduleBase.ModuleBase.setupVisRule(shapes, self.REVERSE_MOD.VISRULE_GRP, '{Side}__{Basename}_FK_Reverse_CTRL__{Suffix}'.format(**self.nameStructure), False)
            self.setupVisRule(self.reverse_spine_chain_joints, self.REVERSE_MOD.VISRULE_GRP, '{Side}__{Basename}_FK_Reverse_JNT__{Suffix}'.format(**self.nameStructure), False)

            return self.REVERSE_MOD.getJoints


        def connectReverseToResult(spine_joint_connect):
            """ Connections for the fk reverse set up """
            for resultJoint, reverseJoint in zip(spine_joint_connect, self.reverse_spine_chain_joints):
                reverseJoint.rotateOrder.set(5)
                multNode = pm.shadingNode('multiplyDivide', asUtility=1)
                multNode.operation.set(1)
                multNode.input2X.set(-1)
                multNode.input2Y.set(-1)
                multNode.input2Z.set(-1)

                resultJoint.rx >> multNode.input1X
                resultJoint.ry >> multNode.input1Y
                resultJoint.rz >> multNode.input1Z

                multNode.outputX >> reverseJoint.getParent().rx
                multNode.outputY >> reverseJoint.getParent().ry
                multNode.outputZ >> reverseJoint.getParent().rz

            ## Connect FK Variable
            if self.FKVARIABLE_MOD:
                for revJnt, grp in zip(self.reverse_spine_chain_joints, self.FKVARIABLE_MOD.getResetJoints[0]):
                    FkVariableRev = adb.makeroot_func(revJnt, suff=self.FKVARIABLE_MOD.NAME, forceNameConvention=True)
                    multNode = pm.shadingNode('multiplyDivide', asUtility=1)
                    multNode.operation.set(1)
                    multNode.input2X.set(-1)
                    multNode.input2Y.set(-1)
                    multNode.input2Z.set(-1)

                    grp.rx >> multNode.input1X
                    grp.ry >> multNode.input1Y
                    grp.rz >> multNode.input1Z

                    multNode.outputX >> revJnt.getParent().rx
                    multNode.outputY >> revJnt.getParent().ry
                    multNode.outputZ >> revJnt.getParent().rz

        createReverseJoints()
        create_offset_grps()
        createFkReverseCTRLS()
        pm.parentConstraint(self.spine_chain_joints[-1], self.reverse_spine_chain_joints[-1].getParent().getParent(), mo=True)
        self.REVERSE_MOD.setFinalHiearchy(OUTPUT_GRP_LIST=[self.reverse_spine_chain_joints[-1].getParent().getParent()])
        connectReverseToResult(spine_joint_connect)


    def createVariableFkSystem(self):
        """
        Create an Fk Variable system based on a Bend Attribute
        Returns:
            Module - Class object of the FkVariable Class
        """
        resultOffset_grp = [adb.makeroot_func(subject=x, suff = 'OFFSET', forceNameConvention=True) for x in self.spine_chain_joints]

        settingsGrpAttr = adbAttr.NodeAttr([self.SETTINGS_GRP])
        settingsGrpAttr.addAttr('Bend', 0)
        fkV = Slide.FkVariable(module_name='Bend', joint_chain=self.spine_chain_joints, driver=[self.SETTINGS_GRP], range=2, driver_axis='Bend', target_axis='rx', useMinus=False)
        fkV.start()
        fkV.build()

        pm.parent(fkV.metaData_GRP, self.SETTINGS_GRP)
        return fkV


    def createIkSystem(self):
        self.SPINEIK_MOD = moduleBase.ModuleBase()
        self.SPINEIK_MOD.hiearchy_setup('{Side}__Ik'.format(**self.nameStructure))
        self.BUILD_MODULES += [self.SPINEIK_MOD]
        pm.parent(self.SPINEIK_MOD.MOD_GRP, self.MODULES_GRP)

        @changeColor('index', col = (18))
        def createIkJoint():
            ik_starter_guide = [self.starter_Spine[0], self.starter_Spine[(len(self.starter_Spine))/2], self.starter_Spine[-1]]

            points = [pm.PyNode(guide).getRotatePivot(space='world') for guide in ik_starter_guide]
            self.spine_ik = Joint.Joint.point_base(*points, name='{Side}__{Basename}_Ik'.format(**self.nameStructure), chain=False, padding=2)

            self.spine_ik_joints = self.spine_ik.joints
            pm.PyNode(self.spine_ik_joints[0]).rename('{Side}__{Basename}_{Parts[0]}'.format(**self.nameStructure))
            pm.PyNode(self.spine_ik_joints[1]).rename('{Side}__{Basename}_{Parts[1]}'.format(**self.nameStructure))
            pm.PyNode(self.spine_ik_joints[2]).rename('{Side}__{Basename}_{Parts[2]}'.format(**self.nameStructure))

            adb.AutoSuffix(self.spine_ik.joints)
            self.spine_ik.radius = self.config['JOINTS']["IK_JNT"]['radius']
            return self.spine_ik_joints

        def createIkCTRLS():
            self.SPINEIK_MOD.getJoints = []
            hips_ctrl =  Control.Control.fkShape(joints=[self.spine_ik_joints[0]],
                                        shape = sl.sl[self.config['CONTROLS']['Spine_IK_Hips']['shape']],
                                        scale = self.config['CONTROLS']['Spine_IK_Hips']['scale'],
                                        color = ('index', self.col_layer1)
                                        )

            belly_ctrl = Control.Control.fkShape(joints=[self.spine_ik_joints[1]],
                                        shape = sl.sl[self.config['CONTROLS']['Spine_IK_Belly']['shape']],
                                        scale =self.config['CONTROLS']['Spine_IK_Belly']['scale'],
                                        color = ('index', self.col_layer1)
                                        )

            chest_ctrl = Control.Control.fkShape(joints=[self.spine_ik_joints[2]],
                                        shape = sl.sl[self.config['CONTROLS']['Spine_IK_Chest']['shape']],
                                        scale = self.config['CONTROLS']['Spine_IK_Chest']['scale'],
                                        color = ('index', self.col_layer1)
                                        )


            self.SPINEIK_MOD.getJoints = self.spine_ik_joints

            for joint in self.spine_ik_joints:
                for att in ['sx','sy','sz','radius']:
                    pm.PyNode(joint).setAttr(att, lock=True, channelBox=False, keyable=False)

            self.nameStructure['Suffix'] = NC.VISRULE
            shapes = [x.getShape() for x in self.spine_ik_joints]
            moduleBase.ModuleBase.setupVisRule(shapes, self.SPINEIK_MOD.VISRULE_GRP, '{Side}__{Basename}_IK_CTRL__{Suffix}'.format(**self.nameStructure), False)
            self.setupVisRule(self.spine_ik_joints, self.SPINEIK_MOD.VISRULE_GRP, '{Side}__{Basename}_IK_JNT__{Suffix}'.format(**self.nameStructure), False)

            self.SPINEIK_MOD.getResetJoints = [x.getParent() for x in self.SPINEIK_MOD.getJoints]
            return self.SPINEIK_MOD.getJoints

        def createRibbon(volumePreservation=True):
            self.RIBBON_MOD = moduleBase.ModuleBase()
            self.RIBBON_MOD.hiearchy_setup('{Side}__Ribbon'.format(**self.nameStructure))
            self.BUILD_MODULES += [self.RIBBON_MOD]
            self.RIBBON_MOD.RIG_GRP.inheritsTransform.set(0)
            pm.parent(self.RIBBON_MOD.MOD_GRP, self.MODULES_GRP)

            def createProxyPlane(name, interval=4):
                locs = locGen.locGenerator(interval, str(self.RESULT_MOD.getJoints[0]), str(self.RESULT_MOD.getJoints[-1]))
                first_loc = Locator.Locator.point_base(pm.PyNode(self.RESULT_MOD.getJoints[0]).getRotatePivot(space='world')).locators[0]
                last_loc = Locator.Locator.point_base(pm.PyNode(self.RESULT_MOD.getJoints[-1]).getRotatePivot(space='world')).locators[0]
                locs.insert(0, first_loc)
                locs.append(last_loc)
                proxy_plane = adbProxy.plane_proxy(locs, name , 'x', type='nurbs')
                pm.delete(locs)
                # pm.polyNormal(upper_proxy_plane, ch=1, userNormalMode=0, normalMode=0)
                pm.select(None)
                return proxy_plane

            def addVolumePreservation():
                self.spine_squash_stretch = adbRibbon.SquashStrech('{Side}__{Basename}_VolumePreservation'.format(**self.nameStructure),
                                                                usingCurve = True,
                                                                ExpCtrl=None,
                                                                ribbon_ctrl= [self.spine_ik_joints[0] , self.spine_ik_joints[-1]],  # Top first, then bottom
                                                                jointList = spine_folli.getResetJoints,
                                                                jointListA = (spine_folli.getResetJoints[0:2], 0),
                                                                jointListB = (spine_folli.getResetJoints[2:-3],  1.5),
                                                                jointListC = (spine_folli.getResetJoints[-1:-3], 0),
                                                            )

                self.spine_squash_stretch.start(metaDataNode='transform')
                self.RIBBON_MOD.metaDataGRPS += [self.spine_squash_stretch.metaData_GRP]
                self.spine_squash_stretch.build()
                return self.spine_squash_stretch

            spine_proxy_plane = createProxyPlane('{Side}__{Basename}_Plane__MSH'.format(**self.nameStructure), interval=4)
            _folliculeVis = 0
            spine_folli = adbFolli.Folli('{Side}__{Basename}_Folli_Plane'.format(**self.nameStructure), countU=1, countV=len(self.spine_chain_joints), vDir='U', radius = 0.5, subject = spine_proxy_plane)
            spine_folli.start(metaDataNode='transform')
            self.RIBBON_MOD.metaDataGRPS += [spine_folli.metaData_GRP]
            spine_folli.build()
            spine_folli.getFollicules = _folliculeVis

            Joint.Joint(spine_folli.getJoints).radius = self.config['JOINTS']["Macro_JNT"]['radius']

            for i, jnt in enumerate(spine_folli.getJoints):
                self.nameStructure['Suffix'] = i + 1
                pm.rename(jnt, '{Side}__{Basename}_END_0{Suffix}'.format(**self.nameStructure))
                adb.AutoSuffix([jnt])

            [adb.changeColor_func(jnt, 'index', 20) for jnt in spine_folli.getJoints]

            pm.parent(spine_folli.MOD_GRP, self.RIBBON_MOD.RIG_GRP)
            self.RIBBON_MOD.setFinalHiearchy(OUTPUT_GRP_LIST=spine_folli.getJoints,
                                             INPUT_GRP_LIST = spine_folli.getInputs,
                                             RIG_GRP_LIST=[spine_proxy_plane])

            if volumePreservation:
                addVolumePreservationMod = addVolumePreservation()
                pm.parent(addVolumePreservationMod.MOD_GRP, self.MODULES_GRP)

                pm.select(addVolumePreservationMod.spineLenghtCurve, r=1)
                pm.select(spine_proxy_plane, add=1)
                mc.CreateWrap()
                addVolumePreservationMod.spineLenghtCurve.inheritsTransform.set(0)
                wrapNode = adb.findDeformer(addVolumePreservationMod.spineLenghtCurve)[0]
                pm.PyNode(wrapNode).autoWeightThreshold.set(1)
                self.nameStructure['Suffix'] = NC.WRAP_SUFFIX
                wrapNode = pm.rename(wrapNode, '{Side}__{Basename}_volumePreservation__{Suffix}'.format(**self.nameStructure))

            for grp in spine_folli.MOD_GRP.getChildren():
                if len(grp.getChildren()) is 0:
                    pm.delete(grp)

            moduleBase.ModuleBase.setupVisRule([self.RIBBON_MOD.OUTPUT_GRP], self.RIBBON_MOD.VISRULE_GRP, '{Side}__{Basename}_MACRO_JNT__{Suffix}'.format(**self.nameStructure), False)
            self.RIBBON_MOD.RIG_GRP.v.set(0)


        # =========================
        # BUILD IK SYSTEM
        # =========================
        createIkJoint()
        createIkCTRLS()

        self.SPINEIK_MOD.setFinalHiearchy(OUTPUT_GRP_LIST=[x.getParent() for x in self.spine_ik_joints])
        createRibbon()


    @makeroot()
    def createHipsMainCTRL(self):
        hips_Ctrl_Object = Control.Control(name='{Side}__Hips__CTRL'.format(**self.nameStructure),
                                           shape = sl.sl[self.config['CONTROLS']['Spine_Hips']['shape']],
                                           scale=self.config['CONTROLS']['Spine_Hips']['scale'],
                                           matchTransforms = (self.SPINEIK_MOD.getJoints[0], 1,0),
                                           parent = self.RIBBON_MOD.INPUT_GRP,
                                           color=('index', self.col_main)
                                           )
        self.hips_Ctrl = hips_Ctrl_Object.control
        pm.parentConstraint(self.hips_Ctrl, self.RESULT_MOD.getJoints[0].getParent().getParent())
        moduleBase.ModuleBase.setupVisRule([self.hips_Ctrl], self.RIBBON_MOD.VISRULE_GRP, '{Side}__{Basename}_Hips_CTRL__{Suffix}'.format(**self.nameStructure), True)

        if self.REVERSE_MOD:
            ik_reverse_spine_guide = [self.reverse_spine_chain_joints[0], self.reverse_spine_chain_joints[(len(self.reverse_spine_chain_joints))/2]]
            for revJnt, ctl in zip(ik_reverse_spine_guide, self.SPINEIK_MOD.getJoints[:-1]):
                pm.parentConstraint(revJnt, pm.PyNode(ctl).getParent(), mo=True)

        return self.hips_Ctrl


    def createChestMainCTRL(self):
        chest_Ctrl_Object = Control.Control(name='{Side}__Chest__CTRL'.format(**self.nameStructure),
                                           shape = sl.sl[self.config['CONTROLS']['Spine_Chest']['shape']],
                                           scale = self.config['CONTROLS']['Spine_Chest']['scale'],
                                           matchTransforms = (self.starter_Spine[self.config['CONTROLS']['Spine_Chest']['pivotPoint']], 1, 1),
                                           parent = self.RIBBON_MOD.INPUT_GRP,
                                           color=('index', self.col_main)
                                           )
        self.chest_Ctrl = chest_Ctrl_Object.control
        adb.makeroot_func(self.chest_Ctrl, suff='OFFSET', forceNameConvention=True)
        pm.parentConstraint(self.chest_Ctrl, self.SPINEIK_MOD.getJoints[-1].getParent(), mo=True)
        moduleBase.ModuleBase.setupVisRule([self.chest_Ctrl], self.RIBBON_MOD.VISRULE_GRP, '{Side}__{Basename}_Chest_CTRL__{Suffix}'.format(**self.nameStructure), True)

        if self.REVERSE_MOD:
            pm.parentConstraint(self.REVERSE_MOD.getJoints[-1], self.chest_Ctrl.getParent(), mo=True)

        return self.chest_Ctrl


    # -------------------
    # CONNECT SLOVERS
    # -------------------


    def connectSpineToLeg(self,
                    spaceSwitchLocatorHips = [],
                    leg_Ik_Hips = [],
                    leg_Fk_Offset_Hips = [],
                    ):
        """
        Args:
            spaceSwitchLocatorHips (list, optional): Group created from a SpaceSwitch Module. Defaults to None.
            leg_Ik_Hips (list, optional): [description]. ex: ['{Side}__Leg_Ik_Hips__JNT'.format(x) for x in 'LR'].
            leg_Fk_Offset_Hips (list, optional): [description]. ex: ['{Side}__Leg_Fk_Hips_Offset__GRP'.format(x) for x in 'LR'].
        """
        [pm.parentConstraint(self.SPINEIK_MOD.getJoints[0], jnt, mo=True) for jnt in leg_Ik_Hips]
        [pm.parentConstraint(self.SPINEIK_MOD.getJoints[0], jnt, mo=True) for jnt in leg_Fk_Offset_Hips]

        # OR
        # [pm.parentConstraint(self.REVERSE_MOD.getJoints[0], jnt, mo=True) for jnt in leg_Ik_Hips]
        # [pm.parentConstraint(self.REVERSE_MOD.getJoints[0], jnt, mo=True) for jnt in leg_Fk_Offset_Hips]

        [pm.parentConstraint(self.REVERSE_MOD.getJoints[0], loc, mo=True) for loc in spaceSwitchLocatorHips]


    def connectSpineToShoulder(self,
                    spaceSwitchLocatorHips = [],
                    spaceSwitchLocatorChest = [],
                    shoulder_ctrl_offset = [],
                    ):
        """
        Args:
            shoulderSpaceGroup (list, optional): [description]. Defaults to None.
            shoulder_ctrl_offset (list, optional): [description]. ex: ['{Side}__Shoulder_Clavicule_AutoClavicule__GRP'.format(x) for x in 'LR'].
        """
        [pm.parentConstraint(self.SPINEIK_MOD.getJoints[2], jnt, mo=True) for jnt in shoulder_ctrl_offset]
        [pm.scaleConstraint(self.SPINEIK_MOD.getJoints[2], jnt, mo=True) for jnt in shoulder_ctrl_offset]

        [pm.parentConstraint(self.SPINEIK_MOD.getJoints[0], loc, mo=True) for loc in spaceSwitchLocatorHips]
        [pm.parentConstraint(self.SPINEIK_MOD.getJoints[2], loc, mo=True) for loc in spaceSwitchLocatorChest]


    def setup_VisibilityGRP(self):
        visGrp = adbAttr.NodeAttr([self.VISIBILITY_GRP])
        visGrp.AddSeparator(self.VISIBILITY_GRP, 'Joints')
        visGrp.addAttr('{Side}_{Basename}_FK_JNT'.format(**self.nameStructure), self.config['VISRULES']['FK_Reg_JNT'])
        visGrp.addAttr('{Side}_{Basename}_FK_Reverse_JNT'.format(**self.nameStructure), self.config['VISRULES']['FK_Rev_JNT'])
        visGrp.addAttr('{Side}_{Basename}_IK_JNT'.format(**self.nameStructure), self.config['VISRULES']['IK_JNT'])
        visGrp.addAttr('{Side}_{Basename}_MACRO_JNT'.format(**self.nameStructure), self.config['VISRULES']['Macro_JNT'])

        visGrp.AddSeparator(self.VISIBILITY_GRP, 'Controls')
        visGrp.addAttr('{Side}_{Basename}_FK_CTRL'.format(**self.nameStructure), self.config['VISRULES']['FK_Reg_CTRL'])
        visGrp.addAttr('{Side}_{Basename}_FK_Reverse_CTRL'.format(**self.nameStructure), self.config['VISRULES']['FK_Rev_CTRL'])
        visGrp.addAttr('{Side}_{Basename}_IK_CTRL'.format(**self.nameStructure), self.config['VISRULES']['IK_CTRL'])
        visGrp.addAttr('{Side}_{Basename}_CHEST_CTRL'.format(**self.nameStructure), self.config['VISRULES']['Chest_CTRL'])
        visGrp.addAttr('{Side}_{Basename}_HIPS_CTRL'.format(**self.nameStructure), self.config['VISRULES']['Hips_CTRL'])

        for attr in visGrp.allAttrs.keys():
            for module in self.BUILD_MODULES:
                for grp in module.VISRULE_GRP.getChildren():
                    shortName = NC.getBasename(grp).split('{Basename}_'.format(**self.nameStructure))[-1]
                    if shortName.lower() in attr.lower():
                        try:
                            pm.connectAttr('{}.{}'.format(visGrp.subject, attr), '{}.vis'.format(grp))
                        except:
                            pass


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


    def cleanUpEmptyGrps(self):
        for ModGrp in self.MODULES_GRP.getChildren():
            for grp in ModGrp.getChildren():
                if len(grp.getChildren()) is 0:
                    pm.delete(grp)


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

    def setup_SpaceGRP(self, transform, Ik_FK_attributeName=[]):
        switch_ctrl = adbAttr.NodeAttr([transform])
        for name in Ik_FK_attributeName:
            switch_ctrl.addAttr(name, 'enum',  eName = "IK:FK:")
        return Ik_FK_attributeName


    def setup_SettingGRP(self):
        setting_ctrl = adbAttr.NodeAttr([self.SETTINGS_GRP])
        setting_ctrl.AddSeparator([self.SETTINGS_GRP], 'VolumePreservation')
        adbAttr.NodeAttr.copyAttr(self.spine_squash_stretch.metaData_GRP, [self.SETTINGS_GRP], nicename='{Side}_{Basename}'.format(**self.nameStructure), forceConnection=True)


    def setupVisRule(self, tansformList, parent, name=False, defaultValue=True):
            """
            Edit : for setting up the visrule for Fk shapes ctrl
            Original one from ModuleBase
            """
            if name:
                visRuleGrp = pm.group(n=name, em=1, parent=parent)
            else:
                visRuleGrp = pm.group(n='{}_{}__{}'.format(NC.getNameNoSuffix(tansformList[0]), NC.getSuffix(tansformList[0]), NC.VISRULE),  em=1, parent=parent)
            visRuleGrp.v.set(0)
            visRuleAttr = adbAttr.NodeAttr([visRuleGrp])
            visRuleAttr.addAttr('vis', 'enum',  eName = "2:0")

            self.nameStructure['Suffix'] = NC.ADDLINEAR_SUFFIX
            addDouble = pm.shadingNode('addDoubleLinear', asUtility=1, n='{Side}__{Basename}_visrule__{Suffix}'.format(**self.nameStructure))
            self.nameStructure['Suffix'] = NC.REVERSE_SUFFIX
            reverse = pm.shadingNode('reverse', asUtility=1, n='{Side}__{Basename}_visrule__{Suffix}'.format(**self.nameStructure))
            addDouble.input2.set(1)
            pm.connectAttr('{}.{}'.format(visRuleGrp, visRuleAttr.name), '{}.inputX'.format(reverse), f=1)
            pm.connectAttr('{}.outputX'.format(reverse), '{}.input1'.format(addDouble), f=1)
            for transform in tansformList:
                pm.connectAttr('{}.output'.format(addDouble), '{}.drawStyle'.format(transform))
            adb.lockAttr_func(visRuleGrp, ['tx', 'ty', 'tz', 'rx', 'ry', 'rx', 'rz', 'sx', 'sy', 'sz','v'])
            return visRuleGrp, visRuleAttr.name


# =========================
# BUILD
# =========================

# L_Spine = LimbSpine(module_name='L__Spine')
# L_Spine.start(jointNumber=7)
# L_Spine.build()
# L_Spine.connect()


