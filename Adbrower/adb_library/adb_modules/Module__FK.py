# ------------------------------------------------------
# FK Module
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import sys
import os
import ast
import importlib

import pymel.core as pm
import maya.cmds as mc

import ShapesLibrary as sl
from CollDict import indexColor

import adbrower
adb = adbrower.Adbrower()
from adbrower import undo, changeColor, makeroot, lockAttr

import adb_core.ModuleBase as moduleBase
import adb_core.Class__Control as Control
import adb_core.NameConv_utils as NC
import adb_core.Class__AddAttr as adbAttr
import adb_core.Class__Joint as Joint
import adb_core.Class__Locator as Locator
from adb_core.Class__Transforms import Transform

import adb_rigModules.ModuleGuides as moduleGuides


importlib.reload(moduleBase)
importlib.reload(moduleGuides)
importlib.reload(Joint)
importlib.reload(adbAttr)
importlib.reload(Locator)

# =========================
# CLASS
# =========================

class FkModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(FkModel, self).__init__()
        pass


class Fk(moduleBase.ModuleBase):
    def __init__(self,
                 module_name,
                 count = 3,
                 parent = None,
                 ):
        """[summary]

        Args:
            module_name ([type]): [description]
            count (int, optional): [description]. Defaults to 3.
            parent ([type], optional): [description]. Defaults to None.

        Example:
            import adb_library.adb_modules.Module__FK as Module__FK
            reload(Module__FK)

            FK = Module__FK.Fk('audrey', count = 8)

            # FK.start()
            # FK.build()

            # FK.FkGuides.exportData(path='C:/Users/Audrey/Desktop/')
        """
        super(Fk, self).__init__()

        self._MODEL = FkModel()

        self.NAME   = module_name
        self.count  = count
        self.parent = parent

    def __repr__(self):
        return str('{} : {} \n {}'.format(self.__class__.__name__, self.subjNAMEect, self.__class__))

# =========================
# METHOD
# =========================


    def start(self, metaDataNode = None, path=None):
        super(Fk, self)._start(self.NAME, _metaDataNode = metaDataNode)

        FkGuide = [moduleGuides.ModuleGuides.createFkGuide(prefix='{}_{:02d}'.format(self.NAME, guide+1)).guides[0] for guide in range(self.count)]
        for index, guide in enumerate(FkGuide):
            pm.parent(guide, self.STARTERS_GRP)
            pm.move(guide, (0+(index), 0, 0), r=0, os=1)

        for _guide, guide in zip(FkGuide[0:-1], FkGuide[1:]):
            self.curve_setup(_guide, guide)

        self.FkGuides = moduleGuides.ModuleGuides(self.NAME.upper(), FkGuide, path=path)
        readPath = self.FkGuides.DATA_PATH + '/' + self.FkGuides.RIG_NAME + '__GLOC.ini'
        if os.path.exists(readPath):
            try:
                sys.stdout.write('load from : {}'.format(readPath))
                self.loadData = self.FkGuides.loadData(readPath)
                for guide in self.FkGuides.guides:
                    _registeredAttributes = ast.literal_eval(self.loadData.get(str(guide), 'registeredAttributes'))
                    for attribute in _registeredAttributes:
                        try:
                            pm.setAttr('{}.{}'.format(guide, attribute), ast.literal_eval(self.loadData.get(str(guide), str(attribute))))
                        except:
                            pass
                    pm.parent(guide, self.loadData.get(str(guide), 'parent'))
                    value, index =  ast.literal_eval(self.loadData.get(str(guide), 'shape'))
                    pm.setAttr('{}.Shape'.format(guide), index)
                    value, index =  ast.literal_eval(self.loadData.get(str(guide), 'color'))
                    pm.setAttr('{}.Color'.format(guide), index)
            except:
                pass



    def build(self):
        super(Fk, self)._build()
        points = [pm.xform(guide, rp=True , q=True , ws=True) for guide in self.FkGuides.guides]
        jnt = Joint.Joint.point_base(*points, name = self.NAME, chain=False, padding=2)
        for _jnt, guide in zip(jnt.joints, self.FkGuides.guides):
            if self.loadData.get(str(guide), 'parent') == self.STARTERS_GRP:
                pm.parent(_jnt, self.OUTPUT_GRP)
            else:
                pm.parent(_jnt, self.loadData.get(str(guide), 'parent').replace('GLOC', NC.JOINT))

        self.side = NC.getSideFromPosition(self.FkGuides.guides[0])
        if self.side == 'L':
            self.col_main = indexColor['fluoBlue']

        elif self.side == 'R':
            self.col_main = indexColor['fluoRed']
        else:
            self.col_main = indexColor['yellow']

        fk_control = []
        for guide in self.FkGuides.guides:
            if self.loadData.get(str(guide), 'color') == 'auto':
                _color = self.col_main
            else:
                valueColor, _indexColor =  ast.literal_eval(self.loadData.get(str(guide), 'color'))
                valueShape, indexShape =  ast.literal_eval(self.loadData.get(str(guide), 'shape'))
                _color = indexColor[str(valueColor)]
            fk = Control.Control.fkShape(jnt.joints,
                                                shape=sl.sl[valueShape],
                                                scale=1,
                                                color=('index', _color)
                                                )
            fk_control.extend(fk)

        [pm.delete(x) for x in [self.INPUT_GRP, self.VISRULE_GRP, self.RIG_GRP]]
        self.STARTERS_GRP.v.set(0)



    def connect(self):
        super(Fk, self)._connect()
        pm.delete(self.STARTERS_GRP)

# =========================
# SOLVERS
# =========================

    @changeColor('index', col=2)
    def curve_setup(self, basePoint, endPoint):
        baseJoint = Joint.Joint.point_base(pm.PyNode(basePoint).getRotatePivot(space='world'), name='{}Base__{}'.format(NC.getNameNoSuffix(basePoint), NC.JOINT)).joints[0]
        endJoint = Joint.Joint.point_base(pm.PyNode(endPoint).getRotatePivot(space='world'), name='{}End__{}'.format(NC.getNameNoSuffix(endPoint),  NC.JOINT)).joints[0]
        pm.setAttr('{}.hiddenInOutliner'.format(baseJoint), 1)
        pm.setAttr('{}.hiddenInOutliner'.format(endJoint), 1)
        pm.parent(baseJoint, basePoint)
        pm.parent(endJoint, endPoint)

        starPointPos = pm.xform(basePoint, q=1, ws=1, t=1)
        endPointPos = pm.xform(endPoint, q=1, ws=1, t=1)
        [pm.PyNode(joint).v.set(0) for joint in [baseJoint, endJoint]]

        starting_locs = [baseJoint, endJoint]
        pos = [pm.xform(x, ws=True, q=True, t=True) for x in starting_locs]
        knot = []
        for i in range(len(starting_locs)):
            knot.append(i)
        _curve = pm.curve(p=pos, k=knot, d=1, n='{}_{}_CRV'.format(self.NAME, NC.getNameNoSuffix(baseJoint)))
        pm.skinCluster(baseJoint , _curve, endJoint)
        pm.setAttr(_curve.inheritsTransform, 0)
        pm.setAttr(_curve.template, 1)
        pm.setAttr(_curve.hiddenInOutliner, 1)
        pm.parent(_curve, pm.PyNode(basePoint))
        return _curve



# test = Fk('audrey', count = 8)

# test.start()
# test.build()

# test.FkGuides.exportData(path='C:/Users/Audrey/Desktop/')