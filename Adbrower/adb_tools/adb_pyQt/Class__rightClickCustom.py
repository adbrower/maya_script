import maya.mel as mel
import pymel.core as pm
from PySide2 import QtCore, QtGui, QtWidgets
from CollDict import pysideColorDic as pyQtDic

#-----------------------------------
#  CLASS
#----------------------------------- 

class CustomQPushButton(QtWidgets.QPushButton):
    def __init__(self, name, actionsList = None, parent = None):
        super(CustomQPushButton, self).__init__(name)
        """
        Custom QpushButton with a right clicked options
        
        @param name: (string) Name / text on the button
        @param actionsList: (List) name of the right clicked action
        
        Exemple"
                customBtn = adbRC.RightClickMenuButton('QQQ', ['coucou', 'salut'])
                customBtn.clicked.connect(self.test2)
                customBtn.action['coucou'].triggered.connect(self.test)
        """

        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.name = name
        self.actionsList = actionsList
        self.colorText = ''
        self.backgroundColor = ''
        self.height = 27
        self.width = ''
        
        self.action = self.addMenuActions()
        self.initCustomButton()
   
    def initCustomButton(self):
        self.setStyleSheet(
            'padding:4px; text-align:Center; font: normal; color:{};  background-color:{};'.format(self.colorText, self.backgroundColor))
        self.setFixedHeight(self.height)
        
        if self.width == '':
            pass
        else:
            self.setFixedWidth(self.width)

    def addMenuActions(self):
        if self.actionsList is not None:
            self.actions = {}
            for actionName in self.actionsList:
                self.actions[actionName] = QtWidgets.QWidgetAction(self)
                self.actions[actionName].setText(actionName)
                self.addAction(self.actions[actionName]) 
            return self.actions
        else:
            return None
    
    def addButtonActions(self, actionsList):
        """
        Add actions after the button is created
        return a dict with all the options
        """
        if actionsList is not None:
            actions = {}
            for actionName in actionsList:
                actions[actionName] = QtWidgets.QWidgetAction(self)
                actions[actionName].setText(actionName)
                self.addAction(actions[actionName]) 
        return actions
    
    
class AddButtonActions(object):
    """
    Add customs RightClicked Action on a QPushButton object
    
    example:
        dict = adbRC.AddButtonActions(self.buttons['Expand All'], ['Shapes', 'Skin Cluster']).actions
        dict['Shapes'].triggered.connect(self.test2)
    """
    def __init__(self, button, actionList):
        self.button = button
        self.actionsList = actionList

        self.button.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.actions = self.initAddActions()

    def initAddActions(self):
        actions = {}
        for actionName in self.actionsList:
            actions[actionName] = QtWidgets.QWidgetAction(self.button)
            actions[actionName].setText(actionName)
            self.button.addAction(actions[actionName])
        return actions 

