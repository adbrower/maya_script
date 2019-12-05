import pymel.core as pm
from pymel.core.datatypes import Vector
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.cmds as mc
from pymel.core.datatypes import Vector
from functools import wraps

# --------------------------------------------------------------------------------------------------------------
#                                                       GET DATA
# --------------------------------------------------------------------------------------------------------------

class SymmetryError(Exception):
    pass

def getSymmetry(center_edge, sets=True, sides=False, mirrors=False):
    sel_list = om.MSelectionList()
    sel_list.add(center_edge)
    sel_shape = om.MDagPath()
    iter      = om.MItSelectionList(sel_list)
    component = om.MObject()
    iter.getDagPath(sel_shape, component)

    sel_edges  = om.MItMeshEdge(sel_shape, component)
    first_edge = sel_edges.index()
    fn_mesh    = om.MFnMesh(sel_shape)

    vert_count       = fn_mesh.numVertices()
    side_verts       = [-1] * vert_count
    checked_verts    = [-1] * vert_count
    checked_polygons = [-1] * fn_mesh.numPolygons()
    checked_edges    = [-1] * fn_mesh.numEdges()

    vertex_iter = om.MItMeshVertex(sel_shape)
    poly_iter   = om.MItMeshPolygon(sel_shape)
    edge_iter   = om.MItMeshEdge(sel_shape)

    lf_edge_queue = om.MIntArray()
    rt_edge_queue = om.MIntArray()

    lf_edge_queue.append(first_edge)
    rt_edge_queue.append(first_edge)

    lf_face_list = om.MIntArray()
    rt_face_list = om.MIntArray()

    lf_curr_edge = lf_curr_poly = rt_curr_edge = rt_curr_poly = 0

    util = om.MScriptUtil()
    util.createFromInt(0)
    prev_index = util.asIntPtr()

    lf_edge_verts_util = om.MScriptUtil()
    rt_edge_verts_util = om.MScriptUtil()
    rt_face_edge_verts_util  = om.MScriptUtil()
    lf_if_checked_verts_util = om.MScriptUtil()

    while len(lf_edge_queue) > 0:
        lf_curr_edge = lf_edge_queue[0]
        rt_curr_edge = rt_edge_queue[0]

        lf_edge_queue.remove(0)
        rt_edge_queue.remove(0)

        if lf_curr_edge == rt_curr_edge and lf_curr_edge != first_edge:
            continue

        checked_edges[lf_curr_edge] = rt_curr_edge
        checked_edges[rt_curr_edge] = lf_curr_edge

        edge_iter.setIndex(lf_curr_edge, prev_index)
        edge_iter.getConnectedFaces(lf_face_list)
        if lf_face_list.length() != 2:
            continue
        f1, f2 = lf_face_list

        if checked_polygons[f1] == -1 and checked_polygons[f2] != -1:
            lf_curr_poly = f1
        elif checked_polygons[f1] != -1 and checked_polygons[f2] == -1:
            lf_curr_poly = f2
        elif checked_polygons[f1] == -1 and checked_polygons[f2] == -1:
            lf_curr_poly = f1
            checked_polygons[f1] = -2

        edge_iter.setIndex(rt_curr_edge, prev_index)
        edge_iter.getConnectedFaces(rt_face_list)
        f1, f2 = rt_face_list

        if checked_polygons[f1] == -1 and checked_polygons[f2] != -1:
            rt_curr_poly = f1
        elif checked_polygons[f1] != -1 and checked_polygons[f2] == -1:
            rt_curr_poly = f2
        elif checked_polygons[f2] == -1 and checked_polygons[f1] == -1:
            raise SymmetryError('Topology is invalid.')
        else:
            continue

        checked_polygons[rt_curr_poly] = lf_curr_poly
        checked_polygons[lf_curr_poly] = rt_curr_poly


        lf_edge_verts_util.createFromInt(0, 0)
        lf_edge_verts = lf_edge_verts_util.asInt2Ptr()
        rt_edge_verts_util.createFromInt(0, 0)
        rt_edge_verts = rt_edge_verts_util.asInt2Ptr()

        fn_mesh.getEdgeVertices(lf_curr_edge, lf_edge_verts)
        lf_edge_vert_1 = om.MScriptUtil.getInt2ArrayItem(lf_edge_verts, 0, 0)
        lf_edge_vert_2 = om.MScriptUtil.getInt2ArrayItem(lf_edge_verts, 0, 1)

        fn_mesh.getEdgeVertices(rt_curr_edge, rt_edge_verts)
        rt_edge_vert_1 = om.MScriptUtil.getInt2ArrayItem(rt_edge_verts, 0, 0)
        rt_edge_vert_2 = om.MScriptUtil.getInt2ArrayItem(rt_edge_verts, 0, 1)

        if lf_curr_edge == first_edge:
            checked_verts[lf_edge_vert_1] = rt_edge_vert_1
            checked_verts[lf_edge_vert_2] = rt_edge_vert_2
            checked_verts[rt_edge_vert_1] = lf_edge_vert_1
            checked_verts[rt_edge_vert_2] = lf_edge_vert_2

        lf_face_edges = om.MIntArray()
        rt_face_edges = om.MIntArray()

        poly_iter.setIndex(lf_curr_poly, prev_index)
        poly_iter.getEdges(lf_face_edges)
        poly_iter.setIndex(rt_curr_poly, prev_index)
        poly_iter.getEdges(rt_face_edges)

        if lf_face_edges.length() != rt_face_edges.length():
            raise SymmetryError('Geometry is not symmetrical.')

        rt_face_edge_verts_util.createFromInt(0, 0)
        rt_face_edge_verts = rt_face_edge_verts_util.asInt2Ptr()
        lf_if_checked_verts_util.createFromInt(0, 0)
        lf_if_checked_verts = lf_if_checked_verts_util.asInt2Ptr()

        lf_checked_vert = lf_non_checked_vert = 0

        for lf_face_edge_index in lf_face_edges:
            if checked_edges[lf_face_edge_index] != -1:
                continue

            edge_iter.setIndex(lf_curr_edge, prev_index)

            connected = edge_iter.connectedToEdge(lf_face_edge_index)
            if not connected or lf_curr_edge == lf_face_edge_index:
                continue

            fn_mesh.getEdgeVertices(lf_face_edge_index, lf_if_checked_verts)
            lf_vert_1 = om.MScriptUtil.getInt2ArrayItem(lf_if_checked_verts, 0, 0)
            lf_vert_2 = om.MScriptUtil.getInt2ArrayItem(lf_if_checked_verts, 0, 1)

            if lf_vert_1 in (lf_edge_vert_1, lf_edge_vert_2):
                lf_checked_vert     = lf_vert_1
                lf_non_checked_vert = lf_vert_2
            elif lf_vert_2 in (lf_edge_vert_1, lf_edge_vert_2):
                lf_checked_vert     = lf_vert_2
                lf_non_checked_vert = lf_vert_1
            else:
                continue

            lf_checked_state = 0
            if checked_verts[lf_vert_1] != -1: lf_checked_state += 1
            if checked_verts[lf_vert_2] != -1: lf_checked_state += 1

            for rt_face_edge_index in rt_face_edges:
                edge_iter.setIndex(rt_curr_edge, prev_index)

                connected = edge_iter.connectedToEdge(rt_face_edge_index)
                if not connected or rt_curr_edge == rt_face_edge_index:
                    continue

                fn_mesh.getEdgeVertices(rt_face_edge_index, rt_face_edge_verts)
                rt_vert_1 = om.MScriptUtil.getInt2ArrayItem(rt_face_edge_verts, 0, 0)
                rt_vert_2 = om.MScriptUtil.getInt2ArrayItem(rt_face_edge_verts, 0, 1)

                lf_checked_mirror = checked_verts[lf_checked_vert]
                if rt_vert_1 == lf_checked_mirror or rt_vert_2 == lf_checked_mirror:
                    rt_checked_state = 0
                    if checked_verts[rt_vert_1] != -1: rt_checked_state += 1
                    if checked_verts[rt_vert_2] != -1: rt_checked_state += 1
                    if lf_checked_state != rt_checked_state:
                        raise SymmetryError('Geometry is not symmetrical.')

                    lf_edge_queue.append(lf_face_edge_index)
                    rt_edge_queue.append(rt_face_edge_index)

                if rt_vert_1 == lf_checked_mirror:
                    checked_verts[lf_non_checked_vert] = rt_vert_2
                    checked_verts[rt_vert_2] = lf_non_checked_vert
                    side_verts[lf_non_checked_vert] = 2
                    side_verts[rt_vert_2] = 1
                    break

                elif rt_vert_2 == lf_checked_mirror:
                    checked_verts[lf_non_checked_vert] = rt_vert_1
                    checked_verts[rt_vert_1] = lf_non_checked_vert
                    side_verts[lf_non_checked_vert] = 2
                    side_verts[rt_vert_1] = 1
                    break

    average_a = average_b = 0
    point_pos = om.MPoint()

    total_len_x = 0
    for index in range(vert_count):
        mirror_vert = checked_verts[index]
        if mirror_vert != index and mirror_vert != -1:
            fn_mesh.getPoint(mirror_vert, point_pos)
            if side_verts[index] == 2:
                total_len_x += 1
                average_b += point_pos.x
            elif side_verts[index] == 1:
                average_a += point_pos.x

    if average_a < average_b:
        switch_side = True
    else:
        switch_side = False

    side_map = []; mirror_map = []
    for index in range(vert_count):
        mirror_map.append(checked_verts[index])
        if checked_verts[index] != index:
            if not switch_side:
                side_map.append(side_verts[index])
            else:
                if side_verts[index] == 1:
                    side_map.append(2)
                else:
                    side_map.append(1)
        else:
            side_map.append(0)

    if sides is True:
        return side_map

    if mirrors is True:
        return mirror_map

    lf_verts = []
    cn_verts = []
    rt_verts = []

    mirror_dict = {}
    for index, (side, mirror) in enumerate(zip(side_map, mirror_map)):
        if side == 0:
            cn_verts.append(index);
            continue
        if side == 2:
            continue
        mirror_dict[index] = mirror

    for rt_vert, lf_vert in mirror_dict.items():
        lf_verts.append(lf_vert)
        rt_verts.append(rt_vert)

    return lf_verts, cn_verts, rt_verts  



def getAllVertexPositions(geometry, world_space=True):
    sel_list = om.MSelectionList()
    sel_list.add(geometry)
    mesh = om.MObject()
    sel_list.getDependNode(0, mesh)

    vert_positions = []
    vert_iter = om.MItMeshVertex(mesh)

    space = om.MSpace.kObject
    if world_space:
        space = om.MSpace.kWorld

    while not vert_iter.isDone():
        point = vert_iter.position(space)
        vert_positions.append([point[0], point[1], point[2]])
        vert_iter.next()
    return vert_positions


def getCurrentGeometry():
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
            

def _getSelectionPairs(geometry, vert_indices, mirror_src, lf_verts, cn_verts, rt_verts):
    if mirror_src == LEFT:
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



def mirrorSelection(vert_selection, center_edge, mirror_src):
    geometry, edge_index = center_edge.split('.')
    edge_index = int(edge_index.split('e[')[1].split(']')[0])
    if edge_index > (mc.polyEvaluate(geometry, e=True) - 1):
        raise RuntimeError("Edge '%s' is not valid." %center_edge)
    
    vert_indices = [int(vert.split('.vtx[')[1].split(']')[0]) for vert in vert_selection]
    
    lf_verts, cn_verts, rt_verts = self.getSymmetry(center_edge)
    
    _mirrorSelection(vert_indices, geometry, mirror_src, lf_verts, cn_verts, rt_verts)


def _mirrorSelection(vert_indices, geometry, mirror_src, lf_verts, cn_verts, rt_verts):
    vert_positions = getAllVertexPositions(geometry, world_space=False)
        
    mirror_pairs, cn_verts = _getSelectionPairs(geometry, vert_indices, mirror_src, 
                                                lf_verts, cn_verts, rt_verts)

    mc.undoInfo(openChunk=True)

    for src_vert, dst_vert in list(mirror_pairs):
        src_pos = vert_positions[src_vert]
        mc.move(src_pos[0] * -1, src_pos[1], src_pos[2],
                '%s.vtx[%s]' %(geometry, dst_vert), a=True, os=True)

    for cn_vert in cn_verts:
        cn_pos = vert_positions[cn_vert]
        mc.move(0, cn_pos[1], cn_pos[2],
                '%s.vtx[%s]' %(geometry, cn_vert), a=True, os=True)

    mc.undoInfo(closeChunk=True)

 
def _flip(geometry, lf_verts, cn_verts, rt_verts):
    vert_positions = getAllVertexPositions(geometry, world_space=False)
    src = lf_verts; dst = rt_verts

    mc.undoInfo(openChunk=True)

    for src_vert, dst_vert in zip(src, dst):
        if src_vert == -1 or dst_vert == -1: continue
        src_pos = vert_positions[src_vert]
        dst_pos = vert_positions[dst_vert]
        mc.move(src_pos[0] * -1, src_pos[1], src_pos[2],
                '%s.vtx[%s]' %(geometry, dst_vert), a=True, os=True)
        mc.move(dst_pos[0] * -1, dst_pos[1], dst_pos[2],
                '%s.vtx[%s]' %(geometry, src_vert), a=True, os=True)
        
    for cn_vert in cn_verts:
        if cn_vert == -1: continue
        cn_pos = vert_positions[cn_vert]
        mc.move(cn_pos[0] * -1, cn_pos[1], cn_pos[2],
                '%s.vtx[%s]' %(geometry, cn_vert), a=True, os=True)

    mc.undoInfo(closeChunk=True)
    


def _resetDelta(base_geometry, delta_geometry, percentage=1.0, axis = 'xyz'):    
    
    base_vert_positions = getAllVertexPositions(base_geometry,  world_space=False)
    delta_vert_positions = getAllVertexPositions(delta_geometry,  world_space=False)
    
    if percentage == 0.0:
        return

    mc.undoInfo(openChunk=True)

    if percentage == 1.0:  
        for vert_index in range(mc.polyEvaluate(base_geometry, v=True)):
            base_vert_pos = base_vert_positions[vert_index]  
            delta_vert_pos = delta_vert_positions[vert_index]
            
            if axis == 'xyz':  
                mc.move(base_vert_pos[0], base_vert_pos[1], base_vert_pos[2],
                        '{}.vtx[{}]'.format(delta_geometry, vert_index), a=True, os=True)
            else:
                if axis == 'x':
                    mc.move(base_vert_pos[0], delta_vert_pos[1], delta_vert_pos[2],
                    '{}.vtx[{}]'.format(delta_geometry, vert_index), a=True, os=True)
                if axis == 'y':
                    mc.move(delta_vert_pos[0], base_vert_pos[1], delta_vert_pos[2],
                    '{}.vtx[{}]'.format(delta_geometry, vert_index), a=True, os=True)
                
                if axis == 'z':
                    mc.move(delta_vert_pos[0], delta_vert_pos[1], base_vert_pos[2],
                    '{}.vtx[{}]'.format(delta_geometry, vert_index), a=True, os=True)        
        
    else:
        percentage = max(min(percentage, 1.0), 0.0)
        
        for vert_index in range(mc.polyEvaluate(base_geometry, v=True)):
            base_vert_pos_ori  = Vector(base_vert_positions[vert_index])
            delta_vert_pos_ori = Vector(delta_vert_positions[vert_index])
            
            vector = delta_vert_pos_ori - base_vert_pos_ori
            vector *= (1.0 - percentage)
            delta_vert_pos = base_vert_pos_ori + vector
            base_vert_pos = delta_vert_pos_ori + vector
            
            if axis == 'xyz':  
                mc.move(base_vert_pos[0], base_vert_pos[1], base_vert_pos[2],
                        '{}.vtx[{}]'.format(delta_geometry, vert_index), a=True, os=True)
            else:
                if axis == 'x':
                    mc.move(delta_vert_pos[0], delta_vert_pos_ori[1], delta_vert_pos_ori[2],
                    '{}.vtx[{}]'.format(delta_geometry, vert_index), a=True, os=True)
                if axis == 'y':
                    mc.move(delta_vert_pos_ori[0], delta_vert_pos[1], delta_vert_pos_ori[2],
                    '{}.vtx[{}]'.format(delta_geometry, vert_index), a=True, os=True)
                
                if axis == 'z':
                    mc.move(delta_vert_pos_ori[0], delta_vert_pos_ori[1], delta_vert_pos[2],
                    '{}.vtx[{}]'.format(delta_geometry, vert_index), a=True, os=True)      
 
 
    mc.undoInfo(closeChunk=True)


def _resetDeltaSelection(vert_indices, base_geometry, delta_geometry, percentage=1.0, axis ='xyz'):    
    base_vert_positions = getAllVertexPositions(base_geometry,  world_space=False)
    delta_vert_positions = getAllVertexPositions(delta_geometry,  world_space=False)
    
    if percentage == 0.0:
        return
    
    mc.undoInfo(openChunk=True)
    
    if percentage == 1.0:
        for vert_index in vert_indices:
            base_vert_pos = base_vert_positions[vert_index]  
            delta_vert_pos = delta_vert_positions[vert_index]
                    
            if axis == 'xyz':  
                mc.move(base_vert_pos[0], base_vert_pos[1], base_vert_pos[2],
                        '{}.vtx[{}]'.format(delta_geometry, vert_index), a=True, os=True)
            else:
                if axis == 'x':
                    mc.move(base_vert_pos[0], delta_vert_pos[1], delta_vert_pos[2],
                    '{}.vtx[{}]'.format(delta_geometry, vert_index), a=True, os=True)
                if axis == 'y':
                    mc.move(delta_vert_pos[0], base_vert_pos[1], delta_vert_pos[2],
                    '{}.vtx[{}]'.format(delta_geometry, vert_index), a=True, os=True)
                                    
                if axis == 'z':
                    mc.move(delta_vert_pos[0], delta_vert_pos[1], base_vert_pos[2],
                    '{}.vtx[{}]'.format(delta_geometry, vert_index), a=True, os=True)
            

    else:
        percentage = max(min(percentage, 1.0), 0.0)
        
        delta_vert_positions = getAllVertexPositions(delta_geometry, world_space=False)
        base_vert_positions = getAllVertexPositions(base_geometry, world_space=False)
        
        for vert_index in vert_indices:
            base_vert_pos_ori  = Vector(base_vert_positions[vert_index])
            delta_vert_pos_ori = Vector(delta_vert_positions[vert_index])
            
            vector = delta_vert_pos_ori - base_vert_pos_ori
            vector *= (1.0 - percentage)
            delta_vert_pos = base_vert_pos_ori + vector
            base_vert_pos = delta_vert_pos_ori + vector
     
            if axis == 'xyz':  
                mc.move(base_vert_pos[0], base_vert_pos[1], base_vert_pos[2],
                        '{}.vtx[{}]'.format(delta_geometry, vert_index), a=True, os=True)
            else:
                if axis == 'x':
                    mc.move(delta_vert_pos[0], delta_vert_pos_ori[1], delta_vert_pos_ori[2],
                    '{}.vtx[{}]'.format(delta_geometry, vert_index), a=True, os=True)
                if axis == 'y':
                    mc.move(delta_vert_pos_ori[0], delta_vert_pos[1], delta_vert_pos_ori[2],
                    '{}.vtx[{}]'.format(delta_geometry, vert_index),  os=True)
                
                if axis == 'z':
                    mc.move(delta_vert_pos_ori[0], delta_vert_pos_ori[1], delta_vert_pos[2],
                    '{}.vtx[{}]'.format(delta_geometry, vert_index), a=True, os=True)   
    
    mc.undoInfo(closeChunk=True)               




def resetDelta(base_geometry, delta_geometry, percentage=1.0, axis = 'xyz'):
    """
    ex: resetDelta(str(pm.selected()[0]), str(pm.selected()[1]))
    """
    [_resetDelta(base_geometry, delta_geometry, percentage=percentage, axis = letter) for letter in axis]
    


def flipMesh(center_edge):
    geometry = str(center_edge).split('.e')[0]
    lf_verts, cn_verts, rt_verts = getSymmetry(center_edge)
    _flip(geometry, lf_verts, cn_verts, rt_verts)



def resetDeltaSelection(base_geometry, delta_geometry, percentage=1.0, axis = 'xyz'):
    [_resetDeltaSelection(getCurrentGeometry()[1], base_geometry , delta_geometry, percentage=percentage, axis = letter) for letter in axis]
    
    
    
        
resetDelta('eyeBrow_down_NORM1', 'eyeBrow_down_beauty3', percentage=1, axis ='xyz')  
# resetDeltaSelection('eyeBrow_down_NORM', 'eyeBrow_down_beauty1', percentage=1, axis ='xyz')  

# flipMesh('eyeBrow_down_beauty1.e[51]')
