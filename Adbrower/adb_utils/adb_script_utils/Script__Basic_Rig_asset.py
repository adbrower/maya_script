import traceback
import maya.cmds as mc
import pymel.core as pm

import adbrower
reload(adbrower)

adb = adbrower.Adbrower()

import ShapesLibrary as sl
reload(sl)

from adbrower import lprint
from adbrower import flatList

from adbrower import makeroot
from adbrower import changeColor


asset = pm.selected()

@changeColor('index', col = 17)
@makeroot()
def aaa(target):

    pm.select(target, r =True)
    ctrl = sl.square_prop_shape()
    new_name = pm.rename(ctrl,target)
    adb.AutoSuffix([new_name])
    pm.parentConstraint(ctrl, target, mo=True)
    pm.scaleConstraint(ctrl, target, mo=True)
    pm.select(None)
    
    return ctrl
    

for x in asset:   
    aaa(x)


    