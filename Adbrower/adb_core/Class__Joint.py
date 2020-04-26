# -------------------------------------------------------------------
# Class Joint
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# -------------------------------------------------------------------


from collections import namedtuple
import pymel.core.datatypes as dt

import adb_core.Class__Transforms as adbTransform
import adbrower
import pymel.core as pm
import maya.cmds as mc

adb = adbrower.Adbrower()

# -----------------------------------
# CLASS
# -----------------------------------


class Joint(adbTransform.Transform):
    """A Module containing multiples joint methods"""

    def __init__(self,
                 _joints,
                 ):

        self.joints = _joints

        if isinstance(self.joints, list):
            self.joints = [pm.PyNode(x) for x in _joints]
        elif isinstance(self.joints, basestring):
            self.joints = [_joints]
        else:
            self.joints = _joints

        super(Joint, self).__init__(self.joints)

    @classmethod
    def find_all(cls):
        """ Return a Joint instance for every joint node in the scene. """
        return cls([jnt for jnt in pm.ls(type='joint')])

    @classmethod
    def from_selected(cls):
        """ Return a instance for a list with all selected """
        return cls([(jnt) for jnt in pm.selected()])

    @classmethod
    def create(cls, numb=1, name='joint1', rad=1):
        jnt_created = []
        for number in range(numb):
            jnt = pm.joint(n='{}_{:02d}'.format(name, number+1), rad=rad)
            pm.parent(jnt, w=1)
            jnt_created.append(jnt)
        return cls(jnt_created)

    @classmethod
    def point_base(cls, *point_array, **kwargs):
        """
        @param *point_array : (list) Each element of the list need to be a vector value (x,y,z)
                                     and it will be unpack

        @param padding      : (Bool) If the joints will have padding number
        @param chain        : (Bool) If the joints will be chained or not
        @param orient_axis  : (string)  'x' : 'y' :  'z' : 'world'

        # example
        points =[[0.0, 0.0, 0.0],[-2.54, 4.68, -0.96],[2.66, 4.66, -6.16], [0.66, 8.22, -6.83]]
        test = adbJnt.Joint.point_base(*points)
        """

        name = kwargs.pop('name', 'joint1')
        padding = kwargs.pop('padding', False)
        radius = kwargs.pop('radius', 1)
        chain = kwargs.pop('chain', False)
        orient_axis = kwargs.pop('orient_axis', 'world')

        joint_array = []
        for index, point in enumerate(point_array):
            pm.select(None)
            if padding:
                new_joint = pm.joint(name='{}_{:02d}'.format(name, index+1), p=point, rad=radius)
            else:
                new_joint = pm.joint(name=name, p=point, rad=radius)
            joint_array.append(new_joint)

        if chain:
            def chain_parent(oColljoint):
                for oParent, oChild in zip(oColljoint[0:-1], oColljoint[1:]):
                    try:
                        pm.parent(oChild, None)
                        pm.parent(oChild, oParent)
                    except RuntimeError:
                        continue

            chain_parent(joint_array)

        # orient joint
        _temp = cls(joint_array)
        _temp.orient_axis = orient_axis

        return cls(joint_array)

    @classmethod
    def selection_base(cls, *args, **kwargs):
        """
        @param *point_array : (list) Each element of the list need to be a vector value (x,y,z)
                                     and it will be unpack

        @param name        : (String)
        @param padding      : (Bool) If the joints will have padding number

        # example
        points =[[0.0, 0.0, 0.0], [-2.54, 4.68, -0.96], [2.66, 4.66, -6.16], [0.66, 8.22, -6.83]]
        test = adbJnt.Joint.selection_base()
        """

        name = kwargs.pop('name', 'joint1')
        padding = kwargs.pop('padding', False)

        jnts_array = []
        for index, sel in enumerate(pm.selected()):
            # create variable for the position of the locators
            pos = sel.getRotatePivot(space='world')
            # unparent the joints
            pm.select(cl=True)
            # create joints and position them on top of locators
            if padding:
                _joint = pm.joint(p=pos, n='{}_{}'.format(name, index+1))
            else:
                _joint = pm.joint(p=pos, n=name)
            jnts_array.append(_joint)

        return cls(jnts_array)

    def __init__(self,
                 _joint,
                 ):

        self.joints = _joint
        self._orient_axis = None
        self._radius = None

        if isinstance(self.joints, list):
            self.joints = [pm.PyNode(x) for x in _joint]
        elif isinstance(self.joints, str):
            self.joints = [_joint]
        else:
            self.joints = _joint

        super(Joint, self).__init__(self.joints)

    def __repr__(self):
        return str('<{} \'{}\'>'.format(self.__class__.__name__, self.joints))


    @property
    def draw_style(self):
        if self.joints is None:
            pass
        return pm.PyNode(self.joints[0]).draw_style.get()

    @draw_style.setter
    def draw_style(self, value):
        """
        0 : Bone
        1 : Multi - Child as box
        2 : None
        """
        for jnt in self.joints:
            pm.PyNode(jnt).draw_style.set(value)

    @property
    def radius(self):
        if self.joints is None:
            pass
        rad = pm.PyNode(self.joints[0]).radius.get() or []
        if rad:
            self._radius = rad
        else:
            pass
        return self._radius

    @radius.setter
    def radius(self, rad):
        self._radius = rad
        for joint in self.joints:
            pm.PyNode(joint).radius.set(rad)


    def orient_joint(self):
        if self._orient_axis == 'Y':
            pm.select(self.joints)
            pm.joint(zso=1, ch=1, e=1, oj='yxz', secondaryAxisOrient='xdown')
            pm.select(cl=True)

            # Orient the last joint to the world#
            pm.select(self.joints[-1])
            pm.joint(e=1, oj='none')
            pm.select(None)

        elif self._orient_axis == 'y':
            pm.select(self.joints)
            pm.joint(zso=1, ch=1, e=1, oj='yxz', secondaryAxisOrient='xup')
            pm.select(cl=True)

            # Orient the last joint to the world#
            pm.select(self.joints[-1])
            pm.joint(e=1, oj='none')
            pm.select(None)

        elif self._orient_axis == 'X':
            pm.select(self.joints)
            pm.joint(zso=1, ch=1, e=1, oj='xyz', secondaryAxisOrient='xup')
            pm.select(cl=True)

            # Orient the last joint to the world#
            pm.select(self.joints[-1])
            pm.joint(e=1, oj='none')
            pm.select(None)

        elif self._orient_axis == 'x':
            pm.select(self.joints)
            pm.joint(zso=1, ch=1, e=1, oj='xyz', secondaryAxisOrient='xdown')
            pm.select(cl=True)

            # Orient the last joint to the world#
            pm.select(self.joints[-1])
            pm.joint(e=1, oj='none')
            pm.select(None)

        elif self._orient_axis == 'world':
            pm.select(self.joints)
            pm.joint(zso=1, ch=1, e=1, oj='none')
            pm.select(cl=True)

        else:
            raise ValueError('That Axis does not exist')

    @property
    def orientAxis(self):
        if len(self.joints) > 1:
            vec = self.getVectors(str(self.joints[0]))
        else:
            vec = self.getVectors(str(self.joints))
        return self.getAxis(vec.aimV)


    @orientAxis.setter
    def orientAxis(self, val):
        self._orient_axis = val
        self.orient_joint()

    @staticmethod
    def label_jnts(left_side='L_', right_side='R_'):
        for sel in pm.ls(type='joint'):
            short = sel.split('|')[-1].split(':')[-1]
            if short.startswith(left_side):
                side = 1
                other = short.split(left_side)[-1]
            elif short.startswith(right_side):
                side = 2
                other = short.split(right_side)[-1]
            else:
                side = 0
                other = short
            pm.setAttr('{0}.side'.format(sel), side)
            pm.setAttr('{0}.type'.format(sel), 18)
            pm.setAttr('{0}.otherType'.format(sel), other, type='string')


    @staticmethod
    def getClosestVector(v, axies=None):
        """
        returns the vector in axies that is the closets to the vector v

        :param tuple v: input vector
        :param list axies: list of vectors to match against.
                           defaults to the vectors of [+x, -x, +y, -y, +z, -z]
        :rtype: tuple
        """
        axies = axies or [(1, 0, 0), (0, 1, 0), (0, 0, 1),
                          (-1, 0, 0), (0, -1, 0), (0, 0, -1)]
        return sorted(axies, key=lambda a: dt.Vector(v).dot(a))[-1]


    def getVectors(self, obj, child=None, normal=(0, 0, 1)):
        """
        get local aim and up vectors

        :param str obj: name of the transform
        :param tuple normal: inVector to compute the upVector defaults to (0,0,1)
        :return: (aimVector, upVector) as tuple
        :rtype: tuple
        """
        # Get first child joint or, if no children, use the joint itself
        # to get translation vector (if has a parent, otherwise error...)
        if not child:
            children = mc.listRelatives(obj, c=True, type="joint")
            if not children:
                parent = mc.listRelatives(obj, p=True, type="joint")[0]
                if not parent:
                    raise RuntimeError("Can't get vectors for '{}' since it has no joint hierarchy...")
                else:
                    child = obj
            else:
                child = children[0]
        v = mc.xform(child, q=True, translation=True)

        aim = self.getClosestVector(v)
        up = tuple(dt.Vector(normal).cross(aim))

        jntOrientation = namedtuple('jointOrientation', ['aimV', 'upV'])
        getJntOriention = jntOrientation(aim, up)

        return getJntOriention

    @staticmethod
    def getAxis(vector):
        """
        returns the name of the vector (x,y or z)

        :param tuple vector: a vector
        :rtype: str
        """
        return {
            (1, 0, 0): "x",
            (-1, 0, 0): "-x",
            (0, 1, 0): "y",
            (0, -1, 0): "-y",
            (0, 0, 1): "z",
            (0, 0, -1): "-z",
        }[vector]

