# ------------------------------------------------------
# Auto Rig Spine SetUp
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import sys
import os

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
import adb_library.adb_utils.Script__LocGenerator as locGen
import adb_library.adb_utils.Script__PoseReader as PoseReader
import adb_library.adb_utils.Script__ProxyPlane as adbProxy
import adb_core.Class__Skinning as Skinning

import adb_library.adb_modules.Module__Folli as adbFolli
import adb_library.adb_modules.Module__IkStretch as adbIkStretch
import adb_library.adb_modules.Module__SquashStretch_Ribbon as adbRibbon
import adb_library.adb_modules.Module__Slide as Slide
import adb_library.adb_modules.Class__SpaceSwitch as SpaceSwitch

import adb_rigModules.RigBase as RigBase

# reload(adbrower)
# reload(sl)
# reload(Joint)
# reload(RigBase)
# reload(adbAttr)
# reload(NC)
# reload(moduleBase)
# reload(adbIkStretch)
# reload(Control)
# reload(locGen)
# reload(adbPiston)
# reload(Locator)
# reload(adbFolli)
# reload(adbRibbon)
# reload(SpaceSwitch)
# reload(PoseReader)
# reload(Slide)
# reload(Skinning)

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

FkVARIABLE_CONFIG = {
    # color : key : position : value
    'remap' : {
            0 : (0.0 , 0.0),
            1 : (0.5 , 1.0),
            2 : (1.0 , 0.0),
            },
                    }


DATA_WEIGHT_PATH = 'C:/Users/Audrey/Documents/maya/projects/Roller_Rigging_Project/data/skinWeights/'


class LimbSpineModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(LimbSpineModel, self).__init__()
        pass


class LimbSpine(moduleBase.ModuleBase):
    """
    """
    def __init__(self,
                 module_name=None,
                ):
        super(LimbSpine, self).__init__('')

        self.nameStructure = None
        self._MODEL = LimbSpineModel()
        self.NAME = module_name


    def __repr__(self):
        return str('{} : {} \n {}'.format(self.__class__.__name__, self.subject, self.__class__))

    # =========================
    # METHOD
    # =========================

    def start(self, metaDataNode = 'transform'):
        super(LimbSpine, self)._start('', _metaDataNode = metaDataNode)

        # TODO: Create Guide Setup

    def build(self, GUIDES):
        """
        """
        super(LimbSpine, self)._build()

        self.RIG = RigBase.RigBase(rigName = self.NAME)
        self.starter_Spine = GUIDES
        self.side = 'C'

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


    def connect(self):
        super(LimbSpine, self)._connect()

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
            pm.parent(self.RESULT_MOD.MOD_GRP, self.RIG.MODULES_GRP)

            points = [pm.PyNode(guide).getRotatePivot(space='world') for guide in self.starter_Spine]
            self.spine_chain = Joint.Joint.point_base(*points, name='{Side}__{Basename}_Result'.format(**self.nameStructure), chain=True, padding=2)
            self.spine_chain_joints = self.spine_chain.joints
            adb.AutoSuffix(self.spine_chain.joints)

            Joint.Joint(self.spine_chain_joints).orientAxis = 'Y'
            self.spine_chain.radius = 2
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
                                            shape = sl.pinZ_shape,
                                            scale=0.8,
                                            matchTransforms = (False, 1,0),
                                            color=('index', 22)
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
        pm.parent(self.REVERSE_MOD.MOD_GRP, self.RIG.MODULES_GRP)

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
                                                shape = sl.circleY_shape,
                                                scale=1,
                                                matchTransforms = (False, 1,0),
                                                color=('index', 20),
                                                )
                self.REVERSE_MOD.getJoints.append(joint)
                pm.parent(rev_ctrl.control.getShape(), joint, relative=True, shape=True)
                pm.delete(rev_ctrl.control)
                pm.rename(joint, NC.getNameNoSuffix(joint))
                adb.AutoSuffix([joint])

                adb.lockAttr_func(joint, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'radius'])

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

        settingsGrpAttr = adbAttr.NodeAttr([self.RIG.SETTINGS_GRP])
        settingsGrpAttr.addAttr('Bend', 0)
        fkV = Slide.FkVariable(module_name='Bend', joint_chain=self.spine_chain_joints, driver=[self.RIG.SETTINGS_GRP], range=2, driver_axis='Bend', target_axis='rx', useMinus=False)
        fkV.start()
        fkV.build()

        pm.parent(fkV.metaData_GRP, self.RIG.SETTINGS_GRP)
        return fkV

    def createIkSystem(self):
        self.SPINEIK_MOD = moduleBase.ModuleBase()
        self.SPINEIK_MOD.hiearchy_setup('{Side}__Ik'.format(**self.nameStructure))
        self.BUILD_MODULES += [self.SPINEIK_MOD]
        pm.parent(self.SPINEIK_MOD.MOD_GRP, self.RIG.MODULES_GRP)

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
            [adb.makeroot_func(x, suff='OFFSET', forceNameConvention=True) for x in self.spine_ik.joints]
            self.spine_ik.radius = 0.5
            return self.spine_ik_joints

        def createIkCTRLS():
            self.SPINEIK_MOD.getJoints = []
            for joint in self.spine_ik_joints:
                ctrl = Control.Control(name=joint.replace(NC.JOINT, NC.CTRL),
                                                shape = sl.square_shape,
                                                scale=1.2,
                                                matchTransforms = (False, 1,0),
                                                color=('index', 18)
                                                )
                for att in ['radius']:
                    pm.PyNode(joint).setAttr(att, lock=True, channelBox=False, keyable=False)

                self.SPINEIK_MOD.getJoints.append(joint)
                pm.parent(ctrl.control.getShape(), joint, relative=True, shape=True)
                pm.delete(ctrl.control)
                pm.rename(joint, NC.getNameNoSuffix(joint))
                adb.AutoSuffix([joint])

            self.nameStructure['Suffix'] = NC.VISRULE
            shapes = [x.getShape() for x in self.spine_ik_joints]
            moduleBase.ModuleBase.setupVisRule(shapes, self.SPINEIK_MOD.VISRULE_GRP, '{Side}__{Basename}_IK_CTRL__{Suffix}'.format(**self.nameStructure), False)
            self.setupVisRule(self.spine_ik_joints, self.SPINEIK_MOD.VISRULE_GRP, '{Side}__{Basename}_IK_JNT__{Suffix}'.format(**self.nameStructure), False)

            if self.REVERSE_MOD:
                ik_reverse_spine_guide = [self.reverse_spine_chain_joints[0], self.reverse_spine_chain_joints[(len(self.reverse_spine_chain_joints))/2], self.reverse_spine_chain_joints[-1]]
                for revJnt, ctl in zip(ik_reverse_spine_guide, self.SPINEIK_MOD.getJoints):
                    adb.matrixConstraint(revJnt, pm.PyNode(ctl).getParent(), mo=True)

            return self.SPINEIK_MOD.getJoints

        def createRibbon(volumePreservation=True):
            self.RIBBON_MOD = moduleBase.ModuleBase()
            self.RIBBON_MOD.hiearchy_setup('{Side}__Ribbon'.format(**self.nameStructure))
            self.BUILD_MODULES += [self.RIBBON_MOD]
            self.RIBBON_MOD.RIG_GRP.inheritsTransform.set(0)
            pm.parent(self.RIBBON_MOD.MOD_GRP, self.RIG.MODULES_GRP)

            def createProxyPlane(name, interval=4):
                locs = locGen.locGenerator(interval, str(self.spine_ik_joints[0]), str(self.spine_ik_joints[-1]))
                first_loc = Locator.Locator.point_base(pm.PyNode(self.spine_ik_joints[0]).getRotatePivot(space='world')).locators[0]
                last_loc = Locator.Locator.point_base(pm.PyNode(self.spine_ik_joints[-1]).getRotatePivot(space='world')).locators[0]
                locs.insert(0, first_loc)
                locs.append(last_loc)
                proxy_plane = adbProxy.plane_proxy(locs, name , 'x', type='nurbs')
                pm.delete(locs)
                # pm.polyNormal(upper_proxy_plane, ch=1, userNormalMode=0, normalMode=0)
                pm.select(None)
                return proxy_plane

            def addVolumePreservation():
                spine_squash_stretch = adbRibbon.SquashStrech('{Side}__{Basename}_VolumePreservation'.format(**self.nameStructure),
                                                                usingCurve = True,
                                                                ExpCtrl=None,
                                                                ribbon_ctrl= [self.spine_ik_joints[0] , self.spine_ik_joints[-1]],  # Top first, then bottom
                                                                jointList = spine_folli.getResetJoints,
                                                                jointListA = (spine_folli.getResetJoints[0:2], 0),
                                                                jointListB = (spine_folli.getResetJoints[2:-3],  1.5),
                                                                jointListC = (spine_folli.getResetJoints[-1:-3], 0),
                                                            )

                spine_squash_stretch.start(metaDataNode='transform')
                self.RIBBON_MOD.metaDataGRPS += [spine_squash_stretch.metaData_GRP]
                spine_squash_stretch.build()
                return spine_squash_stretch

            spine_proxy_plane = createProxyPlane('{Side}__{Basename}_Plane__MSH'.format(**self.nameStructure), interval=4)
            _folliculeVis = 0
            spine_folli = adbFolli.Folli('{Side}__{Basename}_Folli_Plane'.format(**self.nameStructure), countU=1, countV=len(self.spine_chain_joints), vDir='U', radius = 0.5, subject = spine_proxy_plane)
            spine_folli.start(metaDataNode='transform')
            self.RIBBON_MOD.metaDataGRPS += [spine_folli.metaData_GRP]
            spine_folli.build()
            spine_folli.addControls(shape=sl.circleX_shape, scale=0.5, color=('index', 28))
            spine_folli.getFollicules = _folliculeVis

            Joint.Joint(spine_folli.getJoints).radius = 1

            for i, jnt in enumerate(spine_folli.getJoints):
                self.nameStructure['Suffix'] = i + 1
                pm.rename(jnt, '{Side}__{Basename}_END_0{Suffix}'.format(**self.nameStructure))
                adb.AutoSuffix([jnt])

            [adb.changeColor_func(jnt, 'index', 28) for jnt in spine_folli.getJoints]

            pm.parent(spine_folli.MOD_GRP, self.RIBBON_MOD.RIG_GRP)
            self.RIBBON_MOD.setFinalHiearchy(OUTPUT_GRP_LIST=spine_folli.getJoints,
                                             INPUT_GRP_LIST = spine_folli.getInputs,
                                             RIG_GRP_LIST=[spine_proxy_plane])

            if volumePreservation:
                addVolumePreservationMod = addVolumePreservation()
                pm.parent(addVolumePreservationMod.MOD_GRP, self.RIG.MODULES_GRP)

                # CBB: Wrap integration
                pm.select(addVolumePreservationMod.spineLenghtCurve, r=1)
                pm.select(spine_proxy_plane, add=1)
                mc.CreateWrap()
                addVolumePreservationMod.spineLenghtCurve.inheritsTransform.set(0)
                wrapNode = adb.findDeformer(addVolumePreservationMod.spineLenghtCurve)[0]
                pm.PyNode(wrapNode).autoWeightThreshold.set(1)
                self.nameStructure['Suffix'] = NC.WRAP_SUFFIX
                wrapNode = pm.rename(wrapNode, '{Side}__{Basename}_volumePreservation__{Suffix}'.format(**self.nameStructure))
                print wrapNode

            for grp in spine_folli.MOD_GRP.getChildren():
                if len(grp.getChildren()) is 0:
                    pm.delete(grp)

            moduleBase.ModuleBase.setupVisRule([self.RIBBON_MOD.OUTPUT_GRP], self.RIBBON_MOD.VISRULE_GRP, '{Side}__{Basename}_MACRO_JNT__{Suffix}'.format(**self.nameStructure), False)
            moduleBase.ModuleBase.setupVisRule([self.RIBBON_MOD.INPUT_GRP], self.RIBBON_MOD.VISRULE_GRP, '{Side}__{Basename}_MACRO_CTRL__{Suffix}'.format(**self.nameStructure), False)
            self.RIBBON_MOD.RIG_GRP.v.set(0)


        # =========================
        # BUILD IK SYSTEM
        # =========================
        createIkJoint()
        createIkCTRLS()

        self.SPINEIK_MOD.setFinalHiearchy(OUTPUT_GRP_LIST=[x.getParent() for x in self.spine_ik_joints])
        createRibbon()

    def createMainCTRL(self):
        ctrl = Control.Control(name='{Side}__{Basename}_Reverse'.format(**self.nameStructure),
                                            shape = sl.square_shape,
                                            scale=0.8,
                                            matchTransforms = (False, 1,0),
                                            color=('index', 22)
                                            )


    # -------------------
    # CONNECT SLOVERS
    # -------------------


    def setup_VisibilityGRP(self):
        visGrp = adbAttr.NodeAttr([self.RIG.VISIBILITY_GRP])
        visGrp.AddSeparator(self.RIG.VISIBILITY_GRP, 'Joints')
        visGrp.addAttr('FK_JNT', False)
        visGrp.addAttr('FK_Reverse_JNT', False)
        visGrp.addAttr('IK_JNT', False)
        visGrp.addAttr('MACRO_JNT', True)

        visGrp.AddSeparator(self.RIG.VISIBILITY_GRP, 'Controls')
        visGrp.addAttr('FK_CTRL', True)
        visGrp.addAttr('FK_Reverse_CTRL', False)
        visGrp.addAttr('IK_CTRL', True)
        visGrp.addAttr('MACRO_CTRL', False)

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
        for ModGrp in self.RIG.MODULES_GRP.getChildren():
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
# L_Spine.build(['C_spine001_guide', 'C_spine002_guide', 'C_spine003_guide', 'C_spine004_guide', 'C_spine005_guide', 'C_spine006_guide', 'C_spine007_guide'])
# L_Spine.connect()


