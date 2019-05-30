# ------------------------------------------------------------------------------------------------------
# Rigging Joint Generator Tool
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------------------------------------------------------

import traceback
import maya.cmds as mc
import pymel.core as pm

import adbrower
reload(adbrower)

adb = adbrower.Adbrower()

from adbrower import lprint
from adbrower import flatList
from adbrower import undo
 
@undo
def locGenerator(intervals, obj1, obj2):
    '''
    This fonction builds the locators which are guide for futur joints
    
    import adb_utils.adb_script_utils.Script__LocGenerator as locGen
    reload (locGen)
    '''

    GuideLocList = []   
    posStart = pm.PyNode(obj1).getRotatePivot(space='world')
    posEnd = pm.PyNode(obj2).getRotatePivot(space='world')

    # CALCULATE DISTANCE VECTOR

    dist = []
    distX = posEnd[0] - posStart[0]
    distY = posEnd[1] - posStart[1]
    distZ = posEnd[2] - posStart[2]
    dist.append(distX)
    dist.append(distY)
    dist.append(distZ)

    # EVALUATE EACH INTERVAL IN THE LIST FOR X, Y and Z

    intervalList = range(0, intervals)
    proxy_posX_list = []
    proxy_posY_list = []
    proxy_posZ_list = []

    # CALCULATE X, Y and Z intervals

    for each in intervalList:
        each = each/float(intervals -1)
        eachX = each * dist[0]
        proxy_posX_list.append(eachX)
        eachY = each * dist[1]
        proxy_posY_list.append(eachY)
        eachZ = each * dist[2]
        proxy_posZ_list.append(eachZ)
        if posEnd < 0:
            intervalList = range(0, intervals, 1)

    for count, posX in enumerate(proxy_posX_list):
        posY = proxy_posY_list[count]
        posZ = proxy_posZ_list[count]

        @undo
        def myGuideLocs():            
            GuideLoc = pm.spaceLocator(p=(posX + posStart[0], posY + posStart[1], posZ + posStart[2]))
            pm.xform(centerPivots=True)

            GuideLocList.append(GuideLoc)
            GuideLoc.overrideEnabled.set(1)
            GuideLoc.overrideRGBColors.set(0)
            GuideLoc.overrideColor.set(17)
            
            locPx = GuideLoc.localPositionX.get()
            locPy = GuideLoc.localPositionY.get()
            locPz = GuideLoc.localPositionZ.get()
            
            GuideLoc.translateX.set(locPx)
            GuideLoc.translateY.set(locPy)
            GuideLoc.translateZ.set(locPz)
            
            GuideLoc.localPositionX.set(0)
            GuideLoc.localPositionY.set(0)
            GuideLoc.localPositionZ.set(0)
            
            pm.xform(GuideLoc, cp=True)
            
        myGuideLocs()

    #This line deletes first 2 locators#   

    # pm.delete(obj1)
    # pm.delete(obj2)
    pm.select(GuideLocList)
    return GuideLocList



# locGenerator(10, pm.selected()[0], pm.selected()[1])