#-----------------------------------
# IMPORT CUSTOM MODULES
#----------------------------------- 

import adbrower
reload(adbrower)

adb = adbrower.Adbrower()

import adb_utils.Class__Folli as adbFolli
reload (adbFolli)   

import adb_utils.Class__AddAttr as adbAttr
reload (adbAttr)

#-----------------------------------
#  DECORATORS
#----------------------------------- 

from adbrower import undo
from adbrower import changeColor
from adb_utils.Class__Transforms import Transform

#-----------------------------------
# FUNCTION
#-----------------------------------

@changeColor('index', col = (22))
def follicule_rivet( 
                    references_obj,
                     target_mesh,
                     visibility = True,                    
                    ):
    """
    Method that creates a follicule rivet on the target mesh base on the position of the 
    reference object
    
    # NOTES: UV must be done on the target mesh in order to work properly
    
        @param obj            : (list) list of objects that is used as reference to get the closest point on the surface
        @param target_mesh    : (str) name of the transform of the mesh.
        @param visibility     : (bool) visibility of the locators

    Returns:
            (list) Follicules, follicule_locs

    """
                                                
    follicule_sys =  adbFolli.Folli(1, len(references_obj), radius = 0.5, sub = target_mesh) 
    follicule_joint = follicule_sys.getJoints
    follicule_shape = follicule_sys.getFollicules
    follicules = [x.getParent() for x in follicule_shape]
    follicule_locs = []
    
    ## Set u_v values
    u_v_values = [Transform.get_closest_u_v_point_on_mesh(obj, target_mesh) for obj in references_obj]
    for uv_values, joint in zip (u_v_values, follicule_joint ):
        joint.u_param.set(uv_values[0]*100)
        joint.v_param.set(uv_values[1]*100)
        
   
    ## Replace follicules_joints by a locators
    for fol_jnt, fol in zip (follicule_joint, follicules):    
        foll_loc = pm.spaceLocator()
        follicule_locs.append(foll_loc)
        pm.rename(foll_loc, fol_jnt.replace('jnt','loc'))
        pm.matchTransform(foll_loc, fol, pos= True,  rot= True)
        pm.parent(foll_loc, fol_jnt.getParent())  
        follicule_loc_attr = adbAttr.NodeAttr([foll_loc])
        follicule_loc_attr.addAttr('U_Param', fol_jnt.u_param.get(),  min = -100, max =100) 
        follicule_loc_attr.addAttr('V_Param', fol_jnt.v_param.get(),  min = -100, max =100)         
        foll_loc.U_Param >> fol.u_param
        foll_loc.V_Param >> fol.v_param
     
           
    ## Clean up
    pm.delete(fol_jnt)
    [x.v.set(0) for x in follicule_shape] ## Hide the red follicule
    [x.v.set(visibility) for x in follicule_locs] 
        
    
    return follicules, follicule_locs


    
follicule_rivet([ 'locator1'], 'pPlane1'  )

    