import sys
import os
import pymel.core as pm

from CollDict import indexColor
from adbrower import lockAttr, makeroot, changeColor
import ShapesLibrary as sl

import adb_core.NameConv_utils as NC
import adb_core.Class__AddAttr as adbAttr
import adb_core.Class__Locator as Locator
import adb_core.Class__Control as Control
import adb_core.Class__Skinning as Skinning

import adbrower
adb = adbrower.Adbrower()

DATA_WEIGHT_PATH = 'C:/Users/Audrey/Documents/maya/projects/Roller_Rigging_Project/data/skinWeights/'

# ====================================
# CLASS
# ===================================


class RigBase(object):

    def __init__(self, rigName = 'Audrey'):
        self.RIG_NAME = rigName

        self._start()

    def _start(self):
        """
        - Creates Rig Group
        """
        self.createRigGroups(self.RIG_NAME)
        self.createRigLocators(self.RIG_NAME)


    @classmethod
    def createMainRigCtrl(cls, mainRigName):
        cls.RIG_NAME = mainRigName
        cls.MAIN_BASERIG_GRP = pm.group(n='{}_MainRig__GRP'.format(mainRigName), em=1)
        cls.GEO_BASERIG_GRP = pm.group(n='{}_Geometry__GRP'.format(mainRigName), em=1, parent=cls.MAIN_BASERIG_GRP)
        cls.MODULES_BASERIG_GRP = pm.group(n='{}_Modules__GRP'.format(mainRigName), em=1, parent=cls.MAIN_BASERIG_GRP)
        cls.CONTROL_BASERIG_GRP = pm.group(n='{}_Control__GRP'.format(mainRigName), em=1, parent=cls.MAIN_BASERIG_GRP)

        cls.main_CTRL = Control.Control(name='{}_Main__{}'.format(mainRigName, NC.CTRL),
                                    shape=sl.main_shape,
                                    scale=3,
                                    color = ('index', indexColor["lightYellow"]),
                                    parent=cls.CONTROL_BASERIG_GRP,
                                        )

        cls.mainOffset_CTRL = Control.Control(name='{}_MainOffset__{}'.format(mainRigName, NC.CTRL),
                                    shape=sl.circleY_shape,
                                    scale=4,
                                    color = ('index', indexColor["lightBlue"]),
                                    parent=cls.main_CTRL.control
                                        )

        [adb.makeroot_func(grp, 'Offset', forceNameConvention=True) for grp in [cls.main_CTRL.control, cls.mainOffset_CTRL.control]]
        return cls



    def createRigGroups(self, rigName):
        """
        @module_name : string. Name of the module
        @is_module : Boolean. If its a MODULE or a SYSTEM

        MOD_GRP : Module grp
        RIG__GRP: Constains all the rigs stuff
        INPUT__GRP : contains all the ctrls and offset groups attach to those ctrls
        OUTPUT__GRP : contains all the joints who will be skinned

        Returns: RIG_GRP, INPUT_GRP, OUTPUT_GRP
        """
        self.MAIN_RIG_GRP   = pm.group(n='{}_Rig__GRP'.format(rigName), em=1)
        self.VISIBILITY_GRP = pm.group(n='{}_Visibility__GRP'.format(rigName), em=1, parent=self.MAIN_RIG_GRP)
        self.SETTINGS_GRP   = pm.group(n='{}_Settings__GRP'.format(rigName), em=1, parent=self.MAIN_RIG_GRP)
        self.SPACES_GRP     = pm.group(n='{}_Space__GRP'.format(rigName), em=1, parent=self.MAIN_RIG_GRP)
        self.MODULES_GRP    = pm.group(n='{}_Module__GRP'.format(rigName), em=1, parent=self.MAIN_RIG_GRP)

        [grp.v.set(0) for grp in [self.VISIBILITY_GRP, self.SETTINGS_GRP, self.SPACES_GRP]]
        for grp in [self.VISIBILITY_GRP, self.SETTINGS_GRP, self.SPACES_GRP]:
            for att in ['tx', 'ty', 'tz', 'rx', 'ry', 'rx', 'rz', 'sx', 'sy', 'sz','v']:
                        pm.PyNode(grp).setAttr(att, lock=True, channelBox=False, keyable=False)

        return self.VISIBILITY_GRP, self.SETTINGS_GRP, self.SPACES_GRP, self.MODULES_GRP,


    @classmethod
    @lockAttr()
    def createVSOGrp(cls, mainRigName):
        cls.VIS_VSO_GRP     = pm.group(n='Visibility__GRP', empty=True, parent=cls.CONTROL_BASERIG_GRP)
        cls.SPACES_VSO_GRP  = pm.group(n='Spaces__GRP', empty=True, parent=cls.CONTROL_BASERIG_GRP) 
        cls.OPTIONS_VSO_GRP = pm.group(n='Options__GRP', empty=True, parent=cls.CONTROL_BASERIG_GRP) 

        return cls.VIS_VSO_GRP, cls.SPACES_VSO_GRP, cls.OPTIONS_VSO_GRP


    @classmethod
    @lockAttr()
    @changeColor('index', col = indexColor['lightGrey'])
    def createVSOCtrl(cls, mainRigName):
        VSO_GRP = pm.group(n='{}_VSO_GRP'.format(mainRigName), empty=True, parent=cls.mainOffset_CTRL.control)
        cls.VIS_VSO_CTRL, cls.SPACES_VSO_CTRL, cls.OPTIONS_VSO_CTRL = sl.VSO_shape()

        for ctrl in [cls.VIS_VSO_CTRL, cls.SPACES_VSO_CTRL, cls.OPTIONS_VSO_CTRL]:
            pm.parent(ctrl, VSO_GRP)
            pm.rename(ctrl, ctrl.replace('_ctrl', '__CTRL'))
        pm.select(None)
        return cls.VIS_VSO_CTRL, cls.SPACES_VSO_CTRL, cls.OPTIONS_VSO_CTRL


    @classmethod
    def vsoGrpTovsoCtrl(cls):
        vsoGrps = [ cls.VIS_VSO_GRP, cls.SPACES_VSO_GRP, cls.OPTIONS_VSO_GRP]
        vsoCtrls = [cls.VIS_VSO_CTRL, cls.SPACES_VSO_CTRL, cls.OPTIONS_VSO_CTRL]
        for vso_grp, vso_crl in zip(vsoGrps, vsoCtrls):
            all_attr = pm.listAttr(vso_grp, k=1, v=1, ud=1)
            allSeparator = [x for x in all_attr if  adbAttr.NodeAttr.isSeparator(x)]

            separatorToIgnore = []
            for separator in allSeparator:
                enum = pm.attributeQuery(str(separator), node=vso_grp, listEnum=True)[0]
                if enum == 'Joints':
                    separatorToIgnore.append(separator)
                elif enum == 'Controls':
                    separatorToIgnore.append(separator)

            attrJNT_toIgnore = [x for x in all_attr if x.endswith('JNT')]
            attr_toIgnore = separatorToIgnore + attrJNT_toIgnore
            adbAttr.NodeAttr.copyAttr(vso_grp, [vso_crl], ignore=attr_toIgnore, forceConnection=True)


    @lockAttr()
    def createRigLocators(self, rigName):
        self.WORLD_LOC = Locator.Locator.create(name='{}_WorldTransform__LOC'.format(rigName)).locators[0]
        pm.parent(self.WORLD_LOC, self.SPACES_GRP)
        self.WORLD_LOC.v.set(0)
        return self.WORLD_LOC


    @staticmethod
    def loadSkinClustersWeights(path=DATA_WEIGHT_PATH):
        os.chdir(path)
        for _file in os.listdir(path):
            try:
                Skinning.Skinning.importWeights(path, _file)
            except:
                pass