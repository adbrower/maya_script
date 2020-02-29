# -------------------------------------------------------------------
# Class BoundingBox Module
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# -------------------------------------------------------------------

from adbrower import changeColor
import maya.cmds as mc
import pymel.core as pm
import adbrower
adb = adbrower.Adbrower()

# -----------------------------------
#  CLASS
# -----------------------------------

# NOTES CMDS ------------------------------------------------------------
# -----------------------------------------------------------------------
# pos = cmds.xform(sub, q=1, ws=1, boundingBoxInvisible=1)

# POSminZ = [pos[3], ((pos[1] + pos[4])/2), pos[2]]
# POSminZ = [pos[3], ((pos[1] + pos[4])/2), pos[5]]

# POSminX = [pos[0], ((pos[1] + pos[4])/2), pos[5]]
# POSmaxX = [pos[0], ((pos[1] + pos[4])/2), pos[2]]

# print POSminZ, POSminZ, POSminX, POSmaxX

# -----------------------------------------------------------------------



class Bbox_Array(object):
    """
    bbox is a 6-element list of XYZ min and XYZ max: [xmin, ymin, zmin, xmax, ymax, zmax].
    If you want the pivot point to be the bottom center,
    you'll want the average X, minimum Y, and average Z

    Base on list of array of 6

    @param array: (list)

    ## EXTERIOR CLASS BUILD
    #------------------------
    from adb_utils.rig_utils.Class__BoundingBox  import Bbox_Array

    posBox = Bbox_Array([1,2,3,4,5,6])
    posBox.createPosLocs()
    """

    def __init__(self, array):

        if isinstance(array, pm.datatypes.BoundingBox):
            self.boundingbox = array
        else:
            _spheres = [pm.polySphere(r=0.01)[0] for x in xrange(6)]
            for sphere, points, axe in zip(_spheres, array, 'xyzxyz'):
                sphere.setAttr('t{}'.format(axe), points)
            pm.select(_spheres, r=1)
            _lattrice = pm.lattice(pm.selected(), divisions=(2, 2, 2), ldv=(2, 2, 2), objectCentered=True)
            self.boundingbox = (_lattrice[-1]).getBoundingBox()
            pm.delete(_lattrice)
            pm.delete(_spheres)

        self.getAllPos()
        self.all_locs = []
        self.axisDic = {
            'all': 'all',
            'x': 0,
            'y': 1,
            'z': 2,
        }

    def posCenter(self, loc=True, axis='all'):
        """ Get the center position """
        self.axis = axis
        if loc:
            loc_center = self.mminiLoc(self.boundingbox.center(), 'center__loc__')
            self.all_locs.append(loc_center)

        if self.axis == 'all':
            return self.boundingbox.center()
        else:
            return self.boundingbox.center()[self.axisDic[self.axis]]

    def posTop(self, loc=True, axis='all'):
        """ Get the top position """
        self.axis = axis
        if loc:
            loc_top = self.mminiLoc(self.top, 'top__loc__')
            self.all_locs.append(loc_top)

        if self.axis == 'all':
            return self.top
        else:
            return self.top[self.axisDic[self.axis]]

    def posBot(self,  loc=True, axis='all'):
        """ Get the bottom position """
        self.axis = axis
        if loc:
            loc_bot = self.mminiLoc(self.bottom, 'bot__loc__')
            self.all_locs.append(loc_bot)

        if self.axis == 'all':
            return self.bottom
        else:
            return self.bottom[self.axisDic[self.axis]]

    def posMinZ(self,  loc=True, axis='all'):
        """ Get the minimum Z position """

        self.axis = axis
        if loc:
            loc_minz = self.mminiLoc(self.minZ, 'minZ__loc__')
            self.all_locs.append(loc_minz)

        if self.axis == 'all':
            return self.minZ
        else:
            return self.minZ[self.axisDic[self.axis]]

    def posMaxZ(self,  loc=True, axis='all'):
        """ Get the maximum Z position """
        self.axis = axis
        if loc:
            loc_maxz = self.mminiLoc(self.maxZ, 'maxZ__loc__'.format(self.oGeo_string))
            self.all_locs.append(loc_maxz)

        if self.axis == 'all':
            return self.maxZ
        else:
            return self.maxZ[self.axisDic[self.axis]]

    def posMinX(self, loc=True, axis='all'):
        """ Get the minimum X position """
        self.axis = axis
        if loc:
            loc_minx = self.mminiLoc(self.minX, 'minX__loc__')
            self.all_locs.append(loc_minx)

        if self.axis == 'all':
            return self.minX
        else:
            return self.minX[self.axisDic[self.axis]]

    def posMaxX(self, loc=True, axis='all'):
        """ Get the maximum X position """
        self.axis = axis
        if loc:
            loc_maxx = self.mminiLoc(self.maxX, 'maxX__loc__')
            self.all_locs.append(loc_maxx)

        if self.axis == 'all':
            return self.maxX
        else:
            return self.maxX[self.axisDic[self.axis]]

    def getAllPos(self):
        """Get all positions according to the boundingBox """
        box = self.boundingbox
        self.top = [box.center()[0], box.max()[1], box.center()[2]]
        self.bottom = [box.center()[0], box.min()[1], box.center()[2]]

        # Au niveau du sol
        self.bot_minZ = [box.center()[0], box.min()[1], box.min()[2]]
        self.bot_maxZ = [box.center()[0], box.min()[1], box.max()[2]]

        self.minX = [box.min()[0], box.min()[1], box.center()[2]]
        self.maxX = [box.max()[0], box.min()[1], box.center()[2]]

        # Au niveau du centre
        self.minZ = [box.center()[0], box.center()[1], box.min()[2]]
        self.maxZ = [box.center()[0], box.center()[1], box.max()[2]]

        self.minX = [box.min()[0], box.center()[1], box.center()[2]]
        self.maxX = [box.max()[0], box.center()[1], box.center()[2]]

        return(self.minX, self.bottom, self.minZ, self.maxX, self.top, self.maxZ)

    @changeColor('index', col=(17))
    def mminiLoc(self, pos, name):
        miniloc = pm.spaceLocator(position=pos, n=name)
        miniloc.localScaleX.set(0.2)
        miniloc.localScaleY.set(0.2)
        miniloc.localScaleZ.set(0.2)
        pm.xform(miniloc, cp=1)
        return miniloc

    def createPosLocs(self):
        """Create locators at different positions according to the boundingBox"""
        self.getAllPos()
        loc_top = self.mminiLoc(self.top, 'top__loc__')
        loc_bot = self.mminiLoc(self.bottom, 'bot__loc__')
        loc_minz = self.mminiLoc(self.minZ, 'minZ__loc__')
        loc_maxz = self.mminiLoc(self.maxZ, 'maxZ__loc__')
        loc_minx = self.mminiLoc(self.minX, 'minX__loc__')
        loc_maxx = self.mminiLoc(self.maxX, 'maxX__loc__')

        self.all_locs.append(loc_top)
        self.all_locs.append(loc_bot)
        self.all_locs.append(loc_minz)
        self.all_locs.append(loc_maxz)
        self.all_locs.append(loc_minx)
        self.all_locs.append(loc_maxx)

        pm.select(self.all_locs, r=True)
        return loc_minx, loc_bot, loc_minz, loc_maxx, loc_top, loc_maxz


# ================================== CLASS  =============================================

class Bbox(object):
    """
    bbox is a 6-element list of XYZ min and XYZ max: [xmin, ymin, zmin, xmax, ymax, zmax].
    If you want the pivot point to be the bottom center,
    you'll want the average X, minimum Y, and average Z

    Base on meshes.

    @param geo: Transform


    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_core.Class__BoundingBox  as adbBBox
    reload (adbBBox)

    posBox = Bbox(pm.selected())
    posBox.createPosLocs()
    """

    def __init__(self,
                 geo=pm.selected(),
                 ):

        self.oGeo = geo

        if isinstance(self.oGeo, list):
            self.oGeo = geo
        elif isinstance(self.oGeo, basestring):
            self.oGeo = [geo]
        elif isinstance(self.oGeo, unicode):
            self.oGeo = [pm.PyNode(geo)]
        else:
            self.oGeo = [geo]

        if len(self.oGeo) == 1:
            self.bbox = [pm.PyNode((self.oGeo[0])).getBoundingBox()]

        elif len(self.oGeo) > 1:
            _lattrice = pm.lattice(self.oGeo, divisions=(2, 2, 2), ldv=(2, 2, 2), objectCentered=True)
            self.bbox = [(_lattrice[-1]).getBoundingBox()]
            pm.delete(_lattrice)

        self.oGeo_string = [str(x) for x in self.oGeo][0]
        self.all_locs = []
        self.axisDic = {
            'all': 'all',
            'x': 0,
            'y': 1,
            'z': 2,
        }

        self.getAllPos()

    def __repr__(self):
        return str('<{} \'{}\'>'.format(self.__class__.__name__, self.oGeo))

    @classmethod
    def forEach(cls):
        all_mesh = []
        for i in pm.selected():
            bbb = Bbox([i])
            bbb.getAllPos()
            bbb.createPosLocs()
            all_mesh.append(i)
        return cls(all_mesh)

    @staticmethod
    def fromComponent():
        sel = pm.selected(fl=1)
        _lattrice = pm.lattice(sel, divisions=(2, 2, 2), ldv=(2, 2, 2), objectCentered=True, n=sel[0].split('Shape')[0] + '_')
        bbox = (_lattrice[-1]).getBoundingBox()
        _bbox = Bbox([_lattrice[1]])
        _bbox.getAllPos()
        _bbox.createPosLocs()
        pm.delete(_lattrice)
        return (bbox)

    @staticmethod
    def fromSelection():
        _meshes = Bbox(pm.selected())
        _meshes.getAllPos()
        _meshes.createPosLocs()
        print _meshes

    @property
    def height(self):
        return self.bbox[0].height()

    @property
    def width(self):
        return self.bbox[0].width()

    @property
    def getBbox(self):
        if len(self.bbox) > 1:
            return self.bbox
        else:
            return self.bbox[0]

    def posCenter(self, loc=True, axis='all'):
        """ Get the center position """
        self.axis = axis
        if loc:
            loc_center = self.mminiLoc(self.getBbox.center(), '{}_center__loc__')
            self.all_locs.append(loc_center)

        if self.axis == 'all':
            return self.getBbox.center()
        else:
            return self.getBbox.center()[self.axisDic[self.axis]]

    def posTop(self, loc=True, axis='all'):
        """ Get the top position """
        self.axis = axis
        if loc:
            loc_top = self.mminiLoc(self.top, '{}_top__loc__')
            self.all_locs.append(loc_top)

        if self.axis == 'all':
            return self.top
        else:
            return self.top[self.axisDic[self.axis]]

    def posBot(self,  loc=True, axis='all'):
        """ Get the bottom position """
        self.axis = axis
        if loc:
            loc_bot = self.mminiLoc(self.bottom, '{}_bot__loc__'.format(self.oGeo_string))
            self.all_locs.append(loc_bot)

        if self.axis == 'all':
            return self.bottom
        else:
            return self.bottom[self.axisDic[self.axis]]

    def posMinZ(self,  loc=True, axis='all'):
        """ Get the minimum Z position """
        self.axis = axis
        if loc:
            loc_minz = self.mminiLoc(self.minZ, '{}_minZ__loc__'.format(self.oGeo_string))
            self.all_locs.append(loc_minz)

        if self.axis == 'all':
            return self.minZ
        else:
            return self.minZ[self.axisDic[self.axis]]

    def posMaxZ(self,  loc=True, axis='all'):
        """ Get the maximum Z position """
        self.axis = axis
        if loc:
            loc_maxz = self.mminiLoc(self.maxZ, '{}_maxZ__loc__'.format(self.oGeo_string))
            self.all_locs.append(loc_maxz)

        if self.axis == 'all':
            return self.maxZ
        else:
            return self.maxZ[self.axisDic[self.axis]]

    def posMinX(self, loc=True, axis='all'):
        """ Get the minimum X position """
        self.axis = axis
        if loc:
            loc_minx = self.mminiLoc(self.minX, '{}_minX__loc__'.format(self.oGeo_string))
            self.all_locs.append(loc_minx)

        if self.axis == 'all':
            return self.minX
        else:
            return self.minX[self.axisDic[self.axis]]

    def posMaxX(self, loc=True, axis='all'):
        """ Get the maximum X position """
        self.axis = axis
        if loc:
            loc_maxx = self.mminiLoc(self.maxX, '{}_maxX__loc__'.format(self.oGeo_string))
            self.all_locs.append(loc_maxx)

        if self.axis == 'all':
            return self.maxX
        else:
            return self.maxX[self.axisDic[self.axis]]

    @changeColor('index', col=(17))
    def mminiLoc(self, pos, name):
        miniloc = pm.spaceLocator(position=pos, n=name)
        miniloc.localScaleX.set(0.2)
        miniloc.localScaleY.set(0.2)
        miniloc.localScaleZ.set(0.2)
        pm.xform(miniloc, cp=1)
        return miniloc

    def getAllPos(self):
        """Get all positions according to the boundingBox """

        for box in self.bbox:
            self.top = [box.center()[0], box.max()[1], box.center()[2]]
            self.bottom = [box.center()[0], box.min()[1], box.center()[2]]

            # Au niveau du sol
            self.bot_minZ = [box.center()[0], box.min()[1], box.min()[2]]
            self.bot_maxZ = [box.center()[0], box.min()[1], box.max()[2]]

            self.minX = [box.min()[0], box.min()[1], box.center()[2]]
            self.maxX = [box.max()[0], box.min()[1], box.center()[2]]

            # Au niveau du centre
            self.minZ = [box.center()[0], box.center()[1], box.min()[2]]
            self.maxZ = [box.center()[0], box.center()[1], box.max()[2]]

            self.minX = [box.min()[0], box.center()[1], box.center()[2]]
            self.maxX = [box.max()[0], box.center()[1], box.center()[2]]

        return(self.minX, self.bottom, self.minZ, self.maxX, self.top, self.maxZ)

    def createPosLocs(self):
        """Create locators at different positions according to the boundingBox"""
        loc_top = self.mminiLoc(self.top, '{}_top__loc__'.format(self.oGeo_string))
        loc_bot = self.mminiLoc(self.bottom, '{}_bot__loc__'.format(self.oGeo_string))
        loc_minz = self.mminiLoc(self.minZ, '{}_minZ__loc__'.format(self.oGeo_string))
        loc_maxz = self.mminiLoc(self.maxZ, '{}_maxZ__loc__'.format(self.oGeo_string))
        loc_minx = self.mminiLoc(self.minX, '{}_minX__loc__'.format(self.oGeo_string))
        loc_maxx = self.mminiLoc(self.maxX, '{}_maxX__loc__'.format(self.oGeo_string))

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
