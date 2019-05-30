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

import getpass
import os
import ConfigParser
import maya.cmds as mc
import maya.mel as mel
import sys



def maya_main_window():
    """Return the Maya main window widget as a Python object."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

#-----------------------------------
#  CLASS
#----------------------------------- 


class mainLayout(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(mainLayout, self).__init__(parent = maya_main_window())

        
        self.setObjectName('test')        
        self.version =  2.0
        self.setWindowTitle('test Win' + '  v' + str(self.version))
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setFixedWidth(370)
            

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(*[5]*4)        
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)
        
        




def showUI():
    # Make sure the UI is deleted before recreating
	global tools_cw_ui
	try:
		tools_cw_ui.deleteLater()
	except:
		pass
	tools_cw_ui = mainLayout()
	tools_cw_ui.show()      
    
showUI()

