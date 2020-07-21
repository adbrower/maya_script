import traceback
import maya.cmds as mc
import pymel.core as pm

import adbrower
# reload(adbrower)
adb = adbrower.Adbrower()

from adbrower import lprint
from adbrower import flatList

import adb_core.Class__AddAttr as adbAttr
# reload (adbAttr)

def ik_fk_switch(ctrl_name = '',
               blend_attribute = '',
               result_joints = [],
               ik_joints = [],
               fk_joints = [],
               lenght_blend = 1,
           ):
            
    """
    Function to create an Ik - Fk rotation based script
    
    @param ctrl_name            : (str) Name of the control having the switch attribute
    @param blend_attribute      : (sr)  Name of blend attribute
    @param result_joints        : (list) List of result joints
    @param ik_joints            : (list) List of ik joints
    @param fk_joints            : (list) List of fk joints
    
    example:
    ik_fk_switch(ctrl_name = 'locator1',
                blend_attribute = 'ik_fk_switch',
                result_joints = ['result_01', 'result_02', 'result_03'],
                ik_joints = ['ik_01', 'ik_02', 'ik_03'],
                fk_joints = ['fk_01', 'fk_02', 'fk_03'],
            )
    
    """

    ## add attribute message
    switch_ctrl = adbAttr.NodeAttr([ctrl_name])
    switch_ctrl.addAttr('lenght_blend', lenght_blend, keyable=False)

    ## Creation of the remaps values and blendColor nodes
    BlendColorColl_R = [pm.shadingNode('blendColors',asUtility=1, n="Rotate__BC") for x in result_joints]
    RemapValueColl = [pm.shadingNode('remapValue',asUtility=1, n="Blend__RV") for x in result_joints]

    ## Connect the FK in the Color 1
    for oFK, oBlendColor in zip (ik_joints,BlendColorColl_R):
        pm.PyNode(oFK).rx >> pm.PyNode(oBlendColor).color1R
        pm.PyNode(oFK).ry >> pm.PyNode(oBlendColor).color1G
        pm.PyNode(oFK).rz >> pm.PyNode(oBlendColor).color1B

    ## Connect the IK in the Color 2
    for oIK, oBlendColor in zip (fk_joints,BlendColorColl_R):
        pm.PyNode(oIK).rx >> pm.PyNode(oBlendColor).color2R
        pm.PyNode(oIK).ry >> pm.PyNode(oBlendColor).color2G
        pm.PyNode(oIK).rz >> pm.PyNode(oBlendColor).color2B
                        
    ## Connect the BlendColor node in the Blend joint chain        
    for oBlendColor, oBlendJoint in zip (BlendColorColl_R,result_joints):
        pm.PyNode(oBlendColor).outputR  >> pm.PyNode(oBlendJoint).rx
        pm.PyNode(oBlendColor).outputG  >> pm.PyNode(oBlendJoint).ry
        pm.PyNode(oBlendColor).outputB  >> pm.PyNode(oBlendJoint).rz

    for oBlendColor in BlendColorColl_R:
        pm.PyNode(oBlendColor).blender.set(1)

    ## Connect the Remap Values to Blend Colors
    for oRemapValue,oBlendColor in zip (RemapValueColl,BlendColorColl_R):            
        pm.PyNode(oRemapValue).outValue >> pm.PyNode(oBlendColor).blender

    ## Connect the IK -FK Control to Remap Value
    blend_switch =  '{}.{}'.format(ctrl_name, blend_attribute)
    for each in RemapValueColl:
        pm.PyNode(blend_switch) >> pm.PyNode(each).inputValue
        pm.PyNode('{}.{}'.format(ctrl_name, switch_ctrl.attrName)) >> pm.PyNode(each).inputMax

        

