import traceback
import maya.cmds as mc
import pymel.core as pm

import adbrower
reload(adbrower)
adb = adbrower.Adbrower()

from adbrower import lprint
from adbrower import flatList

import adb_utils.Class__AddAttr as adbAttr
reload (adbAttr)

def switch(blend_attribute_name = 'l__Leg_Options__ctrl__',
           blend_attribute = "l__Leg_Options__ctrl__.IK_FK_Switch",
           oColljoints = ['l__Foot__ankle_result__jnt__', 'l__Foot__ball_result__jnt__', 'l__Foot__toe_result__jnt__'],
           option1 = ['l__Foot__ankle_ik__jnt__', 'l__Foot__ball_ik__jnt__', 'l__Foot__toe_ik__jnt__'],
           option2 = ['l__Foot__ankle_fk_fk__ctrl__', 'l__Foot__ball_fk_fk__ctrl__', 'l__Foot__toe_fk_fk__ctrl__'],
           ):

    ## add attribute message
    switch_ctrl = adbAttr.NodeAttr([blend_attribute_name])
    switch_ctrl.addAttr('blend_lenght', 10, 'message', keyable = False) 

    ## Creation of the remaps values and blendColor nodes
    BlendColorColl_T = [pm.shadingNode('blendColors',asUtility=1, n="Translate_BC_01") for x in oColljoints]
    RemapValueColl = [pm.shadingNode('remapValue',asUtility=1, n="Blend_RV_01") for x in oColljoints]

    ## Connect the FK in the Color 1
    for oFK, oBlendColor in zip (option1,BlendColorColl_T):
        pm.PyNode(oFK).rx >> pm.PyNode(oBlendColor).color1R
        pm.PyNode(oFK).ry >> pm.PyNode(oBlendColor).color1G
        pm.PyNode(oFK).rz >> pm.PyNode(oBlendColor).color1B

    ## Connect the IK in the Color 2
    for oIK, oBlendColor in zip (option2,BlendColorColl_T):
        pm.PyNode(oIK).rx >> pm.PyNode(oBlendColor).color2R
        pm.PyNode(oIK).ry >> pm.PyNode(oBlendColor).color2G
        pm.PyNode(oIK).rz >> pm.PyNode(oBlendColor).color2B
                        
    ## Connect the BlendColor node in the Blend joint chain        
    for oBlendColor, oBlendJoint in zip (BlendColorColl_T,oColljoints):
        pm.PyNode(oBlendColor).outputR  >> pm.PyNode(oBlendJoint).rx
        pm.PyNode(oBlendColor).outputG  >> pm.PyNode(oBlendJoint).ry
        pm.PyNode(oBlendColor).outputB  >> pm.PyNode(oBlendJoint).rz

    for oBlendColor in BlendColorColl_T:
        pm.PyNode(oBlendColor).blender.set(1)

    ## Connect the Remap Values to Blend Colors
    for oRemapValue,oBlendColor in zip (RemapValueColl,BlendColorColl_T):            
        pm.PyNode(oRemapValue).outValue >> pm.PyNode(oBlendColor).blender

    ## Connect the IK -FK Control to Remap Value
    for each in RemapValueColl:
        pm.PyNode(blend_attribute) >> pm.PyNode(each).inputValue
        pm.PyNode(switch_ctrl.getAttrConnection[0]) >> pm.PyNode(each).inputMax
        

# switch()