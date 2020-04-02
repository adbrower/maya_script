# =====================================================================
# Author : Audrey Deschamps-Brower
#  audreydb23@gmail.com
# =====================================================================

import sys
import time

import maya.OpenMaya as om
from maya.api import OpenMaya as om2
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaFX as OpenMayaFX

import pymel.core as pm
import maya.cmds as mc
import maya.mel

commandName = "resetDelta"

kHelpFlag = "-h"
kHelpLongFlag = "-help"
kPercentageFlag = "-p"
kPercentageLongFlag = "-percentage"
kAxisFlag = "-ax"
kAxisLongFlag = "-axis"
kPositiveFlag = "-pos"
kPositiveLongFlag = "-positive"
kWorldSpaceFlag = "-ws"
kWorldSpaceLongFlag = "-worldSpace"

class gShowProgress(object):
    """
    Based on: http://josbalcaen.com/maya-python-progress-decorator

    Function decorator to show the user (progress) feedback.
    @usage

    import time
    @gShowProgress(end=10)
    def createCubes():
        for i in range(10):
            time.sleep(1)
            if createCubes.isInterrupted(): break
            iCube = mc.polyCube(w=1,h=1,d=1)
            mc.move(i,i*.2,0,iCube)
            createCubes.step()
    """
    def __init__(self, status='Busy...', start=0, end=100, interruptable=True):

        self.mStartValue = start
        self.mEndValue = end
        self.mStatus = status
        self.mInterruptable = interruptable
        self.mMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar')

    def step(self, inValue=1):
        """Increase step
        @param inValue (int) Step value"""
        mc.progressBar(self.mMainProgressBar, edit=True, step=inValue)

    def isInterrupted(self):
        """Check if the user has interrupted the progress
        @return (boolean)"""
        return mc.progressBar(self.mMainProgressBar, query=True, isCancelled=True)

    def start(self):
        """Start progress"""
        mc.waitCursor(state=True)
        mc.progressBar( self.mMainProgressBar,
                edit=True,
                beginProgress=True,
                isInterruptable=self.mInterruptable,
                status=self.mStatus,
                minValue=self.mStartValue,
                maxValue=self.mEndValue
            )
        mc.refresh()

    def end(self):
        """Mark the progress as ended"""
        mc.progressBar(self.mMainProgressBar, edit=True, endProgress=True)
        mc.waitCursor(state=False)

    def __call__(self, inFunction):
        """
        Override call method
        @param inFunction (function) Original function
        @return (function) Wrapped function
        @description
            If there are decorator arguments, __call__() is only called once,
            as part of the decoration process! You can only give it a single argument,
            which is the function object.
        """
        def wrapped_f(*args, **kwargs):
            # Start progress
            self.start()
            # Call original function
            inFunction(*args,**kwargs)
            # End progress
            self.end()

        # Add special methods to the wrapped function
        wrapped_f.step = self.step
        wrapped_f.isInterrupted = self.isInterrupted

        # Copy over attributes
        wrapped_f.__doc__ = inFunction.__doc__
        wrapped_f.__name__ = inFunction.__name__
        wrapped_f.__module__ = inFunction.__module__

        # Return wrapped function
        return wrapped_f

class resetDeltaCmd(OpenMayaMPx.MPxCommand):
    """This command is reset vertex from a mesh to another
    Command Arguments:
        base_geometry {str} -- transform on wich we apply the changes

    Keyword Arguments:
        -p / percentage {float} -- amount of percentage of transformation (default: {1.0})
        - ax / axis {str} -- axis on which transformation will be applied (default: {'xyz'})
        - pos / positive {bool} -- The calculation of the vectors (default: {False})
        - ws / worldSpace {bool} -- world space or Local space (default: {False})
    """
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        self.baseGeo = None
        self.targetGeo = None

    def argumentParser(self, argList):
        argData = om.MArgParser(self.syntax(), argList)

        if argData.isFlagSet(kHelpFlag):
            print self.__class__.__doc__
            return None

        if argData.isFlagSet(kHelpLongFlag):
            print self.__class__.__doc__
            return None

        else:
            self.baseGeo = argData.commandArgumentString(0)
            try:
                self.targetGeo = argData.commandArgumentString(1)
            except RuntimeError:
                selList =om2.MGlobal.getActiveSelectionList()
                self.targetGeo = selList.getSelectionStrings(0)[0]

            if argData.isFlagSet(kPercentageFlag):
                self.percentage = argData.flagArgumentDouble(kPercentageFlag, 0)
            else:
                self.percentage = 1.0

            if argData.isFlagSet(kPercentageLongFlag):
                self.percentage = argData.flagArgumentDouble(kPercentageLongFlag, 0)
            else:
                self.percentage = 1.0

            if argData.isFlagSet(kAxisFlag):
                self.axis = "{}".format(argData.flagArgumentString(kAxisFlag, 0))
            else:
                self.axis = 'xyz'

            if argData.isFlagSet(kAxisLongFlag):
                self.axis = "{}".format(argData.flagArgumentString(kAxisLongFlag, 0))
            else:
                self.axis = 'xyz'

            if argData.isFlagSet(kPositiveFlag):
                self.positive = argData.flagArgumentBool(kPositiveFlag, 0)
            else:
                self.positive = False

            if argData.isFlagSet(kPositiveLongFlag):
                self.positive = argData.flagArgumentBool(kPositiveLongFlag, 0)
            else:
                self.positive = False

            if argData.isFlagSet(kWorldSpaceFlag):
                self.ws = argData.flagArgumentBool(kWorldSpaceFlag, 0)
            else:
                self.ws = False

            if argData.isFlagSet(kWorldSpaceLongFlag):
                self.ws = argData.flagArgumentBool(kWorldSpaceLongFlag, 0)
            else:
                self.ws = False

    def getSoftSelection(self):
        softSelectDict = {}

        softSelection = om2.MGlobal.getRichSelection()
        richSelection = om2.MRichSelection(softSelection)
        richeSelectionList = richSelection.getSelection()
        component =  richeSelectionList.getComponent(0)

        componentIndex = om2.MFnSingleIndexedComponent(component[1])
        vertexList =  componentIndex.getElements()

        for loop in xrange(len(vertexList)):
            weight = componentIndex.weight(loop)
            softSelectDict[vertexList[loop]] = float(format(weight.influence, '.5f'))

        return softSelectDict

    def setAllVertexPositions(self, geoObj, positions=[], worldSpace=True):
        """
        Set all vertex of a mesh from a list
        """
        mPoint = om2.MPointArray(positions)
        mSpace = None

        if worldSpace == True:
            mSpace = om.MSpace.kWorld
        else:
            mSpace = om.MSpace.kObject

        mSL = om2.MSelectionList()
        mSL.add(geoObj)

        mFnSet = om2.MFnMesh(mSL.getDagPath(0))
        mFnSet.setPoints(mPoint, mSpace)

    def isUndoable(self):
        return True

    def undoIt(self):
        """
        Reset target geo's vertex to initial position
        """
        self.setAllVertexPositions(self.targetGeo, self.delta_vert_positions.values(), worldSpace=self.ws)


    def redoIt(self):
        def getAllVertexPositions(geometry, worldSpace=True):
            """
            Get All Vertex Position from a mesh

            Arguments:
                geometry {str} -- Mesh

            Keyword Arguments:
                worldSpace {bool} -- (default: {True})

            Returns:
                List -- All vertex positions
            """
            mSLmesh = om2.MGlobal.getSelectionListByName(geometry).getDependNode(0)
            dag = om2.MFnDagNode(mSLmesh).getPath()

            vert_positions = {}
            vert_iter = om2.MItMeshVertex(dag)

            space = om2.MSpace.kObject
            if worldSpace:
                space = om2.MSpace.kWorld

            while not vert_iter.isDone():
                point = vert_iter.position(space)
                vrtxIndex = vert_iter.index()
                vert_positions[vrtxIndex] = [point[0], point[1], point[2]]
                vert_iter.next()
            return vert_positions

        def _resetDelta(base_geometry, delta_geometry, percentage=1.0, axis = 'xyz', positive=False, worldSpace=False):
            """Reset the vertex position between a BASE mesh and a TARGET mesh.

            Arguments:
                base_geometry {str} -- Mesh to which the target is taking vertex position (default Mesh)
                delta_geometry {str} -- Mesh getting the new vertex position (Usually Shapes / Sculpt)

            Keyword Arguments:
                percentage {float} -- Amount of % the vertex position is blending. Between 0.0 and 1.0 (default: {1.0})
                axis {str} --  On Which axis the vertex are moving (default: {'xyz'})
                positive {bool} -- The deformation is expanding. False: The deformation is resetting towards the BASE  mesh
                                    (default: {False})
            """
            base_vert_positions = getAllVertexPositions(base_geometry,  worldSpace=worldSpace)
            self.delta_vert_positions = getAllVertexPositions(delta_geometry,  worldSpace=worldSpace)

            if percentage == 0.0:
                return

            if percentage == 1.0:
                if len(axis) > 2:
                    self.setAllVertexPositions(delta_geometry, base_vert_positions.values(), worldSpace=worldSpace)
                else:
                    if axis == 'x':
                        new_pos = []
                        for base, delta in zip(base_vert_positions.values(), self.delta_vert_positions.values()):
                            pos = (base[0], delta[1], delta[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=worldSpace)

                    elif axis == 'y':
                        new_pos = []
                        for base, delta in zip(base_vert_positions.values(), self.delta_vert_positions.values()):
                            pos = (delta[0], base[1], delta[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=worldSpace)

                    elif axis == 'z':
                        new_pos = []
                        for base, delta in zip(base_vert_positions.values(), self.delta_vert_positions.values()):
                            pos = (delta[0], delta[1], base[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=worldSpace)
            else:
                percentage = max(min(percentage, 1.0), 0.0)

                if len(axis) > 2:
                    new_pos= []
                    for delta, base in zip(self.delta_vert_positions.values(), base_vert_positions.values()):
                        vector =  om2.MVector(delta) - om2.MVector(base)
                        vector *= percentage
                        if positive:
                            deltaV = om2.MVector(delta) + vector
                        else:
                            deltaV = om2.MVector(delta) - vector
                        new_pos.append(deltaV)
                    self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=worldSpace)

                else:
                    if axis == 'x':
                        new_pos= []
                        for delta, base in zip(self.delta_vert_positions.values(), base_vert_positions.values()):
                            vector =  om2.MVector(delta) - om2.MVector(base)
                            vector *= percentage
                            if positive:
                                deltaV = om2.MVector(delta) + vector
                            else:
                                deltaV = om2.MVector(delta) - vector
                            pos = [deltaV[0], delta[1], delta[2]]
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=worldSpace)

                    if axis == 'y':
                        new_pos= []
                        for delta, base in zip(self.delta_vert_positions.values(), base_vert_positions.values()):
                            vector =  om2.MVector(delta) - om2.MVector(base)
                            vector *= percentage
                            if positive:
                                deltaV = om2.MVector(delta) + vector
                            else:
                                deltaV = om2.MVector(delta) - vector
                            pos = [delta[0], deltaV[1], delta[2]]
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=worldSpace)

                    if axis == 'z':
                        new_pos= []
                        for delta, base in zip(self.delta_vert_positions.values(), base_vert_positions.values()):
                            vector =  om2.MVector(delta) - om2.MVector(base)
                            vector *= percentage
                            if positive:
                                deltaV = om2.MVector(delta) + vector
                            else:
                                deltaV = om2.MVector(delta) - vector
                            pos = [delta[0], delta[1], deltaV[2]]
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=worldSpace)


        @gShowProgress(status="Reset Selection ...")
        def _resetDeltaSelection(base_geometry, percentage=1.0, axis ='xyz', positive=False, worldSpace=False):
            """
            Reset the vertex position between a BASE mesh and a TARGET mesh based on vertex selection

            Arguments:
                base_geometry {str} -- Mesh to which the target is taking vertex position (default Mesh)

            Keyword Arguments:
                percentage {float} -- Amount of % the vertex position is blending. Between 0.0 and 1.0 (default: {1.0})
                axis {str} -- On Which axis the vertex are moving (default: {'xyz'})
                positive {bool} -- The deformation is expanding. False: The deformation is resetting towards the BASE mesh  (default: {False})
            """
            selectionVtx = mc.ls(sl=1, flatten=1)
            delta_geometry = selectionVtx[0].split('.vtx')[0]
            indexVtxList = [int(x.split('[')[-1].split(']')[0]) for x in selectionVtx]

            base_vert_positions = getAllVertexPositions(base_geometry,  worldSpace=worldSpace)
            self.delta_vert_positions = getAllVertexPositions(delta_geometry,  worldSpace=worldSpace)

            mSLmesh = om2.MGlobal.getSelectionListByName(base_geometry).getDependNode(0)
            dag = om2.MFnDagNode(mSLmesh).getPath()

            vertsIter = om2.MItMeshVertex(dag)

            if mc.softSelect(q=1, sse=1):
                softSelect = self.getSoftSelection()
                softIndex = softSelect.keys()
                indexVtxList = softIndex
            else:
                softIndex = []

            newPosDelta = self.delta_vert_positions.values()[:]
            replacement = {}

            _step = float(100) / vertsIter.count()
            if _resetDeltaSelection.isInterrupted(): return

            while not vertsIter.isDone():
                actual_pos = vertsIter.position(om2.MSpace.kObject)
                vrtxIndex = vertsIter.index()

                if vrtxIndex in softIndex:
                    vector =  om2.MVector(self.delta_vert_positions[vrtxIndex]) - om2.MVector(base_vert_positions[vrtxIndex])
                    vector*= softSelect[vrtxIndex]
                    deltaV = list(om2.MVector(self.delta_vert_positions[vrtxIndex]) - vector)
                    replacement[vrtxIndex] = deltaV

                    _resetDeltaSelection.step(_step)

                elif vrtxIndex in indexVtxList:
                    replacement[vrtxIndex] = actual_pos

                    _resetDeltaSelection.step(_step)

                vertsIter.next()

            # replace index with replacement value
            for (index, replace) in zip(replacement.keys(), replacement.values()):
                newPosDelta[index] = replace

            if percentage == 0.0:
                return

            if percentage == 1.0:
                if len(axis) > 2:
                    self.setAllVertexPositions(delta_geometry, newPosDelta, worldSpace=worldSpace)
                else:
                    if axis == 'x':
                        new_pos = []
                        for b, delta in zip(self.delta_vert_positions.values(), newPosDelta):
                            pos = (delta[0], b[1], b[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=worldSpace)

                    elif axis == 'y':
                        new_pos = []
                        for target, delta in zip(self.delta_vert_positions.values(), newPosDelta):
                            pos = (target[0], delta[1], target[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=worldSpace)

                    elif axis == 'z':
                        new_pos = []
                        for target, delta in zip(self.delta_vert_positions.values(), newPosDelta):
                            pos = (target[0], target[1], delta[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=worldSpace)
            else:
                percentage = max(min(percentage, 1.0), 0.0)
                if len(axis) > 2:
                    new_pos= []
                    for delta, base in zip(self.delta_vert_positions.values(), newPosDelta):
                        vector =  om2.MVector(delta) - om2.MVector(base)
                        vector *= percentage
                        if positive:
                            deltaV = om2.MVector(delta) + vector
                        else:
                            deltaV = om2.MVector(delta) - vector
                        new_pos.append(deltaV)
                    self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=worldSpace)
                else:
                    if axis == 'x':
                        new_pos = []
                        deltaV_pos = []
                        for delta, base in zip(self.delta_vert_positions.values(), newPosDelta):
                            vector =  om2.MVector(delta) - om2.MVector(base)
                            vector *= percentage
                            if positive:
                                deltaV = om2.MVector(delta) + vector
                            else:
                                deltaV = om2.MVector(delta) - vector
                            deltaV_pos.append(deltaV)

                        for target, delta  in zip(self.delta_vert_positions.values(), deltaV_pos):
                            pos = (delta[0], target[1], target[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=worldSpace)

                    if axis == 'y':
                        new_pos = []
                        deltaV_pos = []
                        for delta, base in zip(self.delta_vert_positions.values(), newPosDelta):
                            vector =  om2.MVector(delta) - om2.MVector(base)
                            vector *= percentage
                            if positive:
                                deltaV = om2.MVector(delta) + vector
                            else:
                                deltaV = om2.MVector(delta) - vector
                            deltaV_pos.append(deltaV)

                        for target, delta  in zip(self.delta_vert_positions.values(), deltaV_pos):
                            pos = (target[0], delta[1], target[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=worldSpace)

                    if axis == 'z':
                        new_pos = []
                        deltaV_pos = []
                        for delta, base in zip(self.delta_vert_positions.values(), newPosDelta):
                            vector =  om2.MVector(delta) - om2.MVector(base)
                            vector *= percentage
                            if positive:
                                deltaV = om2.MVector(delta) + vector
                            else:
                                deltaV = om2.MVector(delta) - vector
                            deltaV_pos.append(deltaV)

                        for target, delta  in zip(self.delta_vert_positions.values(), deltaV_pos):
                            pos = (target[0], target[1], delta[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=worldSpace)

        def resetDelta(base_geometry, delta_geometry, percentage=1.0, axis = 'xyz', positive=False, worldSpace=False):
            """
            callback _resetDelta into a loop
            """
            if len(axis) < 3:
                [_resetDelta(base_geometry, delta_geometry, percentage=percentage, axis = letter, positive=positive, worldSpace=worldSpace) for letter in axis]
            else:
                _resetDelta(base_geometry, delta_geometry, percentage=percentage, axis = axis, positive=positive, worldSpace=worldSpace)

        def resetDeltaSelection(base_geometry, percentage=1.0, axis = 'xyz', positive=False, worldSpace=False):
            """callback _resetDeltaSelection into a loop
            Arguments:
                base_geometry {str} -- transform on wich we apply the changes

            Keyword Arguments:
                percentage {float} -- [description] (default: {1.0})
                axis {str} -- [description] (default: {'xyz'})
                positive {bool} -- [description] (default: {False})
            """
            if len(axis) < 3:
                [_resetDeltaSelection(base_geometry, percentage=percentage, axis = letter, positive=positive, worldSpace=worldSpace) for letter in axis]
            else:
                _resetDeltaSelection(base_geometry, percentage=percentage, axis = axis, positive=positive, worldSpace=worldSpace)

        #===========================
        # DO IT
        #===========================

        if not pm.selected():
            resetDelta(self.baseGeo, str(self.targetGeo), percentage=self.percentage, axis =self.axis, positive=self.positive, worldSpace=self.ws)
        else:
            sel_type = type(pm.selected()[0])
            if str(sel_type) == "<class 'pymel.core.general.MeshFace'>":
                maya.mel.eval('PolySelectConvert 3')
                resetDeltaSelection(self.baseGeo, percentage=self.percentage, axis=self.axis, positive=self.positive, worldSpace=self.ws)

            elif str(sel_type) == "<class 'pymel.core.general.MeshEdge'>":
                maya.mel.eval('PolySelectConvert 3')
                resetDeltaSelection(self.baseGeo, percentage=self.percentage, axis=self.axis, positive=self.positive, worldSpace=self.ws)

            elif str(sel_type) == "<class 'pymel.core.general.MeshVertex'>":
                resetDeltaSelection(self.baseGeo, percentage=self.percentage, axis=self.axis, positive=self.positive, worldSpace=self.ws)
            else:
                resetDelta(self.baseGeo, self.targetGeo, percentage=self.percentage, axis=self.axis, positive=self.positive, worldSpace=self.ws)


    def doIt(self,argList):
        self.argumentParser(argList)
        if self.baseGeo is not None:
            self.redoIt()


def cmdCreator():
    return OpenMayaMPx.asMPxPtr(resetDeltaCmd())


def syntaxCreator():
	syntax = om.MSyntax()
	syntax.addFlag(kHelpFlag, kHelpLongFlag)
	syntax.addFlag(kPercentageFlag, kPercentageLongFlag, om.MSyntax.kDouble)
	syntax.addFlag(kAxisFlag, kAxisLongFlag, om.MSyntax.kString)
	syntax.addFlag(kPositiveFlag, kPositiveLongFlag, om.MSyntax.kBoolean)
	syntax.addFlag(kWorldSpaceFlag, kWorldSpaceLongFlag, om.MSyntax.kBoolean)
	syntax.addArg(om.MSyntax.kString)
	syntax.addArg(om.MSyntax.kString)
	return syntax


#====================
# INITIALIZING THE PLUG-IN
#====================

def initializePlugin(mobject):
    """
    Initialize the script plug-in
    """
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand(commandName, cmdCreator, syntaxCreator)
    except:
        sys.stderr.write( "Failed to register command: {}\n".format(commandName))


def uninitializePlugin(mobject):
    """
    Uninitialize the script plug-in
    """
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(commandName)
    except:
        sys.stderr.write( "Failed to unregister command: {}\n".format(commandName))



#====================
# BUILD
#====================


# mc.unloadPlugin("resetDelta.py")
# mc.loadPlugin("resetDelta.py", qt=True)