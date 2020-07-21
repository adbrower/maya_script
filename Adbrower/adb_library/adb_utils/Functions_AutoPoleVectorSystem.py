import pymel.core as pm
import maya.OpenMaya as om

import adb_core.Class__Joint as Joint

def getAimMatrix(aimVector, upVector=(0,1,0), pos=(0, 0, 0), aimAxis='x', upAxis='y'):
        """
        Find the aimMatrix from the aimVector

         ^ : XOR  Sets each bit to 1 if only one of two bits is 1

        Args:
            aimVector ([type]): [description]
            upVector (tuple, optional): [description]. Defaults to (0,1,0).
            pos (tuple, optional): [description]. Defaults to (0, 0, 0).
            aimAxis (str, optional): [description]. Defaults to 'x'.
            upAxis (str, optional): [description]. Defaults to 'y'.

        Returns:
            [type]: [description]
        """
        vecDict = {
            aimAxis:aimVector,
            upAxis:upVector,
        }

        xVector = vecDict.get('x', []) or vecDict.get('+x', []) or [i*-1.0 for i in vecDict.get('-x', [])]
        yVector = vecDict.get('y', []) or vecDict.get('+y', []) or [i*-1.0 for i in vecDict.get('-y', [])]
        zVector = vecDict.get('z', []) or vecDict.get('+z', []) or [i*-1.0 for i in vecDict.get('-z', [])]

        if xVector:
            xVector = om.MVector(xVector[0], xVector[1], xVector[2]).normal()
        if yVector:
            yVector = om.MVector(yVector[0], yVector[1], yVector[2]).normal()
        if zVector:
            zVector = om.MVector(zVector[0], zVector[1], zVector[2]).normal()

        if not xVector:
            xVector = (yVector ^ zVector).normal()
        elif not yVector:
            yVector = (zVector ^ xVector).normal()
        elif not zVector:
            zVector = (xVector ^ yVector).normal()

        # fix up vector
        if upAxis[-1] == 'x':
            xVector = (yVector ^ zVector).normal()
        elif upAxis[-1] == 'y':
            yVector = (zVector ^ xVector).normal()
        elif upAxis[-1] == 'z':
            zVector = (xVector ^ yVector).normal()

        xVector = [xVector.x, xVector.y, xVector.z, 0.0]
        yVector = [yVector.x, yVector.y, yVector.z, 0.0]
        zVector = [zVector.x, zVector.y, zVector.z, 0.0]
        pos = [pos[0], pos[1], pos[2], 1.0]

        return xVector + yVector + zVector + pos

def autoPoleVectorSystem(prefix='',
                         ikCTL = 'L__Arm_IK__CTRL',
                         ikJointChain = ['L__Arm_Ik_Shoulder__JNT', 'L__Arm_Ik_Elbow__JNT', 'L__Arm_Ik_Wrist__JNT'],
                         ):

    prefix = '{}AutoPole'.format([prefix])
    ikjnt = Joint.Joint(ikJointChain)
    grp = pm.createNode('transform', name=prefix + "__GRP")
    aimGrp = pm.createNode('transform', name=prefix + "_Aim__GRP")
    outGrp = pm.createNode('transform', name=prefix + "_Out__GRP")
    pm.parent(aimGrp, outGrp, grp)

    aimVec = ikjnt.getVectors(ikJointChain[0], normal=(0,1,0)).aimV
    upVec = ikjnt.getVectors(ikJointChain[0], normal=(1,0,0)).upV

    aimVec, upVec = map(ikjnt.getClosestVector, (aimVec, upVec))

    mat = getAimMatrix(aimVec, upVec, pos=pm.xform(ikJointChain[0], ws=True, q=True, t=True))
    pm.xform(grp, ws=True, matrix=mat)

    pm.matchTransform(ikJointChain[2], aimGrp, rot=1, pos=0)
    pm.pointConstraint(ikCTL, aimGrp)

    angle = pm.createNode('angleBetween')

    localAim, localUp = ikjnt.getVectors(ikJointChain[0])
    pm.setAttr(angle + ".vector1", *localAim, type='double3')

    for axis in 'XYZ':
        cmds.connectAttr("{}.translate{}".format(aimGrp, axis), "{}.vector2{}".format(angle, axis))
        cmds.connectAttr("{}.euler{}".format(angle, axis), "{}.rotate{}".format(outGrp, axis))



# ==========================================

# autoPoleVectorSystem(prefix='L_Leg',
#                      ikCTL = 'L__Leg_IK__CTRL',
#                      ikJointChain = ['L__Leg_Ik_Hips__JNT', 'L__Leg_Ik_Knee__JNT', 'L__Leg_Ik_Ankle__JNT'],
#                     )






