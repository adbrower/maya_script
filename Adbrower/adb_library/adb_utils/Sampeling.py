import pymel.core as pm
import maya.cmds as mc
from maya.api import OpenMaya as om2
from scipy.spatial import cKDTree
from adb_library.adb_utils.Utils_matrix import matrixFromVertex



def getMaxCountFromRadius(sourcesPoints, radius=1, maximumCount=5):
    """
    Args:
        sourcesPoints (Mpoints): All the Points from a Mesh
        radius (nonnegative Float) : Return only neighbors within this distance. 
        maximumCount (Int): The list of k-th nearest neighbors to return. Defaults to 5.
    Returns:
        (numpy.ndarray): The list of the closest vtx
    """

    tree = cKDTree(sourcePoints)
    distance, indexes = tree.query(sourcePoints, distance_upper_bound=radius, k=maximumCount)
    return indexes


#======================================
# RUN CALCULATION
#======================================

mSLmeshDag = om2.MFnDagNode(om2.MGlobal.getSelectionListByName('pSphere1').getDependNode(0)).getPath()
mFnMesh = om2.MFnMesh(mSLmeshDag)
sourcePoints = mFnMesh.getPoints()
closestPointVtxId = getMaxCountFromRadius(sourcePoints, radius=1, maximumCount=10)

