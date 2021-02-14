# -------------------------------------------------------------------
# adb Module Toolbox
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# -------------------------------------------------------------------


import pymel.core as pm
import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.mel as mel

import sys, os, ConfigParser
from functools import wraps

#-----------------------------------
#  CUSTOM IMPORT
#-----------------------------------

from CollDict import colordic
import adbrower
from maya_script import Adbrower
from adbrower import undo, timeit
import adb_library.adb_utils.Functions__topology as adbTopo
import adb_core.deformers.Class__Blendshape as adbBLS


adb = adbrower.Adbrower()

# reload(adbBLS)
# reload(adbTopo)


VERSION = 4.0
ICONS_FOLDER = Adbrower.ICONS_FOLDER_INIT
PATH_WINDOW = Adbrower.PATH_WINDOW_INIT + 'AppData/Roaming'
PATH_LINUX = Adbrower.PATH_LINUX_INIT
FOLDER_NAME = Adbrower.FOLDER_NAME_INIT

FILE_NAME = 'Topology_Tool_config.ini'

def loadPlugin(plugin):
    if not mc.pluginInfo(plugin, query=True, loaded=True):
        try:
            mc.loadPlugin(plugin)
        except RuntimeError:
            pm.warning('could not load plugin {}'.format(plugin))

loadPlugin('adbResetDelta__Command')
loadPlugin('adbMirrorBlsWeights__Command')


#-----------------------------------
#  CLASS
#-----------------------------------


class TopoTool(object):
    """This Tool makes a tilt fonction on any object  """

    def __init__(self, **kwargs):
        self.name = 'Topology Tool'
        self.object = 'Topology_win'
        self.symetry_data = None
        self.targetGeo = None
        self.baseGeo = None
        self.edge = None

        # -----------------------------
        # ---  DATA

        self.final_path = self.setPath()
        self.dataList = []
        self.dataList = self.loadData()
        if self.dataList is not []:
            self.baseGeo = self.dataList[1]
            self.edge = self.dataList[0]

        self.ui()

        try:
            self.load_symetry_data()
        except:
            pass

        pm.scriptJob(uiDeleted = (self.object, self.death_notice), runOnce=True)

    def death_notice(self, *_):

        self.saveData()

    def ui(self):
        template = pm.uiTemplate('ExampleTemplate', force = True )
        template.define(pm.button, w=60, height = 25)
        template.define(pm.frameLayout, borderVisible = False, labelVisible = False)

        if pm.window(self.object  , q=1, ex=1):
            pm.deleteUI(self.object )

        with pm.window(self.object , t= self.name , s=True, tlb=False, mnb=True) as win:
            with template:
                with pm.columnLayout(adj=True, rs = 1):
                    pm.text('MESH')
                    with pm.rowLayout(adj=True, numberOfColumns=4):
                        pm.separator(w=2, vis=0)
                        self.symetry_status = pm.iconTextButton(h=20, w=20, i=ICONS_FOLDER+'red_status')
                        pm.button(label="Load Symetry Data", w=200,  backgroundColor = colordic['grey1'],  c = pm.Callback(self.load_symetry_data))
                    with pm.columnLayout(adj=True, rs = 4):
                        self.targetGeoInput = pm.textField(pht='Target Geo', w=60, ed=0, bgc=(0.15, 0.15, 0.15), tx= str(self.edge))
                        pm.popupMenu()
                        pm.menuItem(l='Select Mesh', c=pm.Callback(self.selectTargetMesh))
                        pm.menuItem(l='Clear', c=pm.Callback(self.clearAB, 'target'))
                    
                    with pm.frameLayout( cll = True, bgc=(0.15, 0.15, 0.15), labelVisible=True , cl = True, label = " BLENDSHAPE"):
                        with pm.columnLayout(adj=True, rs = 4):
                            pm.button(label="Delete History",  backgroundColor = colordic['grey1'], c = mc.DeleteHistory)
                            pm.button(label="Add BlendShape", w=110, backgroundColor = colordic['grey1'], c=pm.Callback(self.addBlendshapeAB))

                        with pm.rowLayout(adj=True, numberOfColumns=4):
                            pm.iconTextButton(h=20, w=20, i='refresh', c=pm.Callback(self.refreshBlsMenu))

                            self.bls_node = pm.optionMenu('bls_node', w=130)
                            all_bls = self.getAllBLS()
                            if all_bls != []:
                                for node in all_bls:
                                    pm.menuItem(label="{}".format(node.bs_node))
                            else:
                                pm.menuItem(label = 'None')
                            pm.separator(w=2)
                            pm.button(label="Add Target",  backgroundColor = colordic['grey1'], c=pm.Callback(self.addTargetAB))

                        with pm.columnLayout(adj=True, rs = 4):
                            pm.button(label="Mirror Blendshape Map",  backgroundColor = colordic['green3'], c=pm.Callback(self.mirrorBlsWeightsMapAB))
                            pm.button(label="Mirror Target Blendshape Map",  backgroundColor = colordic['green3'], c=pm.Callback(self.mirrorBlsTargetMapAB))


                    with pm.frameLayout( cll = True, bgc=[0.15, 0.15, 0.15], labelVisible=True , cl = False, label = " RESET"):
                        with pm.rowLayout( adj=True, numberOfColumns=2):
                            self.baseGeoInput = pm.textField(pht='Base Geo', w=50, ed=0, bgc=(0.15, 0.15, 0.15), tx= str(self.baseGeo))
                            pm.popupMenu()
                            pm.menuItem(l='Select Mesh',  c=pm.Callback(self.selectBaseMesh))
                            pm.menuItem(l='Clear', c=pm.Callback(self.clearAB, 'base'))
                            pm.button('<<<', w=40, c=pm.Callback(self.addBaseGeo))

                        with pm.rowLayout(numberOfColumns=4):
                            pm.text('   RESET :    ')
                            self.inputXchbx = pm.checkBox(l='X', w=40, v=1)
                            self.inputYchbx = pm.checkBox(l='Y', w=40, v=1)
                            self.inputZchbx = pm.checkBox(l='Z', w=40, v=1)

                        with pm.rowLayout(numberOfColumns=4):
                            pm.separator(w=25, vis=0)
                            pm.radioCollection()
                            pm.separator(vis=0, w=30)
                            self.posInput = pm.radioButton(label="Pos",  sl=0, )
                            self.negInput = pm.radioButton(label="Neg",  sl=1, w=80)

                        with pm.columnLayout( adj=True, rs=4) :
                            self.percentageSlider = pm.intSliderGrp(field=True, minValue=1, maxValue=100,
                                fieldMinValue=0, fieldMaxValue=100, value=100, cw2=(40, 100), ann="percentage of modification on your mesh")
                            pm.popupMenu()
                            pm.menuItem(l='20', c=lambda*args:pm.intSliderGrp(self.percentageSlider, e=1, value=20))
                            pm.menuItem(l='50', c=lambda*args:pm.intSliderGrp(self.percentageSlider, e=1, value=50))
                            pm.menuItem(l='75', c=lambda*args:pm.intSliderGrp(self.percentageSlider, e=1, value=75))
                            pm.button('Reset Mesh', w=40, backgroundColor = colordic['green3'], c=pm.Callback(self.resetMeshAB))

                    with pm.frameLayout(cll = True, bgc=[0.15, 0.15, 0.15], labelVisible=True , cl=False, label=" SELECTION"):
                        with pm.rowLayout(adj=True, numberOfColumns=3):
                            pm.button(label="Invert",  backgroundColor=colordic['grey1'], w=110, c=lambda *args: mel.eval('InvertSelection'))
                            pm.button(label="Match",  backgroundColor=colordic['grey1'], w=110, c=pm.Callback(self.MatchSelection))

                        with pm.rowLayout(adj=True, numberOfColumns=4):
                            pm.button(label="R",  backgroundColor=colordic['grey1'], w=70, c=pm.Callback(self.select_right_edge))
                            pm.button(label="C",  backgroundColor=colordic['grey1'], w=70, c=pm.Callback(self.select_center_edge))
                            pm.button(label="L",  backgroundColor=colordic['grey1'], w=70, c=pm.Callback(self.select_left_edge))

                        with pm.rowLayout(adj=True, numberOfColumns=2):
                            pm.button(label="Mirror Selection",  backgroundColor=colordic['grey1'], c=pm.Callback(self.selectMirrorVtxAB))
                    with pm.frameLayout( cll = True, bgc=[0.15, 0.15, 0.15], labelVisible=True , cl = False, label = " MODIFY"):
                        pm.text('MIRRORING',h=20)
                        with pm.rowLayout( adj=True, numberOfColumns=3):
                            pm.radioCollection()
                            self.leftInput = pm.radioButton(label="Left > Right" , sl=1)
                            self.rightInput = pm.radioButton(label="Right > Left", sl=0)
                        with pm.columnLayout( adj=True, rs=4) :
                            pm.button(label="Mirror Position",  backgroundColor=colordic['grey1'], c=pm.Callback(self.mirrorAB))
                            pm.button(label="Flip",  backgroundColor=colordic['grey1'], c=pm.Callback(self.flipMeshAB))
                            pm.separator(h=10)
                            self.outputWin = pm.textScrollList(h=20, w=200)

#-----------------------------------
#  UI
#-----------------------------------

    def writeText(self):
        with open(FILE_NAME, 'w+') as file_ini:
            file_ini.write('[General] \n')
            file_ini.write('source_edge= \n')
            file_ini.write('source_base= \n')


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
        except:
            pass

        if os.path.exists(self.final_path + '/' + FOLDER_NAME + '/' + FILE_NAME):
            pass
        else:
            os.chdir(self.final_path + '/' + FOLDER_NAME)
            self.writeText()

        return(self.final_path)


    def saveData(self):
        os.chdir(self.final_path)
        try:
            os.mkdir(folder_name)
        except:
            pass

        os.chdir(self.final_path + '/' + FOLDER_NAME)
        with open(FILE_NAME, 'w+') as file_ini:
            file_ini.write('[General] \n')
            if self.edge is None:
                file_ini.write("source_edge= \n")
            else:
                file_ini.write('source_edge=' + str(self.edge) +  '\n')

            if self.baseGeo is None:
                file_ini.write("source_base=  \n")
            else:
                file_ini.write('source_base=' + str(self.baseGeo) +  '\n')


    def loadData(self):
        dataList = []
        config = ConfigParser.ConfigParser()
        config.read(self.final_path + '/' + FOLDER_NAME + '/' + FILE_NAME)

        edge_data = config.get("General", "source_edge")
        baseGeo_data = config.get("General", "source_base")

        dataList.append(edge_data)
        dataList.append(baseGeo_data)

        return dataList


    def getAllBLS(self):
        all_bls_nodes = adbBLS.Blendshape.findAll()
        return all_bls_nodes

    def clearAB(self, input):
        if input == 'base':
            pm.textField(self.baseGeoInput, e=1, tx=None)
            self.edge = None
        else:
            pm.textField(self.targetGeoInput, e=1, tx=None)
            self.baseGeo = None


    def refreshBlsMenu(self):
        all_bls = self.getAllBLS()
        selectedBlsNode = mc.optionMenu(self.bls_node, q=1, v=1)
        pm.optionMenu(self.bls_node, e=1, dai=1)
        if all_bls != []:
            for node in all_bls:
                pm.menuItem(parent=self.bls_node, label="{}".format(node.bs_node))
            try:
                mc.optionMenu(self.bls_node, e=1, v=selectedBlsNode)
            except RuntimeError:
                pass
        else:
            pm.menuItem(parent=self.bls_node, label = 'None')


    def progressBarCalculation(self, maxValue = 500):
        gMainProgressBar = mel.eval('$tmp = $gMainProgressBar');
        mc.progressBar(gMainProgressBar,
                        edit=True,
                        beginProgress=True,
                        isInterruptable=True,
                        status='"Calculation ...',
                        maxValue=maxValue)

        for i in range(maxValue):
                if mc.progressBar(gMainProgressBar, query=True, isCancelled=True ) :
                        break
                mc.progressBar(gMainProgressBar, edit=True, step=1)
        mc.progressBar(gMainProgressBar, edit=True, endProgress=True)

        pm.textScrollList(self.outputWin, e=1, removeAll=True)
        pm.textScrollList(self.outputWin, e=1, append=['DONE!'])

#-----------------------------------
#  SLOTS
#-----------------------------------

    def test(self):
        print 'test'


    def addBlendshapeAB(self):
        adb.blendshape(pm.selected()[-1], pm.selected()[0:-1], origin="local")
        self.refreshBlsMenu()


    def addTargetAB(self):
        selectedBlsNode = mc.optionMenu(self.bls_node, q=1, v=1)
        bls = adbBLS.Blendshape(selectedBlsNode)
        bls.add_target(pm.selected())
        self.refreshBlsMenu()


    def mirrorBlsWeightsMapAB(self):
        if pm.radioButton(self.leftInput, q=1, sl=1):
            mirror_src = 'RIGHT'
        else:
            mirror_src = 'LEFT'
        mc.mirrorBlsWeights(ce=self.edge, s=mirror_src)

    def mirrorBlsTargetMapAB(self):
        if pm.radioButton(self.leftInput, q=1, sl=1):
            mirror_src = 'RIGHT'
        else:
            mirror_src = 'LEFT'
        mc.mirrorBlsMap(ce=self.edge, s=mirror_src)


    def load_symetry_data(self):
        if not pm.selected():
            self.targetGeo = pm.PyNode(str(self.edge).split('.e')[0]).getTransform()
        else:
            if str(type(pm.selected()[0])) == "<class 'pymel.core.general.MeshEdge'>":
                self.edge = str(pm.selected()[0])

        self.targetGeo = pm.PyNode(str(self.edge).split('.e')[0]).getTransform()

        try:
            self.symetry_data = adbTopo.getSymmetry(self.edge) or []
            if self.symetry_data:
                pm.iconTextButton(self.symetry_status, edit=1, i=ICONS_FOLDER+'green_status')
                pm.textField(self.targetGeoInput, edit=1, text=self.edge)
        except adbTopo.SymmetryError, e:
            pm.iconTextButton(self.symetry_status, edit=1, i=ICONS_FOLDER+'red_status')
            pm.warning('Topology is invalid')
        return self.symetry_data


    def select_center_edge(self):
        lf_verts, cn_verts, rt_verts = self.symetry_data
        vert_to_select = ['{}.vtx[{}]'.format(self.targetGeo, vert)  for vert in cn_verts]
        pm.select(vert_to_select, r=1)


    def select_left_edge(self):
        lf_verts, cn_verts, rt_verts = self.symetry_data
        vert_to_select = ['{}.vtx[{}]'.format(self.targetGeo, vert)  for vert in lf_verts]
        pm.select(vert_to_select, r=1)


    def select_right_edge(self):
        lf_verts, cn_verts, rt_verts = self.symetry_data
        vert_to_select = ['{}.vtx[{}]'.format(self.targetGeo, vert)  for vert in rt_verts]
        pm.select(vert_to_select, r=1)


    def addBaseGeo(self):
        self.baseGeo = pm.selected()[0]
        pm.textField(self.baseGeoInput, edit=1, text=self.baseGeo)


    def selectTargetMesh(self):
        pm.select(self.targetGeo, r=1)


    def selectBaseMesh(self):
        pm.select(pm.textField(self.baseGeoInput, q=1, text=1), r=1)


    def resetMeshAB(self):
        pm.textScrollList(self.outputWin, e=1, removeAll=True)
        pm.textScrollList(self.outputWin, e=1, append=['Calculation .  .  .'])
        axisInput = ''
        if pm.checkBox(self.inputXchbx, q=1, value=1):
            axisInput += 'x'

        if pm.checkBox(self.inputYchbx, q=1, value=1):
            axisInput += 'y'

        if pm.checkBox(self.inputZchbx, q=1, value=1):
            axisInput += 'z'

        percentageInput = pm.intSliderGrp(self.percentageSlider, q=1, value=1)
        percentageInput /= 100.0

        positiveInput = pm.radioButton(self.posInput, q=1, sl=1)

        if not pm.selected():
            mc.resetDelta(str(self.baseGeo), str(self.targetGeo), percentage=percentageInput, axis =axisInput, positive=positiveInput)
        else:
            sel_type = type(pm.selected()[0])
            if str(sel_type) == "<class 'pymel.core.general.MeshVertex'>":
                mc.resetDelta(str(self.baseGeo), percentage=percentageInput, axis =axisInput, positive=positiveInput)
            else:
                mc.resetDelta(str(self.baseGeo), str(self.targetGeo), percentage=percentageInput, axis =axisInput, positive=positiveInput)
        self.progressBarCalculation()


    def mirrorAB(self):
        pm.textScrollList(self.outputWin, e=1, removeAll=True)
        pm.textScrollList(self.outputWin, e=1, append=['Calculation .  .  . '])

        if pm.radioButton(self.leftInput, q=1, sl=1):
            mirror_src = 'RIGHT'
        else:
            mirror_src = 'LEFT'

        if not pm.selected():
            pm.select(self.targetGeo, r=1)
            mc.symmetrize(self.edge, side=mirror_src)
            pm.select(None)
        else:
            mc.symmetrize(self.edge, side=mirror_src)
        self.progressBarCalculation()


    def flipMeshAB(self):
        pm.textScrollList(self.outputWin, e=1, removeAll=True)
        pm.textScrollList(self.outputWin, e=1, append=['Calculation .  .  . '])

        mc.flip(self.edge)
        self.progressBarCalculation()


    def MatchSelection(self):
        currentSelection = mc.ls(sl=1, flatten=1)
        basemesh = currentSelection[0].split('.')[0]
        indexVtxList = [int(x.split('[')[-1].split(']')[0]) for x in currentSelection]
        pm.select(None)

        pm.select(None)
        for index in indexVtxList:
            pm.select('{}.vtx[{}]'.format(self.targetGeo, index), add=1)


    def selectMirrorVtxAB(self):
        pm.textScrollList(self.outputWin, e=1, removeAll=True)
        pm.textScrollList(self.outputWin, e=1, append=['Calculation .  .  . '])
        if pm.radioButton(self.leftInput, q=1, sl=1):
            mirror_src = 'RIGHT'
        else:
            mirror_src = 'LEFT'

        sel = mc.ls(sl=1, flatten=1)
        sel_string = [str(x) for x in sel]

        adbTopo.selectMirrorVtx(sel_string, self.edge, mirror_src)
        self.progressBarCalculation()


# ===============================
# BUILD WINDOW
# ===============================

def showUI():
    TopoTool()


# showUI()