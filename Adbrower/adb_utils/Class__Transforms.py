# -------------------------------------------------------------------
# Class Transforms
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# -------------------------------------------------------------------

import pymel.core as pm
import maya.OpenMaya as om
import maya.mel as mel

import adb_utils.Class__AddAttr as adbAttr
from adbrower import flatList
from adbrower import undo

# -----------------------------------
# CLASS
# -----------------------------------


class Transform(adbAttr.NodeAttr):
    """

    """

    def __init__(self,
                 transform=pm.selected()
                 ):

        self.transform = transform
        if isinstance(self.transform, list):
            self.transform = transform
        elif isinstance(self.transform, str):
            self.transform = [transform]
        elif isinstance(self.transform, unicode):
            self.transform = [pm.PyNode(transform)]
        else:
            self.transform = [pm.PyNode(transform)]

        super(Transform, self).__init__(self.transform)

    @classmethod
    def findAll(cls):
        all_transforms = []
        for transf in pm.ls(tr=1):
            all_transforms.append((transf))
        return cls(all_transforms)

    @property
    def getTransform(self):
        return self.transform

    @property
    def pivotPoint(self):
        """
        Change de pivot Point of a subject base values
        """
        pivot_point = [pm.PyNode(x).getRotatePivot() for x in self.transform]
        return pivot_point

    @pivotPoint.setter
    def pivotPoint(self, val):
        """
        Change de pivot Point of a subject base values
        """
        pivot_point = [pm.PyNode(x).setRotatePivot(val) for x in self.transform]
        return

    @property
    def type(self):
        """
        Print selection Type
        """
        all_types = []
        try:
            _type = [(pm.objectType(pm.PyNode(x).getShape())) for x in self.transform]
        except:
            _type = _type = [(pm.objectType(pm.PyNode(x))) for x in self.transform]
        all_types.append(_type)
        return _type

    @property
    def worldTrans(self):
        """
        Get the world Position of the transform

        return List
        """
        pos = [pm.PyNode(x).getRotatePivot(space='world') for x in self.transform]
        return pos

    def setPivotPoint(self, value=[]):
        """
        Change de pivot Point of a subject base values
        """
        [pm.PyNode(x).setRotatePivot(value) for x in self.transform]
        [pm.PyNode(x).setScalePivot(value) for x in self.transform]

    def getAllConns(self):
        """ Print all connections for selected subject """
        oDriver = self.transform[0]
        All_incomingConn = []
        All_DestinationsConn = []
        All_Outputs = []

        print('{} :'.format(oDriver))
        # Incoming Connections
        for DriverSource, DriverDestination in oDriver.inputs(c=1, p=1):
            All_incomingConn.append(DriverDestination)

        if All_incomingConn:
            print('  Incomming Connections Are : ')
            for i, each in enumerate(All_incomingConn):
                print('    {}  {}'.format(i, each))
        else:
            print('  No Incoming Connections')

        for DriverSource, DriverDestination in oDriver.outputs(c=1, p=1):
            All_DestinationsConn.append(DriverDestination)

        # Outputs
        for DriverSource, DriverDestination in oDriver.outputs(c=1, p=1):
            All_Outputs.append(DriverSource)

        if All_Outputs:
            print('  Outputs are : ')
            for i, each in enumerate(All_Outputs):
                print('    {}  {}'.format(i, each))
        else:
            print('  No Outputs')

        # Destinations connections
        if All_DestinationsConn:
            print('  Destinations connections are : ')
            for i, each in enumerate(All_DestinationsConn):
                print('    {}  {}'.format(i, each))
        else:
            print('  No destinations connections')

    def getOutputs(self):
        """
        get outputs from a selection based on the type.
        """
        selection = pm.selected()
        out = flatList([pm.PyNode(x) for x in selection])
        out_shape = flatList([pm.PyNode(x).getShapes() for x in selection])
        all_outs = out + out_shape
        _output = list(set(flatList([x.outputs() for x in all_outs])))

        print(_output)
        return _output

    def matrixConstraint(self,
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
        parent_transform = self.transform[0]

        if isinstance(child, list):
            child = child[0]
        elif isinstance(child, basestring):
            child = child
        elif isinstance(child, unicode):
            child = pm.PyNode(child)

        def getDagPath(node=None):
            sel = om.MSelectionList()
            sel.add(str(node))
            d = om.MDagPath()
            sel.getDagPath(0, d)
            return d

        def getLocalOffset():
            parentWorldMatrix = getDagPath(str(parent_transform)).inclusiveMatrix()
            childWorldMatrix = getDagPath(child).inclusiveMatrix()
            return childWorldMatrix * parentWorldMatrix.inverse()

        mult_matrix = pm.createNode('multMatrix', n='{}_multM'.format(parent_transform))
        dec_matrix = pm.createNode('decomposeMatrix', n='{}_dectM'.format(parent_transform))

        if mo is True:
            localOffset = getLocalOffset()

            # matrix Mult Node CONNECTIONS
            pm.setAttr("{}.matrixIn[0]".format(mult_matrix), [localOffset(i, j) for i in range(4) for j in range(4)], type="matrix")
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
                    pm.PyNode('{}.outputTranslate{}'.format(dec_matrix, axe)) >> pm.PyNode('{}.translate{}'.format(child, axe))
            if channel == 'r':
                for axe in axes:
                    pm.PyNode('{}.outputRotate{}'.format(dec_matrix, axe)) >> pm.PyNode('{}.rotate{}'.format(child, axe))
                pm.PyNode(child).rotateOrder >> pm.PyNode(dec_matrix).inputRotateOrder
                try:
                    pm.PyNode(child).jointOrientX.set(0)
                    pm.PyNode(child).jointOrientY.set(0)
                    pm.PyNode(child).jointOrientZ.set(0)
                except AttributeError:
                    pass
            if channel == 's':
                for axe in axes:
                    pm.PyNode('{}.outputScale{}'.format(dec_matrix, axe)) >> pm.PyNode('{}.scale{}'.format(child, axe))
            if channel == 'h':
                dec_matrix.outputShearX >> pm.PyNode(child).shearXY
                dec_matrix.outputShearY >> pm.PyNode(child).shearXZ
                dec_matrix.outputShearZ >> pm.PyNode(child).shearYZ

        return dec_matrix

    def mirror(self, axis='X'):
        """
        Mirror a transform according to given axis.
        """
        subject = self.transform[0]
        # get the name
        if (pm.PyNode(subject).name()).startswith('r__'):
            _name = '{}'.format(str(subject).replace('r__', 'l__'))

        elif (pm.PyNode(subject).name()).startswith('l__'):
            _name = '{}'.format(str(pm.PyNode(subject)).replace('l__', 'r__'))

        else:
            _name = None

        # temp unlock all user defined attributes
        locks_attr_list = adbAttr.NodeAttr.getLock_attr(subject)
        # Unlock all
        att_to_unlock = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
        for att in att_to_unlock:
            pm.PyNode(subject).setAttr(att, lock=False, keyable=True)

        # mirror function
        dup = pm.duplicate(subject, rr=True, name=_name)[0]
        offset_grp = pm.group(name='dup_grp', em=True)
        pm.makeIdentity(dup, n=0, s=1, r=1, t=1, apply=True, pn=1)
        pm.parent(dup, offset_grp)

        if axis == 'x':
            pm.PyNode(offset_grp).scaleX.set(-1)
        elif axis == 'y':
            pm.PyNode(offset_grp).scaleY.set(-1)
        elif axis == 'z':
            pm.PyNode(offset_grp).scaleZ.set(-1)
        elif axis == 'X':
            pm.PyNode(offset_grp).scaleX.set(-1)
        elif axis == 'Y':
            pm.PyNode(offset_grp).scaleY.set(-1)
        elif axis == 'Z':
            pm.PyNode(offset_grp).scaleZ.set(-1)

        pm.parent(dup, world=True)
        pm.makeIdentity(dup, n=0, s=1, r=1, t=1, apply=True, pn=1)
        pm.delete(offset_grp)

        # relock attribute
        for att in locks_attr_list:
            pm.PyNode(subject).setAttr(att, lock=True, channelBox=True, keyable=False)
            pm.PyNode(dup).setAttr(att, lock=True, channelBox=True, keyable=False)

    @staticmethod
    def get_closest_u_v_point_on_mesh(obj, target_mesh):
        """
        Method that returns the closest u v values of an object on a given mesh
        Args:
            obj: (str) object that is used as reference to get the closest point on the surface
            target_mesh: (str) name of the transform of the mesh.

        Returns:
            list() with the u and v values

        """
        target_mesh_shape = pm.PyNode(target_mesh).getShape()
        closest_point_on_mesh = pm.createNode('closestPointOnMesh', n='{}_CPM'.format(obj))

        target_mesh_shape.matrix >> closest_point_on_mesh.inputMatrix
        target_mesh_shape.outMesh >> closest_point_on_mesh.inMesh
        real_pos = pm.PyNode(obj).getRotatePivot(space='world')

        for pos, i in zip(real_pos, 'XYZ'):
            pm.PyNode('{}.inPosition{}'.format(closest_point_on_mesh, i)).set(pos)
        u_v = [pm.getAttr('{}.r.u'.format(closest_point_on_mesh)), pm.getAttr('{}.r.v'.format(closest_point_on_mesh))]
        pm.delete(closest_point_on_mesh)
        # print u_v
        return u_v

    def iterateHistory(self, plugs=False, node_type=None):
        """
        A generator that parses the history of the shape based on connections. As a result
        you get a depth-only history, without nodes that are connected as blendShape targets or
        other clutter.
        :param str node: deformable shape (or its transform)
        :param bool plugs: list tuples of (input, output) attributes instead of nodes
        :param str node_type: filter the history based on the node type
        :return generator: generator that iterates over history

        ex: skin_clusters = list(adbTransform.Transform(pm.selected()[0]).iterateHistory( node_type='skinCluster'))
        """
        history_plug = (pm.listHistory(self.transform, q=True, historyAttr=True) or [None])[0]
        future_plug = None

        while True:
            if node_type is None or pm.objectType(self.transform, isAType=node_type):
                if plugs:
                    yield history_plug, future_plug
                else:
                    yield self.transform

            if history_plug is None:
                break

            future_plug = (pm.listConnections(history_plug, source=True, destination=False, shapes=True,
                                              skipConversionNodes=False, plugs=True) or [None])[0]
            if future_plug is None:
                break

            self.transform = future_plug.split('.')[0]
            future_attr = '.'.join(future_plug.split('.')[1:])
            history_plug = None
            if pm.objectType(self.transform, isAType='geometryFilter'):
                if future_attr.startswith('outputGeometry['):
                    history_plug = '{0}.{1}.inputGeometry'.format(self.transform, future_attr.replace('outputGeometry', 'input'))
            elif pm.objectType(self.transform, isAType='polyModifier'):
                if future_attr == 'output':
                    history_plug = '{0}.inputPolymesh'.format(self.transform)
            elif pm.objectType(self.transform, isAType='deformableShape'):
                if future_plug in (pm.listHistory(self.transform, q=True, futureLocalAttr=True)[0],
                                   pm.listHistory(self.transform, q=True, futureWorldAttr=True)[0]):
                    history_plug = pm.listHistory(self.transform, q=True, historyAttr=True)[0]
            elif future_attr == 'outputGeometry':
                if pm.objExists('{0}.inputGeometry'.format(self.transform)):
                    history_plug = '{0}.inputGeometry'.format(self.transform)

    def getDeformationOrder(self):
        """
        Return deformation order on a given shape in a list
        """
        deformers = mel.eval('findRelatedDeformer("' + str(self.transform) + '")')
        return deformers

    @undo
    def findBlendShape(self):
        """
        Find the blendShape from a string
        """
        result = []
        if not (pm.objExists(self.transform)):
            return result
        validList = mel.eval('findRelatedDeformer("' + str(self.transform) + '")')
        if validList is None:
            return result

        for elem in validList:
            if pm.nodeType(elem) == 'blendShape':
                result.append(elem)
        return result

