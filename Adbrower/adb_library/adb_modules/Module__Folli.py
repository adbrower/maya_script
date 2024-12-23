# ------------------------------------------------------
# Class Follicule Module
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
#     Based on Chris Lesage's script
# ------------------------------------------------------


import sys

import adb_core.ModuleBase as moduleBase
import adb_core.Class__AddAttr as adbAttr
from adb_core.Class__Transforms import Transform

import adb_core.Class__Control as Control
reload(Control)

import adbrower
import maya.cmds as mc
import maya.mel as mel
import adb_core.NameConv_utils as NC
import pymel.core as pm
import ShapesLibrary as sl

from adbrower import changeColor, flatList, lprint, undo
adb = adbrower.Adbrower()

# =========================
# CLASS
# =========================

class FolliModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(FolliModel, self).__init__()
        self.getFollicules = []
        self.getFolliGrp = []


class Folli(moduleBase.ModuleBase):
    """
    Create Follicules on a surface

    @param countU: int
    @param countV: int
    @param vDir: String. Default Value is 'U'
    @param radius : float or int. Default value is 1
    @param sub : Surface on which we build the follicules system.

    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_library.adb_modules.Module__Folli as adbFolli
    reload (adbFolli)

    # example:

    arm = Folli('ArmFolli', 1, 5, radius = 0.5, subject = 'nurbsPlane1')
    arm.start()
    arm.build()

    arm.addControls()

    """
    def __init__(self,
                module_name,
                countU,
                countV,
                vDir = 'U',
                radius = 0.2,
                subject=pm.selected()):
        super(Folli, self).__init__()

        self._MODEL = FolliModel()

        self.NAME = module_name
        self.subject = pm.PyNode(subject)
        self.countU = countU
        self.countV = countV
        self.vDir = vDir
        self.radius = radius

    def __repr__(self):
        return str('{} : {} \n {}'.format(self.__class__.__name__, self.subject, self.__class__))

    # =========================
    # PROPERTY
    # =========================

    @property
    def getFolliGrp(self):
        return self._MODEL.getFolliGrp

    @property
    def getFollicules(self):
        """ Returns the follicules """
        return self._MODEL.getFollicules

    @getFollicules.setter
    def getFollicules(self, value):
        """ set the follicules visibility"""
        for oFoll in self._MODEL.getFollicules:
            pm.PyNode(oFoll).v.set(value)

    # =========================
    # METHOD
    # =========================

    def start(self, metaDataNode = 'network'):
        super(Folli, self)._start(self.NAME, _metaDataNode = metaDataNode)

        # add attribute on METADATA node

    def build(self):
        super(Folli, self)._build()

        if self.subject.getShape().type() == 'nurbsSurface':
            plugs = pm.listConnections(str(self.subject.getShape()) + '.local', d=True, sh=True)
        else:
            plugs = pm.listConnections(str(self.subject.getShape()) + '.outMesh', d=True, sh=True)
        current_numb_foll = len([x for x in plugs if x.type() == 'follicle']) or []

        if current_numb_foll == []:
            self.many_follicles(self.subject, self.countU, self.countV, self.vDir)
        else:
            self.add_folli(self.countV)

        # CBB: Put the group under the INPUT_GRP ???
        self.setFinalHiearchy(
                    RIG_GRP_LIST=[self.getFolliGrp],
                    INPUT_GRP_LIST=[],
                    OUTPUT_GRP_LIST=[self._MODEL.getJoints])

        for joint, joint_grp in zip(self._MODEL.getJoints, self._MODEL.getResetJoints):
            Transform(joint_grp).matrixConstraint(joint, mo=True)

        self.RIG_GRP.inheritsTransform.set(0)


    # =========================
    # SOLVERS
    # =========================

    def create_follicle(self, oNurbs, count, uPos=0.0, vPos=0.0):
        # manually place and connect a follicle onto a nurbs surface.
        if oNurbs.type() == 'transform':
            oNurbs = oNurbs.getShape()
        elif oNurbs.type() == 'nurbsSurface' or 'mesh':
            pass
        else:
            'Warning: Input must be a nurbs surface.'
            return False

        pName = '{}_{}__foll__'.format(oNurbs.name(), count)

        oFoll = pm.createNode('follicle', name='{}'.format(pName))
        oFoll.v.set(1)  # hide the little red shape of the follicle
        if oNurbs.type() == 'nurbsSurface':
            oNurbs.local.connect(oFoll.inputSurface)
        if oNurbs.type() == 'mesh':
            # if using a polygon mesh, use this line instead.
            # (The polygons will need to have UVs in order to work.)
            oNurbs.outMesh.connect(oFoll.inputMesh)

        for param in pm.listAttr(oFoll, keyable=True):
            if param in ['parameterU', 'parameterV']:
                pass
            else:
                pm.PyNode(oFoll + '.' + param).setKeyable(False)

        oNurbs.worldMatrix[0].connect(oFoll.inputWorldMatrix)
        oFoll.outRotate.connect(oFoll.getParent().rotate)
        oFoll.outTranslate.connect(oFoll.getParent().translate)
        uParam = self.add_keyable_attribute(oFoll.getParent(), 'double', 'u_param', oMin=-100, oMax=100, oDefault=0)
        vParam = self.add_keyable_attribute(oFoll.getParent(), 'double', 'v_param', oMin=-100, oMax=100, oDefault=0)
        self.connect_multiply(oFoll.parameterU, oFoll.getParent().u_param, 0.01)
        self.connect_multiply(oFoll.parameterV, oFoll.getParent().v_param, 0.01)
        uParam.set(uPos)
        vParam.set(vPos)
        oFoll.getParent().t.lock()
        oFoll.getParent().r.lock()
        return oFoll

    @staticmethod
    def add_keyable_attribute(myObj, oDataType, oParamName, oMin=None, oMax=None, oDefault=0.0):
        """adds an attribute that shows up in the channel box; returns the newly created attribute"""
        oFullName = '.'.join([str(myObj), oParamName])
        if pm.objExists(oFullName):
            return pm.PyNode(oFullName)
        else:
            myObj.addAttr(oParamName, at=oDataType, keyable=True, dv=oDefault)
            myAttr = pm.PyNode(myObj + '.' + oParamName)
            if oMin is not None:
                myAttr.setMin(oMin)
            if oMax is not None:
                myAttr.setMax(oMax)
            pm.setAttr(myAttr, e=True, channelBox=True)
            pm.setAttr(myAttr, e=True, keyable=True)
            return myAttr

    @staticmethod
    def connect_multiply(oDriven, oDriver, oMultiplyBy):
        nodeName = oDriven.replace('.', '_') + '_mult'
        try:
            testExists = pm.PyNode(nodeName)
            pm.delete(pm.PyNode(nodeName))
            print('deleting'.format(nodeName))
        except:
            pass
        oMult = pm.shadingNode('unitConversion', asUtility=True, name=nodeName)
        pm.PyNode(oDriver).connect(oMult.input)
        oMult.output.connect(pm.Attribute(oDriven))
        oMult.conversionFactor.set(oMultiplyBy)
        return oMult

    def many_follicles(self, myObject, countU, countV, vDir='U'):
        self.countU = countU
        self.countV = countV
        self.vDir = vDir

        obj = self.subject
        pm.select(obj, r=True)
        pName = '{}{}'.format(NC.getSideFromName(obj), NC.getBasename(obj))
        self._MODEL.getFolliGrp = pm.spaceLocator(n='{}{}_FOLLI_{}__{}'.format(NC.getSideFromName(obj), NC.getBasename(obj), NC.SYSTEM, NC.GRP))
        pm.delete(self._MODEL.getFolliGrp.getShape())
        currentFollNumber = 0

        for i in range(countU):
            for j in range(countV):
                currentFollNumber += 1
                pm.select(None)
                if countU == 1:
                    uPos = 50.0
                else:
                    uPos = (i / (countU - 1.00)) * 100.0  # NOTE: I recently changed this to have a range of 0-10
                if countV == 1:
                    vPos = 50.0
                else:
                    vPos = (j / (countV - 1.00)) * 100.0  # NOTE: I recently changed this to have a range of 0-10
                if vDir == 'U':
                    oFoll = self.create_follicle(myObject, currentFollNumber, vPos, uPos)
                    self._MODEL.getFollicules.append(oFoll)
                else:
                    # reverse the direction of the follicles
                    oFoll = self.create_follicle(myObject, currentFollNumber, uPos, vPos)
                    self._MODEL.getFollicules.append(oFoll)

                pm.rename(oFoll.getParent(), '{}_0{}__{}'.format(pName, currentFollNumber, NC.FOLL_SUFFIX))
                pm.rename(oFoll, '{}_{}__foll__Shape'.format(pName, currentFollNumber))
                oGrp = pm.group(em=True, n='{}_0{}__{}'.format(pName, currentFollNumber, NC.GRP))
                self._MODEL.getResetJoints.append(oGrp)
                oGrp.setTranslation(oFoll.getParent().getTranslation(space='world'), space='world')

                oJoint = pm.joint(n='{}_0{}__{}'.format(pName, currentFollNumber, NC.JOINT), rad=self.radius)
                self._MODEL.getJoints.append(oJoint)
                oJoint.setTranslation(oFoll.getParent().getTranslation(space='world'), space='world')
                pm.matchTransform(oJoint, oGrp, rot=1)

                # connect the UV params to the joint so you can move the follicle by selecting the joint directly.
                uParam = self.add_keyable_attribute(oJoint, 'double', 'u_param', oMin=-100, oMax=100, oDefault=0)
                vParam = self.add_keyable_attribute(oJoint, 'double', 'v_param', oMin=-100, oMax=100, oDefault=0)
                uParam.set(oFoll.getParent().u_param.get())
                vParam.set(oFoll.getParent().v_param.get())
                uParam.connect(oFoll.getParent().u_param)
                vParam.connect(oFoll.getParent().v_param)

                pm.parent(oGrp, oFoll.getParent())
                pm.parent(oFoll.getParent(), self._MODEL.getFolliGrp)

                pm.select(None)

        return self._MODEL.getFollicules


    def addControls(self, shape=sl.ball_shape, scale=1, color=('index', 13)):
        """ add Controls to the follicules """

        create_ctrls =  [Control.Control(str(joint),
                            shape = shape,
                            scale=scale,
                            parent = self.INPUT_GRP,
                            matchTransforms=(joint, 0, 0),
                            color=color,
                            ) for joint in self._MODEL.getJoints]

        for foll, ctrls in zip(self._MODEL.getFollicules,  create_ctrls):
            offset = adb.makeroot_func(ctrls.control, 'OFFSET')
            self._MODEL.getInputs.append(offset)
            self._MODEL.getResetControls.append(offset)
            pm.rename(offset, '{}'.format(offset).replace('__CTRL', ''))
            Transform(foll.getTransform()).matrixConstraint(offset, channels='trh', mo=True)

        for grp, ctrls in zip(self._MODEL.getResetJoints, create_ctrls):
            pm.parent(grp, ctrls.control)

        self._MODEL.getControls = create_ctrls
        return self._MODEL.getControls


    def add_folli(self, add_value):
        """
        add follicules to an already existing system

        @param add_value: (int) Number of follicules to add
        @param mesh: (str) Mesh having the follicules

        """
        mesh = self.subject

        for index in range(add_value):
            mesh_shape = pm.PyNode(mesh).getShape()

            plugs = pm.listConnections(str(mesh_shape) + '.outMesh', d=True, sh=True)
            current_numb_foll = len([x for x in plugs if x.type() == 'follicle'])
            oFoll = self.create_follicle(pm.PyNode(mesh), (current_numb_foll + 1), 1)
            pName = '{}{}'.format(NC.getSideFromName(mesh), NC.getBasename(mesh))
            oRoot = [x for x in plugs if x.type() == 'follicle'][0].getParent().getParent()

            pm.rename(oFoll.getParent(), '{}_0{}__{}'.format(pName, current_numb_foll + 1, NC.FOLL_SUFFIX))
            pm.rename(oFoll, '{}_{}__foll__Shape'.format(pName, current_numb_foll))

            oGrp = pm.group(em=True, n='{}_0{}__{}'.format(pName, index, NC.GRP))
            oGrp.setTranslation(oFoll.getParent().getTranslation(space='world'), space='world')

            oJoint = pm.joint(rad=self._MODEL.getJoints[0].radius.get())
            self._MODEL.getJoints.append(oJoint)
            oJoint.setTranslation(oFoll.getParent().getTranslation(space='world'), space='world')

            # connect the UV params to the joint so you can move the follicle by selecting the joint directly.
            uParam = self.add_keyable_attribute(oJoint, 'double', 'u_param', oMin=-100, oMax=100, oDefault=0)
            vParam = self.add_keyable_attribute(oJoint, 'double', 'v_param', oMin=-100, oMax=100, oDefault=0)
            uParam.set(oFoll.getParent().u_param.get())
            vParam.set(oFoll.getParent().v_param.get())
            uParam.connect(oFoll.getParent().u_param)
            vParam.connect(oFoll.getParent().v_param)

            pm.rename(oJoint,'{}_0{}__{}'.format(pName, current_numb_foll + 1, NC.JOINT))
            pm.rename(oJoint.getParent(), '{}_0{}__{}'.format(pName, current_numb_foll + 1, NC.GRP))

            pm.parent(oGrp, oFoll.getParent())
            pm.parent(oFoll.getParent(), oRoot)

            Transform(oFoll.getTransform().getChildren(type='transform')[0]).matrixConstraint(oJoint, channels='trh', mo=True)
            pm.parent(oJoint, self.OUTPUT_GRP)
            pm.select(None)

        # Re adjust all the U and V attribute
        inital_v_param = self._MODEL.getJoints[0].v_param.get()
        for index, joint in enumerate(self._MODEL.getJoints):
            uPos = (index / (len(self._MODEL.getJoints) - 1.00)) * 100.0
            joint.u_param.set(uPos)
            joint.v_param.set(inital_v_param)

# arm = Folli('ArmFolli', 1, 5, radius = 0.5, subject = 'proxy_plane')
# arm.start()
# arm.build()

# arm.add_folli(23)
# arm.addControls()




