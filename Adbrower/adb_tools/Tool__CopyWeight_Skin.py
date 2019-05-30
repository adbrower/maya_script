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
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import adb_pyQt.Class__frameLayout as adbFrameLayout

import getpass
import os
import ConfigParser
import maya.cmds as mc
import maya.mel as mel
import sys
import CollDict
from CollDict import pysideColorDic as pyQtDic

import adbrower
reload(adbrower)
adb = adbrower.Adbrower()

import adb_utils.Class__Skinning as skin
import adb_utils.deformers.Class__Blendshape as bs
# reload(skin)


VERSION = 3.0
USERNAME = getpass.getuser() 
PATH_WINDOW = 'C:/Users/'+ USERNAME + '/AppData/Roaming'
PATH_LINUX = '/home/'+ USERNAME + '/'
FOLDER_NAME ='.config/adb_Setup'
FILE_NAME = 'Copy_WEIGHTS_Tool_config2.ini'
ICONS_FOLDER = 'C:/Users/Audrey/Google Drive/[SCRIPT]/python/Adbrower/adb_icons/'


#-----------------------------------
#  CLASS
#----------------------------------- 



class SkinCopyWEIGHTS(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    def __init__(self,parent=None):                
        super(SkinCopyWEIGHTS, self).__init__(parent = maya_main_window())           
        self.setObjectName('test')      
        self.starting_height = 760  
        self.starting_width = 390  
        self.setWindowTitle('adbrower - Copy Weights Tool' +  ' v' + str(VERSION))
        self.setWindowFlags(QtCore.Qt.Tool)        
        self.setMinimumWidth(self.starting_width)
        self.resize(self.starting_width,self.starting_height) 
        
        # -----------------------------
        # ---  DATA
                
        self.final_path = self.setPath()  
        self.dataList = []
        self.dataList = self.loadData()
        self.sources = self.dataList[0]
        self.targets = self.dataList[1]
        
        
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
        self.main_layout.setContentsMargins(*[5]*4)        
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)
        
        self.scroll_widget.setLayout(self.main_layout)
        self.widgetsAndLayouts()
        self.create_Button()
        self.buildMainLayout()
        self.status_icon_update()        
        self.keep_same_joints_checked()
        self.type_update()  
        self.target_jnts_hide()      
        pm.select(None)
        
    def closeEvent(self, eventQCloseEvent): 
        self.saveData()
        
    def dockCloseEventTriggered(self):
        self.saveData()
        
    def close(self):
        self.saveData()           

 
    def widgetsAndLayouts(self):   
        
        #--------- Predefine widgets                 

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
    
        self.vLayoutAndFunctions = [
                # name,              margins
                ['data',           [1,1,1,1]      ],                                                      
                ['framelayout',    [1,1,1,1]      ],                                                      
                ['WEIGHTS',        [1,1,1,1]      ],                                                                                                          
                ['spacing',        [1,5,1,1]      ],                            
        ]
        self.vlayout = {}        
        for layoutName, margins, in self.vLayoutAndFunctions:
            self.vlayout[layoutName] = QtWidgets.QVBoxLayout()
            self.vlayout[layoutName].setContentsMargins(margins[0],margins[1],margins[2],margins[3],)
        
        
        self.hLayoutAndFunctions = [
                # name,           
                ['icons',                    ],                            
                ['add_meshes_QList',         ],                            
                ['add_meshes_01',            ],                            
                ['add_meshes_02',            ],                            
                ['search_joint',             ],                            
                ['verify_joint',             ],                            
                ['manually_joint_layout',    ],                            
                ['manually_joint_button',    ],                            
        ]
        self.hlayout = {}        
        for layoutName, in self.hLayoutAndFunctions:
            self.hlayout[layoutName] = QtWidgets.QHBoxLayout()


        self.gridLayoutAndFunctions = [
                # name,                                    
                ['influence_choice',                 ],                            
                ['apply',                 ],                            
                          
        ]
        self.glayout = {}        
        for layoutName, in self.gridLayoutAndFunctions:
            self.glayout[layoutName] = QtWidgets.QGridLayout()


    #------------------------------
    #--------- Widgets

        ## MenuBar
        self.menuBar = QMenuBar(self) # requires parent
        
        self.menu_file = QMenu(self)
        self.menu_file.setTitle("File")
        self.action_change_path = self.menu_file.addAction("Change Path...")
        self.action_print_path = self.menu_file.addAction("Print Path")
        self.action_save = self.menu_file.addAction("Save Data")
       
        
        self.action_save.triggered.connect(self.saveData)
        self.action_print_path.triggered.connect(lambda * args : sys.stdout.write('adb_copyWeightToolsettings file saved at: ' + self.final_path + FOLDER_NAME + '/' + FILE_NAME))
        
        self.menu_refresh = QMenu(self)
        self.menu_refresh.setTitle('Edit')
        self.action_clear_info = self.menu_refresh.addAction('Clear all Info')
        self.action_load = self.menu_refresh.addAction("Reload Data")
        
        self.action_clear_info.triggered.connect(self.clear_all_info)
        self.action_load.triggered.connect(lambda * args :showUI())
        
        self.menuBar.addMenu(self.menu_file) 
        self.menuBar.addMenu(self.menu_refresh) 

        ## Line        
        self.line_widget = {'line_0{}'.format(i): addLine() for  i in range(1,5)}
                
        ## GroupBox        
        self.options_groupbox = QtWidgets.QGroupBox('   Options:   ') 
        self.options_groupbox.setStyleSheet("QGroupBox { padding:10px; border: 1px solid #606060; border-radius: 3px;}")
        
                
        ### Text
        self.copy_skin_text = addText('COPY SKIN', bold=1)
        self.joint_text = addText('Joints - Search and Replace:')
        self.manually_text = addText('Or add it manually:')
        self.search_text = addText('Search for:')
        self.replace_text = addText('Replace for:')
        self.target_jnts_text = addText('Targets Joints:')
        self.space_01_text = addText('<<')
        self.mirror_text = addText('MIRROR',bold=1)
        self.mirror_across_text = addText('Mirror across', alignement = QtCore.Qt.AlignLeft, height=20)
        
        self.surface_Assoc_text = addText('Surface Association', alignement = QtCore.Qt.AlignLeft, height=20)
        self.inf_Assoc_1_text = addText('Influence Association 1', alignement = QtCore.Qt.AlignLeft, height=20)
        self.inf_Assoc_2_text = addText('Influence Association 2', alignement = QtCore.Qt.AlignLeft, height=20)
        self.inf_Assoc_3_text = addText('Influence Association 3', alignement = QtCore.Qt.AlignLeft, height=20)
        
        ## ----- set text Color for all text
        for text in [self.copy_skin_text,
                     self.joint_text,
                     self.manually_text,
                     self.mirror_text,
                        ]:            
            text.setStyleSheet("color:{}".format(pyQtDic['colorYellowlabel']))

        ### QListWidget            
        self.mesh_left_QList = QtWidgets.QListWidget()
        self.mesh_left_QList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection) 
        if self.sources:
            pm.select(self.sources)
            _sources = pm.selected()
            self.sources = [item for item in _sources]    
            [self.mesh_left_QList.addItem(str(item)) for item in self.sources] 
            _type = adb.Type(self.sources)[0]
            if _type == 'mesh':
                for i in xrange(len(self.sources)):
                    self.mesh_left_QList.item(i).setIcon(QtGui.QIcon(':/out_mesh.png')) 
            elif _type == 'joint':
                for i in xrange(len(self.sources)):
                    self.mesh_left_QList.item(i).setIcon(QtGui.QIcon(':/kinJoint.png')) 
            else:
                pass
    
        self.mesh_left_QList.setMinimumHeight(100)  
        self.mesh_left_QList.setMaximumHeight(100)  
        
        self.mesh_right_QList = QtWidgets.QListWidget()
        self.mesh_right_QList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)   
        if self.targets:
            pm.select(self.targets)
            self.refresh_targets()
            _targets = pm.selected()
            self.targets = [item for item in _targets]    
            [self.mesh_right_QList.addItem(str(item)) for item in self.targets] 
            _type = adb.Type(self.targets)[0]
            if _type == 'mesh':
                for i in xrange(len(self.targets)):
                    self.mesh_right_QList.item(i).setIcon(QtGui.QIcon(':/out_mesh.png')) 
            elif _type == 'joint':
                for i in xrange(len(self.targets)):
                    self.mesh_right_QList.item(i).setIcon(QtGui.QIcon(':/kinJoint.png')) 
            else:
                pass   

        self.mesh_right_QList.setMinimumHeight(100)  
        self.mesh_right_QList.setMaximumHeight(100)  


        ### QLineEdit  
        self.search_QLine = QtWidgets.QLineEdit(self.search_setdata )
        self.search_QLine.setMinimumSize(QtCore.QSize(80, 20))
        self.replace_QLine = QtWidgets.QLineEdit(self.replace_setdata )
        self.replace_QLine.setMinimumSize(QtCore.QSize(80, 20))
        
        self.hlayout['search_joint'].addWidget(self.search_text)
        self.hlayout['search_joint'].addWidget(self.search_QLine)

        self.target_jnts_QLine = QtWidgets.QLineEdit(self.target_jnts_setdata)
        self.target_jnts_QLine.setMinimumSize(QtCore.QSize(150, 20))        
        self.target_jnts_QLine.setPlaceholderText('Select Target Mesh') 
        self.target_jnts_QLine.textChanged.connect(self.target_jnts_hide)
        
        self.mirror_options_QLine = QtWidgets.QLineEdit('YZ')    
        
        ## CheckBoxes
        self.same_jnts_Chbx = QtWidgets.QCheckBox('Keep Same Joints - Copy Weights')
        if self.same_jnts_setdata == 'True':
            self.same_jnts_Chbx.setChecked(True)
        else:
            self.same_jnts_Chbx.setChecked(False) 
        self.same_jnts_Chbx.setStyleSheet("color:{}; padding-top: 10px ; padding-bottom: 5px;".format(pyQtDic['colorYellowlabel']))
        self.same_jnts_Chbx.stateChanged.connect(self.keep_same_joints_checked)        


        ## Qcombo Box
        self.mirror_options = ["XY","YZ ","XZ"] 
        self.SurfaceAss_options = ["closest Point","rayCast","closest Component", "uv Space" ]
        self.InfluenceAss_options1 = ["closest Joint","closest Bone","one To One", "label","name" ]
        self.InfluenceAss_options23 = ["None","closest Joint","closest Bone","one To One", "label","name" ] 
            
        self.comboLayoutAndFunctons = [
            #name   ,                         index,           item
            ['mirror_across',                 1,        self.mirror_options],
            ['surface_Association',           0,        self.SurfaceAss_options],
            ['influence_Association_1',       2,        self.InfluenceAss_options1],
            ['influence_Association_2',       3,        self.InfluenceAss_options23],
            ['influence_Association_3',       0,        self.InfluenceAss_options23],
            
        ]
        
        self.comboBox={}
        for widgetName, index, items in self.comboLayoutAndFunctons  :        
            self.comboBox[widgetName] = QtWidgets.QComboBox()
            self.comboBox[widgetName].addItems(items)
            self.comboBox[widgetName].setCurrentIndex(index)
      
        
    #------------------------------
    #--------- FRAMELAYOUT
    
        self.frameLayoutAndFunctions = [
                # name,           collapse
                ['WEIGHTS',        True     ],                                                 
                ['BLENDSHAPES',    False    ],                                                      
                ['JOINTS',         False    ],                                                      
                           
        ]
        self.framelayout = {}        
        for layoutName, collapse, in self.frameLayoutAndFunctions:
            self.framelayout[layoutName] =adbFrameLayout.frameLayout()
            self.framelayout[layoutName].title = layoutName
            self.framelayout[layoutName].isCollapsed = not collapse
            self.framelayout[layoutName].contentFrame.setVisible(collapse)


    def create_Button(self):       
        ''' Create the buttons  '''  
        self.buttonAndFunctions = [
                # name,                  function ,     group number,                   labelColor,            backgroundColor,                      layout,              layout_coordinate     width
                ['expand',               self.qList_expand_plus,       0,        pyQtDic['colorLightGrey'],         '',                    self.hlayout['icons'],                    '',         20],
                ['minus',                self.qList_expand_moins,      0,        pyQtDic['colorLightGrey'],         '',                    self.hlayout['icons'],                    '',         20],
                ['reverse',              self.swap_data,               0,        pyQtDic['colorLightGrey'],         '',                    self.hlayout['icons'],                    '',         20],
                
                ['Load Sources',         self.add_sources,             1,        pyQtDic['colorLightGrey'],   pyQtDic['colorDarkGrey3'],   self.hlayout['add_meshes_01'],            '',         ''],
                ['Load Targets',         self.add_targets,             1,        pyQtDic['colorLightGrey'],   pyQtDic['colorDarkGrey3'],   self.hlayout['add_meshes_01'],            '',         ''],    
                ['Refresh',              self.refresh_sources,         1,        pyQtDic['colorLightGrey'],   pyQtDic['colorDarkGrey2'],   self.hlayout['add_meshes_02'],            '',         ''],      
                [' Refresh',             self.refresh_targets,         1,        pyQtDic['colorLightGrey'],   pyQtDic['colorDarkGrey2'],   self.hlayout['add_meshes_02'],            '',         ''],    
                               
                ['>>>',                  self.swap_search_replace,     0,        pyQtDic['colorLightGrey'],   pyQtDic['colorOrange'],      self.hlayout['search_joint'],             '',         60],                   
                ['Add',                  self.addJointManuallyAB,      2,        pyQtDic['colorDarkGrey3'],   pyQtDic['colorOrange'],      self.hlayout['manually_joint_button'],    '',         60],  
                ['Verify',               self.verifyReplaceJnts,       2,        pyQtDic['colorDarkGrey3'],   pyQtDic['colorOrange'],      self.hlayout['manually_joint_button'],    '',         60], 
                
                ['copy',                 self.copySkinAB,              4,      pyQtDic['colorYellowlabel'],   pyQtDic['colorDarkGrey3'],   self.glayout['apply'],                    '0,0,0,0',         ''],        
                ['Joint_transfer',       self.transferJointSkinAB,     4,      pyQtDic['colorYellowlabel'],   pyQtDic['colorDarkGrey3'],   self.glayout['apply'],                    '1,0,0,0',         ''],                 
                ['Mirror Skin',          self.mirrorSkinAB,            4,      pyQtDic['colorYellowlabel'],   pyQtDic['colorDarkGrey3'],   self.glayout['apply'],                    '2,0,0,0',         ''],                                   
                
                ['Label Joints',         self.labelJointsAB,           3,      pyQtDic['colorLightGrey'],     pyQtDic['colorDarkGrey3'],   self.framelayout['JOINTS'],               '',         ''],  
                ['Select skn Joints',    self.selectSknJntsAB,         3,      pyQtDic['colorLightGrey'],     pyQtDic['colorDarkGrey3'],   self.framelayout['JOINTS'],               '',         ''],  
                
                ['Verify Joint Sides',   self.verifyJointSideAB,       3,      pyQtDic['colorLightGrey'],     pyQtDic['colorDarkGrey3'],   self.framelayout['JOINTS'],               '',         ''],  

                ['Mirror BLS',           self.mirrorBSAB,              3,      pyQtDic['colorLightGrey'],     pyQtDic['colorDarkGrey3'],   self.framelayout['BLENDSHAPES'],          '',         ''],  

        ]

        ## Build Buttons
        self.buttons = {}        
        for buttonName, buttonFunction, _, labColor, bgColor, layout, layout_coord, width, in self.buttonAndFunctions:
            self.buttons[buttonName] = QtWidgets.QPushButton(buttonName)
            self.buttons[buttonName].clicked.connect(buttonFunction) 
            self.buttons[buttonName].setFixedHeight(25)
            if width == '':
                pass
            else:
                self.buttons[buttonName].setFixedWidth(width)
            
            self.buttons[buttonName].setStyleSheet(
                    'padding:4px; text-align:Center; font: normal; color:{}; border: none ; background-color:{};'.format(labColor,bgColor))
            try:
                layout.addWidget(self.buttons[buttonName], int(layout_coord.split(',')[0]), int(layout_coord.split(',')[1]))
            except ValueError:
                layout.addWidget(self.buttons[buttonName])

        self.buttons0 = [button for button, _, groupNumber, labColor, bgColor, layout, layout_coord, width, in self.buttonAndFunctions if groupNumber == 0]         
        self.buttons4 = [button for button, _, groupNumber, labColor, bgColor, layout, layout_coord, width, in self.buttonAndFunctions if groupNumber == 4]         
        
        self.buttons['expand'].setIcon(QtGui.QIcon(ICONS_FOLDER+'Plus.png'))
        self.buttons['minus'].setIcon(QtGui.QIcon(ICONS_FOLDER+'Moins.png'))
        self.buttons['reverse'].setIcon(QtGui.QIcon(ICONS_FOLDER+'swap.png'))
        self.buttons['>>>'].setIcon(QtGui.QIcon(ICONS_FOLDER+'swap.png'))
        
        
        for buttonName in self.buttons0:            
            self.buttons[buttonName].setText(None)
            
        text_list = [ 
                    'Copy Skin',
                    'Transfer Skin to another Joint chain',
                    'Mirror Skin',
        ]
        for buttonName, txt in zip(self.buttons4 , text_list):            
            self.buttons[buttonName].setText(txt)
        
    def buildMainLayout(self):
    #------------------------------
    #--------- BUILD MAIN LAYOUT     
            
        self.main_layout.addWidget(self.menuBar)   
        self.main_layout.addLayout(self.vlayout['data'])      
        self.main_layout.addLayout(self.vlayout['framelayout'])      
                       
        self.vlayout['data'].addLayout(self.hlayout['icons'])        
        self.vlayout['data'].addLayout(self.hlayout['add_meshes_01'])
        self.vlayout['data'].addLayout(self.hlayout['add_meshes_QList'])
        self.vlayout['data'].addLayout(self.hlayout['add_meshes_02'])
        
        self.vlayout['framelayout'].addWidget(self.framelayout['WEIGHTS'])        

        self.hlayout['add_meshes_QList'].addWidget(self.mesh_left_QList)
        self.hlayout['add_meshes_QList'].addWidget(self.mesh_right_QList)

        self.framelayout['WEIGHTS'].addWidget(self.same_jnts_Chbx)  
        self.framelayout['WEIGHTS'].addWidget(self.line_widget['line_01'])                       
        self.framelayout['WEIGHTS'].addWidget(self.mirror_text)                       
        self.framelayout['WEIGHTS'].addWidget(self.copy_skin_text)    
        self.framelayout['WEIGHTS'].addWidget(self.line_widget['line_02'])    
        self.framelayout['WEIGHTS'].addWidget(self.joint_text)
        self.framelayout['WEIGHTS'].addLayout(self.hlayout['search_joint'])
        
        self.hlayout['search_joint'].addWidget(self.replace_text)
        self.hlayout['search_joint'].addWidget(self.replace_QLine)         
        
        self.framelayout['WEIGHTS'].addWidget(self.manually_text)        
        self.framelayout['WEIGHTS'].addLayout(self.hlayout['manually_joint_layout'])
        
        self.hlayout['manually_joint_layout'].addWidget(self.target_jnts_text)   
        self.hlayout['manually_joint_layout'].addWidget(self.target_jnts_QLine)   
        self.hlayout['manually_joint_layout'].addWidget(self.space_01_text) 
        self.hlayout['manually_joint_layout'].addLayout(self.hlayout['manually_joint_button'])    
        self.framelayout['WEIGHTS'].addLayout(self.vlayout['spacing'])  
                      
        self.glayout['influence_choice'].addWidget(self.mirror_across_text , 0,0,)
        self.glayout['influence_choice'].addWidget(self.comboBox['mirror_across'] , 0,1)
        self.glayout['influence_choice'].addWidget(self.line_widget['line_03'], 1,0,1,0)
        self.glayout['influence_choice'].addWidget(self.surface_Assoc_text , 2,0)
        self.glayout['influence_choice'].addWidget(self.comboBox['surface_Association'] , 2,1)
        self.glayout['influence_choice'].addWidget(self.inf_Assoc_1_text , 3,0)
        self.glayout['influence_choice'].addWidget(self.comboBox['influence_Association_1'] , 3,1)
        self.glayout['influence_choice'].addWidget(self.inf_Assoc_2_text , 4,0)
        self.glayout['influence_choice'].addWidget(self.comboBox['influence_Association_2'] , 4,1)
        self.glayout['influence_choice'].addWidget(self.inf_Assoc_3_text , 5,0)
        self.glayout['influence_choice'].addWidget(self.comboBox['influence_Association_3'] , 5,1)
        
        self.options_groupbox.setLayout(self.glayout['influence_choice'])
        self.framelayout['WEIGHTS'].addWidget(self.options_groupbox)  
        self.framelayout['WEIGHTS'].addWidget(self.line_widget['line_04'])   
        self.framelayout['WEIGHTS'].addLayout(self.glayout['apply'])
              
        self.vlayout['framelayout'].addWidget(self.framelayout['JOINTS'])  
        self.vlayout['framelayout'].addWidget(self.framelayout['BLENDSHAPES'])               

        self.hlayout['icons'].addStretch()
        self.vlayout['framelayout'].addStretch()
        


        
#==================================
#  SLOTS
#==================================

    #-------------------------------------
    # DATA MANAGEMENT
    
    def writeText(self):
            file_ini = open(FILE_NAME, 'w+')
            file_ini.write('[General] \n')     
            file_ini.write("sources_number=  \n" ) 
            file_ini.write("source_mesh_data=  \n" )
            file_ini.write("targets_number=  \n")
            file_ini.write("target_mesh_data=  \n")
            file_ini.write("search_data= l__  \n" )
            file_ini.write("replace_data= r__ \n" )
            file_ini.write("target_jnts_data=  \n")
            file_ini.write("same_jnts_data=0 \n")
            file_ini.write("surf_ass_data=0 \n")
            file_ini.write("inf_ass1_data=2 \n")
            file_ini.write("inf_ass2_data=3 \n")
            file_ini.write("inf_ass3_data=5 \n")            
            file_ini.close()

    def setPath(self):    
        def finalPath():
            if not os.path.exists(PATH_LINUX):
                pass
            else:
                return PATH_LINUX   
           
            if not os.path.exists(PATH_WINDOW): 
                pass              
            else:
                return PATH_WINDOW      

        self.final_path = finalPath() 

        os.chdir(self.final_path)        
        try:
            os.makedirs(FOLDER_NAME)        
        except :
            pass          
            
        if os.path.exists(self.final_path + '/' + FOLDER_NAME + '/' + FILE_NAME): 
            # print ('file exist')
            pass
        else:
            os.chdir(self.final_path + '/' +  FOLDER_NAME)
            # print(os.getcwd())
               
            self.writeText()
        
        return(self.final_path)

    def saveData(self):
        os.chdir(self.final_path)        
        try:
            os.mkdir(folder_name)        
        except :
            pass
                
        os.chdir(self.final_path +'/'+ FOLDER_NAME)
        # print(os.getcwd())
           
        file_ini = open(FILE_NAME, 'w+')
        file_ini.write('[General] \n') 
        
        if self.mesh_left_QList.count() == 0:
            file_ini.write("sources_number=  \n" ) 
            file_ini.write("sources_data=  "+  '\n')
        else:
            file_ini.write("sources_number=" + str(len(self.sources)) + '\n')
            for i in xrange(len(self.sources)):    
                file_ini.write("sources_data_{}=".format(i) + self.mesh_left_QList.item(i).text() + '\n')

        if self.mesh_right_QList.count() == 0:
            file_ini.write("targets_number=  \n" ) 
            file_ini.write("targets_data=  "+  '\n')
        else:
            file_ini.write("targets_number=" + str(len(self.targets))+'\n')
            for i in xrange(len(self.targets)):    
                file_ini.write("targets_data_{}=".format(i) + self.mesh_right_QList.item(i).text() + '\n')

        file_ini.write("search_data=" + self.search_QLine.text()+  '\n')
        file_ini.write("replace_data=" + self.replace_QLine.text()+ ' \n')
        file_ini.write("target_jnts_data=" + self.target_jnts_QLine.text()+  '\n')
        file_ini.write("same_jnts_data=  "+ str(self.same_jnts_Chbx.isChecked()) +  '\n')
        
        file_ini.write("surf_ass_data=  "+ str(self.comboBox['surface_Association'].currentIndex()) +  '\n')
        file_ini.write("inf_ass1_data=  "+ str(self.comboBox['influence_Association_1'].currentIndex()) +  '\n')
        file_ini.write("inf_ass2_data=  "+ str(self.comboBox['influence_Association_2'].currentIndex()) +  '\n')
        file_ini.write("inf_ass3_data=  "+ str(self.comboBox['influence_Association_3'].currentIndex()) +  '\n')
      
        file_ini.close()
        return(file_ini)


    def loadData(self):  
        dataList = []
        config = ConfigParser.ConfigParser()
        config.read(self.final_path + '/' + FOLDER_NAME + '/' + FILE_NAME)
    
        source_number_data = config.get("General", "sources_number")        
        self.sources_setdata = []
        if source_number_data == '':
            self.sources_setdata = []
        else:
            for i in xrange(int(source_number_data)):
                _sources_setdata = config.get("General", "sources_data_{}".format(i))
                if pm.objExists(_sources_setdata):
                    self.sources_setdata.append(_sources_setdata)
                else:
                   pass
        

        target_number_data = config.get("General", "targets_number")
        self.targets_setdata = []
        if target_number_data == '':
            self.targets_setdata = []
        else:
            for i in xrange(int(target_number_data)):
                _targets_setdata = config.get("General", "targets_data_{}".format(i))
                if pm.objExists(_targets_setdata):
                    self.targets_setdata.append(_targets_setdata) 
                else:
                    pass

                       
        self.search_setdata = config.get("General", "search_data")
        self.replace_setdata = config.get("General", "replace_data")
        
        self.target_jnts_setdata = config.get("General", "target_jnts_data")
        self.same_jnts_setdata = config.get("General", "same_jnts_data")
        
        self.SurfaceAss_setdata = config.get("General", "surf_ass_data")          
        self.InfluenceAss1_setdata = config.get("General", "inf_ass1_data")
        self.InfluenceAss2_setdata = config.get("General", "inf_ass2_data")
        self.InfluenceAss3_setdata = config.get("General", "inf_ass3_data")
            
        dataList.append(self.sources_setdata)
        dataList.append(self.targets_setdata)
        dataList.append(self.search_setdata)
        dataList.append(self.replace_setdata)
        dataList.append(self.target_jnts_setdata)
        dataList.append(self.same_jnts_setdata)            
        dataList.append(self.SurfaceAss_setdata)            
        dataList.append(self.InfluenceAss1_setdata)
        dataList.append(self.InfluenceAss2_setdata)
        dataList.append(self.InfluenceAss3_setdata)
        
        return(dataList)

    def clear_all_info(self):
        file_ini = self.saveData()
        self.search_QLine.setText('L_')
        self.replace_QLine.setText('R_')

        self.same_jnts_Chbx.setChecked(False)                  
        self.comboBox['surface_Association'].setCurrentIndex(0)
        self.comboBox['influence_Association_1'] .setCurrentIndex(2)
        self.comboBox['influence_Association_2'] .setCurrentIndex(3)
        self.comboBox['influence_Association_3'] .setCurrentIndex(0)
        
        self.mesh_left_QList.clear()
        self.mesh_right_QList.clear()
        
        [self.comboBox[x].setVisible(True) for x in self.comboBox.keys()]
        [self.line_widget[x].setVisible(True) for x in self.line_widget.keys()]
        self.options_groupbox.setVisible(True)
        self.copy_skin_text.setVisible(True)
        self.same_jnts_Chbx.setVisible(True)
        self.mirror_across_text.setVisible(True) 
        self.keep_same_joints_checked()

    #-------------------------------------
    # UI MANAGEMENT


    def qList_expand_plus(self):
        self.mesh_right_QList.setMaximumHeight(self.mesh_right_QList.height() + 50) 
        self.mesh_left_QList.setMaximumHeight(self.mesh_left_QList.height() + 50) 
        self.mesh_right_QList.setMinimumHeight(self.mesh_left_QList.height() + 50) 
        self.mesh_left_QList.setMinimumHeight(self.mesh_left_QList.height() + 50) 
        self.resize(self.width(), self.height()+50) 
        
    def qList_expand_moins(self):
        if self.mesh_right_QList.height() > 100:
            self.mesh_right_QList.setMaximumHeight(self.mesh_right_QList.height() - 50) 
            self.mesh_left_QList.setMaximumHeight(self.mesh_left_QList.height() - 50) 
            self.mesh_right_QList.setMinimumHeight(self.mesh_left_QList.height() - 50) 
            self.mesh_left_QList.setMinimumHeight(self.mesh_left_QList.height()-50)
            self.resize(self.width(), self.height()-50)             
        else:
            pass

    def status_icon_update(self):
        if self.sources == []:
            pass
        else:
            _type = adb.Type(self.sources)[0]
            if _type == 'mesh':    
                self.buttons['copy'].setIcon(QtGui.QIcon(ICONS_FOLDER+'green_status.png'))
                self.buttons['Joint_transfer'].setIcon(QtGui.QIcon(ICONS_FOLDER+'red_status.png'))
                if self.same_jnts_Chbx.checkState() == QtCore.Qt.Checked:
                    self.buttons['Mirror Skin'].setIcon(QtGui.QIcon(ICONS_FOLDER+'red_status.png'))
                else: 
                    self.buttons['copy'].setIcon(QtGui.QIcon(ICONS_FOLDER+'red_status.png'))
                    self.buttons['Mirror Skin'].setIcon(QtGui.QIcon(ICONS_FOLDER+'green_status.png'))
                
            elif _type == 'joint':
                self.buttons['copy'].setIcon(QtGui.QIcon(ICONS_FOLDER+'red_status.png'))
                self.buttons['Joint_transfer'].setIcon(QtGui.QIcon(ICONS_FOLDER+'green_status.png'))
                self.buttons['Mirror Skin'].setIcon(QtGui.QIcon(ICONS_FOLDER+'red_status.png'))

    def type_update(self):
        if self.sources:
            pm.select(self.sources)
            _sources = pm.selected()
            self.sources = [item for item in _sources]    
            _type = adb.Type(self.sources)[0]
            print _type
            if _type == 'mesh':
                [self.comboBox[x].setVisible(True) for x in self.comboBox.keys()]
                [self.line_widget[x].setVisible(True) for x in self.line_widget.keys()]
                self.options_groupbox.setVisible(True)
                self.same_jnts_Chbx.setVisible(True)   


            elif _type == 'joint':
                [self.comboBox[x].setVisible(False) for x in self.comboBox.keys()]
                [self.line_widget[x].setVisible(False) for x in self.line_widget.keys()]
                self.options_groupbox.setVisible(False)
                self.copy_skin_text.setVisible(False)
                self.same_jnts_Chbx.setVisible(False)
                self.joint_text.setVisible(False)
                self.manually_text.setVisible(False)
                self.search_text.setVisible(False)
                self.replace_text.setVisible(False)
                self.target_jnts_text.setVisible(False)
                self.space_01_text.setVisible(False)
                self.mirror_text.setVisible(False)
                self.mirror_across_text.setVisible(False)
                self.search_QLine.setVisible(False)
                self.replace_QLine.setVisible(False)
                self.target_jnts_QLine.setVisible(False)
                self.buttons['>>>'].setVisible(False)
                self.buttons['Add'].setVisible(False)
                self.buttons['Verify'].setVisible(False)
            else:
                pass
        
                
    def keep_same_joints_checked(self):       
        hide_list = [
            self.buttons['>>>'],
            self.buttons['Add'],
            self.target_jnts_text,
            self.target_jnts_QLine,
            self.joint_text,
            self.manually_text,
            self.replace_QLine,          
            self.search_QLine,     
            self.search_text,
            self.replace_text,
            self.space_01_text,             
            self.mirror_text,             
            self.mirror_across_text,                                     
            self.comboBox['mirror_across'],                                                             
            self.buttons['Verify'],  
            self.line_widget['line_03']                                                                                                                    
        ]
        
        show_list =[
            self.copy_skin_text,  
            self.comboBox['surface_Association'],             
            self.comboBox['influence_Association_3'],                      
        ]
        
        if self.same_jnts_Chbx.checkState() == QtCore.Qt.Checked:
            for each in hide_list:
                each.setVisible(False)
            for each in show_list:
                each.setVisible(True)
                   
        elif self.same_jnts_Chbx.checkState() == QtCore.Qt.Unchecked:
            for each in hide_list:
                each.setVisible(True)
            for each in show_list:
                each.setVisible(False)
        self.status_icon_update()
    

    def add_sources(self):

        self.refresh_sources()
        _sources = pm.selected()
        self.sources = [item for item in _sources]    
        [self.mesh_left_QList.addItem(str(item)) for item in self.sources] 
        _type = adb.Type(self.sources)[0]
        if _type == 'mesh':
            for i in xrange(len(self.sources)):
                self.mesh_left_QList.item(i).setIcon(QtGui.QIcon(':/out_mesh.png')) 
                        
        elif _type == 'joint':
            for i in xrange(len(self.sources)):
                self.mesh_left_QList.item(i).setIcon(QtGui.QIcon(':/kinJoint.png')) 
                            
        else:
            pass
        self.status_icon_update()
        self.type_update()
        self.target_jnts_hide()
         
        return self.sources

    def add_targets(self):
        self.refresh_targets()
        _targets = pm.selected()
        self.targets = [item for item in _targets]    
        [self.mesh_right_QList.addItem(str(item)) for item in self.targets] 
        _type = adb.Type(self.targets)[0]
        if _type == 'mesh':
            for i in xrange(len(self.targets)):
                self.mesh_right_QList.item(i).setIcon(QtGui.QIcon(':/out_mesh.png')) 
        elif _type == 'joint':
            for i in xrange(len(self.targets)):
                self.mesh_right_QList.item(i).setIcon(QtGui.QIcon(':/kinJoint.png')) 
        else:
            pass
        self.status_icon_update()
        return self.targets

    def refresh_sources(self):
        self.mesh_left_QList.clear()
        self.sources = []
        [self.comboBox[x].setVisible(True) for x in self.comboBox.keys()]
        [self.line_widget[x].setVisible(True) for x in self.line_widget.keys()]
        self.options_groupbox.setVisible(True)
        self.same_jnts_Chbx.setVisible(True)
        self.keep_same_joints_checked()
  
        
    def refresh_targets(self):
        self.mesh_right_QList.clear()
        self.targets = []
        
    
    def swap_data(self):
        self.sources, self.targets = self.targets,self.sources
        
         ## ui update
        self.mesh_left_QList.clear()
        [self.mesh_left_QList.addItem(str(item)) for item in self.sources] 
        _type_left = adb.Type(self.sources)[0]
        if _type_left == 'mesh':
            for i in xrange(len(self.sources)):
                self.mesh_left_QList.item(i).setIcon(QtGui.QIcon(':/out_mesh.png')) 
        elif _type_left == 'joint':
            for i in xrange(len(self.sources)):
                self.mesh_left_QList.item(i).setIcon(QtGui.QIcon(':/kinJoint.png')) 
        else:
            pass

        self.mesh_right_QList.clear()
        [self.mesh_right_QList.addItem(str(item)) for item in self.targets] 
        _type_right = adb.Type(self.targets)[0]
        if _type_right == 'mesh':
            for i in xrange(len(self.targets)):
                self.mesh_right_QList.item(i).setIcon(QtGui.QIcon(':/out_mesh.png')) 
        elif _type_right == 'joint':
            for i in xrange(len(self.targets)):
                self.mesh_right_QList.item(i).setIcon(QtGui.QIcon(':/kinJoint.png')) 
        else:
            pass
        

    def swap_search_replace(self):
        org_replace = self.replace_QLine.text()
        org_search = self.search_QLine.text()
        
        self.search_QLine.setText(org_replace)
        self.replace_QLine.setText(org_search)
        
        self.search_setdata = self.search_QLine.text()
        self.replace_setdata = self.replace_QLine.text()


    def target_jnts_hide(self):
        if len(self.target_jnts_QLine.text()) > 0:        
            self.copy_skin_text.setVisible(False)
            self.same_jnts_Chbx.setVisible(False)
            self.joint_text.setVisible(False)
            self.search_text.setVisible(False)
            self.replace_text.setVisible(False)
            self.mirror_across_text.setVisible(False)
            self.search_QLine.setVisible(False)
            self.replace_QLine.setVisible(False)
            self.buttons['>>>'].setVisible(False)
        else:
            self.same_jnts_Chbx.setVisible(True)
            self.joint_text.setVisible(True)
            self.search_text.setVisible(True)
            self.replace_text.setVisible(True)
            self.mirror_across_text.setVisible(True)
            self.search_QLine.setVisible(True)
            self.replace_QLine.setVisible(True)
            self.buttons['>>>'].setVisible(True)
            self.keep_same_joints_checked()


    def getList(self):                
        '''Print my selection's names into a list'''            
        oColl = pm.selected()

        for each in oColl:
            try:        
                mylist = [ x.name() for x in pm.selected()]
            except:
                mylist = [ x.getTransform().name() for x in pm.selected()]

        return mylist


    #-------------------------------------
    # FUNCTIONS


    def test(self):
        print('test')



    def copySkinAB(self):        
        if len(self.sources) == len(self.targets): ## for zip
            data_surfaceAssociation = str(self.comboBox['surface_Association'].currentText().replace(' ',''))
            data_influenceAssociation = [str(self.comboBox['influence_Association_1'].currentText().replace(' ','')),
                                     str(self.comboBox['influence_Association_2'].currentText().replace(' ','')),
                                     str(self.comboBox['influence_Association_3'].currentText().replace(' ','')),
                                     ]  
            data_influenceAssociation = [x for x in data_influenceAssociation if x != 'None']                    
                                     
                                       
            for source, target in zip (self.sources, self.targets):
                try:
                    pm.skinCluster(target, e=1, ub=1,)
                except:
                    pass
                    
                #  Pour l'option uv Space
                if self.comboBox['surface_Association'].currentText() == 'uv Space': 
                    skn = skin.Skinning(source)
                    skn.copyWeight(target,_surfaceAssociation='closestPoint', _influenceAssociation=['oneToOne', 'oneToOne'])  
                    uvMaps = target.getUVSetNames()
                    if len(uvMaps) == 1:
                        str_uvMaps = str(uvMaps[0])
                        para_uv = (str_uvMaps,str_uvMaps)
                    else:
                        para_uv = (str(uvMaps[0]),str(uvMaps[-1])) 
                    pm.copySkinWeights(source,target, surfaceAssociation='closestPoint', uvSpace=para_uv, noMirror=1, influenceAssociation=data_influenceAssociation)    
                else:                                
                    skn = skin.Skinning(source)
                    skn.copyWeight(target,_surfaceAssociation=data_surfaceAssociation, _influenceAssociation=data_influenceAssociation)   
            sys.stdout.write('// Result: Zip skin is done!  //')

        else: ## for looping
            for target in self.targets:
                try:
                    pm.skinCluster(target, e=1, ub=1,)
                except:
                    pass
                skn = skin.Skinning(self.sources[0])
                skn.copyWeight(target) 
            sys.stdout.write('// Result: Loop skin is done!  //')


    def verifyJointSideAB(self):
        if not pm.selected():
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText('Nothing is selected!!!')
            msgBox.setInformativeText('Select a mesh')
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
            ret = msgBox.exec_()
        else:
            skn = skin.Skinning(pm.selected()[0])
            skn.verifyJntsSkin() 
        

    def verifyReplaceJnts(self):
        search_for = self.search_QLine.text()
        replace_for = self.replace_QLine.text()
        try:
            for sources in self.sources:
                skn = skin.Skinning(sources)
                self.joint_to_verify = skn.find_replacement_joints(search = search_for , replace=replace_for)
                pm.select(self.joint_to_verify)                    
        except:
            inexistant = [ x for x in self.joint_to_verify  if not pm.objExists(x)]
            pm.warning(str('{} doesn\'t exist!!'.format(inexistant)).replace('u\'',"'"))

    def addJointManuallyAB(self):
        try:                       
            result1 = self.getList()
            bindJnt_target_man = [x for x in result1]                       
            self.target_jnts_QLine.setText(str(result1).replace('u\'','\''))           
            return bindJnt_target_man
        except:
            print ("// Warning: Nothing Selected! //")
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText('Nothing is selected!!!')
            msgBox.setInformativeText('Select a your joints')
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
            ret = msgBox.exec_()

        

    def labelJointsAB(self):       
        for sel in pm.ls(type='joint'):
            short = sel.split('|')[-1].split(':')[-1]
            if short.startswith('L_'):
                side = 1
                other = short[2:]
            elif short.startswith('R_'):
                side = 2
                other = short[2:]
            else:
                side = 0
                other = short
            pm.setAttr('{0}.side'.format(sel), side)
            pm.setAttr('{0}.type'.format(sel), 18)
            pm.setAttr('{0}.otherType'.format(sel), other, type='string')

    
    def transferJointSkinAB(self):
        if not pm.selected():
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText('Nothing is selected!!!')
            msgBox.setInformativeText('Select a mesh')
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
            ret = msgBox.exec_()
        else:
            skn = skin.Skinning(pm.selected()[0])
            skn.addInfluencese(self.targets)
            skn.transferJointWeights(self.sources, self.targets)

        
    def mirrorSkinAB(self):        
        for mesh in self.sources:        
            pm.select(mesh, r = True)
            pm.mel.removeUnusedInfluences()
            pm.select(None)
                              
        search_for = self.search_QLine.text()
        replace_for = self.replace_QLine.text()
        custom_joint = (self.target_jnts_setdata).replace('[','').replace(']','').replace("'","")
        custom_joint_list = custom_joint.split(',') 

        if custom_joint_list == ['']:
            custom_joint_value = False
        else:
            custom_joint_value = custom_joint_list        
       
        mirrorMode = self.mirror_options_QLine.text()
        data_surfaceAssociation = str(self.comboBox['surface_Association'].currentText().replace(' ',''))
        data_influenceAssociation = [str(self.comboBox['influence_Association_1'].currentText().replace(' ','')),
                                 str(self.comboBox['influence_Association_2'].currentText().replace(' ','')),
                                 str(self.comboBox['influence_Association_3'].currentText().replace(' ','')),
                                 ]  
        data_influenceAssociation = [x for x in data_influenceAssociation if x != 'None']                    
                                 
                                   
        for source, target in zip (self.sources, self.targets):
            try:
                pm.skinCluster(target, e=1, ub=1,)
            except:
                pass
            
            skn = skin.Skinning(source)
            skn.mirrorSkinWeight(target, 
                                _mirrorMode = mirrorMode, 
                                 _surfaceAssociation = data_surfaceAssociation, 
                                 _influenceAssociation = data_influenceAssociation,
                                 custom =custom_joint_value,
                                 search = search_for, 
                                 replace = replace_for
                                 ) 


    def selectSknJntsAB(self):
        skn = skin.Skinning(pm.selected()[0])
        pm.select(skn.getBindJoints())
        

    def mirrorBSAB(self):
        bls = bs.Blendshape.fromSelected()[0]
        bs.mirror_left_to_right_poses(bls.bs_node)


# ===============================
# BUILD WINDOW
# ===============================

def maya_main_window():
    """Return the Maya main window widget as a Python object."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def showUI():
    # Make sure the UI is deleted before recreating
	global tools_cw_ui
	try:
		tools_cw_ui.deleteLater()
	except:
		pass
	tools_cw_ui = SkinCopyWEIGHTS()
	tools_cw_ui.show()      
    
# showUI()






























