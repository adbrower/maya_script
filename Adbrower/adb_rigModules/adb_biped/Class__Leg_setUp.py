# ------------------------------------------------------
# Auto Rig Leg SetUp
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import sys
import pymel.core as pm
import maya.cmds as mc
from pprint import pprint

#-----------------------------------
# IMPORT CUSTOM MODULES
#----------------------------------- 

import ShapesLibrary as sl
from ShapesLibrary import* 

import adbrower
adb = adbrower.Adbrower()

import adb_core.Class__AddAttr as adbAttr
import adb_library.adb_utils.Func__Piston as adbPiston
import adb_library.adb_utils.Script__LocGenerator as locGen
import adb_library.adb_utils.Class__ShapeManagement as adbShape

import adb_library.adb_utils.Script__ProxyPlane as adbProxy
import adb_library.adb_modules.Module__Folli as adbFolli
from adb_core.Class__Transforms import Transform
from adb_core.Class__Joint import Joint

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
       
@undo 
class LegSetUp(object):
    def __init__(self, guide_leg_loc = pm.selected(), 
                 ik_ctrl_shape = sl.cube_shape,
                 pole_vector_shape = sl.diamond_shape,
                 plane_proxy_axis = 'x',
                 sliding_ctrl_position = 1,
                 pole_vect_exposant = 5,
                 result_joint_rad = 0.5,
                 ):    
          
        self.guide_leg_loc = [pm.PyNode(x) for x in guide_leg_loc]
        self.ik_ctrl_shape = ik_ctrl_shape
        self.pole_vector_shape = pole_vector_shape
        self.result_joint_rad = result_joint_rad
        self.plane_proxy_axis = plane_proxy_axis
        self.sliding_ctrl_position = sliding_ctrl_position
        self.pole_vect_exposant = pole_vect_exposant
                              
        self.result_leg_chain = None
        self.IKjointsCh = None
        self.FKjointsCh = None
        self.leg_IkHandle_ctrl = None
        self.leg_IkHandle_ctrl_offset = None
        self.leg_IkHandle_jnt_offset = None
        self.max_distance = None
        self.FKcontrols = None
        self.bind_joints_plane_offset = None        
        
        self.side = self.getSide(self.guide_leg_loc[0])
       
        self.nameStructure = {
             'Side':self.side,
             'Basename': 'Leg',
             }

        if self.side == 'r':
            self.col_main = 13
            self.pol_vector_col = (0.5, 0.000, 0.000)
            self.sliding_knee_col = 4
        
        else:
            self.col_main = 6 
            self.pol_vector_col = (0, 0.145, 0.588)
            self.sliding_knee_col = 5
               
        #-----------------------------------
        # FUNTION BUILD
        #-----------------------------------                                        
        self.settingsGrp_creation()
        
        # self.initial_ctrl = pm.PyNode('pCube1') # Nom du controleur existant
        self.initial_ctrl = self.create_switch_ctrl()
        self.ik_fk_switch()

        self.CreateFKcontrols()
        self.CreateIKcontrols()
        self.stretchyIK() 
        self.addFollicules()  
        self.squashRibbon()
        self.set_settingGrp()    
        self.cleanUp_grp()   
 

    #-----------------------------------
    # SETTINGS FUNCTIONS AND PROPERTIES
    #-----------------------------------

    @lockAttr()
    def settingsGrp_creation(self):
        self.ik_sys_grp = pm.group(n='Leg_setting_ik_grp', em=True)
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
        
        self.slidingKnee_sys_grp = pm.group(n='Leg_setting_slidingKnee_grp', em=True)
        _slidingKnee_sys_grp = adbAttr.NodeAttr([self.slidingKnee_sys_grp ]) 
        _slidingKnee_sys_grp.addAttr('Slinding_Knee_Control', 'message', )
        _slidingKnee_sys_grp.addAttr('Top_Loc_Control', 'message', )
        _slidingKnee_sys_grp.addAttr('Bot_Loc_Control', 'message', )
                
        self.ik_sys_grp.v.set(0)
        self.slidingKnee_sys_grp.v.set(0)
        
        return self.ik_sys_grp, self.slidingKnee_sys_grp
        

    @property
    def stretchAxis(self):
        return 'Y'

    @property
    def getBindJoint(self):
        """Joints bind to the proxy plane """
        return self.bind_joints_plane_offset
        
    @property
    def startJoint(self):
        return self.IKjointsCh[0]

    @property
    def endJoint(self):
        return self.IKjointsCh[-1]

    @property
    def hingeJoint(self):
        return self.IKjointsCh[1]

    @property
    def ikCtrl(self):
        return self.leg_IkHandle_ctrl
        
    @property
    def ikHandle_stretch(self):
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
        return(self.md_stretch_node)

    @property
    def condition_node(self):
        return(self.cond_node)        
        
    @property
    def setting_grp(self):
        return(self.ik_sys_grp)

    @property
    def root_grp(self):
        return self.oRoot_grp
                    
    #-----------------------------------
    # BUILD FUNCTIONS
    #-----------------------------------

    @lockAttr(att_to_lock = ['tx','ty','tz','rx','ry','rx','rz','sx','sy','sz','v']) 
    @changeColor('index',col = 3)
    def create_switch_ctrl(self):           
        """Swtich Control options """     
                   
        self.ikfk_ctrl = sl.ik_fk_shape() 
        if self.side == 'r':
            _shapes = pm.PyNode(self.ikfk_ctrl).getShapes()

            pm.select('{}.cv[:]'.format(_shapes[0]))
            pm.select('{}.cv[:]'.format(_shapes[1]), add=True)
            pm.select('{}.cv[:]'.format(_shapes[2]), add=True)
            pm.select('{}.cv[:]'.format(_shapes[3]), add=True)
            
            pm.move(-3, 0, 0, r=1, os=1, wd=1)
        
        else:
            pass
        
        pm.matchTransform(self.ikfk_ctrl,self.guide_leg_loc[-1], pos=True)
        adb.makeroot_func(self.ikfk_ctrl)
                                    
        CtrlName = '{Side}__{Basename}_Options'.format(**self.nameStructure)
        self.ikfk_ctrl.rename(CtrlName)
        adb.AutoSuffix([self.ikfk_ctrl])
        self.ikfk_ctrl.addAttr('IK_FK_Switch', keyable=True, attributeType='enum', en="IK:FK") 
    
        Transform.AddSeparator(self.ikfk_ctrl) 
                  
        self.ikfk_ctrl.addAttr('Auto_Stretch', keyable=True, attributeType='enum', en="on:off")         
        self._ikfk_ctrl_switchAttr = adbAttr.NodeAttr([self.ikfk_ctrl]) 
        self._ikfk_ctrl_switchAttr.addAttr('Offset_Ctrls', False)

        Transform.AddSeparator(self.ikfk_ctrl) 

        # shape visibility
        _IKFK_ctrl_ik_switch_param = self.ikfk_ctrl.name() + ".IK_FK_Switch"

        ctrl_shapes = self.ikfk_ctrl.getShapes() 
        pm.PyNode(_IKFK_ctrl_ik_switch_param) >> pm.PyNode(ctrl_shapes[0]).visibility 
        pm.PyNode(_IKFK_ctrl_ik_switch_param) >> pm.PyNode(ctrl_shapes[1]).visibility         
        
        ReverseColl = [pm.shadingNode('reverse',asUtility=1, n='ik_shape_v__reverse__') for x in range(2)]
                                 
        for each in ReverseColl:
            pm.PyNode(_IKFK_ctrl_ik_switch_param) >> pm.PyNode(each).inputX

        ## Connect the Reverse nodes to IK controls's visibility
        for oReverse,oFkctrls in zip (ReverseColl ,ctrl_shapes[2:]):            
            pm.PyNode(oReverse).outputX  >> pm.PyNode(oFkctrls).visibility            
        return self.ikfk_ctrl
             

    def ik_fk_switch(self):                         
        def setResultjointChain():               
            ## Creating - positionning and renaming the joint         
            pm.select(None)
            self.guide_result_leg_chain = [pm.joint(n='result_joint_0', rad = self.result_joint_rad) for x in range(len(self.guide_leg_loc))]
            for joint in self.guide_result_leg_chain:
                pm.parent(joint, w=True)                    
            for _joint, guide in zip(self.guide_result_leg_chain,self.guide_leg_loc):
                pm.matchTransform(_joint,guide, pos=True)            
            ## Parenting the joints          
            for oParent, oChild in zip(self.guide_result_leg_chain[0:-1], self.guide_result_leg_chain[1:]):
                pm.parent(oChild, None)
                pm.parent(oChild, oParent)     
                    
            pm.PyNode(self.guide_result_leg_chain[0]).rename('{Side}__{Basename}__thigh_result'.format(**self.nameStructure))
            pm.PyNode(self.guide_result_leg_chain[1]).rename('{Side}__{Basename}__knee_result'.format(**self.nameStructure))
            pm.PyNode(self.guide_result_leg_chain[2]).rename('{Side}__{Basename}__ankle_result'.format(**self.nameStructure))            
            adb.AutoSuffix(self.guide_result_leg_chain)
            
            ## orient joint                        
            if self.side == 'r':   
                mirror_chain_1 = pm.mirrorJoint(self.guide_result_leg_chain[0],mirrorYZ=1)
                mirror_chain_2 = [pm.PyNode(x) for x in mirror_chain_1]
                Joint(mirror_chain_2[0:2]).orientAxis = 'Y'
                
                mirror_chain_3 = pm.mirrorJoint(mirror_chain_2[0] ,mirrorBehavior=1, mirrorYZ=1)                
                pm.delete(mirror_chain_1,mirror_chain_2,self.guide_result_leg_chain)
                self.guide_result_leg_chain = [pm.PyNode(x) for x in mirror_chain_3]                
            else:
                Joint(self.guide_result_leg_chain).orientAxis = 'Y'
                   
            return self.guide_result_leg_chain             
        self.result_leg_chain = setResultjointChain()           
        
        def Create3jointsChain():
            """ Duplicates the result joints chain for the Ik and Fk chain"""
                
            for joint in self.result_leg_chain:
                jntradius = joint.radius.get()
            
            def Ikchain(col = 21):
                self.IKjointsCh = pm.duplicate(self.result_leg_chain)                                
                ## Setter le radius de mes joints ##
                for joint in self.IKjointsCh:
                    joint.radius.set(jntradius + 0.2)                                
                for each in self.IKjointsCh:   
                        ctrl = pm.PyNode(each)
                        ctrl.overrideEnabled.set(1)
                        ctrl.overrideRGBColors.set(0)
                        ctrl.overrideColor.set(col)                          
                pm.PyNode(self.IKjointsCh[0]).rename('{Side}__{Basename}___thigh_ik'.format(**self.nameStructure))
                pm.PyNode(self.IKjointsCh[1]).rename('{Side}__{Basename}__knee_ik'.format(**self.nameStructure))
                pm.PyNode(self.IKjointsCh[2]).rename('{Side}__{Basename}__ankle_ik'.format(**self.nameStructure))                      
                adb.AutoSuffix(self.IKjointsCh)                                                
                return self.IKjointsCh
                      
            def Fkchain(col = 14):
                self.FKjointsCh = pm.duplicate(self.result_leg_chain)
                pm.select(self.FKjointsCh)
                
                ## Setter le radius de mes joints ##
                for joint in self.FKjointsCh:
                    joint.radius.set(jntradius + 0.3)                                    
                ## Changer la couleur  de la chaine de joints ##
                for each in  self.FKjointsCh:   
                    ctrl = pm.PyNode(each)
                    ctrl.overrideEnabled.set(1)
                    ctrl.overrideRGBColors.set(0)
                    ctrl.overrideColor.set(col)
                pm.PyNode(self.FKjointsCh[0]).rename('{Side}__{Basename}___thigh_fk'.format(**self.nameStructure))
                pm.PyNode(self.FKjointsCh[1]).rename('{Side}__{Basename}__knee_fk'.format(**self.nameStructure))
                pm.PyNode(self.FKjointsCh[2]).rename('{Side}__{Basename}__ankle_fk'.format(**self.nameStructure))                      
                adb.AutoSuffix(self.FKjointsCh)                                 
                return self.FKjointsCh
            Ikchain()
            Fkchain()                     
    
        def CreateSwitchSetup():
            nameStructure = {
                 'Side':self.side,
                 }

            ## CONNECTIONS FOR ROTATION
            ##-------------------------------- 
            self.BlendColor_Rot_Coll = [pm.shadingNode('blendColors', n =(x).replace(x.split('__')[3], 'rot_switch_bc'), asUtility=1,) for x in self.result_leg_chain]                                                                    
            self.IKFK_ctrl_ik_switch_param = self.initial_ctrl.name() + ".IK_FK_Switch"
           
            ## Connect the FK in the Color 1
            for oFK, oBlendColor in zip (self.FKjointsCh,self.BlendColor_Rot_Coll):
                pm.PyNode(oFK).rx >> pm.PyNode(oBlendColor).color1R
                pm.PyNode(oFK).ry >> pm.PyNode(oBlendColor).color1G
                pm.PyNode(oFK).rz >> pm.PyNode(oBlendColor).color1B

            ## Connect the IK in the Color 2
            for oIK, oBlendColor in zip (self.IKjointsCh,self.BlendColor_Rot_Coll):
                pm.PyNode(oIK).rx >> pm.PyNode(oBlendColor).color2R
                pm.PyNode(oIK).ry >> pm.PyNode(oBlendColor).color2G
                pm.PyNode(oIK).rz >> pm.PyNode(oBlendColor).color2B
                            
            ## Connect the BlendColor node in the Blend joint chain        
            for oBlendColor, oBlendJoint in zip (self.BlendColor_Rot_Coll,self.result_leg_chain):
                pm.PyNode(oBlendColor).outputR  >> pm.PyNode(oBlendJoint).rx
                pm.PyNode(oBlendColor).outputG  >> pm.PyNode(oBlendJoint).ry
                pm.PyNode(oBlendColor).outputB  >> pm.PyNode(oBlendJoint).rz

            for oBlendColor in self.BlendColor_Rot_Coll:
                pm.PyNode(oBlendColor).blender.set(1)

            ## Setting up the blending according to the IK-FK control
            self.RemapValueColl = [pm.shadingNode('remapValue',asUtility=1, n=(x).replace(x.split('__')[3], 'switch_rv')) for x in self.BlendColor_Rot_Coll ]

            ## Connect the Remap Values to Blend Colors
            for oRemapValue,oBlendColor in zip (self.RemapValueColl,self.BlendColor_Rot_Coll):            
                pm.PyNode(oRemapValue).outValue >> pm.PyNode(oBlendColor).blender

            ## Connect the IK -FK Control to Remap Value
            for each in self.RemapValueColl:
                pm.PyNode(self.IKFK_ctrl_ik_switch_param) >> pm.PyNode(each).inputValue
            
            ## CONNECTIONS FOR TRANSLATION       
            ##--------------------------------     
            self.BlendColor_Pos = pm.shadingNode('blendColors', n =(x).replace(x.split('__')[3], 'pos_switch_bc'), asUtility=1)
            
            ## connect the Remap Value to Blend Color
            pm.PyNode(self.RemapValueColl[0]).outValue >> pm.PyNode(self.BlendColor_Pos).blender

            ## Connect the IK in the Color 2
            pm.PyNode(self.IKjointsCh[0]).tx >> pm.PyNode(self.BlendColor_Pos).color2R
            pm.PyNode(self.IKjointsCh[0]).ty >> pm.PyNode(self.BlendColor_Pos).color2G
            pm.PyNode(self.IKjointsCh[0]).tz >> pm.PyNode(self.BlendColor_Pos).color2B

            ## creation Locator FK position
            self.fk_pos_loc = pm.spaceLocator(n='{Side}__{Basename}__thigh_fk_pos__loc__'.format(**self.nameStructure))
            pm.matchTransform(self.fk_pos_loc, self.FKjointsCh[0], pos = True, rot = True) 
            pm.pointConstraint(self.FKjointsCh[0],self.fk_pos_loc, mo = True)
            pm.PyNode(self.fk_pos_loc).v.set(0)

            ## Connect the FK in the Color 2
            pm.PyNode(self.fk_pos_loc).tx >> pm.PyNode(self.BlendColor_Pos).color1R
            pm.PyNode(self.fk_pos_loc).ty >> pm.PyNode(self.BlendColor_Pos).color1G
            pm.PyNode(self.fk_pos_loc).tz >> pm.PyNode(self.BlendColor_Pos).color1B

            ## Connect the BlendColor node in the Blend joint chain                
            pm.PyNode(self.BlendColor_Pos).outputR  >> pm.PyNode(self.result_leg_chain[0]).tx
            pm.PyNode(self.BlendColor_Pos).outputG  >> pm.PyNode(self.result_leg_chain[0]).ty
            pm.PyNode(self.BlendColor_Pos).outputB  >> pm.PyNode(self.result_leg_chain[0]).tz

        ## BUILD IK FK Switch 
        Create3jointsChain() 
        CreateSwitchSetup()      

    
    @lockAttr(att_to_lock = ['tx','ty','tz','sx','sy','sz','v','radius'])      
    @changeColor(col = (1,1,0.236))
    def CreateFKcontrols(self):
        """Creates the FK controls on the Fk joint chain """       
        self.FKcontrols = self.fk_shape_setup(RadiusCtrl = 1,
                                              Normalsctrl = (0,1,0),
                                              listJoint = self.FKjointsCh )

        # Connect the IK -FK Control to FK controls's visibility
        pm.PyNode(self.IKFK_ctrl_ik_switch_param) >> pm.PyNode(self.FKcontrols[0]).visibility      
        return self.FKcontrols
      
   
    def CreateIKcontrols(self): 
        leg_IkHandle = pm.ikHandle( n='{Side}__{Basename}__IkHandle__'.format(**self.nameStructure), sj=self.IKjointsCh[0], ee=self.IKjointsCh[-1])
        leg_IkHandle[0].v.set(0)
        pm.select(self.IKjointsCh[-1], r = True)
        
        @makeroot()
        @changeColor('index', col = self.col_main )        
        def Ik_ctrl(name ='{Side}__{Basename}_IK__ctrl__'.format(**self.nameStructure)):            
            _leg_IkHandle_ctrl = self.ik_ctrl_shape()
            pm.rename(_leg_IkHandle_ctrl,name)
            pm.matchTransform(_leg_IkHandle_ctrl, self.IKjointsCh[-1], pos = True)
            return _leg_IkHandle_ctrl        
        self.leg_IkHandle_ctrl = Ik_ctrl()
               
        @lockAttr(att_to_lock = ['rx','ry','rz','sx','sy','sz'])    
        @changeColor('rgb', col = self.pol_vector_col) 
        @makeroot()  
        def pole_vector_ctrl(name ='{Side}__{Basename}_pv__ctrl__'.format(**self.nameStructure)):            
            pv_guide = adb.PvGuide(leg_IkHandle[0],self.IKjointsCh[-2], exposant=self.pole_vect_exposant)            
            _pole_vector_ctrl = self.pole_vector_shape()
            pm.rename(_pole_vector_ctrl,name)            
            last_point = pm.PyNode(pv_guide).getCVs()
            pm.move(_pole_vector_ctrl,last_point[-1])
            pm.poleVectorConstraint(_pole_vector_ctrl,leg_IkHandle[0] ,weight=1)
                                            
            ## Curve setup
            self.pv_curve = pm.curve(p=[(adb.getWorldTrans([_pole_vector_ctrl])), (adb.getWorldTrans([self.IKjointsCh[-2]]))], k = [0,1], d=1, n ='{Side}__pv__curve__'.format(**self.nameStructure) )
            mc.CenterPivot()
            pm.select(_pole_vector_ctrl, r=True)
            pv_jnt = adb.jointAtCenter()[0]
        
            _loc = pm.spaceLocator(p= adb.getWorldTrans([self.IKjointsCh[-2]]))
            mc.CenterPivot()
            pm.select(_loc, r=True)
            pv_ik_jnt = adb.jointAtCenter()[0]
            pm.skinCluster(pv_jnt ,self.pv_curve,pv_ik_jnt)
            
            ## spaceSwitch
            _pv_switchAttr = adbAttr.NodeAttr([_pole_vector_ctrl]) 
            _pv_switchAttr.addAttr('Follow', 'enum', eName = 'Real Parent:World')   
            
            self.attr_cond_node1 = pm.shadingNode('condition',asUtility=1, n=(self.IKjointsCh[0]).replace(self.IKjointsCh[0].split('__')[3], "switch_cond__"))
            self.attr_cond_node2 = pm.shadingNode('condition',asUtility=1, n=(self.IKjointsCh[0]).replace(self.IKjointsCh[0].split('__')[3], "switch_cond__"))
                        
            _pole_vector_ctrl.Follow >> self.attr_cond_node1.firstTerm
            _pole_vector_ctrl.Follow >> self.attr_cond_node2.firstTerm
            
            self.attr_cond_node2.operation.set(1)
           
            ## Clean up
            pm.PyNode(pv_jnt).v.set(0)
            pm.PyNode(self.pv_curve).template.set(1)            
            pm.PyNode(pv_ik_jnt).v.set(0)
            pm.parent(pv_jnt,_pole_vector_ctrl)
            pm.parent(pv_ik_jnt, self.IKjointsCh[-2])
            pm.delete(_loc,pv_guide)
            adb.changeColor_func(self.pv_curve,col=(0.341, 0.341, 0.341))
            adb.lockAttr_func( self.pv_curve, att_to_lock = ['tx','ty','tz','rx','ry','rx','rz','sx','sy','sz']) 
                                 
            return _pole_vector_ctrl    
        self.pole_vector_ctrl = pole_vector_ctrl()                                
                                                                                                                        
        @makeroot()
        @changeColor('index', col = self.col_main ) 
        def Ik_ctrl_offset(name ='{Side}__{Basename}_IK_offset__ctrl__'.format(**self.nameStructure) ):
            _leg_IkHandle_ctrl_offset = sl.circleY_shape()
            pm.rename(_leg_IkHandle_ctrl_offset,name)
            pm.matchTransform(_leg_IkHandle_ctrl_offset, self.IKjointsCh[-1], pos = True)            
            return _leg_IkHandle_ctrl_offset               
        self.leg_IkHandle_ctrl_offset = Ik_ctrl_offset()  
        
        ## spaceSwitch (suite)
        self.gr_world_offset = pm.group(em=True, n = "world_offset")
        cons_switch = pm.parentConstraint(self.leg_IkHandle_ctrl_offset, self.pole_vector_ctrl[0].getParent(), mo = True)
        pm.parentConstraint(self.gr_world_offset, self.pole_vector_ctrl[0].getParent(), mo = True)
        WeightParam = cons_switch.getWeightAliasList()
        
        self.attr_cond_node1.outColorR >> WeightParam[1]
        self.attr_cond_node2.outColorR >> WeightParam[0]
            
        def IKVisibiltySetUp():              
            ik_ctrls_vis = self.leg_IkHandle_ctrl + self.pole_vector_ctrl
            ik_ctrls_vis.append(self.pv_curve)
                                                      
            ReverseColl = [pm.shadingNode('reverse',asUtility=1, n=(x).replace(x.split('__')[3], 'ik_visibility__reverse__')) for x in ik_ctrls_vis]
                                 
            ## Connect the IK -FK Control to Reverse
            for each in ReverseColl:
                pm.PyNode(self.IKFK_ctrl_ik_switch_param) >> pm.PyNode(each).inputX

            ## Connect the Reverse nodes to IK controls's visibility
            for oReverse,oFkctrls in zip (ReverseColl ,ik_ctrls_vis):            
                pm.PyNode(oReverse).outputX  >> pm.PyNode(oFkctrls).visibility
        
        IKVisibiltySetUp()
        
        ## connection for sliding knee attribute
        self.leg_IkHandle_jnt_offset = pm.duplicate(self.IKjointsCh[-1])            
        pm.rename(self.leg_IkHandle_jnt_offset, self.IKjointsCh[-1].replace(self.IKjointsCh[-1].split('__')[2],'offset' ))        
        pm.parent((pm.PyNode(self.leg_IkHandle_ctrl_offset[0]).getParent()),self.leg_IkHandle_ctrl[0])
        pm.parent(self.leg_IkHandle_jnt_offset, self.leg_IkHandle_ctrl_offset[0])        
        pm.parent(leg_IkHandle[0],self.leg_IkHandle_jnt_offset[0])
        pm.select(None)

        @lockAttr(att_to_lock = ['rx','ry','rz',])   
        @changeColor( type = 'index', col = self.sliding_knee_col)
        def slidingKnee():     
            self.bind_joints_plane_offset = []
                    
            ## TOP PART
            ##-------------
            self.locs_top = locGen.locGenerator(4,self.IKjointsCh[0], self.IKjointsCh[1])
            pm.select(self.locs_top)

            piston_joints_top = adb.jointAtCenter()
            pm.rename(piston_joints_top[0], '{Side}__{Basename}__thigh_top__jnt__'.format(**self.nameStructure))
            pm.rename(piston_joints_top[1], '{Side}__{Basename}__thigh_bot__jnt__'.format(**self.nameStructure))
            pm.rename(piston_joints_top[2], '{Side}__{Basename}__knee_top_01__jnt__'.format(**self.nameStructure))
            pm.rename(piston_joints_top[3], '{Side}__{Basename}__knee_bot_01__jnt__'.format(**self.nameStructure))
            pm.parent(piston_joints_top[1], piston_joints_top[0])
            pm.parent(piston_joints_top[2], piston_joints_top[3])            
            pm.delete(self.locs_top[1:3])
            del self.locs_top[1:3]            
            pm.rename(self.locs_top[0], '{Side}__{Basename}__thigh_top__loc__'.format(**self.nameStructure))
            pm.rename(self.locs_top[1], '{Side}__{Basename}__knee_bot__loc__'.format(**self.nameStructure))
            pm.move(self.locs_top[1],( 0, 0, self.sliding_ctrl_position), r=1, os=1, wd=1) 
            
            ## change controler shape     
            sliding_shape = adbShape.shapeManagement([self.locs_top[1]])
            sliding_shape.shapes = sl.cube_shape 
            pm.scale(self.locs_top[1], (0.2,0.2,0.2) )
            mc.FreezeTransformations()
                        
            ## changement de pivot du sliding knee control
            trans = adb.getWorldTrans([piston_joints_top[-1]])
            pm.move(trans[0], trans[1], trans[2], (pm.PyNode(self.locs_top[1]).scalePivot), (pm.PyNode(self.locs_top[1]).rotatePivot))
            
            ## orient Joint
            Joint(piston_joints_top[0:2]).orientAxis = 'Y'
            pm.select(piston_joints_top[3], r = True)
            pm.select(piston_joints_top[2], add = True)
            Joint(pm.selected()).orientAxis = 'Y'
                   
            adbPiston.createDoublePiston(
                                 lowRootjnt = piston_joints_top[3],
                                 lowEndjnt = piston_joints_top[2],
                                 topRootjnt = piston_joints_top[0],
                                 topEndjnt = piston_joints_top[1],
                                 low_ctrl = self.locs_top[1],
                                 top_ctrl = self.locs_top[0],
                                )
            
            ## bind joints
            for joint in piston_joints_top:
                pm.select(joint,r=True)
                bind_jnt = adb.jointAtCenter()
                adb.changeColor_func(bind_jnt,'index', 13)
                pm.pointConstraint(joint, bind_jnt, mo=True)
                pm.rename(bind_jnt, '{Side}__{Basename}__plane_01'.format(**self.nameStructure))
                self.bind_joints_plane_offset.extend(bind_jnt)

            for bind_jnt in self.bind_joints_plane_offset:
                pm.orientConstraint(self.result_leg_chain[0], bind_jnt, mo=True)
                
                                                                                                            
            ## BOT PART
            ##------------
            self.locs_bot = locGen.locGenerator(4,self.IKjointsCh[1], self.IKjointsCh[2])
            pm.select(self.locs_bot)
            piston_joints_bot = adb.jointAtCenter()
            pm.rename(piston_joints_bot[0], '{Side}__{Basename}__knee_top_02__jnt__'.format(**self.nameStructure))
            pm.rename(piston_joints_bot[1], '{Side}__{Basename}__knee_bot__02__jnt__'.format(**self.nameStructure))
            pm.rename(piston_joints_bot[2], '{Side}__{Basename}__ankle_top__jnt__'.format(**self.nameStructure))
            pm.rename(piston_joints_bot[3], '{Side}__{Basename}__ankle_bot__jnt__'.format(**self.nameStructure))
            pm.parent(piston_joints_bot[1], piston_joints_bot[0])
            pm.parent(piston_joints_bot[2], piston_joints_bot[3])            
            pm.delete(self.locs_bot[1:3])
            del self.locs_bot[1:3]            
            pm.rename(self.locs_bot[0], '{Side}__{Basename}__knee_top__loc__'.format(**self.nameStructure))
            pm.rename(self.locs_bot[1], '{Side}__{Basename}__ankle_bot__loc__'.format(**self.nameStructure))

            ## orient Joint
            Joint(piston_joints_bot[0:2]).orientAxis = 'Y'
            
            pm.select(piston_joints_bot[3], r = True)
            pm.select(piston_joints_bot[2], add = True)
            Joint(pm.selected()).orientAxis = 'Y'
                     
            adbPiston.createDoublePiston(
                                 lowRootjnt = piston_joints_bot[3],
                                 lowEndjnt = piston_joints_bot[2],
                                 topRootjnt = piston_joints_bot[0],
                                 topEndjnt = piston_joints_bot[1],
                                 low_ctrl = self.locs_bot[1],
                                 top_ctrl = self.locs_bot[0],
                                )

            ## bind joints
            for joint in piston_joints_bot[1:]:
                pm.select(joint,r=True)
                bind_jnt = adb.jointAtCenter()
                pm.pointConstraint(joint, bind_jnt, mo=True)
                adb.changeColor_func(bind_jnt,'index', 13)
                pm.rename(bind_jnt, '{Side}__{Basename}__plane_01'.format(**self.nameStructure))
                self.bind_joints_plane_offset.extend(bind_jnt)                                

            for bind_jnt in self.bind_joints_plane_offset[4:]:
                pm.orientConstraint(self.result_leg_chain[1], bind_jnt, mo=True)                                                                                                
                                                                                                                                                                                                                                                                                                
            ## Clean Up
            pm.parent(self.locs_bot[0].getParent(), self.locs_top[1])
            pm.parent(self.locs_bot[1].getParent(), self.result_leg_chain[-1])
            pm.pointConstraint( self.result_leg_chain[0], self.locs_top[0].getParent(),mo=True)
            
            ## match transform position et rotation knee ctrl au joint du genoux
            knee_loc_parent = self.locs_top[1].getParent()
            pm.parent(self.locs_top[1], world=True)
            pm.matchTransform(knee_loc_parent, self.result_leg_chain[1], pos = True, rot=True)
            pm.parent(self.locs_top[1], knee_loc_parent)
            mc.FreezeTransformations(self.locs_top[1])
                        
            pm.pointConstraint(self.result_leg_chain[1], self.locs_top[1].getParent(), mo=True)
            pm.orientConstraint(self.result_leg_chain[1], self.locs_top[1].getParent(), mo=True)

            self.locs_bot[0].getShape().v.set(0)
            self.locs_bot[1].getShape().v.set(0)
            self.locs_top[0].getShape().v.set(0) 
            [x.radius.set((pm.PyNode(self.result_leg_chain[0]).radius.get()) * 0.5) for x in piston_joints_bot]                                   
            [x.radius.set((pm.PyNode(self.result_leg_chain[0]).radius.get()) * 0.5) for x in piston_joints_top]                                   
            [x.radius.set((pm.PyNode(self.result_leg_chain[0]).radius.get()) * 0.8) for x in self.bind_joints_plane_offset]  
            adb.AutoSuffix(self.bind_joints_plane_offset)

                        
            self.sliding_knee_root_grp = pm.group(n='{Side}__{Basename}__slindingKnee__grp__'.format(**self.nameStructure), em = True)
            pm.parent(self.locs_top[1].getParent(),
                     self.locs_top[0].getParent(),
                     self.sliding_knee_root_grp
                     )

            self.bind_joints_plane_offset_grp = pm.group(n='{Side}__{Basename}__skin_jnt__grp__'.format(**self.nameStructure), em = True)
            pm.parent(self.bind_joints_plane_offset,
                     self.bind_joints_plane_offset_grp
                     )                                          
            
            adb.AutoSuffix([self.locs_top[1]])
            return self.locs_top[1]
            
        self.sliding_knee = slidingKnee()

                           
    def stretchyIK(self,
                scaleAxe = 'Y',
                ):
        
        """
        Creates a stretch system for an arm or leg  
        """

        #-----------------------------------
        # FUNCTION
        #----------------------------------- 

        pm.select(self.IKjointsCh, r = True)
        def createloc(sub = pm.selected()):    
            """Creates locator at the Pivot of the object selected """    

            locs = []
            for sel in sub:                           
                loc_align = pm.spaceLocator(n='{}__pos_loc__'.format(sel))
                locs.append(loc_align)
                pm.matchTransform(loc_align,sel,rot=True, pos=True)
                pm.select(locs, add = True)
            return locs

        posLocs = createloc([self.IKjointsCh[0],self.IKjointsCh[-1]])
        pm.rename(posLocs[0],'{Side}__{Basename}__thigh_ik_pos__loc__'.format(**self.nameStructure))

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
            pm.parent(posLocs[1],self.IKjointsCh[-1])
            oriTranslate = self.leg_IkHandle_ctrl[0].getTranslation()
            pm.move(self.leg_IkHandle_ctrl[0], 0,-1000,0)
            _max_distance = self.DistanceLoc.distance.get()
            self.leg_IkHandle_ctrl[0].setTranslation(oriTranslate)        
            return _max_distance

        self.max_distance = getMaxDistance()

        ## condition node
        self.cond_node = pm.shadingNode('condition',asUtility=1, n=(self.IKjointsCh[0]).replace(self.IKjointsCh[0].split('__')[3], "strech_cond"))
        self.cond_node.operation.set(3)
        self.cond_node.colorIfFalseR.set(1)
        self.cond_node.secondTerm.set(1)

        ## multiply Divide strech
        self.md_stretch_node = pm.shadingNode('multiplyDivide',asUtility=1, n=(self.IKjointsCh[0]).replace(self.IKjointsCh[0].split('__')[3], "strech_md"))
        self.md_stretch_node.operation.set(1)

        ## blend Color strech
        self.bc_stretch_node = pm.shadingNode('blendColors', n =(self.IKjointsCh[0]).replace(self.IKjointsCh[0].split('__')[3], 'strech_ik_bc'), asUtility=1,) 
        self.bc_stretch_node.color1R.set(1)
        self.bc_stretch_node.color1G.set(1)
        self.bc_stretch_node.color1B.set(1)
        
        ## multiply Divide proportion
        self.md_prp_node = pm.shadingNode('multiplyDivide',asUtility=1, n=(self.IKjointsCh[0]).replace(self.IKjointsCh[0].split('__')[3], "prp_md"))
        self.md_prp_node.operation.set(2)
        self.md_prp_node.input2X.set(self.max_distance)

        ## blend Colors Auto Stretch
        bc_autoStretch_result_node = [pm.shadingNode('blendColors', n =(x).replace(x.split('__')[3], 'autoStretch_result_bc'), asUtility=1,) for x in self.IKjointsCh]
        bc_autoStretch_ik_node = [pm.shadingNode('blendColors', n =(x).replace(x.split('__')[3], 'autoStretch_ik_bc'), asUtility=1,) for x in self.IKjointsCh]

        ## blend Colors IK FK Switch
        bc_ikFk_node = [pm.shadingNode('blendColors', n =(x).replace(x.split('__')[3], 'ikFk_switch_bc'), asUtility=1,) for x in self.IKjointsCh]
        
        for node in bc_ikFk_node:
            node.color1R.set(1)
            node.color1G.set(1)
            node.color1B.set(1)
        
        ## parenting
        pm.parent(posLocs[1],self.leg_IkHandle_ctrl_offset[0])
        pm.pointConstraint(self.IKjointsCh[0],posLocs[0])

        ## connections for strech
        self.DistanceLoc.distance >> self.md_prp_node.input1X

        self.md_prp_node.outputX >> self.cond_node.firstTerm
        self.md_prp_node.outputX >> self.cond_node.colorIfTrueR

        self.cond_node.outColorR >> self.md_stretch_node.input1X
        self.cond_node.outColorR >> self.md_stretch_node.input1Y
        
        self.IKFK_ctrl_AutoStrech_param = self.initial_ctrl.name() + ".Auto_Stretch"

        self.md_stretch_node.outputX >> self.bc_stretch_node.color2R
        pm.PyNode(self.IKFK_ctrl_AutoStrech_param) >> self.bc_stretch_node.blender  
           
        self.bc_stretch_node.outputR >> pm.PyNode(self.IKjointsCh[0])+ '.scale' + str(scaleAxe)
        self.bc_stretch_node.outputR >> pm.PyNode(self.IKjointsCh[1])+ '.scale' + str(scaleAxe)
        
        ## connections for linking Ik chain with the result chain         
        for oIK, oBlendColor in zip (self.IKjointsCh, bc_autoStretch_result_node):
            pm.PyNode(oIK).sx >> pm.PyNode(oBlendColor).color1R
            pm.PyNode(oIK).sy >> pm.PyNode(oBlendColor).color1G
            pm.PyNode(oIK).sz >> pm.PyNode(oBlendColor).color1B

        for oFK, oBlendColor in zip (self.FKjointsCh,bc_autoStretch_result_node):
            pm.PyNode(oFK).sx >> pm.PyNode(oBlendColor).color2R
            pm.PyNode(oFK).sy >> pm.PyNode(oBlendColor).color2G
            pm.PyNode(oFK).sz >> pm.PyNode(oBlendColor).color2B

        for bcStrech, bcSwitch in zip (bc_autoStretch_result_node,bc_ikFk_node):
            pm.PyNode(bcStrech).outputR >> pm.PyNode(bcSwitch).color2R
            pm.PyNode(bcStrech).outputG >> pm.PyNode(bcSwitch).color2G
            pm.PyNode(bcStrech).outputB >> pm.PyNode(bcSwitch).color2B

        for bcSwitch, oResult in zip (bc_ikFk_node,self.result_leg_chain ):
            pm.PyNode(bcSwitch).outputR >> pm.PyNode(oResult).sx
            pm.PyNode(bcSwitch).outputG >> pm.PyNode(oResult).sy
            pm.PyNode(bcSwitch).outputB >> pm.PyNode(oResult).sz  
                
        Reverse_autoStretch_result_node = [pm.shadingNode('reverse',asUtility=1, n=(x).replace(x.split('__')[3], 'autoStretch__reverse')) for x in self.IKjointsCh]
        
        for node in Reverse_autoStretch_result_node:            
            pm.PyNode(self.IKFK_ctrl_AutoStrech_param) >> node.inputX     

        for oReverse, bcStrech in zip (Reverse_autoStretch_result_node, bc_autoStretch_result_node ):
            pm.PyNode(oReverse).outputX >> pm.PyNode(bcStrech).blender              
                                                
        for node in bc_ikFk_node:          
            pm.PyNode(self.IKFK_ctrl_ik_switch_param) >> node.blender     

        ## Clean up
        posLocs[0].v.set(0)
        posLocs[1].v.set(0)
        self.DistanceLoc.getParent().v.set(0)
        pm.PyNode(self.leg_IkHandle_jnt_offset[0]).v.set(0)
        
        for joint in self.IKjointsCh:
            joint.v.set(0)

        for joint in self.FKcontrols:
            joint.drawStyle.set(2)

             
        self.main_strech_grp = pm.group(n='{Side}__{Basename}__ik_strech__grp__'.format(**self.nameStructure), em = True)   
        pm.parent(self.IKjointsCh[0], self.DistanceLoc.getParent(), pm.PyNode(self.leg_IkHandle_ctrl[0]).getParent(), posLocs[0], self.fk_pos_loc, self.main_strech_grp)

        
    # @lockAttr(att_to_lock = ['sx','sy','sz'])    
    # @changeColor( type = 'index', col = (18))   
    def addFollicules(self,
                      radius = 0.2,
                      controls_shape = sl.circleX_shape
                      ):
        
        ## offset follicules
        leg_proxy_plane_offset = adbProxy.plane_proxy(self.bind_joints_plane_offset, '{Side}__{Basename}__proxy_plane_offset'.format(**self.nameStructure), self.plane_proxy_axis, )
        pm.polyNormal(leg_proxy_plane_offset)
        leg_folli_offset = adbFolli.Folli('test',1, 5, radius = radius, subject = leg_proxy_plane_offset)   
        leg_folli_offset.start()
        leg_folli_offset.build()
        self.follicules_offset_ctrl = leg_folli_offset.addControls(controls_shape)
        pm.PyNode(leg_proxy_plane_offset).v.set(0)
        pm.select(leg_proxy_plane_offset, self.bind_joints_plane_offset, r = True)
        mc.SmoothBindSkin()
        
        follicules_offset_root_grp =  leg_folli_offset.getFolliGrp
        follicules_offset_joints =  leg_folli_offset.getJoints
        [x.v.set(0) for x in follicules_offset_joints]
        [x.v.set(0) for x in leg_folli_offset.getFollicules]
        
        ## skinning follicules
        leg_proxy_plane_skin = adbProxy.plane_proxy(self.bind_joints_plane_offset, '{Side}__{Basename}__proxy_plane_skin'.format(**self.nameStructure), self.plane_proxy_axis, )  
        pm.polyNormal(leg_proxy_plane_skin)     
        # pm.polySmooth(leg_proxy_plane_skin, ch=0, ost=1, khe=0, ps=0.1, kmb=1, bnr=1, mth=0, suv=1, peh=0, ksb=1, ro=1, sdt=2, ofc=0, kt=1, ovb=1, dv=1, ofb=3, kb=1, c=1, ocr=0, dpe=1, sl=1)        
        leg_folli_skin = adbFolli.Folli('test1', 1, 20, radius = radius, subject = leg_proxy_plane_skin)   
        leg_folli_skin.start()
        leg_folli_skin.build()
        pm.PyNode(leg_proxy_plane_skin).v.set(0)
        pm.select(leg_proxy_plane_skin, follicules_offset_joints, r = True)
        mc.SmoothBindSkin()
        
        follicules_skin_root_grp =  leg_folli_skin.getFolliGrp
        self.follicules_skin_joints =  leg_folli_skin.getJoints
        pm.PyNode(follicules_skin_root_grp).v.set(0)  
        [x.v.set(0) for x in leg_folli_skin.getFollicules]    
                                                                            
        ## clean up group
        self.follicules_offset_root_grp = pm.group(n='{Side}__{Basename}__follicules__grp__'.format(**self.nameStructure), em = True)
        pm.parent(leg_proxy_plane_offset,
                 follicules_offset_root_grp,
                 leg_proxy_plane_skin,
                 follicules_skin_root_grp,
                 self.follicules_offset_root_grp,
                 )
 
        ## renaming clean up
        adb.AutoSuffix(['{Side}__{Basename}__proxy_plane_offset'.format(**self.nameStructure)])       
        adb.AutoSuffix(['{Side}__{Basename}__proxy_plane_skin'.format(**self.nameStructure)])       
                        
        [pm.rename(x,'{[Side]}__{[Basename]}__proxy_plane_skin_0{}'.format(self.nameStructure, self.nameStructure,index+1)) for index, x in enumerate(self.follicules_offset_ctrl)]
        pm.select(self.follicules_skin_joints, r =True)
        
        ## connection de la visibility des controleurs
        [self.ikfk_ctrl.Offset_Ctrls >> control.v for control in self.follicules_offset_ctrl]

        return self.follicules_offset_ctrl                
                        

    def squashRibbon(self): 
      
        ## Attribute  
        self._ikfk_ctrl_switchAttr = adbAttr.NodeAttr([self.ikfk_ctrl])   
        self._ikfk_ctrl_switchAttr.addAttr('Volume_Preservation', False)
        self._ikfk_ctrl_switchAttr.addAttr('ExpA', 0.2)
        self._ikfk_ctrl_switchAttr.addAttr('ExpB', 0.3)
        self._ikfk_ctrl_switchAttr.addAttr('ExpC', 0.2)
        
        Transform.ShiftAtt(1,_obj=[str(self.ikfk_ctrl)], _attr= ['Volume_Preservation','ExpA','ExpB','ExpC'])
        Transform.ShiftAtt(1,_obj=[str(self.ikfk_ctrl)], _attr= ['Volume_Preservation','ExpA','ExpB','ExpC'])
        
        Transform.AddSeparator(self.ikfk_ctrl) 
                
        Transform.ShiftAtt(0,_obj=[str(self.ikfk_ctrl)], _attr= ['Offset_Ctrls'])

        ## multiply Divide squash
        self.md_squash_node = pm.shadingNode('multiplyDivide',asUtility=1, n=(self.IKjointsCh[0]).replace(self.IKjointsCh[0].split('__')[3], "squash_md"))
        self.md_squash_node.operation.set(2)
        self.md_squash_node.input1X.set(self.orig_distance)

        self.bc_squash_node = pm.shadingNode('blendColors', n =(self.IKjointsCh[0]).replace(self.IKjointsCh[0].split('__')[3], 'squash_skn_jnts_bc'), asUtility=1,) 
        self.bc_squash_node.color2R.set(0)
        self.bc_squash_node.color2G.set(0)
        self.bc_squash_node.color2B.set(0)
        
        self.md_squash_expA_node = pm.shadingNode('multiplyDivide',asUtility=1, n=(self.IKjointsCh[0]).replace(self.IKjointsCh[0].split('__')[3], "squash_expA_md"))
        self.md_squash_expA_node.operation.set(3)

        self.md_squash_expB_node = pm.shadingNode('multiplyDivide',asUtility=1, n=(self.IKjointsCh[0]).replace(self.IKjointsCh[0].split('__')[3], "squash_expB_md"))
        self.md_squash_expB_node.operation.set(3)
        
        self.md_squash_expC_node = pm.shadingNode('multiplyDivide',asUtility=1, n=(self.IKjointsCh[0]).replace(self.IKjointsCh[0].split('__')[3], "squash_expC_md"))
        self.md_squash_expC_node.operation.set(3)
                
        ## connections for squash
        self.DistanceLoc.distance >> self.md_squash_node.input2X
        
        self.md_squash_node.outputX >> self.md_squash_expA_node.input1X
        self.md_squash_node.outputX >> self.md_squash_expB_node.input1X
        self.md_squash_node.outputX >> self.md_squash_expC_node.input1X
        
        self.ikfk_ctrl.ExpA >> self.bc_squash_node.color1R
        self.ikfk_ctrl.ExpB >> self.bc_squash_node.color1G
        self.ikfk_ctrl.ExpC >> self.bc_squash_node.color1B  
                                                                                                                                                    
        self.bc_squash_node.outputR >> self.md_squash_expA_node.input2X
        self.bc_squash_node.outputG >> self.md_squash_expB_node.input2X
        self.bc_squash_node.outputB >> self.md_squash_expC_node.input2X                                     

        self.IKFK_ctrl_VolumePreserve_param = self.initial_ctrl.name() + ".Volume_Preservation"
        pm.PyNode(self.IKFK_ctrl_VolumePreserve_param) >> self.bc_squash_node.blender     

        ## Connection Exp A B C
        self.UpFoll = self.follicules_skin_joints[1:3]
        self.MidFoll = self.follicules_skin_joints[3:17]
        self.LowFoll = self.follicules_skin_joints[17:]

        for each in self.UpFoll:
            pm.PyNode(self.md_squash_expA_node).outputX >> pm.PyNode(each).scaleY
            pm.PyNode(self.md_squash_expA_node).outputX >> pm.PyNode(each).scaleZ

        for each in self.MidFoll:
            pm.PyNode(self.md_squash_expB_node).outputX >> pm.PyNode(each).scaleY
            pm.PyNode(self.md_squash_expB_node).outputX >> pm.PyNode(each).scaleZ

        for each in self.LowFoll:
            pm.PyNode(self.md_squash_expC_node).outputX >> pm.PyNode(each).scaleY
            pm.PyNode(self.md_squash_expC_node).outputX >> pm.PyNode(each).scaleZ                                                                                                                        
                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
    def cleanUp_grp(self):
        """ creating oRoot grp and final cleanup"""
        side = self.getSide(self.guide_result_leg_chain[0])
        rigging_grp = pm.group(n='{Side}__{Basename}__Rig_sys__grp__'.format(**self.nameStructure), em = True)          
        joints_grp = pm.group(n='{Side}__{Basename}__Joints__grp__'.format(**self.nameStructure), em = True)          
        self.oRoot_grp = pm.group(n='{Side}__{Basename}__Root__grp__'.format(**self.nameStructure), em = True)          
        
        pm.parent(self.main_strech_grp,
                  self.pole_vector_ctrl[0].getParent(),
                  self.initial_ctrl.getParent(),
                  self.FKcontrols[0].getParent(),
                  self.sliding_knee_root_grp,
                  self.gr_world_offset ,
                  self.pv_curve ,
                  rigging_grp
                  )   
                  
        pm.parent(self.follicules_offset_root_grp,
                  self.bind_joints_plane_offset_grp,
                  self.guide_result_leg_chain[0],
                  joints_grp
                  )                   
                                                      
        pm.parent(self.ik_sys_grp, 
                  self.slidingKnee_sys_grp,
                  rigging_grp,
                  joints_grp,
                  self.oRoot_grp
                  ) 

        ## set all joints to Drawstyle to None
        pm.select(pm.listRelatives(self.oRoot_grp,allDescendents=True), r = True)
        adb.selectType('joint')
        [x.v.set(0) for x in pm.selected()]
        
        # Except...
        [x.v.set(1) for x in self.guide_result_leg_chain]
        [x.v.set(1) for x in self.follicules_skin_joints]

        return self.oRoot_grp
                                              
    def set_settingGrp(self):
        """Fulfill the Leg_setting_ik_grp """
        
        ## IK sys
        pm.PyNode(self.ikHandle_stretch).translate >> pm.PyNode(self.ik_sys_grp).Ik_Handle 
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
        
        ## Sliding Knee sys
        pm.PyNode(self.sliding_knee).translate >> self.slidingKnee_sys_grp.Slinding_Knee_Control
        pm.PyNode(self.locs_top[0]).translate >> self.slidingKnee_sys_grp.Top_Loc_Control
        pm.PyNode(self.locs_bot[-1]).translate >> self.slidingKnee_sys_grp.Bot_Loc_Control
              

# ===================================================
    
    #-----------------------------------
    # FUNCTIONS Repeated
    #-----------------------------------
    
    
    class FUNCTIONS_REPEATED():
        def __init__():
            pass 


    def getSide(self,sub):
        """ Find the side according to the selection """
        totalBox = pm.PyNode(sub).getBoundingBox()    
        if totalBox.center()[0] > 0.0:
            _side = 'l'
            # print('l')            
        elif totalBox.center()[0] < 0.0:
            _side = 'r'
            # print('r')                
        else:
            _side = 'm'
            # print('m')    
        return _side 

                      
    def fk_shape_setup(self,
                       RadiusCtrl=1,
                       Normalsctrl = (0,1,0),
                       listJoint = pm.selected(),
                       ):
        """Fk chain setUp by parenting the shape to the joint """        
        def CreateCircles():
            CurveColl = []
            for joint in listJoint:

                myname = '{}'.format(joint)
                new_name = myname.split('__jnt__')[0] + '__ctrl__'
                    
                curve = pm.circle(nr=Normalsctrl, r = RadiusCtrl )
                curveShape = pm.PyNode(curve[0]).getShape()
                CurveColl.extend(curve)
                
                tras = pm.xform(joint, ws=True, q=True, t=True)
                pivot = pm.xform(joint, ws=True, q=True, rp=True)
                
                pm.xform(curve, ws=True, t=tras, rp=pivot)                
                pm.parent(curveShape,joint, r=True, s=True)                
                pm.delete(curve)                
                pm.rename(joint,new_name)
        
            return(listJoint)

        
        def makeroot_func(subject = pm.selected()):
            pm.select(subject)
            oColl = pm.selected()
            newSuffix = 'root__grp'
            
            for each in oColl:
                try:
                    suffix = each.name().split('__')[-2]
                    cutsuffix = '__{}__'.format(suffix)
                except:
                    suffix, cutsuffix = '', ''
                oRoot = pm.group(n=each.name().replace(cutsuffix,'') + '_{}__{}__'.format(suffix, newSuffix), em=True)

                for i in xrange(4):
                    oRoot.rename(oRoot.name().replace('___','__'))
                oRoot.setTranslation(each.getTranslation(space='world'), space='world')
                oRoot.setRotation(each.getRotation(space='world'), space='world')
                try:
                    pm.parent(oRoot, each.getParent())
                except:
                    pass
                pm.parent(each, oRoot)
                pm.setAttr(oRoot.v, keyable=False, cb=False)
                # oRoot.v.lock()
            pm.select(oRoot)
            return oRoot
                           
        #-----------------------------------
        #   BUILD Fk Shape SetUp
        #-----------------------------------
     
        controls =  CreateCircles()
        adb.makeroot_func(controls)    
        return(controls)


 
# -----------------------------------
#   IN CLASS BUILD
# # -----------------------------------
# rightLeg = LegSetUp(['joint1', 'joint2', 'joint3'] )
# leftLeg = LegSetUp(['joint4', 'joint5', 'joint6'] )



#-----------------------------------
#   EXEMPLE  EXTERIOR CLASS BUIL
#-----------------------------------

# import adb_rig.Class__Leg_setUp as adb_leg
# reload(adb_rig.Class__Leg_setUp)  

    
# rightLeg = adb_leg.LegSetUp(['joint1', 'joint2', 'joint3'] )
# leftLeg = adb_leg.LegSetUp(['joint1', 'joint2', 'joint3'] )

