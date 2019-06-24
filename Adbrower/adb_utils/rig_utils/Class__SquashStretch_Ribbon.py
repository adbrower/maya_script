# ------------------------------------------------------
# Squash and Strech
# -- Method Rigger (Maya)
# -- Version 1.0.0 
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import maya.cmds as mc
import pymel.core as pm

import NameConv_utils as NC
reload(NC)

from adbrower import undo
from adb_utils.Class__Transforms import Transform


MODULE_NAME = 'ribbon_squash_stretch'
METADATA_grp_name = '{}_METADATA'.format(MODULE_NAME)

class SquashStrech(object):
    '''
    Squash and Strech for a ribbon system
    
    import adb_utils.Class__SquashStretch_Ribbon as adb_ST_Ribbon
    reload(adb_utils.Class__SquashStretch_Ribbon)  
      
      
    adb_ST_Ribbon.SquashStrech(
                    ExpCtrl = "l__Leg_Options__ctrl__",
                    jointList = ['joint1', 'joint2' ... ],
                    ribbon_ctrl = ['l__Leg_IK_offset__ctrl__', 'l__Leg__thigh_result__jnt__'], ## bottom first, then top
                    intervalA_1 = 0,
                    intervalA_2 = 3,

                    intervalB_1 = 4,
                    intervalB_2 = 17,   
                    
                    intervalC_1 = 7, 
                    
                    expA = 1.25,                        
                    expB = 1.5,                        
                    expC = 1.25,  )
    
    '''

    def __init__(self,
                ExpCtrl = "ball_ctrl",
                jointList = ['X__test_0{}__GRP'.format(x+1) for x in xrange(5)],

                ribbon_ctrl = ['bendy_01__CTRL__', 'bendy_02__CTRL__'], ## bottom first, then top
                intervalA_1 = 1,
                intervalA_2 = 2,

                intervalB_1 = 2,
                intervalB_2 = 3,   
                
                intervalC_1 = 3, 
                intervalC_2 = -1, 
                
                expA = 0,                        
                expB = 1.5,                        
                expC = 0,                        
                ):
        
        self.ExpCtrl = ExpCtrl
        self.jointList = jointList
        self.ribbon_ctrl = ribbon_ctrl
        
        self.jointListA = self.jointList[intervalA_1:intervalA_2]
        self.jointListB = self.jointList[intervalB_1:intervalB_2]
        self.jointListC = self.jointList[intervalC_1:intervalC_2]
        
        self.expA = expA                        
        self.expB = expB                       
        self.expC = expC 
                        
        self.addExposant_attrs(self.expA , self.expB , self.expC)
        self.CreateNodes()
        self.MakeConnections()
        self.JointConnections()
        self.setFinal_hiearchy() 
        self.set_TAGS()
        
        


    @undo
    def addExposant_attrs(self, expA, expB, expC):
        """Create the Exp Attribute on a selected Controler """     
        if pm.objExists('{}.ExpA'.format(self.ExpCtrl)):
            pass
        else:
            pm.PyNode(self.ExpCtrl).addAttr('ExpA', keyable=True, dv= expA, at='double', min=0)
            pm.PyNode(self.ExpCtrl).addAttr('ExpB', keyable=True, dv= expB, at='double', min=0)
            pm.PyNode(self.ExpCtrl).addAttr('ExpC', keyable=True, dv= expC, at='double', min=0)

        
    @undo
    def CreateNodes(self):
        """Creation et settings de mes nodes"""
        
        pm.select(self.jointList, r = True)
        def createloc(sub = pm.selected()):    
            '''Creates locator at the Pivot of the object selected '''    

            locs = []
            for sel in sub:                           
                loc_align = pm.spaceLocator(n='{}__pos_loc__'.format(sel))
                locs.append(loc_align)
                pm.matchTransform(loc_align,sel,rot=True, pos=True)
                pm.select(locs, add = True)
            return locs

        posLocs = createloc([self.jointList[0],self.jointList[-1]])

        sp = (pm.PyNode(posLocs[0]).translateX.get(),pm.PyNode(posLocs[0]).translateY.get(),pm.PyNode(posLocs[0]).translateZ.get())
        ep = (pm.PyNode(posLocs[1]).translateX.get(),pm.PyNode(posLocs[1]).translateY.get(),pm.PyNode(posLocs[1]).translateZ.get())


        ## create Distances Nodes
        self.DistanceLoc = pm.distanceDimension(sp=sp,  ep=ep)
        pm.rename(self.DistanceLoc, 'bendy_distDimShape')
        pm.rename(pm.PyNode(self.DistanceLoc).getParent(), 'bendy_distDim')
        distance = self.DistanceLoc.distance.get()
        
        pm.parent(posLocs[0],self.ribbon_ctrl[0])
        pm.parent(posLocs[1],self.ribbon_ctrl[1])
        
        pm.rename(posLocs[0], 'distance_depart__{}'.format(NC.LOC))
        pm.rename(posLocs[1], 'distance_end__{}'.format(NC.LOC))
        
        posLocs[0].v.set(0)
        posLocs[1].v.set(0)
        self.DistanceLoc.getParent().v.set(0)
                     
        ## Creation des nodes Multiply Divide
        self.CurveInfoNode = pm.shadingNode('curveInfo',asUtility=1, n="IK_Spline_CurveInfo")
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
        
        

    def create_scale_distance(self):
        distObjs_LIST_QDT = self.ribbon_ctrl

        distanceNode_shape = pm.distanceDimension (sp = (1, 1, 1), ep = (2, 2, 2))

        pm.rename(distanceNode_shape, 'bendy_scale_distDimShape')
        pm.rename(pm.PyNode(distanceNode_shape).getParent(),'bendy_scale_distDim')

        distanceNode = (pm.PyNode(distanceNode_shape).getParent())

        end_point_loc = pm.listConnections(str(distanceNode_shape)+'.endPoint', source=True)[0]
        start_point_loc = pm.listConnections(str(distanceNode_shape)+'.startPoint', source=True)[0]

        pm.rename(start_point_loc, '{}_Dist__{}'.format(distObjs_LIST_QDT[0], NC.LOC))
        pm.rename(end_point_loc, '{}_Dist__{}'.format(distObjs_LIST_QDT[1], NC.LOC))

        pm.matchTransform(start_point_loc, distObjs_LIST_QDT[0])
        pm.matchTransform(end_point_loc, distObjs_LIST_QDT[1])
        
        [loc.v.set(0) for loc in [end_point_loc, start_point_loc]]
        
        self.scale_grp = pm.group(n = '{}_scale__{}'.format(MODULE_NAME, NC.GRP), w = True, em = True)
        pm.parent(distanceNode,start_point_loc,end_point_loc, self.scale_grp) 
        self.scale_grp.v.set(0)
        
        return distanceNode_shape    
        
    @undo
    def MakeConnections(self):   
        
        self.scale_distanceNode = self.create_scale_distance()
        
        self.scale_distanceNode.distance >> self.Stretch_MD.input2X
        self.scale_distanceNode.distance >>self.Squash_MD.input1X
        
        ## Distance >> StretchMult
        self.DistanceLoc.distance >> self.Stretch_MD.input1X
           
        ## StretchMult >> All scale X of each joint       
        for each in self.jointList[1:-1]:
            self.Stretch_MD.outputX >> pm.PyNode(each).scaleX
 
        ## Distance >> SquashMult
        self.DistanceLoc.distance  >> self.Squash_MD.input2X
        
        ## SquashMult >> Exp A,B,C
        self.Squash_MD.outputX >> self.expA_MD.input1X
        self.Squash_MD.outputX >> self.expB_MD.input1X
        self.Squash_MD.outputX >> self.expC_MD.input1X

        ## ExpCtrl >> Exp A,B,C
        pm.PyNode(self.ExpCtrl).ExpA >> self.expA_MD.input2X
        pm.PyNode(self.ExpCtrl).ExpB >> self.expB_MD.input2X
        pm.PyNode(self.ExpCtrl).ExpC >> self.expC_MD.input2X
        
        pm.PyNode(self.ExpCtrl).ExpA >> self.expA_MD.input2Y
        pm.PyNode(self.ExpCtrl).ExpB >> self.expB_MD.input2Y
        pm.PyNode(self.ExpCtrl).ExpC >> self.expC_MD.input2Y
        
        pm.PyNode(self.ExpCtrl).ExpA >> self.expA_MD.input2Z
        pm.PyNode(self.ExpCtrl).ExpB >> self.expB_MD.input2Z
        pm.PyNode(self.ExpCtrl).ExpC >> self.expC_MD.input2Z
        


    def JointConnections(self):
        """Connections on joints in Scale Y and Scale Z """
       
        expA_MD = "ExpA"
        expB_MD = "ExpB"
        expC_MD = "ExpC"
        
        for each in self.jointListA:
            pm.PyNode(expA_MD).outputX >> pm.PyNode(each).scaleY
            pm.PyNode(expA_MD).outputX >> pm.PyNode(each).scaleZ

        for each in self.jointListB:
            pm.PyNode(expB_MD).outputX >> pm.PyNode(each).scaleY
            pm.PyNode(expB_MD).outputX >> pm.PyNode(each).scaleZ

        for each in self.jointListC:
            pm.PyNode(expC_MD).outputX >> pm.PyNode(each).scaleY
            pm.PyNode(expC_MD).outputX >> pm.PyNode(each).scaleZ
            
    

    def setFinal_hiearchy(self):
        final_grp = NC.setFinalHiearchy('{}'.format(MODULE_NAME),
                    RIG_GRP_LIST = [self.DistanceLoc.getParent()],
                    INPUT_GRP_LIST = [],
                    OUTPUT_GRP_LIST = [],
                    mod=0)    
 
        self.Do_not_touch_grp = pm.group(n = NC.NO_TOUCH, em=1, parent=final_grp[1])
                ## hiearchy
        pm.parent(self.scale_grp,self.Do_not_touch_grp)
        [pm.delete(grp) for grp in final_grp[2:]]

                    
    def set_TAGS(self):    
        Transform(str(self.scale_grp)).addAttr(NC.TAG_GlOBAL_SCALE, '')
        
      
                           
# SquashStrech()        










        
        
        
        
        
        
