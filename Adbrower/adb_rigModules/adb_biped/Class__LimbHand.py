# ------------------------------------------------------
# Auto Rig Hand SetUp
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


import adb_rigModules.RigBase as rigBase
import adb_rigModules.ModuleGuides as moduleGuides

# reload(adbrower)
# reload(sl)
# reload(Joint)
# reload(adbAttr)
# reload(NC)
# reload(moduleBase)
# reload(Control)
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


class LimbHandModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(LimbHandModel, self).__init__()
        pass

DATA_WEIGHT_PATH = 'C:/Users/Audrey/Documents/maya/projects/Roller_Rigging_Project/data/skinWeights/'
CONFIG_PATH = 'C:/Users/Audrey/Google Drive/[SCRIPT]/python/maya_script/Adbrower/adb_rigModules/adb_biped'

os.chdir(CONFIG_PATH)
with open("BipedConfig.json", "r") as f:
    BIPED_CONFIG = json.load(f)

class LimbHand(rigBase.RigBase):
    """
    """
    def __init__(self,
                 module_name=None,
                 config = BIPED_CONFIG
                ):
        super(LimbHand, self).__init__(module_name, _metaDataNode=None)

        self.nameStructure = None
        self._MODEL = LimbHandModel()
        self.NAME = module_name
        self.config = config


    def __repr__(self):
        return str('{} : {} \n {}'.format(self.__class__.__name__, self.MAIN_RIG_GRP, self.__class__))

    # =========================
    # METHOD
    # =========================

    def start(self):
        Gindex1, Gindex2, Gindex3 = [moduleGuides.ModuleGuides.createFkGuide(prefix='{}_{}'.format(self.NAME, part)) for part in range(3)]
        for guide in [Gindex1, Gindex2, Gindex3]:
            pm.parent(guide.guides, self.STARTERS_GRP)

        pm.PyNode(Gankle.guides[0]).translate.set(0, 2.5, 0)
        pm.PyNode(Gball.guides[0]).translate.set(0, 0.5, 2)
        pm.PyNode(Gtoe.guides[0]).translate.set(0, 0.5, 4)
        pm.PyNode(Gheel.guides[0]).translate.set(0, 0.5, -0.8)

        self.curve_setup(Gankle.guides[0], Gball.guides[0])
        self.curve_setup(Gball.guides[0], Gtoe.guides[0])
        self.curve_setup(Gankle.guides[0], Gheel.guides[0])

        self.handGuides = moduleGuides.ModuleGuides(self.NAME.upper(), [Gankle.guides[0], Gball.guides[0], Gtoe.guides[0], Gheel.guides[0]], self.DATA_PATH)
        readPath = self.handGuides.DATA_PATH + '/' + self.handGuides.RIG_NAME + '__GLOC.ini'
        if os.path.exists(readPath):
            self.loadData = self.handGuides.loadData(readPath)
            for guide in self.handGuides.guides:
                _registeredAttributes = ast.literal_eval(self.loadData.get(str(guide), 'registeredAttributes'))
                for attribute in _registeredAttributes:
                    try:
                        pm.setAttr('{}.{}'.format(guide, attribute), ast.literal_eval(self.loadData.get(str(guide), str(attribute))))
                    except :
                        pass

        pm.select(None)

    def build(self, GUIDES=None):
        """
        # TODO : Add Bank System
        # TODO : Automate walking cycle

        """
        super(LimbHand, self)._build()

        if GUIDES is None:
            GUIDES = self.handGuides.guides

        self.starter_Hand = GUIDES
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
                            'Basename': 'Hand',
                            'Parts'   : ['Ankle', 'Ball', 'Toe', 'Heel'],
                            'Suffix'  : ''
                            }

        self.BUILD_MODULES = []


        # =================
        # BUILD

        self.Hand_MOD = moduleBase.ModuleBase()
        self.BUILD_MODULES += [self.Hand_MOD]
        self.Hand_MOD._start('{Side}__Hand'.format(**self.nameStructure),_metaDataNode = 'transform')
        pm.parent(self.Hand_MOD.metaData_GRP, self.SETTINGS_GRP)
        pm.parent(self.Hand_MOD.MOD_GRP, self.MODULES_GRP)

        # self.handGroupSetup()
        # self.create_hand_ctrl()

    def connect(self,
                armModule = None,
                ):

        super(LimbHand, self)._connect()

        self.connectHandToArm(armModule = armModule,
                              )

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

        Transform(self.MODULES_GRP).pivotPoint = Transform(self.hand_ctrl).worldTrans


    # =========================
    # SOLVERS
    # =========================

    # -------------------
    # BUILD SLOVERS
    # -------------------


    def create_hand_ctrl(self):
        @changeColor('index', col = self.col_main)
        @lockAttr(['sx', 'sy', 'sz' ])
        def create_ctrl():
            self.nameStructure['Suffix'] = NC.CTRL
            self.hand_ctrl = Control.Control(name='{Side}__{Basename}_Main__{Suffix}'.format(**self.nameStructure),
                                                shape = sl.sl[self.config['CONTROLS']['Hand']['shape']],
                                                scale=self.config['CONTROLS']['Hand']['scale'],
                                                matchTransforms = (self.starter_Hand[1], 1,0)
                                                ).control
            pm.matchTransform(self.hand_ctrl, self.handAnkle_joint, pos=0, rot=1)
            if self.side == NC.LEFT_SIDE_PREFIX:
                pm.PyNode(self.hand_ctrl).sx.set(-1)
                pm.makeIdentity(self.hand_ctrl, n=0, s=1, apply=True, pn=1)

            Transform(self.hand_ctrl).pivotPoint = Transform(self.handAnkle_joint).worldTrans
            adb.makeroot_func(self.hand_ctrl, suff='Offset', forceNameConvention=True)
            return self.hand_ctrl
        create_ctrl()

        moduleBase.ModuleBase.setupVisRule([self.hand_ctrl], self.Hand_MOD.VISRULE_GRP)
        pm.parent(self.hand_ctrl.getParent(), self.Hand_MOD.INPUT_GRP)


    def handGroupSetup(self):
        pass


    def connectHandToArm(self,
                 armModule = None,
                 ):
        pass

    # -------------------
    # CONNECT SLOVERS
    # -------------------


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

        Transform(heelRoll).pivotPoint = Transform(self.handHeel_joint).worldTrans
        Transform(ballRoll).pivotPoint = Transform(self.handBall_joint).worldTrans
        Transform(toeRoll).pivotPoint = Transform(self.handToes_joint).worldTrans

        if self.side == NC.RIGTH_SIDE_PREFIX:
            pm.makeIdentity(toeRoll, n=0, r=1, apply=True, pn=1)

        if forceConnection:
            ## connect Attributes
            pm.PyNode(self.Hand_MOD.metaData_GRP.heelRoll) >> heelRoll.rx
            pm.PyNode(self.Hand_MOD.metaData_GRP.ballRoll) >> ballRoll.rx
            pm.PyNode(self.Hand_MOD.metaData_GRP.toeRoll) >> toeRoll.rx

            pm.PyNode(self.Hand_MOD.metaData_GRP.heelSide) >> heelRoll.ry
            pm.PyNode(self.Hand_MOD.metaData_GRP.heelTwist) >> heelRoll.rz
            pm.PyNode(self.Hand_MOD.metaData_GRP.toeSide) >> toeRoll.ry

            self.nameStructure['Suffix'] = NC.MULTIPLY_DIVIDE_SUFFIX
            mult_node = pm.shadingNode('multiplyDivide', asUtility=1, n='{Side}__{Basename}_toeNegate__{Suffix}'.format(**self.nameStructure))
            self.nameStructure['Suffix'] = NC.PLUS_MIN_AVER_SUFFIX
            pma_node = pm.shadingNode('plusMinusAverage', asUtility=1, n='{Side}__{Basename}_toeNegate__{Suffix}'.format(**self.nameStructure))
            mult_node.input2X.set(-1)
            ballRoll.rx >> mult_node.input1X
            mult_node.outputX >> pma_node.input3D[0].input3Dx
            pm.PyNode(self.Hand_MOD.metaData_GRP.toeBend) >> pma_node.input3D[1].input3Dx
            pma_node.output3Dx >> self.handBall_joint.rx

        handOffsetGrp = adb.makeroot_func(toeRoll, suff='Offset', forceNameConvention=True)
        NC.renameBasename(handOffsetGrp, name)

        return handOffsetGrp



# =========================
# BUILD
# =========================

# L_hand = LimbHand(module_name='L__Hand')
# L_hand.start()
# L_hand.build()
# L_hand.connect()


# R_hand = LimbHand(module_name='R__Hand')
# R_hand.build(['R__ankle_guide', 'R__ball_guide', 'R__toe_guide', 'R__heel_guide'])
