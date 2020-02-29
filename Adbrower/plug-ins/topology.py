# =====================================================================
# Author : Chayan Vinayak
# Copyright Chayan Vinayak
# =====================================================================

import sys
import maya.OpenMaya as om
from maya.api import OpenMaya as om2
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaFX as OpenMayaFX

import pymel.core as pm
import maya.cmds as mc

commandName = "resetDelta"

kHelpFlag = "-h"
kHelpLongFlag = "-help"
kPercentageFlag = "-p"
kPercentageLongFlag = "-percentage"
kAxisFlag = "-ax"
kAxisLongFlag = "-axis"
kPositiveFlag = "-pos"
kPositiveLongFlag = "-positive"
helpMessage = "This command is reset vertex from a mesh to another"

class resetDeltaCmd(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        self.baseGeo = None
        self.targetGeo = None

    def argumentParser(self, argList):
        argData = om.MArgParser(self.syntax(), argList)
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

        if argData.isFlagSet(kHelpFlag):
            self.setResult(helpMessage)

        if argData.isFlagSet(kHelpLongFlag):
            self.setResult(helpMessage)

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

        # Attach a MFnMesh functionSet and set the positions
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
        self.setAllVertexPositions(self.targetGeo, self.delta_vert_positions, worldSpace=False)
    
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

            vert_positions = []
            vert_iter = om2.MItMeshVertex(dag)

            space = om2.MSpace.kObject
            if worldSpace:
                space = om2.MSpace.kWorld

            while not vert_iter.isDone():
                point = vert_iter.position(space)
                vert_positions.append([point[0], point[1], point[2]])
                vert_iter.next()
            return vert_positions

        def _resetDelta(base_geometry, delta_geometry, percentage=1.0, axis = 'xyz', positive=False):  
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
            base_vert_positions = getAllVertexPositions(base_geometry,  worldSpace=False)
            self.delta_vert_positions = getAllVertexPositions(delta_geometry,  worldSpace=False)
            
            if percentage == 0.0:
                return

            if percentage == 1.0:  
                if len(axis) > 2:
                    self.setAllVertexPositions(delta_geometry, base_vert_positions, worldSpace=False)
                else:
                    if axis == 'x':
                        new_pos = []
                        for base, delta in zip(base_vert_positions, self.delta_vert_positions):
                            pos = (base[0], delta[1], delta[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=False)
                        
                    elif axis == 'y':
                        new_pos = []
                        for base, delta in zip(base_vert_positions, self.delta_vert_positions):
                            pos = (delta[0], base[1], delta[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=False)
                            
                    elif axis == 'z':
                        new_pos = []
                        for base, delta in zip(base_vert_positions, self.delta_vert_positions):
                            pos = (delta[0], delta[1], base[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=False)
            else:
                percentage = max(min(percentage, 1.0), 0.0)
                
                if len(axis) > 2:  
                    new_pos= []
                    for delta, base in zip(self.delta_vert_positions, base_vert_positions):
                        vector =  om2.MVector(delta) - om2.MVector(base)
                        vector *= percentage
                        if positive:
                            deltaV = om2.MVector(delta) + vector
                        else:
                            deltaV = om2.MVector(delta) - vector
                        new_pos.append(deltaV)
                    self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=False)

                else:
                    if axis == 'x':
                        new_pos= []
                        for delta, base in zip(self.delta_vert_positions, base_vert_positions):
                            vector =  om2.MVector(delta) - om2.MVector(base)
                            vector *= percentage
                            if positive:
                                deltaV = om2.MVector(delta) + vector
                            else:
                                deltaV = om2.MVector(delta) - vector
                            pos = [deltaV[0], delta[1], delta[2]]
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=False)
                        
                    if axis == 'y':
                        new_pos= []
                        for delta, base in zip(self.delta_vert_positions, base_vert_positions):
                            vector =  om2.MVector(delta) - om2.MVector(base)
                            vector *= percentage
                            if positive:
                                deltaV = om2.MVector(delta) + vector
                            else:
                                deltaV = om2.MVector(delta) - vector
                            pos = [delta[0], deltaV[1], delta[2]]
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=False)
                    
                    if axis == 'z':
                        new_pos= []
                        for delta, base in zip(self.delta_vert_positions, base_vert_positions):
                            vector =  om2.MVector(delta) - om2.MVector(base)
                            vector *= percentage
                            if positive:
                                deltaV = om2.MVector(delta) + vector
                            else:
                                deltaV = om2.MVector(delta) - vector
                            pos = [delta[0], delta[1], deltaV[2]]
                            new_pos.append(pos)

        def _resetDeltaSelection(base_geometry, percentage=1.0, axis ='xyz', positive=False):    
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

            base_vert_positions = getAllVertexPositions(base_geometry,  worldSpace=False)
            self.delta_vert_positions = getAllVertexPositions(delta_geometry,  worldSpace=False)

            mSLmesh = om2.MGlobal.getSelectionListByName(base_geometry).getDependNode(0)
            dag = om2.MFnDagNode(mSLmesh).getPath()

            vertsIter = om2.MItMeshVertex(dag)

            newPosDelta = self.delta_vert_positions[:]
            replacement = []
            while not vertsIter.isDone():
                actual_pos = vertsIter.position(om2.MSpace.kObject)
                vrtxIndex = vertsIter.index()
                if vrtxIndex in indexVtxList: 
                    replacement.append([actual_pos[0], actual_pos[1], actual_pos[2]])
                vertsIter.next()
                
            # replace index with replacement value
            for (index, replace) in zip(indexVtxList, replacement):
                newPosDelta[index] = replace

            if percentage == 0.0:
                return

            if percentage == 1.0:  
                if len(axis) > 2:
                    self.setAllVertexPositions(delta_geometry, newPosDelta, worldSpace=False)
                else:
                    if axis == 'x':
                        new_pos = []
                        for b, delta in zip(self.delta_vert_positions, newPosDelta):
                            pos = (delta[0], b[1], b[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=False)
                        
                    elif axis == 'y':
                        new_pos = []
                        for target, delta in zip(self.delta_vert_positions, newPosDelta):
                            pos = (target[0], delta[1], target[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=False)
                            
                    elif axis == 'z':
                        new_pos = []
                        for target, delta in zip(self.delta_vert_positions, newPosDelta):
                            pos = (target[0], target[1], delta[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=False)
            else:
                percentage = max(min(percentage, 1.0), 0.0)
                if len(axis) > 2:
                    new_pos= []
                    for delta, base in zip(self.delta_vert_positions, newPosDelta):
                        vector =  om2.MVector(delta) - om2.MVector(base)
                        vector *= percentage
                        if positive:
                            deltaV = om2.MVector(delta) + vector
                        else:
                            deltaV = om2.MVector(delta) - vector
                        new_pos.append(deltaV)
                    self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=False)
                else:
                    if axis == 'x':
                        new_pos = []
                        deltaV_pos = []
                        for delta, base in zip(self.delta_vert_positions, newPosDelta):
                            vector =  om2.MVector(delta) - om2.MVector(base)
                            vector *= percentage
                            if positive:
                                deltaV = om2.MVector(delta) + vector
                            else:
                                deltaV = om2.MVector(delta) - vector
                            deltaV_pos.append(deltaV)
                            
                        for target, delta  in zip(self.delta_vert_positions, deltaV_pos):
                            pos = (delta[0], target[1], target[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=False)
                        
                    if axis == 'y':
                        new_pos = []
                        deltaV_pos = []
                        for delta, base in zip(self.delta_vert_positions, newPosDelta):
                            vector =  om2.MVector(delta) - om2.MVector(base)
                            vector *= percentage
                            if positive:
                                deltaV = om2.MVector(delta) + vector
                            else:
                                deltaV = om2.MVector(delta) - vector
                            deltaV_pos.append(deltaV)
                            
                        for target, delta  in zip(self.delta_vert_positions, deltaV_pos):
                            pos = (target[0], delta[1], target[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=False)
                    
                    if axis == 'z':
                        new_pos = []
                        deltaV_pos = []
                        for delta, base in zip(self.delta_vert_positions, newPosDelta):
                            vector =  om2.MVector(delta) - om2.MVector(base)
                            vector *= percentage
                            if positive:
                                deltaV = om2.MVector(delta) + vector
                            else:
                                deltaV = om2.MVector(delta) - vector
                            deltaV_pos.append(deltaV)
                            
                        for target, delta  in zip(self.delta_vert_positions, deltaV_pos):
                            pos = (target[0], target[1], delta[2])
                            new_pos.append(pos)
                        self.setAllVertexPositions(delta_geometry, new_pos, worldSpace=False)

        def resetDelta(base_geometry, delta_geometry, percentage=1.0, axis = 'xyz', positive=False):
            """
            callback _resetDelta into a loop
            """    
            if len(axis) < 3:
                [_resetDelta(base_geometry, delta_geometry, percentage=percentage, axis = letter, positive=positive) for letter in axis]
            else:
                _resetDelta(base_geometry, delta_geometry, percentage=percentage, axis = axis, positive=positive)

        def resetDeltaSelection(base_geometry, percentage=1.0, axis = 'xyz', positive=False):
            """callback _resetDeltaSelection into a loop   
            Arguments:
                base_geometry {str} -- transform on wich we apply the changes
            
            Keyword Arguments:
                percentage {float} -- [description] (default: {1.0})
                axis {str} -- [description] (default: {'xyz'})
                positive {bool} -- [description] (default: {False})
            """
            if len(axis) < 3:
                [_resetDeltaSelection(base_geometry, percentage=percentage, axis = letter, positive=positive) for letter in axis]
            else:
                _resetDeltaSelection(base_geometry, percentage=percentage, axis = axis, positive=positive)

        if not pm.selected():
                resetDelta(self.baseGeo, str(self.targetGeo), percentage=self.percentage, axis =self.axis, positive=self.positive) 
        else:
            sel_type = type(pm.selected()[0])
            if str(sel_type) == "<class 'pymel.core.general.MeshVertex'>":
                resetDeltaSelection(self.baseGeo, percentage=self.percentage, axis=self.axis, positive=self.positive)  
            else:
                resetDelta(self.baseGeo, self.targetGeo, percentage=self.percentage, axis=self.axis, positive=self.positive)


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