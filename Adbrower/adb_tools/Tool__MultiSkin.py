from functools import wraps

import maya.cmds as mc
import maya.mel as mel
import pymel.core as pm
from PySide2 import QtCore, QtGui, QtWidgets

import adb_core.Class__multi_skin as ms
import adbrower
from CollDict import pysideColorDic as pyQtDic
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya_script import Adbrower


adb = adbrower.Adbrower()

VERSION = 1.0

PATH_WINDOW = Adbrower.PATH_WINDOW_INIT + 'AppData/Roaming'
PATH_LINUX = Adbrower.PATH_LINUX_INIT
FOLDER_NAME = Adbrower.FOLDER_NAME_INIT
ICONS_FOLDER = Adbrower.ICONS_FOLDER_INIT

YELLOW = '#ffe100'
ORANGE = '#fd651d'
GREEN = '#597A59'
DARKRED = '#745a54'

def undo(func):
    ''' 
    Puts the wrapped `func` into a single Maya Undo action, then
    undoes it when the function enters the finally: block
    from schworer Github
    '''
    @wraps(func)
    def _undofunc(*args, **kwargs):
        try:
            # start an undo chunk
            mc.undoInfo(ock=True)
            return func(*args, **kwargs)
        finally:
            # after calling the func, end the undo chunk
            mc.undoInfo(cck=True)
    return _undofunc


def flatList(ori_list=''):
    """
    Flatten a list
    """
    flat_list = []
    for item in ori_list:
        if isinstance(item, list):
            for sub_item in item:
                flat_list.append(sub_item)
        else:
            flat_list.append(item)
    return flat_list

#-----------------------------------
#  CLASS
#----------------------------------- 



class MultiSkin_UI(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    __dialog = None
    
    @classmethod
    def show_dialog(cls):
        if cls.__dialog is None:
            cls.__dialog = cls()
        else:
            cls.__dialog.raise_() 
        cls.__dialog.show()
    
    def __init__(self,parent=None):                
        super(MultiSkin_UI, self).__init__(parent=parent)
    
        self.setObjectName('multi skin ui')
        self.starting_height = 500
        self.starting_width = 390
        self.setWindowTitle('adbrower - Multi Skin Tool' + ' v' + str(VERSION))
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setMinimumWidth(self.starting_width)
        self.resize(self.starting_width, self.starting_height)
    
        
        # -----------------------------
        # ---  Create scrollArea

        self.mainBox = QtWidgets.QVBoxLayout()
        self.mainBox.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout = QtWidgets.QScrollArea()

        self.mainBox.addWidget(self.scroll_layout)
        self.setLayout(self.mainBox)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_layout.setWidgetResizable(True)
        self.scroll_layout.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.scroll_layout.setFrameShadow(QtWidgets.QFrame.Plain)

        self.scroll_widget = QtWidgets.QWidget()
        self.scroll_layout.setWidget(self.scroll_widget)    
    
    
        # -----------------------------
        # ---  Main Layout

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(*[5] * 4)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)

        self.scroll_widget.setLayout(self.main_layout)
        self.widgetsAndLayouts()
        self.buildMainLayout()


    def widgetsAndLayouts(self):

        # --------- Predefine widgets

        def addLine():
            line = QtWidgets. QFrame()
            line.setFrameShape(QtWidgets.QFrame.HLine)
            return line

        def addText(message, alignement=QtCore.Qt.AlignCenter, height=30, bold=False):
            myFont = QtGui.QFont()
            myFont.setBold(bold)
            text = QtWidgets.QLabel(message)
            text.setAlignment(alignement)
            text.setFixedHeight(height)
            text.setFont(myFont)
            return text    
    

    # ------------------------------
    #--------- Layouts

        self.vLayoutAndFunctions = [
            # name,              margins
            ['treeWidget',           [1, 1, 1, 1]],
        ]
        self.vlayout = {}
        for layoutName, margins, in self.vLayoutAndFunctions:
            self.vlayout[layoutName] = QtWidgets.QVBoxLayout()
            self.vlayout[layoutName].setContentsMargins(margins[0], margins[1], margins[2], margins[3],)    
    

        # ------------------------------
        # --------- TREE LIST WIDGET

        self.meshTreeWidget=QtWidgets.QTreeWidget()

        self.meshTreeWidget.setHeaderLabel('Cloth Tree View')
        self.vlayout['treeWidget'].addWidget(self.meshTreeWidget)
        header = QtWidgets.QTreeWidgetItem(["Geometries"])
        self.meshTreeWidget.setHeaderItem(header)
 
        
        self.meshTreeWidget.itemClicked.connect(self.singleClickedAction)
        self.filterList = self.filterMeshes(filter='skinClusters')
        
        self.populateQTree(self.filterList)
        
    
    
    def buildMainLayout(self):
        # ------------------------------
        # --------- BUILD MAIN LAYOUT    
        
        self.main_layout.addLayout(self.vlayout['treeWidget'])



# ==================================
#  SLOTS
# ==================================    

    def populateQTree(self, filterList):
         # Meshes
        # ----------------------
        
        roots = [QtWidgets.QTreeWidgetItem(self.meshTreeWidget, [str(item)]) for item in filterList]
        [root.setIcon(0, QtGui.QIcon(':/out_mesh.png')) for root in roots]
        [root.setExpanded(True) for root in roots]
        
        
        # Shapes
        # ----------------------
        
        QtShapes = []
        shape_dic = self.getAllShapes(self.getAllMeshes())
        QTroots_dic = {} # Keys are Qtree object
        for root in roots:
            QTroots_dic.update({root:shape_dic[root.text(0)]})
        
        # added the shapes under there mesh
        for QTroot, shapesList in QTroots_dic.items():
            [QtWidgets.QTreeWidgetItem(QTroot, [str(shape)]) for shape in shapesList]
            
            # changed their color
            child_count=QTroot.childCount()
            children=[QTroot.child(index) for index in range(child_count)]
            [child.setForeground(0, QtGui.QBrush(QtGui.QColor(YELLOW))) for child in children]            
            [child.setIcon(0, QtGui.QIcon(':/out_transform.png')) for child in children]   
            [child.setExpanded(True) for child in children]         
            [QtShapes.append(child) for child in children]
                
        # skinClusters
        # ----------------------
        QTClusters = []      
        cluster_dic = self.getSkinClusterbyShape(flatList(shape_dic.values()))
        QTshape_dic = {}
        for shape in QtShapes:
            QTshape_dic.update({shape:cluster_dic[shape.text(0)]})
            
        # added the skinCluster under there shape
        for QTshape, clusterList in QTshape_dic.items():
            if clusterList == 'None':
                pass
            else:
                QtWidgets.QTreeWidgetItem(QTshape, [str(clusterList)]) 
              
            # changed their color
            child_count=QTshape.childCount()
            children=[QTshape.child(index) for index in range(child_count)]
            [child.setForeground(0, QtGui.QBrush(QtGui.QColor(GREEN))) for child in children]            
            [child.setIcon(0, QtGui.QIcon(':/cluster.png')) for child in children]            
            [QTClusters.append(child) for child in children]   
            


        # Joints
        # ---------------------- 
        bindJoints_dic = self.getBindJointsFromCluster([x for x in cluster_dic.values() if x != 'None'])
    
        QTcluster_dic = {}
        for cluster in QTClusters:
            QTcluster_dic.update({cluster:bindJoints_dic[cluster.text(0)]})
            
        for QTCluster, jointList in QTcluster_dic.items():
            [QtWidgets.QTreeWidgetItem(QTCluster, [str(jnt)]) for jnt in jointList]
            
            # changed their color
            child_count=QTCluster.childCount()
            children=[QTCluster.child(index) for index in range(child_count)]
            [child.setForeground(0, QtGui.QBrush(QtGui.QColor(DARKRED))) for child in children]            
            [child.setIcon(0, QtGui.QIcon(':/out_joint.png')) for child in children]            
 
            

    def singleClickedAction(self):
        mySelection = self.meshTreeWidget.currentItem()
        pm.select(mySelection.text(0), r=1)
        
    
    def filterMeshes(self, filter = 'all'):
        """
        filter:
            all : all meshes
            skinClusters : all meshes with skinClusters
            None
        """
        if filter =='all':
            return getAllMeshes()

        elif filter == "skinClusters":
            clusters = pm.ls(type='skinCluster')
            meshesShapes = set(sum([pm.skinCluster(c, q=1, geometry=1) for c in clusters], []))
            meshes = set([x.getParent() for x in meshesShapes])
            return meshes
        
        elif filter == 'None':
            return None
            
        
# ==================================
#  STATIC METHOD
# ==================================    

    @staticmethod
    def getSkinCluster(_transform):
        """
        Find a SkinCluster from a transform
        Returns the skinCluster node
        """
        result = []
        if not (pm.objExists(_transform)):
            return result
        validList = mel.eval('findRelatedDeformer("' + str(_transform) + '")')
        if validList is None:
            return result
        for elem in validList:
            if pm.nodeType(elem) == 'skinCluster':
                result.append(elem)
        pm.select(result, r=True)
        result_node = pm.selected()
        
        if len(result_node) > 1:
            return result_node
        else:
            try:
                return result_node[0]
            except IndexError:
                return False

    @staticmethod
    def getBindJointsFromCluster(clusterList):
        """
        Find all joints attached to a skinCluster
        @param clusterList: List. list of skin Clusters
        return dic with key: skin Cluster. Value: list of joint 
        """
        bindJoints_dic = {}
        for cluster in clusterList:
            all_binds_jnts = [x for x in pm.listConnections(str(cluster) + '.matrix[*]', s=1)]
            bindJoints_dic.update({str(cluster):all_binds_jnts})
        return bindJoints_dic
    
    @staticmethod
    def getAllMeshes():
        """
        return: list of all meshes / geometry
        """
        shapesList = pm.ls(type="mesh", ni=1)
        transformList = list(set(pm.listRelatives(shapesList ,parent=True)))
        return transformList
    
    @staticmethod
    def getAllShapes(transforms):
        """
        @param transforms: List. 
        return :  dictionnary with key:mesh / values: shapes
        """
        shapes_dic = {}
        for transform in transforms:
            all_shapes = pm.PyNode(transform).getShapes(ni=True)
            shapes_dic.update({str(transform):all_shapes})            
        return shapes_dic
            
    
    def getSkinClusterbyShape(self, shapes):
        """
        get skinCluster attached to the shape
        @param shapes: List
        return: List
        """
        cluster_dic = {}
        for shape in shapes:        
            try:
                incoming = cmds.listConnections('{}.inMesh'.format(shape))[0]
                if pm.objectType(incoming) == 'skinCluster':
                    cluster_dic.update({str(shape):incoming})
                else:
                    skinCluster = self.getSkinCluster(shape)
                    if skinCluster:
                        if len(skinCluster) > 1:
                            cluster_dic.update({str(shape):'None'})
                        else:
                            cluster_dic.update({str(shape):skinCluster})                    
                    else:
                        cluster_dic.update({str(shape):'None'})                    
            except TypeError:
                cluster_dic.update({str(shape):'None'})
        return cluster_dic

   
   
# ===============================
# BUILD WINDOW
# ===============================


def showUI(dialog = False):
    if dialog:
        MultiSkin_UI.show_dialog()
    else:    
        # Make sure the UI is deleted before recreating
        global tools_cw_ui
        try:
            tools_cw_ui.deleteLater()
        except:
            pass
        tools_cw_ui = MultiSkin_UI()
        tools_cw_ui.show()
        
        
    
showUI()
