# ------------------------------------------------------
# adbrower Copy Weight Tool
# -- Method Rigger (Maya)
# -- Version 2.0.0 
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

import traceback

try:
    import PySide2.QtCore as QtCore
    import PySide2.QtGui as QtGui
    import PySide2.QtWidgets as QtWidgets
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2 import QtGui
except:
    print "fail to import PySide2, %s" % __file__
    import PySide.QtCore as QtCore
    import PySide.QtGui as QtGui
    import PySide.QtGui as QtWidgets
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide import QtGui

try:
    # future proofing for Maya 2017.
    from shiboken2 import wrapInstance
except ImportError:
    from shiboken import wrapInstance

import pymel.core as pm
import pymel.core.datatypes as dt
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

import os

#-----------------------------------
#  DECORATORS
#----------------------------------- 

from adbrower import undo
from adbrower import changeColor

#-----------------------------------
#  CLASS
#----------------------------------- 

class IkFk_switch(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(IkFk_switch, self).__init__(parent=maya_main_window())
        
        self.setObjectName('adb_Rig_Tool')        
        self.version =  4.0
        self.setWindowTitle('adbrower - IK FK Switch Tool' + '  v' + str(self.version))
       
        self.setFixedWidth(400)
        self.setFixedHeight(250)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        ## Main layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(*[5]*4)        
        self.main_layout.setSpacing(2)  

        self.create_Button()
        self.create_layout()

        
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

                ['Create the Switch Control',   self.CreateSwitchCtrl,              1,      self.colorLightGrey,        self.colorDarkGrey2],
                ['IK -FK Switch Set Up',        self.MainSetup,                     1,      self.colorLightGrey,        self.colorDarkGrey2],
                
                ['FK Visibility Set Up',        self.FKVisibiltySetUp,              2,      self.colorLightGrey,        self.colorDarkGrey2],
                ['IK Visibility Set Up',        self.IKVisibiltySetUp,              2,      self.colorLightGrey,        self.colorDarkGrey2],

        ]


        self.buttons = {}        
        for buttonName,buttonFunction, _,labColor, bgColor in self.buttonAndFunctions:
            self.buttons[buttonName] = QtWidgets.QPushButton(buttonName)
            self.buttons[buttonName].clicked.connect(buttonFunction)
            self.buttons[buttonName].setFixedHeight(30)
            self.buttons[buttonName].setStyleSheet(
                    'padding:4px; text-align:Center; font: normal; color:{}; background-color:{};'.format(labColor,bgColor))


        ## Build Buttons
        self.buttons1 = [button for button, _, groupNumber,labColor, bgColor in self.buttonAndFunctions if groupNumber == 1] 
        self.buttons2 = [button for button, _, groupNumber,labColor, bgColor in self.buttonAndFunctions if groupNumber == 2] 
 


    def create_layout(self):
        """ all layouts """
        

        def addLineL(Layout):
            line = QFrame()
            line.setFrameShape(QFrame.HLine)  
            Layout.addWidget(line)         
            return line 

        def addLine():
            line = QFrame()
            line.setFrameShape(QFrame.HLine)          
            return line        
       
        def addText(message, alignement = QtCore.Qt.AlignCenter, height=30, bold = False):
            myFont=QtGui.QFont()
            myFont.setBold(bold)
            
            text = QtWidgets.QLabel(message)
            text.setAlignment(alignement) 
            text.setFixedHeight(height)
            text.setFont(myFont)
            text.setStyleSheet('color:{};'.format(self.colorOrange))

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

           
       
        #=======================
        # OPTIONS UI 
        #=======================
        
        option_layout = QtWidgets.QGridLayout()
        self.name_LineEdit = QtWidgets.QLineEdit()
        self.name_Label = QtWidgets.QLabel(' Name           >>')
        self.name2_Label = QtWidgets.QLabel('Full Name     >>')
        self.name2_Label.setStyleSheet("padding-top: 5px;")
        self.choose = addText('Choose : ')
        self.choose.setStyleSheet("padding-right: 50px;")

        self.name2_LineEdit = QtWidgets.QLineEdit()
               
        self.tras_checkbx = QtWidgets.QCheckBox('Translate')              
        self.tras_checkbx.setStyleSheet("color:{}; padding-top: 10px; padding-bottom: 10px;".format(self.colorOrange))

        self.rot_checkbx = QtWidgets.QCheckBox('Rotation')        
        self.rot_checkbx.setStyleSheet("color:{}; padding-left: 32px; padding-top: 10px; padding-bottom: 10px;".format(self.colorOrange))
        self.rot_checkbx.setChecked(1)
    
        option_layout.addWidget(self.name_Label, 0,0,1,1) 
        option_layout.addWidget(self.name_LineEdit, 0,1,1,3) 

        option_layout.addWidget(self.name2_Label, 1,0,1,1) 
        option_layout.addWidget(self.name2_LineEdit, 1,1,1,3) 
        
        option_layout.addWidget(self.choose, 2,0)
        option_layout.addWidget(self.tras_checkbx, 2,1)
        option_layout.addWidget(self.rot_checkbx, 2,2)
        
        self.name_LineEdit.setMaximumSize(QtCore.QSize(300, 20))

       
        ## Groups
        group1 = QtWidgets.QGroupBox('Options') 
        group1.setFlat(True)
        group1.setLayout(option_layout)


        #=======================
        # BUILD UI 
        #=======================

       
        build_layout_Grid = QtWidgets.QGridLayout()
        build_layout_Grid.setContentsMargins(*[2]*4)

        for buttonName, index, in zip(self.buttons1[:1], range(2)):
            build_layout_Grid.addWidget(self.buttons[buttonName], 0,0,1,2, index)

        for buttonName, index, in zip(self.buttons1[1:], range(2)):
            build_layout_Grid.addWidget(self.buttons[buttonName], 1,0,1,2, index)
            self.buttons[buttonName].setFixedHeight(35)
       
        for buttonName, index, in zip(self.buttons2, range(2)):
            build_layout_Grid.addWidget(self.buttons[buttonName], 2, index)
    
  


#=======================
# MAIN LAYOUT BUILD
#=======================

        # self.main_layout.addWidget(instructions_label)          
        self.main_layout.addWidget(group1)          
 
        self.main_layout.addLayout(build_layout_Grid)  
        
         
              



#-----------------------------------
#  UI FUNCTIONS
#----------------------------------- 

    def empty(self):
        pass


    def CreateSwitchCtrl(self):
        try:
            Naming = self.name_LineEdit.text()
            self.CtrlName = Naming + '_IK_FK__ctrl__'

            Ctrl = pm.selected()[0]        
            Ctrl.rename(self.CtrlName)
            Ctrl.addAttr('IK_FK_Switch', keyable=True, attributeType='enum', en="IK:FK")
            # Lock and Hide all parameters #
            Ctrl.setAttr("tx", lock=True, channelBox=False, keyable=False)
            Ctrl.setAttr("ty", lock=True, channelBox=False, keyable=False)
            Ctrl.setAttr("tz", lock=True, channelBox=False, keyable=False)
            Ctrl.setAttr("rx", lock=True, channelBox=False, keyable=False)
            Ctrl.setAttr("ry", lock=True, channelBox=False, keyable=False)
            Ctrl.setAttr("rz", lock=True, channelBox=False, keyable=False)
            Ctrl.setAttr("sx", lock=True, channelBox=False, keyable=False)
            Ctrl.setAttr("sy", lock=True, channelBox=False, keyable=False)
            Ctrl.setAttr("sz", lock=True, channelBox=False, keyable=False)
            Ctrl.setAttr("v", lock=True, channelBox=False, keyable=False)

        except IndexError:            
            pm.warning(' Fulfill the UI!')


    def Create3jointsChain(self):
        
        self.oColljoints = pm.selected()
        
        fullname  = self.name2_LineEdit.text()
        self.IKFK_ctrl = fullname + ".IK_FK_Switch"
             
        
        ## Trouver la longeur de la chaine de joints ##
        # self.oColljointsLen = len(list([x for x in self.oColljoints]))


        for joint in self.oColljoints:
            jntradius = joint.radius.get()

        ## Creation de la chaine IK
        self.IKjointsCh = pm.duplicate(self.oColljoints)
        pm.select(self.IKjointsCh)
        
        ## Setter le radius de mes joints ##
        for joint in self.IKjointsCh:
            joint.radius.set(jntradius + 0.2)
            IKName = joint.split('jnt')[0] + '_jnt__IK__0'
        
        ## Renommer les joints ##
        for i, each in enumerate(self.IKjointsCh):
            each.rename(IKName + str(i+1))
            
            
            pm.select(self.IKjointsCh)
        

        ## Changer la couleur  de la chaine de joints ##
            ctrlSet = pm.selected()
            for ctrl in ctrlSet:
                if pm.objectType(ctrl) == "joint":
                    for each in  ctrlSet:   
                        ctrl = pm.PyNode(each)
                        ctrl.overrideEnabled.set(1)
                        ctrl.overrideRGBColors.set(0)
                        ctrl.overrideColor.set(21)

            

        ## Creation de la chaine FK
        self.FKjointsCh = pm.duplicate(self.oColljoints)
        pm.select(self.FKjointsCh)
        
        ## Setter le radius de mes joints ##
        for joint in self.FKjointsCh:
            joint.radius.set(jntradius + 0.3)
            FKName = joint.split('jnt')[0] + '_jnt__FK__0'
        
        ## Renommer les joints ##
        for i, each in enumerate(self.FKjointsCh):
            each.rename(FKName + str(i+1))
            
            
            pm.select(self.FKjointsCh)
        

        ## Changer la couleur  de la chaine de joints ##
            ctrlSet = pm.selected()
            for ctrl in ctrlSet:
                if pm.objectType(ctrl) == "joint":
                    for each in  ctrlSet:   
                        ctrl = pm.PyNode(each)
                        ctrl.overrideEnabled.set(1)
                        ctrl.overrideRGBColors.set(0)
                        ctrl.overrideColor.set(14)

    def CreateSwitchSetup(self):
        """Connect the IK and FK joint chain with a blendColor to the Blend joint chain """
        
        fullname  = self.name2_LineEdit.text()
        self.IKFK_ctrl = fullname + ".IK_FK_Switch"
        
             
        """## CHOICE FOR TRANSLATE"""
        if self.tras_checkbx.checkState() ==  QtCore.Qt.Checked and self.rot_checkbx.checkState() == QtCore.Qt.Unchecked:       

            self.BlendColorColl_T = [pm.shadingNode('blendColors',asUtility=1, n="Translate_BC_01") for x in self.oColljoints]

            ## Connect the FK in the Color 1
            for oFK, oBlendColor in zip (self.FKjointsCh,self.BlendColorColl_T):
                pm.PyNode(oFK).tx >> pm.PyNode(oBlendColor).color1R
                pm.PyNode(oFK).ty >> pm.PyNode(oBlendColor).color1G
                pm.PyNode(oFK).tz >> pm.PyNode(oBlendColor).color1B

            ## Connect the IK in the Color 2
            for oIK, oBlendColor in zip (self.IKjointsCh,self.BlendColorColl_T):
                pm.PyNode(oIK).tx >> pm.PyNode(oBlendColor).color2R
                pm.PyNode(oIK).ty >> pm.PyNode(oBlendColor).color2G
                pm.PyNode(oIK).tz >> pm.PyNode(oBlendColor).color2B
                
                            
            ## Connect the BlendColor node in the Blend joint chain        
            for oBlendColor, oBlendJoint in zip (self.BlendColorColl_T,self.oColljoints):
                pm.PyNode(oBlendColor).outputR  >> pm.PyNode(oBlendJoint).tx
                pm.PyNode(oBlendColor).outputG  >> pm.PyNode(oBlendJoint).ty
                pm.PyNode(oBlendColor).outputB  >> pm.PyNode(oBlendJoint).tz


            for oBlendColor in self.BlendColorColl_T:
                pm.PyNode(oBlendColor).blender.set(1)

            ## Setting up the blending according to the IK-FK control
            self.RemapValueColl = [pm.shadingNode('remapValue',asUtility=1, n="Blend_RV_01") for x in self.BlendColorColl_T]

            ## Connect the Remap Values to Blend Colors
            for oRemapValue,oBlendColor in zip (self.RemapValueColl,self.BlendColorColl_T):            
                pm.PyNode(oRemapValue).outValue >> pm.PyNode(oBlendColor).blender

            ## Connect the IK -FK Control to Remap Value
            for each in self.RemapValueColl:
                pm.PyNode(self.IKFK_ctrl) >> pm.PyNode(each).inputValue
                
                
        """## CHOICE FOR ROTATE"""
        if self.tras_checkbx.checkState() == QtCore.Qt.Unchecked and self.rot_checkbx.checkState() ==  QtCore.Qt.Checked:   
                                   
            self.BlendColorColl_R = [pm.shadingNode('blendColors',asUtility=1, n="Roration_BC_01") for x in self.oColljoints]

            ## Connect the FK in the Color 1
            for oFK, oBlendColor in zip (self.FKjointsCh,self.BlendColorColl_R):
                pm.PyNode(oFK).rx >> pm.PyNode(oBlendColor).color1R
                pm.PyNode(oFK).ry >> pm.PyNode(oBlendColor).color1G
                pm.PyNode(oFK).rz >> pm.PyNode(oBlendColor).color1B

            ## Connect the IK in the Color 2
            for oIK, oBlendColor in zip (self.IKjointsCh,self.BlendColorColl_R):
                pm.PyNode(oIK).rx >> pm.PyNode(oBlendColor).color2R
                pm.PyNode(oIK).ry >> pm.PyNode(oBlendColor).color2G
                pm.PyNode(oIK).rz >> pm.PyNode(oBlendColor).color2B
                
                            
            ## Connect the BlendColor node in the Blend joint chain        
            for oBlendColor, oBlendJoint in zip (self.BlendColorColl_R,self.oColljoints):
                pm.PyNode(oBlendColor).outputR  >> pm.PyNode(oBlendJoint).rx
                pm.PyNode(oBlendColor).outputG  >> pm.PyNode(oBlendJoint).ry
                pm.PyNode(oBlendColor).outputB  >> pm.PyNode(oBlendJoint).rz


            for oBlendColor in self.BlendColorColl_R:
                pm.PyNode(oBlendColor).blender.set(1)

            ## Setting up the blending according to the IK-FK control
            self.RemapValueColl = [pm.shadingNode('remapValue',asUtility=1, n="Blend_RV_01") for x in self.BlendColorColl_R ]

            ## Connect the Remap Values to Blend Colors
            for oRemapValue,oBlendColor in zip (self.RemapValueColl,self.BlendColorColl_R):            
                pm.PyNode(oRemapValue).outValue >> pm.PyNode(oBlendColor).blender

            ## Connect the IK -FK Control to Remap Value
            for each in self.RemapValueColl:
                pm.PyNode(self.IKFK_ctrl) >> pm.PyNode(each).inputValue




    def FKVisibiltySetUp(self):
        
        fullname  = self.name2_LineEdit.text()
        self.IKFK_ctrl = fullname + ".IK_FK_Switch"
             
        " Select the Fk Controls  "
        self.oColl_Ctrls = pm.selected()
        
            
        ## Connect the IK -FK Control to FK controls's visibility
        for each in  self.oColl_Ctrls:
            pm.PyNode(self.IKFK_ctrl) >> pm.PyNode(each).visibility


    def IKVisibiltySetUp(self):  
        
        fullname  = self.name2_LineEdit.text()
        self.IKFK_ctrl = fullname + ".IK_FK_Switch"
              
        " Select the Ik Controls  "
        self.oColl_Ctrls = pm.selected()
        
        self.ReverseColl = [pm.shadingNode('reverse',asUtility=1, n="FK_Visibility_Rev_01") for x in self.oColl_Ctrls]
                  
        ## Connect the IK -FK Control to Reverse
        for each in self.ReverseColl:
            pm.PyNode(self.IKFK_ctrl) >> pm.PyNode(each).inputX


        ## Connect the Reverse nodes to IK controls's visibility
        for oReverse,oFkctrls in zip (self.ReverseColl ,self.oColl_Ctrls):            
            pm.PyNode(oReverse).outputX  >> pm.PyNode(oFkctrls).visibility

    def MainSetup(self):
        try:
            self.Create3jointsChain()
            self.CreateSwitchSetup()
        except TypeError:
            pass



#-----------------------------------
#  SLOTS
#----------------------------------- 





def maya_main_window():
    """Return the Maya main window widget as a Python object."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def ui():
	global tools_cw_ui
	try:
		tools_cw_ui.deleteLater()
	except:
		pass
	tools_cw_ui = IkFk_switch()
	tools_cw_ui.show() 


# ui()
