from adb_utils.Class__AddAttr import NodeAttr
import pymel.core as pm

import adbrower
adb = adbrower.Adbrower()

# -----------------------------------
# CLASS
# -----------------------------------

METADATA_grp_name = 'slide__METADATA'


class Slide(object):
    """
    Sliding moduele

    @param targets : (list) List of transform who will be affected by the slide
    @param driver  : (transform) Transform which will drive the sliding
    @range         : (int) range for the remap values.
    @driver_axis   : (string)
    @target_axis   : (string)

    ## EXTERIOR CLASS BUILD
    #------------------------
    from adb_rig.Class__Slide import Slide

    # example:
    sliding = Slide( targets = target_list, driver = 'pPlane1_02__jnt____ctrl__',  range = 2, driver_axis='ry',  target_axis='rz')

    """

    def __init__(self, targets=[], driver=None,  range=2, driver_axis='ty', target_axis='ty'):
        self.targets = targets
        self.range = range
        self.falloff_FACTOR = 0.5
        self.driver = pm.PyNode(driver)
        self.driver_axis = driver_axis
        self.target_axis = target_axis

        try:
            self.driver_attribute = NodeAttr([self.driver])
            self.driver_attribute.addAttr('position', 0)
            self.driver_attribute.addAttr('falloff', 0)
        except RuntimeError:
            pass

        self.driver_falloff = '{}.falloff'.format(self.driver)
        self.driver_position = '{}.position'.format(self.driver)

        self.create_metaData_GRP()
        self.creates_nodes()
        self.make_connections()

    def create_metaData_GRP(self):

        if pm.objExists(METADATA_grp_name):
            pm.delete(METADATA_grp_name)

        # self.metaData_GRP = pm.group(n=METADATA_grp_name, em=True)
        self.metaData_GRP = pm.shadingNode('network', au=1, n='{}_{}'.format(self.driver, METADATA_grp_name))
        metaData_GRP_attribute = NodeAttr([self.metaData_GRP])
        metaData_GRP_attribute.addAttr('range', self.range)
        metaData_GRP_attribute.addAttr('fallof_Factor', self.falloff_FACTOR)
        metaData_GRP_attribute.addAttr('driver', 'message')

        pm.PyNode(self.metaData_GRP).addAttr('remapValue_values', numberOfChildren=5, attributeType='compound')
        pm.PyNode(self.metaData_GRP).addAttr('pt0', at='float', parent='remapValue_values')
        pm.PyNode(self.metaData_GRP).addAttr('pt1', at='float', parent='remapValue_values')
        pm.PyNode(self.metaData_GRP).addAttr('pt2', at='float', parent='remapValue_values')
        pm.PyNode(self.metaData_GRP).addAttr('pt3', at='float', parent='remapValue_values')
        pm.PyNode(self.metaData_GRP).addAttr('pt4', at='float', parent='remapValue_values')

        pm.PyNode(self.metaData_GRP).addAttr('remapValue_position', numberOfChildren=5, attributeType='compound')
        pm.PyNode(self.metaData_GRP).addAttr('pos0', at='float', parent='remapValue_position')
        pm.PyNode(self.metaData_GRP).addAttr('pos1', at='float', parent='remapValue_position')
        pm.PyNode(self.metaData_GRP).addAttr('pos2', at='float', parent='remapValue_position')
        pm.PyNode(self.metaData_GRP).addAttr('pos3', at='float', parent='remapValue_position')
        pm.PyNode(self.metaData_GRP).addAttr('pos4', at='float', parent='remapValue_position')

        self.metaData_GRP.pt0.set(0)
        self.metaData_GRP.pt1.set(0.6)
        self.metaData_GRP.pt2.set(1)
        self.metaData_GRP.pt3.set(1)
        self.metaData_GRP.pt4.set(1)

        self.metaData_GRP.pos0.set(0)
        self.metaData_GRP.pos1.set(0.25)
        self.metaData_GRP.pos2.set(0.5)
        self.metaData_GRP.pos3.set(0.75)
        self.metaData_GRP.pos4.set(1)

        self.driver.t >> self.metaData_GRP.driver

        return self.metaData_GRP

    def creates_nodes(self):
        # FALLOF FACTOR
        self.md_fallof_FACTOR = pm.shadingNode('multiplyDivide', asUtility=1, n='Fallof_FACTOR_MD')
        self.md_fallof_FACTOR.operation.set(1)
        self.metaData_GRP.fallof_Factor >> self.md_fallof_FACTOR.input2X

        # PLUS MINUS AVERAGE - ADD
        self.pma_falloff_add_list = [pm.shadingNode('plusMinusAverage', asUtility=1, n='add_PMA') for x in self.targets]
        self.pma_falloff_add_list[0].input3D[0].input3Dx.set(0)
        self.pma_falloff_add_list[0].input3D[0].input3Dy.set(self.range)

        for index, node in enumerate(self.pma_falloff_add_list[1:]):
            node.input3D[0].input3Dx.set(index + 1)
            getAtt = node.input3D[0].input3Dx.get()
            node.input3D[0].input3Dy.set(getAtt + self.range)

        # PLUS MINUS AVERAGE - MINUS
        self.pma_falloff_minus_list = [pm.shadingNode('plusMinusAverage', asUtility=1,  n='minus_PMA') for x in self.targets]
        self.pma_falloff_minus_list[0].input3D[0].input3Dx.set(0)
        self.pma_falloff_minus_list[0].input3D[0].input3Dy.set(self.range)
        self.pma_falloff_minus_list[0].operation.set(2)

        for index, node in enumerate(self.pma_falloff_minus_list[1:]):
            node.operation.set(2)
            node.input3D[0].input3Dx.set(index - 1)
            getAtt = node.input3D[0].input3Dx.get()
            node.input3D[0].input3Dy.set(getAtt + self.range)

        # REMAP VALUE FOR REMAPING THE POSITION
        self.rm_position_list = [pm.shadingNode('remapValue', asUtility=1, n='range_remap_RV') for x in self.targets]
        for node in self.rm_position_list:
            self.metaData_GRP.pos0 >> node.value[0].value_Position
            self.metaData_GRP.pt0 >> node.value[0].value_FloatValue

            self.metaData_GRP.pos1 >> node.value[1].value_Position
            self.metaData_GRP.pt1 >> node.value[1].value_FloatValue

            self.metaData_GRP.pos2 >> node.value[2].value_Position
            self.metaData_GRP.pt2 >> node.value[2].value_FloatValue

            self.metaData_GRP.pos3 >> node.value[3].value_Position
            self.metaData_GRP.pt3 >> node.value[3].value_FloatValue

            self.metaData_GRP.pos4 >> node.value[4].value_Position
            self.metaData_GRP.pt4 >> node.value[4].value_FloatValue

            [node.value[i + 1].value_Interp.set(3) for i in xrange(4)]
            node.outputMin.set(0)
            node.outputMax.set(1)

        # MULTIPLY DIVIDE OUTPUT GOING INTO THE TARGETS
        self.md_ouptut_list = [pm.shadingNode('multiplyDivide', asUtility=1, n='OUTPUT_MD') for x in self.targets]
        for node in self.md_ouptut_list:
            node.operation.set(1)

    def make_connections(self):
        pm.PyNode(self.driver_falloff) >> self.md_fallof_FACTOR.input1X

        for pma_falloff in self.pma_falloff_add_list:
            self.md_fallof_FACTOR.outputX >> pma_falloff.input3D[1].input3Dy

        for pma, rm in zip(self.pma_falloff_add_list, self.rm_position_list):
            pma.output3Dy >> rm.inputMax
            # pma.output3Dx >> rm.inputMin

        for pma_falloff in self.pma_falloff_minus_list:
            self.md_fallof_FACTOR.outputX >> pma_falloff.input3D[1].input3Dx

        for pma, rm in zip(self.pma_falloff_minus_list, self.rm_position_list):
            pma.output3Dx >> rm.inputMin

        for rm in self.rm_position_list:
            pm.PyNode(self.driver_position) >> rm.inputValue

        for md in self.md_ouptut_list:
            pm.PyNode('{}.{}'.format(self.driver, self.driver_axis)) >> md.input1X

        for rm, md in zip(self.rm_position_list, self.md_ouptut_list):
            rm.outValue >> md.input2X

        for md, target in zip(self.md_ouptut_list, self.targets):
            pm.connectAttr(md.outputX, '{}.{}'.format(target, self.target_axis))


class FkVariable(object):
    """
    Creates a Fk Variable Module
    Base on the Slide Class

    # example
    jnts = ['adb_00{}'.format(x+1) for x in xrange(49)]
    fk_ctrl = ['pPlane1_01__jnt____ctrl__', 'pPlane1_02__jnt____ctrl__', 'pPlane1_03__jnt____ctrl__']
    fkV = FkVariable(jnts, fk_ctrl, 15 , 'ry', 'rz')
    """

    def __init__(self,
                 joint_chain=[],
                 fk_controls=[],
                 range=5,
                 driver_axis='ry',
                 target_axis='rz',
                 ):

        self.joint_chain = joint_chain
        self.fk_controls = fk_controls
        self.range = range
        self.driver_axis = driver_axis
        self.target_axis = target_axis

        self.creates_joint_offset_grp()
        self.create_fkVariable()

    @property
    def md_ouptut_list(self):
        return sliding.md_ouptut_list

    def creates_joint_offset_grp(self):
        self.offset_groups_layers = []
        for ctrl in xrange(len(self.fk_controls)):
            layer = [adb.makeroot_func(x, suff='OFFSET0{}'.format(ctrl + 1)) for i, x in enumerate(self.joint_chain)]
            self.offset_groups_layers.append(layer)

    def create_fkVariable(self):
        for offset_grp, fk_ctrl in zip(self.offset_groups_layers, self.fk_controls):
            sliding = Slide(targets=offset_grp, driver=fk_ctrl,  range=self.range, driver_axis=self.driver_axis, target_axis=self.target_axis)

    def connect_position_to_uv(self, factor=2):
        for ctrl in self.fk_controls:
            mult = pm.shadingNode('multiplyDivide', au=1)
            mult.input2X.set(factor)
            folli = pm.PyNode(ctrl).getParent().getParent()
            pm.PyNode(ctrl).position >> mult.input1X
            mult.outputX >> folli.u_param
