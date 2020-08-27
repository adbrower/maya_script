import sys
import os
import ConfigParser
import ast
import pymel.core as pm

from CollDict import indexColor
from adbrower import lockAttr, makeroot, changeColor
import ShapesLibrary as sl

import adb_core.NameConv_utils as NC
import adb_core.Class__AddAttr as adbAttr
import adb_core.Class__Locator as Locator
import adb_core.Class__Control as Control
import adb_core.Class__Skinning as Skinning

import adb_rigModules.ModuleGuides as ModuleGuides

reload(ModuleGuides)

import adbrower
adb = adbrower.Adbrower()

DATA_WEIGHT_PATH = '/'.join(pm.sceneName().split('/')[:-2]) + '/data/' + 'skinWeights/'
PROJECT_DATA_PATH = '/'.join(pm.sceneName().split('/')[:-2]) + '/data/'


# ====================================
# CLASS
# ===================================


class MainRigBase(object):
    def __init__(self, rigName = 'Audrey', data_path=None):
        self.RIG_NAME = rigName
        self.DATA_PATH = None 
        if data_path is None:
            self.DATA_PATH = self.initDataPath()
        else:
            self.DATA_PATH = data_path

        self.start()


    def start(self):
        self.createMainRigCtrl()
        self.vosGuide = self.createGuides()

        readPath = self.DATA_PATH + '{}_DATA/'.format(self.vosGuide.RIG_NAME) + self.vosGuide.RIG_NAME + '__GLOC.ini'
        if os.path.exists(readPath):
            self.readData = self.vosGuide.readData(readPath)
            _registeredAttributes = ast.literal_eval(self.readData.get(str(self.vosGuide.guides[0]), 'registeredAttributes'))
            for attribute in _registeredAttributes:
                pm.setAttr('{}.{}'.format(self.vosGuide.guides[0], attribute), ast.literal_eval(self.readData.get(str(self.vosGuide.guides[0]), str(attribute))))
        else:
            pass


    def build(self):
        self.createVSOGrp()
        self.createVSOCtrl()
        pm.matchTransform(self.VIS_VSO_CTRL.getParent(), self.vosGuide.guides, pos=1)
        pm.select(None)


    def connect(self):
        self.STARTER_BASERIG_GRP.v.set(0)
        self.vsoGrpTovsoCtrl()


    def initDataPath(self):
        PROJECT_DATA_PATH = '/'.join(pm.sceneName().split('/')[:-2]) + '/data/'
        if os.path.exists(PROJECT_DATA_PATH  + 'Guides/'):
            os.chdir(PROJECT_DATA_PATH  + 'Guides/')
            return PROJECT_DATA_PATH  + 'Guides/'
        else:
            os.mkdir(PROJECT_DATA_PATH  + 'Guides/')
            os.chdir(PROJECT_DATA_PATH  + 'Guides/')
            return PROJECT_DATA_PATH  + 'Guides/'


    def createMainRigCtrl(self):
        self.MAIN_BASERIG_GRP = pm.group(n='{}_MainRig__GRP'.format(self.RIG_NAME), em=1)
        self.STARTER_BASERIG_GRP = pm.group(n='{}_Starters__GRP'.format(self.RIG_NAME), em=1, parent=self.MAIN_BASERIG_GRP)
        self.GEO_BASERIG_GRP = pm.group(n='{}_Geometry__GRP'.format(self.RIG_NAME), em=1, parent=self.MAIN_BASERIG_GRP)
        self.MODULES_BASERIG_GRP = pm.group(n='{}_Modules__GRP'.format(self.RIG_NAME), em=1, parent=self.MAIN_BASERIG_GRP)
        self.CONTROL_BASERIG_GRP = pm.group(n='{}_Control__GRP'.format(self.RIG_NAME), em=1, parent=self.MAIN_BASERIG_GRP)

        self.main_CTRL = Control.Control(name='{}_Main__{}'.format(self.RIG_NAME, NC.CTRL),
                                    shape=sl.main_shape,
                                    scale=3,
                                    color = ('index', indexColor["lightYellow"]),
                                    parent=self.CONTROL_BASERIG_GRP,
                                        )

        self.mainOffset_CTRL = Control.Control(name='{}_MainOffset__{}'.format(self.RIG_NAME, NC.CTRL),
                                    shape=sl.circleY_shape,
                                    scale=4,
                                    color = ('index', indexColor["lightBlue"]),
                                    parent=self.main_CTRL.control
                                        )

        [adb.makeroot_func(grp, 'Offset', forceNameConvention=True) for grp in [self.main_CTRL.control, self.mainOffset_CTRL.control]]


    @lockAttr()
    def createVSOGrp(self, ):
        self.VIS_VSO_GRP     = pm.group(n='Visibility__GRP', empty=True, parent=self.CONTROL_BASERIG_GRP)
        self.SPACES_VSO_GRP  = pm.group(n='Spaces__GRP', empty=True, parent=self.CONTROL_BASERIG_GRP)
        self.OPTIONS_VSO_GRP = pm.group(n='Options__GRP', empty=True, parent=self.CONTROL_BASERIG_GRP)

        return self.VIS_VSO_GRP, self.SPACES_VSO_GRP, self.OPTIONS_VSO_GRP


    @lockAttr()
    @changeColor('index', col = indexColor['lightGrey'])
    def createVSOCtrl(self):
        VSO_GRP = pm.group(n='{}_VSO_GRP'.format(self.RIG_NAME), empty=True, parent=self.mainOffset_CTRL.control)
        self.VIS_VSO_CTRL, self.SPACES_VSO_CTRL, self.OPTIONS_VSO_CTRL = sl.VSO_shape()

        for ctrl in [self.VIS_VSO_CTRL, self.SPACES_VSO_CTRL, self.OPTIONS_VSO_CTRL]:
            pm.parent(ctrl, VSO_GRP)
            pm.rename(ctrl, ctrl.replace('_ctrl', '__CTRL'))
        pm.select(None)
        return self.VIS_VSO_CTRL, self.SPACES_VSO_CTRL, self.OPTIONS_VSO_CTRL


    def vsoGrpTovsoCtrl(self):
        vsoGrps = [ self.VIS_VSO_GRP, self.SPACES_VSO_GRP, self.OPTIONS_VSO_GRP]
        vsoCtrls = [self.VIS_VSO_CTRL, self.SPACES_VSO_CTRL, self.OPTIONS_VSO_CTRL]
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


    def createGuides(self):
        vsoGuide = ModuleGuides.ModuleGuides.createFkGuide('{}_VSO'.format(self.RIG_NAME))
        [pm.parent(guide, self.STARTER_BASERIG_GRP) for guide in vsoGuide.guides]
        return vsoGuide


    @staticmethod
    def loadSkinClustersWeights(path=DATA_WEIGHT_PATH):
        os.chdir(path)
        for _file in os.listdir(path):
            try:
                Skinning.Skinning.importWeights(path, _file)
            except:
                pass


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



# =========================
# BUILD
# =========================

# rig = MainRigBase('test')
# rig.build()
# rig.connect()

# rig.vosGuide.exportData()
