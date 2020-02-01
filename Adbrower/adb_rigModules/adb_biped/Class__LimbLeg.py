# ------------------------------------------------------
# Auto Rig Leg SetUp
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import sys

import pymel.core as pm

import ShapesLibrary as sl
import adbrower
adb = adbrower.Adbrower()
 
import adb_core.ModuleBase as moduleBase
import adb_core.NameConv_utils as NC
import adb_core.Class__AddAttr as adbAttr
from adb_core.Class__Transforms import Transform
from adb_core.Class__Joint import Joint

import adb_library.adb_utils.Func__Piston as adbPiston
import adb_library.adb_utils.Script__LocGenerator as locGen
import adb_library.adb_utils.Script__ProxyPlane as adbProxy
import adb_library.adb_utils.Class__FkShapes as adbFKShape

import adb_library.adb_modules.Module__Folli as adbFolli
import adb_rigModules.RigBase as RigBase

reload(RigBase)
reload(adbAttr)
reload(adbFKShape)
reload(NC)

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

class LimbLegModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(LimbLegModel, self).__init__()
        pass
        
        
class LimbLeg(moduleBase.ModuleBase):       
    """
    """
    def __init__(self,
                module_name=None,
                pole_vector_shape=None,
                plane_proxy_axis=None,
                output_joint_radius=1,
                ):
        super(LimbLeg, self).__init__()
        
        self.nameStructure = None
        
        self._MODEL = LimbLegModel()
        
        self.NAME = module_name
        self.output_joint_radius = output_joint_radius
        
    def __repr__(self):
        return str('{} : {} \n {}'.format(self.__class__.__name__, self.subject, self.__class__))    
        
        
    # =========================
    # METHOD
    # =========================        
        
    def start(self, _metaDataNode = 'transform'):
        super(LimbLeg, self)._start(metaDataNode = _metaDataNode)          
        
        # TODO: Create Guide setup
        
    def build(self, GUIDES):
        """      
        @param GUIDE: List of 3
          
         Get starting Info
             - Side Info
        
        CREATE BASE CHAIN
        
         Ik-FK SWITCH SYSTEM
             - Create IK-FK Switch Control 
             - Create Ik Controls & system
             - Create Fk Controls & system
             - Create blend 
            
         STRETCHY LIMB
            # - Ribbon
            
         SLIDING KNEE
             - Create control
        """
        super(LimbLeg, self)._build()   
        
        self.RIG = RigBase.RigBase()
        
        self.starter_Leg = GUIDES
        
        self.side = NC.getSideFromPosition(GUIDES[0])

        if self.side == 'R':
            self.col_main = 13
            self.pol_vector_col = (0.5, 0.000, 0.000)
            self.sliding_knee_col = 4
        
        else:
            self.col_main = 6 
            self.pol_vector_col = (0, 0.145, 0.588)
            self.sliding_knee_col = 5

        self.nameStructure = {
                            'Side':self.side,
                            'Basename': 'Leg',
                            'Parts': ['Hips', 'Knee', 'Ankle'],
                            'Suffix':''
                            }
    
        # =================
        # BUILD
            
        self.createBaseLegJoints()
        self.ik_fk_system()
            
        
    # =========================
    # SOLVERS
    # =========================    
          
    def createBaseLegJoints(self):
        """
        Create basic 3 joints base leg chain
        """
        pm.select(None)
        self.base_leg_joints = [pm.joint(rad = self.output_joint_radius) for x in range(len(self.starter_Leg))]
        for joint in self.base_leg_joints:
            pm.parent(joint, w=True)
        
        for joint, guide in zip(self.base_leg_joints, self.starter_Leg):
            pm.matchTransform(joint,guide, pos=True)        

        ## Parenting the joints          
        for oParent, oChild in zip(self.base_leg_joints[0:-1], self.base_leg_joints[1:]):
            pm.parent(oChild, None)
            pm.parent(oChild, oParent)

        pm.PyNode(self.base_leg_joints[0]).rename('{Side}__{Basename}_Base_{Parts[0]}'.format(**self.nameStructure))
        pm.PyNode(self.base_leg_joints[1]).rename('{Side}__{Basename}_Base_{Parts[1]}'.format(**self.nameStructure))
        pm.PyNode(self.base_leg_joints[2]).rename('{Side}__{Basename}_Base_{Parts[2]}'.format(**self.nameStructure))
        
        adb.AutoSuffix(self.base_leg_joints)
        
        ## orient joint                        
        if self.side == NC.RIGTH_SIDE_PREFIX:   
            mirror_chain_1 = pm.mirrorJoint(self.base_leg_joints[0], mirrorYZ=1)
            Joint(mirror_chain_1).orientAxis = 'Y'
            
            mirror_chain_3 = pm.mirrorJoint(mirror_chain_1[0] ,mirrorBehavior=1, mirrorYZ=1)                
            pm.delete(mirror_chain_1,mirror_chain_1,self.base_leg_joints)
            self.base_leg_joints = [pm.PyNode(x) for x in mirror_chain_3]                
        else:
            Joint(self.base_leg_joints).orientAxis = 'Y'

        def createBaseLegJointsHiearchy():
            baseJnst_grp = pm.group(em=True, name='{Side}__{Basename}_BaseJnts'.format(**self.nameStructure))
            adb.AutoSuffix([baseJnst_grp])
            pm.parent(self.base_leg_joints[0], baseJnst_grp)
            
        createBaseLegJointsHiearchy()
                 
        
    def ik_fk_system(self):
        """
        Create an IK-FK blend system
        """
        
        @changeColor()
        def IkJointChain():
            self.ik_leg_joints = pm.duplicate(self.base_leg_joints)                                
            ## Setter le radius de mes joints ##
            for joint in self.ik_leg_joints:
                joint.radius.set(self.base_leg_joints[0].radius.get() + 0.4)                                

            pm.PyNode(self.ik_leg_joints[0]).rename('{Side}__{Basename}_Ik_{Parts[0]}'.format(**self.nameStructure))
            pm.PyNode(self.ik_leg_joints[1]).rename('{Side}__{Basename}_Ik_{Parts[1]}'.format(**self.nameStructure))
            pm.PyNode(self.ik_leg_joints[2]).rename('{Side}__{Basename}_Ik_{Parts[2]}'.format(**self.nameStructure))
            adb.AutoSuffix(self.ik_leg_joints)
            return self.ik_leg_joints

        @changeColor('index', 14)
        def FkJointChain():
            self.fk_leg_joints = pm.duplicate(self.base_leg_joints)                                
            ## Setter le radius de mes joints ##
            for joint in self.fk_leg_joints:
                joint.radius.set(self.base_leg_joints[0].radius.get() + 0.2)                                

            pm.PyNode(self.fk_leg_joints[0]).rename('{Side}__{Basename}_Fk_{Parts[0]}'.format(**self.nameStructure))
            pm.PyNode(self.fk_leg_joints[1]).rename('{Side}__{Basename}_Fk_{Parts[1]}'.format(**self.nameStructure))
            pm.PyNode(self.fk_leg_joints[2]).rename('{Side}__{Basename}_Fk_{Parts[2]}'.format(**self.nameStructure))
            adb.AutoSuffix(self.fk_leg_joints)
            return self.fk_leg_joints
    
        def createIKFKSwitchControl():
            """Swtich Control options """     
                   
            self.ikfk_ctrl = sl.ik_fk_shape() 
            if self.side == NC.RIGTH_SIDE_PREFIX:
                _shapes = pm.PyNode(self.ikfk_ctrl).getShapes()

                pm.select('{}.cv[:]'.format(_shapes[0]))
                pm.select('{}.cv[:]'.format(_shapes[1]), add=True)
                pm.select('{}.cv[:]'.format(_shapes[2]), add=True)
                pm.select('{}.cv[:]'.format(_shapes[3]), add=True)
                
                pm.move(-3, 0, 0, r=1, os=1, wd=1)
            
            else:
                pass
                
            pm.matchTransform(self.ikfk_ctrl,self.base_leg_joints[-1], pos=True)
            adb.makeroot_func(self.ikfk_ctrl)
                                        
            CtrlName = '{Side}__{Basename}_Options'.format(**self.nameStructure)
            self.ikfk_ctrl.rename(CtrlName)
            adb.AutoSuffix([self.ikfk_ctrl])
            self.ikfk_ctrl.addAttr('IK_FK_Switch', keyable=True, attributeType='enum', en="IK:FK") 
        
        def makeConnections():
            self.addIkFKSpaceAttributes(self.RIG.SPACES_GRP)
            self.blendSystem(ctrl_name = self.RIG.SPACES_GRP,
                            blend_attribute = '{}_spaces'.format(self.side),
                            result_joints = self.base_leg_joints,
                            ik_joints = self.ik_leg_joints,
                            fk_joints = self.fk_leg_joints,
                            lenght_blend = 1,
                            )

        @changeColor('index', col = self.col_main )
        def CreateFkcontrols(radius = 1, 
                    normalsCtrl=(0,1,0)):
            """Creates the FK controls on the Fk joint chain """  
            FkShapeSetup = adbFKShape.FkShape(self.fk_leg_joints)
            FkShapeSetup.shapeSetup(radius, normalsCtrl)
            return FkShapeSetup.controls

        def CreateIKcontrols(Ikshape = sl.cube_shape, exposant = 40, pvShape = sl.ball_shape):
            
            self.nameStructure['Suffix'] = NC.IKHANDLE_SUFFIX 
            leg_IkHandle = pm.ikHandle( n='{Side}__{Basename}__{Suffix}'.format(**self.nameStructure), sj=self.ik_leg_joints[0], ee=self.ik_leg_joints[-1])
            leg_IkHandle[0].v.set(0)
            pm.select(self.ik_leg_joints[-1], r = True)
            
            @makeroot()
            @changeColor('index', col = self.col_main)        
            def Ik_ctrl():            
                self.nameStructure['Suffix'] = NC.CTRL 
                _leg_IkHandle_ctrl = Ikshape()
                pm.rename(_leg_IkHandle_ctrl, '{Side}__{Basename}__{Suffix}'.format(**self.nameStructure))
                pm.matchTransform(_leg_IkHandle_ctrl, self.ik_leg_joints[-1], pos = True)
                return _leg_IkHandle_ctrl      
            self.leg_IkHandle_ctrl = Ik_ctrl()[0]

            @makeroot()
            @changeColor('index', col = self.col_main ) 
            def Ik_ctrl_offset():
                _leg_IkHandle_ctrl_offset = Ikshape()
                _leg_IkHandle_ctrl_offset.scale.set(0.7, 0.7, 0.7)
                pm.rename(_leg_IkHandle_ctrl_offset, '{Side}__{Basename}_IK_offset__ctrl__'.format(**self.nameStructure) )
                pm.matchTransform(_leg_IkHandle_ctrl_offset, self.ik_leg_joints[-1], pos = True)            
                return _leg_IkHandle_ctrl_offset            
            self.leg_IkHandle_ctrl_offset = Ik_ctrl_offset()[0]  

            @lockAttr(att_to_lock = ['rx','ry','rz','sx','sy','sz'])    
            @changeColor('rgb', col = self.pol_vector_col) 
            @makeroot()  
            def pole_vector_ctrl(name ='{Side}__{Basename}_pv__{Suffix}'.format(**self.nameStructure)):            
                pv_guide = adb.PvGuide(leg_IkHandle[0],self.ik_leg_joints[-2], exposant=exposant)            
                self.poleVectorCtrl = pvShape()
            
                pm.rename(self.poleVectorCtrl,name)            
                last_point = pm.PyNode(pv_guide).getCVs()
                pm.move(self.poleVectorCtrl,last_point[-1])
                pm.poleVectorConstraint(self.poleVectorCtrl,leg_IkHandle[0] ,weight=1)

                def curve_setup():
                    pm.select(self.poleVectorCtrl, r=True)
                    pv_tip_jnt = adb.jointAtCenter()[0]
                    pm.rename(pv_tip_jnt, '{}__pvTip__{}'.format(self.side, NC.JOINT))
                    pm.parent(pv_tip_jnt, self.poleVectorCtrl)
                
                    _loc = pm.spaceLocator(p= adb.getWorldTrans([self.ik_leg_joints[-2]]))
                    mc.CenterPivot()
                    pm.select(_loc, r=True)
                    pv_base_jnt = adb.jointAtCenter()[0]
                    pm.delete(_loc)
                    pm.rename(pv_base_jnt, '{}__pvBase__{}'.format(self.side, NC.JOINT))
                    pm.skinCluster(pv_base_jnt , pv_guide, pv_tip_jnt)
                    pm.parent(pv_base_jnt, self.ik_leg_joints[1])

                    [pm.setAttr('{}.drawStyle'.format(joint),  2) for joint in [pv_tip_jnt, pv_base_jnt]]
                
                curve_setup()
                
                return self.poleVectorCtrl    
           
            pole_vector_ctrl()

            pm.parent(self.leg_IkHandle_ctrl_offset, self.leg_IkHandle_ctrl)
            pm.parent(leg_IkHandle[0], self.leg_IkHandle_ctrl_offset)

        IkJointChain()
        FkJointChain()
        makeConnections()
        CreateFkcontrols()
        CreateIKcontrols()


    def stretchyLimb(self):
        pass

    # =========================
    # SLOTS
    # =========================  

    def blendSystem(self,
                    ctrl_name = '',
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
            # TODO: ADD THE BLEND OPTIONS
            ## add attribute message
            switch_ctrl = adbAttr.NodeAttr([ctrl_name])
            switch_ctrl.addAttr('lenght_blend', lenght_blend, keyable=False)

            ## Creation of the remaps values and blendColor nodes
            BlendColorColl_R = [pm.shadingNode('blendColors', asUtility=1, n='{}__{}_rotate__{}'.format(self.side, NC.getBasename(x), NC.BLENDCOLOR_SUFFIX)) for x in result_joints]
            RemapValueColl = [pm.shadingNode('remapValue',asUtility=1, n='{}__{}__{}'.format(self.side, NC.getBasename(x), NC.REMAP_VALUE_SUFFIX)) for x in result_joints]

            ## Connect the IK in the Color 2
            for oIK, oBlendColor in zip (fk_joints,BlendColorColl_R):
                pm.PyNode(oIK).rx >> pm.PyNode(oBlendColor).color1R
                pm.PyNode(oIK).ry >> pm.PyNode(oBlendColor).color1G
                pm.PyNode(oIK).rz >> pm.PyNode(oBlendColor).color1B

            ## Connect the FK in the Color 1
            for oFK, oBlendColor in zip (ik_joints,BlendColorColl_R):
                pm.PyNode(oFK).rx >> pm.PyNode(oBlendColor).color2R
                pm.PyNode(oFK).ry >> pm.PyNode(oBlendColor).color2G
                pm.PyNode(oFK).rz >> pm.PyNode(oBlendColor).color2B
                                
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


    def addIkFKSpaceAttributes(self, transform):
        switch_ctrl = adbAttr.NodeAttr([transform])
        switch_ctrl.AddSeparator(transform, 'LEGS')
        switch_ctrl.addAttr('{}_spaces'.format(self.side), 'enum',  eName = "IK:FK:")



# =========================
# BUILD
# ========================= 
    
leg = LimbLeg(module_name='L_Leg')

# leg.start()
leg.build(['hip_guide', 'knee_guide', 'ankle_LOC'])
        
        

        
        
        
        
        