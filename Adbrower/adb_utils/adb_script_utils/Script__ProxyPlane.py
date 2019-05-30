import maya.cmds as mc
import pymel.core as pm

import adb_utils.rig_utils.Class__BoundingBox  as adbBBox


def plane_proxy(joints_chain, name , axis = 'z', type = 'mesh'):
    ''' 
    Create a plane proxy for a joint chain
    
    @param joints_chain: list. List of the joints from which to create a curve
    @param name: String. Name of the final plane proxy
    @param axis: String {'x','y' or 'z'}
    
    NOTES!! : The joint chain need to be proprely oriented
    
    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_utils.adb_script_utils.Script__ProxyPlane as adbProxy
    reload (adbProxy)
    
    Proxy_plane = adbProxy.plane_proxy(pm.selected(), 'adb', 'z')
    '''
    all_xmax_locs = []
    all_xmin_locs = []
    all_loc_groups = []


    def createLocs(subject):                         
        loc_align = pm.spaceLocator()
        pm.matchTransform(loc_align,subject, rot=True, pos=True)
        return loc_align

    def createCurve(pos ,curve_name):
        knot = []
        for i in range(len(joints_chain)):
            knot.append(i)
        _curve= pm.curve(p = pos, k =knot, d=1, n=curve_name)
        # pm.rebuildCurve(_curve, rt=0, ch=0, end=1, d=3, kr=0, s=len(joints_chain), kcp=0, tol=0.1, kt=0, rpo=1, kep=1)        
        return _curve

    starting_locs = [createLocs(x) for x in joints_chain]

    for each in starting_locs:
        posBox = adbBBox.Bbox([each])
        posLocs = posBox.createPosLocs()

        posLocs_grp = pm.group(posLocs, n= '{}__grp__'.format(each) )
        all_loc_groups.append(posLocs_grp)
        pm.xform(posLocs_grp, cp=True)
        pm.matchTransform(posLocs_grp, each, pos=True, rot=True)

        if axis == 'y':
            max_value = posLocs[1]
            all_xmax_locs.append(max_value)

            min_value = posLocs[4]
            all_xmin_locs.append(min_value)
        
        elif axis == 'x':
            max_value = posLocs[3]
            all_xmax_locs.append(max_value)
            min_value = posLocs[0]
            all_xmin_locs.append(min_value)

        elif axis == 'z':
            max_value = posLocs[-1]
            all_xmax_locs.append(max_value)

            min_value = posLocs[2]
            all_xmin_locs.append(min_value)
            
    pos_locs_xmax = [createLocs(x) for x in all_xmax_locs]
    all_xmax_values = [x.getTranslation() for x in pos_locs_xmax]

    pos_locs_xmin = [createLocs(x) for x in all_xmin_locs]
    all_xmin_values = [x.getTranslation() for x in pos_locs_xmin]

    curve1 = createCurve(all_xmax_values, 'max_curve')
    curve2 = createCurve(all_xmin_values, 'min_curve')

    if type == 'mesh':
        nurbs_plane = pm.loft(curve1, curve2, c=0, ch=0, reverseSurfaceNormals = True, d=1, ar=1, u=1, rn=1, po=0)[0]
        plane_msh = pm.nurbsToPoly(nurbs_plane, n=name, uss=1, ch=0, ft=0.01, d=0.1, pt=1, f=2, mrt=0, mel=0.001, ntr=0, vn=1, pc=100, chr=0.1, un=len(pm.PyNode(curve2).getShape().getCVs()), 
        vt=1, ut=1, ucr=0, cht=0.2, mnd=1, es=0, uch=0)[0]
        pm.delete(nurbs_plane)
        
    elif type == 'nurbs':
        pm.rebuildCurve(curve1, rt=0, ch=0, end=1, d=3, kr=0, s=len(joints_chain), kcp=0, tol=0.1, kt=0, rpo=1, kep=1)
        pm.rebuildCurve(curve2, rt=0, ch=0, end=1, d=3, kr=0, s=len(joints_chain), kcp=0, tol=0.1, kt=0, rpo=1, kep=1)
        plane_msh = pm.loft(curve1, curve2, n=name, c=0, ch=0, reverseSurfaceNormals = True, d=1, ar=1, u=1, rn=1, po=0)[0]
              
    mc.DeleteHistory(plane_msh)
    mc.CenterPivot(plane_msh)
    
    ## cleanUp
    pm.delete(starting_locs, all_loc_groups, pos_locs_xmax, pos_locs_xmin)
    pm.delete(curve1)
    pm.delete(curve2)
            
    return plane_msh
    
    
# plane_proxy(pm.selected(), 'proxy' , axis = 'x', type = 'mesh')
    
    