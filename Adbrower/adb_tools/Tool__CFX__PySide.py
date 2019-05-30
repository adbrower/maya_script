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
import subprocess
import ConfigParser
import maya.cmds as mc
import maya.mel as mel
import sys

#-----------------------------------
#  IMPORT CUSTOM
#----------------------------------- 

import adbrower
adb = adbrower.Adbrower()

import adb_pyQt.Class__frameLayout as adbFrameLayout
import adb_utils.adb_script_utils.Functions__Rivet as adbRivet
import CollDict

from CollDict import pysideColorDic 
from adbrower import lprint
from adbrower import flatList

#-----------------------------------
#  CLASS
#----------------------------------- 

version = '1.00'

class cfxToolbox(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(cfxToolbox, self).__init__(parent = maya_main_window())        

        self.currentCam=pm.lookThru(q=1)
        self.allCam = pm.listCameras(o=False, p = True)
        self.Original_startTime_value = 1001
        self.Original_endTime = self.getCurrentTimeSlider()
        self.playbast_path = None

        self.setObjectName('CFX_TOOLS_UI')    
        self.setWindowTitle('CFX Toolbox  v{}'.format(version))
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.resize(290, 900)
        # self.setFixedWidth(250)
            
    # -----------------------------
    # ---  Create scrollArea
    
        self.mainBox = QtWidgets.QVBoxLayout()
        self.mainBox.setContentsMargins(0,0,0,0)
        self.scroll_layout = QtWidgets.QScrollArea()
                
        self.mainBox.addWidget(self.scroll_layout)
        self.setLayout(self.mainBox)
        self.scroll_layout.setContentsMargins(0,0,0,0)
        self.scroll_layout.setWidgetResizable(True)
        self.scroll_layout.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.scroll_layout.setFrameShadow(QtWidgets.QFrame.Plain)
       
        self.scroll_widget = QtWidgets.QWidget()
        self.scroll_layout.setWidget(self.scroll_widget)


    # -----------------------------
    # ---  Main Layout
    
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(2,2,4,4)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)
        
        self.widgetsAndLayouts()      
        self.getOsDatas()         
        self.getRootsData() 
                          
        self.create_Button()
        self.populate()
        self.buildMainLayout()
        
        self.scroll_widget.setLayout(self.main_layout)


    def dock_ui( self ):
        '''Create and dock GUI.'''       
        # DEFINE ALLOWED DOCKING AREAS
        allowedAreas = ['right', 'left']

        # DELETE EXISTING PANEL LAYOUT IF IT EXISTS, THEN CREATE A NEW ONE
        if pm.paneLayout( 'CFX_Toolbox', q = True, ex = True):
            pm.deleteUI( 'CFX_Toolbox' )
        pm.paneLayout( 'CFX_Toolbox' ,configuration = 'single', w = 50)

        # DELETE DOCK CONTROL IF IT EXISTS, THEN CREATE A NEW ONE
        if pm.dockControl( 'cfx_ToolBox', q = 1, ex = 1 ):
            pm.deleteUI( 'cfx_ToolBox' )
        pm.dockControl( 'cfx_ToolBox', area = 'right', allowedArea = allowedAreas, content = 'CFX_Toolbox', l= 'CFX Toolbox  v{}'.format(version) )
        
        # PARENT WIDGIT TO PANEL LAYOUT
        pm.control( 'CFX_TOOLS_UI', e = True, p = 'CFX_Toolbox' )

    
    def getOsDatas(self):   
        ''' Get the files inside the path '''                    
        self.playbast_path = self.path_LineEdit.text()    
        _playblastFiles = os.listdir(self.playbast_path)
        self.playblastFiles = sorted(_playblastFiles)
        return self.playblastFiles

                
    def getRootsData(self):
        ''' Get the title of the Top Item '''
        roots = []
        for _file in self.playblastFiles:
            try:
                root = _file.split('_')[2]
                roots.append(root)                
            except:
                roots.append(_file)        
        self.roots = sorted(list(set(roots)))
        return self.roots


    def widgetsAndLayouts(self):      
       
        #------------------------------
        #--------- Predefine widgets     
                
        def addLineLayout(Layout):
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
            return text        

    #------------------------------
    #--------- Layouts        
    
        self.path_layout = QtWidgets.QHBoxLayout()                           
        self.text_top_layout = QtWidgets.QGridLayout() # ----- For Original start/end section
        self.button_top_layout = QtWidgets.QVBoxLayout()
        self.button_top_layout.setContentsMargins(4,4,4,4)
        self.text_camera_layout = QtWidgets.QHBoxLayout() # ----- For Cameras text section
        self.playblastMan_layout = QtWidgets.QVBoxLayout()

        self.bottons_layout = QtWidgets.QHBoxLayout()    
        self.bottons_layout2 = QtWidgets.QHBoxLayout()  
        
        self.cameraFunctions_layout = QtWidgets.QVBoxLayout()
        self.cameraFunctions_layout.setContentsMargins(1,1,1,1)
        self.cameraFunctions_Hlayout = QtWidgets.QHBoxLayout() # ----- For Refresh and Reset Buttons
        self.blendshape_layout = QtWidgets.QGridLayout()
        self.blendshapeButton_layout = QtWidgets.QHBoxLayout()
        self.blendshapeButton_layout2 = QtWidgets.QVBoxLayout()
        self.clothFunctions_layout = QtWidgets.QVBoxLayout()
        self.clothFunctions_doublelayout = QtWidgets.QGridLayout()
        
        ### QListWidget            
        self.presetListLeft = QtWidgets.QListWidget()
        self.presetListLeft.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)      
        self.presetListLeft.setMaximumHeight(100)      
        [self.presetListLeft.addItem(cam) for cam in self.allCam] # ---- add Alls cameras
        self.presetListLeft.itemDoubleClicked.connect(self.doubleClickedCamLeft)
        
        self.presetListRight = QtWidgets.QListWidget()
        self.presetListRight.setMaximumHeight(100) 
        self.presetListRight.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.presetListRight.itemDoubleClicked.connect(self.doubleClickedCamRight)        
        self.playblastList = QtWidgets.QListWidget()

        self.listBoxLayout = QtWidgets.QHBoxLayout() # ---- For the Qlist Widget
        self.listBoxLayout.addWidget(self.presetListLeft)
        self.listBoxLayout.addWidget(self.presetListRight)
        
        ### QCheckBox
        self.bls_checkbx = QtWidgets.QCheckBox('Blend blendshape position / world')
        self.bls_checkbx.setStyleSheet("color:{}; padding-left: 10px; padding-top: 10px; padding-bottom: 10px;".format(pysideColorDic['colorLightGrey']))
        
        ### QLineEdit
        self.originalStartFrame_LineEdit = QtWidgets.QLineEdit(str(self.Original_startTime_value))
        self.originalStartFrame_LineEdit.setMaximumSize(QtCore.QSize(50, 20))
        self.originalStartFrame_LineEdit.editingFinished.connect(self.OriginalStartFrameCC)
        
        self.originalEndFrame_LineEdit = QtWidgets.QLineEdit(str(self.Original_endTime))
        self.originalEndFrame_LineEdit.setMaximumSize(QtCore.QSize(50, 20))
        self.originalEndFrame_LineEdit.editingFinished.connect(self.OriginalEndFrameCC)
        
        self.blendshapeValue_LineEdit = QtWidgets.QLineEdit('1.00')
        self.blendshapeValue_LineEdit.setMaximumSize(QtCore.QSize(50, 20))
        
        self.path_LineEdit = QtWidgets.QLineEdit('/on/work/adbrower/sandbox/movies') 
        self.path_LineEdit.setStyleSheet("QLineEdit { background-color : #2E2E2E; }") 

                         
        ### Text        
        self.originalStartFrameText = addText('Original Start Frame :')
        self.originalEndFrameText = addText('Original End Frame :')
        self.allCamerasText = addText('All Cameras')
        self.selectedCamerasText = addText('Selected Cameras')
        self.blendshapeValueText = addText('Blendshapes Value :')
        self.pathText = addText('Path :')
        self.playblastManagerText = addText('Playblast Manager :')

        ## QFileDialog
        self.dial = QtWidgets.QFileDialog()
        
        ## QTreeWidget
        self.treeLayout = QVBoxLayout() 
        self.playTree = QTreeWidget()        
        self.playTree.setMinimumHeight(200)
        self.playTree.setMaximumHeight(300)

        self.playTree.setSelectionMode(self.playTree.ExtendedSelection)
        header = QTreeWidgetItem(["Playblast"])
        self.playTree.setHeaderItem(header)
        self.playTree.header().resizeSection(0, 300) ## ---- Colum Witdh
        self.treeLayout.addWidget(self.playTree)   
        self.playTree.itemDoubleClicked.connect(self.playblast_clic)   
        self.playTree.horizontalScrollBar().setSingleStep(25)             
   
                             
    #------------------------------
    #--------- FRAMELAYOUT
    
        self.playblastFrame = adbFrameLayout.frameLayout()
        self.playblastFrame.title = 'Playblast Functions'

        self.cameraFrame = adbFrameLayout.frameLayout()
        self.cameraFrame.title = 'Camera Functions'

        self.utilsFrame = adbFrameLayout.frameLayout()
        self.utilsFrame.title = 'CFX Utils'        
                        
        self.blendshapeFrame = adbFrameLayout.frameLayout()
        self.blendshapeFrame.title = 'Blendshapes Functions'
        
        self.clothsFrame = adbFrameLayout.frameLayout()
        self.clothsFrame.title = 'Cloth Functions'

        ## set text Color for all FrameLayouts
        for flayout in [self.playblastFrame,
                       self.cameraFrame,
                       self.blendshapeFrame,
                       self.clothsFrame,
                       self.utilsFrame,
                       
                        ]:            
            flayout.colorText = '#E5C651'
                                  
    #------------------------------
    #--------- BUILD LAYOUTS
    
        self.text_top_layout.addWidget(self.originalStartFrameText, 0,0,)
        self.text_top_layout.addWidget(self.originalStartFrame_LineEdit, 0,1)
        self.text_top_layout.addWidget(self.originalEndFrameText, 1,0,)
        self.text_top_layout.addWidget(self.originalEndFrame_LineEdit, 1,1,)
        
        self.text_camera_layout.addWidget(self.allCamerasText)
        self.text_camera_layout.addWidget(self.selectedCamerasText)

        self.path_layout.addWidget(self.pathText) 
        self.path_layout.addWidget(self.path_LineEdit)         
        self.playblastMan_layout.addWidget(self.playblastManagerText)         
        self.playblastMan_layout.addLayout(self.path_layout)          
        self.playblastMan_layout.addLayout(self.treeLayout)     
        self.playblastMan_layout.addLayout(self.bottons_layout)
        self.playblastMan_layout.addLayout(self.bottons_layout2)     
        self.playblastMan_layout.addStretch()         
    
        self.cameraFunctions_layout.addLayout(self.text_camera_layout)
        self.cameraFunctions_layout.addLayout(self.listBoxLayout)
        self.cameraFunctions_layout.addLayout(self.cameraFunctions_Hlayout)
        self.cameraFrame.addLayout(self.cameraFunctions_layout)
        
        self.blendshape_layout.addWidget(self.blendshapeValueText, 0,0)
        self.blendshape_layout.addWidget(self.blendshapeValue_LineEdit, 0,1)
        
        self.blendshapeFrame.addLayout(self.blendshape_layout)
        self.blendshapeFrame.addLayout(self.blendshapeButton_layout)
        self.blendshapeFrame.addLayout(self.blendshapeButton_layout2)
        
        self.utilsFrame.addWidget(self.bls_checkbx)
        self.clothsFrame.addLayout(self.clothFunctions_layout)
        self.clothsFrame.addLayout(self.clothFunctions_doublelayout)


    def create_Button(self):       
        ''' Create the buttons  '''  
        self.buttonAndFunctions = [
                # name,                             function ,          group number,           labelColor,                     backgroundColor,                 layout,               layout_coordinate
                ['Set Timeslider for Caches',   self.cachesTimeSlider,       1,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.button_top_layout,              ''],
                ['Reset Timeslider',            self.reset,                  1,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.button_top_layout,              ''],    
                
                ['Clean View  ',                self.cleanViewer,            2,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.playblastFrame,                 ''],
                ['Playblast',                   self.playbast_org,           2,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.playblastFrame,                 ''],
                ['Playblast Rewrite',           self.playbast_re,            2,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.playblastFrame,                 ''],               
                ['Playblast NEW VERSION',       self.playbast_ver,           2,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorGreen3'],      self.playblastFrame,                 ''],
                ['...',                         self.selectPath,             2,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.path_layout,                    ''],

                ['Expand / Collapse All',       self.expandAll,              2,    pysideColorDic['colorBlue'],        pysideColorDic['colorDarkGrey3'],   self.bottons_layout,                 ''],
                ['Delete',                      self.messageSelDelete,       2,    pysideColorDic['colorBlue'],        pysideColorDic['colorDarkGrey3'],   self.bottons_layout2,                ''],
                ['Delete All',                  self.messageAllDelete,       2,    pysideColorDic['colorBlue'],        pysideColorDic['colorDarkGrey3'],   self.bottons_layout2,                ''],
                                                                          
                ['Refresh',                     self.refreshCam,             3,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.cameraFunctions_Hlayout,        ''],
                ['Reset',                       self.presetListRight.clear,  3,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.cameraFunctions_Hlayout,        ''],
                ['Add Custom Cam',              self.AddCams,                3,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorBlue4'],       self.cameraFunctions_layout,         ''],
                ['Remove Custom Cam',           self.removeCam,              3,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorBlue4'],       self.cameraFunctions_layout,         ''],
                ['Toggle',                      self.toggleCam,              3,    pysideColorDic['colorBlack'],       pysideColorDic['colorBlue'],        self.cameraFunctions_layout,         ''],
                
                ['Apply',                       self.ActiveBLS_BA,           4,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.blendshapeButton_layout,        ''],
                ['Key',                         self.keyBls,                 4,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.blendshapeButton_layout,        ''],                
                ['Blendshape',                  self.createBls,              4,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.utilsFrame,                     ''],    
                ['Add Target',                  adb.addBlsTarget,           4,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.utilsFrame,                     ''],    
                ['Blend 2 Group',               self.blend2GrpBls,           4,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.utilsFrame,                     ''],
                ['Delete BLS',                  self.deleteBls,              4,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.utilsFrame,                     ''],
                ['Sticky From Face',            adbRivet.sticky_from_faces,  4,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.utilsFrame,                     ''],  
                
                ['Cloth Manager UI',            self.clothManagerAB,         5,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.clothFunctions_layout,          ''],
                ['Duplicate Special',           self.duplicateSpecial,       5,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.clothFunctions_layout,          ''],
                ['Make Cloth',                  self.makeCloth,              5,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.clothFunctions_doublelayout,    '0,0'],
                ['Rename Cloth',                self.renameCloth,            5,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.clothFunctions_doublelayout,    '0,1'],
                ['Make Rigid',                  self.makeRigid,              5,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.clothFunctions_doublelayout,    '1,0'],
                ['Rename Rigid',                self.renameRigid,            5,    pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3'],   self.clothFunctions_doublelayout,    '1,1'],                
        ]

        ## Build Buttons
        self.buttons = {}        
        for buttonName, buttonFunction, _, labColor, bgColor, layout, layout_coord, in self.buttonAndFunctions:
            self.buttons[buttonName] = QtWidgets.QPushButton(buttonName)
            self.buttons[buttonName].clicked.connect(buttonFunction)
            self.buttons[buttonName].setFixedHeight(25)
            self.buttons[buttonName].setStyleSheet(
                    'padding:4px; text-align:Center; font: normal; color:{}; background-color:{};'.format(labColor,bgColor))
            try:
                layout.addWidget(self.buttons[buttonName], int(layout_coord.split(',')[0]), int(layout_coord.split(',')[1]))
            except ValueError:
                layout.addWidget(self.buttons[buttonName])
                
        self.buttons['...'].setFixedWidth(40)
        self.buttons['...'].setFixedHeight(20)

        # ## Grouping Buttons
        self.buttons1 = [button for button, _, groupNumber,labColor, bgColor, layout, layout_coord in self.buttonAndFunctions if groupNumber == 1] 
        self.buttons2 = [button for button, _, groupNumber,labColor, bgColor, layout, layout_coord in self.buttonAndFunctions if groupNumber == 2] 
        self.buttons3 = [button for button, _, groupNumber,labColor, bgColor, layout, layout_coord in self.buttonAndFunctions if groupNumber == 3] 
        self.buttons4 = [button for button, _, groupNumber,labColor, bgColor, layout, layout_coord in self.buttonAndFunctions if groupNumber == 4] 
        self.buttons5 = [button for button, _, groupNumber,labColor, bgColor, layout, layout_coord in self.buttonAndFunctions if groupNumber == 5] 


    def populate(self):
        ''' Populate the TreeQ Widget '''
        self.playRoots = [QTreeWidgetItem(self.playTree, [str(item)]) for item in self.roots ]
        [root.setExpanded(True) for root in self.playRoots]                                                                            
        [root.setForeground(0,QBrush(QColor('#00cdff')))   for root in self.playRoots]  
        
        playbDic = {}        
        for video in self.roots:          
            playbDic.update({video:[x for x in self.playblastFiles if video in x]})                
        ### populate children under the right Root
        for index in range(len(self.roots)):    
            for value in playbDic[self.roots[index]]:
                child = QTreeWidgetItem(self.playRoots[index], [value])
                child.setForeground(0,QBrush(QColor('#84939B')))


    def buildMainLayout(self):
    #------------------------------
    #--------- BUILD MAIN LAYOUT         
          
        self.playblastFrame.addLayout(self.playblastMan_layout)
             
        self.main_layout.addLayout(self.text_top_layout)      
        self.main_layout.addLayout(self.button_top_layout)   
        self.main_layout.addWidget(self.playblastFrame)   
        self.main_layout.addWidget(self.cameraFrame) 
        self.main_layout.addLayout(self.listBoxLayout)
        self.main_layout.addWidget(self.blendshapeFrame) 
        self.main_layout.addWidget(self.utilsFrame) 
        self.main_layout.addWidget(self.clothsFrame) 
               
        self.main_layout.addStretch()        


    def messageAllDelete(self):
        msgBox = QMessageBox()
        msgBox.setText("You are about to delete somes files.")
        msgBox.setInformativeText("Do you want to delete All?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec_()
        
        if ret == QMessageBox.Yes:
            self.deleteAllPlayblast()

        if ret == QMessageBox.Cancel:
            print 'delete canceled!'

                        
    def messageSelDelete(self):
        msgBox = QMessageBox()
        msgBox.setText("You are about to delete somes files.")
        msgBox.setInformativeText("Do you want to delete them?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec_()
        
        if ret == QMessageBox.Yes:
            self.deleteSelectedPlayblast()

        if ret == QMessageBox.Cancel:
            print 'delete canceled!'


    def updateData(self):
        ''' Update Playblast QList ''' 
                  
        self.playTree.clear()

        update_data = self.getOsDatas()      
        update_root = self.getRootsData()
        update_playRoots = [QTreeWidgetItem(self.playTree, [str(item)]) for item in update_root ]  
        [root.setForeground(0,QBrush(QColor('#00cdff')))   for root in update_playRoots]        

        playbDic = {}        
        for video in update_root:          
            playbDic.update({video:[x for x in self.playblastFiles if video in x]})                
        ### populate children under the right Root
        for index in range(len(update_root)):    
            for value in playbDic[update_root[index]]:
                child = QTreeWidgetItem(update_playRoots[index], [value]) 
                child.setForeground(0,QBrush(QColor('#84939B')))        
        self.expandAll() 


#=====================================
#  SLOTS
#=====================================

    #------------------------------
    #--------- TIMESLIDER FUNCTIONS 

    def getCurrentTimeSlider(self):
        endFrame = pm.playbackOptions(q=True, maxTime=True)         
        return int(endFrame)


    def cachesTimeSlider(self):
        endFrameTimeS = mc.playbackOptions(q=True, maxTime=True) 
        endFrame = int(self.originalEndFrame_LineEdit.text())
        
        if endFrame == endFrameTimeS :
            mc.playbackOptions(e=True, animationStartTime=970, minTime=970,  animationEndTime= endFrame + 1, maxTime = endFrame + 1)
            self.buttons['Set Timeslider for Caches'].setStyleSheet(
                    'padding:4px; text-align:Center; font: normal; color:{}; background-color:{};'.format(pysideColorDic['colorLightGrey'],   pysideColorDic['colorGreen3']))        
        else:
            mc.playbackOptions(e=True, minTime=1001, animationEndTime= endFrame, maxTime = endFrame)
            self.buttons['Set Timeslider for Caches'].setStyleSheet(
                    'padding:4px; text-align:Center; font: normal; color:{}; background-color:{};'.format(pysideColorDic['colorLightGrey'],   pysideColorDic['colorDarkGrey3']))

                        
    def OriginalEndFrameCC(self):
        val = int(self.originalEndFrame_LineEdit.text())
        mc.playbackOptions(e=True, minTime=1001, maxTime = val) 
        self.Original_endTime = None

                                                                                
    def OriginalStartFrameCC(self):
        val = int(self.originalStartFrame_LineEdit.text())
        mc.playbackOptions(e=True, minTime=1001, maxTime = val) 
        self.Original_endTime = None


    def reset(self):
        startFrame = mc.playbackOptions(q=True, minTime=True) 
        endFrame = mc.playbackOptions(q=True, maxTime=True) 
        mc.playbackOptions(e=True, minTime=startFrame, maxTime = endFrame)
        self.originalEndFrame_LineEdit.setText(str(int(endFrame)))
        sys.stdout.write('// Result : The values are reset //')


    #------------------------------
    #--------- PLAYBLAST FUNCTIONS 


    def cleanViewer(self):
        activeView = pm.getPanel(wf=True)
        pm.modelEditor(activeView, e=True, alo=False)
        pm.modelEditor(activeView, e=True, polymeshes=True)


    def selectPath(self):
        '''select folder to set path '''
        path = QtWidgets.QFileDialog.getExistingDirectory() or []
        if path == []:
            path = self.path_LineEdit.text()
        self.path_LineEdit.setText(path+'/')
        self.updateData() 

            
    def playbast_org(self):       
        currentSceneName = pm.sceneName().split('/')[-1]
        videoName = currentSceneName.split('.')[0]
        version = '000'
   
        pm.playblast(fp=4, offScreen=1, clearCache=0, format='qt', sequenceTime=0, showOrnaments=1, percent=100, filename='{}/{}.{}'.format(self.playbast_path,videoName,version), 
                     viewer=1, forceOverwrite=1, quality=100, useTraxSounds=1, compression="png")                              

        self.updateData()
        sys.stdout.write('Playblast is done! {}/{}.{} \n'.format(self.playbast_path,videoName,version))


    def playbast_re(self):      
        currentSceneName = pm.sceneName().split('/')[-1]
        videoName = currentSceneName.split('.')[0]                       
        latest_ver = []
        for file_name in os.listdir(self.playbast_path):
            file = file_name.split('.')[0]
            ver = file_name.split('.')[-2]
                       
            if file == videoName:
                latest_ver.append(ver)

        version = '{:03d}'.format(int(sorted(latest_ver)[-1]))

        pm.playblast(fp=4, offScreen=1, clearCache=0, format='qt', sequenceTime=0, showOrnaments=1, percent=100, filename='{}/{}.{}'.format(self.playbast_path,videoName,version), 
                     viewer=1, forceOverwrite=1, quality=100, useTraxSounds=1, compression="png")
        
        self.updateData()                
        sys.stdout.write('Playblast is done! {}/{}.{} \n'.format(self.playbast_path,videoName,version))


    def playbast_ver(self):                   
        currentSceneName = pm.sceneName().split('/')[-1]
        videoName = currentSceneName.split('.')[0]                       
        latest_ver = []
        for file_name in os.listdir(self.playbast_path):
            file = file_name.split('.')[0]
            ver = file_name.split('.')[-2]
                       
            if file == videoName:
                latest_ver.append(ver)

        version = '{:03d}'.format(int(sorted(latest_ver)[-1]) + 1)                        
        pm.playblast(fp=4, offScreen=1, clearCache=0, format='qt', sequenceTime=0, showOrnaments=1, percent=100, filename='{}/{}.{}'.format(self.playbast_path,videoName,version), 
                     viewer=1, forceOverwrite=1, quality=100, useTraxSounds=1, compression="png")        
        self.updateData() 

        
    def playblast_clic(self):
        sel_playb = self.playTree.currentItem()           
        sel_playb_text = self.playTree.currentItem().text(0)  
        video_path = '{}/{}'.format(self.playbast_path, sel_playb_text)
        
        if os.path.exists(video_path):
            subprocess.Popen(["rv", video_path])        
            sys.stdout.write('Playblast Opening... : {} \n'.format(video_path))   
        else:
            pass


    def expandAll(self):
        all_tops_item = []
        for index in range(self.playTree.topLevelItemCount()):
            topItems = self.playTree.topLevelItem(index)
            all_tops_item.append(topItems)
       
        expand_state = all_tops_item[0].isExpanded()
        if expand_state == True:
            current_sel = self.playTree.collapseAll()   
        else:    
            current_sel = self.playTree.expandAll()    
            
                                    
    def deleteAllPlayblast(self):
        print ('Deleting...')
        for video in self.playblastFiles:
            toDelete =  '{}/{}'.format(self.playbast_path,video)
            print ('    ' + str(toDelete))
            os.remove(toDelete)
            
            self.playTree.clear()
            
            
    def deleteSelectedPlayblast(self):
        sel_playb = self.playTree.selectedItems()   
        sel_playb_text = [playb.text(0) for playb in sel_playb]    
        
        print ('Deleting...')
        for video in sel_playb_text:
            toDelete =  '{}/{}'.format(self.playbast_path,video)
            print ('    ' + str(toDelete))
            os.remove(toDelete)   
            

        ## Update Playblast QList   
        ####################################                 
        self.playTree.clear()

        update_data = self.getOsDatas()      
        update_root = self.getRootsData()
        update_playRoots = [QTreeWidgetItem(self.playTree, [str(item)]) for item in update_root ]  
        [root.setForeground(0,QBrush(QColor('#00cdff')))   for root in update_playRoots]        

        playbDic = {}
        
        for video in update_root:          
            playbDic.update({video:[x for x in self.playblastFiles if video in x]})       
         
        ### populate children under the right Root
        for index in range(len(update_root)):    
            for value in playbDic[update_root[index]]:
                child = QTreeWidgetItem(update_playRoots[index], [value]) 
                child.setForeground(0,QBrush(QColor('#84939B')))        
        self.expandAll()                        
                                                        
    #------------------------------
    #--------- CAMEREA FUNCTIONS 
                                
    def AddCams(self):
        _sel_cams = self.presetListLeft.selectedItems()
        self.sel_cams = [cam.text() for cam in _sel_cams]    
        [self.presetListRight.addItem(cam) for cam in self.sel_cams] # ---- add Custom camera   
        return self.sel_cams

    def removeCam(self):
        numb = self.presetListRight.count()
        _oldcameras =  [self.presetListRight.item(index).text() for index in range(numb)]
        _sel_cams = self.presetListRight.selectedItems()
        sel_cams_text = [cam.text() for cam in _sel_cams]
        self.sel_cams = list(set(_oldcameras) - set(sel_cams_text))
        self.presetListRight.clear()
        [self.presetListRight.addItem(cam) for cam in self.sel_cams]


    def refreshCam(self):
        self.presetListLeft.clear()
        _allCam = pm.listCameras(o=False, p = True)
        [self.presetListLeft.addItem(cam) for cam in _allCam]


    def toggleCam(self):
        currentCam=pm.lookThru(q=1)
        allCam=self.sel_cams
        for pos in range(0,len(allCam)):
            if currentCam == allCam[pos]:
                nextCam=int(pos + 1)                 
        if nextCam>=len(allCam):
            nextCam=0            
        pm.lookThru(allCam[nextCam])
        
    
    def doubleClickedCamRight(self):
        _sel_cams = self.presetListRight.currentItem().text()        
        pm.lookThru(_sel_cams)

                
    def doubleClickedCamLeft(self):
        _sel_cams = self.presetListLeft.currentItem().text()
        pm.lookThru(_sel_cams)

        
    #----------------------------------
    #--------- BLENDSHAPES FUNCTIONS 

        
    def ActiveBLS_BA(self):
        self.bls_value = float(self.blendshapeValue_LineEdit.text())
        selection=pm.selected()

        def ActiveBLS(value):        
            all_bls = flatList([adb.findBlendShape(str(x)) for x in selection])
            [pm.PyNode(x).setWeight(0,value) for x in all_bls]                
            sys.stdout.write('blendshapes set to {} \n'.format(self.bls_value))
        ActiveBLS(self.bls_value)
        pm.select(selection,r=True)


    def keyBls(self):
        all_bls = flatList([adb.findBlendShape(str(x)) for x in pm.selected()])
        weight_name = flatList([pm.PyNode(x).getTarget() for x  in all_bls])
        all_weight_name = [weight_name[index] for index in range(0, len(pm.selected()))]    
        for bls, w_name in zip(all_bls, all_weight_name):
            pm.setKeyframe('{}.{}'.format(bls,w_name))   
        sys.stdout.write('Blendshapes Keyed!!! \n')  


    def createBls(self):
        if self.bls_checkbx.checkState() == QtCore.Qt.Unchecked :
            adb.blendshape(pm.selected(),"local")
        else:
            adb.blendshape(pm.selected(),"world")

                        
    def blend2GrpBls(self):
        if self.bls_checkbx.checkState() == QtCore.Qt.Unchecked :
            adb.blend2grps(origin = 'local')
        else:
            adb.blend2grps(origin = 'world')


    def deleteBls(self):
        adb.deleteBLS(subject = pm.selected(), suffix = 'BLS')
        

    #----------------------------------
    #--------- CLOTH FUNCTIONS 

    def duplicateSpecial(self):
        for each in pm.selected():
            dup_mesh = pm.duplicate(each, inputConnections=True, returnRootsOnly=True)[0]
            pm.parent(dup_mesh, w=True)                
            try:
                new_name = dup_mesh.split('__')[1] + '__Duplicate__'
                pm.rename(dup_mesh, new_name)
            except:
                pm.rename(dup_mesh, '{}__Duplicate__'.format(dup_mesh))                

            att_to_lock = ['tx','ty','tz','rx','ry','rx','rz','sx','sy','sz', 'v']
            for att in  att_to_lock:
                pm.PyNode(dup_mesh).setAttr(att, lock=False, keyable=True)
            
            attr = dup_mesh + '.v'
            mel.eval("source channelBoxCommand; CBdeleteConnection \"{}\"".format(attr))
            pm.select(None)


    def makeCloth(self):
        '''cloth SetUp '''
        selection = pm.selected()
        def makeCloth_node(msh):
                pm.select(msh)
                pm.mel.createNCloth(0)
                cloth = pm.rename('nCloth1',msh.split('cloth')[0]+'__ncloth__')
                pm.parent(cloth, pm.PyNode(msh).getParent())
                pm.select(None)
                return cloth
                
        all_cloth = []
        for each in selection:
            cloth = makeCloth_node(each)        
            all_cloth.append(cloth)
            
        for sel, cloth in zip(selection,all_cloth):
            pm.reorder(sel, back=True)
            pm.reorder(cloth, back=True)


    def makeRigid(self):
        '''Rigid SetUp '''
        selection = pm.selected()
        def makeCloth_node(msh):
                pm.select(msh)
                pm.mel.makeCollideNCloth()
                rigid = pm.rename('nRigid1',msh.split('cloth')[0]+'__nRigid__')
                pm.parent(rigid, pm.PyNode(msh).getParent())
                pm.select(None)
                return rigid                
        all_rigid = []
        for each in selection:
            rigid = makeCloth_node(each)        
            all_rigid.append(rigid)
            
        for sel, rigid in zip(selection,all_rigid):
            pm.reorder(sel, back=True)
            pm.reorder(rigid, back=True)


    def renameCloth(self):
        selection = pm.selected()
        out = flatList([pm.PyNode(x).getShapes() for x in selection]) 
        nCloths = flatList([x.outputs(type='nCloth') for x in out])  
        
        for cloth, sel in zip (nCloths, selection):
            pm.rename(cloth, '{}__nCloth__'.format(sel))

                        
    def renameRigid(self):
        selection = pm.selected()
        out = flatList([pm.PyNode(x).getShapes() for x in selection]) 
        nRigids = flatList([x.outputs(type='nRigid') for x in out])  
        
        for rigids, sel in zip (nRigids, selection):
            pm.rename(rigids, '{}__nRigid__'.format(sel))


    def clothManagerAB(self):
        global win
        try:
            win.deleteLater()
        except:
            pass
        
        win = clothManager()
        win.show()
        sys.stdout.write('Cloth Manager UI is open!')


#####################################################################################
#####################################################################################


class clothManager(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(clothManager, self).__init__(parent = maya_main_window())

        
        self.setObjectName('Cloth_Manager')        
        self.version =  1.0
        self.setWindowTitle('Cloth Manager' + '  v' + str(self.version))
        self.setWindowFlags(QtCore.Qt.Tool)
        self.resize(250,250)
            
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(*[5]*4)        
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)
                
        self.create_Button()
        self.getDatas()
        self.qTreeSetup()
        self.populate()


    def create_Button(self):     
        self.bottons_layout = QtWidgets.QHBoxLayout()    
        self.buttonAndFunctions = [
                # name,               function ,                  labelColor,                     backgroundColor,                       layout,               
                ['Expand All',   self.expandAll,   pysideColorDic['colorYellowlabel'],   pysideColorDic['colorDarkGrey3'],   self.bottons_layout,  ],
            
        ]

        ## Build Buttons
        self.buttons = {}        
        for buttonName, buttonFunction,labColor, bgColor, layout, in self.buttonAndFunctions:
            self.buttons[buttonName] = QtWidgets.QPushButton(buttonName)
            self.buttons[buttonName].clicked.connect(buttonFunction)
            self.buttons[buttonName].setFixedHeight(25)
            self.buttons[buttonName].setStyleSheet(
                    'padding:4px; text-align:Center; font: normal; color:{}; background-color:{};'.format(labColor,bgColor))   
            layout.addWidget(self.buttons[buttonName])



    def getDatas(self):
        self.all_necleus = pm.ls(type='nucleus')
        self.all_nRigids = pm.ls(type='nRigid')
        self.all_nCloth = pm.ls(type='nCloth')
                        
             
    def qTreeSetup(self):
        self.treeLayout = QVBoxLayout()

        #------------------------------
        #--------- TREE LIST WIDGET  

        self.clothTree = QTreeWidget()
        self.clothTree.setSelectionMode(self.clothTree.ExtendedSelection)
        self.clothTree.setHeaderLabel('Cloth Tree View')
        self.treeLayout.addWidget(self.clothTree)  
        self.clothTree.itemSelectionChanged.connect(self.selectionAB)   
        self.clothTree.itemClicked.connect(self.checkAB)   
             

        self.nucRoots = [QTreeWidgetItem(self.clothTree, [str(item)]) for item in self.all_necleus ]
        [root.setExpanded(True) for root in self.nucRoots]                                                                            
        [root.setForeground(0,QBrush(QColor('#99f44f')))   for root in self.nucRoots]    
        
        
        for root in self.nucRoots:
            value = pm.PyNode(root.text(0)).enable.get()
            if value == True:
                root.setCheckState(0,QtCore.Qt.Checked)
            elif value == False:
                root.setCheckState(0,QtCore.Qt.Unchecked)

            
        self.treeSetUpChild = [
                # name,                  function ,         labelColor,     Expand                     
                ['nRigid',              self.selectionAB,   '#fd651d',      False, ],       
                ['nCloth',              self.test,          '#ffe100',      True,  ],   
                ['constraints',         self.test,          '#11a11f',      False, ],                    
        ]

        for treeItem, buttonFunction, labColor, expand in self.treeSetUpChild:
            for parent in self.nucRoots:
                for nuk in self.all_necleus:
                    value = nuk.enable.get()                    
                child = QtWidgets.QTreeWidgetItem(parent, [treeItem])
                child.setExpanded(expand)                  
                child.setForeground(0,QBrush(QColor(labColor)))  
                
      
                                                                
                                
    def populate(self):
        def getType(subject):
            '''Print selection Type '''
            all_types = []  
            try:
                _type = (pm.objectType(pm.PyNode(subject).getShape()) )
            except:  
                _type =_type = (pm.objectType(pm.PyNode(subject)))
            all_types.append(_type)                
            return _type
    
        ## nCloth
        #----------------------    

        nucDictCloth = {}                      
        for nuc in self.all_necleus:
            _connectionCloth = list(set(pm.listConnections(nuc , s=True,d=False )))   
            __connectionCloth = [x for x in _connectionCloth if not 'time' in str(x)]
            connectionCloth = [x for x in __connectionCloth if getType(x) == 'nCloth']   
            nucDictCloth[str(nuc)] = connectionCloth
       
        for _index in range(len(self.all_necleus)):
            for cloth in nucDictCloth[str(self.all_necleus[_index])]:
                _root = self.nucRoots[_index]
                child_count = _root.childCount()        
                children = [_root.child(index) for index in range(child_count)] # = nRigid, nCloth, constraint
                child = QTreeWidgetItem(children[1], [str(cloth)])
                child.setForeground(0,QBrush(QColor('#ffe100'))) 
                value = pm.PyNode(cloth).isDynamic.get() ## set checkstate

                if value == True:
                    child.setCheckState(0,QtCore.Qt.Checked)
                elif value == False:
                    child.setCheckState(0,QtCore.Qt.Unchecked)
            

        ## nRigid
        #---------------------- 
                                                                
        nucDictRigid = {}                      
        for nuc in self.all_necleus:
            _connectionRigid = list(set(pm.listConnections(nuc , s=True,d=False )))   
            __connectionRigid = [x for x in _connectionRigid if not 'time' in str(x)]
            connectionRigid = [x for x in __connectionRigid if getType(x) == 'nRigid']    
            nucDictRigid[str(nuc)] = connectionRigid

        for _index in range(len(self.all_necleus)):
            for rigid in nucDictRigid[str(self.all_necleus[_index])]:
                _root = self.nucRoots[_index]
                child_count = _root.childCount()        
                children = [_root.child(index) for index in range(child_count)] # = nRigid, nCloth, constraint
                child = QTreeWidgetItem(children[0], [str(rigid)]) 
                child.setForeground(0,QBrush(QColor('#fd651d')))  
                
                value = pm.PyNode(rigid).isDynamic.get() ## set checkstate
                if value == True:
                    child.setCheckState(0,QtCore.Qt.Checked)
                elif value == False:
                    child.setCheckState(0,QtCore.Qt.Unchecked)
                            
                                
        ## nConstraint
        #---------------------- 
                                                                
        nucDictCons = {}                      
        for nuc in self.all_necleus:
            _connectionCons = list(set(pm.listConnections(nuc , s=True,d=False )))   
            __connectionCons = [x for x in _connectionCons if not 'time' in str(x)]
            connectionCons = [x for x in __connectionCons if getType(x) == 'dynamicConstraint']    
            nucDictCons[str(nuc)] = connectionCons

        for _index in range(len(self.all_necleus)):
            for cons in nucDictCons[str(self.all_necleus[_index])]:
                _root = self.nucRoots[_index]
                child_count = _root.childCount()        
                children = [_root.child(index) for index in range(child_count)] # = nRigid, nCloth, constraint
                child = QTreeWidgetItem(children[2], [str(cons)])     
                child.setForeground(0,QBrush(QColor('#11a11f')))                                            
                                
                value = pm.PyNode(cons).enable.get() ## set checkstate
                if value == True:
                    child.setCheckState(0,QtCore.Qt.Checked)
                elif value == False:
                    child.setCheckState(0,QtCore.Qt.Unchecked)                                
                                
                                
        self.main_layout.addLayout(self.bottons_layout)
        self.main_layout.addLayout(self.treeLayout)
        

#==================================
#  SLOTS
#==================================
        
    
    def test(self):
        print('test')


    def selectionAB(self):        
        try:
            current_sel = self.clothTree.currentItem().text(0)   
            pm.select(current_sel, r =True)
        except:
            pass
        

    def checkAB(self):
        try:
            current_sel = self.clothTree.currentItem()        
            current_sel_name = self.clothTree.currentItem().text(0)        
            state = str(current_sel.checkState(0)).split('.')[-1]        
                
            if state == 'Checked':
                try:
                    pm.PyNode(current_sel_name).enable.set(1)
                except AttributeError: 
                    pm.PyNode(current_sel_name).isDynamic.set(1)
            elif state == 'Unchecked':
                try:
                    pm.PyNode(current_sel_name).enable.set(0)
                except AttributeError: 
                    pm.PyNode(current_sel_name).isDynamic.set(0)                
        except:
            pass      


    def expandAll(self):
        try:
            expand_state = self.nucRoots[0].isExpanded()
        except IndexError:
            pass
        if expand_state == True:
            current_sel = self.clothTree.collapseAll()   
        else:    
            current_sel = self.clothTree.expandAll()    




#==================================
#  UI BUILD
#==================================

def maya_main_window():
    """Return the Maya main window widget as a Python object."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def showUI():
    # Make sure the UI is deleted before recreating
	global cfx_tool_ui
	try:
		cfx_tool_ui.deleteLater()
	except:
		pass
	cfx_tool_ui = cfxToolbox()
	cfx_tool_ui.show()      

        
def dockUI():
	cfx_tool_ui2 = cfxToolbox()
	cfx_tool_ui2.dock_ui()  

        
# dockUI()
# showUI()
