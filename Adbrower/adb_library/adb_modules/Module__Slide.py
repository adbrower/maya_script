from adb_core.Class__AddAttr import NodeAttr
import pymel.core as pm

import adbrower
adb = adbrower.Adbrower()

import adb_core.ModuleBase as moduleBase
reload(moduleBase)
# -----------------------------------
# CLASS
# -----------------------------------

SLIDE_CONFIG = {
    # color : key : position : value
    'remap' : {
            0 : (0.0 , 0.0),
            1 : (0.5 , 1.0),
            2 : (1.0 , 0.0),
            },
                    }

class SlideModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(SlideModel, self).__init__()


class Slide(moduleBase.ModuleBase):
    """
    Sliding moduele

    Args:
        targets      :(list) List of transform who will be affected by the slide
        driver       :(transform) Transform which will drive the sliding
        range        :(int) range for the remap values.
        driver_axis  :(str): Driver's axis. Defaults to 'ty'.
        target_axis  :(str): Target's axis influenced by the driver. Defaults to 'ty'.
        config       :(Dictionnary): Config of value for the remapValue curves
        useMinus     :(bool): if the setup is going tu Use PlusMinusAverage with operation to minus or not.
                       if used, Fallof behaves equally both direction
                       Defaults to True.

    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_library.adb_modules.Module__Slide as Slide
    reload(Slide)

    # example:
    sliding = Slide.Slide(targets = target_list, driver = 'pPlane1_02__jnt____ctrl__',  range = 2, driver_axis='ty',  target_axis='ty')
    """

    def __init__(self,
                module_name = 'Slide',
                targets=[],
                driver=None,
                range=2,
                driver_axis='ty',
                target_axis='ty',
                config=SLIDE_CONFIG,
                useMinus=True):
        super(Slide, self).__init__()

        self._MODEL = SlideModel()

        self.NAME = module_name
        self.targets = targets
        self.range = range
        self.falloff_FACTOR = 0.5
        self.driver = pm.PyNode(driver)
        self.driver_axis = driver_axis
        self.target_axis = target_axis
        self.CONFIG = config
        self.useMinus = useMinus

        try:
            self.driver_attribute = NodeAttr([self.driver])
            self.driver_attribute.addAttr('position', 1, min=1, max=len(targets)+1)
            self.driver_attribute.addAttr('falloff', 0, min=-10, max=10)
        except RuntimeError:
            pass

        self.driver_falloff = '{}.falloff'.format(self.driver)
        self.driver_position = '{}.position'.format(self.driver)


    def __repr__(self):
        return str('{} : {} \n {}'.format(self.__class__.__name__, self.subject, self.__class__))

    # =========================
    # METHOD
    # =========================

    def start(self, metaDataNode = 'transform'):
        super(Slide, self)._start(self.NAME, _metaDataNode = metaDataNode)

        metaData_GRP_attribute = NodeAttr([self.metaData_GRP])
        metaData_GRP_attribute.addAttr('range', self.range, lock=True)
        metaData_GRP_attribute.addAttr('fallof_Factor', self.falloff_FACTOR)
        metaData_GRP_attribute.addAttr('driver', 'message')
        metaData_GRP_attribute.addAttr('targets', 'string')

        pm.PyNode(self.metaData_GRP).addAttr('remapValue_position', numberOfChildren=len(self.CONFIG['remap'].keys()), attributeType='compound')
        for pt, val in zip(self.CONFIG['remap'].keys(), self.CONFIG['remap'].values()):
            pm.PyNode(self.metaData_GRP).addAttr('pos{}'.format(pt), at='float', parent='remapValue_position', dv=val[0])

        pm.PyNode(self.metaData_GRP).addAttr('remapValue_values', numberOfChildren=len(self.CONFIG['remap'].keys()), attributeType='compound')
        for pt, val in zip(self.CONFIG['remap'].keys(), self.CONFIG['remap'].values()):
            pm.PyNode(self.metaData_GRP).addAttr('pt{}'.format(pt), at='float', parent='remapValue_values', dv=val[1])

        ## Connecting Data to metaData_GRP
        self.driver.t >> self.metaData_GRP.driver
        self.metaData_GRP.targets.set(str([str(joint) for joint in self.targets]), lock=True)

        return self.metaData_GRP

    def build(self):
        super(Slide, self)._build()

        self.creates_nodes()
        self.make_connections()

        self._MODEL.getInputs = self.driver
        self._MODEL.getOutputs = self.md_ouptut_list or []
        self._MODEL.getJoints = self.targets


    # =========================
    # SOLVERS
    # =========================

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

        if self.useMinus:
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
            for pt, val in zip(self.CONFIG['remap'].keys(), self.CONFIG['remap'].values()):
                pm.connectAttr('{}.pos{}'.format(self.metaData_GRP, pt), '{}.value[{}].value_Position'.format(node, pt))
                pm.connectAttr('{}.pt{}'.format(self.metaData_GRP, pt), '{}.value[{}].value_FloatValue'.format(node, pt))
                node.value[pt + 1].value_Interp.set(1)
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
            if self.useMinus is not True:
                pma.output3Dx >> rm.inputMin

        if self.useMinus:
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


# =========================
# CLASS
# =========================


class FkVariableModel(moduleBase.ModuleBaseModel):
    def __init__(self):
        super(FkVariableModel, self).__init__()


class FkVariable(moduleBase.ModuleBase):
    """
    Creates a Fk Variable Module
    Base on the Slide Class

    # example
    import adb_library.adb_modules.Module__Slide as Slide
    reload(Slide)

    jnts = ['adb_00{}'.format(x+1) for x in range(49)]
    fk_ctrl = ['pPlane1_01__jnt____ctrl__', 'pPlane1_02__jnt____ctrl__', 'pPlane1_03__jnt____ctrl__']
    fkV = Slide.FkVariable(jnts, fk_ctrl, 15 , 'ry', 'rz')
    """

    def __init__(self,
                 module_name = 'FkVariable',
                 joint_chain=[],
                 driver=[],
                 range=5,
                 driver_axis='ry',
                 target_axis='rz',
                 useMinus=False
                 ):
        super(FkVariable, self).__init__()

        self._MODEL = FkVariableModel()
        self.CLASS_NAME = self.__class__.__name__
        self.NAME = module_name

        self.joint_chain = joint_chain
        self.driver = driver
        self.range = range
        self.driver_axis = driver_axis
        self.target_axis = target_axis
        self.useMinus = useMinus

    def __repr__(self):
        return str('{} : {} \n {}'.format(self.__class__.__name__, self.subject, self.__class__))

    # =========================
    # PROPERTY
    # =========================


    # =========================
    # METHOD
    # =========================

    def start(self, metaDataNode = 'transform'):
        super(FkVariable, self)._start(self.NAME, _metaDataNode = metaDataNode)


    def build(self):
        super(FkVariable, self)._build

        self._MODEL.getResetJoints = self.creates_joint_offset_grp()
        self.create_fkVariable()

    # =========================
    # SOLVERS
    # =========================

    def creates_joint_offset_grp(self):
        offset_groups_layers = []
        for ctrl in range(len(self.driver)):
            layer = [adb.makeroot_func(x, suff='{}0{}'.format(self.NAME, ctrl + 1), forceNameConvention=True) for i, x in enumerate(self.joint_chain)]
            offset_groups_layers.append(layer)
        return offset_groups_layers

    def create_fkVariable(self):
        for offset_grp, fk_ctrl in zip(self._MODEL.getResetJoints, self.driver):
            self.sliding = Slide(targets=offset_grp, driver=fk_ctrl,  range=self.range, driver_axis=self.driver_axis, target_axis=self.target_axis, useMinus=self.useMinus)
            self.sliding.start()
            self.sliding.build()

        ## Updating metaData nodes. Using the one from Slide Module instead
        oldName = str(self.metaData_GRP)
        pm.delete(self.metaData_GRP)
        self.metaData_GRP = self.sliding.metaData_GRP
        pm.rename(self.metaData_GRP, oldName)
        metaData_GRP_attribute = NodeAttr([self.metaData_GRP])
        metaData_GRP_attribute.addAttr('Ouputs', 'string')
        self.metaData_GRP.Ouputs.set(str([str(joint) for joint in self._MODEL.getResetJoints[0]]), lock=True)

        ## Delete MOD GROUPS
        pm.delete(self.sliding.MOD_GRP)
        pm.delete(self.MOD_GRP)


    def connect_position_to_uv(self, factor=2):
        """ To match the position of the control / UV postion while the position is changing
        Args:
            factor (int): Defaults to 2.
        """
        for ctrl in self.driver:
            mult = pm.shadingNode('multiplyDivide', au=1)
            mult.input2X.set(factor)
            folli = pm.PyNode(ctrl).getParent().getParent()
            pm.PyNode(ctrl).position >> mult.input1X
            mult.outputX >> folli.u_param
