# ------------------------------------------------------
# Auto Rig Foot SetUp
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import ShapesLibrary as sl
import adbrower
import pymel.core as pm
from ShapesLibrary import *

# -----------------------------------
# IMPORT CUSTOM MODULES
# -----------------------------------
adb = adbrower.Adbrower()
import adb_core.Class__AddAttr as adbAttr

# BUG: Replace Class__OrientJoint with Joint Class
# import adb_utils.rig_utils.Class__OrientJoint as adbOrient


#-----------------------------------
#  DECORATORS
#-----------------------------------
from adbrower import changeColor

#-----------------------------------
# CLASS
#-----------------------------------

class FootSetUp(object):
    def __init__(self,
                 guide_foot_loc = pm.selected(),
                 joint_orient_axis = 'y',
                 foot_ctrl_shape = sl.foot_shape,
                 result_joint_rad = 0.5,
                ):

        self.guide_foot_loc = [pm.PyNode(x) for x in guide_foot_loc]
        self.foot_ctrl_shape = foot_ctrl_shape
        self.joint_orient_axis = joint_orient_axis
        self.result_joint_rad = result_joint_rad

        self.side = self.getSide(self.guide_foot_loc[0])
        self.nameStructure = {
             'Side':self.side,
             'Basename': 'Foot',
             }

        if self.side == 'r':
            self.col_main = 13
        else:
            self.col_main = 6


        self.create_foot_ctrl()
        self.Create3jointsChain()
        self.ik_setup()
        self.fk_setup()
        self.cleanUp()

    #-----------------------------------
    # SETTINGS FUNCTIONS AND PROPERTIES
    #-----------------------------------

    @property
    def getFootLocators(self):
        return (self.poslocTX01, self.poslocTX02, self.poslocTZ01, self.poslocTZ02)

    @property
    def root_grp(self):
        return self.oRoot_grp

    #-----------------------------------
    # BUILD FUNCTIONS
    #-----------------------------------

    def create_foot_ctrl(self):
        @changeColor('index', col = self.col_main )
        def create_ctrl():
            self.foot_ctrl = sl.foot_shape()
            return self.foot_ctrl
        create_ctrl()

        pm.matchTransform(self.foot_ctrl,self.guide_foot_loc[0], pos=True)
        self.foot_ctrl.rename('{Side}__{Basename}__ctrl__'.format(**self.nameStructure))

        ## postion of the controller
        pos_loc = adb.createLoc(self.guide_foot_loc[0])
        _shapes = pm.PyNode(self.foot_ctrl).getShapes()
        pm.select('{}.cv[:]'.format(_shapes[0]))
        pm.move(0, -(pos_loc.getTranslation()[1]), 0, r=1, os=1, wd=1)
        pm.delete(pos_loc)

        adb.makeroot_func(self.foot_ctrl)

        self.foot_ctrl_Attr = adbAttr.NodeAttr([self.foot_ctrl])
        self.foot_ctrl_Attr.addAttr('FOOT_ATTRIBUTES', 'enum',eName = "..........:.............:")
        self.foot_ctrl_Attr.addAttr('Heel_Front', 0)
        self.foot_ctrl_Attr.addAttr('Heel_Side', 0)
        self.foot_ctrl_Attr.addAttr('Heel_Twist', 0)
        self.foot_ctrl_Attr.addAttr('Tip_Front', 0)
        self.foot_ctrl_Attr.addAttr('Tip_Side', 0)
        self.foot_ctrl_Attr.addAttr('Tip_Twist', 0)
        self.foot_ctrl_Attr.addAttr('Ball_Front', 0)
        self.foot_ctrl_Attr.addAttr('Ball_Side', 0)
        self.foot_ctrl_Attr.addAttr('Ball_Twist', 0)
        self.foot_ctrl_Attr.addAttr('Bank', 0)
        self.foot_ctrl_Attr.addAttr('Roll', 0)

    def Create3jointsChain(self):
        # @changeColor('index',col=3)
        def ReverseJoints():
            ## Creating - positionning and renaming the joint
            pm.select(None)
            self.rev_foot_chain = [pm.joint(n='result_joint_0', rad = self.result_joint_rad+0.3) for x in range(len(self.guide_foot_loc))]
            for joint in self.rev_foot_chain:
                pm.parent(joint, w=True)

            for _joint, guide in zip(self.rev_foot_chain,self.guide_foot_loc):
                pm.matchTransform(_joint,guide, pos=True)

            self.rev_foot_chain_reverse = self.rev_foot_chain[::-1][1:]
            ## Parenting the joints
            for oParent, oChild in zip(self.rev_foot_chain_reverse[:-1], self.rev_foot_chain_reverse[1:]):
                pm.parent(oChild, None)
                pm.parent(oChild, oParent)

            pm.parent(self.rev_foot_chain_reverse[0],self.rev_foot_chain[-1])

            pm.PyNode(self.rev_foot_chain[0]).rename('{Side}__{Basename}__ankle_Rev'.format(**self.nameStructure))
            pm.PyNode(self.rev_foot_chain[1]).rename('{Side}__{Basename}__ball_Rev'.format(**self.nameStructure))
            pm.PyNode(self.rev_foot_chain[2]).rename('{Side}__{Basename}__toe_Rev'.format(**self.nameStructure))
            pm.PyNode(self.rev_foot_chain[3]).rename('{Side}__{Basename}__heel_Rev'.format(**self.nameStructure))
            adb.AutoSuffix(self.rev_foot_chain)

            ## orient joint
            if self.side == 'r':
                mirror_chain_1 = pm.mirrorJoint(self.rev_foot_chain[-1],mirrorYZ=1)
                mirror_chain_2 = [pm.PyNode(x) for x in mirror_chain_1]
                # adbOrient.OrientJoint(mirror_chain_2, 'y')
                mirror_chain_3 = pm.mirrorJoint(mirror_chain_2[0] ,mirrorBehavior=1, mirrorYZ=1)
                pm.delete(mirror_chain_1,mirror_chain_2,self.rev_foot_chain)
                self.rev_foot_chain = [pm.PyNode(x) for x in mirror_chain_3]
                pm.select(self.rev_foot_chain[0])
                pm.joint(e=1, oj='zyx', secondaryAxisOrient='ydown')
                self.rev_foot_chain = self.rev_foot_chain[::-1]
                pm.PyNode(self.rev_foot_chain[0]).rename('{Side}__{Basename}__ankle_Rev'.format(**self.nameStructure))
                pm.PyNode(self.rev_foot_chain[1]).rename('{Side}__{Basename}__ball_Rev'.format(**self.nameStructure))
                pm.PyNode(self.rev_foot_chain[2]).rename('{Side}__{Basename}__toe_Rev'.format(**self.nameStructure))
                pm.PyNode(self.rev_foot_chain[3]).rename('{Side}__{Basename}__heel_Rev'.format(**self.nameStructure))
                adb.AutoSuffix(self.rev_foot_chain)
            else:
                pass
                # adbOrient.OrientJoint(self.rev_foot_chain, 'y')
                # pm.select(self.rev_foot_chain[-1])
                # pm.joint(e=1, oj='zyx', secondaryAxisOrient='ydown')

            return self.rev_foot_chain

        # @changeColor('index',col=21)
        def ikFootJoints():
            self.ik_foot_chain = [pm.joint(n='result_joint_0', rad = self.result_joint_rad+0.2) for x in range(len(self.guide_foot_loc[:-1]))]
            for joint in self.ik_foot_chain:
                pm.parent(joint, w=True)

            for _joint, guide in zip(self.ik_foot_chain,self.guide_foot_loc):
                pm.matchTransform(_joint,guide, pos=True)

            [x.radius.set(self.result_joint_rad+0.2) for x in self.ik_foot_chain]

            ## Parenting the joints
            for oParent, oChild in zip(self.ik_foot_chain[0:-1], self.ik_foot_chain[1:]):
                pm.parent(oChild, None)
                pm.parent(oChild, oParent)

            pm.PyNode(self.ik_foot_chain[0]).rename('{Side}__{Basename}__ankle_ik'.format(**self.nameStructure))
            pm.PyNode(self.ik_foot_chain[1]).rename('{Side}__{Basename}__ball_ik'.format(**self.nameStructure))
            pm.PyNode(self.ik_foot_chain[2]).rename('{Side}__{Basename}__toe_ik'.format(**self.nameStructure))
            adb.AutoSuffix(self.ik_foot_chain)

            return self.ik_foot_chain

        # @changeColor('index',col=14)
        def fkFootJoints():
            self.fk_foot_chain = [pm.joint(n='result_joint_0', rad = self.result_joint_rad+0.1) for x in range(len(self.guide_foot_loc[:-1]))]
            for joint in self.fk_foot_chain:
                pm.parent(joint, w=True)

            for _joint, guide in zip(self.fk_foot_chain,self.guide_foot_loc):
                pm.matchTransform(_joint,guide, pos=True)

            for oParent, oChild in zip(self.fk_foot_chain[:-1], self.fk_foot_chain[1:]):
                pm.parent(oChild, None)
                pm.parent(oChild, oParent)

            pm.PyNode(self.fk_foot_chain[0]).rename('{Side}__{Basename}__ankle_fk'.format(**self.nameStructure))
            pm.PyNode(self.fk_foot_chain[1]).rename('{Side}__{Basename}__ball_fk'.format(**self.nameStructure))
            pm.PyNode(self.fk_foot_chain[2]).rename('{Side}__{Basename}__toe_fk'.format(**self.nameStructure))
            adb.AutoSuffix(self.fk_foot_chain)

            return self.fk_foot_chain

        # @changeColor('index',col=8)
        def resultFootJoints():
            result_foot_chain = pm.duplicate(self.fk_foot_chain)
            [x.radius.set(self.result_joint_rad) for x in result_foot_chain]

            pm.PyNode(result_foot_chain[0]).rename('{Side}__{Basename}__ankle_result__skn__'.format(**self.nameStructure))
            pm.PyNode(result_foot_chain[1]).rename('{Side}__{Basename}__ball_result__skn__'.format(**self.nameStructure))
            pm.PyNode(result_foot_chain[2]).rename('{Side}__{Basename}__toe_result__skn__'.format(**self.nameStructure))

            return result_foot_chain

        ## =============================
        ## JOINTS BUILD
        ## =============================

        self.rev_foot_chain = ReverseJoints()
        self.ik_foot_chain = ikFootJoints()
        self.fk_foot_chain = fkFootJoints()
        self.result_foot_chain = resultFootJoints()


    def ik_setup(self):
        ## Feet Ik Handle
        ball_IkHandle = pm.ikHandle( n='{Side}__{Basename}__ball_IkHandle__'.format(**self.nameStructure), sj=self.ik_foot_chain[0], ee=self.ik_foot_chain[1])[0]
        toe_IkHandle = pm.ikHandle( n='{Side}__{Basename}__toe_IkHandle__'.format(**self.nameStructure), sj=self.ik_foot_chain[1], ee=self.ik_foot_chain[-1])[0]
        pm.PyNode(ball_IkHandle).v.set(0)
        pm.PyNode(toe_IkHandle).v.set(0)

        ## hiearchie
        pm.parent(ball_IkHandle,self.rev_foot_chain[1])
        pm.parent(toe_IkHandle,self.rev_foot_chain[2])
        pm.orientConstraint(self.rev_foot_chain[0], self.ik_foot_chain[0], mo=True)

        ## Changer le pivot du group offset de toe_IkHandle
        self.toe_rotate_grp = adb.makeroot_func(toe_IkHandle)
        pos_loc = adb.createLoc(self.ik_foot_chain[1])
        pm.move(pos_loc.getTranslation()[0],pos_loc.getTranslation()[1], pos_loc.getTranslation()[2], (pm.PyNode(self.toe_rotate_grp).scalePivot), (pm.PyNode(self.toe_rotate_grp).rotatePivot))
        pm.delete(pos_loc)

        ## Connection attribute to joints rotation
        self.foot_ctrl.Heel_Front >> self.rev_foot_chain[-1].rx
        self.foot_ctrl.Heel_Side >> self.rev_foot_chain[-1].ry
        self.foot_ctrl.Heel_Twist >> self.rev_foot_chain[-1].rz

        self.foot_ctrl.Tip_Front >> self.rev_foot_chain[-2].rx
        self.foot_ctrl.Tip_Side >> self.rev_foot_chain[-2].rz
        self.foot_ctrl.Tip_Twist >> self.rev_foot_chain[-2].ry

        self.foot_ctrl.Ball_Front >> self.rev_foot_chain[-3].rx
        self.foot_ctrl.Ball_Side >> self.rev_foot_chain[-3].rz
        self.foot_ctrl.Ball_Twist >> self.rev_foot_chain[-3].ry


    def fk_setup(self):
        self.fk_foot_ctrls = adb.fk_shape_setup(type = "build",
                                                radius=0.5  ,
                                                Normalsctrl = (0,1,0),
                                                listJoint = self.fk_foot_chain, )
        adb.rotateVertex('y',self.fk_foot_ctrls[1:])

        pm.PyNode(self.fk_foot_ctrls[0]).rename('{Side}__{Basename}__ankle_fk'.format(**self.nameStructure))
        pm.PyNode(self.fk_foot_ctrls[1]).rename('{Side}__{Basename}__ball_fk'.format(**self.nameStructure))
        pm.PyNode(self.fk_foot_ctrls[2]).rename('{Side}__{Basename}__toe_fk'.format(**self.nameStructure))
        adb.AutoSuffix(self.fk_foot_ctrls)

        (pm.PyNode(self.fk_foot_ctrls[0]).getParent()).rename('{Side}__{Basename}__ankle_fk_ctrl__root__grp__'.format(**self.nameStructure))
        (pm.PyNode(self.fk_foot_ctrls[0]).getParent()).rename('{Side}__{Basename}__ball_fk_ctrl__root__grp__'.format(**self.nameStructure))
        (pm.PyNode(self.fk_foot_ctrls[0]).getParent()).rename('{Side}__{Basename}__toe_fk_ctrl__root__grp__'.format(**self.nameStructure))

        self.foot_fk_grp = pm.group( self.fk_foot_chain[0].getParent(), n='{Side}__{Basename}__fk__grp__'.format(**self.nameStructure), w=True)

    def FootToLeg(self,
                 leg_ik_ankle_jnt = None,
                 leg_ikHandle = None,
                 leg_main_ctrl = None,
                 leg_offset_ctrl = None,
                 leg__ankle_fk__ctrl__ = None,
                 ):
        """Connect The Foot Set up to the Leg Set up """
        def ik_set_up_to_leg():
            pm.pointConstraint(leg_ik_ankle_jnt, self.ik_foot_chain[0], mo=True)
            pm.parentConstraint(self.rev_foot_chain[0],leg_ikHandle)
            adb.makeroot_func(self.rev_foot_chain[-1],suff = 'leg_connection')
            pm.parentConstraint(leg_offset_ctrl, self.rev_foot_chain[-1].getParent(), mo=True)

            ## Connect Foot Ctrl to Leg main Ctrl
            att_to_connect = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
            for att in att_to_connect:
                pm.PyNode('{}.{}'.format(self.foot_ctrl, att)) >> pm.PyNode('{}.{}'.format(leg_main_ctrl, att))

            ## hide shape of main leg ctrl
            (pm.PyNode(leg_main_ctrl).getShape()).v.set(0)

        def fk_set_up_to_leg():
            pm.parentConstraint(leg__ankle_fk__ctrl__, self.fk_foot_ctrls[0], mo = True)
            (pm.PyNode(self.fk_foot_ctrls[0]).getShape()).v.set(0)

        def FootVisibiltySetUp():
            ## FK Foot Controls
            pm.PyNode('{}.{}'.format(leg_options_ctrl, 'IK_FK_Switch')) >> pm.PyNode(self.fk_foot_ctrls[0]).visibility

            ## IK Foot Controls
            Reverse_node = pm.shadingNode('reverse',asUtility=1, n=(self.foot_ctrl).replace(self.foot_ctrl.split('__')[3], 'ik_visibility__reverse__'))
            pm.PyNode('{}.{}'.format(leg_options_ctrl, 'IK_FK_Switch')) >> pm.PyNode(Reverse_node).inputX  ## Connect the IK -FK Control to Reverse
            pm.PyNode(Reverse_node).outputX  >> pm.PyNode(self.foot_ctrl).visibility


        def ik_fk_switch_setup():

            ## CONNECTIONS FOR ROTATION
            ##--------------------------------
            self.BlendColor_Rot_Coll = [pm.shadingNode('blendColors', n =(x).replace(x.split('__')[3], 'rot_switch_bc'), asUtility=1,) for x in self.result_foot_chain]
            # self.IKFK_ctrl_ik_switch_param = str(leg_options_ctrl) + ".IK_FK_Switch"

            ## Connect the FK in the Color 1
            for oFK, oBlendColor in zip (self.fk_foot_chain,self.BlendColor_Rot_Coll):
                pm.PyNode(oFK).rx >> pm.PyNode(oBlendColor).color1R
                pm.PyNode(oFK).ry >> pm.PyNode(oBlendColor).color1G
                pm.PyNode(oFK).rz >> pm.PyNode(oBlendColor).color1B

            ## Connect the IK in the Color 2
            for oIK, oBlendColor in zip (self.ik_foot_chain,self.BlendColor_Rot_Coll):
                pm.PyNode(oIK).rx >> pm.PyNode(oBlendColor).color2R
                pm.PyNode(oIK).ry >> pm.PyNode(oBlendColor).color2G
                pm.PyNode(oIK).rz >> pm.PyNode(oBlendColor).color2B

            ## Connect the BlendColor node in the Blend joint chain
            for oBlendColor, oBlendJoint in zip (self.BlendColor_Rot_Coll,self.result_foot_chain):
                pm.PyNode(oBlendColor).outputR  >> pm.PyNode(oBlendJoint).rx
                pm.PyNode(oBlendColor).outputG  >> pm.PyNode(oBlendJoint).ry
                pm.PyNode(oBlendColor).outputB  >> pm.PyNode(oBlendJoint).rz

            for oBlendColor in self.BlendColor_Rot_Coll:
                pm.PyNode(oBlendColor).blender.set(1)

            ## Setting up the blending according to the IK-FK control
            self.RemapValueColl = [pm.shadingNode('remapValue',asUtility=1, n=(x).replace(x.split('__')[3], 'switch_rv')) for x in self.BlendColor_Rot_Coll ]

            ## Connect the Remap Values to Blend Colors
            for oRemapValue,oBlendColor in zip (self.RemapValueColl,self.BlendColor_Rot_Coll):
                pm.PyNode(oRemapValue).outValue >> pm.PyNode(oBlendColor).blender

            # ## Connect the IK -FK Control to Remap Value
            # for each in self.RemapValueColl:
            #     pm.PyNode(self.IKFK_ctrl_ik_switch_param) >> pm.PyNode(each).inputValue

            ## CONNECTIONS FOR TRANSLATION
            ##--------------------------------
            self.BlendColor_Pos = pm.shadingNode('blendColors', n =(x).replace(x.split('__')[3], 'pos_switch_bc'), asUtility=1)

            ## connect the Remap Value to Blend Color
            pm.PyNode(self.RemapValueColl[0]).outValue >> pm.PyNode(self.BlendColor_Pos).blender

            ## Connect the IK in the Color 2
            pm.PyNode(self.ik_foot_chain[0]).tx >> pm.PyNode(self.BlendColor_Pos).color2R
            pm.PyNode(self.ik_foot_chain[0]).ty >> pm.PyNode(self.BlendColor_Pos).color2G
            pm.PyNode(self.ik_foot_chain[0]).tz >> pm.PyNode(self.BlendColor_Pos).color2B

            ## creation Locator FK position
            self.fk_pos_loc = pm.spaceLocator(n='{Side}__{Basename}__thigh_fk_pos__loc__'.format(**self.nameStructure))
            pm.matchTransform(self.fk_pos_loc, self.fk_foot_chain[0], pos = True, rot = True)
            pm.pointConstraint(self.fk_foot_chain[0],self.fk_pos_loc, mo = True)
            pm.PyNode(self.fk_pos_loc).v.set(0)

            ## Connect the FK in the Color 2
            pm.PyNode(self.fk_pos_loc).tx >> pm.PyNode(self.BlendColor_Pos).color1R
            pm.PyNode(self.fk_pos_loc).ty >> pm.PyNode(self.BlendColor_Pos).color1G
            pm.PyNode(self.fk_pos_loc).tz >> pm.PyNode(self.BlendColor_Pos).color1B

            ## Connect the BlendColor node in the Blend joint chain
            pm.PyNode(self.BlendColor_Pos).outputR  >> pm.PyNode(self.result_foot_chain[0]).tx
            pm.PyNode(self.BlendColor_Pos).outputG  >> pm.PyNode(self.result_foot_chain[0]).ty
            pm.PyNode(self.BlendColor_Pos).outputB  >> pm.PyNode(self.result_foot_chain[0]).tz

            pm.parent(self.fk_pos_loc,self.foot_fk_grp)

        def setBank():
            #===================================
            #   BUILD GUIDE
            #===================================

            adb.makeroot_func(self.rev_foot_chain[-1])
            bbox = pm.exactWorldBoundingBox(self.foot_ctrl)

            self.bot = [(bbox[0] + bbox[3])/2, bbox[1], (bbox[2] + bbox[5])/2]
            self.zmin = [(bbox[0] + bbox[3])/2 ,bbox[1], bbox[2]]
            self.zmax = [(bbox[0] + bbox[3])/2 ,bbox[1], bbox[5]]
            self.xmin = [bbox[0] , bbox[1] , (bbox[2] + bbox[5])/2]
            self.xmax = [bbox[3] , bbox[1] , (bbox[2] + bbox[5])/2]

            def createLoc(type):
                if type == 'driverloc':
                    driverloc = pm.spaceLocator(n='{Side}__{Basename}__driver_loc'.format(**self.nameStructure))
                    adb.changeColor_func(driverloc, 'index', 6)
                    pm.setAttr(driverloc.rotatePivotX, k=True)
                    pm.setAttr(driverloc.rotatePivotY, k=True )
                    pm.setAttr(driverloc.rotatePivotZ, k=True )
                    return driverloc

                elif type == 'pivotloc':
                    pivotloc = pm.spaceLocator(n='{Side}__{Basename}__pivot_loc'.format(**self.nameStructure))
                    adb.changeColor_func(pivotloc, 'index', 17)
                    return pivotloc

                elif type == 'objPosloc':
                    objPosloc = pm.spaceLocator(n='{Side}__{Basename}__objPosloc_loc'.format(**self.nameStructure))
                    return objPosloc

                elif type == 'poslocTZ01':
                    poslocTZ01 = pm.spaceLocator(n='{Side}__{Basename}__pos_locatorTZpositive'.format(**self.nameStructure), p = self.zmax)
                    poslocTZ01.localScale.set([0.08,0.08,0.08])
                    adb.changeColor_func(poslocTZ01, 'index', 18)
                    return poslocTZ01

                elif type == 'poslocTZ02':
                    poslocTZ02 = pm.spaceLocator(n='{Side}__{Basename}__pos_locatorTZnegative'.format(**self.nameStructure), p = self.zmin)
                    poslocTZ02.localScale.set([0.08,0.08,0.08])
                    adb.changeColor_func(poslocTZ02, 'index', 18)
                    return poslocTZ02

                elif type == 'poslocTX01':
                    poslocTX01 = pm.spaceLocator(n='{Side}__{Basename}__pos_locatorTXpositive'.format(**self.nameStructure), p = self.xmax)
                    poslocTX01.localScale.set([0.08,0.08,0.08])
                    adb.changeColor_func(poslocTX01, 'index', 4)
                    return poslocTX01

                elif type == 'poslocTX02':
                    poslocTX02 = pm.spaceLocator(n='{Side}__{Basename}__pos_locatorTXnegative'.format(**self.nameStructure), p = self.xmin)
                    poslocTX02.localScale.set([0.08,0.08,0.08])
                    adb.changeColor_func(poslocTX02, 'index', 4)
                    return poslocTX02
            ### Creer mes nodes et loc ###
            self.driverloc = createLoc('driverloc')
            self.pivotloc = createLoc('pivotloc')
            self.objPosloc = createLoc('objPosloc')

            self.poslocTX01 = createLoc('poslocTX01')
            self.poslocTX01Shape = self.poslocTX01.getShape()
            pm.xform(centerPivots=True)

            self.poslocTX02 =  createLoc('poslocTX02')
            self.poslocTX02Shape = self.poslocTX02.getShape()
            pm.xform(centerPivots=True)

            self.poslocTZ01 = createLoc('poslocTZ01')
            self.poslocTZ01Shape = self.poslocTZ01.getShape()
            pm.xform(centerPivots=True)

            self.poslocTZ02 =  createLoc('poslocTZ02')
            self.poslocTZ02Shape = self.poslocTZ02.getShape()
            pm.xform(centerPivots=True)

            self.ZtiltconNode = pm.shadingNode('condition',asUtility=1, n="{Side}__{Basename}__Ztilt_condition".format(**self.nameStructure))
            self.Ztilt_MD = pm.shadingNode('multiplyDivide', asUtility = 1 , n = "{Side}__{Basename}__Ztilt_multiplyDivide".format(**self.nameStructure))

            self.ZtiltconNode.operation.set(2)
            self.Ztilt_MD.operation.set(1)
            self.Ztilt_MD.input2Z.set(1)

            self.XtiltconNode = pm.shadingNode('condition',asUtility=1, n="{Side}__{Basename}__Xtilt_condition".format(**self.nameStructure))
            self.Xtilt_MD = pm.shadingNode('multiplyDivide', asUtility = 1 , n = "{Side}__{Basename}__Xtilt_multiplyDivide".format(**self.nameStructure))

            self.XtiltconNode.operation.set(3)
            self.Xtilt_MD.operation.set(1)
            self.Xtilt_MD.input2X.set(-1)

            #===================================
            #   BUILD RIG
            #===================================

            ptCont = pm.pointConstraint(self.poslocTX01 , self.pivotloc, mo=False)
            pm.delete(ptCont)

            ptCont2 = pm.pointConstraint(self.poslocTZ01 , self.pivotloc, mo=False)
            pm.delete(ptCont2)

            ## Connections ##
            self.pivotloc.translate.connect(self.driverloc.rotatePivot)
            pm.PyNode(self.foot_ctrl).Bank >> self.driverloc.rotateZ
            pm.PyNode(self.foot_ctrl).Bank >> self.XtiltconNode.firstTerm

            pm.PyNode(self.XtiltconNode).outColorR >> self.pivotloc.tx
            pm.PyNode(self.poslocTX01Shape).worldPosition[0].worldPositionX >> pm.PyNode(self.XtiltconNode).colorIfTrueR
            pm.PyNode(self.poslocTX02Shape).worldPosition[0].worldPositionX >> pm.PyNode(self.XtiltconNode).colorIfFalseR

            pm.PyNode(self.foot_ctrl).Bank >> pm.PyNode(self.Xtilt_MD).input1X
            self.Xtilt_MD.outputX >> pm.PyNode(self.driverloc).rz

            pm.PyNode(self.foot_ctrl).Roll >> self.driverloc.rotateX
            pm.PyNode(self.foot_ctrl).Roll >> self.ZtiltconNode.firstTerm

            pm.PyNode(self.ZtiltconNode).outColorR >> self.pivotloc.tz
            pm.PyNode(self.poslocTZ01Shape).worldPosition[0].worldPositionZ >> pm.PyNode(self.ZtiltconNode).colorIfTrueR
            pm.PyNode(self.poslocTZ02Shape).worldPosition[0].worldPositionZ >> pm.PyNode(self.ZtiltconNode).colorIfFalseR

            pm.PyNode(self.foot_ctrl).Roll >> pm.PyNode(self.Ztilt_MD).input1Z
            self.Ztilt_MD.outputZ >> pm.PyNode(self.driverloc).rx

            ## setter visibility ##
            self.pivotloc.visibility.set(0)
            self.driverloc.visibility.set(0)
            # self.poslocTX01.visibility.set(0)
            # self.poslocTX02.visibility.set(0)
            # self.poslocTZ01.visibility.set(0)
            # self.poslocTZ02.visibility.set(0)

            Lastgrp = pm.group(self.driverloc , self.poslocTZ01, self.poslocTZ02, self.poslocTX02, self.poslocTX01, self.rev_foot_chain[-1].getParent().getParent())

            ## =========================================
            ## setter Hiearchie et Clean Up ##
            ## =========================================

            adb.makeroot_func(self.rev_foot_chain[-1],suff = 'bank_roll')
            pm.parentConstraint(self.objPosloc, pm.PyNode(self.rev_foot_chain[-1].getParent()), mo = True)

            pm.parent(self.pivotloc,self.driverloc)
            pm.parentConstraint(str(self.objPosloc),self.rev_foot_chain[-1].getParent().getParent(), mo=True)
            pm.parent(str(self.objPosloc),str(self.driverloc))
            pm.rename ( Lastgrp,  str(self.foot_ctrl) + 'tilt_grp__')
            driver_loc_grp = adb.makeroot_func(self.driverloc)
            pm.parentConstraint(leg_offset_ctrl,driver_loc_grp, mo=True)
            # pm.PyNode(self.rev_foot_chain[-1].getParent()).v.set(0)
            pm.parent(Lastgrp,self.rigging_grp)

        ik_set_up_to_leg()
        fk_set_up_to_leg()
        # FootVisibiltySetUp()
        ik_fk_switch_setup()
        setBank()

    def cleanUp(self):
        self.rigging_grp = pm.group(n='{Side}__{Basename}__Rig_sys__grp__'.format(**self.nameStructure), em = True)
        joints_grp = pm.group(n='{Side}__{Basename}__Joints__grp__'.format(**self.nameStructure), em = True)
        self.oRoot_grp = pm.group(n='{Side}__{Basename}__Root__grp__'.format(**self.nameStructure), em = True)

        pm.parent(self.foot_fk_grp,
                  self.rigging_grp
                  )

        pm.parent(self.ik_foot_chain[0],
                  self.result_foot_chain[0],
                  joints_grp
                  )

        pm.parent(self.rigging_grp,
                  joints_grp,
                  self.foot_ctrl.getParent(),
                  self.oRoot_grp
                  )

        return self.oRoot_grp

# ===================================================

    #-----------------------------------
    # FUNCTIONS Repeated
    #-----------------------------------


    class FUNCTIONS_REPEATED():
        def __init__():
            pass

    def getSide(self,sub):
        """ Find the side according to the selection """
        totalBox = pm.PyNode(sub).getBoundingBox()
        if totalBox.center()[0] > 0.0:
            _side = 'l'
            # print('l')
        elif totalBox.center()[0] < 0.0:
            _side = 'r'
            # print('r')
        else:
            _side = 'm'
            # print('m')
        return _side



# -----------------------------------
#   IN CLASS BUILD
# -----------------------------------

b = FootSetUp(guide_foot_loc = ['L__ankle_guide', 'L__ball_guide', 'L__toe_guide', 'L__heel_guide'])
b.FootToLeg('L__Leg_Base_Ankle__JNT','L__Leg__IKHDL','L__Leg_IK__CTRL','L__Leg_IK_offset__CTRL','L__Leg_Fk_Ankle__CTRL')


