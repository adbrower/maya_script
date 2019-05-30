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

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin



#-----------------------------------
#  CLASS
#----------------------------------- 


class mainLayout(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    UI_NAME = 'test'
    def __init__(self,parent=None):
        super(mainLayout, self).__init__(parent = None)
        
        self.setObjectName(self.UI_NAME)        
        self.version =  2.0
        self.setWindowTitle('test Win' + '  v' + str(self.version))
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setFixedWidth(370)
            

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(*[5]*4)        
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)
        
        

#==================================
#  UI BUILD
#==================================


ui = None
ui_name = '{}WorkspaceControl'.format(mainLayout.UI_NAME)

def getTraceback(last=False):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb = traceback.format_exception(exc_type, exc_value, exc_traceback)
    if last:
        lasttb = []
        lasttb.append(tb[0]); 
        for trace in tb[2:]:
            lasttb.append(trace)
        tb = lasttb
    return ''.join(tb)

def printError(error):
    if not isinstance(error, str):
        return

    error = error.lstrip('\n').rstrip('\n')
    error = error.replace('\n','\n# ')
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


def showUI(build=None, force=False):
    global ui
    if ui and force:
        delete()

    if not ui:
        try:
            deleteDockControl()
            ui = mainLayout()            
        except Exception:
            ui = None
            printTraceback()
            return
        else:   
            try:     
                ui.loadModel(build)
            except Exception:
                pass
                
    ui.show(dockable=True)    
    return ui



showUI()