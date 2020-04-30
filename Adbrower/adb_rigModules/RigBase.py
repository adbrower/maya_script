import pymel.core as pm

from adbrower import lockAttr
import adb_core.NameConv_utils as NC
import adb_core.Class__AddAttr as adbAttr

# ====================================
# CLASS
# ===================================


class RigBase(object):

    def __init__(self, rigName = 'Audrey'):
        self.RIG_NAME = rigName

        self._start()

    def _start(self):
        """
        - Creates Rig Group
        """
        self.createRigGroups(self.RIG_NAME)

    @lockAttr()
    def createRigGroups(self, rigName):
        """
        @module_name : string. Name of the module
        @is_module : Boolean. If its a MODULE or a SYSTEM

        MOD_GRP : Module grp
        RIG__GRP: Constains all the rigs stuff
        INPUT__GRP : contains all the ctrls and offset groups attach to those ctrls
        OUTPUT__GRP : contains all the joints who will be skinned

        Returns: RIG_GRP, INPUT_GRP, OUTPUT_GRP
        """
        self.MAIN_RIG_GRP = pm.group(n='{}_Rig__GRP'.format(rigName), em=1)
        self.VISIBILITY_GRP = pm.group(n='{}_Visibility__GRP'.format(rigName), em=1, parent=self.MAIN_RIG_GRP)
        self.SETTINGS_GRP = pm.group(n='{}_Settings__GRP'.format(rigName), em=1, parent=self.MAIN_RIG_GRP)
        self.SPACES_GRP = pm.group(n='{}_Space__GRP'.format(rigName), em=1, parent=self.MAIN_RIG_GRP)
        self.MODULES_GRP = pm.group(n='{}_Module__GRP'.format(rigName), em=1, parent=self.MAIN_RIG_GRP)

        return self.MAIN_RIG_GRP, self.VISIBILITY_GRP, self.SETTINGS_GRP, self.SPACES_GRP, self.MODULES_GRP, 
