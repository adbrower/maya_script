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


from adbrower import undo



class SquashStrech(object):
    '''
    Squash and Strech for a ribbon system
    
    import adb_utils.Class__SquashStretch_Ribbon as adb_ST_Ribbon
    reload(adb_utils.Class__SquashStretch_Ribbon)  
      
      
    adb_ST_Ribbon.SquashStrech(ExpCtrl = "l__Leg_Options__ctrl__",
                    jointList = ['l__Leg__proxy_plane_skin_01__skn__', 'l__Leg__proxy_plane_skin_02__skn__', 'l__Leg__proxy_plane_skin_03__skn__', 'l__Leg__proxy_plane_skin_04__skn__', 'l__Leg__proxy_plane_skin_05__skn__', 'l__Leg__proxy_plane_skin_06__skn__', 'l__Leg__proxy_plane_skin_07__skn__', 'l__Leg__proxy_plane_skin_08__skn__', 'l__Leg__proxy_plane_skin_09__skn__', 'l__Leg__proxy_plane_skin_010__skn__', 'l__Leg__proxy_plane_skin_011__skn__', 'l__Leg__proxy_plane_skin_012__skn__', 'l__Leg__proxy_plane_skin_013__skn__', 'l__Leg__proxy_plane_skin_014__skn__', 'l__Leg__proxy_plane_skin_015__skn__', 'l__Leg__proxy_plane_skin_016__skn__', 'l__Leg__proxy_plane_skin_017__skn__', 'l__Leg__proxy_plane_skin_018__skn__', 'l__Leg__proxy_plane_skin_019__skn__', 'l__Leg__proxy_plane_skin_020__skn__'],
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
                ExpCtrl = "l__Leg_Options__ctrl__",
                jointList = [],
                ribbon_ctrl = [], ## bottom first, then top
                intervalA_1 = 0,
                intervalA_2 = 3,

                intervalB_1 = 4,
                intervalB_2 = 17,   
                
                intervalC_1 = 17, 
                
                expA = 1.25,                        
                expB = 1.5,                        
                expC = 1.25,                        
                ):
        
        self.ExpCtrl = ExpCtrl
        self.jointList = jointList
        self.ribbon_ctrl = ribbon_ctrl
        
        self.jointListA = self.jointList[intervalA_1:intervalA_2]
        self.jointListB = self.jointList[intervalB_1:intervalB_2]
        self.jointListC = self.jointList[intervalC_1:]
        
        self.expA = expA                        
        self.expB = expB                       
        self.expC = expC 
                        
        self.CreateControl(self.expA , self.expB , self.expC)
        self.CreateNodes()
        self.MakeConnections()
        self.JointConnections()


    @undo
    def CreateControl(self, expA, expB, expC):
        """Create the Exp Attribute on a selected Controler """
        
        pm.PyNode(self.ExpCtrl).addAttr('ExpA', keyable=True, dv= expA, at='double')
        pm.PyNode(self.ExpCtrl).addAttr('ExpB', keyable=True, dv= expB, at='double')
        pm.PyNode(self.ExpCtrl).addAttr('ExpC', keyable=True, dv= expC, at='double')

        
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


        ## create Nodes
        self.DistanceLoc = pm.distanceDimension(sp=sp,  ep=ep)
        distance = self.DistanceLoc.distance.get()
        
        pm.parent(posLocs[0],self.ribbon_ctrl[0])
        pm.parent(posLocs[1],self.ribbon_ctrl[1])
        
        pm.rename(posLocs[0], 'caca')
        pm.rename(posLocs[1], 'pipi')
        
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
        
        self.Stretch_MD.input2X.set(distance) 
        self.Squash_MD.input1X.set(distance)  

        
    @undo
    def MakeConnections(self):   

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
            


                           
# SquashStrech()        










        
        
        
        
        
        