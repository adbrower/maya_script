# =====================================================================
# Author : Audrey Deschamps-Brower
#  audreydb23@gmail.com
# =====================================================================

import sys
import time

import maya.OpenMaya as om
from maya.api import OpenMaya as om2
import maya.OpenMayaMPx as OpenMayaMPx

import pymel.core as pm
import maya.cmds as mc
import maya.mel

from adb_library.adb_utils.Functions__topology import getSymmetry, getSelectionPairs, getMDagPath, getMObject

# ==========================
#  GENERAL DEFORMER

def getWeights():
    pass


def setWeights():
    pass 


def mirrorWeightsMap(center_edge, deformer ='', toSide='RIGHT'):
    """
    Mirror Normal Deformer weight map

    example:
        mirrorWeightsMap('pSphere1.e[614]', deformer='adbResetDeltaDeformer1', toSide='LEFT')
    """   
    geometry, edge_index = center_edge.split('.')
    clusterDnode = om2.MFnDependencyNode(getMObject(deformer))
    weightsPlug  = clusterDnode.findPlug('weightList', True)
    numVerts = om2.MItMeshVertex(getMDagPath(geometry)).count()

    currentWeights = {}
    weightPlugs = {}
    for i in xrange(weightsPlug.numElements()):
        weightlistIdxPlug = weightsPlug.elementByPhysicalIndex(i)

        for j in xrange(weightlistIdxPlug.numChildren()):
            weights = weightlistIdxPlug.child(j)

        for index in xrange(numVerts):
            weightVtxPlug = weights.elementByLogicalIndex(index)
            weightPlugs[index] = weightVtxPlug
            weightVtxValue = weightVtxPlug.asFloat()
            currentWeights[index] = weightVtxValue

    edge_index = int(edge_index.split('e[')[1].split(']')[0])
    if edge_index > (mc.polyEvaluate(geometry, e=True) - 1):
        raise RuntimeError("Edge '{}' is not valid.".format(center_edge))

    lf_verts, cn_verts, rt_verts = getSymmetry(str(center_edge))

    mirror_pairs, cn_verts = getSelectionPairs(geometry, lf_verts, toSide,
                                               lf_verts, cn_verts, rt_verts)

    for pair in mirror_pairs:
        plug = weightPlugs[pair[0]]
        plug.setFloat(currentWeights[pair[1]])

    for pair in cn_verts:
        plug = weightPlugs[pair[0]]
        plug.setFloat(currentWeights[pair[1]])



# ==========================
# BLENDSHAPES

def getBaseWeights(mesh, deformer):
    deformer_node = deformer
    map = 'baseWeights'
    targetWeight = {}

    MeshDag = getMDagPath(str(mesh))
    numVerts = om2.MItMeshVertex(MeshDag).count()
    vert_iter = om2.MItMeshVertex(MeshDag)

    while not vert_iter.isDone():
        vrtxIndex = vert_iter.index()
        sl1 = om2.MSelectionList()
        sl1.add("{}.inputTarget[0].{}".format(deformer_node, map))
        basePlug = sl1.getPlug(0)

        w = basePlug.elementByLogicalIndex(vrtxIndex)
        weight = w.asFloat()

        targetWeight[vrtxIndex] = weight
        vert_iter.next()

    return targetWeight


def setBaseWeights():
    pass


def mirrorBaseWeightMap(center_edge, deformer ='', toSide='RIGHT'):
    """Mirror BaseWeight Map

    example:
        mirrorBaseWeightMap(center_edge='head_geo.e[4993]', deformer='head_geo_BLS')

    Arguments:
        center_edge {String} -- Edge from with we separate Left from Right
        mirror_src {String} -- LEFT or RIGHT
    """
    mesh, edge_index = center_edge.split('.')
    deformer_node = deformer
    map = 'baseWeights'

    targetWeight = {}

    MeshDag = getMDagPath(str(mesh))
    numVerts = om2.MItMeshVertex(MeshDag).count()
    vert_iter = om2.MItMeshVertex(MeshDag)

    while not vert_iter.isDone():
        vrtxIndex = vert_iter.index()
        sl1 = om2.MSelectionList()
        sl1.add("{}.inputTarget[0].{}".format(deformer_node, map))
        basePlug = sl1.getPlug(0)

        w = basePlug.elementByLogicalIndex(vrtxIndex)
        weight = w.asFloat()

        targetWeight[vrtxIndex] = weight
        vert_iter.next()

    geometry, edge_index = center_edge.split('.')
    edge_index = int(edge_index.split('e[')[1].split(']')[0])
    if edge_index > (mc.polyEvaluate(geometry, e=True) - 1):
        raise RuntimeError("Edge '{}' is not valid.".format(center_edge))

    lf_verts, cn_verts, rt_verts = getSymmetry(str(center_edge))

    mirror_pairs, cn_verts = getSelectionPairs(geometry, lf_verts, toSide,
                                        lf_verts, cn_verts, rt_verts)

    for pair in mirror_pairs:
        sl2 = om2.MSelectionList()
        sl2.add("{}.inputTarget[0].{}".format(deformer_node, map))
        basePlug = sl2.getPlug(0)
        basePlug.elementByLogicalIndex(pair[0]).setFloat(targetWeight[pair[1]])

    for pair in cn_verts:
        sl3 = om2.MSelectionList()
        sl3.add("{}.inputTarget[0].{}".format(deformer_node, map))
        basePlug = sl3.getPlug(0)
        basePlug.elementByLogicalIndex(pair[0]).setFloat(targetWeight[pair[1]])


def getTargetWeights():
    pass


def setTargetWeights():
    pass


def mirrorTargetMap(center_edge, deformer ='', toSide='RIGHT'):
    """
    Mirror Target Map
    NOTES : You need to select the target you want to mirror

    example:
        mirrorTargetMap(center_edge='pPlane1.e[74]', deformer ='pPlane1_BLS', toSide='RIGHT')

    Arguments:
        center_edge {String} -- Edge from with we separate Left from Right
        mirror_src {String} -- LEFT or RIGHT

    """
    mesh, edge_index = center_edge.split('.')
    bs_node = deformer

    MeshDag = getMDagPath(str(mesh))
    numVerts = om2.MItMeshVertex(MeshDag).count()
    vert_iter = om2.MItMeshVertex(MeshDag)

    targetWeight = {}

    while not vert_iter.isDone():
        vrtxIndex = vert_iter.index()
        sl1 = om2.MSelectionList()
        sl1.add("{}.inputTarget[0].paintTargetWeights[{}]".format(bs_node,  vrtxIndex))
        paintTargetWeightsPlug = sl1.getPlug(0)

        targetWeightsValue =  paintTargetWeightsPlug.asFloat()
        targetWeight[vrtxIndex] = targetWeightsValue
        vert_iter.next()

    geometry, edge_index = center_edge.split('.')
    edge_index = int(edge_index.split('e[')[1].split(']')[0])
    if edge_index > (mc.polyEvaluate(geometry, e=True) - 1):
        raise RuntimeError("Edge '{}' is not valid.".format(center_edge))

    lf_verts, cn_verts, rt_verts = getSymmetry(str(center_edge))

    mirror_pairs, cn_verts = getSelectionPairs(geometry, lf_verts, toSide,
                                        lf_verts, cn_verts, rt_verts)

    for pair in mirror_pairs:
        sl2 = om2.MSelectionList()
        sl2.add("{}.inputTarget[0].paintTargetWeights[{}]".format(bs_node,  pair[0]))
        plug = sl2.getPlug(0)
        plug.setFloat(targetWeight[pair[1]])


    for pair in cn_verts:
        sl3 = om2.MSelectionList()
        sl3.add("{}.inputTarget[0].paintTargetWeights[{}]".format(bs_node, pair[0]))
        plug = sl3.getPlug(0)
        plug.setFloat(targetWeight[pair[1]])


