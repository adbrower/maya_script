import maya.OpenMaya as om
from maya.api import OpenMaya as om2
import maya.OpenMayaMPx as ommpx

import maya.cmds as cmds


class BreathingDeformerNode(ommpx.MPxDeformerNode):

    TYPE_NAME = "adbBreathing"
    TYPE_ID = om.MTypeId(0x103fff)

    def __init__(self):
        super(BreathingDeformerNode, self).__init__()

    def deform(self, data_block, geo_iter, matrix, geometryIndex):
        envelopeValue = data_block.inputValue(self.envelope).asFloat()
        if envelopeValue == 0:
            return

        blend_weight = data_block.inputValue(BreathingDeformerNode.blend_weight).asFloat()
        if blend_weight == 0:
            return

        amplitudeValue = data_block.inputValue(BreathingDeformerNode.amplitudeValue).asFloat()
        if amplitudeValue == 0:
            return

        input = ommpx.cvar.MPxGeometryFilter_input
        ## 1. Attach handle to input Array Attribute
        dataHandleInputArray = data_block.outputArrayValue(input)

        ## 2. Jump to particular element
        dataHandleInputArray.jumpToElement(geometryIndex)

        ## 3. Attach a handle to specific data block
        dataHandleInputElement = dataHandleInputArray.outputValue()

        ## 4.Reach to the child - InputGeom
        inputGeom = ommpx.cvar.MPxGeometryFilter_inputGeom
        dataHandleInputGeom = dataHandleInputElement.child(inputGeom)
        inMesh = dataHandleInputGeom.asMesh()

        global_weight = blend_weight * envelopeValue
        mPointArray_meshVert = om.MPointArray()

        while not geo_iter.isDone():
            pointPosition = geo_iter.position()
            weight = self.weightValue(data_block, geometryIndex, geo_iter.index())
            pointPosition.x  = pointPosition.x + (pointPosition.x  * amplitudeValue * weight * global_weight)
            pointPosition.y  = pointPosition.y + (pointPosition.y  * amplitudeValue * weight * global_weight)
            pointPosition.z  = pointPosition.z + (pointPosition.z  * amplitudeValue * weight * global_weight)
            mPointArray_meshVert.append(pointPosition)
            geo_iter.next()
        geo_iter.setAllPositions(mPointArray_meshVert)


    @classmethod
    def creator(cls):
        return BreathingDeformerNode()

    @classmethod
    def initialize(cls):

        typed_attr = om.MFnTypedAttribute()
        numeric_attr = om.MFnNumericAttribute()
        cls.amplitudeValue = numeric_attr.create("amplitude", "amp", om.MFnNumericData.kFloat, 0.05)
        numeric_attr.setKeyable(True)
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)

        cls.blend_weight = numeric_attr.create("blendWeight", "bWeight", om.MFnNumericData.kFloat, 1.0)
        numeric_attr.setKeyable(True)
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(5.0)

        cls.addAttribute(cls.blend_weight)
        cls.addAttribute(cls.amplitudeValue)

        output_geom = ommpx.cvar.MPxGeometryFilter_outputGeom
        cls.attributeAffects(cls.amplitudeValue, output_geom)
        cls.attributeAffects(cls.blend_weight, output_geom)



def initializePlugin(plugin):
    vendor = "Audrey Deschamps-Brower"
    version = "1.0.0"

    plugin_fn = ommpx.MFnPlugin(plugin, vendor, version)
    try:
        plugin_fn.registerNode(BreathingDeformerNode.TYPE_NAME,
                               BreathingDeformerNode.TYPE_ID,
                               BreathingDeformerNode.creator,
                               BreathingDeformerNode.initialize,
                               ommpx.MPxNode.kDeformerNode)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(BreathingDeformerNode.TYPE_NAME))
    cmds.makePaintable(BreathingDeformerNode.TYPE_NAME, "weights", attrType="multiFloat", shapeMode="deformer")


def uninitializePlugin(plugin):
    cmds.makePaintable(BreathingDeformerNode.TYPE_NAME, "weights", remove=True)

    plugin_fn = ommpx.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterNode(BreathingDeformerNode.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(BreathingDeformerNode.TYPE_NAME))



