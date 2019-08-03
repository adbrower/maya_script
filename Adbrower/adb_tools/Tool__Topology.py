# -------------------------------------------------------------------
# adb Module Toolbox    
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# -------------------------------------------------------------------

from pymel.core import *
import traceback
import pymel.core as pm
import maya.cmds as mc
import maya.OpenMaya as om
import maya.mel as mel


import sys, os
from functools import wraps

#-----------------------------------
#  CUSTOM IMPORT
#----------------------------------- 
from CollDict import colordic   
import adbrower
import adb_utils.adb_script_utils.Functions__topology as adbTopo
reload(adbTopo)

ICONS_FOLDER = 'C:/Users/Audrey/Google Drive/[SCRIPT]/python/Adbrower/adb_icons/'


#-----------------------------------
#  CLASS
#----------------------------------- 

class TopoTool():
    """This Tool makes a tilt fonction on any object  """

    def __init__(self, **kwargs): 
        self.name = 'Topology Tool'
        self.object = 'Topology_win'
        self.symetry_data = None
        self.geometry = None
        
        self.ui()
        
    def ui(self):  
        template = uiTemplate('ExampleTemplate', force = True )
        template.define( button, w=60, height = 25)
        template.define( frameLayout, borderVisible = False, labelVisible = False)
        
        if pm.window(self.object  , q=1, ex=1):
            pm.deleteUI(self.object )
        
        with window(self.object , t= self.name , s=True, tlb = True, mnb=True) as win:
            with template:  
                
                with columnLayout(adj=True, rs = 4):   
                    text('Utilites')
                    button(label="Delete History",  backgroundColor = colordic['grey1'])  
                    with rowLayout(adj=True, numberOfColumns=4):
                        separator(w=2, vis=0)
                        self.symetry_status = iconTextButton(h=20, w=20, i=ICONS_FOLDER+'red_status') 
                        # separator(w=90, vis=0)
                        button(label="Load Symetry Data", w=200,  backgroundColor = colordic['grey1'],  c = pm.Callback(self.load_symetry_data))  
                         
                        
                    with frameLayout( cll = True, bgc=[0.15, 0.15, 0.15], labelVisible=True , cl = False, label = " RESET"):  
                        with rowLayout( adj=True, numberOfColumns=2):
                            textField(pht='Base Geo', w=50)
                            button('<<<', w=40)

                        with rowLayout(numberOfColumns=4):
                            text('   RESET :    ')
                            checkBox(l='X', w=40, v=1) 
                            checkBox(l='Y', w=40, v=1) 
                            checkBox(l='Z', w=40, v=1) 
                            
                        with rowLayout(numberOfColumns=4):
                            separator(w=25, vis=0)
                            radioCollection()
                            radioButton(label="All",  sl=1)
                            radioButton(label="Pos",  sl=0)
                            radioButton(label="Neg",  sl=0, w=80)
                            
                        with columnLayout( adj=True, rs=4) :
                            intSliderGrp(field=True, minValue=0, maxValue=100, fieldMinValue=0, fieldMaxValue=100, value=0, cw2=(40, 100), ann="percentage of modification on your mesh")
                            button('Reset Mesh', w=40, backgroundColor = colordic['green3'])
                            
                    with frameLayout( cll = True, bgc=[0.15, 0.15, 0.15], labelVisible=True , cl = False, label = " SELECTION"):  

                        with rowLayout(adj=True, numberOfColumns=3):
                            button(label="Invert",  backgroundColor = colordic['grey1'], w=110, c = lambda *args: mel.eval('InvertSelection'))  
                            button(label="Mirror",  backgroundColor = colordic['grey1'], w=110,)  
                        
                        with rowLayout(adj=True, numberOfColumns=4):

                            button(label="L",  backgroundColor = colordic['grey1'], w=70, c= pm.Callback(self.select_left_edge))    
                            button(label="C",  backgroundColor = colordic['grey1'], w=70, c= pm.Callback(self.select_center_edge))  
                            button(label="R",  backgroundColor = colordic['grey1'], w=70, c= pm.Callback(self.select_right_edge))   

                        with rowLayout(adj=True, numberOfColumns=2):
                            button(label="Match",  backgroundColor = colordic['grey1']) 

                    with frameLayout( cll = True, bgc=[0.15, 0.15, 0.15], labelVisible=True , cl = False, label = " MODIFY"):  
                        text('MIRRORING',h=20)
                        with rowLayout( adj=True, numberOfColumns=3):
                            radioCollection()
                            radioButton(label="Left > Right" , sl=1)
                            radioButton(label="Right > Left", sl=0)
                        with columnLayout( adj=True, rs=4) :
                            button(label="Mirror",  backgroundColor = colordic['grey1']) 
                            separator(h=10)
                            button(label="Flip",  backgroundColor = colordic['grey1']) 
                            button(label="Match",  backgroundColor = colordic['grey1']) 
                                        



#-----------------------------------
#  SLOTS
#----------------------------------- 

    def load_symetry_data(self):
        self.edge = str(pm.selected()[0])
        self.geometry = pm.PyNode(str(self.edge).split('.e')[0]).getTransform()

        self.symetry_data = adbTopo.getSymmetry(self.edge) or []      
        if self.symetry_data:
            pm.iconTextButton(self.symetry_status, edit=1, i=ICONS_FOLDER+'green_status') 
        return self.symetry_data
        
    
    def select_center_edge(self):
        lf_verts, cn_verts, rt_verts = self.symetry_data
        vert_to_select = ['{}.vtx[{}]'.format(self.geometry, vert)  for vert in cn_verts]
        pm.select(vert_to_select, r =1)


    def select_left_edge(self):
        lf_verts, cn_verts, rt_verts = self.symetry_data
        vert_to_select = ['{}.vtx[{}]'.format(self.geometry, vert)  for vert in lf_verts]
        pm.select(vert_to_select, r =1)


    def select_right_edge(self):
        lf_verts, cn_verts, rt_verts = self.symetry_data
        vert_to_select = ['{}.vtx[{}]'.format(self.geometry, vert)  for vert in rt_verts]
        pm.select(vert_to_select, r =1)

        



TopoTool()
