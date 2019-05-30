
import traceback

try:
    import PySide2.QtCore as QtCore
    import PySide2.QtGui as QtGui
    import PySide2.QtWidgets as QtWidgets
except ImportError:
    print("failed to import PySide2, {}".format(__file__))
    import PySide.QtCore as QtCore
    import PySide.QtGui as QtGui
    import PySide.QtWidgets as QtWidgets

try:
    # future proofing for Maya 2017.
    from shiboken2 import wrapInstance
except ImportError:
    from shiboken import wrapInstance

import pymel.core as pm
import pymel.core.datatypes as dt
import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

import getpass
import os
import ConfigParser




def maya_main_window():
    """Return the Maya main window widget as a Python object."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)



class Match_IkFk(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(Match_IkFk, self).__init__(parent)


        """Create the UI"""
        self.setWindowTitle('adbrower - Match_IkFk v1.0.0')
        self.setWindowFlags(QtCore.Qt.Tool)

        self.userName = getpass.getuser()         
        self.path_window = 'C:/Users/'+ self.userName + '/AppData/Roaming'
        self.path_linux = '/on/work/'+ self.userName + '/'
        self.folder_name ='.config/adb_Setup'
        self.file_name = 'ik_fk_match_confi.ini'
        
        self.centralwidget = QtWidgets.QWidget()
        self.centralwidget.setObjectName("match_Tool")
       
        self.final_path = self.setPath()
     
        self.dataList = self.loadData()
        # print('adb_match_IKFK settings file load from: ' + self.final_path + self.folder_name + '/' + self.file_name)
        
        self.IKFK_ctrl = self.dataList[0]
        self.IKjointsCh = self.dataList[1]         
        self.FKjointsCh = self.dataList[2]           
        self.IKCtrls = self.dataList[3] 
        self.FKCtrls = self.dataList[4]         

        self.create_Button()
        self.create_layout()

    def closeEvent (self, eventQCloseEvent):
        self.saveData()
        print('adb_match_IKFK settings file saved at: ' + self.final_path + self.folder_name + '/' + self.file_name)

    def create_Button(self):         
        self.colorWhite = '#FFFFFF'
        self.colorBlack = '#190707'
        
        self.colorBlue = '#81DAF5'
        self.colorBluelabel = '#00cdff'
        self.colorBluelabel2 = '#01A9DB'
        
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
        
        self.colorYellowlabel = 'rgb(229,198,81)'
        self.colorYellowlabel2 = 'rgb(209,200,55)'
        self.colorYellow = '#ffe100'

        self.colorDarkGrey2 = '#373737'
        self.colorDarkGrey3 = '#2E2E2E'
        self.colorGrey2 = '#4A4949'
        

        self.buttonAndFunctions = [
                # name, function , group number, labelColor, backgroundColor
                ['Add', self.getSwitchCtrl,                 1, self.colorWhite, self.colorGreen],
                ['Add ', self.getIKjointsCh,                1, self.colorWhite, self.colorGreen],
                ['Add  ', self.getFKjointsCh,               1, self.colorWhite, self.colorGreen],
                ['Add   ', self.getIKjctrl,                 1, self.colorWhite, self.colorGreen],
                ['Add    ', self.getFKjctrl,                1, self.colorWhite, self.colorGreen],
                ['Snap IK-FK', self.IK_FK_switch,           2, self.colorYellowlabel, self.colorDarkGrey3],
                ['Permanent Switch', self.PermanentSwitch,  2, self.colorYellowlabel, self.colorDarkGrey3],
                ['Delete the Match Script', self.KillAll,     2, self.colorYellowlabel, self.colorDarkGrey3],
                ['Clear Info', self.Refresh,                2, self.colorLightGrey, self.colorDarkGrey2],
        ]

        self.buttons = {}        
        for buttonName,buttonFunction, _, labColor, bgColor in self.buttonAndFunctions:
            self.buttons[buttonName] = QtWidgets.QPushButton(buttonName)
            self.buttons[buttonName].clicked.connect(buttonFunction)
            self.buttons[buttonName].setFixedHeight(25)
            self.buttons[buttonName].setStyleSheet(
                    'padding:4px; text-align:Center; font: normal; color:{}; background-color:{};'.format(labColor,bgColor))

        ## Build Buttons
        self.buttons1 = [button for button, _, groupNumber,labColor, bgColor in self.buttonAndFunctions if groupNumber == 1] 
        self.buttons2 = [button for button, _, groupNumber,labColor, bgColor in self.buttonAndFunctions if groupNumber == 2] 

#---------------

        self.lineEditAndFunctions = [
                # name, function , placeHolderText, 
                ['switch Control', self.empty,      "Select Switch Control and add '.' switch attr" ],
                ['ik jnts', self.empty,             "Select Ik joints chain"],
                ['fk jnts', self.empty,             "Select Fk joints chain"],
                ['ik ctrl', self.empty,             "Select Ik controls"    ],
                ['fk ctrl', self.empty,             "Select Fk controls"],
        ]

        self.lineEdit = {}        
        for buttonName, buttonFunction, textHolder,  in self.lineEditAndFunctions:
            self.lineEdit[buttonName] = QtWidgets.QLineEdit()
            self.lineEdit[buttonName].setPlaceholderText(textHolder)
            self.lineEdit[buttonName].setFixedWidth(250)

        ## Build Lines edits
        self.lineEdit1 = [x for x, _, textHolder in self.lineEditAndFunctions]

        self.lineEdit['switch Control'].setText(self.IKFK_ctrl)        
        self.lineEdit['ik jnts'].setText(self.IKjointsCh)        
        self.lineEdit['fk jnts'].setText(self.FKjointsCh)        
        self.lineEdit['ik ctrl'].setText(self.IKCtrls)        
        self.lineEdit['fk ctrl'].setText(self.FKCtrls)        


#---------------

        self.textLabelAndFunctions = [
                                      'SWITCH CONTROL :',  
                                      'Ik JOINTS :',  
                                      'Fk JOINTS :',  
                                      'Ik CONTROLS :',  
                                      'Fk CONTROLS :',  
                                     ]

        self.textLabel = {}        
        for buttonName in self.textLabelAndFunctions:
            self.textLabel[buttonName] = QtWidgets.QLabel(buttonName)
            self.textLabel[buttonName].setStyleSheet('padding-left:10px; text-align:Center; font: normal; color:{};'.format(''))

        ## Build Text Label
        self.textLabel1 = [x for x in self.textLabelAndFunctions]
    
    def create_layout(self):
        
        ''' all layouts '''
                
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
            return text      

        ## Main layout
        self.main_layout = QtWidgets.QGridLayout()
        self.main_layout.setContentsMargins(*[5]*4)        
        self.main_layout.setSpacing(7)
        self.setLayout(self.main_layout)

        title_layout = QtWidgets.QVBoxLayout()
        self.title = addText('Seamless IK-FK Switch Tool') 
        self.title.setStyleSheet('padding-right:100px; text-align:Center; font: normal; color:{}'.format(''))     
        title_layout.addWidget(self.title)
        
        self.space1 = addText('<<<')      
        self.space2 = addText('<<<')      
        self.space3 = addText('<<<')      
        self.space4 = addText('<<<')      
        self.space5 = addText('<<<')  

        add_btn_layout = QtWidgets.QVBoxLayout()
        lineEdit_layout = QtWidgets.QVBoxLayout()
        space_layout = QtWidgets.QVBoxLayout()
        label_layout = QtWidgets.QVBoxLayout()
        apply_layout = QtWidgets.QHBoxLayout()
        
        for buttonName in self.buttons1[0:]:
            add_btn_layout.addWidget(self.buttons[buttonName])
            self.buttons[buttonName].setFixedWidth(70)
            
        for buttonName in self.lineEdit1:
            lineEdit_layout.addWidget(self.lineEdit[buttonName])

        for buttonName in self.textLabel1:
            label_layout.addWidget(self.textLabel[buttonName])

        for buttonName in self.buttons2[:1]:
            self.main_layout.addWidget(self.buttons[buttonName], 3,0,1,4)
            self.buttons[buttonName].setFixedWidth(500)
            self.buttons[buttonName].setFixedHeight(30)

        for buttonName in self.buttons2[1:2]:
            apply_layout.addWidget(self.buttons[buttonName])
            self.buttons[buttonName].setFixedHeight(30)

        for buttonName in self.buttons2[2:]:
            apply_layout.addWidget(self.buttons[buttonName])
            self.buttons[buttonName].setFixedHeight(30)
        
        lineEdit_layout.setSpacing(12)
        space_layout.setSpacing(1)

        space_layout.addWidget(self.space1)
        space_layout.addWidget(self.space2)
        space_layout.addWidget(self.space3)
        space_layout.addWidget(self.space4)
        space_layout.addWidget(self.space5)
        
        #=======================
        # MAIN LAYOUT BUILD
        #=======================
        
        self.main_layout.addLayout(title_layout,    0,1,1,4)
        self.main_layout.addLayout(label_layout,    1,0)
        self.main_layout.addLayout(lineEdit_layout, 1,1)
        self.main_layout.addLayout(space_layout,    1,2)
        self.main_layout.addLayout(add_btn_layout,  1,3)  
        self.main_layout.addLayout(apply_layout,    4,0,1,4)  

        self.buttons['Add  '].setVisible(False)
        self.lineEdit['fk jnts'].setVisible(False)
        self.textLabel['Fk JOINTS :'].setVisible(False)

          
#-----------------------------------
#  SLOTS
#----------------------------------- 

    def empty(self):
        pass
 
    def getList(self):                
        '''Print my selection's names into a list'''           

        oColl = pm.selected()
        for each in oColl:
            try:        
                mylist = [ x.name() for x in pm.selected()]
            except:
                mylist = [ x.getTransform().name() for x in pm.selected()]

        return mylist
 
    def writeText(self):
        file_ini = open(self.file_name, 'w+')
        file_ini.write('[General] \n')      
      
        file_ini.write("switch_ctrl_data= \n")      
        file_ini.write("Ik_jnts_data= \n")
        file_ini.write("Fk_jnts_data= \n")
        file_ini.write("Ik_ctrl_data= \n")
        file_ini.write("Fk_ctrl_data= \n")          
        file_ini.close()



    def setPath(self):    
        def finalPath():
            if not os.path.exists(self.path_linux):
                # print('path linux does NOT extist')
                pass
            else:
                # print('path linux does extist')   
                return self.path_linux   
           
            if not os.path.exists(self.path_window):
                # print('path window does NOT extist') 
                pass              
            else:
                # print('path window does extist')
                return self.path_window      

        self.final_path = finalPath() 

        os.chdir(self.final_path)        
        try:
            os.makedirs(self.folder_name)        
        except :
            pass          
            
        if os.path.exists(self.final_path + '/' + self.folder_name + '/' + self.file_name): 
            # print ('file exist')
            pass
        else:
            os.chdir(self.final_path + '/' +  self.folder_name)
            # print(os.getcwd())
               
            self.writeText()
        
        return(self.final_path)      


    def saveData(self):
        os.chdir(self.final_path)        
        try:
            os.mkdir(folder_name)        
        except :
            pass
                
        os.chdir(self.final_path +'/'+ self.folder_name)
        # print(os.getcwd())
           
        file_ini = open(self.file_name, 'w+')
        file_ini.write('[General] \n')      
      
        for buttonName in self.lineEdit1[:1]:
            file_ini.write("switch_ctrl_data=" + self.lineEdit[buttonName].text()+ ' \n')
        
        for buttonName in self.lineEdit1[1:2]:
            file_ini.write("Ik_jnts_data=" + self.lineEdit[buttonName].text()+ ' \n')

        for buttonName in self.lineEdit1[2:3]:
            file_ini.write("Fk_jnts_data=" + self.lineEdit[buttonName].text()+ ' \n')

        for buttonName in self.lineEdit1[3:4]:
            file_ini.write("Ik_ctrl_data=" + self.lineEdit[buttonName].text()+ ' \n')

        for buttonName in self.lineEdit1[4:]:
            file_ini.write("Fk_ctrl_data=" + self.lineEdit[buttonName].text()+ ' \n')
          
        # file_ini.close()

        return(file_ini)


        
    def loadData(self):        
        try:               
            dataList = []
            config = ConfigParser.ConfigParser()
            config.read( self.final_path + '/' + self.folder_name + '/' + self.file_name)
            
            self.switch_ctrl_setdata = config.get("General", "switch_ctrl_data")
            self.Ik_jnts_setdata = config.get("General", "Ik_jnts_data")
            self.Fk_jnts_setdata = config.get("General", "Fk_jnts_data")
            self.Ik_ctrl_setdata = config.get("General", "Ik_ctrl_data")
            self.Fk_ctrl_setdata = config.get("General", "Fk_ctrl_data")

            dataList.append(self.switch_ctrl_setdata)
            dataList.append(self.Ik_jnts_setdata)
            dataList.append(self.Fk_jnts_setdata)
            dataList.append(self.Ik_ctrl_setdata)
            dataList.append(self.Fk_ctrl_setdata)
            
            return(dataList)
            
        except:
            os.chdir(self.final_path + '/' +  self.folder_name)
            # print(os.getcwd())
               
            self.writeText()

                  
#-----------------------------------
#  FUNCTIONS
#----------------------------------- 

    
    def getSwitchCtrl(self): 
        try:            
            self.switchCtrl = pm.selected()                       
            ctrl = pm.selected()[0]
            ctrl_name = ctrl.name()
            result1 = str(ctrl_name + ".IK_FK_Switch")            

            for buttonName in self.lineEdit1[:1]:
                self.lineEdit[buttonName].setText(result1)
        except:
            print ("// Warning: Nothing Selected! //")


    def getIKjointsCh(self): 
        try:                      
            result2 = self.getList()

            for buttonName in self.lineEdit1[1:2]:
                self.lineEdit[buttonName].setText(str(result2).replace("u'"," ").replace("'"," "))

        except:
            print ("// Warning: Nothing Selected! //")


    def getFKjointsCh(self): 
        try:           
            result3 = self.getList()
           
            for buttonName in self.lineEdit1[2:3]:
                self.lineEdit[buttonName].setText(str(result3).replace("u'"," ").replace("'"," "))
       
        except:
            print ("// Warning: Nothing Selected! //")


    def getIKjctrl(self): 
        try:           

            result4 = self.getList()        
            for buttonName in self.lineEdit1[3:4]:
                self.lineEdit[buttonName].setText(str(result4).replace("u'"," ").replace("'"," "))
        
        except:
            print ("// Warning: Nothing Selected! //")

    def getFKjctrl(self): 
        try:                        
            result5 = self.getList()           
            for buttonName in self.lineEdit1[4:]:
                self.lineEdit[buttonName].setText(str(result5).replace("u'"," ").replace("'"," "))
        
        except:
            print ("// Warning: Nothing Selected! //")
 

    def IK_FK_switch(self):
        try:
            self.saveData()        
            self.dataList = self.loadData()
            
            self.IKFK_ctrl = self.dataList[0]
            self.IKjointsCh = self.dataList[1]         
            self.FKjointsCh = self.dataList[2]           
            self.IKCtrls = self.dataList[3] 
            self.FKCtrls = self.dataList[4] 
                 
            value = pm.PyNode(self.IKFK_ctrl).get()
            FKCtrls_str = (self.Fk_ctrl_setdata).replace('[','').replace(']','')       
            FKCtrls_list = FKCtrls_str.split(',')   
           
            IKCtrls_str = (self.Ik_ctrl_setdata).replace('[','').replace(']','')       
            IKCtrls_list = IKCtrls_str.split(',')  

            IKjointsCh_str = (self.Ik_jnts_setdata).replace('[','').replace(']','')       
            IKjointsCh_list = IKjointsCh_str.split(',') 

            if value == 0:
                pm.PyNode(self.IKFK_ctrl).set(1)
                for oFkCtrls, oIKjointsCh in zip (FKCtrls_list ,IKjointsCh_list):
                    pm.matchTransform(oFkCtrls,oIKjointsCh, pos = True, rot = True)
                
            else:
                pm.PyNode(self.IKFK_ctrl).set(0)
                pm.matchTransform(IKCtrls_list, FKCtrls_list[-1],pos = True)
        
        except MayaNodeError: 
            pm.warning()
            pm.warning('Fulfill UI')



    def PermanentSwitch(self):              
    
        def switch():               
            value = pm.PyNode(self.IKFK_ctrl).get()
            IKFK_str = (self.Fk_ctrl_setdata).replace('[','').replace(']','')           
            FKCtrls_str = (self.Fk_ctrl_setdata).replace('[','').replace(']','')       
            FKCtrls_list = FKCtrls_str.split(',')             
            IKCtrls_str = (self.Ik_ctrl_setdata).replace('[','').replace(']','')       
            IKCtrls_list = IKCtrls_str.split(',')  
            IKjointsCh_str = (self.Ik_jnts_setdata).replace('[','').replace(']','')       
            IKjointsCh_list = IKjointsCh_str.split(',') 

            if value == 1:
                for oFkCtrls, oIKjointsCh in zip (FKCtrls_list ,IKjointsCh_list):
                    pm.matchTransform(oFkCtrls,oIKjointsCh, pos = True, rot = True)
            
            if value == 0: 
                pm.matchTransform(IKCtrls_list, FKCtrls_list[-1],pos = True)

        IKFK_ctrl_name = pm.PyNode(self.IKFK_ctrl).name()
        self.jobNum = mc.scriptJob( ac= [IKFK_ctrl_name ,switch]) 
        
           
    def KillAll(self):
        try:
            mc.scriptJob( kill=self.jobNum, force=True)
            print('Script Job Deleted!')
        except:
            print ("// Warning: Nothing to Delete //")


    def Refresh(self):
        file_ini = self.saveData()
        
        for buttonName in self.lineEdit1[:1]:
            self.lineEdit[buttonName].setText('')

        for buttonName in self.lineEdit1[1:2]:
            self.lineEdit[buttonName].setText('')

        for buttonName in self.lineEdit1[2:3]:
            self.lineEdit[buttonName].setText('')

        for buttonName in self.lineEdit1[3:4]:
            self.lineEdit[buttonName].setText('')

        for buttonName in self.lineEdit1[4:]:
            self.lineEdit[buttonName].setText('')

        ## file ini
        file_ini.write("switch_ctrl_data= \n")        
        file_ini.write("Ik_jnts_data= \n")
        file_ini.write("Fk_jnts_data= \n")
        file_ini.write("Ik_ctrl_data= \n")
        file_ini.write("Fk_ctrl_data= \n")
        


def ui():
	global tools_cw_ui
	try:
		tools_cw_ui.deleteLater()
	except:
		pass
	tools_cw_ui = Match_IkFk()
	tools_cw_ui.show() 
