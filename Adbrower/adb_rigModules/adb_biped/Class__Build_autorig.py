# ------------------------------------------------------
# Rigging Toolbox
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import traceback
import maya.cmds as mc
import pymel.core as pm
import sys


#-----------------------------------
# IMPORT CUSTOM MODULES
#----------------------------------- 

import ShapesLibrary as sl
import adbrower


adb = adbrower.Adbrower()

#-----------------------------------
#  DECORATORS
#----------------------------------- 

from adbrower import undo
from adbrower import changeColor

#-----------------------------------
#  CLASS IMPORT
#----------------------------------- 

import adb_rigModules.adb_biped.Class__Leg_setUp as adb_leg
import adb_rigModules.adb_biped.Class__Foot_setUp as adb_foot
import adb_rigModules.adb_biped.Class__Spine_setUp as adb_spine
import adb_rigModules.adb_biped.Class__Arm_setUp as adb_arm
import adb_library.adb_modules.Module__AttachOnCurve as adb_PointonCurve
import adb_rigModules.adb_biped.Class__Spine_setUp as adb_spine

  

#-----------------------------------
#  CLASS
#----------------------------------- 

class autoRig():
    def __init__(self,**kwargs):

        pass
        
    @property
    def getFeetLocators(self):
        all_feet_locs = self.leftFoot.getFootLocators + self.rightFoot.getFootLocators
        return all_feet_locs
                
    def build_legs(self):
        self.leftLeg = adb_leg.LegSetUp(['l__leg_thigh__loc__', 'l__leg_knee__loc__', 'l__leg_ankle__loc__']) 
        self.leftFoot = adb_foot.FootSetUp(guide_foot_loc = ['l__leg_ankle__loc__', 'l__leg_ball__loc__', 'l__leg_toe__loc__', 'l__leg_heel__loc__'])            
        self.leftFoot.FootToLeg('l__Leg__ankle_ik__jnt__','l__Leg__IkHandle__','l__Leg_IK__ctrl__','l__Leg_IK_offset__ctrl__','l__Leg_Options__ctrl__','l__Leg__ankle_fk__ctrl__')              

        self.rightLeg = adb_leg.LegSetUp(['r__leg_thigh__loc__', 'r__leg_knee__loc__', 'r__leg_ankle__loc__'])                    
        self.rightFoot = adb_foot.FootSetUp(guide_foot_loc = ['r__leg_ankle__loc__', 'r__leg_ball__loc__', 'r__leg_toe__loc__', 'r__leg_heel__loc__'])            
        self.rightFoot.FootToLeg('r__Leg__ankle_ik__jnt__','r__Leg__IkHandle__','r__Leg_IK__ctrl__','r__Leg_IK_offset__ctrl__','r__Leg_Options__ctrl__','r__Leg__ankle_fk__ctrl__')      
                            
    def build_arms(self): 
        self.lefttArm = adb_arm.ArmSetUp(['l__arm_clav__loc__', 'l__arm_elbow__loc__', 'l__arm_hand__loc__'])
        self.rightArm = adb_arm.ArmSetUp(['r__arm_clav__loc__', 'r__arm_elbow__loc__', 'r__arm_hand__loc__'])


    def build_spine(self, spine_num):
        
        spine_curve_dup = pm.duplicate('spine_guide__curve', n = 'spine_guide__curve_dup')[0]
        pm.makeIdentity(spine_curve_dup , n=0, s=1, r=1, t=1, apply=True, pn=1)
        pm.parent(spine_curve_dup, world=True)
        
        poc = adb_PointonCurve.PointToCurveJnt(spine_num, sel=spine_curve_dup)

        spine_joints = poc.getJoints      
        adb_spine.SpineSetUp(spine_joints)        
        pm.delete(spine_curve_dup)
        [pm.delete(pm.PyNode(x).getParent()) for x in spine_joints]
        
        
# Rig = autoRig()
# Rig.build_arms()


# adb_spine.SpineSetUp()

