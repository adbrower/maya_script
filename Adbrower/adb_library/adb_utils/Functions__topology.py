import time
import maya.cmds as mc
import pymel.core as pm
import maya.mel as mel

import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
from maya.api import OpenMaya as om2
from pymel.core.datatypes import Vector

from adbrower import undo, timeit

def loadPlugin(plugin):
    if not mc.pluginInfo(plugin, query=True, loaded=True):
        try:
            mc.loadPlugin(plugin)
        except RuntimeError:
            pm.warning('could not load plugin {}'.format(plugin))

loadPlugin('adbResetDelta__Command')
loadPlugin('adbTopology__Command')
# --------------------------------------------------------------------------------------------------------------
#                                                       GET DATA
# --------------------------------------------------------------------------------------------------------------
def getMDagPath(node):
    """
    Returns MDagPath of given nodepour invert les value
    """
    selList = om2.MSelectionList()
    selList.add(node)
    return selList.getDagPath(0)


def getMObject(node):
    """
    Returns MObject of given node
    """
    selList = om2.MSelectionList()
    selList.add(node)
    return selList.getDependNode(0)


class gShowProgress(object):
    """
    Based on: http://josbalcaen.com/maya-python-progress-decorator

    Function decorator to show the user (progress) feedback.
    @usage

    import time
    @gShowProgress(end=10)
    def createCubes():
        for i in range(10):
            time.sleep(1)
            if createCubes.isInterrupted(): break
            iCube = mc.polyCube(w=1,h=1,d=1)
            mc.move(i,i*.2,0,iCube)
            createCubes.step()
    """
    def __init__(self, status='Busy...', start=0, end=100, interruptable=True):
        import maya.cmds as cmds
        import maya.mel

        self.mStartValue = start
        self.mEndValue = end
        self.mStatus = status
        self.mInterruptable = interruptable
        self.mMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar')

    def step(self, inValue=1):
        """Increase step
        @param inValue (int) Step value"""
        mc.progressBar(self.mMainProgressBar, edit=True, step=inValue)

    def isInterrupted(self):
        """Check if the user has interrupted the progress
        @return (boolean)"""
        return mc.progressBar(self.mMainProgressBar, query=True, isCancelled=True)

    def start(self):
        """Start progress"""
        mc.waitCursor(state=True)
        mc.progressBar( self.mMainProgressBar,
                edit=True,
                beginProgress=True,
                isInterruptable=self.mInterruptable,
                status=self.mStatus,
                minValue=self.mStartValue,
                maxValue=self.mEndValue
            )
        mc.refresh()

    def end(self):
        """Mark the progress as ended"""
        mc.progressBar(self.mMainProgressBar, edit=True, endProgress=True)
        mc.waitCursor(state=False)

    def __call__(self, inFunction):
        """
        Override call method
        @param inFunction (function) Original function
        @return (function) Wrapped function
        @description
            If there are decorator arguments, __call__() is only called once,
            as part of the decoration process! You can only give it a single argument,
            which is the function object.
        """
        def wrapped_f(*args, **kwargs):
            # Start progress
            self.start()
            # Call original function
            inFunction(*args,**kwargs)
            # End progress
            self.end()

        # Add special methods to the wrapped function
        wrapped_f.step = self.step
        wrapped_f.isInterrupted = self.isInterrupted

        # Copy over attributes
        wrapped_f.__doc__ = inFunction.__doc__
        wrapped_f.__name__ = inFunction.__name__
        wrapped_f.__module__ = inFunction.__module__

        # Return wrapped function
        return wrapped_f


class SymmetryError(Exception):
    pass


def getSymmetry(center_edge):
    sel_list =  om2.MSelectionList()
    sel_list.add(center_edge)
    sel_shape_DAG = sel_list.getDagPath(0)

    sel_edges = om2.MItMeshEdge(sel_shape_DAG)
    first_edge = int(center_edge.split('e[')[1].split(']')[0])
    fn_mesh = om2.MFnMesh(sel_shape_DAG)

    vert_count       = om2.MItMeshVertex(sel_shape_DAG).count()
    side_verts       = [-1] * vert_count
    checked_verts    = [-1] * vert_count
    checked_polygons = [-1] * om2.MItMeshPolygon(sel_shape_DAG).count()
    checked_edges    = [-1] * om2.MItMeshEdge(sel_shape_DAG).count()

    vertex_iter = om2.MItMeshVertex(sel_shape_DAG)
    poly_iter   = om2.MItMeshPolygon(sel_shape_DAG)
    edge_iter   = om2.MItMeshEdge(sel_shape_DAG)

    lf_edge_queue = om2.MIntArray()
    rt_edge_queue = om2.MIntArray()

    lf_edge_queue.append(first_edge)
    rt_edge_queue.append(first_edge)

    lf_current_edge = lf_current_poly = rt_current_edge = rt_current_poly = 0

    while len(lf_edge_queue) > 0:
        lf_current_edge = lf_edge_queue[0]
        rt_current_edge = rt_edge_queue[0]

        lf_edge_queue.remove(0)
        rt_edge_queue.remove(0)

        if lf_current_edge == rt_current_edge and lf_current_edge != first_edge:
            continue

        checked_edges[lf_current_edge] = rt_current_edge
        checked_edges[rt_current_edge] = lf_current_edge

        lf_face_list = om2.MIntArray()
        rt_face_list = om2.MIntArray()

        edge_iter.setIndex(lf_current_edge)
        lf_face_list = edge_iter.getConnectedFaces()

        if len(lf_face_list) != 2:
            continue
        f1, f2 = lf_face_list

        if checked_polygons[f1] == -1 and checked_polygons[f2] != -1:
            lf_current_poly = f1
        elif checked_polygons[f1] != -1 and checked_polygons[f2] == -1:
            lf_current_poly = f2
        elif checked_polygons[f1] == -1 and checked_polygons[f2] == -1:
            lf_current_poly = f1
            checked_polygons[f1] = -2

        edge_iter.setIndex(rt_current_edge)
        rt_face_list = edge_iter.getConnectedFaces()
        f1, f2 = rt_face_list

        if checked_polygons[f1] == -1 and checked_polygons[f2] != -1:
            rt_current_poly = f1
        elif checked_polygons[f1] != -1 and checked_polygons[f2] == -1:
            rt_current_poly = f2
        elif checked_polygons[f2] == -1 and checked_polygons[f1] == -1:
            raise SymmetryError('Topology is invalid.')
        else:
            continue

        ## Replace original value by new corresponding pairs
        checked_polygons[rt_current_poly] = lf_current_poly
        checked_polygons[lf_current_poly] = rt_current_poly

        lf_edge_vert_1, lf_edge_vert_2 = fn_mesh.getEdgeVertices(lf_current_edge)
        rt_edge_vert_1, rt_edge_vert_2 = fn_mesh.getEdgeVertices(rt_current_edge)

        if lf_current_edge == first_edge:
            checked_verts[lf_edge_vert_1] = rt_edge_vert_1
            checked_verts[lf_edge_vert_2] = rt_edge_vert_2
            checked_verts[rt_edge_vert_1] = lf_edge_vert_1
            checked_verts[rt_edge_vert_2] = lf_edge_vert_2

        lf_face_edges = om2.MIntArray()
        rt_face_edges = om2.MIntArray()

        poly_iter.setIndex(lf_current_poly)
        lf_face_edges = poly_iter.getEdges()
        poly_iter.setIndex(rt_current_poly)
        rt_face_edges = poly_iter.getEdges()

        if len(lf_face_edges) != len(rt_face_edges):
            raise SymmetryError('Geometry is not symmetrical!')

        lf_checked_vert = lf_non_checked_vert = 0

        for lf_face_edge_index in lf_face_edges:
            if checked_edges[lf_face_edge_index] != -1:
                continue

            edge_iter.setIndex(lf_current_edge)
            connected = edge_iter.connectedToEdge(lf_face_edge_index)
            if not connected or lf_current_edge == lf_face_edge_index:
                continue

            lf_vert_1, lf_vert_2 = fn_mesh.getEdgeVertices(lf_face_edge_index)

            if lf_vert_1 in (lf_edge_vert_1, lf_edge_vert_2):
                lf_checked_vert     = lf_vert_1
                lf_non_checked_vert = lf_vert_2

            elif lf_vert_2 in (lf_edge_vert_1, lf_edge_vert_2):
                lf_checked_vert     = lf_vert_2
                lf_non_checked_vert = lf_vert_1
            else:
                continue

            lf_checked_state = 0
            if checked_verts[lf_vert_1] != -1:
                lf_checked_state += 1
            if checked_verts[lf_vert_2] != -1:
                lf_checked_state += 1

            for rt_face_edge_index in rt_face_edges:
                edge_iter.setIndex(rt_current_edge)

                connected = edge_iter.connectedToEdge(rt_face_edge_index)
                if not connected or rt_current_edge == rt_face_edge_index:
                    continue

                rt_vert_1, rt_vert_2 = fn_mesh.getEdgeVertices(rt_face_edge_index)
                lf_checked_mirror = checked_verts[lf_checked_vert]

                if rt_vert_1 == lf_checked_mirror or rt_vert_2 == lf_checked_mirror:
                    rt_checked_state = 0
                    if checked_verts[rt_vert_1] != -1: 
                        rt_checked_state += 1
                    if checked_verts[rt_vert_2] != -1: 
                        rt_checked_state += 1
                    if lf_checked_state != rt_checked_state:
                        raise SymmetryError('Geometry is not symmetrical!')

                    lf_edge_queue.append(lf_face_edge_index)
                    rt_edge_queue.append(rt_face_edge_index)

                if rt_vert_1 == lf_checked_mirror:
                    checked_verts[lf_non_checked_vert] = rt_vert_2
                    checked_verts[rt_vert_2] = lf_non_checked_vert
                    side_verts[lf_non_checked_vert] = "Right"
                    side_verts[rt_vert_2] = "Left"
                    break

                elif rt_vert_2 == lf_checked_mirror:
                    checked_verts[lf_non_checked_vert] = rt_vert_1
                    checked_verts[rt_vert_1] = lf_non_checked_vert
                    side_verts[lf_non_checked_vert] = "Right"
                    side_verts[rt_vert_1] = "Left"
                    break

    average_a = average_b = 0
    for index in range(vert_count):
        mirror_vert = checked_verts[index]
        if mirror_vert != index and mirror_vert != -1:
            point_pos = fn_mesh.getPoint(mirror_vert, om2.MSpace.kObject)
            if side_verts[index] == "Right":
                average_b += point_pos.x
            elif side_verts[index] == "Left":
                average_a += point_pos.x

    if average_a < average_b:
        switch_side = True
    else:
        switch_side = False

    side_map = []
    mirror_map = []

    for index in range(vert_count):
        mirror_map.append(checked_verts[index])
        if checked_verts[index] != index:
            if not switch_side:
                side_map.append(side_verts[index])
            else:
                if side_verts[index] == 'Left':
                    side_map.append('Right')
                else:
                    side_map.append('Left')
        else:
            side_map.append('Center')

    lf_verts = []
    cn_verts = []
    rt_verts = []

    mirror_dict = {}
    for index, (side, mirror) in enumerate(zip(side_map, mirror_map)):
        if side == 'Center':
            cn_verts.append(index)
            continue
        if side == 'Right':
            continue
        mirror_dict[index] = mirror

    for rt_vert, lf_vert in mirror_dict.items():
        lf_verts.append(lf_vert)
        rt_verts.append(rt_vert)

    return lf_verts, cn_verts, rt_verts


def getSoftSelection():
    softSelectDict = {}

    softSelection = om2.MGlobal.getRichSelection()
    richSelection = om2.MRichSelection(softSelection)
    richeSelectionList = richSelection.getSelection()
    component =  richeSelectionList.getComponent(0)

    componentIndex = om2.MFnSingleIndexedComponent(component[1])
    vertexList =  componentIndex.getElements()

    for loop in range(len(vertexList)):
        weight = componentIndex.weight(loop)
        softSelectDict[vertexList[loop]] = float(format(weight.influence, '.5f'))

    return softSelectDict


def getAllVertexPositions(geometry, worldSpace=True):
    """
    Get All Vertex Position from a mesh

    Arguments:
        geometry {str} -- Mesh

    Keyword Arguments:
        worldSpace {bool} -- (default: {True})

    Returns:
        Dict -- All vertex positions. keys: index, Values: vrtx positions
    """
    mSLmesh = om2.MGlobal.getSelectionListByName(geometry).getDependNode(0)
    dag = om2.MFnDagNode(mSLmesh).getPath()

    vert_positions = {}
    vert_iter = om2.MItMeshVertex(dag)

    space = om2.MSpace.kObject
    if worldSpace:
        space = om2.MSpace.kWorld

    while not vert_iter.isDone():
        point = vert_iter.position(space)
        vrtxIndex = vert_iter.index()
        vert_positions[vrtxIndex] = [point[0], point[1], point[2]]
        vert_iter.next()

    return vert_positions


def setAllVertexPositions(geoObj, positions=[], worldSpace=True):
    """
    Set all vertex of a mesh from a list
    """
    mPoint = om2.MPointArray(positions)
    mSpace = None

    if worldSpace == True:
        mSpace = om.MSpace.kWorld
    else:
        mSpace = om.MSpace.kObject

    # Attach a MFnMesh functionSet and set the positions
    mSL = om2.MSelectionList()
    mSL.add(geoObj)

    mFnSet = om2.MFnMesh(mSL.getDagPath(0))
    mFnSet.setPoints(mPoint, mSpace)


def getCurrentGeometry():
    """
    Get Geometry from selected Edge
    """
    selection = mc.ls(sl=True, fl=True)
    if not len(selection):
        raise RuntimeError("Nothing Selected.")

    # get selected verts and geometry
    vert_indices = []; geometry = None
    for item in selection:
        if '.vtx[' in item:
            vert_geometry, vert_index = item.split('.vtx[')
            if geometry is not None and vert_geometry != geometry:
                raise RuntimeError("More than one piece of geometry selected.")
            geometry = vert_geometry
            vert_indices.append(int(vert_index.split(']')[0]))

    # if no verts are selected assume geometry
    if len(vert_indices) == 0:
        if mc.objectType(selection[0]) != "transform":
            raise RuntimeError("Requires Mesh Selection.")
        return selection[0], None

    return geometry, vert_indices


def getSelectionPairs(geometry, vert_indices, mirror_src, lf_verts, cn_verts, rt_verts):
    """
    Find the opposite vertex
        return List of pair of vertex and list of center vertex

    @param geometry: String
    @param vert_indices: List of all the vertex index
    @param mirror_src : String 'LEFT' or 'RIGTH
    @param lf_verts: List of all the vtx on the left side
    @param cn_verts: List of all the vtx on the center
    @param rt_verts: List of all the vtx on the right side
    """
    if mirror_src.upper() == 'LEFT':
        src_verts = lf_verts; dst_verts = rt_verts
    else:
        src_verts = rt_verts; dst_verts = lf_verts

    src_verts_set = set(src_verts)
    cn_verts_set  = set(cn_verts)
    dst_verts_set = set(dst_verts)

    selected_pairs = []; selected_cn_verts = []
    for vert_index in vert_indices:
        if vert_index in src_verts_set:
            selected_pairs.append((vert_index, dst_verts[src_verts.index(vert_index)]))
        elif vert_index in dst_verts_set:
            selected_pairs.append((src_verts[dst_verts.index(vert_index)], vert_index))
        else:
            selected_cn_verts.append(vert_index)

    return selected_pairs, selected_cn_verts

# --------------------------------------------------------------------------------------------------------------
#                                        EXECUTE FUNCTIONS
# --------------------------------------------------------------------------------------------------------------

@gShowProgress('Mirroring Selection. . .')
@undo
def _selectMirrorVtx(geometry, vert_indices, mirror_src, lf_verts, cn_verts, rt_verts):
    vert_positions = getAllVertexPositions(geometry, worldSpace=False)

    mirror_pairs, cn_verts = getSelectionPairs(geometry, vert_indices, mirror_src,
                                                lf_verts, cn_verts, rt_verts)

    for pair_vert, original_vert in list(mirror_pairs):
        pair_pos = vert_positions.values()[pair_vert]
        original_pos = vert_positions.values()[original_vert]

        mc.select('{}.vtx[{}]'.format(geometry, pair_vert), add=1)


#=======================================
# LOOP FUNCTIONS
#=======================================

@timeit
@undo
def selectMirrorVtx(vert_selection, center_edge, mirror_src):
    geometry, edge_index = center_edge.split('.')
    edge_index = int(edge_index.split('e[')[1].split(']')[0])
    if edge_index > (mc.polyEvaluate(geometry, e=True) - 1):
        raise RuntimeError("Edge '{}' is not valid.".format(center_edge))

    vert_indices = [int(vert.split('.vtx[')[1].split(']')[0]) for vert in vert_selection]
    lf_verts, cn_verts, rt_verts = getSymmetry(center_edge)
    _selectMirrorVtx(geometry, vert_indices, mirror_src, lf_verts, cn_verts, rt_verts)
