
import maya.cmds as mc
import pymel.core as pm

def curveFromCylinder(mesh = pm.selected()):
    """
    Creates a curve from the middle point from every loops    
    @param mesh: List. By default is pm.selected()
    """
    
    def createCurveFrom(selection = pm.selected(), curve_name = 'curve'):
        """ 
        Creates a curve from the position values of the selection 
        """
        def createLocs(subject):                         
            loc_align = pm.spaceLocator()
            pm.matchTransform(loc_align,subject, rot=True, pos=True)
            return loc_align
        starting_locs = [createLocs(x) for x in selection]
        pos = [pm.xform(x, ws=True, q=True, t=True) for x in starting_locs]
        knot = []
        for i in range(len(selection)):
            knot.append(i)
        _curve = pm.curve(p = pos, k =knot, d=1, n=curve_name)
        pm.rebuildCurve(_curve, rt=0, ch=0, end=1, d=3, kr=0, s=len(selection), kcp=0, tol=0.1, kt=0, rpo=1, kep=1)    
        pm.delete(starting_locs)
        return(_curve)

    def centre_joint():
        """
        Creates a joint in the centre of the selection. You can select objects, components...
        """
        sel = pm.ls(sl=1, fl=1)

        bb = [0, 0, 0, 0, 0, 0]
        for obj in sel:
            pos = pm.xform(obj, q=1, ws=1, bb=1)
            for i in range(6):
                bb[i] += pos[i]
        for i in range(6):
            bb[i] /= len(sel)
        pm.select(cl=True)
        return pm.joint(p=((bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, (bb[2] + bb[5]) / 2))
    
    
    for mesh_name in mesh:         
        border_loop = pm.polySelect(mesh_name,  eb = 1) or []        
        pm.polySelect(mesh_name,  edgeRing = 1)        
        edgeLoop_num = len(pm.selected()) 
        pm.polySelect(mesh_name,  el = 1)
        
        if border_loop:
            [pm.pickWalk(type='edgeloop', d='left') for x in range(1)]
            
            temp_all_jnts = []
            for index in range(edgeLoop_num): 
                pm.polySelect(mesh_name,edgeLoopPattern=(1,1))
                [pm.pickWalk(type='edgeloop', d='left') for x in range(index)]
                joint = centre_joint()
                temp_all_jnts.append(joint)
                
            all_jnts = [x for x in temp_all_jnts[1:]]
            pm.delete(temp_all_jnts[0])
                
        else:                   
            all_jnts = []
            for index in range(edgeLoop_num): 
                pm.polySelect(mesh_name,edgeLoopPattern=(1,1))
                [pm.pickWalk(type='edgeloop', d='left') for x in range(index)]
                joint = centre_joint()
                all_jnts.append(joint)
         
     
        createCurveFrom(all_jnts)
        pm.delete(all_jnts)
        
    
curveFromCylinder()

