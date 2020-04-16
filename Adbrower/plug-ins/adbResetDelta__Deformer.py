import maya.OpenMaya as om
import maya.OpenMayaMPx as ommpx

import maya.cmds as cmds



class ResetDeltaDeformerNode(ommpx.MPxDeformerNode):

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

        output_geom = ommpx.cvar.MPxGeometryFilter_outputGeom

        cls.attributeAffects(cls.blend_mesh, output_geom)
        cls.attributeAffects(cls.percentageValue, output_geom)
        cls.attributeAffects(cls.factorValue, output_geom)
        cls.attributeAffects(cls.axisXvalue, output_geom)
        cls.attributeAffects(cls.axisYvalue, output_geom)
        cls.attributeAffects(cls.axisZvalue, output_geom)



def initializePlugin(plugin):
    vendor = "Audrey Deschamps-Brower"
    version = "1.0.0"

    plugin_fn = ommpx.MFnPlugin(plugin, vendor, version)
    try:
        plugin_fn.registerNode(ResetDeltaDeformerNode.TYPE_NAME,
                               ResetDeltaDeformerNode.TYPE_ID,
                               ResetDeltaDeformerNode.creator,
                               ResetDeltaDeformerNode.initialize,
                               ommpx.MPxNode.kDeformerNode)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(ResetDeltaDeformerNode.TYPE_NAME))

    cmds.makePaintable(ResetDeltaDeformerNode.TYPE_NAME, "weights", attrType="multiFloat", shapeMode="deformer")


def uninitializePlugin(plugin):
    cmds.makePaintable(ResetDeltaDeformerNode.TYPE_NAME, "weights", remove=True)

    plugin_fn = ommpx.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterNode(ResetDeltaDeformerNode.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(ResetDeltaDeformerNode.TYPE_NAME))


