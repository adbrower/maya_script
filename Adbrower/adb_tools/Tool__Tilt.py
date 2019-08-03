# ------------------------------------------------------------------------------------------------------
# Rigging Titl Tool
# -- Version 2.0.0
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------------------------------------------------------

import ConfigParser
import getpass
import os

import adb_rig.Class__Tilt_Setup as adb_tilt
import adbrower
import CollDict
import maya.cmds as mc
import maya.OpenMayaUI as omui
import pymel.core as pm
from adbrower import undo
from CollDict import colordic

adb = adbrower.Adbrower()
# reload(adb_tilt)

# -----------------------------------
#  CLASS
# -----------------------------------


class TiltTool():
    """This Tool makes a tilt fonction on any object  """

    def __init__(self, **kwargs):

        self.version = 3.0
        self.name = 'TiltTool_win'
        self.title = 'adbrower - Tilt_Tool' + '  v' + str(self.version)
        self.userName = getpass.getuser()

        self.path_window = 'C:/Users/' + self.userName + '/AppData/Roaming'
        self.path_linux = '/home/' + self.userName + '/'
        self.folder_name = '.config/adb_Setup'
        self.file_name = 'Tilt_Tool_confi.ini'

        self.final_path = self.setPath()
        self.loadData()

        self.tiltCtrl_txt = self. tilt_ctrl_setdata
        self.mesh_txt = self.mesh_setdata
        self.parent_txt = self.parent_setdata
        self.offset_txt = self.offset_setdata

        self.ui()

        omui.MUiMessage_addUiDeletedCallback(self.name, self.MUiMessageCallback, "clientData")
        # pm.scriptJob(uiDeleted=[self.name, self.scriptJobCallback], runOnce=True)

    def MUiMessageCallback(self, clientData):
        print('adb_TiltToolsettings file saved at: ' + self.final_path + self.folder_name + '/' + self.file_name)

    def scriptJobCallback(self, *args):
        self.saveData()

    def ui(self):
        template = pm.uiTemplate('ExampleTemplate', force=True)
        template.define(pm.button, height=30, w=80)
        template.define(pm.frameLayout, mw=2, mh=2, borderVisible=False, labelVisible=False)

        if pm.window(self.name, q=1, ex=1):
            pm.deleteUI(self.name)

        with pm.window("TiltTool_win", t=self.title, s=False, tlb=True, mnb=True) as win:
            with template:
                with pm.frameLayout():
                    with pm.columnLayout(adj=True, rs=10):
                        pm.text(label="OPTIONS", h=30, fn="boldLabelFont")

                    with pm.frameLayout():
                        with pm.columnLayout(adj=True, rs=5):

                            with pm.rowLayout(columnWidth3=(0, 0, 0), adj=True, numberOfColumns=4):
                                pm.text(label="Tilt Control  ", align='left')
                                self.tiltCtrl = pm.textFieldGrp(pht="Select the tilt control", cw1=150, tx=self.tiltCtrl_txt)
                                pm.text(label="< < < ")
                                pm.button(label="Add",  h=25, backgroundColor=colordic['green3'], c=pm.Callback(self.getCtrl))

                            with pm.rowLayout(columnWidth3=(0, 0, 0), adj=True, numberOfColumns=4):
                                pm.text(label="Mesh ", align='left')
                                self.mesh = pm.textFieldGrp(pht="Select the mesh", cw1=150, tx=self.mesh_txt)
                                pm.text(label="< < < ")
                                pm.button(label="Add",  h=25, backgroundColor=colordic['green3'], c=pm.Callback(self.getMesh))

                            with pm.rowLayout(columnWidth3=(0, 0, 0), adj=True,  numberOfColumns=4):
                                pm.text(label="Target Parent Group", align='left')
                                self.target = pm.textFieldGrp(pht="Select the target", cw1=150, tx=self.parent_txt)
                                pm.text(label="< < < ")
                                pm.button(label="Add", h=25,  backgroundColor=colordic['green3'], c=pm.Callback(self.getTarget))

                            with pm.rowLayout(columnWidth3=(0, 0, 0), adj=True,  numberOfColumns=4):
                                pm.text(label="Mesh Last Offset Ctrl", align='left')
                                self.offset_ctrl = pm.textFieldGrp(pht="Select the target", cw1=150, tx=self.offset_txt)
                                pm.text(label="< < < ")
                                pm.button(label="Add", h=25,  backgroundColor=colordic['green3'], c=pm.Callback(self.getOffsetCtrl))

                            pm.separator()
                            pm.text(label="RIGGING", h=20, fn="boldLabelFont")
                            pm.separator()

                            with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=7):
                                pm.text(label="   CHOOSE AXIS    ", h=50,)

                                if self.axisZ_setdata == 'True':
                                    pm.checkBox("myChBxZ", l="Z  axis", h=25, value=True)
                                else:
                                    pm.checkBox("myChBxZ", l="Z  axis", h=25, value=False)

                                if self.axisX_setdata == 'True':
                                    pm.checkBox("myChBxX", l="X  axis", h=25, value=True)
                                else:
                                    pm.checkBox("myChBxX", l="X  axis", h=25, value=False)

                                pm.button(label="Save Data", w=88, h=25,  backgroundColor=colordic['blue'], c=pm.Callback(self.saveData))
                                pm.button(label="Clear Info", w=88, h=25,  backgroundColor=colordic['darkblue'], c=pm.Callback(self.refresh))

                            with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=2):

                                pm.button(label="Build Basic Guide", w=197, backgroundColor=colordic['grey'], c=pm.Callback(self.buildGuide))
                                pm.button(label="Build Basic Rig", w=197, backgroundColor=colordic['grey'], c=pm.Callback(self.buildRig))


# -----------------------------------
#   FUNCTIONS
# -----------------------------------

    def setPath(self):
        def finalPath():
            if not os.path.exists(self.path_linux):
                # print('path linux does NOT extist')
                pass
            else:
                # print('path linux does extist')
                return self.path_linux

            if not os.path.exists(self.path_window):
                # print('path pm.window does NOT extist')
                pass
            else:
                # print('path pm.window does extist')
                return self.path_window

        self.final_path = finalPath()

        os.chdir(self.final_path)
        try:
            os.makedirs(self.folder_name)
        except:
            pass

        if os.path.exists(self.final_path + '/' + self.folder_name + '/' + self.file_name):
            # print ('file exist')
            pass
        else:
            os.chdir(self.final_path + '/' + self.folder_name)

        # print(os.getcwd())
        file_ini = open(self.file_name, 'w+')
        file_ini.write('[General] \n')

        file_ini.write("tilt_ctrl_data=  \n")
        file_ini.write("mesh_data=  \n")
        file_ini.write("parent_data=  \n")
        file_ini.write("offset_data=  \n")
        file_ini.write("axisZ_data=True \n")
        file_ini.write("axisX_data=True \n")

        file_ini.close()

        return(self.final_path)

    def saveData(self):
        os.chdir(self.final_path + '/' + self.folder_name)
        # print(os.getcwd())

        file_ini = open(self.file_name, 'w+')
        file_ini.write('[General] \n')
        file_ini.write("tilt_ctrl_data=" + str(pm.textFieldGrp(self.tiltCtrl, q=True, text=True)) + '\n')
        file_ini.write("mesh_data=" + str(pm.textFieldGrp(self.mesh, q=True, text=True)) + '\n')
        file_ini.write("parent_data=" + str(pm.textFieldGrp(self.target, q=True, text=True)) + '\n')
        file_ini.write("offset_data=" + str(pm.textFieldGrp(self.offset_ctrl, q=True, text=True)) + ' \n')

        file_ini.write("axisZ_data=" + str(pm.checkBox("myChBxZ", q=True, value=True)) + '\n')
        file_ini.write("axisX_data= " + str(pm.checkBox("myChBxX", q=True, value=True)) + '\n')

        file_ini.close()
        return(file_ini)

    def refresh(self):
        pm.textFieldGrp(self.tiltCtrl, edit=True, tx='')
        pm.textFieldGrp(self.mesh, edit=True, tx='')
        pm.textFieldGrp(self.target, edit=True, tx='')
        pm.textFieldGrp(self.offset_ctrl, edit=True, tx='')

        file_ini = self.saveData()
        file_ini = open(self.file_name, 'w+')

        file_ini.write('[General] \n')
        file_ini.write("tilt_ctrl_data=  \n")
        file_ini.write("mesh_data=  \n")
        file_ini.write("parent_data=  \n")
        file_ini.write("offset_data=  \n")
        file_ini.write("axisZ_data=True \n")
        file_ini.write("axisX_data=True \n")
        file_ini.close()

    def loadData(self):
        try:
            config = ConfigParser.ConfigParser()
            config.read(self.final_path + '/' + self.folder_name + '/' + self.file_name)

            self.tilt_ctrl_setdata = config.get("General", "tilt_ctrl_data")
            self.mesh_setdata = config.get("General", "mesh_data")
            self.parent_setdata = config.get("General", "parent_data")
            self.offset_setdata = config.get("General", "offset_data")
            self.axisZ_setdata = config.get("General", "axisZ_data")
            self.axisX_setdata = config.get("General", "axisX_data")
            # print('adb_TiltToolsettings load file from: ' + self.final_path + self.folder_name + '/' + self.file_name)

        except:
            os.chdir(self.final_path + '/' + self.folder_name)
            # print(os.getcwd())

            file_ini = open(self.file_name, 'w+')
            file_ini.write('[General] \n')
            file_ini.write("tilt_ctrl_data=  \n")
            file_ini.write("mesh_data=  \n")
            file_ini.write("parent_data=  \n")
            file_ini.write("offset_data=  \n")
            file_ini.write("axisZ_data=1 \n")
            file_ini.write("axisX_data=1 \n")

            file_ini.close()

    def getCtrl(self):
        try:
            ctrl = pm.selected()[0]
            ctrl_name = ctrl.name()
            result2 = str(ctrl_name)

            pm.textFieldGrp(self.tiltCtrl, edit=True, tx=str(result2))

        except:
            pass

    def getMesh(self):
        try:
            ctrl = pm.selected()[0]
            ctrl_name = ctrl.name()
            result1 = str(ctrl_name)

            pm.textFieldGrp(self.mesh, edit=True, tx=str(result1))

        except:
            pass

    def getTarget(self):
        try:
            ctrl = pm.selected()[0]
            ctrl_name = ctrl.name()
            result1 = str(ctrl_name)

            pm.textFieldGrp(self.target, edit=True, tx=str(result1))

        except:
            pass

    def getOffsetCtrl(self):
        try:
            ctrl = pm.selected()[0]
            ctrl_name = ctrl.name()
            result2 = str(ctrl_name)

            pm.textFieldGrp(self.offset_ctrl, edit=True, tx=str(result2))

        except:
            pass

    def oVariables(self):
        """Defining the starting variables"""
        self.geo = str(pm.textFieldGrp(self.mesh, q=True, text=True))
        self.geoShape = pm.PyNode(self.geo).getShape()

        self.tiltctrl = str(pm.textFieldGrp(self.tiltCtrl, q=True, text=True))
        bbox = pm.exactWorldBoundingBox(self.geo)

        self.mesh_ctrl_parent = str(pm.textFieldGrp(self.target, q=True, text=True))
        self.mesh_ctrl_offset = str(pm.textFieldGrp(self.offset_ctrl, q=True, text=True))


# -----------------------------------
#   BUILD GUIDE
# -----------------------------------

    def createLoc(self, type):
        if type == 'driverloc':
            driverloc = pm.spaceLocator(n='{}__driver_loc'.format(str(self.geo)))
            adb.changeColor_func(driverloc, 'index', 6)
            pm.setAttr(driverloc.rotatePivotX, k=True)
            pm.setAttr(driverloc.rotatePivotY, k=True)
            pm.setAttr(driverloc.rotatePivotZ, k=True)
            return driverloc

        elif type == 'pivotloc':
            pivotloc = pm.spaceLocator(n='{}__pivot_loc'.format(str(self.geo)))
            adb.changeColor_func(pivotloc, 'index', 17)
            return pivotloc

        elif type == 'objPosloc':
            objPosloc = pm.spaceLocator(n='{}__objPosloc_loc'.format(str(self.geo)))
            return objPosloc

        elif type == 'poslocTZ01':
            poslocTZ01 = pm.spaceLocator(n='{}__pos_locatorTZpositive'.format(str(self.geo)), p=self.zmax)
            poslocTZ01.localScale.set([0.3, 0.3, 0.3])
            adb.changeColor_func(poslocTZ01, 'index', 18)
            return poslocTZ01

        elif type == 'poslocTZ02':
            poslocTZ02 = pm.spaceLocator(n='{}__pos_locatorTZnegative'.format(str(self.geo)), p=self.zmin)
            poslocTZ02.localScale.set([0.3, 0.3, 0.3])
            adb.changeColor_func(poslocTZ02, 'index', 18)
            return poslocTZ02

        elif type == 'poslocTX01':
            poslocTX01 = pm.spaceLocator(n='{}__pos_locatorTZpositive'.format(str(self.geo)), p=self.xmax)
            poslocTX01.localScale.set([0.3, 0.3, 0.3])
            adb.changeColor_func(poslocTX01, 'index', 4)
            return poslocTX01

        elif type == 'poslocTX02':
            poslocTX02 = pm.spaceLocator(n='{}__pos_locatorTZnegative'.format(str(self.geo)), p=self.xmin)
            poslocTX02.localScale.set([0.3, 0.3, 0.3])
            adb.changeColor_func(poslocTX02, 'index', 4)
            return poslocTX02

    @undo
    def buildGuide(self):
        """Building the guide lines with locators """

        self.saveData()
        self.oVariables()

        bbox = pm.exactWorldBoundingBox(self.geo)
        self.bot = [(bbox[0] + bbox[3]) / 2, bbox[1], (bbox[2] + bbox[5]) / 2]
        self.zmin = [(bbox[0] + bbox[3]) / 2, bbox[1], bbox[2]]
        self.zmax = [(bbox[0] + bbox[3]) / 2, bbox[1], bbox[5]]
        self.xmin = [bbox[0], bbox[1], (bbox[2] + bbox[5]) / 2]
        self.xmax = [bbox[3], bbox[1], (bbox[2] + bbox[5]) / 2]

        """ -------------------- Z AXIS -------------------- """

        if mc.pm.checkBox("myChBxZ", q=True, v=True,) == 1 and mc.pm.checkBox("myChBxX", q=True, v=True,) == 0:
            self.axe = 'z'
            self.tiltZ = adb_tilt.Tilt(self.geo, self.tiltctrl, self.mesh_ctrl_parent, self.mesh_ctrl_offset, self.axe)
            self.tiltZ.buildGuide()

        """ -------------------- X AXIS -------------------- """

        if mc.pm.checkBox("myChBxX", q=True, v=True,) == 1 and mc.pm.checkBox("myChBxZ", q=True, v=True,) == 0:
            self.axe = 'x'
            self.tiltX = adb_tilt.Tilt(self.geo, self.tiltctrl, self.mesh_ctrl_parent, self.mesh_ctrl_offset, self.axe)
            self.tiltX.buildGuide()

        """ -------------------- Z AND X AXIS -------------------- """

        if mc.pm.checkBox("myChBxZ", q=True, v=True,) == 1 and mc.pm.checkBox("myChBxX", q=True, v=True,) == 1:
            self.axe = 'both'
            self.tiltBoth = adb_tilt.Tilt(self.geo, self.tiltctrl, self.mesh_ctrl_parent, self.mesh_ctrl_offset, self.axe)
            self.tiltBoth.buildGuide()


# -----------------------------------
#   BUILD RIG
# -----------------------------------

    @undo
    def buildRig(self):
        """Building the Rig and the connections """
        self.saveData()

        """ -------------------- Z AXIS -------------------- """

        if mc.pm.checkBox("myChBxZ", q=True, v=True,) == 1 and mc.pm.checkBox("myChBxX", q=True, v=True,) == 0:

            self.tiltZ.buildRig()

        """ -------------------- X AXIS -------------------- """

        if mc.pm.checkBox("myChBxX", q=True, v=True,) == 1 and mc.pm.checkBox("myChBxZ", q=True, v=True,) == 0:

            self.tiltX.buildRig()

        """ -------------------- Z AND X AXIS -------------------- """

        if mc.pm.checkBox("myChBxZ", q=True, v=True,) == 1 and mc.pm.checkBox("myChBxX", q=True, v=True,) == 1:

            self.tiltBoth.buildRig()


# myTool = TiltTool()
