# ----------------------------------------------------------------------------------------------
# INITALLY FROM:
#       transferSkinCluster.py
#       v1.43 (160430)
#
#       export/import weights of the selected skinCluster
#
#       Ingo Clemens
#       www.braverabbit.com
#
#       Copyright brave rabbit, Ingo Clemens 2012-2015
#       All rights reserved.
# 
# 
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
#
#     I modified the script for my needs
# ----------------------------------------------------------------------------------------------

import os

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaAnim as OpenMayaAnim

import maya.cmds as cmds
import maya.mel as mel

kPluginCmdName = 'manageSkinCluster'

# --------------------------------------------------------------------------------
# argument flags
# --------------------------------------------------------------------------------

helpFlag = '-h'
helpFlagLong = '-help'

fileFlag = '-f'
fileFlagLong = '-file'

modeFlag = '-m'
modeFlagLong = '-mode'

orderFlag = '-ro'
orderFlagLong = '-reverseOrder'

exclusiveFlag = '-ex'
exclusiveFlagLong = '-exclusive'

helpText = ''
helpText += '\n Description: The command exports and imports the selected skinCluster to/from a file.'
helpText += '\n'
helpText += '\n Flags: manageSkinCluster   -h    -help          <n/a>       this message'
helpText += '\n                            -m    -mode          <int>       write (default=0) or read (1)'
helpText += '\n                            -ro   -reverseOrder  <int>       from file (default=0) or reversed (1)'
helpText += '\n                            -f    -file          <string>    the file name for the skinCluster weight data'
helpText += '\n                            -ex   -exclusive     <int>       stores the weight for each influence to a separate file'
helpText += '\n'
helpText += '\n Usage:   Execute the command with the following arguments:'
helpText += '\n Execute: manageSkinCluster -m <mode> -f <file name>;';


# --------------------------------------------------------------------------------
# command
# --------------------------------------------------------------------------------

class transferSkinCluster(OpenMayaMPx.MPxCommand):

    def __init__( self ):
        OpenMayaMPx.MPxCommand.__init__(self)

    def doIt( self, args ):
        modeArg = 0
        fileName = ''
        orderArg = 0
        exclusiveArg = 0

        # parse the arguments.
        argData = OpenMaya.MArgDatabase(self.syntax(), args)

        if argData.isFlagSet(helpFlag):
            self.setResult(helpText)
            return()

        if argData.isFlagSet(modeFlag):
            modeArg = argData.flagArgumentDouble(modeFlag, 0)
        if argData.isFlagSet(orderFlag):
            orderArg = argData.flagArgumentDouble(orderFlag, 0)
        if argData.isFlagSet(exclusiveFlag):
            exclusiveArg = argData.flagArgumentDouble(exclusiveFlag, 0)
        if argData.isFlagSet(fileFlag):
            fileName = argData.flagArgumentString(fileFlag, 0)
        else:
            OpenMaya.MGlobal.displayError(kPluginCmdName + ' needs file name flag.')
            return();

        if fileName == '':
            OpenMaya.MGlobal.displayError(kPluginCmdName + ' file name is not specified.')
            return()

        if modeArg < 0 or modeArg > 1:
            OpenMaya.MGlobal.displayError(kPluginCmdName + ' mode needs to be set to either 0 for \'write\' or 1 for \'read\'.')
            return()

        start = cmds.timerX()
        msgString = ''

        result = 0
        if modeArg == 0:
            result = self.writeWeights(fileName, exclusiveArg)
            msgString = 'exported to '
        else:
            result = self.readWeights(fileName, orderArg)
            msgString = 'imported from '

        doneTime = cmds.timerX(startTime = start)
        if result == 1:
            OpenMaya.MGlobal.displayInfo('transferSkinCluster command took %.02f seconds' % doneTime)
            OpenMaya.MGlobal.displayInfo('Weights ' + msgString + '\'' + fileName + '\'')


    # --------------------------------------------------------------------------------
    # write the weights file
    # --------------------------------------------------------------------------------

    def writeWeights( self, fileName, exclusive ):

        # get the current selection
        skinClusterNode = cmds.ls(sl = True, fl = True)
        if len(skinClusterNode) != 0:
                skinClusterNode = skinClusterNode[0]
        else:
            OpenMaya.MGlobal.displayError('Select a skinCluster node to export.')
            return(-1)

        # check if it's a skinCluster
        if cmds.nodeType(skinClusterNode) != 'skinCluster':
            OpenMaya.MGlobal.displayError('Selected node is not a skinCluster.')
            return(-1)

        # get the MFnSkinCluster
        sel = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(sel)
        skinClusterObject = OpenMaya.MObject()
        sel.getDependNode(0, skinClusterObject)
        skinClusterFn = OpenMayaAnim.MFnSkinCluster(skinClusterObject)

        # get the influence objects
        infls = cmds.skinCluster(skinClusterNode, q = True, inf = True)
        if len(infls) == 0:
            OpenMaya.MGlobal.displayError('No influence objects found for skinCluster %s.' % skinClusterNode)
            return(-1)

        # get the connected shape node
        shape = cmds.skinCluster(skinClusterNode, q = True, g = True)[0]
        if len(shape) == 0:
            OpenMaya.MGlobal.displayError('No connected shape nodes found.')
            return(-1)

        # get the dag path of the shape node
        cmds.select(shape, r = True)
        sel = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(sel)
        shapeDag = OpenMaya.MDagPath()
        sel.getDagPath(0, shapeDag)
        # create the geometry iterator
        geoIter = OpenMaya.MItGeometry(shapeDag)

        # create a pointer object for the influence count of the MFnSkinCluster
        infCount = OpenMaya.MScriptUtil()
        infCountPtr = infCount.asUintPtr()
        OpenMaya.MScriptUtil.setUint(infCountPtr, 0)

        value = OpenMaya.MDoubleArray()

        #----------------------------------------------------
        # default export to a single skin weights file
        #----------------------------------------------------
        if not exclusive:
            try:
                weightFile = open(fileName, 'wb')
            except:
                OpenMaya.MGlobal.displayError('A file error has occured for file \'' + fileName + '\'.')
                return(-1)

            # write all influences and the shape node to the file
            for i in range(0, len(infls), 1):
                weightFile.write(infls[i] + " ")
            weightFile.write(shape + '\n')

            weightFile.write(skinClusterNode + '\n')

            # write the attributes of the skinCluster node to the file
            result = cmds.getAttr(skinClusterNode + ".normalizeWeights")
            weightFile.write('-nw %s ' % result)
            result = cmds.getAttr(skinClusterNode + ".maxInfluences")
            weightFile.write('-mi %s ' % result)
            result = cmds.getAttr(skinClusterNode + ".dropoff")[0][0]
            weightFile.write('-dr %s\n' % result)

            # get the skinCluster weights
            while geoIter.isDone() == False:
                skinClusterFn.getWeights(shapeDag, geoIter.currentItem(), value, infCountPtr)
                for j in range(0, len(infls)):
                    if value[j] > 0:
                        lineArray = [geoIter.index(), infls[j], j, value[j]]
                        weightFile.write(str(lineArray) + '\n')
                geoIter.next()
            weightFile.close()

        # ------------------------------------
        # custom export to individual files
        # ------------------------------------
        else:
            cmds.skinCluster(skinClusterNode, e = True, fnw = True);
            dataPath = '%s/%s' % (fileName, skinClusterNode)
            if not os.path.exists(dataPath):
                try:
                    os.makedirs(dataPath)
                except:
                    OpenMaya.MGlobal.displayError('Unable to create export directory \'' + dataPath + '\'.')
                    return(-1)

            for j in range(0, len(infls)):
                fileName = '%s/%s.bsw' % (dataPath, infls[j])
                try:
                    weightFile = open(fileName, 'wb')
                except:
                    OpenMaya.MGlobal.displayError('A file error has occured for file \'' + fileName + '\'.')
                    return(-1)
                geoIter.reset()

                while geoIter.isDone() == False:
                    skinClusterFn.getWeights(shapeDag, geoIter.currentItem(), value, infCountPtr)
                    line = str(geoIter.index()) + ' ' + str(value[j]) + '\n'
                    weightFile.write(line)
                    geoIter.next()
                weightFile.close()
        return(1)

    # --------------------------------------------------------------------------------
    # read the weights file
    # --------------------------------------------------------------------------------

    @staticmethod
    def getSkinCluster(_transform):
        """
        Find a SkinCluster from a transform
        Returns the skinCluster node
        """
        result = []
        if not (cmds.objExists(_transform)):
            return result
        validList = mel.eval('findRelatedDeformer("' + str(_transform) + '")')
        if validList is None:
            return result
        for elem in validList:
            if cmds.nodeType(elem) == 'skinCluster':
                result.append(elem)
        cmds.select(result, r=True)
        result_node = cmds.ls(sl=1)
        
        if len(result_node) > 1:
            return str(result_node)
        else:
            try:
                return str(result_node[0])
            except IndexError:
                return False


    def readWeights(self, fileName, reverseOrder):
        # open the file for reading
        try:
            weightFile = open(fileName, 'rb')
        except:
            OpenMaya.MGlobal.displayError('A file error has occured for file \'' + fileName + '\'.')
            return(-1)

        weightData = weightFile.read()
        weightLines = weightData.split('\n')
        weightFile.close()

        normalization = 1

        # variables for writing a range of influences
        weightString = ''
        inflStart = -1
        inflEnd = -1
        setCount = 0
        writeData = 0

        # --------------------------------------------------------------------------------
        # the first line contains the joints and skin shape
        # --------------------------------------------------------------------------------
        objects = weightLines[0]
        items = objects.split(' ')
        shape = items[len(items) - 1]

        # --------------------------------------------------------------------------------
        # the second line contains the name of the skin cluster
        # --------------------------------------------------------------------------------
        skinClusterName = weightLines[1]

        # --------------------------------------------------------------------------------
        # the third line contains the values for the skin cluster
        # --------------------------------------------------------------------------------
        objects = objects.split(' ')
        if reverseOrder == 1:
            objects = objects[::-1]
            objects.pop(0)
            objects.append(shape)

        # check for the version
        # up to Maya 2012 the bind method flag is not available
        version = mel.eval('getApplicationVersionAsFloat()')
        bindMethod = '-bm 0 '
        if version < 2013:
            bindMethod = '-ih '

        # create the new skinCluster
        original_skinCls = self.getSkinCluster(shape)
        if original_skinCls is not False:
            try:
                cmds.skinCluster(cmds.listRelatives(shape, parent=1)[0], e=1, ub=1)
            except:
                pass

        # select the influences and the skin shape
        try:
            cmds.select(objects, r = True)
        except:
            weightFile.close()
            return()    
        newSkinCluster = mel.eval('newSkinCluster \"-tsb ' + bindMethod + weightLines[2] + '-omi true -rui false\"')[0]
        cmds.rename(newSkinCluster, skinClusterName)

        # get the current normalization and store it
        # it will get re-applied after applying all the weights
        normalization = cmds.getAttr(skinClusterName + '.nw')
        # turn off the normalization to correctly apply the stored skin weights
        cmds.setAttr((skinClusterName + '.nw'), 0)
        # pruning the skin weights to zero is much faster
        # than iterating through all components and setting them to 0
        cmds.skinPercent(skinClusterName, shape, prw = 100, nrm = 0)

        # allocate memory for the number of components to set
        weights = eval(weightLines[len(weightLines) - 2])
        # get the index of the last component stored in the weight list
        maxIndex = weights[0]
        cmds.select(skinClusterName, r = True)
        cmdString = 'setAttr -s ' + str(maxIndex + 1) + ' \".wl\"'
        OpenMaya.MGlobal.executeCommand(cmdString)

        # --------------------------------------------------------------------------------
        # apply the weight data
        # --------------------------------------------------------------------------------

        # timer for timing the read time without the smooth binding
        #start = cmds.timerX()

        for l in range(3, len(weightLines) - 1):
            weights = eval(weightLines[l])
            weightsNext = ''
            # also get the next line for checking if the component changes
            # but only if it's not the end of the list
            if l < len(weightLines) - 2:
                weightsNext = eval(weightLines[l + 1])
            else:
                weightsNext = weights
                writeData = 1

            compIndex = weights[0]

            # --------------------------------------------------------------------------------
            # construct the setAttr string
            # i.e. setAttr -s 4 ".wl[9].w[0:3]"  0.0003 0.006 0.496 0.496
            # --------------------------------------------------------------------------------

            # start a new range
            if inflStart == -1:
                inflEnd = inflStart = weights[2]
            else:
                # if the current component is the next in line
                if inflEnd == weights[2] - 1:
                    inflEnd = weights[2]
                # if influences were dropped because of zero weight
                else:
                    # fill the weight string inbetween with zeros
                    for x in range(inflEnd + 1, weights[2]):
                        weightString += '0 '
                        setCount += 1
                    inflEnd = weights[2]

            # add the weight to the weight string
            weightString += str(weights[3]) + ' '
            # increase the number of weights to be set
            setCount += 1

            # if the next line is for the next index set the weights
            if compIndex != weightsNext[0]:
                writeData = 1

            if writeData == 1:
                # decide if a range or a single influence index is written
                rangeString = ':' + str(inflEnd)
                if inflEnd == inflStart:
                    rangeString = ''

                cmdString = 'setAttr -s ' + str(setCount) + ' \".weightList[' + str(compIndex) + '].weights[' + str(inflStart) + rangeString + ']\" ' + weightString
                OpenMaya.MGlobal.executeCommand(cmdString)

                # reset and start over
                inflStart = inflEnd = -1
                writeData = 0
                setCount = 0
                weightString = ''

        cmds.setAttr((skinClusterName + '.nw'), normalization)

        if original_skinCls is not False:
            cmds.rename(skinClusterName,  str(original_skinCls)) 

        #doneTime = cmds.timerX(startTime = start)
        #OpenMaya.MGlobal.displayInfo('%.02f seconds' % doneTime)

        return(1)


# --------------------------------------------------------------------------------
# define the syntax, needed to make it work with mel and python
# --------------------------------------------------------------------------------

# creator
def cmdCreator():
    return OpenMayaMPx.asMPxPtr(transferSkinCluster())

def syntaxCreator():
    syn = OpenMaya.MSyntax()
    syn.addFlag(helpFlag, helpFlagLong);
    syn.addFlag(fileFlag, fileFlagLong, OpenMaya.MSyntax.kString);
    syn.addFlag(modeFlag, modeFlagLong, OpenMaya.MSyntax.kLong);
    syn.addFlag(orderFlag, orderFlagLong, OpenMaya.MSyntax.kLong);
    syn.addFlag(exclusiveFlag, exclusiveFlagLong, OpenMaya.MSyntax.kLong);
    return syn

# initialization
def initializePlugin( mobject ):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, 'Audrey Deschamps-Brower', '1.00')
    try:
        mplugin.registerCommand(kPluginCmdName, cmdCreator, syntaxCreator)
    except:
        sys.stderr.write('Failed to register command: %s\n' % kPluginCmdName)
        raise

def uninitializePlugin( mobject ):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(kPluginCmdName)
    except:
        sys.stderr.write( 'Failed to unregister command: %s\n' % kPluginCmdName )
        raise

