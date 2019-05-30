import traceback
import maya.cmds as mc
import pymel.core as pm
import sys 

import adb_utils.adb_script_utils.Script__WrapDeformer as adbWrap
import adb_utils.Class__AddAttr as adbAttr


def wrapSetUp(_HiRez = pm.selected(), _LoRez=pm.selected()):
    '''
    Custom wrapDeformer Setup
    Select target - HiRez first, then the source - LoRez
    The script will create a duplicate of the HiRez with a blenshape and add a DeltaMush on the HiRez

    @param Hirez: Target which will receive the wrap 
    @param Lorez: Source     
    
    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_utils.Script__WrapDeformer_Setup as adbWrapSetUp
    reload(adbWrapSetUp)

    #or
    from adb_utils.Script__WrapDeformer_Setup import wrapSetUp             
    '''

    ## Define Variable type
    if str(type(_HiRez)) and str(type(_LoRez)) == "<type 'str'>":
        hi = _HiRez
        lo = _LoRez       
    elif len(_HiRez) == 2:    
        hi = _HiRez[0]
        lo = _LoRez[1]
    
    
    dup = pm.duplicate(hi, n='{}__{}__'.format(hi,'duplicate_wrap'), ic=1, rr=1)[0]
   
    wrapData = adbWrap.wrapDeformer(str(dup),str(lo))

    ## add custom attribute on wrap node
    wrap_node = adbAttr.NodeAttr([wrapData])
    wrap_node.addAttr('mushEnveloppe', 1)
    wrap_node.addAttr('smoothingIterations', 10)
    wrap_node.addAttr('smoothingStep', 0.5)

    ## blendShape
    blendShape = pm.blendShape(dup, hi, exclusive="deformPartition#", o = "world", w = [(0, 1.0)], ib=1, n = '{}__{}__'.format(hi, 'BLS'))[0]

    ## Mush
    mush = pm.deltaMush(hi, smoothingIterations=10, envelope=1, smoothingStep=0.5, pinBorderVertices=1,  n = '{}_{}'.format(hi, 'mush'))

    pm.PyNode(wrapData).mushEnveloppe >> pm.PyNode(mush).envelope
    pm.PyNode(wrapData).smoothingIterations >> pm.PyNode(mush).smoothingIterations
    pm.PyNode(wrapData).smoothingStep >> pm.PyNode(mush).smoothingStep

    ## Clean Up
    pm.PyNode(dup).v.set(0)
    

# wrapSetUp()

