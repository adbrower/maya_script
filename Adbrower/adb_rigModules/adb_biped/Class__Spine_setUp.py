# ------------------------------------------------------
# Auto Rig Spine SetUp
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------
import sys
import traceback
import pymel.core as pm
import maya.cmds as mc

#-----------------------------------
# IMPORT CUSTOM MODULES
#----------------------------------- 

import ShapesLibrary as sl
from ShapesLibrary import*

import adbrower
adb = adbrower.Adbrower()
from adbrower import lprint

import adb_library.adb_utils.Script__LocGenerator as adb_PointonCurve

#-----------------------------------
#  DECORATORS
#----------------------------------- 
from adbrower import changeColor
from adbrower import makeroot

import adb_core.Class__Transforms as adbTransform

#-----------------------------------
# CLASS
#----------------------------------- 

class SpineSetUp():
    def __init__(self, guide_spine_loc = pm.selected(), 
                 spine_ctrl_shape = sl.cog_shape,
                 Up_Start = 3,
                 Up_End = -2,
                 
                 Mid_Start = 3,
                 Mid_end = 4,
                 
                 Low_Start = 1,
                 Low_end =3,
                 
                 anglePin = -90,
                 
                 ):
     
        self.guide_spine_loc = [pm.PyNode(x) for x in guide_spine_loc]
        self.spine_ctrl_shape = spine_ctrl_shape
        self.basename = 'Spine'

        self.reg_spine_jnts = None 
        self.rev_spine_jnts = None    
        self.md_rot_list = None
        self.pma_rot_list = None
        self.nurbs_ik_plane = None
        self.anglePin = anglePin
        self.foll_joint = []
                          
        self.create_spine_chain()         
        # self.initial_ctrl = pm.PyNode('') # Nom du controleur existant

        self.initial_ctrl = self.spine_param_ctrl()
        self.createsFkControls()
        self.createsRevFkControls()
        self.createNodes()        
        self.rev_FK_ctrls_offset_rev = self.create_offset_grps()
                
        self.UpRev = self.rev_FK_ctrls_offset_rev[Up_Start:Up_End]
        self.MidRev = self.rev_FK_ctrls_offset_rev[Mid_Start:Mid_end]
        self.LowRev = self.rev_FK_ctrls_offset_rev[Low_Start:Low_end] 
               
        self.makeConnections()
        self.ikSetup()
        
        self.UpFoll = self.foll_joint[Up_Start:Up_End]
        self.MidFoll = self.foll_joint[Mid_Start:Mid_end]
        self.LowFoll = self.foll_joint[Low_Start:Low_end] 
                       
        # self.ik_squash_con()
        
    
    def create_spine_chain(self,type = 'jnt', radius = 0.5 ):  

        #========================
        # FK CHAIN
        #========================
        
        nameStructure = {
         'Side': 'm',
         'Basename': self.basename,
         }

        ## Creating - positionning and renaming the joint         
        pm.select(None)
        self.reg_spine_jnts = [pm.joint(n= '{Side}__{Basename}_fk_01'.format(**nameStructure), rad = radius) for x in range(len(self.guide_spine_loc))]
        for joint in self.reg_spine_jnts:
            pm.parent(joint, w=True)
                                                                                            
        for _joint, guide in zip(self.reg_spine_jnts,self.guide_spine_loc):
            pm.matchTransform(_joint,guide, pos=True)            

        ## Parenting the joints          
        for oParent, oChild in zip(self.reg_spine_jnts[0:-1], self.reg_spine_jnts[1:]):
            pm.parent(oChild, None)
            pm.parent(oChild, oParent)     

        ## orient joint
        pm.joint(self.reg_spine_jnts, zso=1, ch=1, e=1, oj='yxz', secondaryAxisOrient='xdown')
        pm.joint(self.reg_spine_jnts[-1], e=1, oj='none')
                
        adb.AutoSuffix(self.reg_spine_jnts)
                    
        #========================
        # REV FK CHAIN
        #========================
        
        @changeColor('index', col = (23))
        def fk_rev():
            self.rev_spine_jnts = [pm.joint(n='{Side}__{Basename}_rev_fk_01'.format(**nameStructure), rad = radius-0.2) for x in range(len(self.guide_spine_loc))]
            for joint in self.rev_spine_jnts:
                pm.parent(joint, w=True)
                                        
            for _joint, guide in zip(self.rev_spine_jnts,self.guide_spine_loc):
                pm.matchTransform(_joint,guide, pos=True)    

            self.rev_spine_jnts_reverse = self.rev_spine_jnts[::-1][1:]
            ## Parenting the joints          
            for oParent, oChild in zip(self.rev_spine_jnts_reverse[:-1], self.rev_spine_jnts_reverse[1:]):
                pm.parent(oChild, None)
                pm.parent(oChild, oParent)
                    
            pm.parent(self.rev_spine_jnts_reverse[0],self.rev_spine_jnts[-1])            
            adb.AutoSuffix(self.rev_spine_jnts)             
            pm.parent(self.rev_spine_jnts[-1],self.reg_spine_jnts[-1])                                                       
            return self.rev_spine_jnts
        fk_rev()

                
    def spine_param_ctrl(self, type = 'ctrl', scale = 1, expA = 1.25, expB=1.5, expC=1.25):
        @changeColor('index', col = 3)
        def create_ctrl_shape(scale=scale):
            nameStructure = {
                     'Side':'m',
                     'Basename': self.basename, 
                     'Type':type,
                     }    
            _spine_param_ctrl = self.spine_ctrl_shape()
            CtrlName = '{Side}__{Basename}_Options__{Type}'.format(**nameStructure)
            _spine_param_ctrl.rename(CtrlName)
            _spine_param_ctrl.scaleX.set(scale)
            _spine_param_ctrl.scaleY.set(scale)
            _spine_param_ctrl.scaleZ.set(scale)
            pm.select(_spine_param_ctrl)
            mc.FreezeTransformations()
             
            _spine_param_ctrl.setTranslation(pm.xform(self.guide_spine_loc[0], ws=True, q=True, t=True))
              
            _shapes = pm.PyNode(_spine_param_ctrl).getShapes()
            pm.select('{}.cv[:]'.format(_shapes[0]),r=True)
            for x in range(1,(len(_shapes))):
                pm.select('{}.cv[:]'.format(_shapes[x]),add=True) 
            pm.move(3, 0, 0, r=1, os=1, wd=1) 
            pm.rotate( 0, 90, 0)  
                                                                       
            return _spine_param_ctrl

        self.spine_param_ctrl = create_ctrl_shape()

        ## Add custom attribute
        
        pm.PyNode(self.spine_param_ctrl).addAttr('_visibility',keyable=True, en='Options', at="enum", nn='Visibility Controls')
        pm.PyNode(self.spine_param_ctrl).setAttr("_visibility", lock=True)

        pm.PyNode(self.spine_param_ctrl).addAttr('Fk', keyable=True, at='bool', dv = 1)
        pm.PyNode(self.spine_param_ctrl).addAttr('Ik', keyable=True, at='bool', dv=1)
        pm.PyNode(self.spine_param_ctrl).addAttr('Fk_Reverse', keyable=True, at='bool')
        
        
        pm.PyNode(self.spine_param_ctrl).addAttr('Squash_and_Stretch',keyable=True, en='Options', at="enum", nn='Squash and Stretch')
        pm.PyNode(self.spine_param_ctrl).setAttr("Squash_and_Stretch", lock=True)

        pm.PyNode(self.spine_param_ctrl).addAttr('ExpA', keyable=True, dv= expA, at='double')
        pm.PyNode(self.spine_param_ctrl).addAttr('ExpB', keyable=True, dv= expB, at='double')
        pm.PyNode(self.spine_param_ctrl).addAttr('ExpC', keyable=True, dv= expC, at='double')

        
        pm.PyNode(self.spine_param_ctrl).addAttr('Fk_Bend',keyable=True, en='Options', at="enum", nn='Regular Fk Bend')
        pm.PyNode(self.spine_param_ctrl).setAttr("Fk_Bend", lock=True)

        pm.PyNode(self.spine_param_ctrl).addAttr('Bend', keyable=True, attributeType='double')
        pm.PyNode(self.spine_param_ctrl).addAttr('Position', keyable=True, attributeType='double',dv=1, min=1, max = (len(self.guide_spine_loc)+1) )
        pm.PyNode(self.spine_param_ctrl).addAttr('Falloff', keyable=True, attributeType='double', min = 0, max =(len(self.guide_spine_loc)))

            
        pm.PyNode(self.spine_param_ctrl).addAttr('Reverse_Fk_Bend',keyable=True, en='Options', at="enum", nn='Reverse Fk Bend')
        pm.PyNode(self.spine_param_ctrl).setAttr("Reverse_Fk_Bend", lock=True)
                
        pm.PyNode(self.spine_param_ctrl).addAttr('BendUpRev', keyable=True, attributeType='double')
        pm.PyNode(self.spine_param_ctrl).addAttr('BendMidRev', keyable=True, attributeType='double')
        pm.PyNode(self.spine_param_ctrl).addAttr('BendLowRev', keyable=True, attributeType='double')

        ## Lock and Hide all parameters #
        pm.PyNode(self.spine_param_ctrl).setAttr("tx", lock=True, channelBox=False, keyable=False)
        pm.PyNode(self.spine_param_ctrl).setAttr("ty", lock=True, channelBox=False, keyable=False)
        pm.PyNode(self.spine_param_ctrl).setAttr("tz", lock=True, channelBox=False, keyable=False)
        pm.PyNode(self.spine_param_ctrl).setAttr("rx", lock=True, channelBox=False, keyable=False)
        pm.PyNode(self.spine_param_ctrl).setAttr("ry", lock=True, channelBox=False, keyable=False)
        pm.PyNode(self.spine_param_ctrl).setAttr("rz", lock=True, channelBox=False, keyable=False)
        pm.PyNode(self.spine_param_ctrl).setAttr("sx", lock=True, channelBox=False, keyable=False)
        pm.PyNode(self.spine_param_ctrl).setAttr("sy", lock=True, channelBox=False, keyable=False)
        pm.PyNode(self.spine_param_ctrl).setAttr("sz", lock=True, channelBox=False, keyable=False)
        pm.PyNode(self.spine_param_ctrl).setAttr("v", lock=True, channelBox=False, keyable=False)
        
        return self.spine_param_ctrl

    
    @changeColor(col = (1,1,0.236))
    def createsFkControls(self):
        self.reg_FK_ctrls = self.fk_pin_shape_setup(listJoint = self.reg_spine_jnts )       

        ## set visibility
        shapes = [x.getShape() for x in self.reg_FK_ctrls]
        fk_vis = self.initial_ctrl.name() + ".Fk"       
        for each in shapes:
            pm.PyNode(fk_vis) >> each.visibility 
        
        return self.reg_FK_ctrls


    @changeColor(col = (0,0,1))
    def createsRevFkControls(self):
        _temp_reverse_rev_spine_jnts =  self.rev_spine_jnts[::-1]
        self.rev_fk_ctrls = self.fk_shape_setup(listJoint = _temp_reverse_rev_spine_jnts, radius=1, Normalsctrl = (0,1,0) )       
                
        ## set visibility        
        shapes = [x.getShape() for x in self.rev_fk_ctrls]
        fk_rev_vis = self.initial_ctrl.name() + ".Fk_Reverse"

        for each in shapes:
            pm.PyNode(fk_rev_vis) >> each.visibility 
        return self.rev_fk_ctrls


    def createNodes(self):        
        ## Creation of the multiply Divide Nodes
        self.md_rot_list = [pm.shadingNode('multiplyDivide', asUtility = 1, n =(x).replace(x.split('__')[2], 'reg_to_rev_rot_md')) for x in self.reg_spine_jnts]        
        for node in self.md_rot_list:
            node.operation.set(1)
            node.input2X.set(-1)         
            node.input2Y.set(-1)         
            node.input2Z.set(-1)     
            
        self.md_rot_list_offset_reg = [pm.shadingNode('multiplyDivide', asUtility = 1, n =(x).replace(x.split('__')[2], 'offset_reg_rot_md')) for x in self.reg_spine_jnts]        
        for node in self.md_rot_list_offset_reg:
            node.operation.set(1)
            node.input2X.set(-1)         
            node.input2Y.set(-1)         
            node.input2Z.set(-1)     

        self.md_trans_list = [pm.shadingNode('multiplyDivide', asUtility = 1, n =(x).replace(x.split('__')[2], 'reg_to_rev_trans_md')) for x in self.reg_spine_jnts]        
        for node in self.md_trans_list:
            node.operation.set(1)
            node.input2X.set(-1)         
            node.input2Y.set(-1)         
            node.input2Z.set(-1)     

        self.md_fallof_list = pm.shadingNode('multiplyDivide', asUtility = 1, n =(x).replace(x.split('__')[2], 'fallof_md'))
        self.md_fallof_list.operation.set(1)
        self.md_fallof_list.input2X.set(-1)         
        self.md_fallof_list.input2Y.set(-1)         
        self.md_fallof_list.input2Z.set(-1)          
        
        self.pma_fallof_list = [pm.shadingNode('plusMinusAverage', asUtility = 1, n =(x).replace(x.split('__')[2], 'fallof_pma')) for x in self.reg_spine_jnts]
        
        self.pma_fallof_list[0].input3D[0].input3Dx.set(0)
        self.pma_fallof_list[0].input3D[0].input3Dy.set(2)

        for index,node in enumerate(self.pma_fallof_list[1:]):
            node.input3D[0].input3Dx.set(index+1)
            getAtt = node.input3D[0].input3Dx.get()
            node.input3D[0].input3Dy.set(getAtt+2)
        
        
        self.md_bend_list = [pm.shadingNode('multiplyDivide', asUtility = 1, n =(x).replace(x.split('__')[2], 'ben_md')) for x in self.reg_spine_jnts]
        
        self.rm_position_list = [pm.shadingNode('remapValue', asUtility = 1, n =(x).replace(x.split('__')[2], 'position_rm')) for x in self.reg_spine_jnts]
        for node in self.rm_position_list:
            node.value[1].value_FloatValue.set(1)
            node.value[1].value_Position.set(0.5)

            node.value[2].value_FloatValue.set(0)
            node.value[2].value_Position.set(1)


    def create_offset_grps(self):
        self.reg_FK_ctrls_offset_reg = [self.makeroot_func(subject = x, suff = 'offset_reg_bend' ) for x in self.reg_spine_jnts]
        self.makeroot_func(subject = self.rev_spine_jnts, suff = 'offset')
        self.rev_joint_offset = [self.makeroot_func(subject = x, suff = 'offset_rot_trans') for x in self.rev_spine_jnts]
        self.reg_FK_ctrls_offset_rev = [self.makeroot_func(subject = x, suff = 'offset_reg_bend' ) for x in self.rev_spine_jnts]
        self.rev_FK_ctrls_offset_rev = [self.makeroot_func(subject = x, suff = 'offset_rev_bend' ) for x in self.rev_spine_jnts]
        
        return(self.rev_FK_ctrls_offset_rev)


    def makeConnections(self):
        """ Connections for the fk reverse set up """
               
        ## set orientation order for all groups for rev chain
        for each in self.rev_FK_ctrls_offset_rev:
            pm.PyNode(each).rotateOrder.set(5)

        for each in self.reg_FK_ctrls_offset_rev:
            pm.PyNode(each).rotateOrder.set(5)

        for each in self.rev_joint_offset:
            pm.PyNode(each).rotateOrder.set(5)

        ## Connect the Fk joint rotation to the multiply Divide rot
        for oDriver, oTargets in zip (self.reg_spine_jnts,self.md_rot_list):
            pm.PyNode(oDriver).rotateX >> pm.PyNode(oTargets).input1X
            pm.PyNode(oDriver).rotateY >> pm.PyNode(oTargets).input1Y
            pm.PyNode(oDriver).rotateZ >> pm.PyNode(oTargets).input1Z

        ## Connect the multiply Divide rot to fk rev group rot
        for oDriver, oTargets in zip (self.md_rot_list,self.rev_joint_offset):
            pm.PyNode(oDriver).outputX >> pm.PyNode(oTargets).rotateX
            pm.PyNode(oDriver).outputY >> pm.PyNode(oTargets).rotateY
            pm.PyNode(oDriver).outputZ >> pm.PyNode(oTargets).rotateZ

        ## Connect the Fk joint translation to the multiply Divide trans
        for oDriver, oTargets in zip (self.reg_spine_jnts,self.md_trans_list):
            pm.PyNode(oDriver).tx >> pm.PyNode(oTargets).input1X
            pm.PyNode(oDriver).ty >> pm.PyNode(oTargets).input1Y
            pm.PyNode(oDriver).tz >> pm.PyNode(oTargets).input1Z
       
        # ## Connect the multiply Divide translation to fk rev group trans
        for oDriver, oTargets in zip (self.md_trans_list[1:], self.rev_joint_offset):
            pm.PyNode(oDriver).outputX >> pm.PyNode(oTargets).tx
            pm.PyNode(oDriver).outputY >> pm.PyNode(oTargets).ty
            pm.PyNode(oDriver).outputZ >> pm.PyNode(oTargets).tz

        ## Connect the offset reg and rev groups together
        for oDriver, oTargets in zip (self.reg_FK_ctrls_offset_reg ,self.md_rot_list_offset_reg):
            pm.PyNode(oDriver).rx >> pm.PyNode(oTargets).input1X
      
        for oDriver, oTargets in zip (self.md_rot_list_offset_reg, self.reg_FK_ctrls_offset_rev):
            pm.PyNode(oDriver).outputX >> pm.PyNode(oTargets).rx
     
        ## Connect spine control to the offset groups
        self.ParamBend = self.initial_ctrl.name() + ".Bend"
        self.ParamPos = self.initial_ctrl.name() + ".Position"
        self.ParamFall = self.initial_ctrl.name() + ".Falloff"


        pm.PyNode(self.ParamFall) >> self.md_fallof_list.input1X     
               
        for node in self.md_bend_list:
            pm.PyNode(self.ParamBend) >> node.input1X   
                   
        for node in self.pma_fallof_list:
            pm.PyNode(self.ParamFall) >> node.input3D[1].input3Dy

        for node in self.rm_position_list:
            pm.PyNode(self.ParamPos) >> node.inputValue     

        for node in self.pma_fallof_list:
            self.md_fallof_list.outputX  >> node.input3D[1].input3Dx


        for driver, target in zip(self.pma_fallof_list,self.rm_position_list):
            driver.output3Dx >> target.inputMin
            driver.output3Dy >> target.inputMax
   
        for driver, target in zip(self.rm_position_list,self.md_bend_list):
            driver.outValue  >> target.input2X


        for driver, target in zip(self.md_bend_list,self.reg_FK_ctrls_offset_reg):
            driver.outputX  >> target.rotateX

        ## Connect spine control ReV bend
        self.ParamUpRev = self.initial_ctrl.name() + ".BendUpRev"
        self.ParamMiRev = self.initial_ctrl.name() + ".BendMidRev"
        self.ParamLoRev = self.initial_ctrl.name() + ".BendLowRev"
        
        ## Rev FK Bend Up
        for each in self.UpRev:
            pm.PyNode(self.ParamUpRev) >> pm.PyNode(each).rx
        
        for each in self.MidRev:
            pm.PyNode(self.ParamMiRev) >> pm.PyNode(each).rx

        for each in self.LowRev:
            pm.PyNode(self.ParamLoRev) >> pm.PyNode(each).rx

        
    def ikSetup(self):
                
        @changeColor(col=(0.272, 0.272, 0.272) )
        def createIkcurve():
            pos = [pm.xform(x, ws=True, q=True, t=True) for x in self.reg_FK_ctrls]

            knot = []
            for i in range(len(self.reg_FK_ctrls)):
                knot.append(i)

            _curve = pm.curve(p = pos, k =knot, d=1, n='m__spine_ik__curve__')
            return(_curve)
                
        self.spineIk_curve = createIkcurve()
        self.spineIk_curve_shape = self.spineIk_curve.getShape()

        _dup1 = pm.duplicate(self.spineIk_curve)
        _dup2 = pm.duplicate(self.spineIk_curve)
        pm.move(0.5, 0, 0,_dup1,  r=1, os=1, wd=1)
        pm.move(-0.5, 0, 0,_dup2,  r=1, os=1, wd=1)
        
        pm.rebuildCurve(self.spineIk_curve, rt=0, ch=0, end=1, d=3, kr=0, s=len(self.reg_FK_ctrls), kcp=0, tol=0.1, kt=0, rpo=1, kep=1)
        pm.rebuildCurve(_dup1, rt=0, ch=0, end=1, d=3, kr=0, s=len(self.reg_FK_ctrls), kcp=0, tol=0.1, kt=0, rpo=1, kep=1)
        pm.rebuildCurve(_dup2, rt=0, ch=0, end=1, d=3, kr=0, s=len(self.reg_FK_ctrls), kcp=0, tol=0.1, kt=0, rpo=1, kep=1)
        
        _nurbs_ik_plane = pm.loft(_dup1, _dup2, c=0, ch=0, d=3, ss=1, rsn=True, ar=1, u=1, rn=0, po=0)
        pm.nurbsToPoly(_nurbs_ik_plane, n='m__spine__ik_proxy_plane_skin', uss=1, ch=0, ft=0.01, d=0.1, pt=1, f=2, mrt=0, mel=0.001, ntr=0, vn=1, pc=100, chr=0.1, un=len(pm.PyNode(_dup2[0]).getShape().getCVs()), 
        vt=1, ut=1, ucr=0, cht=0.2, mnd=1, es=0, uch=0)
        
        self.nurbs_ik_plane = 'm__spine__ik_proxy_plane_skin'
        # pm.rename(self.nurbs_ik_plane, 'm__spine_ik_plane__nurbs__')
        pm.delete(_dup1)
        pm.delete(_dup2)
        pm.delete(_nurbs_ik_plane)
        
        ##  set follicules
        
        self.foll = self.Folli(myObject = self.nurbs_ik_plane , radius = self.reg_spine_jnts[0].radius.get()-0.3, countV = len(self.reg_FK_ctrls))

                
        @changeColor(col=(0.540, 0.286, 0.325))
        def create_ik_jnts(basename = 'spine_ik',type ='jnt'):
            """creates the ik joints"""
             
            self.all_ik_jnts = []            
            nameStructure = {
             'Side': 'm',
             'Basename': self.basename,
             'Type':type,
             }
            
            self.bot_ik_jnt = pm.joint(p = pm.xform(self.reg_FK_ctrls[0], ws=True, q=True, t=True), rad = self.reg_spine_jnts[0].radius.get()+0.2, 
                                       n = '{Side}__{Basename}_ik_bot__{Type}__'.format(**nameStructure))
            self.all_ik_jnts.append(self.bot_ik_jnt)
            
            self.mid_ik_jnt = pm.joint(p = pm.xform(self.guide_spine_loc[((len(self.guide_spine_loc)-1)/2)], ws=True, q=True, t=True), rad = self.reg_spine_jnts[0].radius.get()+0.2,
                                       n = '{Side}__{Basename}_ik_mid__{Type}__'.format(**nameStructure))
            self.all_ik_jnts.append(self.mid_ik_jnt)
                                  
            self.top_ik_jnt = pm.joint(p = pm.xform(self.reg_FK_ctrls[-1], ws=True, q=True, t=True), rad = self.reg_spine_jnts[0].radius.get()+0.2,
                                       n = '{Side}__{Basename}_ik_top__{Type}__'.format(**nameStructure))
            self.all_ik_jnts.append(self.top_ik_jnt)
            
            pm.parent(self.bot_ik_jnt, w=True)
            pm.parent(self.mid_ik_jnt, w=True)
            pm.parent(self.top_ik_jnt, w=True)
                        
            return (self.all_ik_jnts)
      
        @changeColor(col=(0.540, 0.286, 0.325))
        @makeroot()
        def create_ik_ctrls(scale = 2.3):
            self.create_ik_ctrls = [sl.rectangle_shape() for x in self.all_ik_jnts]
            
            for ctrl, jnt in zip(self.create_ik_ctrls, self.all_ik_jnts) :
                ctrl.scaleX.set(scale)
                ctrl.scaleY.set(scale)
                ctrl.scaleZ.set(scale)
                
                pm.matchTransform(ctrl, jnt, pos=True, rot=True)                 
                pm.rename(ctrl,jnt.name().replace('jnt','ctrl'))
                pm.parent(jnt,ctrl)  
                                    
            fk_rev_vis = self.initial_ctrl.name() + ".Ik"

            for each in self.create_ik_ctrls:
                pm.PyNode(fk_rev_vis) >> each.visibility 
                                   
            return self.create_ik_ctrls

        nameStructure = {
         'Side': 'm',
         'Basename': self.basename,
         }

        
        # ## Bind curve jont
        self.bind_curve_jnt = [pm.joint(rad = self.foll_joint[0].radius.get()-0.5) for x in self.guide_spine_loc]        
        [pm.rename(x,'{[Side]}__{[Basename]}_skin_ikcurve_0{}'.format(nameStructure, nameStructure,index+1)) for index, x in enumerate(self.bind_curve_jnt)]
        for driver, joint in zip(self.foll_joint, self.bind_curve_jnt):
            pm.parent(joint, driver.getParent()) 
            pm.matchTransform(joint,driver, pos=True) 
            joint.drawStyle.set(2)           

        [pm.rename(x,'{[Side]}__{[Basename]}_folli_0{}'.format(nameStructure, nameStructure,index+1)) for index, x in enumerate(self.foll_joint)]
        [pm.rename(x, '{}__skn__'.format(x)) for x in self.foll_joint]      
        adb.AutoSuffix(self.bind_curve_jnt)
        pm.skinCluster(self.bind_curve_jnt, self.spineIk_curve)
            
     
        def ik_squash(expA, expB, expC):

            ## Creation des nodes Multiply Divide
            self.CurveInfoNode = pm.shadingNode('curveInfo',asUtility=1, n="IK_curve_CurveInfo")
            self.Stretch_MD = pm.shadingNode('multiplyDivide', asUtility = 1 , n = "StretchMult")
            self.Squash_MD = pm.shadingNode('multiplyDivide', asUtility = 1 , n = "SquashMult")
            
            self.expA_MD = pm.shadingNode('multiplyDivide', asUtility = 1 , n = "ExpA")
            self.expB_MD = pm.shadingNode('multiplyDivide', asUtility = 1 , n = "ExpB")
            self.expC_MD = pm.shadingNode('multiplyDivide', asUtility = 1 , n = "ExpC")
            
            ## Settings des nodes Multiply Divide
            self.Stretch_MD.operation.set(2)
            self.Squash_MD.operation.set(2)
            
            self.expA_MD.operation.set(3)
            self.expA_MD.input1X.set(1)
            
            self.expB_MD.operation.set(3)
            self.expB_MD.input1X.set(1)
                   
            self.expC_MD.operation.set(3)
            self.expC_MD.input1X.set(1)
            
            self.spineIk_curve_shape.worldSpace[0] >>  self.CurveInfoNode.inputCurve  
            distance = self.CurveInfoNode.arcLength.get() 
            
            self.Stretch_MD.input2X.set(distance) 
            self.Squash_MD.input1X.set(distance)    
            
            # Connections
            # Distance >> StretchMult
            self.CurveInfoNode.arcLength >> self.Stretch_MD.input1X
               
            ## StretchMult >> All scale X of each joint       
            for each in self.foll_joint[1:-2]:
                self.Stretch_MD.outputX >> pm.PyNode(each).scaleX
     
            ## Distance >> SquashMult
            self.CurveInfoNode.arcLength  >> self.Squash_MD.input2X
            
            ## SquashMult >> Exp A,B,C
            self.Squash_MD.outputX >> self.expA_MD.input1X
            self.Squash_MD.outputX >> self.expB_MD.input1X
            self.Squash_MD.outputX >> self.expC_MD.input1X

            ## initial_ctrl >> Exp A,B,C
            pm.PyNode(self.initial_ctrl).ExpA >> self.expA_MD.input2X
            pm.PyNode(self.initial_ctrl).ExpB >> self.expB_MD.input2X
            pm.PyNode(self.initial_ctrl).ExpC >> self.expC_MD.input2X
            

                                 
        #-----------------------------------
        # Build Ik SetUp
        #-----------------------------------
        create_ik_jnts()
        create_ik_ctrls()    
        ik_squash(1.25, 1.5, 1.25)
        
        pm.select(self.create_ik_ctrls)
        mc.FreezeTransformations()    
        pm.skinCluster(self.all_ik_jnts, self.nurbs_ik_plane)            
                
        ## Hiarchie
        pm.parent(self.create_ik_ctrls[0].getParent(),self.rev_spine_jnts[0])
        pm.parent(self.create_ik_ctrls[1].getParent(),self.rev_spine_jnts[(len(self.guide_spine_loc)+1)/2])
        pm.parent(self.create_ik_ctrls[-1].getParent(),self.rev_spine_jnts[-1])
        _all_grp = pm.group(n='x__spine_ikSystem__grp__', em=True)
        pm.parent(self.nurbs_ik_plane,self.spineIk_curve,self.foll_joint[0].getParent().getParent().getParent(), _all_grp)
        spine_main_grp = pm.group(n='x__spine_rig__grp__', em=True)
        pm.parent(_all_grp, self.reg_FK_ctrls_offset_reg[0].getParent(),self.initial_ctrl, spine_main_grp)
        

        ## visibility
        pm.PyNode(self.nurbs_ik_plane).v.set(0)
        self.spineIk_curve.v.set(0)
        
        for ctrl in self.reg_FK_ctrls:
            ctrl.drawStyle.set(2)

        for ctrl in self.rev_fk_ctrls:
            ctrl.drawStyle.set(2)

        for joint in self.all_ik_jnts:
            pm.PyNode(joint).v.set(0)


    def ik_squash_con(self):
        for each in self.UpFoll:
            pm.PyNode(self.expA_MD).outputX >> pm.PyNode(each).scaleY
            pm.PyNode(self.expA_MD).outputX >> pm.PyNode(each).scaleZ

        for each in self.MidFoll:
            pm.PyNode(self.expB_MD).outputX >> pm.PyNode(each).scaleY
            pm.PyNode(self.expB_MD).outputX >> pm.PyNode(each).scaleZ

        for each in self.LowFoll:
            pm.PyNode(self.expC_MD).outputX >> pm.PyNode(each).scaleY
            pm.PyNode(self.expC_MD).outputX >> pm.PyNode(each).scaleZ

       
# ===================================================

    #-----------------------------------
    # FUNCTIONS Repeated
    #-----------------------------------

    @makeroot()
    def fk_pin_shape_setup(self,
                       listJoint = pm.selected(),
                       ):
        """Fk chain setUp by parenting the shape to the joint """
        
        def CreateCircles():
            CurveColl = []
            for joint in listJoint:

                myname = '{}'.format(joint)
                new_name = myname.split('__jnt__')[0] + '_fk__ctrl__'                    
                curve =sl.pin_shape()
                CurveColl.append(curve)
                curve.rx.set(self.anglePin)                
                curve.scaleX.set(0.5)
                curve.scaleY.set(0.5)
                curve.scaleZ.set(0.5)
                
                pm.select(curve)
                mc.FreezeTransformations()
               
                curveShape = pm.PyNode(curve).getShapes()                                       
                tras = joint.getTranslation()
                
                joint.setTranslation(tras)          
                pm.parent(curveShape,joint, r=True, s=True)            
                pm.delete(curve)            
                pm.rename(joint,new_name)
        
            return(listJoint)
        
        controls =  CreateCircles()    
        return(controls)

    @undo
    def makeroot_func(self, subject = pm.selected(),suff = 'root'):
        pm.select(subject)
        oColl = pm.selected()
        
        
        for each in oColl:
            try:
                suffix = each.name().split('__')[-2]
                cutsuffix = '__{}__'.format(suffix)
            except:
                suffix, cutsuffix = '', ''
            oRoot =  pm.group(n=each.name()+'__'+ suff +'__grp__', em=True)

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


    @makeroot()
    def fk_shape_setup(self,
                       radius=0.5  ,
                       Normalsctrl = (1,0,0),
                       listJoint = pm.selected(),
                       ):
        """Fk chain setUp by parenting the shape to the joint """
        

        def CreateCircles():
            CurveColl = []
            for joint in listJoint:

                myname = '{}'.format(joint)
                new_name = myname.split('__jnt__')[0] + '_fk__ctrl__'
                    
                curve = pm.circle(nr=Normalsctrl, r = radius )

                curveShape = pm.PyNode(curve[0]).getShape()
                CurveColl.extend(curve)            
                tras = joint.getTranslation()
                # pivot = pm.xform(joint, ws=True, q=True, rp=True)
                
                # pm.xform(curve, ws=True, t=tras, rp=pivot)            
                pm.parent(curveShape,joint, r=True, s=True)            
                pm.delete(curve)            
                pm.rename(joint,new_name)
        
            return(listJoint)

        controls =  CreateCircles()  
        return(controls)

    
    def Folli(self, myObject = pm.selected(), radius = 0.5, countV =9):            

        def create_follicle(oNurbs, count, uPos=0.0, vPos=0.0):

            oNurbs = pm.PyNode(oNurbs).getShape()             
            pName = '{}_{}__foll__'.format(oNurbs.name(), count)

            oFoll = pm.createNode('follicle', name='{}'.format(pName))
            oFoll.v.set(0) # hide the little red shape of the follicle
            if oNurbs.type() == 'nurbsSurface':
                oNurbs.local.connect(oFoll.inputSurface)
            if oNurbs.type() == 'mesh':
                # if using a polygon mesh, use this line instead.
                # (The polygons will need to have UVs in order to work.)
                oNurbs.outMesh.connect(oFoll.inputMesh)
             
            for param in pm.listAttr(oFoll, keyable=True):
                if param in ['parameterU', 'parameterV']: pass
                else:
                    pm.PyNode(oFoll + '.' + param).setKeyable(False)
         
            oNurbs.worldMatrix[0].connect(oFoll.inputWorldMatrix)
            oFoll.outRotate.connect(oFoll.getParent().rotate)
            oFoll.outTranslate.connect(oFoll.getParent().translate)
            uParam = add_keyable_attribute(oFoll.getParent(), 'double', 'u_param', oMin=-100, oMax=100, oDefault=0)
            vParam = add_keyable_attribute(oFoll.getParent(), 'double', 'v_param', oMin=-100, oMax=100, oDefault=0)
            connect_multiply(oFoll.parameterU, oFoll.getParent().u_param, 0.01)
            connect_multiply(oFoll.parameterV, oFoll.getParent().v_param, 0.01)
            uParam.set(uPos)
            vParam.set(vPos)
            oFoll.getParent().t.lock()
            oFoll.getParent().r.lock()         
            return oFoll
                  
        def many_follicles(obj, countU, vDir='U'):            
            all_joint = []
            
            pName = pm.PyNode(myObject).name()                                              
            oRoot = pm.spaceLocator(n=pName.replace('_ribbon','') + '_follicles')
            pm.delete(oRoot.getShape())
            currentFollNumber = 0
            for i in range(countU):
                for j in range(countV):
                    currentFollNumber += 1
                    pm.select(None)
                    if countU == 1:
                        uPos = 50.0
                    else:
                        uPos = (i/(countU-1.00)) * 100.0 #NOTE: I recently changed this to have a range of 0-10
                    if countV == 1:
                        vPos = 50.0
                    else:
                        vPos = (j/(countV-1.00)) * 100.0 #NOTE: I recently changed this to have a range of 0-10
                    if vDir == 'U':
                        oFoll = create_follicle(myObject, currentFollNumber, vPos, uPos)
                    else:
                        # reverse the direction of the follicles
                        oFoll = create_follicle(myObject, currentFollNumber, uPos, vPos)
                    pm.rename(oFoll.getParent(), '{}0{}__foll__'.format(pName, currentFollNumber))
                    pm.rename(oFoll, '{}_{}__foll__Shape'.format(pName, currentFollNumber))
                    oLoc = pm.group(em=True, n='{}0{}__grp__'.format(pName, currentFollNumber))
                    oLoc.setTranslation(oFoll.getParent().getTranslation(space='world'), space='world')
            
                    oJoint = pm.joint(n=pName + '0{}__jnt__'.format(currentFollNumber), rad = radius)
                    oJoint.setTranslation(oFoll.getParent().getTranslation(space='world'), space='world')
                    all_joint.append(oJoint)
                    
                    # connect the UV params to the joint so you can move the follicle by selecting the joint directly.
                    uParam = add_keyable_attribute(oJoint, 'double', 'u_param', oMin=-100, oMax=100, oDefault=0)
                    vParam = add_keyable_attribute(oJoint, 'double', 'v_param', oMin=-100, oMax=100, oDefault=0)
                    uParam.set(oFoll.getParent().u_param.get())
                    vParam.set(oFoll.getParent().v_param.get())
                    uParam.connect(oFoll.getParent().u_param)
                    vParam.connect(oFoll.getParent().v_param)
            
                    #pm.parent(oJoint, oLoc)
                    pm.parent(oLoc, oFoll.getParent())
                    pm.parent(oFoll.getParent(), oRoot)
                    oLoc.rx.set(0.0)
                    oLoc.ry.set(0.0)
                    oLoc.rz.set(0.0)
                    pm.select(None)
                return(all_joint)

         
        def add_keyable_attribute(myObj, oDataType, oParamName, oMin=None, oMax=None, oDefault=0.0):
            """adds an attribute that shows up in the channel box; returns the newly created attribute"""
            oFullName = '.'.join( [str(myObj),oParamName] )
            if pm.objExists(oFullName):
                return pm.PyNode(oFullName)
            else:
                myObj.addAttr(oParamName, at=oDataType, keyable=True, dv=oDefault)
                myAttr = pm.PyNode(myObj + '.' + oParamName)
                if oMin != None:
                    myAttr.setMin(oMin)
                if oMax != None:
                    myAttr.setMax(oMax)
                pm.setAttr(myAttr, e=True, channelBox=True)
                pm.setAttr(myAttr, e=True, keyable=True)
                return myAttr
         
         
        def connect_multiply(oDriven, oDriver, oMultiplyBy):
            nodeName = oDriven.replace('.','_') + '_mult'
            try:
                testExists = pm.PyNode(nodeName)
                pm.delete(pm.PyNode(nodeName))
                # print ('deleting'.format(nodeName))
            except: pass
            oMult = pm.shadingNode('unitConversion', asUtility=True, name=nodeName)
            pm.PyNode(oDriver).connect(oMult.input)
            oMult.output.connect( pm.Attribute(oDriven) )
            oMult.conversionFactor.set(oMultiplyBy)
            return oMult
         
        self.foll_joint = many_follicles(myObject, 1, 'U')
         

    def build_spine_from_curve(self, curve, spine_num):
        
        spine_curve_dup = pm.duplicate('spine_guide__curve', n = 'spine_guide__curve_dup')[0]
        pm.makeIdentity(spine_curve_dup , n=0, s=1, r=1, t=1, apply=True, pn=1)
        pm.parent(spine_curve_dup, world=True)
        
        poc = adb_PointonCurve.PointToCurveJnt(spine_num, sel=spine_curve_dup)

        spine_joints = poc.getJoints      
        adb_spine.SpineSetUp(spine_joints)        
        pm.delete(spine_curve_dup)
        [pm.delete(pm.PyNode(x).getParent()) for x in spine_joints]
    


#-----------------------------------
# CLASS BUILD
#-----------------------------------

# SpineSetUp()



# -----------------------------------
#   EXEMPLE EXTERIOR CLASS BUILD
# -----------------------------------

# import adb_rig.Class__Spine_setUp as adb_spine
# reload(adb_spine)  
  
# def spine():    
#     adb_spine.SpineSetUp(['adb_01', 'adb_02', 'adb_03', 'adb_04', 'adb_05', 'adb_06', 'adb_07', 'adb_08', 'adb_09'])
# spine()
    
    
