# -------------------------------------------------------------------
# Class Locator
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# -------------------------------------------------------------------

import adb_core.Class__Transforms as adbTransform
import adbrower
import maya.cmds as mc
import maya.OpenMaya as om
import pymel.core as pm
from adbrower import changeColor, flatList, makeroot

adb = adbrower.Adbrower()

#-----------------------------------
# CLASS
#-----------------------------------


class Locator(adbTransform.Transform):
    """
    A Module containing multiples locrators methods
    """

    def __init__(self,
                 _locator,
                 ):

        self.locators = _locator

        if isinstance(self.locators, list):
            self.locators = [pm.PyNode(x) for x in _locator]
        elif isinstance(self.locators, basestring):
            self.locators = [_locator]
        else:
            self.locators = _locator

        super(Locator, self).__init__(self.locators)

    def __repr__(self):
        return str('<{} \'{}\'>'.format(self.__class__.__name__, self.locators))


    @classmethod
    def findAll(cls):
        """ Return a Joint instance for every joint node in the scene. """
        return cls([loc for loc in pm.ls(type='locator')])


    @classmethod
    def fromSelected(cls):
        """ Return a instance for a list with all selected """
        return cls([(loc) for loc in pm.selected()])


    @classmethod
    def create(cls, numb = 1, name = '', padding=None):
        loc_created = []
        for number in xrange(numb):
            if padding:
                loc = pm.spaceLocator(n='{}_{:0{}d}'.format(name, number+1, padding))
            else:
                loc = pm.spaceLocator(n=name)
            pm.parent(loc, w=1)
            loc_created.append(loc)
        return cls(loc_created)


    @classmethod
    def point_base(cls, *point_array,  **kwargs):

        """
        @param *point_array : (list) Each element of the list need to be a vector value (x,y,z)
                                     and it will be unpack
        @param name        : (String)

        # example
        points =[[0.0, 0.0, 0.0],[-2.54, 4.68, -0.96],[2.66, 4.66, -6.16], [0.66, 8.22, -6.83]]
        test = adbLoc.Locator.point_base(*points)
        """

        name = kwargs.pop('name', 'locator1')
        padding = kwargs.pop('padding', False)

        locs_array = []
        for index, point in enumerate(point_array):
            pm.select(None)
            if padding:
                new_loc = pm.spaceLocator(p=point, name='{}_{:0{}d}'.format(name, number+1, padding))
            else:
                new_loc = pm.spaceLocator(p=point, name=name)
            pm.PyNode(new_loc).setRotatePivot(point)
            locs_array.append(new_loc)
        return cls(locs_array)


    @classmethod
    def selection_base(cls, *args,  **kwargs):

        """
        @param *point_array : (list) Each element of the list need to be a vector value (x,y,z)
                                     and it will be unpack
        @param name        : (String)

        # example
        points =[[0.0, 0.0, 0.0],[-2.54, 4.68, -0.96],[2.66, 4.66, -6.16], [0.66, 8.22, -6.83]]
        test = adbLoc.Locator.selection_base()
        """

        name = kwargs.pop('name', 'locator1')

        locs_array = []
        for sel in pm.selected():
            loc_align = pm.spaceLocator(n= name)
            locs_array.append(loc_align)
            pm.matchTransform(loc_align, sel, pos = True)
            pm.select(locs_array, add = True)
            mc.CenterPivot()

        return cls(locs_array)


    @classmethod
    def in_between_base(cls, intervals, obj1, obj2):
        """
        This fonction builds the locators which are guide for futur joints

        # example
        _args = [5 ,'locator1', 'locator3']
        test = adbLoc.Locator.in_between_base(*_args)
        """
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
            each = each / float(intervals - 1)
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
                [GuideLoc.setAttr('localPosition{}'.format(axis), 0) for axis in 'XYZ']
                pm.xform(GuideLoc, cp=True)
            myGuideLocs()

        pm.select(GuideLocList)
        return cls(GuideLocList)



# aaa = Locator.in_between_base(6, pm.selected()[0], pm.selected()[1])
