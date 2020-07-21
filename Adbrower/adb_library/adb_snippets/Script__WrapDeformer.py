import traceback
import sys

import maya.cmds as mc
import pymel.core as pm

import adbrower
# reload(adbrower)
adb = adbrower.Adbrower()
import adb_core.Class__AddAttr as adbAttr
# reload(adbAttr)


def wrapDeformer(_HiRez = pm.selected(), _LoRez=pm.selected()):
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
        print('a')
        HiRez = _HiRez
        LoRez = _LoRez       
    
    elif len(_HiRez) == 2:    
        print('b')
        HiRez = _HiRez[0]
        LoRez = _LoRez[1]
    
    else:
        print('c')
        HiRez = _HiRez
        LoRez = _LoRez         

    ## get Orig node
    orig_node = adb.getShapeOrig(LoRez)
    if orig_node == None:
        cls = pm.cluster(LoRez)
        pm.delete(cls)    
        orig_node = adb.getShapeOrig(LoRez)        
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
            
    return wrapData
    
    
# wrapDeformer()