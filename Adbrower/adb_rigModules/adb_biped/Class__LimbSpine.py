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
import adb_library.adb_utils.Class__FkShapes as adbFKShape

import adb_library.adb_modules.Module__Folli as adbFolli
import adb_library.adb_modules.Module__IkStretch as adbIkStretch
import adb_library.adb_modules.Module__SquashStretch_Ribbon as adbRibbon
import adb_library.adb_modules.Module__Slide as Slide
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
reload(PoseReader)
reload(Slide)

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
                            'Parts'   : [],
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


    # =========================
    # SOLVERS
    # =========================

    # -------------------
    # BUILD SLOVERS
    # -------------------

    def createResultSystem(self):

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
        pm.parent(self.spine_chain_joints[0], self.RESULT_MOD.INPUT_GRP)

    def createFkRegularCTRLS(self):
        self.fk_ctrl_class_list = []
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

            self.fk_ctrl_class_list.append(ctrl)
            pm.parent(ctrl.control.getShape(), joint, relative=True, shape=True)
            pm.delete(ctrl.control)
            pm.rename(joint, NC.getNameNoSuffix(joint))
            adb.AutoSuffix([joint])

        self.nameStructure['Suffix'] = NC.VISRULE
        shapes = [x.getShape() for x in self.spine_chain_joints]
        moduleBase.ModuleBase.setupVisRule(shapes, self.RESULT_MOD.VISRULE_GRP, '{Side}__{Basename}_FK_CTRL__{Suffix}'.format(**self.nameStructure), False)
        self.setupVisRule(self.spine_chain_joints, self.RESULT_MOD.VISRULE_GRP, '{Side}__{Basename}_FK_JNT__{Suffix}'.format(**self.nameStructure), False)

        return self.fk_ctrl_class_list

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
            self.rev_fk_ctrl_class_list = []
            for joint in self.reverse_spine_chain_joints:
                rev_ctrl = Control.Control(name=joint.replace(NC.JOINT, NC.CTRL),
                                                shape = sl.circleY_shape,
                                                scale=1,
                                                matchTransforms = (False, 1,0),
                                                color=('index', 20),
                                                )
                self.rev_fk_ctrl_class_list.append(rev_ctrl)
                pm.parent(rev_ctrl.control.getShape(), joint, relative=True, shape=True)
                pm.delete(rev_ctrl.control)
                pm.rename(joint, NC.getNameNoSuffix(joint))
                adb.AutoSuffix([joint])

                adb.lockAttr_func(joint, ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'radius'])

            self.nameStructure['Suffix'] = NC.VISRULE
            shapes = [x.getShape() for x in self.reverse_spine_chain_joints]
            moduleBase.ModuleBase.setupVisRule(shapes, self.REVERSE_MOD.VISRULE_GRP, '{Side}__{Basename}_FK_Reverse_CTRL__{Suffix}'.format(**self.nameStructure), False)
            self.setupVisRule(self.reverse_spine_chain_joints, self.REVERSE_MOD.VISRULE_GRP, '{Side}__{Basename}_FK_Reverse_JNT__{Suffix}'.format(**self.nameStructure), False)

            return self.rev_fk_ctrl_class_list


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
        pm.parent(self.reverse_spine_chain_joints[-1].getParent().getParent(), self.REVERSE_MOD.OUTPUT_GRP)
        pm.parentConstraint(self.spine_chain_joints[-1], self.reverse_spine_chain_joints[-1].getParent().getParent(), mo=True)
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
        pass


    # -------------------
    # CONNECT SLOVERS
    # -------------------


    def setup_VisibilityGRP(self):
        visGrp = adbAttr.NodeAttr([self.RIG.VISIBILITY_GRP])
        visGrp.AddSeparator(self.RIG.VISIBILITY_GRP, 'Joints')
        visGrp.addAttr('FK_JNT', True)
        visGrp.addAttr('FK_Reverse_JNT', False)
        visGrp.addAttr('IK_JNT', True)

        visGrp.AddSeparator(self.RIG.VISIBILITY_GRP, 'Controls')
        visGrp.addAttr('FK_CTRL', True)
        visGrp.addAttr('FK_Reverse_CTRL', False)
        visGrp.addAttr('IK_CTRL', True)

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
    # SLOTS
    # =========================


    def setup_SpaceGRP(self, transform, Ik_FK_attributeName=[]):
        switch_ctrl = adbAttr.NodeAttr([transform])
        for name in Ik_FK_attributeName:
            switch_ctrl.addAttr(name, 'enum',  eName = "IK:FK:")

        return Ik_FK_attributeName

# =========================
# BUILD
# =========================

L_Spine = LimbSpine(module_name='L__Spine')
L_Spine.build(['C_spine001_guide', 'C_spine002_guide', 'C_spine003_guide', 'C_spine004_guide', 'C_spine005_guide', 'C_spine006_guide', 'C_spine007_guide'])
L_Spine.connect()


