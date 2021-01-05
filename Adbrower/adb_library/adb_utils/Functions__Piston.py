import sys
import traceback
import pymel.core as pm
import maya.cmds as mc

import adbrower

adb = adbrower.Adbrower()



def createPiston(parent, child, control):
    """
    createPiston('joint1', 'joint2', 'Control')
    """
    try:
        pm.parent(child, parent)
    except RuntimeError:
        pass

    ikNode, effector = pm.ikHandle( n='{}_IkHandle'.format(control), sj=parent, ee=child)
    ik_group = adb.makeroot_func(ikNode, forceNameConvention=False)
    pm.matchTransform(ik_group, control, pos=1, rot=0)
    pm.parent(ik_group, control)
    ikNode.v.set(0)



def createDoublePiston(
                 lowRootjnt,
                 lowEndjnt,
                 topRootjnt,
                 topEndjnt,
                 low_ctrl,
                 top_ctrl,
                 ):
    """
    Creates a piston system

    import adb_utils.Functions__Piston as adbPiston
    reload (adbPiston)

    test = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5__LOC', 'joint6__LOC']
    """
    ## create a root group over the controller
    rootGrp_low = adb.makeroot_func(low_ctrl)
    rootGrp_top = adb.makeroot_func(top_ctrl)

    pm.parent(lowRootjnt,low_ctrl)
    pm.parent(topRootjnt,top_ctrl)


    ## creating the Ik handles
    lowIk = pm.ikHandle( n='{}_IkHandle'.format(lowRootjnt), sj=lowRootjnt, ee=lowEndjnt, )
    topIk = pm.ikHandle( n='{}_IkHandle'.format(topRootjnt), sj=topRootjnt, ee=topEndjnt, )

    pm.parent(lowIk[0],top_ctrl)
    pm.parent(topIk[0],low_ctrl)

    pm.matchTransform(lowIk[0],topRootjnt, pos=True)
    pm.matchTransform(topIk[0],lowRootjnt, pos=True)

    ## hiding the Ik handles
    pm.PyNode(topIk[1]).v.set(0)
    pm.PyNode(lowIk[1]).v.set(0)
    pm.PyNode(topIk[0]).v.set(0)
    pm.PyNode(lowIk[0]).v.set(0)



















