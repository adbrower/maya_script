import pymel.core as pm

import adb_core.NameConv_utils as NC
import adb_core.Class__AddAttr as adbAttr

# ====================================
# CLASS
# ===================================

class ModuleBaseModel(object):
    def __init__(self, *args, **kwargs):
        self.getJoints = []
        self.getResetJoints = []
        self.getControls = []
        self.getResetControls = []
        self.getInputs = []
        self.getoutputs = []

class ModuleBase(object):

    def __init__(self, *args, **kwargs):
        self._MODEL = ModuleBaseModel()

    def _start(self, metaDataNode = 'transform'):
        """
        - Creates Rig Group hiearchy  
        - Create Meta Data Node      
        """
        self.metaData_GRP = self.createMetaDataGrp(type=metaDataNode)
        self.hiearchy_setup(self.NAME, is_module=True)
        
    
    def _guides(self):
        """
        - Creates all the guides
        """
        pass

    def _build(self):
        """
        - Build the rig Module
        """
        pass

    def _connect(self):
        """
        - Connect to other Module
        """
        pass

    @property
    def getJoints(self):
        return self._MODEL.getJoints

    @getJoints.setter
    def getJoints(self, value):
        self._MODEL.getJoints = value

    @property
    def getResetJoints(self):
        return self._MODEL.getResetJoints

    @getResetJoints.setter
    def getResetJoints(self, value):
        self._MODEL.getResetJoints = value

    @property
    def getControls(self):
        return self._MODEL.getControls

    @getControls.setter
    def getControls(self, value):
        self._MODEL.getControls = value

    @property
    def getResetControls(self):
        return self._MODEL.getResetControls

    @getResetControls.setter
    def getResetControls(self, value):
        self._MODEL.getResetControls = value

    @property
    def getInputs(self):
        return self._MODEL.getInputs

    @property
    def getoutputs(self):
        return self._MODEL.getoutputs


    def hiearchy_setup(self, module_name, is_module=True):
        """
        @module_name : string. Name of the module
        @is_module : Boolean. If its a MODULE or a SYSTEM

        MOD_GRP : Module grp
        RIG__GRP: Constains all the rigs stuff
        INPUT__GRP : contains all the ctrls and offset groups attach to those ctrls
        OUTPUT__GRP : contains all the joints who will be skinned

        Returns: RIG_GRP, INPUT_GRP, OUTPUT_GRP
        """
        if is_module:
            module_grp_name = '{}_MOD__GRP'.format(module_name)
        else:
            module_grp_name = '{}_SYS__GRP'.format(module_name)

        self.MOD_GRP = pm.group(n=module_grp_name, em=1)
        self.RIG_GRP = pm.group(n='{}_RIG__GRP'.format(module_name), em=1)
        self.INPUT_GRP = pm.group(n='{}_INPUT__GRP'.format(module_name), em=1)
        self.OUTPUT_GRP = pm.group(n='{}_OUTPUT__GRP'.format(module_name), em=1)

        # self.CONTROLS_GRP = pm.group(n='{}_CONTROLS__GRP'.format(module_name), em=1)
        self.VISRULE_GRP = pm.group(n='{}_VISRULE__GRP'.format(module_name), em=1)

        [pm.parent(grp, self.MOD_GRP) for grp in [self.RIG_GRP, self.INPUT_GRP, self.OUTPUT_GRP]]
        # pm.parent(self.CONTROLS_GRP, self.INPUT_GRP)
        pm.parent(self.VISRULE_GRP, self.MOD_GRP)

        return self.MOD_GRP, self.RIG_GRP, self.INPUT_GRP, self.OUTPUT_GRP


    def setFinalHiearchy(self,
                         RIG_GRP_LIST = [],
                         INPUT_GRP_LIST = [],
                         OUTPUT_GRP_LIST = [],
                         module=True,
                        ):
        """
        Parent children under their group
        """
        [pm.parent(child, self.RIG_GRP) for child in RIG_GRP_LIST]
        [pm.parent(child, self.INPUT_GRP) for child in INPUT_GRP_LIST]
        [pm.parent(child, self.OUTPUT_GRP) for child in OUTPUT_GRP_LIST]

  
    def createMetaDataGrp(self, type ='transform'):
        """
        Create a Meta Data Node
        @param type: string. 
                'transform': empty node
                'network' : network node

        """    
        METADATA_grp_name = self.NAME + '__METADATA'

        if pm.objExists(METADATA_grp_name):
            pm.delete(METADATA_grp_name)

        if type == 'transform':
            metaData_GRP = pm.group(n=METADATA_grp_name, em=True)
        elif type == 'network':
            metaData_GRP = pm.shadingNode('network', au=1, n=METADATA_grp_name)

        return metaData_GRP

