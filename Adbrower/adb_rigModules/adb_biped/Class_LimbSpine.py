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

    'blue' : {
            0 : (0 , 0.45),
            1 : (0.5 , 0.5),
            2 : (0.7 , 0.8),
            3 : (1.0 , 1.0),
                        }
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
        self._MODEL = LimbShoudlerModel()
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

        self.shoulder_MOD = None
        self.AUTO_CLAVICULE_MOD = None


        # =================
        # BUILD

        self.create_clavicule_ctrl()
        self.createJoints()
        self.ikSetup()
        self.autoClavicule()


    def connect(self):

        super(LimbSpine, self)._connect()

        # self.connectSpineToArm()


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

 

    # -------------------
    # CONNECT SLOVERS
    # -------------------



    def setup_VisibilityGRP(self):
        visGrp = adbAttr.NodeAttr([self.RIG.VISIBILITY_GRP])
        visGrp.AddSeparator(self.RIG.VISIBILITY_GRP, 'Joints')
        visGrp.addAttr('Clavicule_JNT', True)
        visGrp.addAttr('IK_JNT', False)

        visGrp.AddSeparator(self.RIG.VISIBILITY_GRP, 'Controls')
        visGrp.addAttr('Clavicule_CTRL', True)

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

# L_Spine = LimbSpine(module_name='L__Spine')
# L_Spine.build(['L__clavicule_guide', 'L__shoulder_guide'])
# L_Spine.connect()


