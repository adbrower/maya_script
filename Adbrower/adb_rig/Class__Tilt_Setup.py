import maya.cmds as mc
import pymel.core as pm

#-----------------------------------
# IMPORT CUSTOM MODULES
#----------------------------------- 

import adbrower
reload(adbrower)
adb = adbrower.Adbrower()

from adbrower import flatList

#-----------------------------------
#  DECORATORS
#----------------------------------- 

from adbrower import changeColor
from adbrower import makeroot

#-----------------------------------
# CLASS
#----------------------------------- 

class Tilt(object):
    '''    
    Class that builds a tilt systeme

    @param geo: Mesh that will tilt
    @param tilt_ctrl: Tilt ctrl
    @param target_parent_grp: Parent group of the latest controler controlling the mesh. (This controler will be hidden)
    @param last_offset: latest controller offset AFTER latest controler controlling the mesh
    @param axe: String. Axis of the tilt. {'x':'y':'both'}

    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_rig.Class__Tilt_Setup as adb_tilt
    reload(adb_tilt)  

    tilt = adb_tilt.Tilt('m__bust__hi_msh__','diamond_ctrl','offset_ctrl__root__grp__','m__element__trajectory__ctrl__' ,'z')
    tilt.buildGuide()

    '''
        
    def __init__(self,  geo, tilt_ctrl, target_parent_grp, last_offset, axe):
        self.geo  = pm.PyNode(geo)
        self.tiltctrl = pm.PyNode(tilt_ctrl)
        
        self.mesh_ctrl_parent = target_parent_grp
        self.mesh_ctrl_offset = last_offset
        self.axe = axe


    def createLoc(self,type):
        if type == 'driverloc':
            driverloc = pm.spaceLocator(n='{}__driver_loc'.format(str(self.geo)))
            adb.changeColor_func(driverloc, 'index', 6) 
            pm.setAttr(driverloc.rotatePivotX, k=True)
            pm.setAttr(driverloc.rotatePivotY, k=True )
            pm.setAttr(driverloc.rotatePivotZ, k=True )            
            return driverloc
        
        elif type == 'pivotloc':                                   
            pivotloc = pm.spaceLocator(n='{}__pivot_loc'.format(str(self.geo)))
            adb.changeColor_func(pivotloc, 'index', 17)
            return pivotloc

        elif type == 'objPosloc': 
            objPosloc = pm.spaceLocator(n='{}__objPosloc_loc'.format(str(self.geo)))
            return objPosloc

        elif type == 'poslocTZ01':
            poslocTZ01 = pm.spaceLocator(n='{}__pos_locatorTZpositive'.format(str(self.geo)), p = self.zmax) 
            poslocTZ01.localScale.set([0.3,0.3,0.3])
            adb.changeColor_func(poslocTZ01, 'index', 18)            
            return poslocTZ01

        elif type == 'poslocTZ02':
            poslocTZ02 = pm.spaceLocator(n='{}__pos_locatorTZnegative'.format(str(self.geo)), p = self.zmin)   
            poslocTZ02.localScale.set([0.3,0.3,0.3])
            adb.changeColor_func(poslocTZ02, 'index', 18)   
            return poslocTZ02

        elif type == 'poslocTX01':
            poslocTX01 = pm.spaceLocator(n='{}__pos_locatorTXpositive'.format(str(self.geo)), p = self.xmax)   
            poslocTX01.localScale.set([0.3,0.3,0.3])
            adb.changeColor_func(poslocTX01, 'index', 4)            
            return poslocTX01

        elif type == 'poslocTX02':
            poslocTX02 = pm.spaceLocator(n='{}__pos_locatorTXnegative'.format(str(self.geo)), p = self.xmin)   
            poslocTX02.localScale.set([0.3,0.3,0.3])
            adb.changeColor_func(poslocTX02, 'index', 4)  
            return poslocTX02


#===================================
#   BUILD GUIDE
#===================================

    def buildGuide(self):
        bbox = pm.exactWorldBoundingBox(self.geo)
        
        self.bot = [(bbox[0] + bbox[3])/2, bbox[1], (bbox[2] + bbox[5])/2]
        self.zmin = [(bbox[0] + bbox[3])/2 ,bbox[1], bbox[2]]
        self.zmax = [(bbox[0] + bbox[3])/2 ,bbox[1], bbox[5]]
        self.xmin = [bbox[0] , bbox[1] , (bbox[2] + bbox[5])/2]
        self.xmax = [bbox[3] , bbox[1] , (bbox[2] + bbox[5])/2] 

        """ -------------------- Z AXIS -------------------- """


        if self.axe == 'z':

            ### Creer mes nodes et loc ###     
            self.driverloc = self.createLoc('driverloc')
            self.pivotloc = self.createLoc('pivotloc')
            self.objPosloc = self.createLoc('objPosloc')

            self.poslocTZ01 = self.createLoc('poslocTZ01')
            self.poslocTZ01Shape = self.poslocTZ01.getShape()
            pm.xform(centerPivots=True)
                        
            self.poslocTZ02 =  self.createLoc('poslocTZ02')
            self.poslocTZ02Shape = self.poslocTZ02.getShape()
            pm.xform(centerPivots=True)
            
            self.ZtiltconNode = pm.shadingNode('condition',asUtility=1, n="{}__Ztilt_condition".format(str(self.geo)))
            self.Ztilt_MD = pm.shadingNode('multiplyDivide', asUtility = 1 , n = "{}__Ztilt_multiplyDivide".format(str(self.geo)))

            self.ZtiltconNode.operation.set(2)
            self.Ztilt_MD.operation.set(1)
            self.Ztilt_MD.input2Z.set(10) 

            ptCont = pm.pointConstraint(self.geo , self.objPosloc, mo=False) 
            pm.delete(ptCont)
            
            self.pivotloc.visibility.set(0)
            self.driverloc.visibility.set(0) 
            self.objPosloc.visibility.set(0)
            

            """ -------------------- X AXIS -------------------- """


        elif self.axe == 'x':

            ### Creer mes nodes et loc ###     
            self.driverloc = self.createLoc('driverloc')
            self.pivotloc = self.createLoc('pivotloc')
            self.objPosloc = self.createLoc('objPosloc')

            self.poslocTX01 = self.createLoc('poslocTX01')
            self.poslocTX01Shape = self.poslocTX01.getShape()
            pm.xform(centerPivots=True)
                        
            self.poslocTX02 =  self.createLoc('poslocTX02')
            self.poslocTX02Shape = self.poslocTX02.getShape()
            pm.xform(centerPivots=True)
           
            self.XtiltconNode = pm.shadingNode('condition',asUtility=1, n="Xtilt_condition")
            pm.rename(self.XtiltconNode,str(self.geo)+"_Xtilt_condition")

            self.Xtilt_MD = pm.shadingNode('multiplyDivide', asUtility = 1 , n = "Xtilt_multiplyDivide")
            pm.rename(self.Xtilt_MD,str(self.geo)+"_Xtilt_multiplyDivide")

            self.XtiltconNode.operation.set(3)
            self.Xtilt_MD.operation.set(1)
            self.Xtilt_MD.input2X.set(-10) 

            ptCont = pm.pointConstraint(self.geo , self.objPosloc, mo=False) 
            pm.delete(ptCont)
            
            self.pivotloc.visibility.set(0)
            self.driverloc.visibility.set(0) 
            self.objPosloc.visibility.set(0)
             


            """ -------------------- Z AND X AXIS -------------------- """


        elif self.axe == 'both':
            
            ### Creer mes nodes et loc ###     
            self.driverloc = self.createLoc('driverloc')
            self.pivotloc = self.createLoc('pivotloc')
            self.objPosloc = self.createLoc('objPosloc')

            self.poslocTX01 = self.createLoc('poslocTX01')
            self.poslocTX01Shape = self.poslocTX01.getShape()
            pm.xform(centerPivots=True)
                        
            self.poslocTX02 =  self.createLoc('poslocTX02')
            self.poslocTX02Shape = self.poslocTX02.getShape()
            pm.xform(centerPivots=True)

            self.poslocTZ01 = self.createLoc('poslocTZ01')
            self.poslocTZ01Shape = self.poslocTZ01.getShape()
            pm.xform(centerPivots=True)
                        
            self.poslocTZ02 =  self.createLoc('poslocTZ02')
            self.poslocTZ02Shape = self.poslocTZ02.getShape()
            pm.xform(centerPivots=True)

            self.ZtiltconNode = pm.shadingNode('condition',asUtility=1, n="{}__Ztilt_condition".format(str(self.geo)))
            self.Ztilt_MD = pm.shadingNode('multiplyDivide', asUtility = 1 , n = "{}__Ztilt_multiplyDivide".format(str(self.geo)))

            self.ZtiltconNode.operation.set(2)
            self.Ztilt_MD.operation.set(1)
            self.Ztilt_MD.input2Z.set(10) 

            self.XtiltconNode = pm.shadingNode('condition',asUtility=1, n="Xtilt_condition")
            pm.rename(self.XtiltconNode,str(self.geo)+"_Xtilt_condition")

            self.Xtilt_MD = pm.shadingNode('multiplyDivide', asUtility = 1 , n = "Xtilt_multiplyDivide")
            pm.rename(self.Xtilt_MD,str(self.geo)+"_Xtilt_multiplyDivide")

            self.XtiltconNode.operation.set(3)
            self.Xtilt_MD.operation.set(1)
            self.Xtilt_MD.input2X.set(-10) 


            ### Setter mes nodes et loc ###


            ptCont = pm.pointConstraint(self.geo , self.objPosloc, mo=False) 
            pm.delete(ptCont)
            
            self.pivotloc.visibility.set(0)
            self.driverloc.visibility.set(0) 
            self.objPosloc.visibility.set(0)



#===================================
#   BUILD RIG
#===================================

    def buildRig(self):

        if self.axe == 'z':
           
            """ -------------------- Z AXIS -------------------- """
            
            ptCont = pm.pointConstraint(self.poslocTZ01 , self.pivotloc, mo=False) 
            pm.delete(ptCont)

            ## Connections ##    
            self.pivotloc.translate.connect(self.driverloc.rotatePivot)            
            pm.PyNode(self.tiltctrl).tz >> self.driverloc.rotateX
            pm.PyNode(self.tiltctrl).tz >> self.ZtiltconNode.firstTerm
            
            pm.PyNode(self.ZtiltconNode).outColorR >> self.pivotloc.tz
            pm.PyNode(self.poslocTZ01Shape).worldPosition[0].worldPositionZ >> pm.PyNode(self.ZtiltconNode).colorIfTrueR          
            pm.PyNode(self.poslocTZ02Shape).worldPosition[0].worldPositionZ >> pm.PyNode(self.ZtiltconNode).colorIfFalseR

            pm.PyNode(self.tiltctrl).tz >> pm.PyNode(self.Ztilt_MD).input1Z
            self.Ztilt_MD.outputZ >> pm.PyNode(self.driverloc).rx
           
            ## setter visibility ##
            self.driverloc.visibility.set(0)
            self.poslocTZ01.visibility.set(0)
            self.poslocTZ02.visibility.set(0)
            self.pivotloc.visibility.set(0)

            Lastgrp = pm.group(self.driverloc , self.poslocTZ01, self.poslocTZ02, self.mesh_ctrl_parent)                        
        

        elif self.axe == 'x':   

            """ -------------------- X AXIS -------------------- """

            ptCont = pm.pointConstraint(self.poslocTX01 , self.pivotloc, mo=False) 
            pm.delete(ptCont)

            ## Connections ##    
            self.pivotloc.translate.connect(self.driverloc.rotatePivot)
            pm.PyNode(self.tiltctrl).tx >> self.driverloc.rotateZ
            pm.PyNode(self.tiltctrl).tx >> self.XtiltconNode.firstTerm
            
            pm.PyNode(self.XtiltconNode).outColorR >> self.pivotloc.tx
            pm.PyNode(self.poslocTX01Shape).worldPosition[0].worldPositionX >> pm.PyNode(self.XtiltconNode).colorIfTrueR          
            pm.PyNode(self.poslocTX02Shape).worldPosition[0].worldPositionX >> pm.PyNode(self.XtiltconNode).colorIfFalseR
            
            pm.PyNode(self.tiltctrl).tx >> pm.PyNode(self.Xtilt_MD).input1X
            self.Xtilt_MD.outputX >> pm.PyNode(self.driverloc).rz           

            ## setter visibility ##
            self.driverloc.visibility.set(0)
            self.poslocTX01.visibility.set(0)
            self.poslocTX02.visibility.set(0)
            self.pivotloc.visibility.set(0)

            Lastgrp = pm.group(self.driverloc , self.poslocTX01, self.poslocTX02, self.mesh_ctrl_parent)            


        elif self.axe == 'both':               

            """ -------------------- Z AND X AXIS -------------------- """

            ptCont = pm.pointConstraint(self.poslocTX01 , self.pivotloc, mo=False) 
            pm.delete(ptCont)
                        
            ptCont2 = pm.pointConstraint(self.poslocTZ01 , self.pivotloc, mo=False) 
            pm.delete(ptCont2)

            ## Connections ##                           
            self.pivotloc.translate.connect(self.driverloc.rotatePivot)
            pm.PyNode(self.tiltctrl).tx >> self.driverloc.rotateZ
            pm.PyNode(self.tiltctrl).tx >> self.XtiltconNode.firstTerm
            
            pm.PyNode(self.XtiltconNode).outColorR >> self.pivotloc.tx
            pm.PyNode(self.poslocTX01Shape).worldPosition[0].worldPositionX >> pm.PyNode(self.XtiltconNode).colorIfTrueR          
            pm.PyNode(self.poslocTX02Shape).worldPosition[0].worldPositionX >> pm.PyNode(self.XtiltconNode).colorIfFalseR
            
            pm.PyNode(self.tiltctrl).tx >> pm.PyNode(self.Xtilt_MD).input1X
            self.Xtilt_MD.outputX >> pm.PyNode(self.driverloc).rz  

            pm.PyNode(self.tiltctrl).tz >> self.driverloc.rotateX
            pm.PyNode(self.tiltctrl).tz >> self.ZtiltconNode.firstTerm
            
            pm.PyNode(self.ZtiltconNode).outColorR >> self.pivotloc.tz
            pm.PyNode(self.poslocTZ01Shape).worldPosition[0].worldPositionZ >> pm.PyNode(self.ZtiltconNode).colorIfTrueR          
            pm.PyNode(self.poslocTZ02Shape).worldPosition[0].worldPositionZ >> pm.PyNode(self.ZtiltconNode).colorIfFalseR

            pm.PyNode(self.tiltctrl).tz >> pm.PyNode(self.Ztilt_MD).input1Z
            self.Ztilt_MD.outputZ >> pm.PyNode(self.driverloc).rx

            ## setter visibility ##            
            self.pivotloc.visibility.set(0)
            self.driverloc.visibility.set(0)
            self.poslocTX01.visibility.set(0)
            self.poslocTX02.visibility.set(0)
            self.poslocTZ01.visibility.set(0)
            self.poslocTZ02.visibility.set(0)

            Lastgrp = pm.group(self.driverloc , self.poslocTZ01, self.poslocTZ02, self.poslocTX02, self.poslocTX01, self.mesh_ctrl_parent)            

        ## setter Hiearchie et Clean Up ##
        pm.parentConstraint(self.objPosloc, pm.PyNode(self.mesh_ctrl_parent).getChildren()[0], mo = True) 
        
        pm.parent(self.pivotloc,self.driverloc)
        mc.parentConstraint(str(self.objPosloc),self.mesh_ctrl_parent, mo=True)
        mc.parent(str(self.objPosloc),str(self.driverloc))
                      
        geo_name = str(self.geo)
        try:
            geo_new_name = geo_name.replace(geo_name.split('__')[2],'{}_tilt_grp'.format(self.axe))
        except IndexError: 
            geo_new_name = ('{}_{}_tilt_grp'.format(geo_name,self.axe))
            
        pm.rename ( Lastgrp, geo_new_name)
        

        driver_loc_grp = adb.makeroot_func(self.driverloc)
        pm.parentConstraint(self.mesh_ctrl_offset,driver_loc_grp, mo=True)
        pm.PyNode(self.mesh_ctrl_parent).v.set(0)

        
                
                                
