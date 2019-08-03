
# -------------------------------------------------------------------
# Class Wrap Module
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
# audreydb23@gmail.com
# -------------------------------------------------------------------

import sys
from functools import wraps

import adb_utils.Class__AddAttr as adbAttr
import adbrower
import maya.cmds as mc
import pymel.core as pm
from adbrower import flatList

# reload(adbrower)
adb = adbrower.Adbrower()
# reload(adbAttr)

#-----------------------------------
# DECORATORS
#-----------------------------------


def undo(func):
    """
    Puts the wrapped `func` into a single Maya Undo action, then
    undoes it when the function enters the finally: block
    from schworer Github
    """
    @wraps(func)
    def _undofunc(*args, **kwargs):
        try:
            # start an undo chunk
            mc.undoInfo(ock=True)
            return func(*args, **kwargs)
        finally:
            # after calling the func, end the undo chunk
            mc.undoInfo(cck=True)
    return _undofunc


#-----------------------------------
# CLASS
#-----------------------------------

class Wrap(object):
    """
    A Module containing multiples wrap deformer methods

    @param _node: Single string or a list. Default value is pm.selected()

    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_utils.Class__Wrap as wrap
    reload (wrap)
    """

    def __init__(self,
                 _node = pm.selected(),
                 ):

        pass


    @classmethod
    def findAll(cls):
        """ Return a Wrap instance for every cluster node in the scene. """
        all_wraps = []
        for wrap_name in pm.ls(type='wrap'):
            all_wraps.append(cls(wrap_name))
        return all_wraps

    @property
    def loRez(self):
        base_connection = pm.listConnections('{}.driverPoints'.format(self.wrapNode), p=True)[0]
        lo = str(base_connection.split('.')[0])
        lo_transform = pm.PyNode(lo).getParent()
        return lo_transform

    @property
    def hiRez(self):
        base_connection = pm.listConnections('{}.outputGeometry'.format(self.wrapNode), d=True)[0]
        return str(base_connection.split('.')[0])


    @property
    def getShapeOrig(self):
        shapeOrig_node = self.shapeOrig(loRez)
        return self.shapeOrig_node


    @property
    def base_shape(self):
        base_connection = pm.listConnections('{}.basePoints'.format(self.wrapNode), p=True)[0]
        return str(base_connection.split('.')[0])


    def shapeOrig(self, _transformName):
        """
        Get Original node
        """
        result = ''
        if not pm.objExists(_transformName):
            return result

        result = pm.PyNode(_transformName).getShapes()[-1]
        if 'Orig' in str(result):
            return result
        else:
            # print("No 'Orig' Node for: {}".format(_transformName))
            return None

    @undo
    def create(self, _HiRez = pm.selected(), _LoRez=pm.selected()):
        """
        Creates a default wrap
        Select target - HiRez first, then the source - LoRez
        @param Hirez: Target which will receive the wrap : str or selection
        @param Lorez: Source : str of selection
        """

        ## Define Variable type
        if isinstance(_HiRez, str) and isinstance(_LoRez, str):
            print('string')
            HiRez = _HiRez
            LoRez = _LoRez

        elif len(_HiRez) == 2:
            print('selection of 2')
            HiRez = _HiRez[0]
            LoRez = _LoRez[1]

        else:
            print('Else')
            HiRez = _HiRez
            LoRez = _LoRez

        pre_wraps = set(pm.ls(type='wrap'))
        pm.select(HiRez, LoRez, r=True)
        mc.CreateWrap()
        post_wraps = set(pm.ls(type='wrap'))
        wrapNode = list(post_wraps - pre_wraps)[0]
        name = pm.rename(wrapNode, '{}_wrap'.format(HiRez))

        self.wrapNode = None
        self.wrapNode = wrapNode
        sys.stdout.write('wrap deformer created \n')
        return self.wrapNode


    @undo
    def createCustom(self, _HiRez = pm.selected(), _LoRez=pm.selected()):

        """
        Custom wrapDeformer
        Select target - HiRez first, then the source - LoRez
        @param Hirez: Target which will receive the wrap : str or selection
        @param Lorez: Source : str of selection

        ## EXTERIOR CLASS BUILD
        #------------------------
        import adb_utils.Script__WrapDeformer as adbWrap
        reload(adbWrap)

        #or
        from adb_utils.Script__WrapDeformer import wrapDeformer
        """
        ## Define Variable type
        if isinstance(_HiRez, str) and isinstance(_LoRez, str):
            # print('a')
            HiRez = _HiRez
            LoRez = _LoRez

        elif len(_HiRez) == 2:
            # print('b')
            HiRez = _HiRez[0]
            LoRez = _LoRez[1]

        else:
            # print('c')
            HiRez = _HiRez
            LoRez = _LoRez


        ## get Orig node
        orig_node = self.shapeOrig(LoRez)
        if orig_node is None:
            cls = pm.cluster(LoRez)
            pm.delete(cls)
            orig_node = self.shapeOrig(LoRez)
            # raise RuntimeError("No 'Orig' Node for: {}".format(LoRez))

        ## Wrap Node creation
        pm.select(HiRez, r=True)
        pm.select(LoRez, add=True)
        wrapData = pm.deformer(HiRez, name = '{}_{}'.format(HiRez, 'wrap'), type='wrap')[0]

        pm.PyNode(wrapData).maxDistance.set(1)
        pm.PyNode(wrapData).autoWeightThreshold.set(1)
        pm.PyNode(wrapData).exclusiveBind.set(0)
        pm.PyNode(wrapData).falloffMode.set(0)

        ## add custom attribute on LoRez mesh
        if adb.attrExist(LoRez, 'dropoff'):
            pass
        else:
            LoRez_node = adbAttr.NodeAttr([LoRez])
            LoRez_node.addAttr('dropoff', 4)
            LoRez_node.addAttr('smoothness', 0)
            LoRez_node.addAttr('inflType', 2)

        ## Connections
        (pm.PyNode(LoRez).getShape()).worldMesh[0] >> pm.PyNode(wrapData).driverPoints[0]
        (pm.PyNode(HiRez).getShape()).worldMatrix[0] >> pm.PyNode(wrapData).geomMatrix
        pm.PyNode(LoRez).dropoff >> pm.PyNode(wrapData).dropoff[0]
        pm.PyNode(LoRez).inflType >> pm.PyNode(wrapData).inflType[0]
        pm.PyNode(LoRez).smoothness >> pm.PyNode(wrapData).smoothness[0]
        pm.PyNode(orig_node).worldMesh[0] >> pm.PyNode(wrapData).basePoints[0]


        ## Clean Up)
        pm.PyNode(LoRez).v.set(0)

        sys.stdout.write('custom wrap deformer created \n')

        self.wrapNode = None
        self.wrapNode = wrapData
        return self.wrapNode

    @undo
    def replaceBasebyOrig(self, wrap_node, loRez_transform):
        """
        Remove the base shape and replace it with the Orig node
        @param wrap_node: string or transform
        """
        base_connection = pm.listConnections('{}.basePoints'.format(wrap_node), p=True)[0]
        base_shape = str(base_connection.split('.')[0])

        orig_node = self.shapeOrig(loRez_transform)
        if orig_node is None:
            cls = pm.cluster(loRez_transform)
            pm.delete(cls)
            orig_node = self.shapeOrig(loRez_transform)

        pm.PyNode(orig_node).worldMesh[0] >> pm.PyNode(wrap_node).basePoints[0]
        pm.delete(pm.PyNode(base_shape).getParent())




# wrap = Wrap()
