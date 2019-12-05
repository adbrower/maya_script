from PySide2 import QtWidgets, QtCore
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


#-----------------------------------
#  CLASS
#----------------------------------- 


class mainLayout(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    __dialog = None
    
    @classmethod
    def show_dialog(cls):
        if cls.__dialog is None:
            cls.__dialog = cls()
        else:
            cls.__dialog.raise_() 
        cls.__dialog.show()
        
    def __init__(self,parent=None):
        super(mainLayout, self).__init__(parent = parent)

        
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
    
# showUI()


# mainLayout.show_dialog()
