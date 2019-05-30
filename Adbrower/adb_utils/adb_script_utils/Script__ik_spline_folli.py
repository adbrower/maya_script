import traceback
import maya.cmds as mc
import pymel.core as pm

import adbrower
reload(adbrower)
adb = adbrower.Adbrower()

from adbrower import lprint
from adbrower import flatList

import adb_utils.adb_script_utils.Script__WrapDeformer as adbWrap
import adb_utils.Class__AddAttr as adbAttr
import adb_utils.adb_script_utils.Script__ProxyPlane as adbProxy


attribute_ctrl = 'cog_ctrl'
geo = 'm__measuring_tape__hi_msh__'
ik_spline_joints = ['m__measuring_tape_ikSpline_01', 'm__measuring_tape_ikSpline_02', 'm__measuring_tape_ikSpline_03', 'm__measuring_tape_ikSpline_04', 'm__measuring_tape_ikSpline_05', 'm__measuring_tape_ikSpline_06', 'm__measuring_tape_ikSpline_07', 'm__measuring_tape_ikSpline_08', 'm__measuring_tape_ikSpline_09', 'm__measuring_tape_ikSpline_010', 'm__measuring_tape_ikSpline_011', 'm__measuring_tape_ikSpline_012', 'm__measuring_tape_ikSpline_013', 'm__measuring_tape_ikSpline_014', 'm__measuring_tape_ikSpline_015']

ik_spline_curve = 'ik_spline__curve1'
bind_joints = ['m__measuring_tape_bind_01', 'm__measuring_tape_bind_02', 'm__measuring_tape_bind_03', 'm__measuring_tape_bind_04', 'm__measuring_tape_bind_05']

    
ik_curve_proxy = adbProxy.plane_proxy(ik_spline_joints, 'x__ik_curve_proxy__msh__', 'z' )
ik_spline_proxy = adbProxy.plane_proxy(ik_spline_joints,'x__ik_spline_proxy__msh__', 'z')
folli_proxy = adbProxy.plane_proxy(ik_spline_joints, 'x__folli_proxy__msh__', 'z')

pm.polySmooth(ik_curve_proxy, ch=0, ost=1, khe=0, ps=0.1, kmb=1, bnr=1, mth=0, suv=1, peh=0, ksb=1, ro=1, sdt=2, ofc=0, kt=1, ovb=1, dv=1, ofb=3, kb=1, c=1, ocr=0, dpe=1, sl=1)
pm.polySmooth(ik_spline_proxy, ch=0, ost=1, khe=0, ps=0.1, kmb=1, bnr=1, mth=0, suv=1, peh=0, ksb=1, ro=1, sdt=2, ofc=0, kt=1, ovb=1, dv=1, ofb=3, kb=1, c=1, ocr=0, dpe=1, sl=1)
pm.polySmooth(folli_proxy, ch=0, ost=1, khe=0, ps=0.1, kmb=1, bnr=1, mth=0, suv=1, peh=0, ksb=1, ro=1, sdt=2, ofc=0, kt=1, ovb=1, dv=1, ofb=3, kb=1, c=1, ocr=0, dpe=1, sl=1)


pm.skinCluster(ik_curve_proxy, bind_joints)
pm.skinCluster(ik_spline_proxy, ik_spline_joints)
pm.skinCluster(folli_proxy, bind_joints)


adbWrap.wrapDeformer(ik_spline_curve, ik_curve_proxy)
wrap_ik_spline = adbWrap.wrapDeformer(geo, ik_spline_proxy)
wrap_folli = adbWrap.wrapDeformer(geo, folli_proxy)

wrap_ik_spline.rename('x__ik_spline__wrap__')
wrap_folli.rename('x__follicule__wrap__')


## Swith set up
rv_ik_spline = pm.shadingNode('remapValue', asUtility = 1, n = 'ik_spline__rv__')
rev_ik_spline = pm.shadingNode('reverse', asUtility = 1, n = 'ik_spline__rv__')

rv_ik_spline.inputMin.set(1)
rv_ik_spline.inputMax.set(10)

## add the swith attribute
ik_blend_ctrl = adbAttr.NodeAttr([attribute_ctrl])
ik_blend_ctrl.addAttr('IK_blend', 1, min=1, max=10)

ParamBlend = pm.PyNode(attribute_ctrl).name() + ".IK_blend"

pm.PyNode(ParamBlend) >> pm.PyNode(rv_ik_spline).inputValue  


pm.PyNode(rv_ik_spline).outValue >> pm.PyNode(wrap_folli).envelope
pm.PyNode(rv_ik_spline).outValue >> pm.PyNode(rev_ik_spline).inputX
pm.PyNode(rev_ik_spline).outputX >> pm.PyNode(wrap_ik_spline).envelope

## Clean up
pm.PyNode(ik_spline_curve).v.set(False)



