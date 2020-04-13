# =====================================================================
# Author : Audrey Deschamps-Brower
#  audreydb23@gmail.com
# =====================================================================


import sys
import maya.OpenMaya as om
import maya.OpenMayaMPx as OpenMayaMPx


nodeName = "adbMath"
nodeId = om.MTypeId(0x100fff)

class adbMath(OpenMayaMPx.MPxNode):
    input1 = om.MObject()
    input2 = om.MObject()
    output = om.MObject()
    mathOption = om.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if plug == adbMath.output:
            _mathOption = dataBlock.inputValue(adbMath.mathOption).asShort()
            dataHandleInput1 = dataBlock.inputArrayValue(adbMath.input1)
            dataHandleInput2 = dataBlock.inputArrayValue(adbMath.input2)
            dataHandleOutput = dataBlock.outputArrayValue(adbMath.output)

            for i in xrange(dataHandleInput1.elementCount()):
                dataHandleInput1.jumpToElement(i)
                inInput1Val = dataHandleInput1.inputValue()

                dataHandleInput2.jumpToElement(i)
                inInput2Val = dataHandleInput2.inputValue()

                if _mathOption == 0:
                    outputVal = inInput1Val.asFloat() * inInput2Val.asFloat()
                elif _mathOption == 1:
                    outputVal = inInput1Val.asFloat() / inInput2Val.asFloat()
                elif _mathOption == 2:
                    outputVal = inInput1Val.asFloat() + inInput2Val.asFloat()
                elif _mathOption == 3:
                    outputVal = inInput1Val.asFloat() - inInput2Val.asFloat()

                dataHandleOutput.jumpToElement(i)
                dataValueOutput = dataHandleOutput.outputValue()
                dataValueOutput.setFloat(outputVal)

            dataBlock.setClean(plug)
        else:
            return om.kUnknownParameter


def nodeCreator():
    return OpenMayaMPx.asMPxPtr( adbMath())

def nodeInitializer():
    # 1. creating a function set for numeric attributes
    mFnAttr = om.MFnNumericAttribute()
    mFnEnumAttr = om.MFnEnumAttribute()
    mFnComp = om.MFnCompoundAttribute()

    # 2. create the attributes
    adbMath.mathOption = mFnEnumAttr.create('operation', 'op', 0)
    mFnEnumAttr.addField('multiply', 0)
    mFnEnumAttr.addField('divide', 1)
    mFnEnumAttr.addField('addition', 2)
    mFnEnumAttr.addField('substraction', 3)

    adbMath.input1 = mFnAttr.create("input1","i1",om.MFnNumericData.kFloat, 0.0)
    mFnAttr.setArray(True)
    mFnAttr.setReadable(1)
    mFnAttr.setWritable(1)
    mFnAttr.setStorable(1)
    mFnAttr.setKeyable(1)

    adbMath.input2 = mFnAttr.create("input2","i2",om.MFnNumericData.kFloat, 0.0)
    mFnAttr.setArray(True)
    mFnAttr.setReadable(1)
    mFnAttr.setWritable(1)
    mFnAttr.setStorable(1)
    mFnAttr.setKeyable(1)

    adbMath.output = mFnAttr.create("output","out",om.MFnNumericData.kFloat)
    mFnAttr.setArray(True)
    mFnAttr.setReadable(1)
    mFnAttr.setWritable(0)
    mFnAttr.setStorable(0)
    mFnAttr.setKeyable(0)

    # 3. Attaching the attributes to the Node
    adbMath.addAttribute(adbMath.mathOption)
    adbMath.addAttribute(adbMath.input1)
    adbMath.addAttribute(adbMath.input2)
    adbMath.addAttribute(adbMath.output)

    # 4. Design circuitry
    adbMath.attributeAffects(adbMath.mathOption, adbMath.output)
    adbMath.attributeAffects(adbMath.input1, adbMath.output)
    adbMath.attributeAffects(adbMath.input2, adbMath.output)


def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Audrey Deschamps-Brower", "1.0.0")
    try:
        mplugin.registerNode(nodeName, nodeId ,nodeCreator, nodeInitializer)
    except:
        sys.stderr.write( "Failed to register command: {} \n".format(nodeName))

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    ''' Uninitializes the plug-in '''
    mplugin = OpenMayaMPx.MFnPlugin( mobject )
    try:
        mplugin.deregisterNode( nodeId )
    except:
        sys.stderr.write( "Failed to deregister node: {} \n".format(nodeName))
