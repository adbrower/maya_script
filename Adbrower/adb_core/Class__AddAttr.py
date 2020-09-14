# -------------------------------------------------------------------
# Class Attribute Module
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# -------------------------------------------------------------------

import sys
from collections import namedtuple

import pymel.core as pm
import maya.cmds as mc

from adbrower import undo


# -----------------------------------
# CLASS
# -----------------------------------


class NodeAttr(object):
    """
    A Module for creating attributes easier based on the type of the argument passed as the default value (dv)

    @param _node: Single string or a list. Default value is pm.selected()

    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_core.Class__AddAttr as adbAttr
    reload (adbAttr)

    # example:
    node = adbAttr.NodeAttr()
    node.addAttr('adb', 50)
    node.addAttr('sim', True)
    node.addAttr('test', 'enum',  eName = "Green:Blue:")

    """

    def __init__(self,
                 _node=pm.selected(),
                 ):
        if isinstance(_node , str):
            self.node = [pm.PyNode(_node)]

        elif isinstance(_node , list):
            self.node = [pm.PyNode(x) for x in _node]

        else:
            self.node = [pm.PyNode(_node)]

        self.name = None
        self.attr = None
        self.list_methods = {}

    def __repr__(self):
        return str('Class name:{} | Object:{} \n {}'.format(self.__class__.__name__, self.node, self.__class__))

    def __getattr__(self, name):
        try:
            currentValue = []
            for node in self.node:
                _currentValue = pm.getAttr('{}.{}'.format(node, name))
                currentValue.append(_currentValue)
                self.list_methods[name] = currentValue
            
            if len(currentValue) == 1:
                return currentValue[0]
            else:
                return currentValue
        except:
            raise AttributeError('object has no attribute {}'.format(name))

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if hasattr(self, name):
            object.__setattr__(self, name, value)  # inital setAttr
            try:
                for node in self.node:
                    pm.setAttr(node + '.' + name, value)
                    self.list_methods[name] = value
            except:
                pass
        else:
            raise AttributeError('object has no attribute {}'.format(name))


# -----------------------------------
# CLASS METHODS
# -----------------------------------


    @classmethod
    def convertFromAttr(cls,  attrList=[], _transform=pm.selected()):
        """
        Convert an existing attribute to the module

        Args:
            attrList (list, optional): [description]. Defaults to [].
            _transform (tranform, optional): Defaults to pm.selected().

        Returns:
            instance of the class
        """
        instance = cls(_transform)
        for node in instance.node:
            for attribute in attrList:
                instance.list_methods.update({attribute: pm.getAttr(
                    '{}.{}'.format(node, attribute))})
        return cls(_transform)


    @classmethod
    @undo
    def copyAttr(cls, source, targets, all=True, ignore=[], nicename=None, forceConnection=False):
        """
        Select mesh and the attribute(s) to copy
        Needs to put the targets into a list
        """
        cls = cls(source)
        _type = type(targets)
        source = pm.PyNode(source)
        _nicename = nicename

        if _type == str:
            targets = [targets]
        elif _type == list:
            pass

        def copyAttrLoop(attribute, target, nicename=_nicename):
            source_attr = pm.PyNode(source).name() + '.' + attribute
            attr = attribute
            _at = str(mc.addAttr(source_attr, q=True, at=True)) or None
            __ln = mc.addAttr(source_attr, q=True, ln=True) or None

            if nicename:
                _ln = '{}_{}'.format(nicename, __ln)
            else:
                _ln = __ln

            _min = mc.addAttr(source_attr, q=True, min=True) or None
            _max = mc.addAttr(source_attr, q=True, max=True) or None
            _dv = mc.addAttr(source_attr, q=True, dv=True) or 0
            _parent = mc.addAttr(source_attr, q=True, p=True) or None
            _locked = pm.getAttr(source_attr, lock=True)

            if cls.isSeparator(attr):
                enList = []
                _en = pm.attributeQuery(str(attr), node=source.name(), listEnum=True)[0]
                enList.append(_en)
                cls.AddSeparator(target, label=enList[0])
            else:
                if pm.objExists('{}.{}'.format(target, attribute)):
                    pass

                elif _at == 'enum':
                    enList = []
                    _en = pm.attributeQuery(str(attr), node=source.name(), listEnum=True)[0]
                    enList.append(_en)

                    pm.addAttr(target, ln=str(_ln), at='enum', en=str(enList[0]), keyable=True)

                elif _locked:
                    pass

                elif _parent != __ln:
                    siblings = pm.attributeQuery(str(attr), node=source.name(), ls=True)
                    parent = pm.attributeQuery(str(attr), node=source.name(), lp=True)[0]
                    pm.addAttr(target, ln=parent, at='compound', nc= 1 + len(siblings), keyable=True)
                    pm.addAttr(target, ln=str(_ln), at=str(_at),  dv=_dv, keyable=True, parent=parent)

                    for sib in siblings:
                        defaultValue = mc.addAttr('{}.{}'.format(source.name(), sib), q=True, dv=True) or 0
                        pm.addAttr(target, ln=str(sib), at=str(_at),  dv=defaultValue, keyable=True, parent=parent)
                else:
                    pm.addAttr(target, ln=str(_ln), at=str(_at),  dv=_dv, keyable=True)

                target_attr = target + '.' + _ln
                if _min is not None:
                    pm.addAttr(target_attr, e=True, min=_min)
                elif _max is not None:
                    pm.addAttr(target_attr, e=True, max=_max)
                else:
                    pass

        if all:
            temp = pm.listAttr(source, k=1, v=1, ud=1)
            siblingsToRemove = []
            parentToRemove = []
            for a in temp:
                siblings = pm.attributeQuery(a, node=source, ls=1)
                if siblings:
                    siblingsToRemove.extend(siblings)
                    parent = pm.attributeQuery(a, node=source, lp=1)
                    parentToRemove.extend(parent)

            def Diff(li1, li2):
                """
                Substract li2 from li1
                Args:
                    li1 (List)
                    li2 (List)
                Returns:
                    List
                """
                li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
                return li_dif

            temp2 = (Diff(temp, siblingsToRemove[:-1]))
            all_attr = (Diff(temp2, parentToRemove))
            if ignore:
                all_attr = (Diff(all_attr, ignore))
        else:
            all_attr = [x for x in pm.channelBox("mainChannelBox", q=1, selectedMainAttributes=1)]

        for att in all_attr:
            for target in targets:
                copyAttrLoop(att, target)

        if forceConnection:
            for att in pm.listAttr(source, ud=1):
                try:
                    if nicename:
                        new_att = '{}_{}'.format(nicename, att)
                        pm.connectAttr('{}.{}'.format(target, new_att), '{}.{}'.format(source, att))
                    else:
                        pm.connectAttr('{}.{}'.format(target, att), '{}.{}'.format(source, att))
                except RuntimeError:
                    pass


    @classmethod
    def AddSeparator(cls, _transform, label = False):
        """
        Add a seperator in the Channel Box
        """
        if isinstance(_transform, str):
            node = _transform
        elif isinstance(_transform, list):
            node = _transform[0]
        else:
            node = _transform
        name = "__________"

        i = 0
        for i in range(0, 100):
            if i == 100:
                pm.pm.mel.error(
                    "There are more than 20 seperators. Why would you even need that many.")

            if pm.mel.attributeExists(name, node):
                name = str(pm.mel.stringAddPrefix("_", name))
            else:
                break

        en = "................................................................:"

        if label:
            pm.addAttr(node, ln=name, keyable=True, en=label, at="enum", nn=en)
        else:
            pm.addAttr(node, ln=name, keyable=True, en=en, at="enum", nn=en)
        pm.setAttr((node + "." + name), lock=True)
        return cls(_transform)


# -----------------------------------
# PROPERTIES
# -----------------------------------


    @property
    def subject(self):
        """ Returns the subject on which the attributes are added"""
        if len(self.node) == 1:
            return str(self.node[0])
        else:
            return [str(x) for x in self.node]


    @property
    def getValue(self):
        """ Returns the value of the attribute"""
        return self.attr


    @property
    def attrName(self):
        """ Returns the attribute's name"""
        return self.name


    @property
    def allAttrs(self):
        """ Returns the list of all the new methods / attributes added"""
        return self.list_methods


    @property
    def getAttrConnection(self):
        """
        Returns the attribute name for making a connection
        Returns: List
        """
        all_attr = []
        for each in self.node:
            attr = '{}.{}'.format(each, self.attrName)
            all_attr.append(attr)
        return all_attr



# -----------------------------------
# METHODS
# -----------------------------------


    def addAttr(self, name, attr, dv=None, min=None, max=None, eName=None, keyable=True, lock=False, parent=None, nc=None):
        """
        Function Adding a new attribute according to the type of the default value argument

        @param name: (String) giving the name of the attribute
        @param attr: It is given by the type of de default value (dv) argument
        @param dv: data which will determine the type of the attribute. Default value is None
        @param min: (Integer) to determine the minimum of the attribute. The attribute type needs to be Float or Integer. Default value is None
        @param max: (Integer) to determine the maximum of the attribute. The attribute type needs to be Float or Integer. Default value is None
        @param eName: eName = "Green:Blue:", enumName of an attribute of type
        @param keyable: (Boolean) to determine if the parameter is keyable or not. Default value is True
        @param lock: (Boolean) to determine if all the default attributes will be locked. Calls the methods: lockAttribute()
        @param parent: (string) name of the parent
        @param nc: (int) Number of children

        """

        nodeTypeDic = {
            "<type 'str'>": {'dt': 'string'},
            "<type 'bool'>": {'dt': 'bool'},
            "<type 'int'>": {'dt': 'float'},
            "<type 'float'>": {'dt': 'float'},
            "enum": {'dt': 'enum'},
            'message': {'dt': 'message'},
        }

        self.name = name
        self.attr = attr

        def addParent_Attr():
            for node in self.node:
                pm.PyNode(node).addAttr(name, at=self.attr, keyable=keyable, nc=nc)

        def addFloat_int():
            """ Add an attribute of type Float or integer"""
            max_val = max or []
            min_val = min or []

            def _getValue():
                if max_val:
                    val1 = True
                else:
                    val1 = False
                if min_val:
                    val2 = True
                else:
                    val2 = False
                value = val1 or val2
                return value
            val = _getValue()

            if val:
                if parent is not None:
                    for node in self.node:
                        pm.PyNode(node).addAttr(
                            name, at=nodeTypeDic[_type]['dt'], dv=attr,  min=min, max=max, keyable=keyable, parent=parent)
                else:
                    for node in self.node:
                        pm.PyNode(node).addAttr(
                            name, at=nodeTypeDic[_type]['dt'], dv=attr,  min=min, max=max, keyable=keyable,)
            else:
                if parent is not None:
                    for node in self.node:
                        pm.PyNode(node).addAttr(
                            name, at=nodeTypeDic[_type]['dt'], dv=attr, keyable=keyable, parent=parent)
                else:
                    for node in self.node:
                        pm.PyNode(node).addAttr(
                            name, at=nodeTypeDic[_type]['dt'], dv=attr, keyable=keyable)
            # self.addMethods()

        def addBool():
            """ Add an attribute of type Boolean"""

            for node in self.node:
                if parent is not None:
                    pm.PyNode(node).addAttr(
                        name, at=nodeTypeDic[_type]['dt'], dv=attr, keyable=keyable, parent=parent)
                else:
                    node.addAttr(
                        name, at=nodeTypeDic[_type]['dt'], dv=attr, keyable=keyable)
            # self.addMethods()

        def addString():
            """ Add an attribute of type String"""
            if parent is not None:
                for node in self.node:
                    pm.PyNode(node).addAttr(
                        name, dt=nodeTypeDic[_type]['dt'], keyable=keyable, parent=parent)
                    pm.PyNode((str(node) + '.' + name)).set(attr)
            else:
                for node in self.node:
                    pm.PyNode(node).addAttr(
                        name, dt=nodeTypeDic[_type]['dt'], keyable=keyable)
                    pm.PyNode((str(node) + '.' + name)).set(attr)
            # self.addMethods()

        def addEnum():
            """
            Add an attribute of type Enum.
            ex: node.addAttr('test', 'enum',  eName = "Green:Blue:")
            """
            if parent is not None:
                for node in self.node:
                    pm.PyNode(node).addAttr(
                        name, at=nodeTypeDic[_type]['dt'], enumName=eName, keyable=keyable, parent=parent)
            else:
                for node in self.node:
                    pm.PyNode(node).addAttr(
                        name, at=nodeTypeDic[_type]['dt'], enumName=eName, keyable=keyable)
            # self.addMethods()

        def addMessage():
            """ Add an attribute of type Message"""
            if parent is not None:
                for node in self.node:
                    pm.PyNode(node).addAttr(
                        name, at=nodeTypeDic[_type]['dt'], keyable=keyable, parent=parent)
            else:
                for node in self.node:
                    pm.PyNode(node).addAttr(
                        name, at=nodeTypeDic[_type]['dt'], keyable=keyable)
            # self.addMethods()

        _type = attr
        if _type == 'enum':
            _type = 'enum'

        elif _type == 'message':
            _type = 'message'

        elif _type == 'float2':
            _type = 'float2'

        elif _type == 'float3':
            _type = 'float3'

        elif _type == 'double2':
            _type = 'double2'

        elif _type == 'double3':
            _type = 'double3'

        elif _type == 'compound':
            _type = 'compound'
        else:
            _type = str(type(attr))

        addAttrDic = {
            "<type 'str'>": addString,
            "<type 'bool'>": addBool,
            "<type 'int'>": addFloat_int,
            "<type 'float'>": addFloat_int,
            "enum": addEnum,
            'message': addMessage,
            'compound': addParent_Attr,
            'float3': addParent_Attr,
            'float2': addParent_Attr,
        }

        try:
            addAttrDic[_type]()  # runs the dictionnary
        except Exception as e:
            pass
        # add the methods to the dictionnary
        currentValue = pm.getAttr('{}.{}'.format(self.subject, self.attrName))
        self.list_methods.update(
            {self.attrName: currentValue})  # self.addMethods()
        if lock is True:
            for node in self.node:
                pm.setAttr('{}.{}'.format(node, self.attrName), lock=True)
        else:
            pass
        return(self.node)


    def addMethods(self):
        """ Add all the new attributes as methods of the class"""
        for methods in self.list_methods:
            setattr(NodeAttr, methods, self.list_methods[methods])



    def set(self, attr, value):
        """
        Function to set a new value of an attribute

        @param attr: String returning the name of the attribute you want to change
        @param value: The new value you want to give to the attribute

        """
        for node in self.node:
            node.setAttr(attr, value)


    def setDefault(self, attr, value):
        """
        Function to set a new value of an attribute

        @param attr: String returning the name of the attribute you want to change
        @param value: The new value you want to give to the attribute

        """
        for node in self.node:
            node.setAttr(attr, value)
            pm.addAttr('{}.{}'.format(node, attr), e=True,  dv=value)


    def lockAttribute(self, att_to_lock=['tx', 'ty', 'tz', 'rx', 'ry', 'rx', 'rz', 'sx', 'sy', 'sz'], cb=False):
        """
        Function to lock all default attribute except visibility
        """
        for sub in self.node:
            for att in att_to_lock:
                pm.PyNode(sub).setAttr(att, lock=True,
                                       channelBox=cb, keyable=False)


    def unlockAttribute(self, att_to_lock=['tx', 'ty', 'tz', 'rx', 'ry', 'rx', 'rz', 'sx', 'sy', 'sz']):
        """
        Function to unlock all default attribute except visibility
        """
        for sub in self.node:
            for att in att_to_lock:
                pm.PyNode(sub).setAttr(att, lock=False, keyable=True)


    def unhideAll(self):
        """
        Unhide and Unlock all channelBox attributes
        """
        att_to_lock = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
        transform = cls(_transform)
        for transform in transform.node:
            for att in att_to_lock:
                pm.PyNode(transform).setAttr(att, lock=False, keyable=True)
        return cls(_transform)


    def addRotationOrderAttr(self):
        for node in self.node:
            pm.addAttr(node, ln="rotationOrder",
                        en="xyz:yzx:zxy:xzy:yxz:zyx:", at="enum")
            pm.setAttr((str(node) + ".rotationOrder"),
                        e=1, keyable=True)
            pm.connectAttr((str(node) + ".rotationOrder"),
                            (str(node) + ".rotateOrder"))


    def breakConnection(self, attributes=['v']):
        """
        Break Connection
        @param attributes : list of different attribute:  ['tx','ty','tz','rx','ry','rz','sx','sy','sz', 'v']

        The default value is : ['v']
        """

        for att in attributes:
            for node in self.node:
                attr = node + '.' + att

                destinationAttrs = pm.listConnections(
                    attr, plugs=True, source=False) or []
                sourceAttrs = pm.listConnections(
                    attr, plugs=True, destination=False) or []

                for destAttr in destinationAttrs:
                    pm.disconnectAttr(attr, destAttr)
                for srcAttr in sourceAttrs:
                    pm.disconnectAttr(srcAttr, attr)


    def getLock_attr(self):
            """
            Get Current list of channel box attributes which are unlock
            returns: List
            """
            attrLock = []
            for node in self.node:
                _attrLock = pm.listAttr(node, l=True) or []
                attrLock.append(_attrLock)
            return attrLock


    @staticmethod
    def addPaintAttribute(shape, attrName, subName = 'mesh'):
        """Create a attribute with is paintable

        Arguments:
            shape {String} -- shape of the mesh
            attrName {String} -- Name of the attribute
            subName {String} -- Name of the node ex: mesh.polyHide, deformer.weights

        Returns:
            Plug -- Plug of the attribute
        """
        plug = '{}.{}'.format(shape, attrName)
        vertCount = mc.polyEvaluate(shape, vertex=True)

        if not mc.objExists(plug):
            mc.addAttr(shape, longName=attrName, dataType='doubleArray')
            mc.makePaintable(subName, attrName)
            pm.PyNode(plug).set([0] * vertCount, type='doubleArray')
        else:
            if not vertCount == len(list(mc.getAttr(plug))):
                pm.PyNode(plug).set([0] * pm.polyEvaluate(shape, vertex=True), type='doubleArray')
        return plug


    @staticmethod
    def rmvPaintAttribute(subName, attrName):
        mc.makePaintable(subName, attrName, rm=1)


    @staticmethod
    def ShiftAtt(mode, _obj=mc.channelBox('mainChannelBox', q=True, mol=True), _attr=mc.channelBox('mainChannelBox', q=True, sma=True)):
        """
        Shift an attribute in the channelBox
        @param mode: {0:1}
            if 0: shift Down
            if 1: shift Up
        """
        obj = _obj
        if obj:
            attr = _attr
            if attr:
                for eachObj in obj:
                    udAttr = mc.listAttr(eachObj, ud=True)
                    if not attr[0] in udAttr:
                        sys.exit(
                            'selected attribute is static and cannot be shifted')
                    # temp unlock all user defined attributes
                    attrLock = mc.listAttr(eachObj, ud=True, l=True)
                    if attrLock:
                        for alck in attrLock:
                            mc.setAttr(eachObj + '.' + alck, lock=0)

                    # shift down
                    if mode == 0:
                        if len(attr) > 1:
                            attr.reverse()
                            sort = attr
                        if len(attr) == 1:
                            sort = attr
                        for i in sort:
                            attrLs = mc.listAttr(eachObj, ud=True)
                            attrSize = len(attrLs)
                            attrPos = attrLs.index(i)
                            mc.deleteAttr(eachObj, at=attrLs[attrPos])
                            mc.undo()
                            for x in range(attrPos + 2, attrSize, 1):
                                mc.deleteAttr(eachObj, at=attrLs[x])
                                mc.undo()
                    # shift up
                    if mode == 1:
                        for i in attr:
                            attrLs = mc.listAttr(eachObj, ud=True)
                            attrSize = len(attrLs)
                            attrPos = attrLs.index(i)
                            if attrLs[attrPos - 1]:
                                mc.deleteAttr(eachObj, at=attrLs[attrPos - 1])
                                mc.undo()
                            for x in range(attrPos + 1, attrSize, 1):
                                mc.deleteAttr(eachObj, at=attrLs[x])
                                mc.undo()

                    # relock all user defined attributes
                    if attrLock:
                        for alck in attrLock:
                            mc.setAttr(eachObj + '.' + alck, lock=1)


    @staticmethod
    def isSeparator(attrName):
        if '___' in attrName:
            return True
        else:
            return False


    @staticmethod
    def enumAttr(_transform, name='name', en="On:Off"):
        """
        Create an enum On:Off
        """
        pm.PyNode(_transform).addAttr(name, keyable=True,
                                attributeType='enum', en=en)


    @staticmethod
    @undo
    def ResetAttr():
        """
        Resets selected channels in the channel box to default, or if nothing's
        selected, resets all keyable channels to default.
        """
        import maya.mel as mm

        def main(selectedChannels=True, transformsOnly=False, excludeChannels=None):
            gChannelBoxName = mm.eval('$temp=$gChannelBoxName')

            sel = mc.ls(sl=True)
            if not sel:
                return

            if excludeChannels and not isinstance(excludeChannels, (list, tuple)):
                excludeChannels = [excludeChannels]

            chans = None
            if selectedChannels:
                chans = mc.channelBox(gChannelBoxName, query=True, sma=True)

            testList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ',
                        'tx', 'ty', 'yz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
            for obj in sel:
                attrs = chans
                if not chans:
                    attrs = mc.listAttr(obj, keyable=True, unlocked=True)
                    if excludeChannels:
                        attrs = [x for x in attrs if x not in excludeChannels]
                if transformsOnly:
                    attrs = [x for x in attrs if x in testList]
                if attrs:
                    for attr in attrs:
                        try:
                            default = mc.attributeQuery(
                                attr, listDefault=True, node=obj)[0]
                            mc.setAttr(obj + '. ' + attr, default)
                        except StandardError:
                            pass

        def resetPuppetControl(*args):
            main(excludeChannels=['rotateOrder',
                                  'pivotPosition', 'spaceSwitch'])

        resetPuppetControl()


# -----------------------------------
#   IN CLASS BUILD
# -----------------------------------


# node = NodeAttr('pCube1')
# node.copyAttr('pCube1', 'pSphere1', all=1)
# node.addAttr("UV", 'compound', nc=2)
# node.addAttr("U_pos", 0, min = 0, max = 100, parent = "UV")
# node.addAttr("V_pos", 0.5, min = 0, max = 1, parent = "UV")
# node.addAttr("zipper", 0, min = 0, max = 100)
# node.addAttr('BowTie_Vis', 'enum',  eName = "off:on:")
# node.addAttr('adb', 50)
# node.addAttr("COUCOU", 'message')



# -----------------------------------
#   EXEMPLE  EXTERIOR CLASS BUILD
# -----------------------------------

# import adb_core.Class__AddAttr as adbAttr
# reload (adbAttr)

# node = adbAttr.NodeAttr()
# node.addAttr('adb', 50)
# node.addAttr('sim', True)
# node.addAttr('test', 'enum',  eName = "Green:Blue:")
