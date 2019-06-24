# ------------------------------------------------------
# Ik Stretch Set Up
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import sys
import traceback
import pymel.core as pm
import maya.cmds as mc
from pprint import pprint
import NameConv_utils as NC
reload(NC)


MODULE_NAME = 'ik_stretch'
METADATA_grp_name = '{}_METADATA'.format(MODULE_NAME)

class stretchyIK(object):
    '''
    Add stretch to any IK chain
    
    @param ik_joints: (list) List of Ik joints chain
    @param ik_ctrl: transform
    @scaleAxe: (string) Axis in which the joints will be scaled
    
    # example
    leg = stretchyIK(  ik_joints = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6', 'joint7'],
                 ik_ctrl = 'joint7__loc__',
                 scaleAxe = 'Y' )
    leg.stretchyIKSetUp()

    
    '''
    def __init__(self,        
                 ik_joints = pm.selected(),
                 ik_ctrl = None,
                 scaleAxe = 'Y'                 
                 ):
                    
                    
       _ik_joints = [pm.PyNode(x) for x in ik_joints]        
       self.start_jnt = _ik_joints[0]
       self.hinge_jnt = _ik_joints[1:-1]
       self.end_jnt = _ik_joints[-1]
       self.ik_ctrl = pm.PyNode(ik_ctrl)
       self.scaleAxe = scaleAxe,       

       self.create_metaData_GRP()
       
    @property
    def stretchAxis(self):
        return self.scaleAxe[0]

    @stretchAxis.setter
    def stretchAxis(self, axis):
        self.scaleAxe = str(axis)
    
    @property
    def startJoint(self):
        return self.start_jnt

    @property
    def endJoint(self):
        return self.end_jnt

    @property
    def hingeJoint(self):
        return self.hinge_jnt

    @property
    def ikCtrl(self):
        return self.ik_ctrl
        
    @property
    def ikHandle(self):
        ik_handle = [x for x in pm.listConnections(str(pm.PyNode(self.startJoint))+'.message', s=1,) if x != 'MayaNodeEditorSavedTabsInfo'][0]
        return (ik_handle)
        
    @property
    def distanceNode(self):
        return self.DistanceLoc

    @property
    def originalDistance(self):
        return self.orig_distance
    
    @property
    def prop_mdv(self):
        return(self.md_prp_node)
    
    @property
    def stretch_mdv(self):
        return(self.md_strech_node)

    @property
    def condition_node(self):
        return(self.cond_node)        
        
    @property
    def setting_grp(self):
        return(self.metaData_GRP)


    def create_metaData_GRP(self):
        ''' Create the sys group for the ikStretch sys'''
        
        if pm.objExists(METADATA_grp_name):
            pm.delete(METADATA_grp_name)
        
        self.metaData_GRP = pm.shadingNode('network', au=1, n='{}_{}'.format(self.ik_ctrl, METADATA_grp_name))
                
        pm.PyNode(self.metaData_GRP).addAttr('Ik_Handle', at='message', keyable = False )
        pm.PyNode(self.metaData_GRP).addAttr('Ik_Distance', at='double', dv=0, keyable = False )
        pm.PyNode(self.metaData_GRP).addAttr('Original_joint_distance', at='double', dv=0, keyable = False )
        pm.PyNode(self.metaData_GRP).addAttr('Joint_Axis', dt='string',  keyable = False )
        
        pm.PyNode(self.metaData_GRP).addAttr('Connecting_Start_Joint', at='message',  keyable = False)
        pm.PyNode(self.metaData_GRP).addAttr('Connecting_End_Joint', at='message',  keyable = False)
        pm.PyNode(self.metaData_GRP).addAttr('Connecting_Hinge_Joint', dt='string',  keyable = False)
        
        pm.PyNode(self.metaData_GRP).addAttr('Distance_Node', at='message',  keyable = False)
        pm.PyNode(self.metaData_GRP).addAttr('Proportion_MDV_Node', at='message',  keyable = False)
        pm.PyNode(self.metaData_GRP).addAttr('Stretch_MDV_Node', at='message',  keyable = False)
        pm.PyNode(self.metaData_GRP).addAttr('Condition_Node', at='message',  keyable = False)


    def stretchyIKSetUp(self):
        '''
        Creates a stretch system for an arm or leg  
        '''

        #-----------------------------------
        # FUNCTION
        #----------------------------------- 


        def createloc(sub = pm.selected()):    
            '''Creates locator at the Pivot of the object selected '''    

            locs = []
            for sel in sub:                           
                loc_align = pm.spaceLocator(n='{}__pos__LOC__'.format(sel))
                locs.append(loc_align)
                pm.matchTransform(loc_align,sel,rot=True, pos=True)
                pm.select(locs, add = True)
            return locs

        posLocs = createloc([self.start_jnt,self.end_jnt])

        sp = (pm.PyNode(posLocs[0]).translateX.get(),pm.PyNode(posLocs[0]).translateY.get(),pm.PyNode(posLocs[0]).translateZ.get())
        ep = (pm.PyNode(posLocs[1]).translateX.get(),pm.PyNode(posLocs[1]).translateY.get(),pm.PyNode(posLocs[1]).translateZ.get())

        #-----------------------------------
        # IK STRETCH BUILD
        #----------------------------------- 

        ## create Nodes
        self.DistanceLoc = pm.distanceDimension(sp=sp,  ep=ep)    
        self.orig_distance = self.DistanceLoc.distance.get()
        
        ## getMaxdistance
        def getMaxDistance():
            pm.parent(posLocs[1],self.end_jnt)
            oriTranslate = self.ik_ctrl.getTranslation()
            pm.move(self.ik_ctrl, 0,-1000,0)
            _max_distance = self.DistanceLoc.distance.get()
            self.ik_ctrl.setTranslation(oriTranslate)        
            return _max_distance
        
        max_distance = getMaxDistance()

        ## condition node
        self.cond_node = pm.shadingNode('condition',asUtility=1, n= '{}__{}'.format(MODULE_NAME, NC.CONDITION_SUFFIX))
        self.cond_node.operation.set(3)
        self.cond_node.colorIfFalseR.set(1)
        self.cond_node.secondTerm.set(1)

        ## multiply Divide strech
        self.md_strech_node = pm.shadingNode('multiplyDivide',asUtility=1, n='{}_strech__MD'.format(MODULE_NAME, NC.MULTIPLY_DIVIDE_SUFFIX))
        self.md_strech_node.operation.set(1)

        ## multiply Divide proportion
        self.md_prp_node = pm.shadingNode('multiplyDivide',asUtility=1, n= '{}_proportion__{}'.format(MODULE_NAME, NC.MULTIPLY_DIVIDE_SUFFIX))
        self.md_prp_node.operation.set(2)
        self.md_prp_node.input2X.set(max_distance)

        ## parenting
        pm.parent(posLocs[1],self.ik_ctrl)
      
        ## connections
        self.DistanceLoc.distance >> self.md_prp_node.input1X
        
        self.md_prp_node.outputX >> self.cond_node.firstTerm
        self.md_prp_node.outputX >> self.cond_node.colorIfTrueR
        
        self.cond_node.outColorR >> self.md_strech_node.input1X
        self.cond_node.outColorR >> self.md_strech_node.input1Y

        self.md_strech_node.outputX >> pm.PyNode(self.start_jnt)+ '.scale' + str(self.scaleAxe[0])
        
        for joint in self.hinge_jnt:
            self.md_strech_node.outputX >> pm.PyNode(joint)+ '.scale' + str(self.scaleAxe[0])

        ## Clean up
        posLocs[0].v.set(0)
        posLocs[1].v.set(0)
        self.DistanceLoc.getParent().v.set(0)
        
        NC.setFinalHiearchy(MODULE_NAME,
                            RIG_GRP_LIST = [self.DistanceLoc.getParent(), posLocs[0]],
                            INPUT_GRP_LIST = [pm.PyNode(self.ik_ctrl).getParent() ],
                            OUTPUT_GRP_LIST = [])     



        def set_metaData_GRP():
            pm.PyNode(self.ikHandle).translate >> pm.PyNode(self.metaData_GRP).Ik_Handle 
            pm.PyNode(self.distanceNode).distance >> pm.PyNode(self.metaData_GRP).Ik_Distance 
            pm.PyNode(self.distanceNode).distance >> pm.PyNode(self.metaData_GRP).Distance_Node 
           
            pm.PyNode(self.startJoint).translate >> pm.PyNode(self.metaData_GRP).Connecting_Start_Joint 
            pm.PyNode(self.endJoint).translate >> pm.PyNode(self.metaData_GRP).Connecting_End_Joint 

            pm.PyNode(self.metaData_GRP).Connecting_Hinge_Joint.set(str([str(joint) for joint in self.hingeJoint]), lock = True)
            
            pm.PyNode(self.prop_mdv).message >> pm.PyNode(self.metaData_GRP).Proportion_MDV_Node 
            pm.PyNode(self.stretch_mdv).message >> pm.PyNode(self.metaData_GRP).Stretch_MDV_Node 
            pm.PyNode(self.condition_node).message >> pm.PyNode(self.metaData_GRP).Condition_Node 
            
            pm.PyNode(self.metaData_GRP).Joint_Axis.set(self.stretchAxis, lock=True) 
            pm.PyNode(self.metaData_GRP).Original_joint_distance.set(self.originalDistance, lock=True) 
        
        set_metaData_GRP()
          




