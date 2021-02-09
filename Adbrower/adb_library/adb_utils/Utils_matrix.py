import pymel.core as pm
import maya.cmds as mc
from maya.api import OpenMaya as om2
import maya.OpenMayaAnim as oma
import pymel.core.datatypes as dt



def getRotationDegreeFromMatrix(Matrix):
    """ 
    Get rotation values in degree from Matrix

    Args:
        Matrix (om2.MMatrix, list or tuple): If a list or Tuple, must be len of 16

    Returns:
        Tuple: A tuple of XYZ rotation in degrees

    Ex:
        locOriginMatrix = om2.MMatrix(mc.xform('Locator1', q=1, m=1, ws=1))
        getRotationDegreeFromMatrix(locOriginMatrix)
    """
    if isinstance(Matrix, om2.MMatrix):
        Matrix = Matrix

    elif isinstance(Matrix, list):
        if len(Matrix) == 16:
            Matrix = om2.MMatrix(Matrix)

    elif isinstance(Matrix, tuple):
        print 'c'
        if len(Matrix) == 16:
            Matrix = om2.MMatrix(Matrix)
    else:
        pm.warning('argument type is not compatible, must be a MMatrix or a list')

    matrixTransforms = om2.MTransformationMatrix(Matrix)
    rot =  matrixTransforms.rotation()

    rotationX = om2.MAngle(rot.x).asDegrees()
    rotationY = om2.MAngle(rot.y).asDegrees()
    rotationZ = om2.MAngle(rot.z).asDegrees()

    return rotationX, rotationY, rotationZ


def matrixFromVertex(mesh, vtxIds, origin=om2.MPoint.kOrigin, space=om2.MSpace.kObject, dataInput=False, formating=False):
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
        upVector = point - mFnMesh.getPoint(shortestDistanceIndex, space)
    else:
        upVector = (point - mFnMesh.getPoint(dataInput[vtxIds], space)) * 0.5

    x = upVector
    z = averageNormals ^ x   # crossProduct
    y = z ^ averageNormals   # crossProduct

    if formating:
        print om2.MMatrix([
        float('{: .4f}'.format(x[0])),        float('{:.4f}'.format(x[1])),        float('{:.4f}'.format(x[2])),                0.0,
        float('{: .4f}'.format(y[0])),        float('{:.4f}'.format(y[1])),        float('{:.4f}'.format(y[2])),                0.0,
        float('{: .4f}'.format(z[0])),        float('{:.4f}'.format(z[1])),        float('{:.4f}'.format(z[2])),                0.0,
        float('{: .4f}'.format(origin[0])),   float('{:.4f}'.format(origin[1])),   float('{:.4f}'.format(origin[2])),           0.0,
        ])

    return om2.MMatrix([
        x[0],                x[1],                x[2],                0.0,
        y[0],                y[1],                y[2],                0.0,
        z[0],                z[1],                z[2],                0.0,
        origin[0],           origin[1],           origin[2],           0.0,
        ])


