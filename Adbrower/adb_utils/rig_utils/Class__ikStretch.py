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


class stretchyIK(object):
    def __init__(self,        
                 _selection = pm.selected(),
                 scaleAxe = 'Z'                 
                 ):
       selection = [pm.PyNode(x) for x in _selection]        
       self.start_jnt = selection[0]
       self.hinge_jnt = selection[1:-2]
       self.end_jnt = selection[-2]
       self.ik_ctrl = selection[-1]
       self.scaleAxe = scaleAxe,        

       self.settingsGrp_creation()
       
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
        return(self.ik_sys_grp)


    def settingsGrp_creation(self):
        ''' Create the sys group for the ikStretch sys'''
        
        self.ik_sys_grp = pm.group(n='setting_ik_grp', em=True)
        
        ## Lock and Hide all parameters #            
        self.ik_sys_grp.setAttr("tx", lock=True, channelBox=False, keyable=False)
        self.ik_sys_grp.setAttr("ty", lock=True, channelBox=False, keyable=False)
        self.ik_sys_grp.setAttr("tz", lock=True, channelBox=False, keyable=False)
        self.ik_sys_grp.setAttr("rx", lock=True, channelBox=False, keyable=False)
        self.ik_sys_grp.setAttr("ry", lock=True, channelBox=False, keyable=False)
        self.ik_sys_grp.setAttr("rz", lock=True, channelBox=False, keyable=False)
        self.ik_sys_grp.setAttr("sx", lock=True, channelBox=False, keyable=False)
        self.ik_sys_grp.setAttr("sy", lock=True, channelBox=False, keyable=False)
        self.ik_sys_grp.setAttr("sz", lock=True, channelBox=False, keyable=False)
        
        pm.PyNode(self.ik_sys_grp).addAttr('Ik_Handle', at='message', keyable = False )
        pm.PyNode(self.ik_sys_grp).addAttr('Ik_Distance', at='double', dv=0, keyable = False )
        pm.PyNode(self.ik_sys_grp).addAttr('Original_joint_distance', at='double', dv=0, keyable = False )
        pm.PyNode(self.ik_sys_grp).addAttr('Joint_Axis', dt='string',  keyable = False )
        
        pm.PyNode(self.ik_sys_grp).addAttr('Connecting_Start_Joint', at='message',  keyable = False)
        pm.PyNode(self.ik_sys_grp).addAttr('Connecting_End_Joint', at='message',  keyable = False)
        pm.PyNode(self.ik_sys_grp).addAttr('Connecting_Hinge_Joint', dt='string',  keyable = False)
        
        pm.PyNode(self.ik_sys_grp).addAttr('Distance_Node', at='message',  keyable = False)
        pm.PyNode(self.ik_sys_grp).addAttr('Proportion_MDV_Node', at='message',  keyable = False)
        pm.PyNode(self.ik_sys_grp).addAttr('Stretch_MDV_Node', at='message',  keyable = False)
        pm.PyNode(self.ik_sys_grp).addAttr('Condition_Node', at='message',  keyable = False)


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
                loc_align = pm.spaceLocator(n='{}__pos_loc__'.format(sel))
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
        self.cond_node = pm.shadingNode('condition',asUtility=1, n= (self.start_jnt).replace(self.start_jnt.split('__')[2], 'cond'))
        self.cond_node.operation.set(3)
        self.cond_node.colorIfFalseR.set(1)
        self.cond_node.secondTerm.set(1)

        ## multiply Divide strech
        self.md_strech_node = pm.shadingNode('multiplyDivide',asUtility=1, n=(self.start_jnt).replace(self.start_jnt.split('__')[2], 'strech_md'))
        self.md_strech_node.operation.set(1)

        ## multiply Divide proportion
        self.md_prp_node = pm.shadingNode('multiplyDivide',asUtility=1, n=(self.start_jnt).replace(self.start_jnt.split('__')[2],'prp_md'))
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
        oRoot_grp = pm.group(n='{}__main_strech__grp__'.format(self.startJoint.split('__')[1]), em = True)   
        pm.parent(self.start_jnt, self.ik_sys_grp, self.DistanceLoc.getParent(), pm.PyNode(self.ik_ctrl).getParent(), posLocs[0], oRoot_grp)  


        def set_settingGrp():
            pm.PyNode(self.ikHandle).translate >> pm.PyNode(self.ik_sys_grp).Ik_Handle 
            pm.PyNode(self.distanceNode).distance >> pm.PyNode(self.ik_sys_grp).Ik_Distance 
            pm.PyNode(self.distanceNode).distance >> pm.PyNode(self.ik_sys_grp).Distance_Node 
           
            pm.PyNode(self.startJoint).translate >> pm.PyNode(self.ik_sys_grp).Connecting_Start_Joint 
            pm.PyNode(self.endJoint).translate >> pm.PyNode(self.ik_sys_grp).Connecting_End_Joint 
            
            pm.PyNode(self.ik_sys_grp).Connecting_Hinge_Joint.set(str(self.hingeJoint).replace('nt.Joint','').replace("u'","'").replace("('","").replace("')",""), lock = True)
            
            pm.PyNode(self.prop_mdv).message >> pm.PyNode(self.ik_sys_grp).Proportion_MDV_Node 
            pm.PyNode(self.stretch_mdv).message >> pm.PyNode(self.ik_sys_grp).Stretch_MDV_Node 
            pm.PyNode(self.condition_node).message >> pm.PyNode(self.ik_sys_grp).Condition_Node 
            
            pm.PyNode(self.ik_sys_grp).Joint_Axis.set(self.stretchAxis, lock=True) 
            pm.PyNode(self.ik_sys_grp).Original_joint_distance.set(self.originalDistance, lock=True) 
        
        set_settingGrp()
          


    
leg = stretchyIK()
leg.stretchyIKSetUp()




