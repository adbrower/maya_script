import maya.cmds as mc
import pymel.core as pm
import pymel.core.datatypes as dt

import adb_core.NameConv_utils as NC
import adb_core.Class__Locator as Locator
import adb_core.Class__AddAttr as adbAttr

from adbrower import changeColor
import adbrower

adb = adbrower.Adbrower()

getAxis = {
    (1, 0, 0): "x",
    (-1, 0, 0): "-x",
    (0, 1, 0): "y",
    (0, -1, 0): "-y",
    (0, 0, 1): "z",
    (0, 0, -1): "-z",
}


@changeColor('index', 3)
def poseReader(name = '', driver='joint1__CTRL', target = 'joint2__CTRL', upPostion = (0,10,0), targetPosition = (10,0,0), twistPosition = (0,0,10), twist=False):
    """
    Create a Pose Reader

    import adb_library.adb_utils.Script__PoseReader as PoseReader

    PoseReader.PoseReader()

    """
    poseReaderGrp = pm.createNode('transform', name='{}_PoseReader__{}'.format(name, NC.GRP))
    pm.matchTransform(poseReaderGrp, driver, pos=True, rot=False)
    mainPoseReader = Locator.Locator.create(name='{}_tempPoseReader__{}'.format(name, NC.LOC))
    mainPoseReaderOutput = Locator.Locator.create(name='{}_MainPoseReader__{}'.format(name, NC.LOC))
    upPoseReader = Locator.Locator.create(name='{}_UpPoseReader__{}'.format(name, NC.LOC))
    targetPoseReader = Locator.Locator.create(name='{}_TargetPoseReader__{}'.format(name, NC.LOC))

    poseReaderLocs = [mainPoseReader.locators, upPoseReader.locators, targetPoseReader.locators, mainPoseReaderOutput.locators]

    [pm.matchTransform(loc, target, pos=True, rot=False) for loc in poseReaderLocs]
    [pm.parent(loc, poseReaderGrp) for loc in poseReaderLocs]
    targetGrp = adb.makeroot_func(targetPoseReader.locators)

    pm.move(upPoseReader.locators[0], upPostion, r=1, os=1, wd=1)
    pm.move(targetPoseReader.locators[0], targetPosition, r=1, os=1, wd=1)

    pm.aimConstraint(targetPoseReader.locators[0], mainPoseReader.locators[0], weight=1, upVector=tuple(dt.Vector(upPostion).normal()), worldUpObject=upPoseReader.locators[0], worldUpType="object", offset=(0, 0, 0), aimVector=tuple(dt.Vector(targetPosition).normal()))

    pm.parent(poseReaderGrp, driver)
    adb.matrixConstraint(target, targetGrp)

    # add double Function
    adb.makeroot_func(mainPoseReader.locators)
    adb.makeroot_func(upPoseReader.locators)

    mainPoseReader.locators[0].tx.set(targetPosition[0]*-1)
    upPoseReader.locators[0].tx.set(targetPosition[0]*-1)
    
    mult = pm.shadingNode('multiplyDivide', asUtility=1, n='{}_PR_double__{}'.format(name, NC.MULTIPLY_DIVIDE_SUFFIX))
    mult.input2X.set(2)
    mult.input2Y.set(2)
    mult.input2Z.set(2)

    mainPoseReader.locators[0].rx >> mult.input1X
    mainPoseReader.locators[0].ry >> mult.input1Y
    mainPoseReader.locators[0].rz >> mult.input1Z

    mult.outputX >> mainPoseReaderOutput.locators[0].rx
    mult.outputY >> mainPoseReaderOutput.locators[0].ry
    mult.outputZ >> mainPoseReaderOutput.locators[0].rz

    ## add Twist
    if twist:
        twistPoseReaderGrp = pm.createNode('transform', name='{}_TwistPoseReader__{}'.format(name, NC.GRP))
        pm.matchTransform(twistPoseReaderGrp, driver, pos=True, rot=False)
        twistMainPoseReader = Locator.Locator.create(name='{}_TwistMainPoseReader__{}'.format(name, NC.LOC))
        twistTargetPoseReader = Locator.Locator.create(name='{}_TwistTargetPoseReader__{}'.format(name, NC.LOC))
        twistUpPoseReader = Locator.Locator.create(name='{}_TwistUpPoseReader__{}'.format(name, NC.LOC))

        twistPoseReaderLocs = [twistMainPoseReader.locators, twistUpPoseReader.locators, twistTargetPoseReader.locators]
        [pm.parent(loc, twistPoseReaderGrp) for loc in twistPoseReaderLocs]
        pm.parent(twistPoseReaderGrp, poseReaderGrp)

        [pm.matchTransform(loc, target, pos=True, rot=False) for loc in twistPoseReaderLocs]

        pm.move(twistUpPoseReader.locators[0], targetPosition, r=1, os=1, wd=1)
        pm.move(twistTargetPoseReader.locators[0], twistPosition, r=1, os=1, wd=1)

        pm.aimConstraint(twistTargetPoseReader.locators[0], twistMainPoseReader.locators[0], weight=1, upVector=tuple(dt.Vector(targetPosition).normal()), worldUpObject=twistUpPoseReader.locators[0], worldUpType="object", offset=(0, 0, 0), aimVector=tuple(dt.Vector(twistPosition).normal()))
        pm.parent(twistTargetPoseReader.locators[0], targetGrp)

        mult.outputY >> twistPoseReaderGrp.ry
        mult.outputZ >> twistPoseReaderGrp.rz

    ## add Extra Attributes
    mainLocAttr = adbAttr.NodeAttr(mainPoseReaderOutput.locators)
    mainLocAttr.addAttr('bend', 0)
    mainLocAttr.addAttr('twist', 0)
    mainLocAttr.addAttr('bendSide', 0)

    if twist:
        twistMainPoseReader.locators[0].rx >>mainPoseReaderOutput.locators[0].twist
    mainPoseReaderOutput.locators[0].ry >> mainPoseReaderOutput.locators[0].bendSide
    mainPoseReaderOutput.locators[0].rz >>mainPoseReaderOutput.locators[0].bend


    poseReaderGrp.v.set(0)
    return mainPoseReaderOutput.locators, upPoseReader.locators, targetPoseReader.locators



# poseReader()