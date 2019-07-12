import maya.cmds as mc
import pymel.core as pm

#-----------------------------------
# IMPORT CUSTOM MODULES
#----------------------------------- 

import adbrower
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

    tilt = Tilt('suitcase',
               'C_tilt_CTRL',
               'C_tilt_offset_OUTPUT_GRP',
               'world_B_CTRL',
               'both',
                driverloc = 'suitcase__driver_loc',
                pivotloc = 'suitcase__pivot_loc',
                objPosloc = 'suitcase__objPosloc_loc',

                poslocTX01 = 'suitcase__pos_locatorTXpositive',
                poslocTZ01 = 'suitcase__pos_locatorTZpositive',

                poslocTX02 = 'suitcase__pos_locatorTXnegative',
                poslocTZ02 = 'suitcase__pos_locatorTZnegative',
                 )
     
              
    tilt.buildGuide()   
    tilt.buildRig()   

    '''
        
    def __init__(self,  
                geo, 
                tilt_ctrl, 
                target_parent_grp, 
                last_offset, 
                axe,
                driverloc=None,
                pivotloc=None,
                objPosloc=None,

                poslocTX01=None,
                poslocTZ01=None,

                poslocTX02=None,
                poslocTZ02=None,
                tilt_FACTOR = 2,
                ):
                    
        self.geo  = pm.PyNode(geo)
        self.tiltctrl = pm.PyNode(tilt_ctrl)
        
        self.target_parent_grp = target_parent_grp
        self.mesh_ctrl_offset = last_offset
        self.axe = axe
        
        if driverloc != None:
            self.driverloc = pm.PyNode(driverloc)
            
        if pivotloc != None:
            self.pivotloc = pm.PyNode(pivotloc)
            
        if objPosloc != None:
            self.objPosloc = pm.PyNode(objPosloc)
            
        if poslocTX01 != None:
            self.poslocTX01 = pm.PyNode(poslocTX01)
            
        if poslocTZ01 != None:
            self.poslocTZ01 = pm.PyNode(poslocTZ01)
            
        if poslocTX02 != None:
            self.poslocTX02 = pm.PyNode(poslocTX02)
            
        if poslocTZ02 != None:
            self.poslocTZ02 = pm.PyNode(poslocTZ02)
            
        self.tilt_FACTOR = tilt_FACTOR


    def createLoc(self,type):
        if type == 'driverloc':
            _driverloc = pm.spaceLocator(n='{}__driver_loc'.format(str(self.geo)))
            adb.changeColor_func(_driverloc, 'index', 6) 
            pm.setAttr(_driverloc.rotatePivotX, k=True)
            pm.setAttr(_driverloc.rotatePivotY, k=True )
            pm.setAttr(_driverloc.rotatePivotZ, k=True )            
            return _driverloc
        
        elif type == 'pivotloc':                                   
            _pivotloc = pm.spaceLocator(n='{}__pivot_loc'.format(str(self.geo)))
            adb.changeColor_func(_pivotloc, 'index', 17)
            return _pivotloc

        elif type == 'objPosloc': 
            _objPosloc = pm.spaceLocator(n='{}__objPosloc_loc'.format(str(self.geo)))
            return _objPosloc

        elif type == 'poslocTZ01':
            _poslocTZ01 = pm.spaceLocator(n='{}__pos_locatorTZpositive'.format(str(self.geo)), p = self.zmax) 
            _poslocTZ01.localScale.set([0.3,0.3,0.3])
            adb.changeColor_func(_poslocTZ01, 'index', 18)            
            return _poslocTZ01

        elif type == 'poslocTZ02':
            _poslocTZ02 = pm.spaceLocator(n='{}__pos_locatorTZnegative'.format(str(self.geo)), p = self.zmin)   
            _poslocTZ02.localScale.set([0.3,0.3,0.3])
            adb.changeColor_func(_poslocTZ02, 'index', 18)   
            return _poslocTZ02

        elif type == 'poslocTX01':
            _poslocTX01 = pm.spaceLocator(n='{}__pos_locatorTXpositive'.format(str(self.geo)), p = self.xmax)   
            _poslocTX01.localScale.set([0.3,0.3,0.3])
            adb.changeColor_func(_poslocTX01, 'index', 4)            
            return _poslocTX01

        elif type == 'poslocTX02':
            _poslocTX02 = pm.spaceLocator(n='{}__pos_locatorTXnegative'.format(str(self.geo)), p = self.xmin)   
            _poslocTX02.localScale.set([0.3,0.3,0.3])
            adb.changeColor_func(_poslocTX02, 'index', 4)  
            return _poslocTX02


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
            
             ## Node creations
            
            self.ZtiltconNode = pm.shadingNode('condition',asUtility=1, n="{}__Ztilt_condition".format(str(self.geo)))
            self.Ztilt_MD = pm.shadingNode('multiplyDivide', asUtility = 1 , n = "{}__Ztilt_multiplyDivide".format(str(self.geo)))

            self.ZtiltconNode.operation.set(2)
            self.Ztilt_MD.operation.set(1)
            self.Ztilt_MD.input2Z.set(10) 

           
            ptCont = pm.pointConstraint(self.geo , self.objPosloc, mo=False) 
            pm.delete(ptCont)        


            ptCont = pm.pointConstraint(self.poslocTZ01 , self.pivotloc, mo=False) 
            pm.delete(ptCont)

            self.poslocTZ01Shape = self.poslocTZ01.getShape()
            self.poslocTZ02Shape = self.poslocTZ02.getShape()


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

            Lastgrp = pm.group(self.driverloc , self.poslocTZ01, self.poslocTZ02, self.target_parent_grp)                        
        

        elif self.axe == 'x':   

            """ -------------------- X AXIS -------------------- """

            ptCont = pm.pointConstraint(self.poslocTX01 , self.pivotloc, mo=False) 
            pm.delete(ptCont)

            self.poslocTX01Shape = self.poslocTX01.getShape()
            self.poslocTX02Shape = self.poslocTX02.getShape()

             ## Node creations

            self.XtiltconNode = pm.shadingNode('condition',asUtility=1, n="Xtilt_condition")
            pm.rename(self.XtiltconNode,str(self.geo)+"_Xtilt_condition")

            self.Xtilt_MD = pm.shadingNode('multiplyDivide', asUtility = 1 , n = "Xtilt_multiplyDivide")
            pm.rename(self.Xtilt_MD,str(self.geo)+"_Xtilt_multiplyDivide")

            self.XtiltconNode.operation.set(3)
            self.Xtilt_MD.operation.set(1)
            self.Xtilt_MD.input2X.set(-10) 

            ptCont = pm.pointConstraint(self.geo , self.objPosloc, mo=False) 
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

            Lastgrp = pm.group(self.driverloc , self.poslocTX01, self.poslocTX02, self.target_parent_grp)            


        elif self.axe == 'both':               

            """ -------------------- Z AND X AXIS -------------------- """

            ## Node creations
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

            self.poslocTX01Shape = self.poslocTX01.getShape()
            self.poslocTX02Shape = self.poslocTX02.getShape()
            self.poslocTZ01Shape = self.poslocTZ01.getShape()
            self.poslocTZ02Shape = self.poslocTZ02.getShape()

            ptCont = pm.pointConstraint(self.poslocTX01 , self.pivotloc, mo=False) 
            pm.delete(ptCont)
                        
            ptCont2 = pm.pointConstraint(self.poslocTZ01 , self.pivotloc, mo=False) 
            pm.delete(ptCont2)

            ## Connections ##                           
            self.pivotloc.translate >> self.driverloc.rotatePivot
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

            Lastgrp = pm.group(self.driverloc , self.poslocTZ01, self.poslocTZ02, self.poslocTX02, self.poslocTX01, self.target_parent_grp)            

        ## setter Hiearchie et Clean Up ##
        pm.parentConstraint(self.objPosloc, pm.PyNode(self.target_parent_grp).getChildren()[0], mo = True) 
        
        pm.parent(self.pivotloc,self.driverloc)
        mc.parentConstraint(str(self.objPosloc),self.target_parent_grp, mo=True)
        mc.scaleConstraint(str(self.objPosloc),self.target_parent_grp, mo=True)
        mc.parent(str(self.objPosloc),str(self.driverloc))
                      
        geo_name = str(self.geo)
        try:
            geo_new_name = geo_name.replace(geo_name.split('__')[2],'{}_tilt_grp'.format(self.axe))
        except IndexError: 
            geo_new_name = ('{}_{}_tilt_grp'.format(geo_name,self.axe))
            
        pm.rename ( Lastgrp, geo_new_name)
        

        driver_loc_grp = adb.makeroot_func(self.driverloc)
        pm.parentConstraint(self.mesh_ctrl_offset,driver_loc_grp, mo=True)
        pm.scaleConstraint(self.mesh_ctrl_offset,driver_loc_grp, mo=True)
        pm.PyNode(self.target_parent_grp).getChildren()[0].getShape().v.set(0)




