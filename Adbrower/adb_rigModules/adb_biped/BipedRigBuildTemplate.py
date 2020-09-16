import json
import sys
import os
import ConfigParser
import ast

import adb_core.Class__AddAttr as adbAttr
import adb_core.NameConv_utils as NC
import adb_rigModules.adb_biped.Class__LimbSpine as LimbSpine
import adb_rigModules.adb_biped.Class__LimbLeg as LimbLeg
import adb_rigModules.adb_biped.Class__LimbArm as LimbArm
import adb_rigModules.RigBase as rigBase
import adb_rigModules.ModuleGuides as moduleGuides
import adb_core.Class__Control as Control

reload(adbAttr)
reload(NC)
reload(LimbSpine)
reload(LimbLeg)
reload(LimbArm)
reload(rigBase)
reload(moduleGuides)


DATA_WEIGHT_PATH = 'C:/Users/Audrey/Documents/maya/projects/Roller_Rigging_Project/data/skinWeights/'
DATA_GUIDES_PATH = 'C:/Users/Audrey/Documents/maya/projects/Roller_Rigging_Project/data/guides/'
DATA_SHAPES_PATH = 'C:/Users/Audrey/Documents/maya/projects/Roller_Rigging_Project/data/shapes/'

CONFIG_PATH = 'C:/Users/Audrey/Documents/maya/projects/Roller_Rigging_Project/scripts/'
os.chdir(CONFIG_PATH)
with open("RollerGirl_Config.json", "r") as f:
    ROLLERGIRL_CONFIG = json.load(f)

class gShowProgress(object):
    """
    Based on: http://josbalcaen.com/maya-python-progress-decorator

    Function decorator to show the user (progress) feedback.
    @usage

    import time
    @gShowProgress(end=10)
    def createCubes():
        for i in range(10):
            time.sleep(1)
            if createCubes.isInterrupted(): break
            iCube = mc.polyCube(w=1,h=1,d=1)
            mc.move(i,i*.2,0,iCube)
            createCubes.step()
    """
    def __init__(self, status='Busy...', start=0, end=100, interruptable=True):

        self.mStartValue = start
        self.mEndValue = end
        self.mStatus = status
        self.mInterruptable = interruptable
        self.mMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar')

    def step(self, inValue=1):
        """Increase step
        @param inValue (int) Step value"""
        mc.progressBar(self.mMainProgressBar, edit=True, step=inValue)

    def isInterrupted(self):
        """Check if the user has interrupted the progress
        @return (boolean)"""
        return mc.progressBar(self.mMainProgressBar, query=True, isCancelled=True)

    def start(self):
        """Start progress"""
        mc.waitCursor(state=True)
        mc.progressBar( self.mMainProgressBar,
                edit=True,
                beginProgress=True,
                isInterruptable=self.mInterruptable,
                status=self.mStatus,
                minValue=self.mStartValue,
                maxValue=self.mEndValue
            )
        mc.refresh()

    def end(self):
        """Mark the progress as ended"""
        mc.progressBar(self.mMainProgressBar, edit=True, endProgress=True)
        mc.waitCursor(state=False)

    def __call__(self, inFunction):
        """
        Override call method
        @param inFunction (function) Original function
        @return (function) Wrapped function
        @description
            If there are decorator arguments, __call__() is only called once,
            as part of the decoration process! You can only give it a single argument,
            which is the function object.
        """
        def wrapped_f(*args, **kwargs):
            # Start progress
            self.start()
            # Call original function
            inFunction(*args,**kwargs)
            # End progress
            self.end()

        # Add special methods to the wrapped function
        wrapped_f.step = self.step
        wrapped_f.isInterrupted = self.isInterrupted

        # Copy over attributes
        wrapped_f.__doc__ = inFunction.__doc__
        wrapped_f.__name__ = inFunction.__name__
        wrapped_f.__module__ = inFunction.__module__

        # Return wrapped function
        return wrapped_f

class BuipedBuildTemplate(object):
    def __init__(self):

        self.RIGBASE = rigBase.MainRigBase('RollerGirl')

        self.ALL_BUILD_MODULES = []
        self.ALL_MODULES = []
        self.L_leg = None
        self.R_leg = None
        self.L_arm = None
        self.R_arm = None
        self.C_spine = None

    @gShowProgress(status="starting ...")
    def start(self):
        sys.stdout.write('// Result: starting...\n')
        # LEGS
        self.L_leg = LimbLeg.LimbLeg(module_name='L__Leg', config=ROLLERGIRL_CONFIG)
        self.L_leg.start(buildFootStatus=True)
        self.ALL_BUILD_MODULES.append(self.L_leg)
        self.ALL_MODULES.append(self.L_leg)

        if self.L_leg.buildFootStatus:
            self.ALL_MODULES.append(self.L_leg.FootRig)

        self.R_leg = LimbLeg.LimbLeg(module_name='R__Leg', config=ROLLERGIRL_CONFIG)
        self.R_leg.start(buildFootStatus=True)
        self.ALL_BUILD_MODULES.append(self.R_leg)
        self.ALL_MODULES.append(self.R_leg)

        if self.R_leg.buildFootStatus:
            self.ALL_MODULES.append(self.R_leg.FootRig)

        # ARMS
        self.L_arm = LimbArm.LimbArm(module_name='L__Arm', config=ROLLERGIRL_CONFIG)
        self.L_arm.start(buildShoulderStatus=True)
        self.ALL_BUILD_MODULES.append(self.L_arm)
        self.ALL_MODULES.append(self.L_arm)

        if self.L_arm.buildShoulderStatus:
            self.ALL_MODULES.append(self.L_arm.ShoulderRig)

        self.R_arm = LimbArm.LimbArm(module_name='R__Arm', config=ROLLERGIRL_CONFIG)
        self.R_arm.start(buildShoulderStatus=True)
        self.ALL_BUILD_MODULES.append(self.R_arm)
        self.ALL_MODULES.append(self.R_arm)

        if self.R_arm.buildShoulderStatus:
            self.ALL_MODULES.append(self.R_arm.ShoulderRig)

        # SPINE
        self.C_spine = LimbSpine.LimbSpine(module_name='C__Spine', config=ROLLERGIRL_CONFIG)
        self.C_spine.start(jointNumber=7)
        self.ALL_BUILD_MODULES.append(self.C_spine)
        self.ALL_MODULES.append(self.C_spine)

        [pm.parent(rig.MAIN_RIG_GRP, self.RIGBASE.MODULES_BASERIG_GRP) for rig in self.ALL_MODULES]
        [pm.parent(rig.STARTERS_GRP, self.RIGBASE.STARTER_BASERIG_GRP) for rig in self.ALL_MODULES]
        sys.stdout.write('// Result: Guide Phase Done //\n')


    @gShowProgress(status="building ...")
    def build(self):
        sys.stdout.write('// Result: building...\n')
        for module in self.ALL_BUILD_MODULES:
            module.build()

        for module in self.ALL_MODULES:
            pm.parentConstraint(self.RIGBASE.mainOffset_CTRL.control, module.MAIN_RIG_GRP, mo=True)
            pm.scaleConstraint(self.RIGBASE.mainOffset_CTRL.control, module.MAIN_RIG_GRP, mo=True)

        sys.stdout.write('// Result: Build Phase Done //\n')


    @gShowProgress(status="building ...")
    def connect(self):
        sys.stdout.write('// Result: connecting...\n')
        for module in self.ALL_BUILD_MODULES:
            module.connect()

        self.C_spine.connectSpineToLeg(spaceSwitchLocatorHips = [self.L_leg.ikSpaceSwitchHipsdGrp, self.R_leg.ikSpaceSwitchHipsdGrp],
                         leg_Ik_Hips=['L__Leg_Ik_Hips__JNT', 'R__Leg_Ik_Hips__JNT', 'L__Leg_Ik_Hips_NonStretch__JNT', 'R__Leg_Ik_Hips_NonStretch__JNT'],
                         leg_Fk_Offset_Hips = ['L__Leg_Fk_Hips_Offset__GRP', 'R__Leg_Fk_Hips_Offset__GRP']
                         )

        self.C_spine.connectSpineToShoulder(spaceSwitchLocatorHips = [self.L_arm.ikSpaceSwitchHipsdGrp, self.R_arm.ikSpaceSwitchHipsdGrp],
                                            spaceSwitchLocatorChest = [self.L_arm.ikSpaceSwitchChestdGrp, self.R_arm.ikSpaceSwitchChestdGrp],
                                            shoulder_ctrl_offset = ['L__Shoulder_Module__GRP', 'R__Shoulder_Module__GRP'],
                                            )

        self.RIGBASE.build()
        for module in self.ALL_MODULES:
            adbAttr.NodeAttr.AddSeparator([self.RIGBASE.VIS_VSO_GRP], label='{}'.format(NC.getNameNoSuffix((module.SETTINGS_GRP)).replace('_Settings', '')).upper())
            adbAttr.NodeAttr.copyAttr(module.VISIBILITY_GRP, [self.RIGBASE.VIS_VSO_GRP], forceConnection=True)

            adbAttr.NodeAttr.AddSeparator([self.RIGBASE.SPACES_VSO_GRP], label='{}'.format(NC.getNameNoSuffix((module.SETTINGS_GRP)).replace('_Settings', '')).upper())
            adbAttr.NodeAttr.copyAttr(module.SPACES_GRP, [self.RIGBASE.SPACES_VSO_GRP], forceConnection=True)

            adbAttr.NodeAttr.AddSeparator([self.RIGBASE.OPTIONS_VSO_GRP], label='{}'.format(NC.getNameNoSuffix((module.SETTINGS_GRP)).replace('_Settings', '')).upper())
            adbAttr.NodeAttr.copyAttr(module.SETTINGS_GRP, [self.RIGBASE.OPTIONS_VSO_GRP], forceConnection=True)

        vsoAttr = adbAttr.NodeAttr([self.RIGBASE.VIS_VSO_CTRL])
        vsoAttr.addAttr('Joints', False)
        self.RIGBASE.connect()

        visGrp_all_attr = pm.listAttr(self.RIGBASE.VIS_VSO_GRP, k=1, v=1, ud=1)
        attrJNT_toIgnore = [x for x in visGrp_all_attr if x.endswith('JNT')]

        for attr in attrJNT_toIgnore:
            destination = pm.listConnections('{}.{}'.format(self.RIGBASE.VIS_VSO_GRP ,attr), d=1, p=1)[0]
            multNode = pm.shadingNode('multDoubleLinear', asUtility=1, name='{}_Vis__{}'.format(attr, NC.MULTLINEAR_SUFFIX))
            self.RIGBASE.VIS_VSO_CTRL.Joints >> multNode.input1
            pm.connectAttr('{}.{}'.format(self.RIGBASE.VIS_VSO_GRP, attr), '{}.input2'.format(multNode))
            pm.connectAttr('{}.output'.format(multNode), destination, force=1)

        pm.PyNode(self.RIGBASE.STARTER_BASERIG_GRP).v.set(0)
        sys.stdout.write('// Result: Connect Phase Done //\n')


    @staticmethod
    def loadSkinClustersWeights(path=DATA_WEIGHT_PATH):
        rigBase.RigBase.loadSkinClustersWeights(path = path)


    @staticmethod
    def loadControlShapes(path=DATA_SHAPES_PATH):
        os.chdir(path)
        for FILE_NAME in os.listdir(path):
            with open("{}".format(FILE_NAME),"rb") as rb:
                weightData = rb.read()
                weightLines = weightData.split('\n')
                ctrl = weightLines[0].replace('[','').replace(']','')
                loadShape(control=ctrl, path=path + FILE_NAME)

# ====================================================
# BUILD
# ====================================================


RollerGirlRig = BuipedBuildTemplate()
RollerGirlRig.start()
RollerGirlRig.build()
RollerGirlRig.connect()

RollerGirlRig.loadSkinClustersWeights()
RollerGirlRig.loadControlShapes()


# ====================================================
# EXPORT DATA

def exportStartersData():
    """
    Export All Starters Data
    """

    RollerGirlRig.RIGBASE.vosGuide.exportData(RIGBASE.DATA_PATH)
    RollerGirlRig.L_leg.legGuides.exportData()
    RollerGirlRig.R_leg.legGuides.exportData()

    RollerGirlRig.L_leg.FootRig.footGuides.exportData()
    RollerGirlRig.R_leg.FootRig.footGuides.exportData()

    RollerGirlRig.L_arm.armGuides.exportData()
    RollerGirlRig.R_arm.armGuides.exportData()

    RollerGirlRig.L_arm.ShoulderRig.shoulderGuides.exportData()
    RollerGirlRig.R_arm.ShoulderRig.shoulderGuides.exportData()

    RollerGirlRig.C_spine.spineGuides.exportData()

    sys.stdout.write('// Result: Data exported! \n')


def exportControlsShapes(controlList=[], path = DATA_SHAPES_PATH):
    for ctrl in controlList:
        Control.exportShape(control=ctrl, path=path)



# exportStartersData()
# exportControlsShapes(controlList=['C__Chest__CTRL', 'C__Spine_Belly__CTRL', 'C__Spine_Hips__CTRL', 'C__Hips__CTRL'])





































