# -------------------------------------------------------------------
# Class BoundingBox Module
# -- Method Rigger (Maya)   
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# -------------------------------------------------------------------

import maya.cmds as mc
import pymel.core as pm

import adbrower
reload(adbrower)
adb = adbrower.Adbrower()

#-----------------------------------
#  DECORATORS
#----------------------------------- 

from adbrower import changeColor

#-----------------------------------
#  CLASS
#----------------------------------- 


class Bbox(object):
    ''' 
    bbox is a 6-element list of XYZ min and XYZ max: [xmin, ymin, zmin, xmax, ymax, zmax]. 
    If you want the pivot point to be the bottom center, 
    you'll want the average X, minimum Y, and average Z

    
    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_utils.Class__BoundingBox as adbBBox
    reload (adbBBox)
    
    posBox = Bbox(pm.selected())
    posBox.createPosLocs()
    '''
    
    def __init__(self,
                sel = pm.selected(),
                ):
        
        self.oGeo = [pm.PyNode(x) for x in sel][0]        
        self.getAllPos()
        
        self.all_locs = []
        self.axisDic = {        
            'all' : 'all',
            'x'  : 0,
            'y'  : 1,
            'z'  : 2,        
        }    

    def posTop(self, axis = 'all'):   
        ''' Get the top position '''
        self.axis = axis
        loc_top = self.mminiLoc(self.top,'{}_top__loc__'.format(self.oGeo))
        self.all_locs.append(loc_top)
        
        if self.axis == 'all':    
            return self.top        
        else:
           return self.top[self.axisDic[self.axis]]

    def posBot(self, axis = 'all'):   
        ''' Get the bottom position '''
        self.axis = axis
        loc_bot = self.mminiLoc(self.bottom,'{}_bot__loc__'.format(self.oGeo))
        self.all_locs.append(loc_bot)
        
        if self.axis == 'all':    
            return self.bottom        
        else:
           return self.bottom[self.axisDic[self.axis]]
    
    def posMinZ(self, axis = 'all'):   
        ''' Get the minimum Z position '''
        
        self.axis = axis
        loc_minz = self.mminiLoc(self.minZ,'{}_minZ__loc__'.format(self.oGeo))
        self.all_locs.append(loc_minz)
        
        if self.axis == 'all':    
            return self.minZ        
        else:
           return self.minZ[self.axisDic[self.axis]]
    
    def posMaxZ(self, axis = 'all'):   
        ''' Get the maximum Z position '''
        self.axis = axis
        loc_maxz = self.mminiLoc(self.maxZ, '{}_maxZ__loc__'.format(self.oGeo))
        self.all_locs.append(loc_maxz)
        
        
        if self.axis == 'all':    
            return self.maxZ        
        else:
           return self.maxZ[self.axisDic[self.axis]]

    def posMinX(self, axis = 'all'):   
        ''' Get the minimum X position '''
        self.axis = axis
        loc_minx = self.mminiLoc(self.minX,'{}_minX__loc__'.format(self.oGeo))
        self.all_locs.append(loc_minx)
        
        if self.axis == 'all':    
            return self.minX        
        else:
           return self.minX[self.axisDic[self.axis]]
    
    def posMaxX(self, axis = 'all'):   
        ''' Get the maximum X position '''
        self.axis = axis
        loc_maxx = self.mminiLoc(self.maxX,'{}_maxX__loc__'.format(self.oGeo))
        self.all_locs.append(loc_maxx)
        
        if self.axis == 'all':    
            return self.maxX        
        else:
           return self.maxX[self.axisDic[self.axis]]        
                        
    @changeColor(col =(1,0,0))
    def mminiLoc(self, pos, name):
        miniloc =pm.spaceLocator(position = pos, n=name)      
        miniloc.localScaleX.set(0.2)
        miniloc.localScaleY.set(0.2)
        miniloc.localScaleZ.set(0.2)
        pm.xform(miniloc, cp=1)     
        return miniloc        

        
    def getAllPos(self):
        '''Get all positions according to the boundingBox '''
        Bbox = (self.oGeo).getBoundingBox()

        self.top = [Bbox.center()[0],Bbox.max()[1],Bbox.center()[2]]
        self.bottom = [Bbox.center()[0],Bbox.min()[1],Bbox.center()[2]]

        ## Au niveau du sol
        # self.minZ = [Bbox.center()[0],Bbox.min()[1],Bbox.min()[2]]
        # self.maxZ = [Bbox.center()[0],Bbox.min()[1],Bbox.max()[2]]

        # self.minX = [Bbox.min()[0],Bbox.min()[1],Bbox.center()[2]]
        # self.maxX = [Bbox.max()[0],Bbox.min()[1],Bbox.center()[2]]

        self.minZ = [Bbox.center()[0],Bbox.center()[1],Bbox.min()[2]]
        self.maxZ = [Bbox.center()[0],Bbox.center()[1],Bbox.max()[2]]

        self.minX = [Bbox.min()[0],Bbox.center()[1],Bbox.center()[2]]
        self.maxX = [Bbox.max()[0],Bbox.center()[1],Bbox.center()[2]]
        
        return(self.minX, self.bottom, self.minZ, self.maxX, self.top, self.maxZ)

        
    def createPosLocs(self):  
        '''Create locators at different positions according to the boundingBox'''      
        loc_top = self.mminiLoc(self.top,'{}_top__loc__'.format(self.oGeo))
        loc_bot = self.mminiLoc(self.bottom,'{}_bot__loc__'.format(self.oGeo))
        loc_minz = self.mminiLoc(self.minZ,'{}_minZ__loc__'.format(self.oGeo))
        loc_maxz = self.mminiLoc(self.maxZ,'{}_maxZ__loc__'.format(self.oGeo))
        loc_minx = self.mminiLoc(self.minX,'{}_minX__loc__'.format(self.oGeo))
        loc_maxx = self.mminiLoc(self.maxX,'{}_maxX__loc__'.format(self.oGeo))
        
        self.all_locs.append(loc_top)
        self.all_locs.append(loc_bot)
        self.all_locs.append(loc_minz)
        self.all_locs.append(loc_maxz)
        self.all_locs.append(loc_minx)
        self.all_locs.append(loc_maxx)
        
        pm.select(self.all_locs, r=True)
        return loc_minx, loc_bot, loc_minz, loc_maxx, loc_top, loc_maxz
        
    def deleteLocs(self):
        pm.delete(self.all_locs)
        self.all_locs = []
        
  

