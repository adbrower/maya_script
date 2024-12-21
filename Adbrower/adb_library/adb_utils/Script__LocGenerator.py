# ------------------------------------------------------------------------------------------------------
# Rigging Joint Generator Tool
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------------------------------------------------------


import pymel.core as pm
from maya.api import OpenMaya as om

from adbrower import undo
 
@undo
def locGenerator(intervals, obj1, obj2):
    """
    This fonction builds the locators which are guide for futur joints
    
    import adb_utils.adb_script_utils.Script__LocGenerator as locGen
    reload (locGen)
    """
    locsList = []  
    mSLStart = om.MSelectionList()
    mSLStart.add(obj1)
    mFTransStart = om.MFnTransform(mSLStart.getDagPath(0))
    startV = om.MVector(mFTransStart.rotatePivot(om.MSpace.kWorld))

    mSLEnd = om.MSelectionList()
    mSLEnd.add(obj2)
    mFTransfEnd = om.MFnTransform(mSLEnd.getDagPath(0))
    endV = om.MVector(mFTransfEnd.rotatePivot(om.MSpace.kWorld))

    distV = endV - startV

    proxy_posX_list = []
    proxy_posY_list = []
    proxy_posZ_list = []

    # CALCULATE X, Y and Z intervals

    nInverval = intervals+2
    intervalList = range(0, nInverval)
    for each in intervalList:
        each = each/float(nInverval -1)
        eachX = each * distV.x
        proxy_posX_list.append(eachX)
        eachY = each * distV.y
        proxy_posY_list.append(eachY)
        eachZ = each * distV.z
        proxy_posZ_list.append(eachZ)
        if [endV] < 0:
            intervalList = range(0, nInverval, 1)

    @undo
    def myGuideLocs():            
        GuideLoc = pm.spaceLocator()
        pm.xform(centerPivots=True)

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
    
        return str(GuideLoc)
        
    locsList = [str(myGuideLocs()) for x in range(intervals)]

    for count, middleTransf in enumerate(locsList):
        mSLMiddle = om.MSelectionList()
        mSLMiddle.add(middleTransf)
        mFTransMiddle = om.MFnTransform(mSLMiddle.getDagPath(0))
       
        newPos = [proxy_posX_list[1:-1][count] + startV.x, proxy_posY_list[1:-1][count] + startV.y, proxy_posZ_list[1:-1][count] + startV.z]
        newPosV = om.MVector(*newPos)
    
        mFTransMiddle.setTranslation(newPosV, om.MSpace.kWorld)

    return locsList



# locGenerator(5, 'pCube1', 'pCube2')