import pymel.core as pm
import maya.cmds as mc
import sys

import adb_utils.Class__AddAttr as adbAttr
import adbrower
adb = adbrower.Adbrower()
import NameConv_utils as NC


reload(NC)
# reload (adbAttr)



#-----------------------------------
#  DECORATORS
#----------------------------------- 

from adbrower import undo
from adbrower import changeColor

#-----------------------------------
#  FUNCTIONS
#-----------------------------------


'''
import adb_utils.adb_script_utils.Functions__Rivet as adbRivet
reload(adbRivet)

function's name: buildRivet
'''

def oppositeEdgesFromFaces():
    ''' Return 2 opposite edges from a face selection  '''
    face_select = pm.selected()
    faces = pm.filterExpand(selectionMask = 34) ## Edge
    facesfromObject = faces[0].split('.')[0]
    final_edge_selection = []
    for each in face_select:    
        edges = each.getEdges()
        opposite_edges_index = edges[::2]    
        opposite_edges = []
        for index_edge in opposite_edges_index:
            edge_to_select = '{}.e[{}]'.format(facesfromObject,index_edge)
            opposite_edges.append(edge_to_select)            
        final_edge_selection.append(opposite_edges)
    return(final_edge_selection)


def buildRivet(scale = 0.2):
    ''' 
    Creates a Rivet Between 2 edges
    Returns : - Rivet locator, 
              - List of the 2 edge from curves nodes 
              - Mesh Name
    '''
    
    if not (pm.pluginInfo('matrixNodes', q=True, loaded=True)):
        pm.loadPlugin( 'matrixNodes' )        
    _edges = pm.filterExpand(selectionMask = 32) ## Edge
    
    if len(_edges) < 2:
        pm.warning('n\Need 2 edges selected')
    
    elif len(_edges) > 2:
        pm.error('Too much edges selected! Only select 2!!')
        
    else:    
        objectFromEdge = _edges[0].split('.')[0]
        edgeMaxNumber = pm.polyEvaluate(objectFromEdge, edge = True)
        objectShape = pm.PyNode(objectFromEdge).getShape()
        edgeCount = len(_edges)
        edgeNumber = [(edge.split('.e[')[1]).split(']')[0] for edge in _edges]

        ## RIVET LOC AND GRP SET UP
        rivet_grp= pm.group(em=True, name = '{}_rivet__grp__'.format(objectFromEdge))
        rivet_locator = pm.spaceLocator(name = '{}_rivet'.format(objectFromEdge))
        adb.changeColor_func(rivet_locator, 'index', col = 17)
        
        pm.PyNode(rivet_locator).localScaleX.set(scale)
        pm.PyNode(rivet_locator).localScaleY.set(scale)
        pm.PyNode(rivet_locator).localScaleZ.set(scale)
        
        pm.parent(rivet_locator, rivet_grp)
        _rivet_Attr = adbAttr.NodeAttr([rivet_locator])
        _rivet_Attr.addAttr("edges_index", 'float2', nc=2)
        _rivet_Attr.addAttr("edge_index_0", int(edgeNumber[0]), min = 0, max = edgeMaxNumber, parent = "edges_index")
        _rivet_Attr.addAttr("edge_index_1", int(edgeNumber[1]), min = 0, max = edgeMaxNumber, parent = "edges_index")
        
        print _rivet_Attr
        _rivet_Attr.addAttr("UV", 'float2', nc=2)
        _rivet_Attr.addAttr("U_pos", 0.5, min = 0, max = 1, parent = "UV")
        _rivet_Attr.addAttr("V_pos", 0.5, min = 0, max = 1, parent = "UV")

        ## NODES CREATION
        curveFromEdge_nodes = [pm.createNode('curveFromMeshEdge', name = 'curveFromEdge_{}_{}'.format(objectFromEdge, x)) for x in edgeNumber]
        loft_node = pm.createNode('loft', name = 'rivet_loft__node__')
        pm.PyNode(loft_node).degree.set(1)

        pointOnSurface_node = pm.createNode('pointOnSurfaceInfo', name = 'pointOnSurface_node')
        pm.PyNode(pointOnSurface_node).turnOnPercentage.set(1)

        matrix_node = pm.createNode('fourByFourMatrix', name = 'mat__node__')
        decomposeMatrix_node = pm.createNode('decomposeMatrix', name = 'decompMat__node__')

        ## MAKING THE CONNECTIONS
        objectShape.worldMesh >> pm.PyNode(curveFromEdge_nodes[0]).inputMesh
        objectShape.worldMesh >> pm.PyNode(curveFromEdge_nodes[1]).inputMesh

        for index in range(0, edgeCount):
            pm.PyNode('{}.{}'.format(curveFromEdge_nodes[index], 'outputCurve')) >> pm.PyNode('{}.inputCurve[{}]'.format(loft_node, index))        
        loft_node.outputSurface >> pointOnSurface_node.inputSurface
        rivet_locator.U_pos >> pointOnSurface_node.parameterU
        rivet_locator.V_pos >> pointOnSurface_node.parameterV

        pos_node_attr = ['normal', 'tangentU.tangentU', 'tangentV.tangentV', 'position.position']
        xyz = 'XYZ'

        for i in range(len(pos_node_attr)):
            for j in range(3):
                axe =  xyz[j]
                if 'tU' in pos_node_attr[i]: axe = axe.lower()
                elif 'tV' in pos_node_attr[i]: axe = axe.lower()
                pm.PyNode('{}.{}{}'.format(pointOnSurface_node, pos_node_attr[i], axe)) >> pm.PyNode('{}.in{}{}'.format(matrix_node, i, j))                
        matrix_node.output >> decomposeMatrix_node.inputMatrix
        for i in range(3):
            axe =  xyz[i]
            pm.PyNode('{}.outputRotate{}'.format(decomposeMatrix_node, axe)) >> pm.PyNode('{}.rotate{}'.format(rivet_grp, axe))
            pm.PyNode('{}.outputTranslate{}'.format(decomposeMatrix_node, axe)) >> pm.PyNode('{}.translate{}'.format(rivet_grp, axe))

        rivet_locator.edge_index_0 >> curveFromEdge_nodes[0].edgeIndex[0]
        rivet_locator.edge_index_1 >> curveFromEdge_nodes[1].edgeIndex[0]

        sys.stdout.write('// Result: Rivet created! // \n')
        return rivet_locator, curveFromEdge_nodes, objectFromEdge


def rivet_from_faces(scale = 0.2):
    '''
    Creates rivet from faces selection
    ''' 
    edge_pair = oppositeEdgesFromFaces()
    for pair in edge_pair:
        pm.select(pair, r =True)
        buildRivet(scale=scale)


def rivet_constraint(geo):
    '''
    Rivet Constraint:
        Select the subject then two edges
    '''    
    rivetLoc = buildRivet()[0]
    pm.parentConstraint(rivetLoc, geo, mo = True)


def createSticky(stickyName = 'Deformer', scale = 0.2):   
    '''
    Sticky : Creates a rivet with a softmod deformer 
    Returns the sticky locator   
    '''  
    rivetData = buildRivet()
    rivet_trans = rivetData[0]
    curveFromMeshEdgeList = rivetData[1]
    MeshName = rivetData[2]                     
    pm.PyNode(rivet_trans).v.set(0) 
        
    ## master and offset grp
    deformer__sys__ = pm.createNode('transform', n = '{}_{}__{}'.format(stickyName, NC.SYSTEM, NC.GRP))
    deformer_offset_grp__ = pm.createNode('transform', n = '{}__offset__{}'.format(stickyName, NC.GRP))
    pm.parent(deformer_offset_grp__, deformer__sys__)
        
    ## create locator
    sticky_locator = pm.spaceLocator(name = '{}_sticky'.format(MeshName))
    adb.changeColor_func(sticky_locator, 'index', col = 18)    
    pm.PyNode(sticky_locator).localScaleX.set(scale)
    pm.PyNode(sticky_locator).localScaleY.set(scale)
    pm.PyNode(sticky_locator).localScaleZ.set(scale)    
    pm.parent(sticky_locator, deformer_offset_grp__)
    pm.matchTransform(deformer_offset_grp__, rivet_trans.getParent(), rot = True, pos=True)    
    
    ## create softmod
    softModName = '{}__softMod__'.format(stickyName)
    softModDeformer = pm.softMod(MeshName,n=softModName)
    pm.softMod(softModDeformer[0], edit = True, wn=(sticky_locator,sticky_locator), fas=False, fm=False )
    pm.PyNode('{}HandleShape'.format(softModDeformer[0])).v.set(0)

    ## connect falloff Center
    adb.connect_axesAttr(deformer_offset_grp__, softModDeformer[0], outputs = ['translate'], inputs = ['falloffCenter'])  
    deformer_offset_grp__.inverseMatrix >> softModDeformer[0].bindPreMatrix
            
    _sticky_Attr = adbAttr.NodeAttr([sticky_locator])  
    _sticky_Attr.addAttr('Softmod_Falloff_Radius', 0.75, min = 0, max = 100 )  
    sticky_locator.Softmod_Falloff_Radius >> softModDeformer[0].falloffRadius
    
    ##giving new input geo to curveFromMeshEdges    
    groupPartsNodeName = pm.listConnections(softModName, t='groupParts') 
    
    for index in range(len(curveFromMeshEdgeList)):
        pm.PyNode('{}GroupParts.outputGeometry'.format(softModName)) >> curveFromMeshEdgeList[index].inputMesh        
    adb.connect_axesAttr(rivet_trans.getParent(), deformer_offset_grp__, outputs = ['translate', 'rotate'], inputs = [])  

    ## clean scene
    pm.delete(softModDeformer[1])
    pm.parent(rivet_trans.getParent(),deformer__sys__)
    pm.select(clear=True)
    
    sys.stdout.write('// Result: Sticky created // \n ')
    return sticky_locator


def sticky_from_faces(stickyName = 'Deformer', scale = 0.2):
    '''
    Creates sticky from faces selection
    ''' 
    edge_pair = oppositeEdgesFromFaces()
    for pair in edge_pair:
        pm.select(pair, r =True)
        sticky = createSticky(stickyName = stickyName, scale = 0.2)        
    return sticky



