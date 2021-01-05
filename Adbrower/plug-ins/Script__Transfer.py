import pymel.core as pm
import maya.cmds as mc

from maya.api import OpenMaya as om2
import maya.OpenMayaAnim as oma
import pymel.core.datatypes as dt

neutral = 'neutral'
shapeMesh = 'neutral_shape'
targetMesh = 'target1'

def getSample(mesh):
    """
    Find closest point for each vertex
    Args:
        mesh (Transform): mesh to evaluate
    Returns:
        Dic: key: vertex / value: closest adjecent vertex
    """
    mDagMesh =  om2.MFnDagNode(om2.MGlobal.getSelectionListByName(mesh).getDependNode(0)).getPath()
    mFnMesh = om2.MFnMesh(mDagMesh)
    vertex_iter = om2.MItMeshVertex(mDagMesh)
    shortest_dic = {}
    while not vertex_iter.isDone():
        vrtxIndex = vertex_iter.index()
        point =  vertex_iter.position(om2.MSpace.kObject)
        connectedVertices = vertex_iter.getConnectedVertices()
        distances_dic = {vert : point.distanceTo(mFnMesh.getPoint(vert, om2.MSpace.kObject)) for vert in connectedVertices}
        shortestDistanceIndex = min(distances_dic.items(), key=lambda x: x[1])[0]
        shortest_dic[vrtxIndex] = shortestDistanceIndex
        vertex_iter.next()
    return shortest_dic

def matrixFromVertex(mesh, vtxIds, origin=om2.MPoint.kOrigin, space=om2.MSpace.kObject, dataInput=False):
        mSLmesh = om2.MGlobal.getSelectionListByName(mesh).getDependNode(0)
        dag = om2.MFnDagNode(mSLmesh).getPath()
        mFnMesh = om2.MFnMesh(dag)

        vertex_iter = om2.MItMeshVertex(dag)
        vertex_iter.setIndex(vtxIds)
        point =  vertex_iter.position(space)
        connectedVertices = vertex_iter.getConnectedVertices()

        connectedNormals = [mFnMesh.getVertexNormal(vert, True) for vert in connectedVertices]
        averageNormals = om2.MVector(map(lambda a : sum(a) / len(a), zip(*connectedNormals)))
        
        if not dataInput:
            distances_dic = {vert : point.distanceTo(mFnMesh.getPoint(vert, space)) for vert in connectedVertices}
            shortestDistanceIndex = min(distances_dic.items(), key=lambda x: x[1])[0]
            upVector = (point - mFnMesh.getPoint(shortestDistanceIndex, space)) * 0.5
        else:
            upVector = (point - mFnMesh.getPoint(dataInput[vtxIds], space)) * 0.5

        x = upVector
        z = averageNormals ^ x   # crossProduct
        y = z ^ averageNormals   # crossProduct

        return om2.MMatrix([
            x[0],                x[1],                x[2],                0.0,
            y[0],                y[1],                y[2],                0.0,
            z[0],                z[1],                z[2],                0.0,
            origin[0],           origin[1],           origin[2],           0.0,
            ])

def getAllVertexPositions(geometry, worldSpace=False):
    """
    Get All Vertex Position from a mesh
    """
    mSLmesh = om2.MGlobal.getSelectionListByName(geometry).getDependNode(0)
    dag = om2.MFnDagNode(mSLmesh).getPath()

    vert_positions = {}
    vertex_iter = om2.MItMeshVertex(dag)

    if worldSpace:
        space = om2.MSpace.kWorld
    else:
        space = om2.MSpace.kObject

    while not vertex_iter.isDone():
        point = vertex_iter.position(space)
        vrtxIndex = vertex_iter.index()
        vert_positions[vrtxIndex] = [point[0], point[1], point[2]]
        vertex_iter.next()
    return vert_positions

def setAllVertexPositions(geoObj, positions=[], worldSpace=False):
    """
    Set all vertex of a mesh from a list
    """
    mPoint = om2.MPointArray(positions)
    mSpace = None

    if worldSpace == True:
        mSpace = om2.MSpace.kWorld
    else:
        mSpace = om2.MSpace.kObject

    mSL = om2.MSelectionList()
    mSL.add(geoObj)

    mFnSet = om2.MFnMesh(mSL.getDagPath(0))
    mFnSet.setPoints(mPoint, mSpace)

def getAllMatrixDifference(targetMesh, neutralMesh, space=om2.MSpace.kObject):
    mSLmesh = om2.MGlobal.getSelectionListByName(targetMesh).getDependNode(0)
    dag = om2.MFnDagNode(mSLmesh).getPath()
    vertex_iter = om2.MItMeshVertex(dag)
    neutral_data = getSample(neutralMesh)

    difference_matrix = {}
    while not vertex_iter.isDone():
        vrtxIndex = vertex_iter.index()
        neutral = matrixFromVertex(neutralMesh, vrtxIndex)
        target = matrixFromVertex(targetMesh, vrtxIndex, dataInput=neutral_data)
        difference = neutral.inverse() * target
        difference_matrix[vrtxIndex] = difference
        vertex_iter.next()
    return difference_matrix


#======================================
# RUN CALCULATION
#======================================

neutral_positions = getAllVertexPositions(neutral, worldSpace=False)
shapeMesh_positions = getAllVertexPositions(shapeMesh,  worldSpace=False)
targetMesh_positions = getAllVertexPositions(targetMesh,  worldSpace=False)
difference_matrix = getAllMatrixDifference(targetMesh, neutral)

new_pos= []
for shape, neutral, target, difference in zip(shapeMesh_positions.values(), neutral_positions.values(), targetMesh_positions.values(), difference_matrix.values()):
    delta =  om2.MVector(shape) - om2.MVector(neutral)

    # final_position = om2.MVector(target) + (delta)
    final_position = om2.MVector(target) + (delta*difference)
    new_pos.append(final_position)

setAllVertexPositions(targetMesh, new_pos, worldSpace=False)


