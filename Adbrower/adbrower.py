
# ------------------------------------------------------
# adbrower Module
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
#
#
# Sections:
#
#    1.  Import Custom Modules
#    2.  Decorators - Function import rapide
#    3.  Function Reutilisables
#    4.  Information
#    5.  Skinning - BlendShape - Cloth - Functions
#    6.  Functions Utilitaires
#    7.  Shapes - Curves Management
#    8.  Display Options
#    9.  Attribute Editor
#    10. Naming
#
# ------------------------------------------------------
import time
import sys
from functools import wraps

import pymel.core as pm
import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as om

import adb_core.NameConv_utils as NC
import ShapesLibrary as sl
from CollDict import suffixDic
# reload(NC)

#TODO: put @staticmethod

# -----------------------------------
# 2.1 DECORATORS
# -----------------------------------

def timeit(method):
    """
    from: https://medium.com/pythonhive/python-decorator-to-measure-the-execution-time-of-methods-fa04cb6bb36d
    """
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('TIME: %r ----  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result
    return timed

def repeat(label):
    """
    Make a function repeatable and adds it to the recent List Command
    original from: https://gist.github.com/justinfx/f86320b6d9b567e6b8e2
    """
    def repeatLastCommand():
        if _repeat_function is not None:
            _repeat_function(*_args, **_kwargs)

    def real_repeate(func):
        def _repeatfunc(*args, **kwargs):
            global _repeat_function
            global _args
            global _kwargs

            _repeat_function = func(*args, **kwargs)

            sys.modules[__name__].repeatLastCommand = lambda : func(*args, **kwargs)
            rplString = 'python("{}.repeatLastCommand()")'.format(__name__)
            pm.repeatLast(ac=rplString, acl=func.__name__, h=10)

        return _repeatfunc
    return real_repeate


def undo(func):
    """
    Puts the wrapped `func` into a single Maya Undo action, then
    undoes it when the function enters the finally: block
    from schworer Github
    """
    @wraps(func)
    def _undofunc(*args, **kwargs):
        try:
            # start an undo chunk
            mc.undoInfo(ock=True)
            return func(*args, **kwargs)
        finally:
            # after calling the func, end the undo chunk
            mc.undoInfo(cck=True)
    return _undofunc


# ===============================================================================

def changeColor(type='rgb', col=(0.8, 0.5, 0.2)):
    """
    Puts the wrapped 'func' into a Nurbs.
    Sets the override color to a RGB value

    @param col : RGB values,
    #NOTE: Works on Transforms
    """
    def real_decorator(func):
        def _changeColorfunc(*args, **kwargs):
            _func = func(*args, **kwargs)
            pm.select(_func)
            ctrls = pm.selected()
            shapes = [x.getShapes() for x in ctrls] or []
            all_shapes = [x for i in shapes for x in i] or []

            if all_shapes == []:
                for ctrl in ctrls:
                    pm.PyNode(ctrl).overrideEnabled.set(1)

                    if type == 'rgb':
                        pm.PyNode(ctrl).overrideRGBColors.set(1)
                        pm.PyNode(ctrl).overrideColorRGB.set(col)

                    if type == 'index':
                        pm.PyNode(ctrl).overrideRGBColors.set(0)
                        pm.PyNode(ctrl).overrideColor.set(col)
            else:
                for ctrl in all_shapes:
                    pm.PyNode(ctrl).overrideEnabled.set(1)
                    if type == 'rgb':
                        pm.PyNode(ctrl).overrideRGBColors.set(1)
                        pm.PyNode(ctrl).overrideColorRGB.set(col)

                    if type == 'index':
                        pm.PyNode(ctrl).overrideRGBColors.set(0)
                        pm.PyNode(ctrl).overrideColor.set(col)
            return _func
        return _changeColorfunc
    return real_decorator


# ===============================================================================

def makeroot(suf='root', forceNameConvention = True):
    """
    Creates a root group over the function
    @param suf : String returning the suffix you want for your group
    """
    def real_decorator(func):
        def _makeroot(*args, **kwargs):
            f = func(*args, **kwargs)
            pm.select(f)
            oColl = pm.selected()
            for each in oColl:
                try:
                    suffix = each.name().split('__')[-2]
                    cutsuffix = '__{}__'.format(suffix)
                except:
                    suffix, cutsuffix = '', ''
                if forceNameConvention:
                    groupName =  '{}_{}__{}'.format(NC.getNameNoSuffix(each.name()), suf,  NC.GRP)
                else:
                    groupName = each.name() + '__' + suf + '__{}'.format(NC.GRP)
                oRoot = pm.group(n=groupName, em=True)
                for i in range(4):
                    oRoot.rename(oRoot.name().replace('___', '__'))
                oRoot.setTranslation(each.getRotatePivot(space='world'))
                oRoot.setRotation(each.getRotation(
                    space='world'), space='world')
                try:
                    pm.parent(oRoot, each.getParent())
                except:
                    pass
                pm.parent(each, oRoot)
                pm.setAttr(oRoot.v, keyable=False, cb=False)
                # oRoot.v.lock()
                try:
                    pm.makeIdentity(n=0, s=1, r=1, t=1, apply=True, pn=1)
                except:
                    pass
            pm.select(oColl)
            return oColl

        return _makeroot
    return real_decorator


# ===============================================================================


def propScale(func):
    """
    Scale proportional to the selection
    #NOTE: Works on the Transform
    """
    def _proportional_Scale(*args, **kwargs):
        my_selection = pm.selected()
        for sel in my_selection:
            Bbox = sel.getBoundingBox()
            minZ = [Bbox.max()[0], Bbox.center()[1], Bbox.min()[2]]
            maxZ = [Bbox.max()[0], Bbox.center()[1], Bbox.max()[2]]

            minX = [Bbox.min()[0], Bbox.center()[1], Bbox.max()[2]]
            maxX = [Bbox.min()[0], Bbox.center()[1], Bbox.min()[2]]

            def mminiLoc(pos, name):
                miniloc = pm.spaceLocator(position=pos, n=name)
                miniloc.overrideEnabled.set(1)
                miniloc.overrideRGBColors.set(1)
                miniloc.overrideColorRGB.set(1, 0, 0)

                miniloc.localScaleX.set(0.2)
                miniloc.localScaleY.set(0.2)
                miniloc.localScaleZ.set(0.2)

            pm.select(None)
            obj = func(*args, **kwargs)
            pm.matchTransform(obj, sel, pos=True)

            BboxCTL = obj.getBoundingBox()
            minZCTL = [BboxCTL.max()[0], BboxCTL.center()[1], BboxCTL.min()[2]]
            maxZCTL = [BboxCTL.max()[0], BboxCTL.center()[1], BboxCTL.max()[2]]

            minXCTL = [BboxCTL.min()[0], BboxCTL.center()[1], BboxCTL.max()[2]]
            maxXCTL = [BboxCTL.min()[0], BboxCTL.center()[1], BboxCTL.min()[2]]

            if (minZ[0] - maxX[0]) + 0.01 > (minX[2] - maxX[2]):
                axis = 'x'
            else:
                axis = 'z'

            if maxX > maxXCTL:
                newScaleX = (maxX[0] - maxXCTL[0])
            else:
                newScaleX =  (maxXCTL[0] - maxX[0])

            if newScaleX > 1.0:
                newScale = newScaleX
                obj.scaleX.set(newScale)
                obj.scaleY.set(newScale)
                obj.scaleZ.set(newScale)

        return obj
    return _proportional_Scale

# ===============================================================================


def lockAttr(att_to_lock=['tx', 'ty', 'tz', 'rx', 'ry', 'rx', 'rz', 'sx', 'sy', 'sz']):
    """
    Lock all the attribute except visibility
    """
    def real_decorator(func):
        def _lockAttr(*args, **kwargs):
            _func = func(*args, **kwargs)
            pm.select(_func)
            selection = pm.selected()
            try:
                for sel in selection:
                    for att in att_to_lock:
                        pm.PyNode(sel).setAttr(att, lock=True,
                                               channelBox=False, keyable=False)
            except:
                pass
            return _func
        return _lockAttr
    return real_decorator


def unlockAttr(att_to_lock=['tx', 'ty', 'tz', 'rx', 'ry', 'rx', 'rz', 'sx', 'sy', 'sz']):
    """
    Lock all the attribute except visibility
    """
    def real_decorator(func):
        def _lockAttr(*args, **kwargs):
            _func = func(*args, **kwargs)
            pm.select(_func)
            selection = pm.selected()
            try:
                for sel in selection:
                    for att in att_to_lock:
                        pm.PyNode(sel).setAttr(att, lock=False,
                                               channelBox=True, keyable=True)
            except:
                pass
            return _func
        return _lockAttr
    return real_decorator

    # ===============================
    # 2.2 FUNCTIONS IMPORT RAPIDE
    # ===============================


@undo
def lprint(oColl=pm.selected()):
    """
    Print my selection's names into a loop list
    """
    print('\n')
    for each in oColl:
        print(each)


def flatList(ori_list=''):
    """
    Flatten a list
    """
    flat_list = []
    for item in ori_list:
        if isinstance(item, list):
            for sub_item in item:
                flat_list.append(sub_item)
        else:
            flat_list.append(item)
    return flat_list


# ===============================
# CLASS MODULE ADBROWER
# ===============================

class Adbrower(object):
    def __init__(self):
        pass

    # ===============================
    # 3. FUNCTIONS IMPORT RAPIDE
    # ===============================


    class FUNCTIONS_REUTILISABLES():
        def __init__():
            pass


    @undo
    def ChainParent(self, sel=pm.selected()):
        """
        Parent Chained all Selected
        """
        def chain_parent(sel):
            for oParent, oChild in zip(sel[0:-1], sel[1:]):
                try:
                    pm.parent(oChild, None)
                    pm.parent(oChild, oParent)
                except:
                    continue
        chain_parent(pm.selected(type='transform'))


    @undo
    def makeroot_func(self, subject=pm.selected(), suff='root', forceNameConvention=False):
        pm.select(subject)
        oColl = pm.selected()

        oColl = pm.selected()
        for each in oColl:
            try:
                suffix = each.name().split('__')[-2]
                cutsuffix = '__{}__'.format(suffix)
            except:
                suffix, cutsuffix = '', ''
            if forceNameConvention:
                groupName =  '{}_{}__{}'.format(NC.getNameNoSuffix(each.name()), suff,  NC.GRP)
            else:
                groupName = each.name() + '__' + suff + '__{}'.format(NC.GRP)
            oRoot = pm.group(n=groupName, em=True)
            for i in range(4):
                oRoot.rename(oRoot.name().replace('___', '__'))
            oRoot.setTranslation(each.getRotatePivot(space='world'))
            oRoot.setRotation(each.getRotation(
                space='world'), space='world')
            try:
                pm.parent(oRoot, each.getParent())
            except:
                pass
            pm.parent(each, oRoot)
            pm.setAttr(oRoot.v, keyable=False, cb=False)
            # oRoot.v.lock()
            try:
                pm.makeIdentity(n=0, s=1, r=1, t=1, apply=True, pn=1)
            except:
                pass
        pm.select(oRoot)
        return oRoot

    # ===============================
    # 4. INFORMATIONS
    # ===============================

    class INFORMATIONS():
        def __init__():
            pass


    @staticmethod
    def loadPlugin(plugin):
        if not mc.pluginInfo(plugin, query=True, loaded=True):
            try:
                mc.loadPlugin(plugin)
            except RuntimeError:
                pm.warning('could not load plugin {}'.format(plugin))


    @undo
    def List(self):
        """
        Print my selection's names into a list
        """
        try:
            mylist = [x.name() for x in pm.selected()]
        except RuntimeError:
            mylist = [x.getTransform().name() for x in pm.selected()]
        mylist_string = [str(x) for x in mylist]  # Remove u'
        print(mylist_string)


    @undo
    def Type(self, sel=pm.selected()):
        """
        Print selection Type
        """

        all_types = []
        for each in sel:
            try:
                _type = (pm.objectType(pm.PyNode(each).getShape()))
            except RuntimeError:
                _type = (pm.objectType(pm.PyNode(each)))
            all_types.append(_type)
        return all_types


    @undo
    def TypePymel(self):
        sel = pm.selected()
        all_types = []
        for each in sel:
            try:
                _type = (type(pm.PyNode(each).getShape()))
            except:
                _type = (type(pm.PyNode(each)))
            all_types.append(_type)
            # print(_type)
        return all_types


    def getWorldTrans(self, subject=pm.selected()):
        """
        Get the world Position of something
        @param subject : List
        """
        for sel in subject:
            pos = pm.PyNode(sel).getRotatePivot(space='world')
        return pos


    def changePivotPoint(self, target, new_pivot_position):
        """
        Change de pivot Point of a subject base on a position of a element
        """
        pm.PyNode(target).setRotatePivot(
            [pm.PyNode(new_pivot_position).getRotatePivot()])
        pm.PyNode(target).setScalePivot(
            [pm.PyNode(new_pivot_position).getScalePivot()])
        return pm.PyNode(new_pivot_position).getScalePivot()


    @undo
    def ConsTarget(self, subject=pm.selected()):
        for each in subject:
            constraints = (set([
                                x for x in pm.PyNode(each).outputs()
                                if type(x) == pm.nodetypes.ParentConstraint
                                or type(x) == pm.nodetypes.PointConstraint
                                or type(x) == pm.nodetypes.ScaleConstraint
                                or type(x) == pm.nodetypes.OrientConstraint
                                or type(x) == pm.nodetypes.AimConstraint
            ]))

        targets = list(set(flatList([pm.listConnections(
            str(x) + '.constraintParentInverseMatrix', s=True) for x in constraints]))) or []

        if targets:
            print(" The targets are : ")
            for each in targets:
                pm.select(targets)
                print('\n{}{}'.format('       ---->  ', each))
            return targets
        else:
            sys.stdout.write('No Constraints \n ')


    @undo
    def ConsDriver(self, subject=pm.selected()):
        for each in subject:
            constraints = (set([
                x for x in pm.PyNode(each).outputs()
                if type(x) == pm.nodetypes.ParentConstraint
                or type(x) == pm.nodetypes.PointConstraint
                or type(x) == pm.nodetypes.ScaleConstraint
                or type(x) == pm.nodetypes.OrientConstraint
                or type(x) == pm.nodetypes.AimConstraint
            ]))
        sources = list(set(flatList([pm.listConnections(
            str(x) + '.target[*].targetParentMatrix', s=True) for x in constraints]))) or []
        if sources:
            print(" The sources are : ")
            for each in sources:
                pm.select(sources)
                print('\n{}{}'.format('       ---->  ', each))
            return sources
        else:
            sys.stdout.write('No Constraints \n ')

    # =========================================
    # 5. SKIN - CLOTH - BLENDSHAPE FUNCTIONS
    # =========================================

    class SKIN_BLENDSHAPE_CLOTH_FUNCTIONS():
        def __init__():
            pass


    @staticmethod
    def findDeformer(_tranformToCheck, deformerType='wrap'):
        """
        Find the blendShape from a string
        @param _tranformToCheck: Needs to be a String!!
        """
        result = []
        if not (pm.objExists(_tranformToCheck)):
            return result

        validList = mel.eval(
            'findRelatedDeformer("' + str(_tranformToCheck) + '")')

        if validList is None:
            return result

        for elem in validList:
            if pm.nodeType(elem) == deformerType:
                result.append(elem)
        return result


    @undo
    def findBlendShape(self, _tranformToCheck):
        """
        Find the blendShape from a string
        @param _tranformToCheck: Needs to be a String!!
        """
        result = []
        if not (pm.objExists(_tranformToCheck)):
            return result

        validList = mel.eval(
            'findRelatedDeformer("' + str(_tranformToCheck) + '")')

        if validList is None:
            return result

        for elem in validList:
            if pm.nodeType(elem) == 'blendShape':
                result.append(elem)
        return result

    @undo
    def connect_bls(self, source=[], target=[], origin="world"):
        """
        This function connects input|source to output|target with a blendShape.
        If the source and target are of type list, it will blendShape each of those lists together.
        Else it will take source and target and blendShape those together

        @source : List. Shape to add to the target
        @target : List. mesh getting the blendshape
        @origin : String. {local:world}
        """

        inputs = [x for x in source]
        outputs = [x for x in target]
        for _input, _output in zip(inputs, outputs):
            try:
                blendShapeNode = (('{}_BLS'.format(_input)).split(
                    '|')[-1]).split(':')[-1]  # remove namespace if one
            except:
                blendShapeNode = (
                    '{}_BLS'.format(_input)).split('|')[-1]

            if not mc.objExists(blendShapeNode):
                pm.blendShape(_input, _output, name=blendShapeNode, o=origin, w=[(0, 1.0)], foc=False)
            else:
                pm.warning('{} already Exist'.format(blendShapeNode))

        sys.stdout.write('// Result: Connection Done // \n ')


    def add_target(self, shape_to_add, mesh,  bls_node=None, value=1):
        """
        Add a shape as a mesh

        @shape_to_add : (List) Shape to add to the mesh
        @mesh :      (String) Mesh getting the blendshape
        """
        if not bls_node:
            bls_node = self.findBlendShape(mesh)[0]
        else:
            bls_node = bls_node

        if pm.objExists(bls_node):
            if pm.PyNode(bls_node).getTarget():
                all_targets = {i: pm.aliasAttr('{}.w[{}]'.format(bls_node, i), q=1) for i in
                    pm.getAttr('{}.w'.format(bls_node), multiIndices=1)}
            else:
                all_targets = []

        numb_target = len(all_targets) + 1
        if numb_target == 0:
            numb_target = 1

        for index, shape in enumerate(shape_to_add):
            pm.blendShape(bls_node, e=1, target=(mesh, index + numb_target, shape, 1))
            pm.setAttr('{}.weight[{}]'.format(bls_node, index + numb_target), value)

        sys.stdout.write('// Result: targets added // \n ')


    def blendshape(self, mesh, targets = [], parallel=False, topology=True, foc=False, origin="world"):
        """
        Blendshape function that creates a blendshape and added other shape as targets
        Works on selection.
        Select the source first (bls), then the target

         -- source : List. shapes to add to the target
         -- target : mesh getting the blendshape
         -- origin : string. {local:world}
        """
        try:
            blendShapeNode = (('{}_BLS'.format(mesh)).split(
                '|')[-1]).split(':')[1]  # remove namespace if one
        except:
            blendShapeNode = (
                '{}_BLS'.format(mesh)).split('|')[-1]

        bs = pm.blendShape(mesh, parallel=parallel, tc=topology, foc=foc, n=blendShapeNode)[0]

        if targets is not []:
            for index, shape in enumerate(targets):
                pm.blendShape(bs, e=1, target=(mesh, index + 1, shape, 1))
                pm.setAttr('{}.weight[{}]'.format(bs, index + 1), 1)


    def getObjectDeformerList(self, _transform):
        """
        Returns all the deformers from a transform
        """
        result = []
        if not (pm.objExists(_transform)):
            return result
        validList = mel.eval('findRelatedDeformer("' + str(_transform) + '")')
        allDeformer = pm.listHistory(_transform)
        for elem in allDeformer:
            if elem in validList:
                result.append(elem)
        if not len(result) == len(validList):
            for elem in validList:
                if elem not in result:
                    result.append(elem)
        return result


    def makeCloth(self, selection=pm.selected()):
        """
        creates cloth nodes on each for the selection
        Returns all the nCloth nodes
        """
        def makeCloth_node(msh):
            pm.select(msh)
            pm.mel.createNCloth(0)
            cloth = pm.rename('nCloth1', msh.split('cloth')[0] + 'ncloth__')
            pm.parent(cloth, pm.PyNode(msh).getParent())
            pm.select(None)
            return cloth
        all_cloth = []
        for each in selection:
            cloth = makeCloth_node(each)
            all_cloth.append(cloth)
        for sel, cloth in zip(selection, all_cloth):
            pm.reorder(sel, back=True)
            pm.reorder(cloth, back=True)
        return all_cloth


    def blend2grps(self, origin='world'):
        """
        Source function: connect_bls function(). Blendshape the children of two groups together
        Select Source first, then the target
        """
        # get all children in group
        inputs = pm.listRelatives(pm.selected()[0], children=True, path=True)
        outputs = pm.listRelatives(pm.selected()[1], children=True, path=True)
        self.connect_bls(inputs, outputs, origin=origin)


    def findBlendShapes(self, subject=pm.selected()):
        """
        Source function: findBlendShape()
        Find all blendshapes from selection
        @subjet : List
        """
        result = flatList([self.findBlendShape(x) for x in subject])
        return result


    def deleteBLS(self, subject=pm.selected(), suffix='BLS'):
        """
        Delete all blendShape node ending by the var suffix
        @param suffix: String. The value is 'BLS' by default
                       If you want to delete all blendShape, put ''

        """
        blendShp = flatList([self.findBlendShape(str(x)) for x in subject])
        blendShpBLS = [x for x in blendShp if x.endswith(suffix)]
        pm.delete(blendShpBLS)


    def findSkinCluster(self, _tranformToCheck):
        """
        Find a SkinCluster
        """
        result = []
        if not (pm.objExists(_tranformToCheck)):
            return result
        validList = mel.eval(
            'findRelatedDeformer("' + str(_tranformToCheck) + '")')
        if validList is None:
            return result
        for elem in validList:
            if pm.nodeType(elem) == 'skinCluster':
                result.append(elem)
        return result


    def quickMirrorWeights(self):
        test = [" -mirrorMode YZ -surfaceAssociation " + 'closestPoint' +
                "-influenceAssociation " + 'oneToOne' + " -influenceAssociation " + 'oneToOne']
        pm.mel.doMirrorSkinWeightsArgList(2, test)


    def resetSkin(self):
        """Reset the skinning after moving a controller """
        sourceMesh = pm.selected()[0]
        _skin_cluster = self.findSkinCluster(sourceMesh)

        bindJnt_source = [x for x in pm.listConnections(
            str(_skin_cluster[0]) + '.matrix[*]', s=1)]
        bindPose = pm.listConnections(
            bindJnt_source[0], d=True, t='dagPose')[0]
        sourceGeShape = pm.skinCluster(_skin_cluster, q=True, geometry=True)[0]

        pm.skinCluster(_skin_cluster, e=True, unbindKeepHistory=True)
        pm.skinCluster(bindJnt_source, sourceGeShape,
                       ignoreBindPose=True, toSelectedBones=True)
        pm.select(bindJnt_source, add=True)

    # ===============================
    # 6. FUNCTIONS UTILITAIRES
    # ===============================

    class FUNCTIONS_UTILITAIRES():
        def __init__():
            pass

    @undo
    def selectType(self, type_name):
        """ Select by type in pm.selected() """
        def _type_func(each):
            try:
                _type = (pm.objectType(pm.PyNode(each).getShape()))
            except:
                _type = (pm.objectType(pm.PyNode(each)))
            return _type

        types_list = [x for x in pm.selected() if _type_func(x) == type_name]
        pm.select(types_list, r=True)


    def selectInt(self, type=0, interval=2):
        """ Selection par Invertal"""
        if type == 0:
            new_selection = pm.selected()[::interval]
        elif type == 1:
            new_selection = pm.selected()[1::interval]
        pm.select(new_selection, r=True)


    def hiearchyBuilder(self, subject=pm.selected(), offset_type='ctrl'):
        """
        hiearchy builder to create two offset from a joint
        @param offset_type: string. {group:ctrl}
        """
        if offset_type == 'ctrl':
            for each in subject:
                @changeColor()
                @makeroot()
                def create_ctrl():
                    _ctrl = pm.circle(n=pm.PyNode(each).name(
                    ) + '__', c=(0, 0, 0), ch=1, d=3, ut=0, sw=360, s=8, r=1, tol=0.01, nr=(1, 0, 0))[0]
                    self.AutoSuffix([_ctrl])
                    pm.matchTransform(_ctrl, each, rot=True, pos=True)
                    try:
                        pm.parent(_ctrl, each.getParent())
                    except:
                        pass
                    pm.parent(each, _ctrl)
                    return _ctrl
                create_ctrl()

        elif offset_type == 'group':
            for each in subject:
                self.makeroot_func(each)
                self.makeroot_func(each, suff='orient')


    def distanceNode(self, distObjs_LIST_QDT=pm.selected()):
        """
        @param distObjs_LIST_QDT : List of 2 elements
        """
        distanceNode_shape = pm.distanceDimension(sp=(1, 1, 1), ep=(2, 2, 2))
        pm.rename(distanceNode_shape, '{}_to_{}_distDimShape'.format(
            distObjs_LIST_QDT[0], distObjs_LIST_QDT[1]))
        pm.rename(pm.PyNode(distanceNode_shape).getParent(), '{}_to_{}_distDim'.format(
            distObjs_LIST_QDT[0], distObjs_LIST_QDT[1]))
        distanceNode = (pm.PyNode(distanceNode_shape).getParent())
        end_point_loc = pm.listConnections(
            str(distanceNode_shape) + '.endPoint', source=True)[0]
        start_point_loc = pm.listConnections(
            str(distanceNode_shape) + '.startPoint', source=True)[0]
        pm.rename(start_point_loc, '{}_Dist_loc__'.format(
            distObjs_LIST_QDT[0]))
        pm.rename(end_point_loc, '{}_Dist_loc__'.format(distObjs_LIST_QDT[1]))
        pm.matchTransform(start_point_loc, distObjs_LIST_QDT[0])
        pm.matchTransform(end_point_loc, distObjs_LIST_QDT[1])
        pm.parentConstraint(distObjs_LIST_QDT[0], start_point_loc)
        pm.parentConstraint(distObjs_LIST_QDT[1], end_point_loc)

        if pm.objExists('dist_GRP'):
            pm.parent(distanceNode, 'dist_GRP')
        else:
            pm.group(n='dist_GRP', w=True, em=True)
            pm.parent(distanceNode, 'dist_GRP')
            pm.parent(start_point_loc, 'dist_GRP')
            pm.parent(end_point_loc, 'dist_GRP')
        return distanceNode


    def connect_sameAttr(self, driver, target, att_to_connect=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']):
        """
        Connect multiples attributes between two object
        """
        for att in att_to_connect:
            pm.PyNode('{}.{}'.format(driver, att)) >> pm.PyNode(
                '{}.{}'.format(target, att))


    def connect_axesAttr(self, driver, target, outputs=['translate', 'rotate'], inputs=[]):
        if inputs == []:
            inputs = outputs
        xyz = ['X', 'Y', 'Z']
        for i in range(len(outputs)):
            for j in range(3):
                axe = xyz[j]
                pm.PyNode('{}.{}{}'.format(driver, outputs[i], axe)) >> pm.PyNode(
                    '{}.{}{}'.format(target, inputs[i], axe))


    def jointAtCenter(self):
        selected = pm.selected()
        all_jnts = []
        # for locators in selection, run the following code
        for sel in selected:
            # create variable for the position of the locators
            pos = sel.getRotatePivot(space='world')
            # unparent the joints
            pm.select(cl=True)
            # create joints and position them on top of locators
            oJoints = pm.joint(p=pos, n='{}'.format(NC.getNameNoSuffix(sel)))
            all_jnts.append(oJoints)
        self.AutoSuffix(all_jnts)
        return all_jnts


    def jointAtCenter_(self):
        """
        Creates a joint in the centre of the selection. You can select objects, components...
        """
        # logger.info('.. Create a joint in the centre of the selection ..')
        sel = mc.ls(sl=1, fl=1)
        if len(sel) == 1:
            # Get the bounding box values of the object
            pos = mc.xform(q=1, ws=1, bb=1)
            mc.select(cl=True)
            return mc.joint(p=((pos[0] + pos[3]) / 2, (pos[1] + pos[4]) / 2, (pos[2] + pos[5]) / 2))
        elif len(sel) > 1:
            bb = [0, 0, 0, 0, 0, 0]
            for obj in sel:
                pos = mc.xform(obj, q=1, ws=1, bb=1)
                for i in range(6):
                    bb[i] += pos[i]
            for i in range(6):
                bb[i] /= len(sel)
            mc.select(cl=True)
            return mc.joint(p=((bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, (bb[2] + bb[5]) / 2))
        else:
            sys.stdout.write(
                '// Result : Nothing selected. Please select at least one object //')


    def createLoc(self, subject):
        """
        creates a locator matching position and rotation with the subject
        """
        loc_align = pm.spaceLocator()
        pm.matchTransform(loc_align, subject, rot=True, pos=True)
        return loc_align


    def find_and_replace_lattices(self):
        """
        search for lattices that are connected to meshes.
        """
        modelGroup = pm.ls(type='transform')
        firstFilter = [x for x in modelGroup if x.getShape()]
        geoWithInputs = [x.getShape() for x in firstFilter if type(
            x.getShape()) == pm.nodetypes.Mesh]
        # drill into the inputs of each mesh to find the FFD inputs
        # return it as a set, since it will return each multiple times for each geo it is connected to
        latticeInputs = list(set([eachInput for geo in geoWithInputs for eachInput in geo.inputs(
        ) if type(eachInput) == pm.nodetypes.Ffd]))
        lprint(latticeInputs)

        for eachLattice in latticeInputs:
            latticeParts = list(set([
                x for x in eachLattice.inputs()
                if 'Lattice' in x.name()
                and 'Base' not in x.name()
                and type(x) == pm.nodetypes.Transform
            ]))

            # find the geo in the lattice
            try:
                oLattice = latticeParts[0]
            except:
                pass

            geometry = oLattice.getGeometry()
            oShapes = [pm.PyNode(x) for x in geometry]
            oTransforms = [pm.PyNode(x).getParent() for x in geometry]

            # find the corresponding new geo
            newGeo = [pm.PyNode('pasted__' + x.name()) for x in oTransforms]
            newShapes = [pm.PyNode('pasted__' + x.name()) for x in oShapes]

            # add the new geo to the lattice deformer set
            oLattice.setGeometry(newShapes)

            # clean up
            for oldgeo, newgeo in zip(oTransforms, newGeo):
                pm.parent(newgeo, oldgeo.getParent())
                pm.delete(oldgeo)
                for each in pm.ls('pasted__*'):
                    each.rename(each.name().replace('pasted__', ''))


    @undo
    def find_and_replace_deformer(self, modelGroup=pm.ls(type='transform'), cleanUp=False):
        """
        Replace pasted Meshes for Non Linear Deformer.
        """
        firstFilter = [x for x in modelGroup if x.getShape()]
        geoWithInputs = [x.getShape() for x in firstFilter if type(
            x.getShape()) == pm.nodetypes.Mesh]

        _deformerList = [deformer_name for mesh in modelGroup for deformer_name in self.getObjectDeformerList(str(mesh))
                         if type(deformer_name) == pm.nodetypes.NonLinear
                         ]
        deformerList = list(set(_deformerList))
        # printdeformerList

        if cleanUp is False:
            for eachDef in deformerList:
                geometry = eachDef.getGeometry()[0]
                oTransforms = pm.PyNode(geometry).getParent()
                # ## find the corresponding new geo
                newGeo = pm.PyNode('pasted__' + pm.PyNode(oTransforms).name())
                newShapes = pm.PyNode('pasted__' + pm.PyNode(geometry).name())
                # ## add the new geo to the deformer set
                eachDef.setGeometry(newShapes)

        elif cleanUp is True:
            for eachDef in deformerList:
                geometry = eachDef.getGeometry()[0]
                oTransforms = pm.PyNode(geometry).getParent()
                # ## find the corresponding new geo
                newGeo = pm.PyNode('pasted__' + pm.PyNode(oTransforms).name())
                newShapes = pm.PyNode('pasted__' + pm.PyNode(geometry).name())
                # ## add the new geo to the deformer set
                eachDef.setGeometry(newShapes)

                # ## clean up
                pasted_grp = newGeo.getParent()
                pm.parent(newGeo, oTransforms.getParent())
                pm.delete(oTransforms)

            for each in pm.ls('pasted__*'):
                each.rename(each.name().replace('pasted__', ''))


    @undo
    def DkToRv(self, nodeType):
        """
        Transform driven Key Nodes to Remap Value.
        @param nodeType : String. The type of the node that needs to be changed. ex: animCurveUU
        """

        allNodes = pm.ls(type=nodeType)
        # pm.select(allNodes)

        pm.select(None)
        for each in allNodes:
            list = pm.listConnections(each + '.output') or []
            # print(list)
            if list == []:
                # pm.select(each, add = True)
                pm.delete(each)
        Nodes = pm.ls(type=nodeType)
        for eachKey in Nodes:
            # get the controllers
            oControl = eachKey.inputs()[0]
            oDriven = eachKey.outputs()[0]
            # get the control plugs (the actual attributes)
            paramControl = eachKey.inputs(plugs=True)[0]
            paramDriven = eachKey.outputs(plugs=True)[0]

            # create a remapValue with the name of the old curve
            remapName = eachKey.split('__grp__')[0] + '_remap__'
            oMap = pm.createNode('remapValue', n=remapName)

            # get the current value of the driven controller.
            "Set the inMin value on the last postion of the Set Driven Key, in this case is number 2"

            inMax = mc.getAttr(eachKey + ".keyTimeValue[0].keyTime")
            inMin = mc.getAttr(eachKey + ".keyTimeValue[1].keyTime")
            outMax = mc.getAttr(eachKey + ".keyTimeValue[0].keyValue")
            outMin = mc.getAttr(eachKey + ".keyTimeValue[1].keyValue")

            # set the remapValue parameters to the same values as the Driven Key.
            oMap.inputMin.set(inMin)
            oMap.inputMax.set(inMax)
            oMap.outputMin.set(outMin)
            oMap.outputMax.set(outMax)
            paramControl.connect(oMap.inputValue)
            oMap.outValue.connect(paramDriven, force=True)
        pm.delete(eachKey)


    @undo
    def PvGuide(self, ikHandle, elbowJoint, exposant=10):
        """
        Ce script permet de construire une courbe qui servira de guide pour le placement du pole Vector.
        Utilisation: Selectionnez dans l'ordre suivant: le ik, puis le joint de depart pour cette courbe.
        Vous pouvez snaper votre pole vecteur controleur sur cette courbe et ensuite effacer cette courbe.
        """
        try:
            # trouver le start point
            StartJoint = pm.listConnections(
                pm.PyNode(ikHandle).startJoint, s=1)
            starPoint = pm.xform(StartJoint, q=1, ws=1, t=1)

            # valeur du pv attr * 100
            endPoint = []
            Pv_x = ((pm.PyNode(ikHandle).poleVectorX.get()) * 5 * exposant)
            Pv_y = ((pm.PyNode(ikHandle).poleVectorY.get()) * 5 * exposant)
            Pv_z = ((pm.PyNode(ikHandle).poleVectorZ.get()) * 5 * exposant)

            endPoint.append(Pv_x)
            endPoint.append(Pv_y)
            endPoint.append(Pv_z)

            # Creation de la curve
            curve = pm.curve(p=([(starPoint[0], starPoint[1], starPoint[2]), ((starPoint[0] + endPoint[0]),
                                                                              (starPoint[1] + endPoint[1]), (starPoint[2] + endPoint[2]))]), k=[0, 1], d=1, n="{}_pv_curve".format(ikHandle))

            # Changer la couleur en jaune
            pm.PyNode(curve).overrideEnabled.set(1)
            pm.PyNode(curve).overrideRGBColors.set(0)
            pm.PyNode(curve).overrideColor.set(17)

            # Changer le pivot
            pm.move(starPoint[0], starPoint[1], starPoint[2], (pm.PyNode(
                curve).scalePivot), (pm.PyNode(curve).rotatePivot))

            # Contraindre la curve au elbowJoint
            ptCons = pm.pointConstraint(elbowJoint, curve, mo=False)
            pm.delete(ptCons)
            pm.mel.FreezeTransformations()
            return curve
        except IndexError:
            pm.warning('Nothing to Delete')


    @undo
    def LocOnVertex(self, ):
        verts = pm.selected(flatten=True)
        allNodes = list(set([x.node() for x in verts]))

        # SNIPPET: Create an aligned locator. Select one vertex and run.
        for eachNode in allNodes:
            # split the verts up by their parent mesh
            selectedVerts = [vert for vert in verts if vert.node() == eachNode]
            selectedVert = selectedVerts[0]
            geoNode = selectedVert.node().getParent()
            ctrlName = geoNode.name()
            connectedVerts = list(selectedVert.connectedVertices())

            xComp = [vert.getPosition(
                space='world').x for vert in connectedVerts]
            yComp = [vert.getPosition(
                space='world').y for vert in connectedVerts]
            zComp = [vert.getPosition(
                space='world').z for vert in connectedVerts]

            xSpread = max(xComp) - min(xComp)
            ySpread = max(yComp) - min(yComp)
            zSpread = max(zComp) - min(zComp)
            spreads = [xSpread, ySpread, zSpread]
            planarAxis = ['x','y','z']

            shortestSide = spreads.index(min(spreads))
            planarAxis.pop(shortestSide)
            if 'x' not in planarAxis:
                # y-up, z-aim
                upVert = connectedVerts[zComp.index(max(zComp))]
                aimVert = connectedVerts[yComp.index(max(yComp))]
                upDir = [0, 1, 0]
                aimDir = [0, 0, 1]
            if 'y' not in planarAxis:
                # z-up, x-aim
                upVert = connectedVerts[zComp.index(max(zComp))]
                aimVert = connectedVerts[xComp.index(max(xComp))]
                upDir = [0, 0, 1]
                aimDir = [1, 0, 0]
            if 'z' not in planarAxis:
                # y-up, x-aim
                upVert = connectedVerts[yComp.index(max(yComp))]
                aimVert = connectedVerts[xComp.index(max(xComp))]
                upDir = [0, 1, 0]
                aimDir = [1, 0, 0]

            ctrlLoc = pm.spaceLocator(n='{}_'.format(ctrlName))
            pm.PyNode(ctrlLoc).overrideEnabled.set(1)
            pm.PyNode(ctrlLoc).overrideRGBColors.set(0)
            pm.PyNode(ctrlLoc).overrideColor.set(22)

            upLoc = pm.spaceLocator(n='{}_upLOC'.format(ctrlName))
            aimLoc = pm.spaceLocator(
                n='{}_TEMP_AIM'.format(ctrlName))

            finalPos = sum([vert.getPosition(space='world')
                            for vert in selectedVerts]) / float(len(selectedVerts))
            ctrlPos = selectedVert.getPosition(space='world')
            upPos = upVert.getPosition(space='world')
            aimPos = aimVert.getPosition(space='world')

            ctrlLoc.setTranslation(ctrlPos, space='world')
            upLoc.setTranslation(upPos, space='world')
            aimLoc.setTranslation(aimPos, space='world')

            oCons = pm.aimConstraint(aimLoc, ctrlLoc, mo=False, aim=aimDir, u=upDir,
                                     n='{}_TEMP__aimconstraint__'.format(
                                         ctrlName),
                                     worldUpObject=upLoc,
                                     worldUpType='object',
                                     )
            pm.delete(oCons, upLoc, aimLoc)
            # the aim constraint is aligned to one selected vert.
            # The control is then moved to the average pos of all selected verts.
            ctrlLoc.setTranslation(finalPos, space='world')

            pm.select(None)
            self.AutoSuffix([ctrlLoc])
            pm.select(ctrlLoc, add=True)
            return ctrlLoc


    @undo
    def removeCons(self, subject=pm.selected(), constraint_type=['parentConstraint', 'scaleConstraint', 'orientConstraint', 'pointConstraint', 'aimConstraint']):
        for each in subject:
            for cons in constraint_type:
                all_Constraints = (
                    set([x for x in each.inputs() if pm.nodeType(x) == cons]))
                pm.delete(all_Constraints)


    def copyUVsFrom2Groups(self):
        sources_list = pm.listRelatives(
            pm.selected()[0], children=True, path=True)
        targets_list = pm.listRelatives(
            pm.selected()[1], children=True, path=True)

        for source, target in zip(sources_list, targets_list):
            pm.polyTransfer(target, vc=0, uv=1, ao=source, v=0)


    def matrixConstraint(self,
                         parent_transform,
                         child,
                         channels='trsh',
                         mo=True
                         ):
        """
        Use the matrixConstraint for faster rigs.
        If you set the channels to 'trsh' it will act just as a parentConstraint.
        If you set the channels to 't' it will act just as a pointConstraint.
        If you set the channels to 's' it will act just as a scaleConstraint.
        If you set the channels to 'r' it will act just as a orientConstraint.

        t:translate, s:scale, r:rotate, s:shear

        there is no blending or multiple targets concept and the driven object MUST have the
        rotate order set to the default xyz or it will not work.

        :param Transform driven: the driven object

        @param channels: (str)  specify if the result should be connected to
                                translate, rotate or/and scale by passing a string with
                                the channels to connect.
                                Example: 'trsh' will connect them all, 'tr' will skip scale and shear

        @param mo:  (bool)  Maintain offset, like in the constrains a difference matrix will be
                            held for retaining the driven original position.
                            1 will multiply the offset before the transformations, 2 after.
                            by multiplying it after, the effect will be suitable for a
                            pointConstraint like behavior.

        Return the decompose Matrix Node
        """
        def getDagPath(node=None):
            sel = om.MSelectionList()
            sel.add(node)
            d = om.MDagPath()
            sel.getDagPath(0, d)
            return d

        def getLocalOffset():
            parentWorldMatrix = getDagPath(str(parent_transform)).inclusiveMatrix()
            childWorldMatrix = getDagPath(str(child)).inclusiveMatrix()
            return childWorldMatrix * parentWorldMatrix.inverse()

        mult_matrix = pm.createNode(
            'multMatrix', n='{}_multM'.format(parent_transform))
        dec_matrix = pm.createNode(
            'decomposeMatrix', n='{}_dectM'.format(parent_transform))

        if mo is True:
            localOffset = getLocalOffset()

            # matrix Mult Node CONNECTIONS
            pm.setAttr("{}.matrixIn[0]".format(mult_matrix), [localOffset(
                i, j) for i in range(4) for j in range(4)], type="matrix")
            pm.PyNode(parent_transform).worldMatrix >> mult_matrix.matrixIn[1]
            mult_matrix.matrixSum >> dec_matrix.inputMatrix
            pm.PyNode(child).parentInverseMatrix >> mult_matrix.matrixIn[2]

        else:
            pm.PyNode(parent_transform).worldMatrix >> mult_matrix.matrixIn[0]
            mult_matrix.matrixSum >> dec_matrix.inputMatrix
            pm.PyNode(child).parentInverseMatrix >> mult_matrix.matrixIn[1]

        # CHANNELS CONNECTIONS
        axes = 'XYZ'
        for channel in channels:
            if channel == 't':
                for axe in axes:
                    pm.PyNode('{}.outputTranslate{}'.format(dec_matrix, axe)) >> pm.PyNode(
                        '{}.translate{}'.format(child, axe))
            if channel == 'r':
                for axe in axes:
                    pm.PyNode('{}.outputRotate{}'.format(dec_matrix, axe)) >> pm.PyNode(
                        '{}.rotate{}'.format(child, axe))
                pm.PyNode(child).rotateOrder >> pm.PyNode(
                    dec_matrix).inputRotateOrder
                try:
                    pm.PyNode(child).jointOrientX.set(0)
                    pm.PyNode(child).jointOrientY.set(0)
                    pm.PyNode(child).jointOrientZ.set(0)
                except AttributeError:
                    pass

            if channel == 's':
                for axe in axes:
                    pm.PyNode('{}.outputScale{}'.format(dec_matrix, axe)) >> pm.PyNode(
                        '{}.scale{}'.format(child, axe))
            if channel == 'h':
                dec_matrix.outputShearX >> pm.PyNode(child).shearXY
                dec_matrix.outputShearY >> pm.PyNode(child).shearXZ
                dec_matrix.outputShearZ >> pm.PyNode(child).shearYZ

        return dec_matrix

    # ===============================
    # 7. SHAPES - CURVES MANAGEMENT
    # ===============================

    class SHAPES_CURVES_MANAGEMENT():
        def __init__():
            pass


    @changeColor(col=(1, 0.944, 0.156))
    def createCurveFrom(self, selection=pm.selected(), curve_name='curve'):
        """
        Creates a curve from the position values of the selection
        """
        def createLocs(subject):
            loc_align = pm.spaceLocator()
            pm.matchTransform(loc_align, subject, rot=True, pos=True)
            return loc_align
        starting_locs = [createLocs(x) for x in selection]
        pos = [pm.xform(x, ws=True, q=True, t=True) for x in starting_locs]
        knot = []
        for i in range(len(selection)):
            knot.append(i)
        _curve = pm.curve(p=pos, k=knot, d=1, n=curve_name)
        pm.rebuildCurve(_curve, rt=0, ch=0, end=1, d=3, kr=0, s=len(
            selection), kcp=0, tol=0.1, kt=0, rpo=1, kep=1)
        pm.delete(starting_locs)
        return(_curve)


    @staticmethod
    def changeColor_func(subject, type='rgb', col=(0.8, 0.5, 0.2)):
            pm.select(subject)
            ctrls = pm.selected()
            shapes = [x.getShapes() for x in ctrls] or []
            all_shapes = [x for i in shapes for x in i] or []

            if all_shapes == []:
                for ctrl in ctrls:
                    pm.PyNode(ctrl).overrideEnabled.set(1)

                    if type == 'rgb':
                        pm.PyNode(ctrl).overrideRGBColors.set(1)
                        pm.PyNode(ctrl).overrideColorRGB.set(col)

                    if type == 'index':
                        pm.PyNode(ctrl).overrideRGBColors.set(0)
                        pm.PyNode(ctrl).overrideColor.set(col)
            else:
                for ctrl in all_shapes:
                    pm.PyNode(ctrl).overrideEnabled.set(1)
                    if type == 'rgb':
                        pm.PyNode(ctrl).overrideRGBColors.set(1)
                        pm.PyNode(ctrl).overrideColorRGB.set(col)

                    if type == 'index':
                        pm.PyNode(ctrl).overrideRGBColors.set(0)
                        pm.PyNode(ctrl).overrideColor.set(col)
            return subject


    def getShapeOrig(self, _transformName=''):
        """
        Get Original node
        """
        result = ''
        if not pm.objExists(_transformName):
            return result

        result = pm.PyNode(_transformName).getShapes()[-1]
        if 'Orig' in str(result):
            return result
        else:
            # print("No 'Orig' Node for: {}".format(_transformName))
            return None


    def freezeCvs(self, selection=pm.selected()):
        """ Freeze all the cvs of a curve """
        mc.DeleteHistory(selection)
        cluster = pm.cluster(selection)
        pm.delete(cluster)
        return selection


    def resetCvs(self, subject=pm.selected()):
        curve_name = subject[0].name()
        pm.rename(subject, 'temp')
        shape = subject[0].getShape()
        cvs_num = len(pm.PyNode(subject[0]).getCVs())

        for number in range(0, cvs_num):
            for axis in 'xyz':
                pm.setAttr('{}.controlPoints[{}].{}Value'.format(
                    shape, number, axis), 0)
        pm.rename(subject, curve_name)


    def selectNurbsVertx(self, subject=pm.selected()):
        """ Select All cvs of selected nurbs curve """
        for each in subject:
            _shapes = pm.PyNode(each).getShapes()
            pm.select('{}.cv[:]'.format(_shapes[0]), add=True)
            for x in range(1, (len(_shapes))):
                pm.select('{}.cv[:]'.format(_shapes[x]), add=True)


    def _rotateVertex(self, axis, subject=pm.selected()):
        if len(subject) == 1:
            _shapes = pm.PyNode(subject[0]).getShapes()
            pm.select('{}.cv[:]'.format(_shapes[0]), r=True)
            for x in range(1, (len(_shapes))):
                pm.select('{}.cv[:]'.format(_shapes[x]), add=True)

        elif type(subject) == "<type 'str'>":
            _shapes = pm.PyNode(subject[0]).getShapes()
            pm.select('{}.cv[:]'.format(_shapes[0]), r=True)
            for x in range(1, (len(_shapes))):
                pm.select('{}.cv[:]'.format(_shapes[x]), add=True)
        if axis == 'x' or 'X':
            pm.rotate(90, 0, 0, r=1, os=1, fo=1)
        elif axis == 'y' or 'Y':
            pm.rotate(0, 90, 0, r=1, os=1, fo=1)
        elif axis == 'z' or 'Z':
            pm.rotate(0, 0, 90, r=1, os=1, fo=1)
        pm.select(subject, r=True)


    def rotateVertex(self, axis, subject=pm.selected()):
        """
        Calls _rotateVertex function
        """
        sel = subject
        for each in sel:
            self._rotateVertex(axis, [each])
        pm.select(sel, r=True)


    def _scaleVertex(self, scale, subject=pm.selected(), valuePos=1.2, valueNeg=0.8):
        if len(subject) == 1:
            _shapes = pm.PyNode(subject[0]).getShapes()
            pm.select('{}.cv[:]'.format(_shapes[0]), r=True)
            for x in range(1, (len(_shapes))):
                pm.select('{}.cv[:]'.format(_shapes[x]), add=True)

        elif type(subject) == "<type 'str'>":
            _shapes = pm.PyNode(subject[0]).getShapes()
            pm.select('{}.cv[:]'.format(_shapes[0]), r=True)
            for x in range(1, (len(_shapes))):
                pm.select('{}.cv[:]'.format(_shapes[x]), add=True)
        if scale == '+':
            pm.scale(valuePos, valuePos, valuePos, r=True)
        elif scale == '-':
            pm.scale(valueNeg, valueNeg, valueNeg, r=True)
        pm.select(subject, r=True)


    def scaleVertex(self, scale, subject=pm.selected()):
        """
        @param scale : '+' / '-'
        """
        sel = subject
        for each in sel:
            self._scaleVertex(scale, [each])
        pm.select(sel, r=True)


    @makeroot()
    def clusterCvs(self, curve=pm.selected()):
        pm.select(curve, r=True)
        sel = pm.select(".cv[*]")
        cvs = pm.filterExpand(fullPath=True, sm=28)
        nbCvs = len(cvs)
        oCollClusters = [pm.cluster(cvs[x])[-1] for x in range(0, nbCvs)]
        return(oCollClusters)


    @changeColor()
    @makeroot()
    def fk_shape_setup(self,
                       type="build",
                       radius=2,
                       Normalsctrl=(1, 0, 0),
                       listJoint=pm.selected(),
                       ):
        """
        Fk chain setUp by parenting the shape to the joint
        """

        if type == "build":
            subject = [pm.PyNode(x) for x in listJoint]

            def CreateCircles():
                CurveColl = []
                for joint in subject:
                    myname = '{}'.format(joint)
                    new_name = myname.split('__jnt__')[0] + '_fk__ctrl__'
                    curve = pm.circle(nr=Normalsctrl, r=radius)

                    curveShape = pm.PyNode(curve[0]).getShape()
                    CurveColl.extend(curve)
                    tras = pm.xform(joint, ws=True, q=True, t=True)
                    pivot = pm.xform(joint, ws=True, q=True, rp=True)

                    pm.xform(curve, ws=True, t=tras, rp=pivot)
                    pm.parent(curveShape, joint, r=True, s=True)
                    pm.delete(curve)
                    pm.rename(joint, new_name)

                return(subject)
            controls = CreateCircles()
            return(controls)

        elif type == "delete":
            ctrls = [x for x in listJoint if x.type() == 'joint']
            groups = [x.getParent() for x in ctrls]
            shapes = [x.getShape() for x in ctrls]
            pm.parent(ctrls, w=True)
            pm.delete(groups, shapes)
            self.ChainParent(ctrls)
            for joint in ctrls:
                pm.PyNode(joint).rename(str(joint).replace('_fk__ctrl__', ''))


    @undo
    def ReplaceShape(self):
        """
        Replacing shape function
        -- Select the Source (shape to copy)
        -- Followed by Target shape
        """
        new_shape = pm.selected()[0]
        old_shape = pm.selected()[1]

        # Duplicate source and move to target location
        new_shape_dup = pm.duplicate(new_shape, rc=True)
        pm.matchTransform(new_shape_dup[0], old_shape, pos=True, rot=True)

        # Parent source to target's parent
        pm.parent(new_shape_dup, old_shape.getTransform())
        pm.makeIdentity(new_shape_dup, apply=True, t=1, r=1, s=1)

        # Get transforms and shapes of source and target
        new_shape_getShape = pm.PyNode(new_shape_dup[0]).getShapes()
        old_shape_getShape = pm.PyNode(old_shape).getShapes()

        # Parent shapes of source to target
        for srcShapes in new_shape_getShape:
            pm.parent(srcShapes, old_shape, add=True, s=True)

        # ## Clean up
        pm.delete(new_shape_dup)
        pm.delete(old_shape_getShape)
        pm.delete(new_shape)


    @undo
    def CombineShape(self, oNurbs=pm.selected()):
        """
        Create a control with multiple shapes
        """
        oDriver = oNurbs[0]
        oDriven = oNurbs[1:]

        shapes = [x.getShapes() for x in oDriven]
        transforms = [x.getTransform() for x in oDriven]

        pm.select(None)
        pm.select(shapes)
        pm.select(oDriver, add=True)

        pm.parent(r=True, s=True)
        pm.delete(transforms)
        return oDriver


    @undo
    def GetCurveShape(self):
        """
        Creates a dictionnary containing all information of a curve
        """
        crvShape = pm.selected()
        numb_point = len(pm.PyNode(crvShape[0]).getCVs())
        points = pm.PyNode(crvShape[0]).getCVs()
        format_points = []

        for i in range(numb_point):
            list = points[i]
            formatting = ['{:.4f}'.format(x) for x in list]
            format_points.append(formatting)

        crvShapeDict = {
            "fpoints": format_points,
            "knots": pm.PyNode(crvShape[0]).getKnots(),
            "degree": pm.PyNode(crvShape[0]).degree(),
            "form": pm.PyNode(crvShape[0]).form(),
        }

        print('\nCurve Info:')
        print('    points : ' + str(crvShapeDict["fpoints"]).replace("'", "") + '\n')
        print('    knots : ' + str(crvShapeDict["knots"]) + '\n')
        print('    degree : ' + str(crvShapeDict["degree"]))
        # mc.curve(p=crvShapeDict["points"], k=crvShapeDict["knots"], d=crvShapeDict["degree"])


    @undo
    @changeColor()
    def makeCtrl(self, shape_name):
        """ Controller builder

        If something is selected :
            - Creates a controller according to the shape. Match the rotation, position, and name of the selection

        if nothing selected
            -Creates a controller in the center at 0,0,0

        """

        if pm.selected():
            _ctrl = sl.makeCtrls(shape_name)
            return _ctrl
        else:
            _ctrl = shape_name()
            return [_ctrl]


    def makeCtrl_Prop(self, sl_shape_name):
        """ Controller builder

        If something is selected :
            - Creates a controller according to the shape. Match the rotation, position, name, and scale of the selection
        """
        Ctrls = []
        oColl = pm.selected()

        @propScale
        def _makeCtrl(sl_shape_name):
            func = sl_shape_name()
            Ctrls.append(func)
            return func

        _makeCtrl(sl_shape_name)

        for oSel, oCtrls in zip(oColl, Ctrls):
            pm.rename(oCtrls, '{}__{}'.format(oSel, NC.CTRL))

        for oCtrl in Ctrls:
            mc.FreezeTransformations(oCtrl)

        return Ctrls

    # ===============================
    # 8. DISPLAY OPTIONS
    # ===============================

    class DISPLAY_OPTIONS():
        def __init__():
            pass


    def hideAllJoint(self):
        """
        Hide all bones in a scene.
        Set there drawStyle to None
        """
        def hide_and_show_all_bones(oColl, pDrawStyle):
            for each in oColl:
                try:
                    each.drawStyle.set(pDrawStyle)
                except:
                    continue

        oColl = pm.ls('*', type='joint')
        hide_and_show_all_bones(oColl, 2)


    def switchDrawStyle(self, oJoints=pm.selected()):
        """
        Switch between drawStyle modes
        """
        CurrentIndex = list(set([x.drawStyle.get() for x in oJoints]))
        if CurrentIndex != 0:
            for joint in oJoints:
                pm.PyNode(joint).drawStyle.set(0)
        for pos in range(0, 3):
            if CurrentIndex[-1] == pos:
                nextIndex = int(CurrentIndex[-1] + 2)
        if nextIndex >= 3:
            nextIndex = 0
        for each in oJoints:
            pm.PyNode(each).drawStyle.set(nextIndex)


    # ===============================
    # 9. ATTRIBUTE EDITOR
    # ===============================

    class ATTRIBUTE_EDITOR():
        def __init__():
            pass


    @staticmethod
    @undo
    def breakConnection(_transform, attributes=['v']):
        """
        Break Connection
        @param attributes : list of different attribute:  ['tx','ty','tz','rx','ry','rz','sx','sy','sz', 'v']

        The default value is : ['v']
        """

        for att in attributes:
            attr = _transform + '.' + att

            destinationAttrs = pm.listConnections(
                attr, plugs=True, source=False) or []
            sourceAttrs = pm.listConnections(
                attr, plugs=True, destination=False) or []

            for destAttr in destinationAttrs:
                pm.disconnectAttr(attr, destAttr)
            for srcAttr in sourceAttrs:
                pm.disconnectAttr(srcAttr, attr)

                ## mel.eval("source channelBoxCommand; CBdeleteConnection \"{}\"".format(attr))


    @staticmethod
    @undo
    def lockAttr_func(subject, attributes=['tx', 'ty', 'tz', 'rx', 'ry', 'rx', 'rz', 'sx', 'sy', 'sz']):
        """ Lock all the attribute except visibility  """
        for att in attributes:
            pm.PyNode(subject).setAttr(att, lock=True, channelBox=False, keyable=False)
        return subject

    @staticmethod
    @undo
    def unlockAttr_func(subject, attributes=['tx', 'ty', 'tz', 'rx', 'ry', 'rx', 'rz', 'sx', 'sy', 'sz']):
        """ unlock all the attribute except visibility  """
        
        for att in attributes:
            pm.PyNode(subject).setAttr(att, lock=False, channelBox=True, keyable=True)
        return subject

    @undo
    def attrExist(self, obj_name, attribute_name=None):
        """ Determine if an attribute exist"""
        full_name = pm.PyNode(obj_name).name()
        if attribute_name:
            full_name = '{}.{}'.format(full_name, attribute_name)

        if pm.objExists(full_name):
            return True
        else:
            return False


    def AttDefault(self, defaultValue):
        """
        Change default value of an attribute
        """
        try:
            sel = pm.selected()
            for each in sel:
                attr = each.name() + '.' + (pm.channelBox("mainChannelBox",
                                                          q=1, selectedMainAttributes=1)[0])
                pm.addAttr(str(attr), e=True, dv=defaultValue)

        except TypeError:
            pm.warning('Select the attribute')


    def deleteAttr(self, attribute):
        """
        Delete Attribute from selection
        """
        for each in pm.selected():
            pm.deleteAttr(each, attribute=attribute)


    def unhideAll(self, transform):
        """
        Unhide and Unlock all channelBox attributes
        """
        for sub in transform:
            att_to_lock = ['tx', 'ty', 'tz', 'rx',
                        'ry', 'rz', 'sx', 'sy', 'sz', 'v']
            for att in att_to_lock:
                pm.PyNode(sub).setAttr(att, lock=False, keyable=True)

    @staticmethod
    @undo
    def addRotationOrderAttr(_transform):
        pm.addAttr(_transform, ln="rotationOrder",
                    en="xyz:yzx:zxy:xzy:yxz:zyx:", at="enum")
        pm.setAttr((str(_transform) + ".rotationOrder"),
                    e=1, keyable=True)
        pm.connectAttr((str(_transform) + ".rotationOrder"),
                        (str(_transform) + ".rotateOrder"))

    # ===============================
    # 10. NAMING
    # ===============================

    class NAMING():
        def __init__():
            pass

    @undo
    def rename(self, name, number=1, subject=pm.selected()):
        """
        Simple rename function with index
        """
        [pm.rename(x, '{}{}'.format(name, index + number)) for index, x in enumerate(subject)]

    @undo
    def AutoSuffix(self, subject=pm.selected()):
        """
        Add the correct suffix according to the type
        """
        new_subject = []
        for name in subject:
            try:
                _type = pm.objectType(pm.PyNode(name).getShape())
            except RuntimeError:
                _type = pm.objectType(pm.PyNode(name))
            Addtype = suffixDic.get(_type, 'Unknown')
            if Addtype == 'Unknown':
                suffixDic.update({_type: '__Unknown__'})
                print('Add type to dictionnary: ' + _type)

            # verify if suffix already exist
            if pm.PyNode(str(name)).endswith(suffixDic[_type]):
                pass
            else:
                try:
                    def getIndex():
                        rep = pm.PyNode(name).split('__')
                        for i, each in enumerate(rep):
                            for val in suffixDic.values():
                                if each == str(val).replace('__', ''):
                                    return i
                                else:
                                    pass
                    new_index = getIndex()
                    new_name = (str(name)).replace((str(name).split('__')[new_index]), suffixDic[_type]).replace(
                        '____', '__').replace('___', '__').replace('hi_msh__', '').replace('proxy_msh__', '')
                    
                    pm.PyNode(name).rename(new_name)
                    new_subject.append(new_name)
                except:
                    new_name = (str(name) + suffixDic[_type]).replace('____', '__').replace(
                        '___', '__').replace('hi_msh__', '').replace('proxy_msh__', '')
                    
                    pm.PyNode(name).rename(new_name)
                    new_subject.append(new_name)
        
        return new_subject


    def renameOutputs(self, _type='', suffix=''):
        """
        Rename an output from a selection based on the type.
        The ouput will have the same name of the selection + a suffix if needed
        Returns the output.

        @param _type: String ex: nurbsCurve
                                 mesh
                                 joint
                                 transform
                                 nurbsSurface
                                 locator
                                 clusterHandle
                                 nRigid
                                 nCloth
                                 ...
        @param suffix: String
        """
        selection = pm.selected()
        out = flatList([pm.PyNode(x) for x in selection])
        out_shape = flatList([pm.PyNode(x).getShapes() for x in selection])
        all_outs = out + out_shape
        _output = list(
            set(flatList([x.outputs(type=_type) for x in all_outs])))

        for output, sel in zip(_output, selection):
            pm.rename(output, '{}{}'.format(sel, suffix))
        return _output


    def copyName(self, original_name=[]):
        """
        Copy the names to all selected
        """
        targets = pm.selected()
        for ori, targ in zip(original_name, targets):
            pm.rename(targ, ori)


    def editName(self,
                 symbol='__',
                 index_to_split=1,
                 suffix='',
                 ):
        """
        l__cardigan_sweater_sleeve__hi_msh__  devient: l__cardigan_sweater_sleeve__01

        @param symbol: string. symbol to split
        @param index_to_split: float
        @param suffix: string.
        """
        for each in pm.selected():
            x = each.split(symbol)[:index_to_split + 1]
            new_name = (symbol).join(x) + symbol + suffix
            print(new_name)
            each.rename(new_name)


    def replaceIndex(self,
                     symbol='__',
                     index_to_split=1,
                     replacement='',
                     ):
        """
        Remplace juste un mot ou une partie

        @param symbol: string. symbol to split
        @param index_to_split: float
        @param replacement: string.
        """

        for each in pm.selected():
            new_name = each.replace(each.split(
                symbol)[index_to_split], replacement)
            print(new_name)
            each.rename(new_name)


    def removeNamespaces(self):
        """
        Removed the namespace before the ':'
        """
        for each in pm.selected():
            new_name = each.split(':')[-1]
            pm.PyNode(each).rename(new_name)
