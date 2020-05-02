# -------------------------------------------------------------------
# SPACE SWITCH SYSTEM
# -- Version 2.0.0
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# -------------------------------------------------------------------


import pymel.core as pm
import maya.OpenMaya as om

import adb_core.Class__AddAttr as adbAttr


class SpaceSwitch(object):
    """
    import adb_library.adb_modules.Class__SpaceSwitch as SpaceSwitch
    
    SpaceSwitch.SpaceSwitch('PV', 
                  spacesInputs =['World', 'L__Leg_IK_offset__CTRL'], 
                  spaceOutput ='L__Leg_pv_root__GRP', 
                  maintainOffset = True,
                  attrNames = ['world', 'ik'],)
    """
    def __init__(self,
                spaceSwtichName,
                spacesInputs = [],
                spaceOutput = None,
                maintainOffset = False,
                worldSpace = True,
                attrNames = []
                ):

        self.NAME = spaceSwtichName
        self.spacesInputs = spacesInputs
        self.spaceOutput = spaceOutput
        self.maintainOffset = maintainOffset
        self.worldSpace = worldSpace
        self.attrNames = attrNames

        self.create()
        self.metaData_GRP = self.createNetworkNode()


    def create(self):
        self.choiceNode = pm.shadingNode('choice', au=1, n='{}__CH'.format(self.NAME))

        if self.worldSpace:
            for i, space in enumerate(self.spacesInputs):
                pm.PyNode('{}.worldMatrix[0]'.format(space)) >> pm.PyNode('{}.input[{}]'.format(self.choiceNode, i))
        else:
            for i, space in enumerate(self.spacesInputs):
                pm.PyNode('{}.Matrix[0]'.format(space)) >> pm.PyNode('{}.input[{}]'.format(self.choiceNode, i))

        self.matrixConstraint(str(self.choiceNode), self.spaceOutput, mo=self.maintainOffset)

        return self.choiceNode


    def createNetworkNode(self):
        spaceAttrNode = pm.shadingNode('network', asUtility=1, n='{}_attribute___network'.format(self.NAME))
        spaceAttr = adbAttr.NodeAttr(spaceAttrNode)
        spaceAttr.addAttr('Spaces',  'enum',  eName = str(':'.join(self.attrNames)))

        pm.PyNode('{}.{}'.format(spaceAttrNode , spaceAttr.attrName)) >> self.choiceNode.selector

        return spaceAttrNode


    def matrixConstraint(self,
                         parent_transform,
                         child,
                         channels='t',
                         mo=True
                         ):

            def getDagPath(node=None):
                sel = om.MSelectionList()
                sel.add(node)
                d = om.MDagPath()
                sel.getDagPath(0, d)
                return d

            def getLocalOffset(parent, child):
                parentWorldMatrix = getDagPath(str(parent)).inclusiveMatrix()
                childWorldMatrix = getDagPath(str(child)).inclusiveMatrix()
                return childWorldMatrix * parentWorldMatrix.inverse()

            mult_matrix = pm.createNode(
                'multMatrix', n='{}_multM'.format(parent_transform))
            dec_matrix = pm.createNode(
                'decomposeMatrix', n='{}_dectM'.format(parent_transform))

            if mo is True:
                self.choiceNodeOffset = pm.shadingNode('choice', au=1, n='{}Offset__CH'.format(self.NAME))
                for index, each in enumerate(self.spacesInputs):
                    mult_matrixOffset = pm.createNode(
                    'multMatrix', n='{}Offset_multM'.format(each))
                    mult_matrixOffset.matrixSum >> self.choiceNodeOffset.input[index]
                    localOffset = getLocalOffset(str(each), str(self.spaceOutput))

                    pm.setAttr("{}.matrixIn[0]".format(mult_matrixOffset), [localOffset(
                        i, j) for i in range(4) for j in range(4)], type="matrix")

                self.choiceNodeOffset.output >> mult_matrix.matrixIn[0]
                self.choiceNode.output >> mult_matrix.matrixIn[1]
                
                mult_matrix.matrixSum >> dec_matrix.inputMatrix
                pm.PyNode(child).parentInverseMatrix >> mult_matrix.matrixIn[2]

            else:
                pm.PyNode(parent_transform).output >> mult_matrix.matrixIn[0]
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



