
import maya.OpenMaya as om
import maya.OpenMayaMPx as OpenMayaMPx

import pymel.core as pm
import maya.cmds as mc

CMD_CLASSES = []

class ResetDeltaDeformerNode(OpenMayaMPx.MPxDeformerNode):
    """
    mc.deformer(type='adbResetDeltaDeformer')
    """

    TYPE_NAME = "adbResetDeltaDeformer"
    TYPE_ID = om.MTypeId(0x0007F7FD)

    def __init__(self):
        super(ResetDeltaDeformerNode, self).__init__()

    def deform(self, data_block, geo_iter, matrix, multi_index):

        envelope = data_block.inputValue(self.envelope).asFloat()
        if envelope == 0:
            return

        percentageValue = data_block.inputValue(ResetDeltaDeformerNode.percentageValue).asFloat()
        if percentageValue == 0:
            return

        factorValue = data_block.inputValue(ResetDeltaDeformerNode.factorValue).asFloat()
        if factorValue == 0:
            return

        axisXvalue = data_block.inputValue(ResetDeltaDeformerNode.axisXvalue).asFloat()
        axisYvalue = data_block.inputValue(ResetDeltaDeformerNode.axisYvalue).asFloat()
        axisZvalue = data_block.inputValue(ResetDeltaDeformerNode.axisZvalue).asFloat()

        target_mesh = data_block.inputValue(ResetDeltaDeformerNode.blend_mesh).asMesh()
        if target_mesh.isNull():
            return

        target_points = om.MPointArray()
        target_mesh_fn = om.MFnMesh(target_mesh)
        target_mesh_fn.getPoints(target_points)

        global_weight = (percentageValue/100) * envelope
        _axisXvalue = (axisXvalue/100) * global_weight
        _axisYvalue = (axisYvalue/100) * global_weight
        _axisZvalue = (axisZvalue/100) * global_weight

        mPointArray_meshVert = om.MPointArray()
        geo_iter.reset()
        while not geo_iter.isDone():
            source_pt = geo_iter.position()
            target_pt = target_points[geo_iter.index()]
            source_weight = self.weightValue(data_block, multi_index, geo_iter.index())

            source_pt.x = source_pt.x + ((target_pt.x - source_pt.x) * _axisXvalue * source_weight * factorValue)
            source_pt.y = source_pt.y + ((target_pt.y - source_pt.y) * _axisYvalue * source_weight * factorValue)
            source_pt.z = source_pt.z + ((target_pt.z - source_pt.z) * _axisZvalue * source_weight * factorValue)

            mPointArray_meshVert.append(source_pt)
            geo_iter.next()
        geo_iter.setAllPositions(mPointArray_meshVert)


    @classmethod
    def creator(cls):
        return cls()

    @classmethod
    def initialize(cls):

        typed_attr = om.MFnTypedAttribute()
        cls.blend_mesh = typed_attr.create("blendMesh", "bMesh", om.MFnData.kMesh)

        numeric_attr = om.MFnNumericAttribute()

        cls.percentageValue = numeric_attr.create("percentage", "p", om.MFnNumericData.kFloat, 0.0)
        numeric_attr.setKeyable(True)
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(100.0)

        cls.factorValue = numeric_attr.create("factor", "fa", om.MFnNumericData.kFloat, 1.0)
        numeric_attr.setKeyable(True)
        numeric_attr.setMin(-1.0)
        numeric_attr.setMax(2.0)

        cls.axisXvalue = numeric_attr.create("axisX", "aX", om.MFnNumericData.kFloat, 100.0)
        numeric_attr.setKeyable(True)
        numeric_attr.setMin(-100.0)
        numeric_attr.setMax(100.0)

        cls.axisYvalue = numeric_attr.create("axisY", "aY", om.MFnNumericData.kFloat, 100.0)
        numeric_attr.setKeyable(True)
        numeric_attr.setMin(-100.0)
        numeric_attr.setMax(100.0)

        cls.axisZvalue = numeric_attr.create("axisZ", "aZ", om.MFnNumericData.kFloat, 100.0)
        numeric_attr.setKeyable(True)
        numeric_attr.setMin(-100.0)
        numeric_attr.setMax(100.0)

        cls.addAttribute(cls.blend_mesh)
        cls.addAttribute(cls.factorValue)
        cls.addAttribute(cls.percentageValue)
        cls.addAttribute(cls.axisXvalue)
        cls.addAttribute(cls.axisYvalue)
        cls.addAttribute(cls.axisZvalue)

        output_geom = OpenMayaMPx.cvar.MPxGeometryFilter_outputGeom

        cls.attributeAffects(cls.blend_mesh, output_geom)
        cls.attributeAffects(cls.percentageValue, output_geom)
        cls.attributeAffects(cls.factorValue, output_geom)
        cls.attributeAffects(cls.axisXvalue, output_geom)
        cls.attributeAffects(cls.axisYvalue, output_geom)
        cls.attributeAffects(cls.axisZvalue, output_geom)


class ResetDeltaDeformerCmd(OpenMayaMPx.MPxCommand):
    """
    Create a ResetDelta Deformer

    Keyword Arguments:
        - g / geometry {str} -- Geo on which the deformer is applied
        - s / source {str} -- Source Geo
        - 
    """
    commandName = "createResetDelta"

    HELP_FLAG =['-h', '-help']
    GEOMETRY =['-g', '-geometry', om.MSyntax.kString]
    SOURCE =['-s', '-source', om.MSyntax.kString]
    PERCENTAGE =['-p', '-percentage', om.MSyntax.kString]

    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        self.geo = None
        self.source = None
        self.percentage = None


    def argumentParser(self, argList):
        argData = om.MArgParser(self.syntax(), argList)

        if argData.isFlagSet(ResetDeltaDeformerCmd.HELP_FLAG[0]):
            print (self.__class__.__doc__)
            return None

        if argData.isFlagSet(ResetDeltaDeformerCmd.HELP_FLAG[1]):
            print (self.__class__.__doc__)
            return None

        else:
            if argData.isFlagSet(ResetDeltaDeformerCmd.GEOMETRY[0]):
                self.geo = "{}".format(argData.flagArgumentString(ResetDeltaDeformerCmd.GEOMETRY[0], 0))
            else:
                self.geo = pm.selected()[-1]

            if argData.isFlagSet(ResetDeltaDeformerCmd.GEOMETRY[1]):
                self.geo = "{}".format(argData.flagArgumentString(ResetDeltaDeformerCmd.GEOMETRY[1], 0))
            else:
                self.geo = pm.selected()[-1]

            if argData.isFlagSet(ResetDeltaDeformerCmd.SOURCE[0]):
                self.source = "{}".format(argData.flagArgumentString(ResetDeltaDeformerCmd.SOURCE[0], 0))
            else:
                self.source = pm.selected()[0]

            if argData.isFlagSet(ResetDeltaDeformerCmd.SOURCE[1]):
                self.source = "{}".format(argData.flagArgumentString(ResetDeltaDeformerCmd.SOURCE[1], 0))
            else:
                self.source = pm.selected()[0]

            if argData.isFlagSet(ResetDeltaDeformerCmd.PERCENTAGE[0]):
                self.percentage = "{}".format(argData.flagArgumentString(ResetDeltaDeformerCmd.PERCENTAGE[0], 0))
            else:
                self.percentage = 100

            if argData.isFlagSet(ResetDeltaDeformerCmd.PERCENTAGE[1]):
                self.percentage = "{}".format(argData.flagArgumentString(ResetDeltaDeformerCmd.PERCENTAGE[1], 0))
            else:
                self.percentage = 100



    def isUndoable(self):
        return True


    def undoIt(self):
        pass


    def redoIt(self):
        pm.select(self.geo, r=1)
        deformerNode = pm.deformer(type='adbResetDeltaDeformer')[0]
        shape = pm.PyNode(self.source).getShape()
        pm.connectAttr(shape.worldMesh[0], '{}.blendMesh'.format(deformerNode), f=1)
        pm.setAttr('{}.percentage'.format(deformerNode), int(self.percentage))

    def doIt(self,argList):
        self.argumentParser(argList)
        self.redoIt()


    @classmethod
    def cmdCreator(cls):
        return OpenMayaMPx.asMPxPtr(cls())


    @classmethod
    def syntaxCreator(cls):
        syntax = om.MSyntax()
        syntax.addFlag(*cls.HELP_FLAG)
        syntax.addFlag(*cls.GEOMETRY)
        syntax.addFlag(*cls.SOURCE)
        syntax.addFlag(*cls.PERCENTAGE)
        return syntax


CMD_CLASSES.append(ResetDeltaDeformerCmd)


def initializePlugin(plugin):
    """
    Initialize the script plug-in
    """
    vendor = "Audrey Deschamps-Brower"
    version = "1.0.0"

    plugin_fn = OpenMayaMPx.MFnPlugin(plugin, vendor, version)
    try:
        plugin_fn.registerNode(ResetDeltaDeformerNode.TYPE_NAME,
                               ResetDeltaDeformerNode.TYPE_ID,
                               ResetDeltaDeformerNode.creator,
                               ResetDeltaDeformerNode.initialize,
                               OpenMayaMPx.MPxNode.kDeformerNode)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(ResetDeltaDeformerNode.TYPE_NAME))
    mc.makePaintable(ResetDeltaDeformerNode.TYPE_NAME, "weights", attrType="multiFloat", shapeMode="deformer")

    for cmd in CMD_CLASSES:
        try:
            plugin_fn.registerCommand(cmd.commandName, cmd.cmdCreator, cmd.syntaxCreator)
        except:
            om.MGlobal.displayError("Failed to register node: {}\n".format(cmd.commandName))


def uninitializePlugin(plugin):
    """
    Uninitialize the script plug-in
    """
    plugin_fn = OpenMayaMPx.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterNode(ResetDeltaDeformerNode.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(ResetDeltaDeformerNode.TYPE_NAME))
    mc.makePaintable(ResetDeltaDeformerNode.TYPE_NAME, "weights", remove=True)

    for cmd in CMD_CLASSES:
        try:
            plugin_fn.deregisterCommand(cmd.commandName)
        except:
            om.MGlobal.displayError("Failed to register node: {}\n".format(cmd.commandName))



