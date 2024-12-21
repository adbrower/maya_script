# ------------------------------------------------------
# adbrower Copy Weight Tool
# -- Method Rigger (Maya)
# -- Version 2.0.0
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import sys
import traceback

import adb_core.Class__Locator as adbLoc
import adb_library.adb_utils.Class__FkShapes as adbFkShape
import adbrower
import maya.cmds as mc
import pymel.core as pm
from adbrower import changeColor, undo
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtCore, QtGui, QtWidgets

adb = adbrower.Adbrower()

# -----------------------------------
#  CLASS
# -----------------------------------


class JointGeneratorTool(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    UI_NAME = 'adb_Rig_Tool'
    __dialog = None
    
    @classmethod
    def show_dialog(cls):
        if cls.__dialog is None:
            cls.__dialog = cls()
        else:
            cls.__dialog.raise_() 
        cls.__dialog.show()
        

    def __init__(self, parent=None):        
        super(JointGeneratorTool, self).__init__(parent=parent)

        self.setObjectName(self.UI_NAME)
        self.version = 4.0
        self.setWindowTitle('adbrower - Joint Generator Tool' + '  v' + str(self.version))

        self.setFixedWidth(400)
        self.setFixedHeight(500)
        self.setWindowFlags(QtCore.Qt.Tool)

        # Main layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(*[5] * 4)
        self.main_layout.setSpacing(2)

        self.create_Button()
        self.create_layout()
        self.connections()

        self.setLayout(self.main_layout)

    def create_Button(self):

        self.colorWhite = '#FFFFFF'
        self.colorBlack = '#190707'

        self.colorBlue = '#81DAF5'
        self.colorBluelabel = '#00cdff'
        self.colorYellowlabel = 'rgb(229,198,81)'

        self.colorBlue2 = 'rgb(55,59,73)'
        self.colorBlue3 = 'rgb(122,122,135)'
        self.colorBlue4 = 'rgb(55,59,70)'

        self.colorGreen = '#597a59'
        self.colorGreen2 = 'rgb(72,96,80)'

        self.colorRed = '#745a54'
        self.colorDarkRed1 = 'rgb(80,55,55)'
        self.colorDarkRed2 = 'rgb(70,55,55)'

        self.colorOrange = 'rgb(192,147,122)'

        self.colorGrey = '#606060'
        self.colorLightGrey = '#F2F2F2'

        self.colorYellow = '#ffe100'

        self.colorDarkGrey2 = '#373737'
        self.colorDarkGrey3 = '#2E2E2E'
        self.colorGrey2 = '#4A4949'

        self.buttonAndFunctions = [
            # name, function , group number, labelColor, backgroundColor
            ['RIGGING BUILD ',          self.ToolsExpand,                 0,    '',                                      ''],
            ['Joint Creation',          self.empty,                       1,    '',                                      ''],
            ['Build Basic Guide',       self.build_guide,                 1,    self.colorLightGrey,            self.colorDarkGrey3],
            ['Build Basic Rig',         self.build_rig,                   1,    self.colorLightGrey,            self.colorDarkGrey3],

            ['FK Set Up',               self.empty,                       2,    '',                                      ''],
            ['Fk Set Up',               self.fk_setup,                    2,    self.colorLightGrey,            self.colorDarkGrey3],
            ['Fk Shapes Set Up',        self.fk_shape_setup,              2,    self.colorLightGrey,            self.colorDarkGrey3],
            ['Delete Fk Shape',         self.delete_fk_shape_setup,       2,    self.colorLightGrey,            self.colorDarkGrey3],

            ['Curve Set Up',            self.empty,                       3,    '',                                      ''],
            ['Joint On Curve',          self.joint_on_curve,              3,    self.colorLightGrey,            self.colorDarkGrey3],
            ['Keep Motion Path',        self.keep_motion_path,            3,    self.colorLightGrey,            self.colorDarkGrey3],
            ['Delete Motion Path',      self.delete_motion_path,          3,    self.colorLightGrey,            self.colorDarkGrey3],
        ]

        self.buttons = {}
        for buttonName, buttonFunction, _, labColor, bgColor in self.buttonAndFunctions:
            self.buttons[buttonName] = QtWidgets.QPushButton(buttonName)
            self.buttons[buttonName].clicked.connect(buttonFunction)
            self.buttons[buttonName].setFixedHeight(30)
            self.buttons[buttonName].setStyleSheet(
                'padding:4px; text-align:Center; font: normal; color:{}; background-color:{};'.format(labColor, bgColor))

        # Build Buttons
        self.buttons0 = [button for button, _, groupNumber, labColor, bgColor in self.buttonAndFunctions if groupNumber == 0]
        self.buttons1 = [button for button, _, groupNumber, labColor, bgColor in self.buttonAndFunctions if groupNumber == 1]
        self.buttons2 = [button for button, _, groupNumber, labColor, bgColor in self.buttonAndFunctions if groupNumber == 2]
        self.buttons3 = [button for button, _, groupNumber, labColor, bgColor in self.buttonAndFunctions if groupNumber == 3]

    def create_layout(self):
        """ all layouts """

        def addLineL(Layout):
            line = QtWidgets.QFrame()
            line.setFrameShape(QFrame.HLine)
            Layout.addWidget(line)
            return line

        def addLine():
            line = QtWidgets.QFrame()
            line.setFrameShape(QtWidgets.QFrame.HLine)
            return line

        def addText(message, alignement=QtCore.Qt.AlignCenter, height=30, bold=False):
            myFont = QtGui.QFont()
            myFont.setBold(bold)

            text = QtWidgets.QLabel(message)
            text.setAlignment(alignement)
            text.setFixedHeight(height)
            text.setFont(myFont)
            text.setStyleSheet('color:{};'.format(self.colorWhite))

            return text

        def addSlider(min, max):
            slider = QtWidgets.QSlider()
            slider.setOrientation(QtCore.Qt.Horizontal)
            slider.setMinimum(int(min))
            slider.setMaximum(int(max))
            return slider

        def getValuBar(bar):
            val = bar.value()
            return val

        instructions_label = addText('JOINT GENERATOR TOOL')
        instructions_label.setStyleSheet("color:{};".format(self.colorLightGrey))

        # =======================
        # OPTIONS UI
        # =======================

        option_layout = QtWidgets.QGridLayout()
        self.name_LineEdit = QtWidgets.QLineEdit()
        self.name_Label = QtWidgets.QLabel('Name     >>>')
        # self.name_Label.setStyleSheet('color:{};'.format(self.colorWhite))

        self.jnt_checkbx = QtWidgets.QCheckBox('Joint Chain')
        self.jnt_checkbx.setStyleSheet("color:{}; padding-top: 10px; padding-bottom: 10px;".format(self.colorBluelabel))

        self.loc_checkbx = QtWidgets.QCheckBox('Delete Locators')
        self.loc_checkbx.setStyleSheet("color:{}; padding-left: 32px; padding-top: 10px; padding-bottom: 10px;".format(self.colorBluelabel))
        self.loc_checkbx.setChecked(1)

        self.curve_checkbx = QtWidgets.QCheckBox('Delete Curve')
        self.curve_checkbx.setStyleSheet("color:{}; padding-left: 35px; padding-top: 10px; padding-bottom: 10px;".format(self.colorBluelabel))

        self.line2 = addLine()
        self.line3 = addLine()

        tools_list = ["1-0-0", "0-1-0", "0-0-1"]
        self.ctrl_normals = QtWidgets.QComboBox()
        self.ctrl_normals.setObjectName("QComboBox")
        self.ctrl_normals.addItems(tools_list)
        self.ctrl_normals_Label = QtWidgets.QLabel('Control Normals')
        self.ctrl_normals_lineEdit = QtWidgets.QLineEdit('1-0-0')
        # self.ctrl_normals_Label.setStyleSheet('color:{};'.format(self.colorBluelabel))

        self.slider_jnt_rad = addSlider(1, 10)
        self.slider_ctrl_rad = addSlider(1, 10)
        self.slider_int = addSlider(1, 100)

        self.slider_jnt_rad_LineEdit = QtWidgets.QLineEdit('1.0')
        self.slider_jnt_rad_Label = QtWidgets.QLabel('Joint Radius    ')
        self.slider_jnt_rad_Layout = QtWidgets.QHBoxLayout()

        self.slider_jnt_rad_Layout.addWidget(self.slider_jnt_rad_Label)
        self.slider_jnt_rad_Layout.addWidget(self.slider_jnt_rad_LineEdit)
        self.slider_jnt_rad_Layout.addWidget(self.slider_jnt_rad)

        self.slider_ctrl_rad_LineEdit = QtWidgets.QLineEdit('1.0')
        self.slider_ctrl_rad_Label = QtWidgets.QLabel('Control Radius')
        self.slider_ctrl_rad_Layout = QtWidgets.QHBoxLayout()

        self.slider_ctrl_rad_Layout.addWidget(self.slider_ctrl_rad_Label)
        self.slider_ctrl_rad_Layout.addWidget(self.slider_ctrl_rad_LineEdit)
        self.slider_ctrl_rad_Layout.addWidget(self.slider_ctrl_rad)

        self.slider_int_LineEdit = QtWidgets.QLineEdit('5')
        self.slider_int_Label = QtWidgets.QLabel('Intervals          ')
        self.slider_int_Layout = QtWidgets.QHBoxLayout()

        self.slider_int_Layout.addWidget(self.slider_int_Label)
        self.slider_int_Layout.addWidget(self.slider_int_LineEdit)
        self.slider_int_Layout.addWidget(self.slider_int)

        # option_layout.addWidget(self.line2, 0,0,1,3)
        option_layout.addWidget(self.name_Label, 1, 0, 1, 1)
        option_layout.addWidget(self.name_LineEdit, 1, 1, 1, 3)
        option_layout.addWidget(self.jnt_checkbx, 2, 0,)
        option_layout.addWidget(self.loc_checkbx,  2, 1,)
        option_layout.addWidget(self.curve_checkbx,  2, 2)
        option_layout.addLayout(self.slider_int_Layout,  3, 0, 1, 3)
        option_layout.addLayout(self.slider_jnt_rad_Layout,  4, 0, 1, 3)
        option_layout.addLayout(self.slider_ctrl_rad_Layout,  5, 0, 1, 3)
        option_layout.addWidget(self.ctrl_normals_Label,  6, 0, 1, 3)
        option_layout.addWidget(self.ctrl_normals,  6, 1, 1, 1)
        # option_layout.addWidget(self.ctrl_normals_lineEdit,  6,2,1,1)

        self.slider_jnt_rad_LineEdit.setMaximumSize(QtCore.QSize(50, 50))
        self.slider_ctrl_rad_LineEdit.setMaximumSize(QtCore.QSize(50, 50))
        self.slider_int_LineEdit.setMaximumSize(QtCore.QSize(50, 50))

        # Groups
        group1 = QtWidgets.QGroupBox('Options :')
        group1.setStyleSheet("QGroupBox { border: 1px solid #606060; border-radius: 3px;}")

        # group1.setAlignment(Qt.AlignLeft)
        group1.setLayout(option_layout)

        # =======================
        # BUILD UI
        # =======================

        build_layout_Grid = QtWidgets.QGridLayout()
        build_layout_Grid.setContentsMargins(*[2] * 4)

        for buttonName in self.buttons0:
            build_layout_Grid.addWidget(self.buttons[buttonName], 1, 0, 1, 2)
            self.buttons[buttonName].setStyleSheet('padding:4px; text-align:center; border: none ; font:bold; color:{};'.format(self.colorBluelabel))
            self.buttons[buttonName].setFixedHeight(25)

        for buttonName in self.buttons1[:1]:
            build_layout_Grid.addWidget(self.buttons[buttonName], 2, 0, 1, 2)
            self.buttons[buttonName].setStyleSheet('padding:4px; text-align:Left; border: none ; font:normal; color:{};'.format(self.colorBluelabel))

        for buttonName, index, in zip(self.buttons1[1:], range(2)):
            build_layout_Grid.addWidget(self.buttons[buttonName], 3, index)

        # =======================
        # FK SET UP UI
        # =======================
        self.curve_layoutH = QtWidgets.QGridLayout()

        for buttonName in self.buttons3[:1]:
            self.curve_layoutH.addWidget(self.buttons[buttonName], 4, 0, 1, 2)
            self.buttons[buttonName].setStyleSheet('padding:4px; text-align:Left; border:none; font:normal; color:{};'.format(self.colorBluelabel))

        for buttonName, index, in zip(self.buttons3[1:], range(3)):
            self.curve_layoutH.addWidget(self.buttons[buttonName], 5, index)

        # =======================
        # CURVE UI
        # =======================

        for buttonName in self.buttons2[:1]:
            self.curve_layoutH.addWidget(self.buttons[buttonName], 0, 0, 1, 3)
            self.buttons[buttonName].setStyleSheet('padding:4px; text-align:Left; border:none; font:normal; color:{};'.format(self.colorBluelabel))

        for buttonName, index, in zip(self.buttons2[1:], range(3)):
            self.curve_layoutH.addWidget(self.buttons[buttonName], 1, index)


# =======================
# MAIN LAYOUT BUILD
# =======================

        # self.main_layout.addWidget(instructions_label)
        self.main_layout.addWidget(group1)
        self.main_layout.addLayout(build_layout_Grid)
        self.main_layout.addLayout(self.curve_layoutH)

    def connections(self):
        self.slider_jnt_rad.valueChanged.connect(self.slider_jnt_rad_act)
        self.slider_ctrl_rad.valueChanged.connect(self.slider_ctrl_rad_act)
        self.slider_int.valueChanged.connect(self.slider_int_act)
        self.ctrl_normals.currentIndexChanged.connect(self.ctrl_normals_act)

        self.slider_int_LineEdit.editingFinished.connect(self.lineEdit_int_act)
        self.slider_jnt_rad_LineEdit.editingFinished.connect(self.lineEdit_jnt_rad_act)
        self.slider_ctrl_rad_LineEdit.editingFinished.connect(self.lineEdit_ctrl_rad_act)


# -----------------------------------
#  UI FUNCTIONS
# -----------------------------------

    def empty(self):
        pass

    def ToolsExpand(self):
        buttons = []
        for buttonName in self.buttons1:
            btn = self.buttons[buttonName]
            buttons.append(btn)

        for buttonName in self.buttons2:
            btn = self.buttons[buttonName]
            buttons.append(btn)

        for buttonName in self.buttons3:
            btn = self.buttons[buttonName]
            buttons.append(btn)

        state = not buttons[0].isVisible()
        for button in buttons:
            button.setVisible(state)

        if state is False:
            self.setFixedHeight(300)

        else:
            self.setFixedHeight(500)

    def slider_jnt_rad_act(self):
        val = self.slider_jnt_rad.value()
        dc = float(val * 10 / 10)
        self.slider_jnt_rad_LineEdit.setText(str(dc))

    def slider_ctrl_rad_act(self):
        val = self.slider_ctrl_rad.value()
        dc = float(val * 10 / 10)
        self.slider_ctrl_rad_LineEdit.setText(str(dc))

    def slider_int_act(self):
        val = self.slider_int.value()
        self.slider_int_LineEdit.setText(str(val))

    def ctrl_normals_act(self):
        val = self.ctrl_normals.currentText()
        self.ctrl_normals_lineEdit.setText(str(val))

    def lineEdit_int_act(self):
        val = self.slider_int_LineEdit.text()
        self.slider_int.setValue(float(val))

    def lineEdit_jnt_rad_act(self):
        val = self.slider_jnt_rad_LineEdit.text()
        self.slider_jnt_rad.setValue(float(val))

    def lineEdit_ctrl_rad_act(self):
        val = self.slider_ctrl_rad_LineEdit.text()
        self.slider_ctrl_rad.setValue(float(val))


# -----------------------------------
#  SLOTS
# -----------------------------------

    @undo
    def build_guide(self):
        """This fonction builds the locators which are guide for futur joints """

        self.intervals = int(self.slider_int_LineEdit.text())
        self.Naming = self.name_LineEdit.text()

        selection = pm.selected()
        GuideLocList = adbLoc.Locator.in_between_base(self.intervals, *selection).locators

        # renaming
        for loc in GuideLocList:
            pm.rename(loc, '{}_loc_01'.format(str(self.Naming)))

    @undo
    def build_rig(self):
        """This fonction builds the rig based on the guide"""

        self.RadiusJnt = float(self.slider_jnt_rad_LineEdit.text())

        if self.jnt_checkbx.checkState() == QtCore.Qt.Unchecked and self.loc_checkbx.checkState() == QtCore.Qt.Unchecked and self.curve_checkbx.checkState() == QtCore.Qt.Unchecked:

            self.oCollJoints = []
            self.oCollLoc = pm.selected()
            self.Naming = self.name_LineEdit.text()

            print(self.Naming)

            # for locators in selection, run the following code
            for loc in self.oCollLoc:
                # create variable for the position of the locators
                pos = pm.xform(loc, q=True, t=True, ws=True)
                # unparent the joints
                pm.select(cl=True)
                # create joints and position them on top of locators
                myjoint = pm.joint(n=str(self.Naming) + "__jnt__01", p=pos, rad=self.RadiusJnt)
                self.oCollJoints.append(myjoint)

            # To put the joints at the same position of the locators
            for locators, joints in zip(self.oCollLoc, self.oCollJoints):
                ptCon = pm.pointConstraint(locators, joints)
                pm.delete(ptCon)

        if self.jnt_checkbx.checkState() == QtCore.Qt.Checked and self.loc_checkbx.checkState() == QtCore.Qt.Unchecked and self.curve_checkbx.checkState() == QtCore.Qt.Unchecked:

            self.oCollJoints = []
            self.oCollLoc = pm.selected()
            self.Naming = self.name_LineEdit.text()

            # for locators in selection, run the following code
            for loc in self.oCollLoc:
                # create variable for the position of the locators
                pos = pm.xform(loc, q=True, t=True, ws=True)
                # unparent the joints
                pm.select(cl=True)
                # create joints and position them on top of locators
                myjoint = pm.joint(n=str(self.Naming) + "__jnt__01", p=pos, rad=self.RadiusJnt)

                self.oCollJoints.append(myjoint)

            # To put the joints at the same position of the locators
            for locators, joints in zip(self.oCollLoc, self.oCollJoints):
                ptCon = pm.pointConstraint(locators, joints)
                pm.delete(ptCon)

            "OPTIONAL if we want the joints to be chained "

            pm.select(self.oCollJoints)

            def chain_parent(oColljoint):
                for oParent, oChild in zip(oColljoint[0:-1], oColljoint[1:]):
                    try:
                        pm.parent(oChild, None)
                        pm.parent(oChild, oParent)
                    except:
                        continue

            chain_parent(pm.selected(type='transform'))

            # This line deletes the locators #
            # pm.delete(self.oCollLoc)

            #This line Orient joints #
            pm.select(self.oCollJoints)
            pm.joint(e=1, oj='xyz', secondaryAxisOrient='yup', ch=True)
            pm.select(cl=True)

            #Orient the last joint to the world#
            self.selLastJnt = pm.select(self.oCollJoints[-1])
            pm.joint(e=1, oj='none')

        if self.jnt_checkbx.checkState() == QtCore.Qt.Unchecked and self.loc_checkbx.checkState() == QtCore.Qt.Checked and self.curve_checkbx.checkState() == QtCore.Qt.Unchecked:

            self.oCollJoints = []
            self.oCollLoc = pm.selected()
            self.Naming = self.name_LineEdit.text()

            # for locators in selection, run the following code
            for loc in self.oCollLoc:
                # create variable for the position of the locators
                pos = pm.xform(loc, q=True, t=True, ws=True)
                # unparent the joints
                pm.select(cl=True)
                # create joints and position them on top of locators
                myjoint = pm.joint(n=str(self.Naming) + "__jnt__01", p=pos, rad=self.RadiusJnt)

                self.oCollJoints.append(myjoint)

            # To put the joints at the same position of the locators
            for locators, joints in zip(self.oCollLoc, self.oCollJoints):
                ptCon = pm.pointConstraint(locators, joints)
                pm.delete(ptCon)

            # This line deletes the locators #
            pm.delete(self.oCollLoc)

        # if mc.checkBox("myChBx1", q =True, v=True,) == 1 and mc.checkBox("myChBx2", q =True, v=True,) == 1 and mc.checkBox("myChBx3", q =True, v=True,) == 0:
        if self.jnt_checkbx.checkState() == QtCore.Qt.Checked and self.loc_checkbx.checkState() == QtCore.Qt.Checked and self.curve_checkbx.checkState() == QtCore.Qt.Unchecked:

            self.oCollJoints = []
            self.oCollLoc = pm.selected()
            self.Naming = self.name_LineEdit.text()

            # for locators in selection, run the following code
            for loc in self.oCollLoc:
                # create variable for the position of the locators
                pos = pm.xform(loc, q=True, t=True, ws=True)
                # unparent the joints
                pm.select(cl=True)
                # create joints and position them on top of locators
                myjoint = pm.joint(n=str(self.Naming) + "__jnt__01", p=pos, rad=self.RadiusJnt)

                self.oCollJoints.append(myjoint)

            # To put the joints at the same position of the locators
            for locators, joints in zip(self.oCollLoc, self.oCollJoints):
                ptCon = pm.pointConstraint(locators, joints)
                pm.delete(ptCon)

            "OPTIONAL if we want the joints to be chained "

            pm.select(self.oCollJoints)

            def chain_parent(oColljoint):
                for oParent, oChild in zip(oColljoint[0:-1], oColljoint[1:]):
                    try:
                        pm.parent(oChild, None)
                        pm.parent(oChild, oParent)
                    except:
                        continue

            chain_parent(pm.selected(type='transform'))

            # This line deletes the locators #
            # pm.delete(self.oCollLoc)

            #This line Orient joints #
            pm.select(self.oCollJoints)
            pm.joint(e=1, oj='xyz', secondaryAxisOrient='yup', ch=True)
            pm.select(cl=True)

            #Orient the last joint to the world#
            self.selLastJnt = pm.select(self.oCollJoints[-1])
            pm.joint(e=1, oj='none')
            pm.delete(self.oCollLoc)

    @undo
    @changeColor(col=(1, 1, 0.236))
    def fk_shape_setup(self):
        """
        Fk chain setup by parenting the shape to the joint
        Source: adb_utils.rig_utils.Class__FkShapes script
        """
        RadiusCtrl = float(self.slider_ctrl_rad_LineEdit.text())
        normals = self.ctrl_normals_lineEdit.text()
        Normalsctrl = tuple(normals.replace('-', ''))

        self.fk = adbFkShape.FkShape(listJoint=pm.selected())
        self.fk.shapeSetup(_radius=RadiusCtrl,
                           normalsCtrl=Normalsctrl
                           )

        return fk.getJoints

    @undo
    def delete_fk_shape_setup(self):
        """
        Delete the Fk chain setup
        Source: adb_utils.rig_utils.Class__FkShapes script
        """
        adb.fk_shape_setup(type="delete", listJoint=pm.selected())

    @undo
    @changeColor(col=(1, 1, 0.236))
    def fk_setup(self):
        self.RadiusCtrl = float(self.slider_ctrl_rad_LineEdit.text())
        normals = self.ctrl_normals_lineEdit.text()
        self.Normalsctrl = tuple(normals.replace('-', ''))
        listJoint = pm.selected()

        def CreateCircles():
            CurveColl = []
            for joint in listJoint:
                myname = '{}'.format(joint)
                new_name = myname.split('__jnt__')[0] + '__ctrl__'

                curve = mc.circle(nr=self.Normalsctrl,  n=new_name, r=self.RadiusCtrl)[0]
                CurveColl.append(curve)

            for oJoint, oCurve in zip(listJoint, CurveColl):
                pm.matchTransform(oCurve, oJoint, pos=True, rot=True)
                pm.parentConstraint(oCurve, oJoint, mo=True)

            return CurveColl

        def chain_parent(subject):
            for oParent, oChild in zip(subject[0:-1], subject[1:]):
                try:
                    pm.parent(oChild, None)
                    pm.parent(oChild, oParent)
                except:
                    continue

        def makeroot_func(subject=pm.selected()):
            pm.select(subject)
            oColl = pm.selected()
            newSuffix = 'root__grp'

            for each in oColl:
                try:
                    suffix = each.name().split('__')[-2]
                    cutsuffix = '__{}__'.format(suffix)
                except:
                    suffix, cutsuffix = '', ''
                oRoot = pm.group(n=each.name().replace(cutsuffix, '') + '_{}__{}__'.format(suffix, newSuffix), em=True)

                for i in range(4):
                    oRoot.rename(oRoot.name().replace('___', '__'))
                oRoot.setTranslation(each.getTranslation(space='world'), space='world')
                oRoot.setRotation(each.getRotation(space='world'), space='world')
                try:
                    pm.parent(oRoot, each.getParent())
                except:
                    pass
                pm.parent(each, oRoot)
                pm.setAttr(oRoot.v, keyable=False, cb=False)
                # oRoot.v.lock()
            pm.select(oRoot)
            return oRoot

        # -----------------------------------
        #   BUILD FK SETUP
        # -----------------------------------

        controls = CreateCircles()
        chain_parent(controls)
        makeroot_func(controls)

        return(controls)

    @undo
    def joint_on_curve(self):
        if self.jnt_checkbx.checkState() == QtCore.Qt.Unchecked and self.curve_checkbx.checkState() == QtCore.Qt.Unchecked:

            curveSel = pm.selected()[0]

            self.RadiusJnt = float(self.slider_jnt_rad_LineEdit.text())
            self.Naming = self.name_LineEdit.text()

            self.interval = int(self.slider_int_LineEdit.text())
            self.curve = pm.selected()

            self.all_jnts = []
            self.all_motionPath = []
            self.Pos = []

            for i in range(int(self.interval)):
                _joint = pm.joint(rad=self.RadiusJnt, n=str(self.Naming))
                pm.parent(_joint, w=True)

                self.all_jnts.append(_joint)

                _motionPathNode = pm.pathAnimation(self.curve, _joint, upAxis='y', fractionMode=True,
                                                   worldUpType="vector",
                                                   inverseUp=False, inverseFront=False, follow=True, bank=False, followAxis='x',
                                                   worldUpVector=(0, 1, 0))

                self.all_motionPath.append(_motionPathNode)

            # New interval value for the Function
            Nintervalls = int(self.interval) - 1

            for i in range(0, Nintervalls):
                factor = 1 / float((Nintervalls))

                oPos = factor * i
                self.Pos.append(oPos)
            self.Pos.append(1)

            for oPosition, oMotionPath in zip(self.Pos, self.all_motionPath):
                pm.PyNode(oMotionPath).uValue.set(oPosition)

            _dup = pm.duplicate(self.all_jnts[-1])

            # delete animation
            for path in self.all_motionPath:
                _motion_uvalue_node = [x for x in pm.listConnections(path + '.uValue', s=1)]
                pm.delete(_motion_uvalue_node)

            pm.select(None)

            # Cleaning the scene
            pm.delete(_dup)
            pm.delete(self.all_motionPath)

            for joint in self.all_jnts:
                joint.jointOrientX.set(0)
                joint.jointOrientY.set(0)
                joint.jointOrientZ.set(0)

                joint.rx.set(0)
                joint.ry.set(0)
                joint.rz.set(0)

        if self.jnt_checkbx.checkState() == QtCore.Qt.Checked and self.curve_checkbx.checkState() == QtCore.Qt.Unchecked:
            curveSel = pm.selected()[0]

            self.RadiusJnt = float(self.slider_jnt_rad_LineEdit.text())
            self.Naming = self.name_LineEdit.text()

            self.interval = int(self.slider_int_LineEdit.text())
            self.curve = pm.selected()

            self.all_jnts = []
            self.all_motionPath = []
            self.Pos = []

            for i in range(int(self.interval)):
                _joint = pm.joint(rad=self.RadiusJnt, n=str(self.Naming))
                pm.parent(_joint, w=True)

                self.all_jnts.append(_joint)

                _motionPathNode = pm.pathAnimation(self.curve, _joint, upAxis='y', fractionMode=True,
                                                   worldUpType="vector",
                                                   inverseUp=False, inverseFront=False, follow=True, bank=False, followAxis='x',
                                                   worldUpVector=(0, 1, 0))

                self.all_motionPath.append(_motionPathNode)

            # New interval value for the Function
            Nintervalls = int(self.interval) - 1

            for i in range(0, Nintervalls):
                factor = 1 / float((Nintervalls))

                oPos = factor * i
                self.Pos.append(oPos)
            self.Pos.append(1)

            for oPosition, oMotionPath in zip(self.Pos, self.all_motionPath):
                pm.PyNode(oMotionPath).uValue.set(oPosition)

            _dup = pm.duplicate(self.all_jnts[-1])

            # delete animation
            for path in self.all_motionPath:
                _motion_uvalue_node = [x for x in pm.listConnections(path + '.uValue', s=1)]
                pm.delete(_motion_uvalue_node)

            pm.select(None)

            # Cleaning the scene
            pm.delete(_dup)
            pm.delete(self.all_motionPath)

            # OPTIONAL if we want the joints to be chained
            pm.select(self.all_jnts[:])
            for oParent, oChild in zip(pm.selected()[0:-1], pm.selected()[1:]):
                pm.parent(oChild, None)
                pm.parent(oChild, oParent)

        if self.jnt_checkbx.checkState() == QtCore.Qt.Unchecked and self.curve_checkbx.checkState() == QtCore.Qt.Checked:

            curveSel = pm.selected()[0]

            self.RadiusJnt = float(self.slider_jnt_rad_LineEdit.text())
            self.Naming = self.name_LineEdit.text()

            self.interval = int(self.slider_int_LineEdit.text())
            self.curve = pm.selected()

            self.all_jnts = []
            self.all_motionPath = []
            self.Pos = []

            for i in range(int(self.interval)):
                _joint = pm.joint(rad=self.RadiusJnt, n=str(self.Naming))
                pm.parent(_joint, w=True)

                self.all_jnts.append(_joint)

                _motionPathNode = pm.pathAnimation(self.curve, _joint, upAxis='y', fractionMode=True,
                                                   worldUpType="vector",
                                                   inverseUp=False, inverseFront=False, follow=True, bank=False, followAxis='x',
                                                   worldUpVector=(0, 1, 0))

                self.all_motionPath.append(_motionPathNode)

            # New interval value for the Function
            Nintervalls = int(self.interval) - 1

            for i in range(0, Nintervalls):
                factor = 1 / float((Nintervalls))

                oPos = factor * i
                self.Pos.append(oPos)
            self.Pos.append(1)

            for oPosition, oMotionPath in zip(self.Pos, self.all_motionPath):
                pm.PyNode(oMotionPath).uValue.set(oPosition)

            _dup = pm.duplicate(self.all_jnts[-1])

            # delete animation
            for path in self.all_motionPath:
                _motion_uvalue_node = [x for x in pm.listConnections(path + '.uValue', s=1)]
                pm.delete(_motion_uvalue_node)

            pm.select(None)

            # Cleaning the scene
            pm.delete(_dup)
            pm.delete(self.all_motionPath)
            pm.delete(curveSel)

            for joint in self.all_jnts:
                joint.jointOrientX.set(0)
                joint.jointOrientY.set(0)
                joint.jointOrientZ.set(0)

                joint.rx.set(0)
                joint.ry.set(0)
                joint.rz.set(0)

        if self.jnt_checkbx.checkState() == QtCore.Qt.Checked and self.curve_checkbx.checkState() == QtCore.Qt.Checked:
            curveSel = pm.selected()[0]

            self.RadiusJnt = float(self.slider_jnt_rad_LineEdit.text())
            self.Naming = self.name_LineEdit.text()

            self.interval = int(self.slider_int_LineEdit.text())
            self.curve = pm.selected()

            self.all_jnts = []
            self.all_motionPath = []
            self.Pos = []

            for i in range(int(self.interval)):
                _joint = pm.joint(rad=self.RadiusJnt, n=str(self.Naming))
                pm.parent(_joint, w=True)

                self.all_jnts.append(_joint)

                _motionPathNode = pm.pathAnimation(self.curve, _joint, upAxis='y', fractionMode=True,
                                                   worldUpType="vector",
                                                   inverseUp=False, inverseFront=False, follow=True, bank=False, followAxis='x',
                                                   worldUpVector=(0, 1, 0))

                self.all_motionPath.append(_motionPathNode)

            # New interval value for the Function
            Nintervalls = int(self.interval) - 1

            for i in range(0, Nintervalls):
                factor = 1 / float((Nintervalls))

                oPos = factor * i
                self.Pos.append(oPos)
            self.Pos.append(1)

            for oPosition, oMotionPath in zip(self.Pos, self.all_motionPath):
                pm.PyNode(oMotionPath).uValue.set(oPosition)

            _dup = pm.duplicate(self.all_jnts[-1])

            # delete animation
            for path in self.all_motionPath:
                _motion_uvalue_node = [x for x in pm.listConnections(path + '.uValue', s=1)]
                pm.delete(_motion_uvalue_node)

            pm.select(None)

            # Cleaning the scene
            pm.delete(_dup)
            pm.delete(self.all_motionPath)
            pm.delete(curveSel)

            # OPTIONAL if we want the joints to be chained
            pm.select(self.all_jnts[:])
            for oParent, oChild in zip(pm.selected()[0:-1], pm.selected()[1:]):
                pm.parent(oChild, None)
                pm.parent(oChild, oParent)

    def keep_motion_path(self):
        curveSel = pm.selected()[0]

        self.RadiusJnt = float(self.slider_jnt_rad_LineEdit.text())
        self.Naming = self.name_LineEdit.text()

        self.interval = int(self.slider_int_LineEdit.text())
        self.curve = pm.selected()

        self.all_jnts = []
        self.all_motionPath = []
        self.Pos = []

        for i in range(int(self.interval)):
            _joint = pm.joint(rad=self.RadiusJnt, n=str(self.Naming))
            pm.parent(_joint, w=True)
            adb.makeroot_func(_joint)

            self.all_jnts.append(_joint)

            double_linears_nodes = []
            _motionPathNode = pm.pathAnimation(self.curve,  _joint.getParent(), upAxis='y', fractionMode=True,
                                               worldUpType="vector",
                                               inverseUp=False, inverseFront=False, follow=True, bank=False, followAxis='x',
                                               worldUpVector=(0, 1, 0))

            ## Delete double Linear nodes
            for axis in 'xyz':
                double_linear = pm.listConnections(_motionPathNode + '.{}Coordinate'.format(axis))[0]
                double_linears_nodes.append(double_linear)                
            pm.delete(double_linears_nodes)     
                          
            for axis in 'xyz':
                # pm.cycleCheck(e=0)
                pm.connectAttr('{}.{}Coordinate'.format(_motionPathNode, axis), '{}.t{}'.format(_joint.getParent(), axis), f=1)
                    
                    
            self.all_motionPath.append(_motionPathNode)
        # New interval value for the Function
        Nintervalls = int(self.interval) - 1

        for i in range(0, Nintervalls):
            factor = 1 / float((Nintervalls))

            oPos = factor * i
            self.Pos.append(oPos)
        self.Pos.append(1)

        for oPosition, oMotionPath in zip(self.Pos, self.all_motionPath):
            pm.PyNode(oMotionPath).uValue.set(oPosition)

        _dup = pm.duplicate(self.all_jnts[-1])

        # delete animation
        for path in self.all_motionPath:
            _motion_uvalue_node = [x for x in pm.listConnections(path + '.uValue', s=1)]
            pm.delete(_motion_uvalue_node)

        pm.select(None)

        # Cleaning the scene
        pm.delete(_dup)

    def delete_motion_path(self):
        curveSel = pm.selected()[0]
        old_name = curveSel.name()

        _dup_curve = pm.duplicate(curveSel)
        pm.delete(curveSel)
        pm.rename(_dup_curve, old_name)


# ==================================
#  UI BUILD
# ==================================


ui = None
ui_name = '{}WorkspaceControl'.format(JointGeneratorTool.UI_NAME)


def getTraceback(last=False):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb = traceback.format_exception(exc_type, exc_value, exc_traceback)
    if last:
        lasttb = []
        lasttb.append(tb[0])
        for trace in tb[2:]:
            lasttb.append(trace)
        tb = lasttb
    return ''.join(tb)


def printError(error):
    if not isinstance(error, str):
        return

    error = error.lstrip('\n').rstrip('\n')
    error = error.replace('\n', '\n# ')
    error = '\n# {}\n'.format(error)
    print error


def printTraceback():
    printError(getTraceback())


def deleteDockControl():
    if mc.about(apiVersion=True) < 201700:
        if mc.dockControl(ui_name, exists=True):
            mc.deleteUI(ui_name)
    else:
        if mc.workspaceControl(ui_name, exists=True):
            mc.deleteUI(ui_name)


def showUI():
    JointGeneratorTool.show_dialog()


def resetUI():
    global ui
    try:
        deleteDockControl()
        ui = JointGeneratorTool()
    except Exception:
        ui = None
        printTraceback()
        return

    ui.show(dockable=True)
    return ui


# showUI()
