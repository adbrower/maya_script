
# ------------------------------------------------------
# Rigging Toolbox
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------

#-----------------------------------
# IMPORT CUSTOM MODULES
#----------------------------------- 
import sys

import maya.cmds as mc
import pymel.core as pm
import ShapesLibrary as sl

import adbrower
from adbrower import changeColor, flatList, undo
from CollDict import colordic, suffixDic
## Import Tools
import adb_tools.Tool__adbModule as Tool__adbModule
import adb_tools.Tool__AutoRig as Tool__AutoRig
import adb_tools.Tool__CFX__PySide as Tool__adbCFX
import adb_tools.Tool__ConnectionTool
import adb_tools.Tool__CopyWeight_Skin as Tool__CopyWeight_Skin
import adb_tools.Tool__IKFK_Switch__PySide as Tool__IKFK_Switch__PySide
import adb_tools.Tool__Joint_Generator__Pyside
import adb_tools.Tool__Match_IkFK_PySide as Tool__Match_IkFK_PySide
import adb_tools.Tool__Tilt as Tool__Tilt
import adb_utils.Class__AddAttr as adbAttr
import adb_utils.Class__Transforms
import adb_utils.rig_utils.Class__ShapeManagement as adbShape
import arShake_v012
from skinWrangler_master import skinWrangler
from spaceSwitchTool import spaceSwitchSetup as switchSetup

adb = adbrower.Adbrower()

#-----------------------------------
#  DECORATORS
#----------------------------------- 

ICONS_FOLDER = 'C:/Users/Audrey/Google Drive/[SCRIPT]/python/Adbrower/adb_icons/'
imageColorLambert = ICONS_FOLDER+'ColorLambert.png'
imageColorGreen = ICONS_FOLDER+'ColorGreen.png'
imageColorRed = ICONS_FOLDER+'ColorRed.png'
imageColorBlue = ICONS_FOLDER+'ColorBlue.png'
imageColorYellow = ICONS_FOLDER+'ColorYellow.png'
imageColorDarkGrey = ICONS_FOLDER+'ColorDarkGRey.png'
imageMoins = ICONS_FOLDER+'Moins.png'
imagePlus = ICONS_FOLDER+'Plus.png'

#-----------------------------------
#  CLASS
#----------------------------------- 

class AudreyToolBox():
    def __init__(self,**kwargs):
        self.name = "toolbox_win"
        self.title = "adbrower_toolbox"
        self.version =  4.0
        self.ui()
        self.allgrey()    
        
    def ui(self):
        
        if pm.window(self.name, q=1, ex=1):
            pm.deleteUI(self.name)
            
        if pm.dockControl("toolbox_dockwin", q=1, ex=1):
            pm.deleteUI("toolbox_dockwin")

        mc.window(self.name, t=self.title, w = 200, s=True, tlb=True)
        mc.scrollLayout(horizontalScrollBarThickness=16,verticalScrollBarThickness=16)
        mc.columnLayout(adj=True)

## ------------ SECTION COMMANDES RAPIDES 


        pm.rowLayout()
        pm.button(command  = mc.DeleteHistory, w = 200, backgroundColor = colordic['grey'], label = "Delete History")
        pm.setParent('..')

        pm.rowLayout()
        pm.button(command  = mc.BakeNonDefHistory, w = 200, backgroundColor = colordic['grey'], label = "Delete Non Deformer History")
        pm.setParent('..')

        pm.rowLayout()
        pm.button(command  = lambda *args: pm.mel.hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes"), w = 200,  backgroundColor = colordic['grey'], label = "Delete Unused Nodes")
        pm.setParent('..')

         #### CHANNELS - VIEWPORT ###

        pm.text( label = "Channel and Viewport" , h=20)
        mc.columnLayout (adj=False)
        pm.setParent('..')
        pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=2)
        pm.button(l = "Selected Joints", h = 25, w = 99, backgroundColor = colordic['grey1'], command  = pm.Callback(self.switchDrawStyle))
        pm.button(l = "All Joints", h = 25, w = 99, backgroundColor = colordic['grey1'], command  = pm.Callback(self.switchDrawStyleAll))
        pm.setParent('..')

        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=2)
        pm.button (l = "Lock and Hide", h = 25, w = 99, backgroundColor = colordic['grey1'], command  = lambda * args: [pm.mel.channelBoxCommand('-lockUnkeyable') for x in pm.selected()])
        pm.button (l = "Unhide All", h = 25, w = 99, backgroundColor = colordic['grey1'], command  = lambda * args:adbAttr.unhideAll(pm.selected()))
        pm.setParent('..')

        pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=2)
        pm.button (l = "Lock", h = 25, w = 99, backgroundColor = colordic['grey1'], command  = pm.Callback(self.lock_unlockAB, 'lock') )
        pm.button (l = "Unlock", h = 25, w = 99, backgroundColor = colordic['grey1'], command  = pm.Callback(self.lock_unlockAB, 'unlock'))
        pm.setParent('..')

        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=4)
        pm.button(l = "Shift Up", h = 25, w = 65, backgroundColor = colordic['grey1'], command  = pm.Callback(self.shiftAtt,1))
        pm.button(l = "Shift Down", h = 25, w = 65, backgroundColor = colordic['grey1'], command  = pm.Callback(self.shiftAtt,0))
        pm.button(l = "Separator", h = 25, w = 65, backgroundColor = colordic['grey1'], command  = pm.Callback(self.addSeparator))
        pm.popupMenu()
        pm.menuItem(l=' Add Rotation Order', c =lambda * args: adbAttr.NodeAttr.addRotationOrderAttr(pm.selected()))      
        pm.menuItem(l=' Set preset Default Value', c = pm.Callback(self.set_AttDefault))

        pm.setParent('..')
        
        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=4)
        self.attr = pm.textField(w=115, pht = 'Select Target')
        pm.button(l = "<<<", h = 25, w = 40, backgroundColor = colordic['grey1'], command  = pm.Callback(self.addAttr))
        pm.button(l = "Copy", h = 25, w = 40, backgroundColor = colordic['grey1'], command  = pm.Callback(self.copyAttr))
        
        pm.setParent('..')
        pm.setParent('..')

        
## ------------ SECTION TOOLS ###
                                 
                                  
        pm.frameLayout(cll = True,w = 200, bgc=(.12, .12, .12), cl = False , label = "TOOLS")
        pm.columnLayout(adj=False) 
        
        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=2)        
        pm.button(l = "Select By ", backgroundColor = colordic['grey'], command = pm.Callback(self._selectBy))
        pm.popupMenu()
        pm.menuItem (l = "joint",  command  = lambda *args:adb.selectType('joint'))
        pm.menuItem (l = "nurbsCurve",   command  = lambda *args:adb.selectType('nurbsCurve'))  
        pm.menuItem (l = "mesh",   command  = lambda *args:adb.selectType('mesh'))  
        self.select_by = pm.textField(w = 138, tx = 'joint')
        pm.setParent('..') 

        pm.rowLayout(numberOfColumns=1)
        pm.button (l = "Joint GeneratorTool", h = 25, w = 199, backgroundColor = colordic['grey'], command = pm.Callback(self.jointGenToolAB))
        pm.setParent('..')       

        pm.rowLayout(numberOfColumns=1)
        pm.button (l = "Connection Tool", h = 25, w = 199, backgroundColor = colordic['grey'], command = pm.Callback(self.multiToolAB))
        pm.setParent('..') 

        self.tool_options = pm.optionMenu(w=200, cc = self.ToolAB)
        pm.menuItem(label = "- Choose Tool -")
        pm.menuItem(label = "adb Module")
        # pm.menuItem(label = "Check Up Tool")
        pm.menuItem(label = "Copy Weights Tool")
        pm.menuItem(label = "Tilt Tool")        
        pm.menuItem(label = "IK - FK Switch")
        pm.menuItem(label = "IK - FK Match")
        pm.menuItem(label = "CFX ToolBox")
        pm.menuItem(label = "Auto Rig Tool")
        pm.menuItem(divider = 1)
        pm.menuItem(label = "Skin Wrangler Tool") 
        pm.menuItem(label = "Shake Tool")
        pm.menuItem(label = "Space Switch Tool")
        
        pm.setParent('..')
        pm.setParent('..')
        pm.setParent('..')

                
## ------------ SECTION NAMING ###

        pm.frameLayout(cll = True,w = 200, bgc=(.12, .12, .12), cl = True , label = "NAMING")
        pm.columnLayout(adj= False)

        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=2)        
        pm.text(l = "Search       ")
        self.vold_name = pm.textField(w = 138, pht = 'Replace - Remove',)
        pm.setParent('..')
        
        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=2)        
        pm.text(l = "New Name ")
        self.vnew_name = pm.textField(w = 138, pht = 'Rename - Prefix - Suffix')
        pm.setParent('..')

        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=2)
        pm.button (l = "Rename", h = 25, w = 98, backgroundColor = colordic['darkred'], command  = pm.Callback(self.renaming))
        pm.button (l = "Replace", h = 25, w = 99, backgroundColor = colordic['darkred'], command  = pm.Callback(self.replace_Name))
        pm.setParent('..')
        
        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=2)
        pm.button (l = "Remove", h = 25, w = 98, backgroundColor = colordic['darkred'], command  = pm.Callback(self.removeName))
        pm.button (l = "Remove 'Pasted'", h = 25, w = 99, backgroundColor = colordic['darkred'], command  = pm.Callback(self.no_Pasted))   
        pm.setParent('..')     

        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=4)        
        pm.button (l = "Add Prefix", h = 25, w = 65, backgroundColor = colordic['darkred3'], command  = pm.Callback(self.add_Prefix), ann='popup menu available')   
        pm.popupMenu()
        pm.menuItem (l = "C_",  command  = pm.Callback(self.add_Prefix_predefined, 'C_'))
        pm.menuItem (l = "L_",   command  = pm.Callback(self.add_Prefix_predefined, 'L_'))  
        pm.menuItem (l = "R_",   command  = pm.Callback(self.add_Prefix_predefined, 'R_'))       
        pm.button (l = "Add Suffix", h = 25, w = 65, backgroundColor = colordic['darkred3'], command  = pm.Callback(self.add_Suffix), ann='popup menu available')
        pm.popupMenu()
        pm.menuItem (l = "_CTRL",  command  = pm.Callback(self.add_Suffix_predefined, '_CTRL'))
        pm.menuItem (l = "_GRP",   command  = pm.Callback(self.add_Suffix_predefined, '_GRP'))  
        pm.menuItem (l = "_JNT",   command  = pm.Callback(self.add_Suffix_predefined, '_JNT'))  
        
        pm.button (l = "Auto Suffix", h = 25, w = 65, backgroundColor = colordic['darkred3'], command  = lambda *args:adb.AutoSuffix(pm.selected()) )
        pm.setParent('..')             
        pm.setParent('..')
        pm.setParent('..')
        pm.setParent('..')


        ### SECTION CONNECTION ###

        pm.frameLayout(cll = True,w = 200, bgc=(.12, .12, .12), cl = True , label = "CONNECTIONS")
        pm.columnLayout(adj=False, rs = 5)        
        pm.text(l = "                  Conversion nodes" , h = 20, align = 'center')

        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=6)
        pm.iconTextButton(i="render_multiplyDivide.png", style="iconOnly", annotation="Multiply Divide", c = pm.Callback(self.addNodeMD), dcc = pm.Callback(self.addNodes,'multiplyDivide'), w = 38)
        pm.iconTextButton(i="render_reverse.png", style="iconOnly", annotation="Reverse Node", c = pm.Callback(self.addNodeRev), dcc = pm.Callback(self.addNodes,'reverse'), w = 38)
        pm.iconTextButton(i="render_remapValue.png", style="iconOnly", annotation="Remap Value", c = pm.Callback(self.addNodes,'remapValue'), dcc = pm.Callback(self.addNodes,'remapValue'), w = 38)
        pm.iconTextButton(i="render_plusMinusAverage.png", style="iconOnly", annotation="Plus Minus Average", c = pm.Callback(self.addNodes,'plusMinusAverage'), dcc = pm.Callback(self.addNodes,'plusMinusAverage'), w = 38)
        pm.iconTextButton(i="render_blendColors.png", style="iconOnly", annotation="Blend Colors", c = pm.Callback(self.addNodes,'blendColors'), dcc = pm.Callback(self.addNodes,'blendColors'), w = 38)
        pm.setParent('..')
        
        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=1)
        pm.button(l = "Print All Existing Connections", h = 25, w = 200, backgroundColor = colordic['grey'], c = pm.Callback(self.printAllConns))
        pm.setParent('..')
        
        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=4)
        pm.text( label=" Factor " , h=20, align='left')
        self.vfactor = pm.floatField(width=40, v = 1, precision=0)
        pm.text( label=" Operation " , h=20, align='left')
        self.voperation = pm.floatField(width=40, v = 1, precision=0)
        pm.setParent('..')


        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=6)
        # pm.checkBox("myChBxAll", l = "ALL", h= 25, w = 40)
        pm.text( label=" Connections index" , h=20, align='left')
        self.vindex = pm.floatField(width=40, v = 0, precision=0)

        pm.setParent('..')
        pm.optionMenu(w = 200)
        pm.menuItem(label = " - Operation Options - ")
        pm.menuItem(label = "0 - None")
        pm.menuItem(label = "1 - Multiply / Sum")
        pm.menuItem(label = "2 - Divide / Subtract")
        pm.menuItem(label = "3 - Power / Average")

        pm.setParent('..')
        pm.setParent('..')


## ------------ SECTION CONSTRAINTS ###

        pm.frameLayout(cll = True, w = 200, bgc=(.12, .12, .12), cl = False, label = "CONSTRAINTS")
        pm.columnLayout()

        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=5)
        pm.iconTextButton(l = "Point", i="posConstraint.png", style="iconAndTextVertical", command  = pm.Callback(self.pointconstraintbutton))
        pm.iconTextButton(l = "Orient", i="orientConstraint.png", style="iconAndTextVertical", command  = pm.Callback(self.orientconstraintbutton))
        pm.iconTextButton(l = "Scale", i="scaleConstraint.png", style="iconAndTextVertical", command  = pm.Callback(self.scaleconstraintbutton))
        pm.iconTextButton(l = "Aim", i="aimConstraint.png", style="iconAndTextVertical", command  = pm.Callback(self.aimconstraintbutton))
        pm.iconTextButton(l = "Parent", i="parentConstraint.png", style="iconAndTextVertical", command  = pm.Callback(self.parentconstraintbutton))
        pm.setParent('..')

        pm.button(command  = pm.Callback(self.parentscaleconstrain), l = "Parent + Scale Constraint",  h = 25,w = 200, backgroundColor = colordic['green3'])
        pm.separator(h=2)
        
        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=4)
        pm.checkBox("myChBx", l = "M. Offset", h= 25, value = 1)
        pm.checkBox("myChBx_matrix", l = "Matrix", h= 25)
        pm.checkBox("myChBx_invert", l = "Invert", h= 25)
        pm.setParent('..')        
        
        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=4)
        pm.checkBox("myChBx_pos", l = "Pos", h= 25, value = 1)
        pm.checkBox("myChBx_rot", l = "Rot", h= 25, value = 1)
        pm.button(command  = pm.Callback(self.MatchTransformRT), l = "Match Transform  ", h = 25, w=120, backgroundColor = colordic['green3'])
        pm.setParent('..')
        
        pm.separator(h=3)
        pm.button(l = "Match Pivot Point", h = 25, w = 200, backgroundColor = colordic['green3'], command  =  lambda *args : adb.changePivotPoint(pm.selected()[0], pm.selected()[1])  )
        pm.separator(h=3)
        pm.button(l = "Remove all Constraints From Selection", h = 25, w = 200, backgroundColor = colordic['grey1'], command  = pm.Callback(self.rmvConstraint))
        pm.setParent('..')
        pm.setParent('..')


## ------------ GROUP, PARENT AND LOC ###


        pm.frameLayout(cll = True,w = 200, bgc=(.12, .12, .12), cl = False, label = "GROUP, PARENT AND LOC")
        mc.columnLayout(rs=1)        
        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=4)
        pm.iconTextButton(l = "Locator", i="locator.png", style="iconAndTextVertical",  command  = pm.Callback(self.createloc), ann='popup meunu available')
        pm.popupMenu()
        pm.menuItem(l=' Create Locator Center Geo', c = pm.Callback(self.createlocCC))
        
        pm.iconTextButton(l = "   Chain Parent",    i="parent.png", style="iconAndTextVertical",  command  = pm.Callback(self.chparent), ann='popup meunu available')
        pm.popupMenu()
        pm.menuItem(l=' Parent to the World', c =lambda *args: [pm.parent(x, w=1)for x in pm.selected()], ann = 'dcc : Parent to the world')
    
        pm.iconTextButton(l = "   Select Children", i="aselect.png", style="iconAndTextVertical", command  = pm.Callback(self.selectchildparent))
        pm.setParent('..')

        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=4)        
        pm.iconTextButton(l = "R. Hiearchy", i='outliner.png', style='iconAndTextVertical',   command  = lambda * args: [pm.reorder(x, back=True) for x in pm.selected()])
        pm.popupMenu() 
        pm.menuItem(l='Hiearchy Builder', c = lambda * args:adb.hiearchyBuilder(pm.selected(),'ctrl'))
        
        pm.iconTextButton(l = "     Material",  style='iconAndTextVertical', i= imageColorLambert, c =  lambda*args:mc.hyperShade( assign= "lambert1" ), ann='popup meunu available')  
        pm.popupMenu()
        mc.menuItem(image= imageColorLambert, l="Lambert",  c =  lambda*args:mc.hyperShade( assign= "lambert1" ))
        mc.menuItem(image= imageColorYellow, l="Yellow",  c = pm.Callback(self.add_material,'mat_yellow'))
        mc.menuItem(image= imageColorBlue, l="Blue",  c = pm.Callback(self.add_material,'mat_bleu'))
        mc.menuItem(image= imageColorRed, l="Red",  c = pm.Callback(self.add_material,'mat_red'))      
        mc.menuItem(image= imageColorGreen, l="Green",  c = pm.Callback(self.add_material,'mat_green'))      
        mc.menuItem(image= imageColorDarkGrey, l="Dark Grey",  c = pm.Callback(self.add_material,'mat_darkGrey'))  
        
        pm.iconTextButton(l = "     Make Root",  style='iconAndTextVertical', i = 'selectByHierarchy.png', command  = pm.Callback(self.makeroot), ann='popup meunu available')
        pm.popupMenu()
        pm.menuItem(l=' Delete grp', c =lambda * args: [pm.ungroup(x) for x in pm.selected()])
        pm.menuItem(l=' Group Null', i="group.png",  command  = lambda * args: [pm.group(x, em=True, n = "{}__grp__".format(x)) for x in pm.selected()])
        
        pm.setParent('..')

        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=2)
        pm.text('Offset Group Name:' )
        self.mroot = pm.textField(w = 99, tx = 'root')        
        pm.setParent('..')

        pm.setParent('..')
        pm.setParent('..')
        

## ------------ SECTION CONTROLS ###


        def createctrl(shape): 
            '''
            Creates a new controler or change controler shape
            '''
            
            if shape == "Cube" and mc.checkBox("myChBx3", q =True, v=True,) == 0 and mc.checkBox(ChBx4, q =True, v=True,) == 0:
                
                adb.makeCtrl(sl.cube_shape)
                
            elif shape == "Cube" and mc.checkBox("myChBx3", q =True, v=True,) == 1:  
                
                try:                
                    self.shape_replacement(sl.cube_shape)
                
                except IndexError:
                    print ("// Warning: Nothing Selected! //") 
                    pm.delete(pm.selected())

            elif shape == "Cube" and mc.checkBox(ChBx4, q =True, v=True,) == 1:
                adb.makeCtrl_Prop(sl.cube_shape)

#====================================

            elif shape == "Square" and mc.checkBox("myChBx3", q =True, v=True,) == 0 and mc.checkBox(ChBx4, q =True, v=True,) == 0:
            
                sl.square_prop_shape()
                
            elif shape == "Square" and mc.checkBox("myChBx3", q =True, v=True,) == 1:  
                
                try:                
                    self.shape_replacement(sl.square_shape)
                
                except IndexError:
                    print ("// Warning: Nothing Selected! //") 
                    pm.delete(pm.selected())

            elif shape == "Square" and mc.checkBox(ChBx4, q =True, v=True,) == 1:
                sl.square_prop_shape()


#====================================


            elif shape == "Circle" and mc.checkBox("myChBx3", q =True, v=True,) == 0 and mc.checkBox(ChBx4, q =True, v=True,) == 0:
                if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                    adb.makeCtrl(sl.circleX_shape)
                elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                    adb.makeCtrl(sl.circleY_shape)
                elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:
                    adb.makeCtrl(sl.circleZ_shape)
                            
            elif shape == "Circle" and mc.checkBox("myChBx3", q =True, v=True,) == 1:                  
                try:                
                    if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                        self.shape_replacement(sl.circleX_shape)
                    elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                        self.shape_replacement(sl.circleY_shape)
                    elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:
                        self.shape_replacement(sl.circleZ_shape)
                
                except IndexError:
                    print ("// Warning: Nothing Selected! //") 
                    pm.delete(pm.selected())

            elif shape == "Circle X" and mc.checkBox(ChBx4, q =True, v=True,) == 1:
                if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                    adb.makeCtrl_Prop(sl.circleX_shape)
                elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                    adb.makeCtrl_Prop(sl.circleY_shape)
                elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:
                    adb.makeCtrl_Prop(sl.circleZ_shape)
            
                
#====================================


            elif shape == "Ball" and mc.checkBox("myChBx3", q =True, v=True,) == 0 and mc.checkBox(ChBx4, q =True, v=True,) == 0:
            
                adb.makeCtrl(sl.ball2_shape)

            elif shape == "Ball" and mc.checkBox("myChBx3", q =True, v=True,) == 1:  
                
                try:                
                    self.shape_replacement(sl.ball2_shape)
                
                except IndexError:
                    print ("// Warning: Nothing Selected! //") 
                    pm.delete(pm.selected())

            elif shape == "Ball" and mc.checkBox(ChBx4, q =True, v=True,) == 1:
                adb.makeCtrl_Prop(sl.ball2_shape)

#====================================


            elif shape == "Diamond" and mc.checkBox("myChBx3", q =True, v=True,) == 0 and mc.checkBox(ChBx4, q =True, v=True,) == 0:  

                adb.makeCtrl(sl.diamond_shape)
               
            elif shape == "Diamond" and mc.checkBox("myChBx3", q =True, v=True,) == 1:  
                
                try:                
                    self.shape_replacement(sl.diamond_shape)
                
                except IndexError:
                    print ("// Warning: Nothing Selected! //") 
                    pm.delete(pm.selected())

            elif shape == "Diamond" and mc.checkBox(ChBx4, q =True, v=True,) == 1:
                adb.makeCtrl_Prop(sl.diamond_shape)

#====================================

            elif shape == "Main" and mc.checkBox("myChBx3", q =True, v=True,) == 0 and mc.checkBox(ChBx4, q =True, v=True,) == 0: 
                
                adb.makeCtrl(sl.main_shape)

            elif shape == "Main" and mc.checkBox("myChBx3", q =True, v=True,) == 1:  
                
                try:                
                    self.shape_replacement(sl.main_shape)
                                    
                except IndexError:
                    print ("// Warning: Nothing Selected! //") 
                    pm.delete(pm.selected())

            elif shape == "Main" and mc.checkBox(ChBx4, q =True, v=True,) == 1:
                adb.makeCtrl_Prop(sl.main_shape)                             

#====================================


            elif shape == "Fleches" and mc.checkBox("myChBx3", q =True, v=True,) == 0 and mc.checkBox(ChBx4, q =True, v=True,) == 0: 
            
                adb.makeCtrl(sl.fleches_shape)                                         

            elif shape == "Fleches" and mc.checkBox("myChBx3", q =True, v=True,) == 1:  
                
                try:                
                    self.shape_replacement(sl.fleches_shape)
                                    
                except IndexError:
                    print ("// Warning: Nothing Selected! //") 
                    pm.delete(pm.selected())

            elif shape == "Fleches" and mc.checkBox(ChBx4, q =True, v=True,) == 1:
                adb.makeCtrl_Prop(sl.fleches_shape)  
                

#====================================


            elif shape == "Arrow" and mc.checkBox("myChBx3", q =True, v=True,) == 0 and mc.checkBox(ChBx4, q =True, v=True,) == 0:                 
                if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                    adb.makeCtrl(sl.Xarrow_shape)
                elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                    adb.makeCtrl(sl.Yarrow_shape)
                elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:
                    adb.makeCtrl(sl.Zarrow_shape)          
            
            elif shape == "Arrow" and mc.checkBox("myChBx3", q =True, v=True,) == 1:                  
                try:                
                    if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                        self.shape_replacement(sl.Xarrow_shape)
                    elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                        self.shape_replacement(sl.Yarrow_shape)
                    elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:
                        self.shape_replacement(sl.Zarrow_shape)
                                    
                except IndexError:
                    print ("// Warning: Nothing Selected! //") 
                    pm.delete(pm.selected())

            elif shape == "Arrow" and mc.checkBox(ChBx4, q =True, v=True,) == 1:
                if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                    adb.makeCtrl_Prop(sl.Xarrow_shape)
                elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                    adb.makeCtrl_Prop(sl.Yarrow_shape)
                elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:
                    adb.makeCtrl_Prop(sl.Zarrow_shape)
                            

#====================================


            elif shape == "Double_fleches_ctrl" and mc.checkBox("myChBx3", q =True, v=True,) == 0 and mc.checkBox(ChBx4, q =True, v=True,) == 0: 
                
                adb.makeCtrl(sl.double_fleches_shape)
 
            elif shape == "Double_fleches_ctrl" and mc.checkBox("myChBx3", q =True, v=True,) == 1:  
                
                try:                
                    self.shape_replacement(sl.double_fleches_shape)
                                    
                except IndexError:
                    print ("// Warning: Nothing Selected! //") 
                    pm.delete(pm.selected())

            elif shape == "Double_fleches_ctrl" and mc.checkBox(ChBx4, q =True, v=True,) == 1:
                adb.makeCtrl_Prop(sl.double_fleches_shape)

#====================================


            elif shape == "Arc_fleches_ctrl" and mc.checkBox("myChBx3", q =True, v=True,) == 0 and mc.checkBox(ChBx4, q =True, v=True,) == 0: 
                
                adb.makeCtrl(sl.arc_fleches_shape)

            elif shape == "Arc_fleches_ctrl" and mc.checkBox("myChBx3", q =True, v=True,) == 1:  
                
                try:                
                    self.shape_replacement(sl.arc_fleches_shape)
                
                except IndexError:
                    print ("// Warning: Nothing Selected! //") 
                    pm.delete(pm.selected())

            elif shape == "Arc_fleches_ctrl" and mc.checkBox(ChBx4, q =True, v=True,) == 1:
                adb.makeCtrl_Prop(sl.arc_fleches_shape)

#====================================


            elif shape == "Locator_shape" and mc.checkBox("myChBx3", q =True, v=True,) == 0 and mc.checkBox(ChBx4, q =True, v=True,) == 0: 
                
               adb.makeCtrl(sl.locator_shape)

            elif shape == "Locator_shape" and mc.checkBox("myChBx3", q =True, v=True,) == 1:  
                
                try:                
                    self.shape_replacement(sl.locator_shape)
                                    
                except IndexError:
                    print ("// Warning: Nothing Selected! //") 
                    pm.delete(pm.selected())

            elif shape == "Locator_shape" and mc.checkBox(ChBx4, q =True, v=True,) == 1:
                adb.makeCtrl_Prop(sl.locator_shape)

#=====================================
            
            
            elif shape == "Double_Pin" and mc.checkBox("myChBx3", q =True, v=True,) == 0 and mc.checkBox(ChBx4, q =True, v=True,) == 0: 
                
                if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                    _ctrl = flatList(adb.makeCtrl(sl.double_pin_shape))[0]
                    pm.PyNode(_ctrl).ry.set(90)
                    pm.select(_ctrl, r =True)
                    mc.FreezeTransformations()
                elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                    _ctrl = flatList(adb.makeCtrl(sl.double_pin_shape))[0]
                    pm.PyNode(_ctrl).rx.set(90)
                    pm.select(_ctrl, r =True)
                    mc.FreezeTransformations()
                elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:
                    adb.makeCtrl(sl.double_pin_shape) 

            elif shape == "Double_Pin" and mc.checkBox("myChBx3", q =True, v=True,) == 1:  
                
                try:                
                    if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                        for each in pm.selected():
                            pm.select(each, r =True)
                            _ctrl = self.shape_replacement(sl.double_pin_shape)[0]
                            _shapes = pm.PyNode(_ctrl).getShapes()
                            pm.select('{}.cv[:]'.format(_shapes[0]))
                            pm.rotate( 90, 0, 0)
                            pm.select(None)
                        
                    elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                        for each in pm.selected():
                            pm.select(each, r =True)                        
                            _ctrl = self.shape_replacement(sl.double_pin_shape)[0]

                    elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:
                        for each in pm.selected():
                            pm.select(each, r =True)
                            _ctrl = self.shape_replacement(sl.double_pin_shape)[0]
                            _shapes = pm.PyNode(_ctrl).getShapes()
                            pm.select('{}.cv[:]'.format(_shapes[0]))
                            pm.rotate( 0, 90, 0)
                            pm.select(None)
                                    
                except IndexError:
                    print ("// Warning: Nothing Selected! //") 
                    pm.delete(pm.selected())

            elif shape == "Double_Pin" and mc.checkBox(ChBx4, q =True, v=True,) == 1:
                if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                    _ctrl = adb.makeCtrl_Prop(sl.double_pin_shape)[0]
                    pm.PyNode(_ctrl).ry.set(90)
                    pm.select(_ctrl, r =True)
                    mc.FreezeTransformations()
                elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                    _ctrl = adb.makeCtrl_Prop(sl.double_pin_shape)[0]
                    pm.PyNode(_ctrl).rx.set(90)
                    pm.select(_ctrl, r =True)
                    mc.FreezeTransformations()
                elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:
                    adb.makeCtrl_Prop(sl.double_pin_shape)


#=====================================
            
            
            elif shape == "Pin" and mc.checkBox("myChBx3", q =True, v=True,) == 0 and mc.checkBox(ChBx4, q =True, v=True,) == 0: 
                
                if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                    _ctrl = flatList(adb.makeCtrl(sl.pin_shape))[0]
                    pm.PyNode(_ctrl).rz.set(-90)
                    pm.select(_ctrl, r =True)
                    mc.FreezeTransformations()
                elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                    _ctrl = flatList(adb.makeCtrl(sl.pin_shape))

                elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:                    
                    _ctrl = flatList(adb.makeCtrl(sl.pin_shape))[0]
                    pm.PyNode(_ctrl).rx.set(-90)
                    pm.select(_ctrl, r =True)
                    mc.FreezeTransformations()

            elif shape == "Pin" and mc.checkBox("myChBx3", q =True, v=True,) == 1:  
                
                try:                
                    if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                        for each in pm.selected():
                            pm.select(each, r =True)
                            _ctrl = self.shape_replacement(sl.pin_shape)[0]
                            _shapes = pm.PyNode(_ctrl).getShapes()
                            pm.select('{}.cv[:]'.format(_shapes[0]))
                            pm.rotate( 90, 0, 0)
                            pm.select(None)
                        
                    elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                        for each in pm.selected():
                            pm.select(each, r =True)                        
                            _ctrl = self.shape_replacement(sl.pin_shape)[0]

                    elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:
                        for each in pm.selected():
                            pm.select(each, r =True)
                            _ctrl = self.shape_replacement(sl.pin_shape)[0]
                            _shapes = pm.PyNode(_ctrl).getShapes()
                            pm.select('{}.cv[:]'.format(_shapes[0]))
                            pm.rotate( 0, 90, 0)
                            pm.select(None)
                                    
                except IndexError:
                    print ("// Warning: Nothing Selected! //") 
                    pm.delete(pm.selected())

            elif shape == "Pin" and mc.checkBox(ChBx4, q =True, v=True,) == 1:
                if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                    _ctrl = adb.makeCtrl_Prop(sl.pin_shape)[0]
                    pm.PyNode(_ctrl).rz.set(-90)
                    pm.select(_ctrl, r =True)
                    mc.FreezeTransformations()
                elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                    adb.makeCtrl_Prop(sl.pin_shape)

                elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:
                    _ctrl = adb.makeCtrl_Prop(sl.pin_shape)[0]
                    pm.PyNode(_ctrl).rx.set(-90)
                    pm.select(_ctrl, r =True)
                    mc.FreezeTransformations()


#==================================== 


            elif shape == "Circle_Cross" and mc.checkBox("myChBx3", q =True, v=True,) == 0 and mc.checkBox(ChBx4, q =True, v=True,) == 0: 
                
                adb.makeCtrl(sl.circleCross_shape)

            elif shape == "Circle_Cross" and mc.checkBox("myChBx3", q =True, v=True,) == 1:  
                                
                try:                
                    self.shape_replacement(sl.circleCross_shape)
                                    
                except IndexError:
                    print ("// Warning: Nothing Selected! //") 
                    pm.delete(pm.selected())

            elif shape == "Circle_Cross" and mc.checkBox(ChBx4, q =True, v=True,) == 1:
                adb.makeCtrl_Prop(sl.circleCross_shape)

#====================================


            elif shape == "Cog" and mc.checkBox("myChBx3", q =True, v=True,) == 0 and mc.checkBox(ChBx4, q =True, v=True,) == 0: 
                
                adb.makeCtrl(sl.cog_shape)

            elif shape == "Cog" and mc.checkBox("myChBx3", q =True, v=True,) == 1:  
                
                try:                
                    self.shape_replacement(sl.cog_shape)
                                    
                except IndexError:
                    print ("// Warning: Nothing Selected! //") 
                    pm.delete(pm.selected())

            elif shape == "Cog" and mc.checkBox(ChBx4, q =True, v=True,) == 1:
                adb.makeCtrl_Prop(sl.cog_shape)


#====================================


            elif shape == "Cylinder" and mc.checkBox("myChBx3", q =True, v=True,) == 0 and mc.checkBox(ChBx4, q =True, v=True,) == 0:   
                      
                if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                    flatList(adb.makeCtrl(sl.cylinder_shape))
                elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                    _ctrl = flatList(adb.makeCtrl(sl.cylinder_shape))[0]
                    pm.PyNode(_ctrl).rz.set(-90)
                    pm.select(_ctrl, r =True)
                    mc.FreezeTransformations()
                elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:                    
                    _ctrl = flatList(adb.makeCtrl(sl.cylinder_shape))[0]
                    pm.PyNode(_ctrl).ry.set(-90)
                    pm.select(_ctrl, r =True)
                    mc.FreezeTransformations()

            elif shape == "Cylinder" and mc.checkBox("myChBx3", q =True, v=True,) == 1:  
                
                try:                
                    if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                         self.shape_replacement(sl.cylinder_shape)

                    elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                        _ctrl = self.shape_replacement(sl.cylinder_shape)[0]
                        pm.PyNode(_ctrl).rz.set(-90)
                        mc.FreezeTransformations()

                    elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:
                        _ctrl = self.shape_replacement(sl.cylinder_shape)[0]
                        pm.PyNode(_ctrl).ry.set(-90)
                        mc.FreezeTransformations()
                                    
                except IndexError:
                    print ("// Warning: Nothing Selected! //") 
                    pm.delete(pm.selected())

            elif shape == "Cylinder" and mc.checkBox(ChBx4, q =True, v=True,) == 1:
                if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                    _ctrl = adb.makeCtrl_Prop(sl.cylinder_shape)
                elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                    _ctrl = adb.makeCtrl_Prop(sl.cylinder_shape)[0]
                    pm.PyNode(_ctrl).rz.set(-90)
                    mc.FreezeTransformations()

                elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:
                    _ctrl = adb.makeCtrl_Prop(sl.cylinder_shape)[0]
                    pm.PyNode(_ctrl).ry.set(-90)
                    mc.FreezeTransformations()


        ##choisir la forme des ctrl####    
        
        pm.frameLayout(cll = True, w = 200, bgc=(.12, .12, .12), cl = True, label = "CONTROLS")
        pm.rowLayout(numberOfColumns=4)
        pm.checkBox("myChBx3", l = "Replace Shape", h = 20)
        pm.checkBox('myChBxX', l = "X", h = 20, v = True, cc = pm.Callback(self.cCommand_axis,'x'))
        pm.checkBox('myChBxY', l = "Y", h = 20, cc = pm.Callback(self.cCommand_axis,'y'))
        pm.checkBox('myChBxZ',  l = "Z", h = 20, cc = pm.Callback(self.cCommand_axis,'z'))
        pm.setParent('..')
        
        ChBx4 = pm.checkBox(l="Proportional Scale")

        pm.optionMenu(cc=createctrl)
        pm.menuItem( "- Choose Shape -")
        pm.menuItem(label = "Circle")
        pm.menuItem(label = "Square")
        pm.menuItem(label = "Cube")
        pm.menuItem(label = "Ball")
        pm.menuItem(label = "Diamond")              
        pm.menuItem(label = "Double_Pin")
        pm.menuItem(label = "Pin")
        pm.menuItem(label = "Cylinder")
        pm.menuItem(label = "Circle_Cross")
        pm.menuItem(label = "Cog")   
        pm.menuItem(label = "Arrow")
        pm.menuItem(label = "Main")                   
        pm.menuItem(label = "Double_fleches_ctrl")
        pm.menuItem(label = "Arc_fleches_ctrl")
        pm.menuItem(label = "Fleches") 
        pm.menuItem(label = "Locator_shape")
        
        pm.formLayout()
        tabs = pm.tabLayout('indexRGBTab',innerMarginWidth=5, innerMarginHeight=5)
                                               
        child1 =pm.rowColumnLayout(numberOfColumns=2)

        '''Index'''

        pm.gridLayout(numberOfColumns=6, cellWidthHeight=(33, 20))
       
        pm.iconTextButton(bgc=(.000, .000, .000), command= pm.Callback(self.shapeColor,1), dcc = pm.Callback(self.SelectBy,1,".overrideColor"))
        pm.iconTextButton(bgc=(.247, .247, .247), command= pm.Callback(self.shapeColor,2), dcc = pm.Callback(self.SelectBy,2,".overrideColor"))
        pm.iconTextButton(bgc=(.498, .498, .498), command= pm.Callback(self.shapeColor,3), dcc = pm.Callback(self.SelectBy,3,".overrideColor"))
        pm.iconTextButton(bgc=(0.608, 0, 0.157), command= pm.Callback(self.shapeColor,4), dcc = pm.Callback(self.SelectBy,4,".overrideColor")) 
        pm.iconTextButton( bgc=(0, 0.016, 0.373), command= pm.Callback(self.shapeColor,5), dcc = pm.Callback(self.SelectBy,5,".overrideColor"))        
        pm.iconTextButton(bgc=(0, 0, 1), command= pm.Callback(self.shapeColor,6), dcc = pm.Callback(self.SelectBy,6,".overrideColor"))

        pm.iconTextButton(bgc=(0, 0.275, 0.094), command= pm.Callback(self.shapeColor,7), dcc = pm.Callback(self.SelectBy,7,".overrideColor"))
        pm.iconTextButton(bgc=(0.145, 0, 0.263), command= pm.Callback(self.shapeColor,8), dcc = pm.Callback(self.SelectBy,8,".overrideColor")) #
        pm.iconTextButton(bgc=(0.78, 0, 0.78), command= pm.Callback(self.shapeColor,9), dcc = pm.Callback(self.SelectBy,9,".overrideColor"))
        pm.iconTextButton(bgc=(0.537, 0.278, 0.2), command= pm.Callback(self.shapeColor,10), dcc = pm.Callback(self.SelectBy,10,".overrideColor"))    
        pm.iconTextButton(bgc=(0.243, 0.133, 0.122), command= pm.Callback(self.shapeColor,11), dcc = pm.Callback(self.SelectBy,11,".overrideColor"))        
        pm.iconTextButton(bgc=(0.6, 0.145, 0), command= pm.Callback(self.shapeColor,12), dcc = pm.Callback(self.SelectBy,12,".overrideColor")) #          

        pm.iconTextButton(bgc=(1, 0, 0), command= pm.Callback(self.shapeColor,13), dcc = pm.Callback(self.SelectBy,13,".overrideColor"))  
        pm.iconTextButton(bgc=(0, 1, 0), command= pm.Callback(self.shapeColor,14), dcc = pm.Callback(self.SelectBy,14,".overrideColor"))        
        pm.iconTextButton(bgc=(0, 0.255, 0.6), command= pm.Callback(self.shapeColor,15), dcc = pm.Callback(self.SelectBy,15,".overrideColor")) #
        pm.iconTextButton(bgc=(1, 1, 1), command= pm.Callback(self.shapeColor,16), dcc = pm.Callback(self.SelectBy,16,".overrideColor")) #   
        pm.iconTextButton(bgc=(1, 1, 0), command= pm.Callback(self.shapeColor,17), dcc = pm.Callback(self.SelectBy,17,".overrideColor"))  
        pm.iconTextButton(bgc=(0.388, 0.863, 1), command= pm.Callback(self.shapeColor,18), dcc = pm.Callback(self.SelectBy,18,".overrideColor"))

        pm.iconTextButton(bgc=(0.263, 1, 0.635), command= pm.Callback(self.shapeColor,19), dcc = pm.Callback(self.SelectBy,19,".overrideColor")) #         
        pm.iconTextButton(bgc=(1, 0.686, 0.686), command= pm.Callback(self.shapeColor,20), dcc = pm.Callback(self.SelectBy,20,".overrideColor"))
        pm.iconTextButton(bgc=(0.89, 0.675, 0.475), command= pm.Callback(self.shapeColor,21), dcc = pm.Callback(self.SelectBy,21,".overrideColor"))
        pm.iconTextButton(bgc=(1, 1, 0.384), command= pm.Callback(self.shapeColor,22), dcc = pm.Callback(self.SelectBy,22,".overrideColor"))            
        pm.iconTextButton(bgc=(0, 0.6, 0.325), command= pm.Callback(self.shapeColor,23), dcc = pm.Callback(self.SelectBy,23,".overrideColor"))
        pm.iconTextButton(bgc=(0.627, 0.412, 0.188), command= pm.Callback(self.shapeColor,24), dcc = pm.Callback(self.SelectBy,24,".overrideColor")) #  

        pm.iconTextButton(bgc=(0.62, 0.627, 0.188), command= pm.Callback(self.shapeColor,25), dcc = pm.Callback(self.SelectBy,25,".overrideColor"))        
        pm.iconTextButton(bgc=(0.408, 0.627, 0.188), command= pm.Callback(self.shapeColor,26), dcc = pm.Callback(self.SelectBy,26,".overrideColor")) #        
        pm.iconTextButton(bgc=(0.188, 0.627, 0.365), command= pm.Callback(self.shapeColor,27), dcc = pm.Callback(self.SelectBy,27,".overrideColor")) #  
        pm.iconTextButton(bgc=(0.188, 0.627, 0.627), command= pm.Callback(self.shapeColor,28), dcc = pm.Callback(self.SelectBy,28,".overrideColor"))
        pm.iconTextButton(bgc=(0.188, 0.404, 0.627), command= pm.Callback(self.shapeColor,29), dcc = pm.Callback(self.SelectBy,29,".overrideColor"))
        pm.iconTextButton(bgc=(0.435, 0.188, 0.627), command= pm.Callback(self.shapeColor,30), dcc = pm.Callback(self.SelectBy,30,".overrideColor"))

        pm.iconTextButton(bgc=(0.507, 0.041, 0.277), command= pm.Callback(self.shapeColor,31), dcc = pm.Callback(self.SelectBy,31,".overrideColor"))       
        pm.iconTextButton(style="iconAndTextHorizontal", bgc=(.498, .498, .498), label="T", command  = pm.Callback(self.makeTemplate,1),dcc = pm.Callback(self.makeLayer,1) )
        pm.iconTextButton(style="iconAndTextHorizontal", bgc=(0, 0, 0),  label="R", command  = pm.Callback(self.makeTemplate,2), dcc = pm.Callback(self.makeLayer,2) )
        pm.iconTextButton(style="iconAndTextHorizontal", bgc=colordic['lightgreen'],  label="N", command  = pm.Callback(self.makeTemplate,0), dcc = pm.Callback(self.makeLayer,0))
                 
        pm.setParent('..')
        pm.setParent('..')


        ''' RGB '''        
        
        child2 = pm.columnLayout() 
        pm.colorInputWidgetGrp('RGB', label='Color', rgb=(1, 0, 0), cw3=(0, 30, 162))
        
        pm.rowLayout(numberOfColumns=2)
        pm.separator(w=50, vis=False)
        pm.button(l='Custom Palette', w =100, backgroundColor = colordic['grey'], c = pm.Callback(self.uiColor) )

        pm.setParent('..')
        pm.setParent('..')
        pm.setParent('..')
        pm.setParent('..')

        mc.tabLayout( tabs, edit=True, tabLabel=((child1, 'Index'), (child2, 'RGB')) )
       
        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=2)
        pm.setParent('..')
        pm.palettePort( 'scenePalette', dim=(10, 1), h =20, ced= True, r= True, scc = 0, cc = self.cCommand)

        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=2)
        pm.button(l = "Default color", w =99, backgroundColor = colordic['greenish'], command  = pm.Callback(self.colordefault))
        pm.button(l = "Set RGB Color", w =99, backgroundColor = colordic['greenish'], command  =pm.Callback( self.colorRGB))      
        pm.setParent('..')
                
        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=4)
        pm.iconTextButton(label="Reduce", w=70, h=20, i=imageMoins,  backgroundColor = colordic['greenish'], c =pm.Callback(self.ScaleVertex,'-')) 
        pm.text(label='      Size:       ')
        pm.iconTextButton(label="Increase", w=70, h=20, i=imagePlus,  backgroundColor = colordic['greenish'], c = pm.Callback(self.ScaleVertex,'+'))   
        pm.setParent('..')
        
        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=4)
        pm.button(label="Rotate X",  w=65, backgroundColor = colordic['greenish'], c =pm.Callback(self.RotateVertex,'x')) 
        pm.button(label="Rotate Y",  w=65, backgroundColor = colordic['greenish'], c = pm.Callback(self.RotateVertex,'y'))   
        pm.button(label="Rotate Z",  w=65, backgroundColor = colordic['greenish'], c = pm.Callback(self.RotateVertex,'z'))   
        pm.setParent('..')

        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=2)
        pm.button(label="Freeze CVs",  w=99, backgroundColor = colordic['greenish'], c = lambda*args:adb.freezeCvs(pm.selected())) 
        pm.button(label="Reset CVs",  w=99, backgroundColor = colordic['greenish'], c = lambda*args:adb.resetCvs(pm.selected()))   
        pm.setParent('..')

        pm.setParent('..')
        

        

## ------------ SECTION JOINTS ###        
        
        def jointOrient(options):
            if options == "X" :  
                oCollJoints = pm.selected()
                pm.joint(zso=1, ch=1, e=1, oj='xyz', secondaryAxisOrient='xup')
                pm.select(cl=True)

                #Orient the last joint to the world#
                selLastJnt = pm.select(oCollJoints[-1])
                pm.joint(e=1, oj='none') 
                pm.select(None)      

            elif options == "Y" : 
                oCollJoints = pm.selected()
                pm.joint(zso=1, ch=1, e=1, oj='yxz', secondaryAxisOrient='xdown')
                pm.select(cl=True)

                #Orient the last joint to the world#
                selLastJnt = pm.select(oCollJoints[-1])
                pm.joint(e=1, oj='none')
                pm.select(None)


        pm.frameLayout(cll = True,w = 200, bgc=(.12, .12, .12), cl = False , label = "JOINTS AND BIND")
        pm.text(l =  "---------------------- JOINTS ---------------------" , h = 18)
        pm.columnLayout(adj=False)
        
        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=5)        
        pm.iconTextButton(style='iconAndTextVertical', l = "Joint Tool", i='kinJoint.png', command  = mc.JointTool)
        pm.iconTextButton (style='iconAndTextVertical', l = "Joint at Center", i = 'kinConnect.png', command  =  lambda * args: adb.jointAtCenter())    
        pm.iconTextButton (style='iconAndTextVertical', l = "Orient Joint", i = 'orientJoint.png', command  =  mc.OrientJointOptions)    
        pm.setParent('..')

        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=2) 
        pm.text(l='Orient Presets :', h = 35)              
        pm.optionMenu(cc = jointOrient)
        pm.menuItem(label = "- Joint Orient -")
        pm.menuItem(label = "X")
        pm.menuItem(label = "Y")
        pm.setParent('..')

        pm.separator(h=3)
        pm.text(l =  "---------------- BIND AND SKIN --------------" , h = 20)

        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=5)        
        pm.iconTextButton(style='iconAndTextVertical', l = "Bind Skin", i='smoothSkin.png', command  = mc.SmoothBindSkin, ann='popup menu available')
        pm.popupMenu()
        pm.menuItem(l='options window', c = mc.SmoothBindSkinOptions)
        pm.iconTextButton (style='iconAndTextVertical', l = "Copy Weight", i = 'copySkinWeight.png', command  = mc.CopySkinWeightsOptions)    
        pm.iconTextButton (style='iconAndTextVertical', l = "Mirror Weight", i = 'mirrorSkinWeight.png', command  = mc.MirrorSkinWeightsOptions)
        pm.setParent('..')
        
        pm.rowLayout(columnWidth3=(0, 0, 0), numberOfColumns=4)
        pm.iconTextButton (style='iconAndTextVertical', l = "Unbind Skin", i = 'detachSkin.png', command  = mc.DetachSkin)
        pm.iconTextButton (style='iconAndTextVertical', l = "Add Influence", i = 'addWrapInfluence.png', command  = mc.AddInfluenceOptions)
        pm.iconTextButton (style='iconAndTextVertical', l = "  Cluster", i = 'cluster.png', command  = lambda *args:pm.mel.newCluster(" -envelope 1"), ann='popup menu available')
        pm.popupMenu()
        pm.menuItem(l='Cluster on each Cvs', c = lambda *args:adb.clusterCvs(pm.selected()))
        pm.setParent('..')


        pm.separator(h=3)
        pm.button (l = "Paint Skin Tool", w = 200, h=30 , backgroundColor = colordic['grey'], command  = mc.ArtPaintSkinWeightsToolOptions)
        pm.separator(h=2)
        pm.button (l = "NgSkin Tool", w = 200, backgroundColor = colordic['grey'], command  = pm.Callback(self.NgskinBA))
        pm.setParent('..')
        pm.setParent('..')


        '''---------------------------------------'''
        ''' # end # '''
        '''---------------------------------------'''
        
               
        pm.dockControl("toolbox_dockwin", content="toolbox_win", a="left", aa = ['left'],  l = self.title + "_v" + str(self.version), ret=False, w = 160, fl = False, po=True)
        pm.setParent('..')
        pm.setParent('..')
        pm.setParent('..')

        '''---------------------------------------'''
        ''' # end # '''
        '''---------------------------------------'''        
        
    def uiColor(self):
        ''' 
        Personnal Palette UI
        '''

        reload(CollDict)
        template = uiTemplate('ExampleTemplate', force=True )
        template.define( button, width=200, height=35)
        template.define( frameLayout, borderVisible=False, labelVisible=False)

        # if pm.window('ColorPalette_win', q=1, ex=1):
        #     pm.deleteUI('ColorPalette_win')
        
        try:
            pm.deleteUI("ColorPalette_win",window=True)            
        except:
            with window("ColorPalette_win", t= "adbrower - ColorPalette v1.0" , tlb = True, s=True, rtf=True ) as win:
                with template:                        
                        with frameLayout():         
                            with columnLayout(adj=True, rs = 1):
                                with rowLayout(adj=True,  numberOfColumns=1):
                                    gridLayout(numberOfColumns=4, cellWidthHeight=(100, 40)) 
                                    button(bgc=colordic['grey'], l='grey', c = pm.Callback(self.getRGB,'grey'))
                                    button(bgc=colordic['grey1'], l='grey1', c = pm.Callback(self.getRGB,'grey1') )
                                    button(bgc=colordic['grey2'], l='grey2', c = pm.Callback(self.getRGB,'grey2'))
                                    button(bgc=colordic['grey4'], l='grey4', c = pm.Callback(self.getRGB,'grey4'))
                                    
                                    button(bgc=colordic['blue'], l='blue', c = pm.Callback(self.getRGB,'blue'))
                                    button(bgc=colordic['blue2'], l='blue2', c = pm.Callback(self.getRGB,'blue2'))
                                    button(bgc=colordic['blue3'], l='blue3', c = pm.Callback(self.getRGB,'blue3'))
                                                                    
                                    button(bgc=colordic['darkblue'], l='darkblue', c = pm.Callback(self.getRGB,'darkblue'))
                                    button(bgc=colordic['lightpurple'], l='lightpurple', c = pm.Callback(self.getRGB,'lightpurple'))
                                    button(bgc=colordic['lightpurple2'], l='lightpurple2', c = pm.Callback(self.getRGB,'lightpurple2'))
                                    
                                    button(bgc=colordic['green'], l='green', c = pm.Callback(self.getRGB,'green'))
                                    button(bgc=colordic['green2'], l='green2', c = pm.Callback(self.getRGB,'green2'))
                                    button(bgc=colordic['green3'], l='green3', c = pm.Callback(self.getRGB,'green3'))
                                    button(bgc=colordic['greenish'], l='greenish', c = pm.Callback(self.getRGB,'greenish'))
                                    button(bgc=colordic['lightgreen'], l='lightgreen', c = pm.Callback(self.getRGB,'lightgreen'))
                                    
                                    button(bgc=colordic['red'], l='red', c = pm.Callback(self.getRGB,'red'))
                                    button(bgc=colordic['lightred'], l='lightred', c = pm.Callback(self.getRGB,'lightred'))
                                    button(bgc=colordic['darkred'], l='darkred', c = pm.Callback(self.getRGB,'darkred'))
                                    button(bgc=colordic['darkred2'], l='darkred2', c = pm.Callback(self.getRGB,'darkred2'))
                                    button(bgc=colordic['darkred3'], l='darkred3', c = pm.Callback(self.getRGB,'darkred3'))
                                    
                                    button(bgc=colordic['orange'], l='orange', c = pm.Callback(self.getRGB,'orange'))
                                    button(bgc=colordic['orange2'], l='orange2', c = pm.Callback(self.getRGB,'orange2'))
                                    button(bgc=colordic['orange3'], l='orange3', c = pm.Callback(self.getRGB,'orange3'))
                                    button(bgc=colordic['orange4'], l='orange4', c = pm.Callback(self.getRGB,'orange4'))
                                                                       
                                    button(bgc=colordic['yellow'], l='yellow', c = pm.Callback(self.getRGB,'yellow'))
                                    
                                    button(bgc=colordic['pink'], l='pink', c = pm.Callback(self.getRGB,'pink'))
                                    button(bgc=colordic['pink2'], l='pink2', c = pm.Callback(self.getRGB,'pink2'))
                                    
                                    button(bgc=colordic['purple'], l='purple', c = pm.Callback(self.getRGB,'purple'))
                                    button(bgc=colordic['purple2'], l='purple2', c = pm.Callback(self.getRGB,'purple2'))
                                    
                                    button(bgc=colordic['darkbrown'], l='darkbrown', c = pm.Callback(self.getRGB,'darkbrown'))
                                    button(bgc=colordic['black'], l='black', c = pm.Callback(self.getRGB,'black'))
                         


    @undo
    def getRGB(self,key):               
        print (key, colordic[key])
        (pm.colorInputWidgetGrp('RGB', e = True, rgbValue=(colordic[key][0],colordic[key][1],colordic[key][2])))


#-----------------------------------
#  SLOTS
#-----------------------------------         
        
        
    @undo
    def switchDrawStyle(self):	  
        '''
        Switch between drawStyle
        '''          
        oJoints = pm.selected()
        CurrentIndex = list(set([x.drawStyle.get() for x in oJoints]))
        if CurrentIndex != 0:
            for joint in oJoints:
                pm.PyNode(joint).drawStyle.set(0)            
        for pos in range(0,3):        
            if CurrentIndex[-1] == pos:
                nextIndex = int(CurrentIndex[-1] + 2)        
        if nextIndex >=3:
            nextIndex = 0   
                    
        for each in oJoints:
            pm.PyNode(each).drawStyle.set(nextIndex)


    @undo
    def switchDrawStyleAll(self):	  
        '''
        Switch between drawStyle 
        '''          
        oJoints = pm.ls('*', type='joint')
        CurrentIndex = list(set([x.drawStyle.get() for x in oJoints]))
        # print ('Current Index    ' + str(CurrentIndex[-1]))

        if CurrentIndex != 0:
            for joint in oJoints:
                pm.PyNode(joint).drawStyle.set(0)
                
        for pos in range(0,3):        
            if CurrentIndex[-1] == pos:
                nextIndex = int(CurrentIndex[-1] + 2)            
        if nextIndex >=3:
            nextIndex = 0   
                    
        for each in oJoints:
            pm.PyNode(each).drawStyle.set(nextIndex)


    def addAttr(self):
        sel = pm.selected()[0]
        sel_name = sel.name()
        pm.textField(self.attr, e = True, text = sel_name)


    def copyAttr(self):
        ''' 
        Select mesh and the attribute(s) to copy
        '''        
        target = pm.textField(self.attr, q = True, text = True)
        
        def copyAttrLoop(attribute, target):           
            sources = pm.selected()[0]           
            source_attr = sources.name() + '.' + attribute
            attr = attribute

            _at = pm.addAttr(source_attr, q = True, at=True)
            _ln = pm.addAttr(source_attr, q = True, ln=True) 
            _min = pm.addAttr(source_attr, q = True, min=True) 
            _max = pm.addAttr(source_attr, q = True, max=True) 
            _dv = pm.addAttr(source_attr, q = True, dv=True)
            enList = [] 
              
            try:
                _en = pm.attributeQuery(str(attr), node = sources.name(), listEnum=True)[0] 
                enList.append(_en)
            except:
                pass

            if _at == 'enum':
                pm.addAttr(target, ln=str(_ln), at='enum',  en= str(enList[0]), keyable= True)
            else:
                pm.addAttr(target, ln=str(_ln), at=str(_at),  dv = _dv, keyable= True)
                    
            target_attr = target + '.' + attr
            if _min != None:
                pm.addAttr(target_attr, e = True, min = _min, max = _max)
            elif _max != None:
                pm.addAttr(target_attr, e=True, max = _max, min = _min)           
            else:
                pass        

        all_attr = [ x for x in pm.channelBox("mainChannelBox", q=1, selectedMainAttributes = 1)]
        for att in all_attr:
            copyAttrLoop(att, target)
        pm.select(target)


    @undo
    def addSeparator(self):
        node = pm.selected()[0]    
            
        name="__________"

        i=0
        for i in range(0,100):
            if i == 100:
                pm.pm.mel.error("There are more than 20 seperators. Why would you even need that many.")                
            if pm.mel.attributeExists(name, node):
                name=str(pm.mel.stringAddPrefix("_", name))                            
            else:
                break
                            
        en="..................................................................................:"
        pm.addAttr(node, ln=name, keyable=False, en=en, at="enum", nn=en)
        pm.setAttr((node + "." + name), 
            channelBox=True, keyable=False)

    @undo
    def lock_unlockAB(self, type):
        try:
            if type == 'unlock':
                selAttrs = pm.channelBox("mainChannelBox", q=1, selectedMainAttributes = 1) or []            
                if selAttrs != []:                    
                    pm.mel.channelBoxCommand('-unlock')                    
                else:
                    att_to_lock = ['tx','ty','tz','rx','ry','rx','rz','sx','sy','sz','v']
                    for sel in pm.selected():
                        for att in  att_to_lock:
                            pm.PyNode(sel).setAttr(att, lock=False,)
                
            elif type == 'lock':
                selAttrs = pm.channelBox("mainChannelBox", q=1, selectedMainAttributes = 1) or []            
                if selAttrs != []:                    
                    pm.mel.channelBoxCommand('-lock')                    
                else:
                    att_to_lock = ['tx','ty','tz','rx','ry','rx','rz','sx','sy','sz','v']
                    for sel in pm.selected():
                        for att in  att_to_lock:
                            pm.PyNode(sel).setAttr(att, lock=True,)

        except IndexError:
            pm.warning('Nothing selected')

    @undo
    def shiftAtt(self,mode):
        obj = mc.channelBox('mainChannelBox',q=True,mol=True)
        if obj:
            attr = mc.channelBox('mainChannelBox',q=True,sma=True)
            if attr:
                for eachObj in obj:
                    udAttr = mc.listAttr(eachObj,ud=True)
                    if not attr[0] in udAttr:
                        sys.exit('selected attribute is static and cannot be shifted')
                    ## temp unlock all user defined attributes
                    attrLock = mc.listAttr(eachObj,ud=True,l=True)
                    if attrLock:
                        for alck in attrLock:
                            mc.setAttr(eachObj + '.' + alck,lock=0)

                    ## shift down
                    if mode == 0:
                        if len(attr) > 1:
                            attr.reverse()
                            sort = attr
                        if len(attr) == 1:
                            sort = attr 
                        for i in sort:
                            attrLs = mc.listAttr(eachObj,ud=True)
                            attrSize = len(attrLs)
                            attrPos = attrLs.index(i)
                            mc.deleteAttr(eachObj,at=attrLs[attrPos])
                            mc.undo()
                            for x in range(attrPos+2,attrSize,1):
                                mc.deleteAttr(eachObj,at=attrLs[x])
                                mc.undo()
                    ## shift up 
                    if mode == 1:
                        for i in attr:
                            attrLs = mc.listAttr(eachObj,ud=True)
                            attrSize = len(attrLs)
                            attrPos = attrLs.index(i)
                            if attrLs[attrPos-1]:
                                mc.deleteAttr(eachObj,at=attrLs[attrPos-1])
                                mc.undo()
                            for x in range(attrPos+1,attrSize,1):
                                mc.deleteAttr(eachObj,at=attrLs[x])
                                mc.undo()

                    ## relock all user defined attributes			
                    if attrLock:
                        for alck in attrLock:
                            mc.setAttr(eachObj + '.' + alck,lock=1)


    def set_AttDefault(self):
        ''' 
        Change default value of an attribute
        '''
        sel = pm.selected()        
        for each in sel:
            attr = each.name() + '.' +(pm.channelBox("mainChannelBox", q=1, selectedMainAttributes = 1)[0])
            defaultValue =  pm.getAttr(attr)
            pm.addAttr(str(attr), e=True,  dv=defaultValue)
            print defaultValue


    ### DEF TOOLS ###
    def ToolAB(self, tool):
        if tool == "Tilt Tool" :  
            Tool__Tilt.TiltTool()
            
        elif tool == "IK - FK Switch" : 
            Tool__IKFK_Switch__PySide.ui()

        elif tool == "IK - FK Match" : 
            Tool__Match_IkFK_PySide.ui()

        elif tool == "adb Module" : 
            Tool__adbModule.adbModule()

        elif tool == "Copy Weights Tool":
            Tool__CopyWeight_Skin.showUI()
                  
        elif tool == "Auto Rig Tool":
            Tool__AutoRig.adbAutoRig()
            
        elif tool == "Shake Tool":
            arShake_v012.GUI()
            
        elif tool == "CFX ToolBox":
            Tool__adbCFX.dockUI()
                            
        elif tool == "Space Switch Tool":
            switchSetup.show()
            
        elif tool == "Skin Wrangler Tool":
            skinWrangler.show()
        
    def jointGenToolAB(self):            
        adb_tools.Tool__Joint_Generator__Pyside.showUI()    

    def multiToolAB(self):
       adb_tools.Tool__ConnectionTool.connectionTool()


    def _selectBy(self):
        type_value = pm.textField(self.select_by, q = True, tx = True)
        adb.selectType(type_value)

    ### DEF CONSTRAINTES ####

    @undo
    def pointconstraintbutton(self):
        if mc.checkBox("myChBx", q =True, v=True,) == 1:
            _mo = True
            
        elif mc.checkBox("myChBx", q =True, v=True,) == 0:
            _mo = False
                            
        if mc.checkBox('myChBx_invert', q = True, v=True) == 1:     
            mylist = mc.ls(sl=True)
            Driver = mylist[-1] #mon controleur mere
            targets = mylist[:-1]
            
        elif mc.checkBox('myChBx_invert', q = True, v=True) == 0: 
            mylist = mc.ls(sl=True)
            Driver = mylist[0] #mon controleur mere
            targets = mylist[1:]

        if mc.checkBox('myChBx_matrix', q =True, v=True)==1:
            for  each in targets:
                adb.matrixConstraint(Driver, each, channels = 't', mo=_mo)
        else:
            for  each in targets:
                mc.pointConstraint(Driver,each, mo=_mo) 
       
        
    @undo
    def orientconstraintbutton(self):
        if mc.checkBox("myChBx", q =True, v=True,) == 1:
            _mo = True
            
        elif mc.checkBox("myChBx", q =True, v=True,) == 0:
            _mo = False
                            
        if mc.checkBox('myChBx_invert', q = True, v=True) == 1:     
            mylist = mc.ls(sl=True)
            Driver = mylist[-1] #mon controleur mere
            targets = mylist[:-1]
            
        elif mc.checkBox('myChBx_invert', q = True, v=True) == 0: 
            mylist = mc.ls(sl=True)
            Driver = mylist[0] #mon controleur mere
            targets = mylist[1:]

        if mc.checkBox('myChBx_matrix', q =True, v=True)==1:
            for  each in targets:
                adb.matrixConstraint(Driver, each, channels = 'r', mo=_mo)
        else:
            for  each in targets:
                mc.orientConstraint(Driver,each, mo=_mo)    

    @undo
    def scaleconstraintbutton(self):        
        if mc.checkBox("myChBx", q =True, v=True,) == 1:
            _mo = True
            
        elif mc.checkBox("myChBx", q =True, v=True,) == 0:
            _mo = False
                            
        if mc.checkBox('myChBx_invert', q = True, v=True) == 1:     
            mylist = mc.ls(sl=True)
            Driver = mylist[-1] #mon controleur mere
            targets = mylist[:-1]
            
        elif mc.checkBox('myChBx_invert', q = True, v=True) == 0: 
            mylist = mc.ls(sl=True)
            Driver = mylist[0] #mon controleur mere
            targets = mylist[1:]

        if mc.checkBox('myChBx_matrix', q =True, v=True)==1:
            for  each in targets:
                adb.matrixConstraint(Driver, each, channels = 's', mo=_mo)
        else:
            for  each in targets:
                mc.scaleConstraint(Driver,each, mo =_mo) 
                
               
    @undo
    def aimconstraintbutton(self):        
        if mc.checkBox("myChBx", q =True, v=True,) == 1:
            _mo = True
            
        elif mc.checkBox("myChBx", q =True, v=True,) == 0:
            _mo = False
                            
        if mc.checkBox('myChBx_invert', q = True, v=True) == 1:     
            mylist = mc.ls(sl=True)
            Driver = mylist[-1] #mon controleur mere
            targets = mylist[:-1]
            
        elif mc.checkBox('myChBx_invert', q = True, v=True) == 0: 
            mylist = mc.ls(sl=True)
            Driver = mylist[0] #mon controleur mere
            targets = mylist[1:]

        for  each in targets:
            mc.aimConstraint(Driver,each, mo=_mo)                
                
                
 
    @undo
    def parentconstraintbutton(self):  
        if mc.checkBox("myChBx", q =True, v=True,) == 1:
            _mo = True
            
        elif mc.checkBox("myChBx", q =True, v=True,) == 0:
            _mo = False
                            
        if mc.checkBox('myChBx_invert', q = True, v=True) == 1:     
            mylist = mc.ls(sl=True)
            Driver = mylist[-1] #mon controleur mere
            targets = mylist[:-1]
            
        elif mc.checkBox('myChBx_invert', q = True, v=True) == 0: 
            mylist = mc.ls(sl=True)
            Driver = mylist[0] #mon controleur mere
            targets = mylist[1:]

        if mc.checkBox('myChBx_matrix', q =True, v=True)==1:
            for  each in targets:
                adb.matrixConstraint(Driver, each, channels = 'tr', mo=_mo)
        else:
            for  each in targets:
                mc.parentConstraint(Driver,each, mo=_mo) 

    @undo
    def parentscaleconstrain(self):
        ''' 
        Combination of a Parent and a Scale constraint 
        '''
        if mc.checkBox("myChBx", q =True, v=True,) == 1:
            _mo = True
            
        elif mc.checkBox("myChBx", q =True, v=True,) == 0:
            _mo = False
                            
        if mc.checkBox('myChBx_invert', q = True, v=True) == 1:     
            mylist = mc.ls(sl=True)
            Driver = mylist[-1] #mon controleur mere
            targets = mylist[:-1]
            
        elif mc.checkBox('myChBx_invert', q = True, v=True) == 0: 
            mylist = mc.ls(sl=True)
            Driver = mylist[0] #mon controleur mere
            targets = mylist[1:]

        if mc.checkBox('myChBx_matrix', q =True, v=True)==1:
            for  each in targets:
                adb.matrixConstraint(Driver, each, mo=_mo)
        else:
            for  each in targets:
                mc.parentConstraint(Driver,each, mo=_mo) 
                mc.scaleConstraint(Driver,each, mo=_mo)

    @undo
    def MatchTransformRT(self):
        '''
        Match the Rotation and Position of 2 objects 
        '''
        mylist = mc.ls(sl=True)
        Driver = mylist[0] #mon controleur mere
        targets = mylist[1:]

        if mc.checkBox("myChBx_pos", q =True, v=True,) == 1 and mc.checkBox('myChBx_rot', q = True, v=True) == 1:
            for each in targets:
                mc.matchTransform(targets,Driver,rot=True, pos=True)
                
        elif mc.checkBox("myChBx_pos", q =True, v=True,) == 1 and mc.checkBox('myChBx_rot', q = True, v=True) == 0:
            for each in targets:
                mc.matchTransform(targets,Driver,rot=False, pos=True)

        elif mc.checkBox("myChBx_pos", q =True, v=True,) == 0 and mc.checkBox('myChBx_rot', q = True, v=True) == 1:
            for each in targets:
                mc.matchTransform(targets,Driver,rot=True, pos=False)


    @undo
    def rmvConstraint(self):        
        for i, each in enumerate(pm.selected()):
            parentConstraints = (set([x for x in each.inputs() if type(x) == pm.nodetypes.ParentConstraint]))
            pm.delete(parentConstraints)
            scaleConstraints = (set([x for x in each.inputs() if type(x) == pm.nodetypes.ScaleConstraint]))
            pm.delete(scaleConstraints)
            orientConstraints = (set([x for x in each.inputs() if type(x) == pm.nodetypes.OrientConstraint]))
            pm.delete(orientConstraints)
            pointConstraints = (set([x for x in each.inputs() if type(x) == pm.nodetypes.PointConstraint]))
            pm.delete(pointConstraints) 
            aimConstraints = (set([x for x in each.inputs() if type(x) == pm.nodetypes.AimConstraint]))
            pm.delete(aimConstraints)


    ### DEF GROUP AND LOC ###
    
    @undo 
    @changeColor('index',col = (17))
    def createloc(self):    
        '''
        Creates locator at the Pivot of the object selected 
        '''    
        if pm.selected():
            try:
                loc = adb.LocOnVertex()
            except AttributeError:                            
                locs = []
                for sel in pm.selected():                                               
                    loc_align = pm.spaceLocator(n= sel)
                    locs.append(loc_align)
                    pm.matchTransform(loc_align, sel, pos = True)  
                    pm.select(locs, add = True)
                    mc.CenterPivot()                                
                adb.AutoSuffix(locs)
                return locs               
        else: 
            locs = pm.spaceLocator(n='Locator1')
            return locs
            
                     
    @undo   
    @changeColor('index',col = (17))
    def createlocCC(self):
        ''' 
        Double Clicked command:
        Creates locator in the middle of the geometry 
        '''
        
        locs = []
        for each in pm.selected():
            cls = pm.cluster(each)
            pm.select(cls, r = 1)
            loc = pm.spaceLocator(n="{}_loc_".format(each))          
            pm.matchTransform(loc,cls, rot=True, pos=True)
            pm.delete(cls)            
            locs.append(loc)
        
        pm.select(locs)
        print ("Locator at the mesh position created")
        return locs


    @undo
    def makeroot(self):
        _suff = pm.textField(self.mroot, q=True, tx=True)       
        adb.makeroot_func(subject = pm.selected(), suff = _suff)


    @undo    
    def selectchildparent(self):
        select=pm.ls(sl = 1)
        shapes=pm.listRelatives(type='transform', allDescendents=1)
        pm.select(shapes, r=1)
        pm.select(select, tgl = 1)


    @undo 
    def chparent(self):
      def chain_parent(oColl):
       for oParent, oChild in zip(oColl[0:-1], oColl[1:]):
           try:
               pm.parent(oChild, None)
               pm.parent(oChild, oParent)
           except:
               continue

      chain_parent(pm.selected(type='transform'))

    def add_material(self,mat_name= 'mat_yellow'):
        mat_dict = {
            'mat_yellow' : (1.0, 0.7, 0.0),
            'mat_bleu'   : (0.0, 0.0, 0.7),
            
            'mat_red'    :  (0.7, 0.0, 0.0),
            'mat_green'  : (0.0, 0.7, 0.0),
            'mat_darkGrey'  : (0.05, 0.05, 0.05),
            
        }
        
        selection = pm.selected()
        if pm.objExists(mat_name):
            pm.hyperShade( assign= mat_name )

        else:
            LambertYellow = mc.shadingNode("lambert",asShader=True)
            pm.setAttr(LambertYellow + ".color", mat_dict[mat_name], type = 'double3')
            pm.rename(LambertYellow, mat_name)
            pm.select(selection)
            pm.hyperShade( assign= mat_name )


    ### DEF CONTROLS ####         

    @undo
    def colorRGB(self):
        '''
        Change RGB Colors
        '''
        
        values = (pm.colorInputWidgetGrp('RGB', q=True, rgbValue=True))         
        oControler = pm.selected()
        shapes = [x.getShapes() for x in oControler]

        all_shapes = [x for i in shapes for x in i]
        
        if all_shapes == []:                
            for ctrl in oControler:
                pm.PyNode(ctrl).overrideEnabled.set(1)
                pm.PyNode(ctrl).overrideRGBColors.set(1)
                pm.PyNode(ctrl).overrideColorRGB.set(values)
        else:
            for ctrl in all_shapes:
                pm.PyNode(ctrl).overrideEnabled.set(1)
                pm.PyNode(ctrl).overrideRGBColors.set(1)
                pm.PyNode(ctrl).overrideColorRGB.set(values)
      
        self.allgrey()


    @undo
    def SelectBy(self,col,Parametre):
        ''' 
        Double Clicked command:
        Select by index color
        '''
            
        MyList = []
        Coll = pm.ls(type=("nurbsCurve","locator"))
        joints = pm.ls(type="joint")

        if joints:
            for shapes in joints: 
                oParam = pm.getAttr(str(shapes) + Parametre)    
                # print (oParam, i)
                if oParam == col:
                    # print (oParam, shapes)
                    MyList.append(shapes)                                    
                pm.select(MyList)
                print (Coll)
                for shapes in Coll:
                    oParam = pm.getAttr(str(shapes) + Parametre)
                    # print (oParam, i) 
  
                    if oParam == col:
                        # print (oParam, shapes)
                        MyList.append(shapes)  
                pm.select(MyList)            
        if Coll:
            for shapes in Coll:
                oParam = pm.getAttr(str(shapes) + Parametre)         
                # print (oParam, i)
                
                if oParam == col:                    
                    # print (oParam, shapes)
                    MyList.append(shapes)
                           
            pm.select(MyList)


    @undo
    def colordefault(self):    
        ''' 
        Reset default color 
        '''   
        try:
            ctrlSet = pm.selected()

            for ctrl in ctrlSet:
                if pm.objectType(ctrl) == "joint":
                    for each in  ctrlSet:   
                        ctrl = pm.PyNode(each)
                        ctrl.overrideEnabled.set(1)
                        ctrl.overrideRGBColors.set(0)
                        ctrl.overrideColor.set(0)
                        ctrl.overrideEnabled.set(0)
                        pm.select(None)
                else:
                    ctrls = pm.selected()
                    shapes = [x.getShapes() for x in ctrls]                    
                    all_shapes = [x for i in shapes for x in i]

                    for ctrl in all_shapes:
                        pm.PyNode(ctrl).overrideEnabled.set(1)
                        pm.PyNode(ctrl).overrideRGBColors.set(0)
                        pm.PyNode(ctrl).overrideColor.set(0)
     
        except:
            pass    

    @undo
    def makeTemplate(self,temp):        
        ctrls = pm.selected()
        shapes = [x.getShapes() for x in ctrls]                    
        ctrlSet = [x for i in shapes for x in i]
        
        for ctrl in ctrlSet:
            pm.PyNode(ctrl).overrideEnabled.set(1)
            pm.PyNode(ctrl).overrideDisplayType.set(temp)
            

    @undo
    def makeLayer(self,temp):
        ctrlSet=pm.ls(sl=1)
        myLayer = pm.createDisplayLayer(nr=1, name="Reference")
        pm.setAttr(myLayer+".displayType", temp)


    @undo
    def allgrey(self):                 
        ''' 
        Puts all the unused case of the RGB Palette grey 
        '''
        allNurbs = pm.ls(type="nurbsCurve")
        allColors = list(set([pm.PyNode(x).overrideColorRGB.get(x) for x in allNurbs]))
        nub = len(allColors)

        if nub ==0:  
            for each in range(0,10):
                pm.palettePort( 'scenePalette', edit=True, rgb=(each, 0.161, 0.161, 0.161) )  

        elif nub > 10:
            nub = 10
            for i in range(0,nub):
                pos1 = allColors[i][0]
                pos2 = allColors[i][1]
                pos3 = allColors[i][2]
                                               
                if pos1 == 0.0 and pos2 == 0.0 and pos3 == 0.0:
                    pm.palettePort( 'scenePalette', edit=True, rgb=(i, 0.161, 0.161, 0.161) )
                
                else:
                    pm.palettePort( 'scenePalette', r = True, edit=True, rgb=(i, pos1 , pos2 , pos3 ,) ) 
                                
                for each in range(nub,10):
                    pm.palettePort( 'scenePalette', edit=True, rgb=(each, 0.161, 0.161, 0.161) ) 
                                                                                                
        else:
            for i in range(0,nub):
                pos1 = allColors[i][0]
                pos2 = allColors[i][1]
                pos3 = allColors[i][2]
                                               
                if pos1 == 0.0 and pos2 == 0.0 and pos3 == 0.0:
                    pm.palettePort( 'scenePalette', edit=True, rgb=(i, 0.161, 0.161, 0.161) )
                
                else:
                    pm.palettePort( 'scenePalette', r = True, edit=True, rgb=(i, pos1 , pos2 , pos3 ,) ) 
                                
                for each in range(nub,10):
                    pm.palettePort( 'scenePalette', edit=True, rgb=(each, 0.161, 0.161, 0.161) ) 
        
            

    @undo
    def cCommand(self):
        '''
        Change or updates the color of the RGB palette case when there is a change state 
        '''
        rbgV = (pm.palettePort('scenePalette', q=True, rgbValue=True))             
        (pm.colorInputWidgetGrp('RGB', e = True, rgbValue=(rbgV[0],rbgV[1],rbgV[2])))
                
        if rbgV != [0.16099999845027924, 0.16099999845027924, 0.16099999845027924]:
            print '('+ str('{:.3f}'.format(rbgV[0])) + ', ' + str('{:.3f}'.format(rbgV[1])) + ', ' + str('{:.3f}'.format(rbgV[2]))+')'            
        else: 
            pass        
        self.allgrey()

    def cCommand_axis(self, axis):
        if axis == 'x':
            mc.checkBox('myChBxY', e =True, v=False) 
            mc.checkBox('myChBxZ', e =True, v=False) 
            
        if axis == 'y':
            mc.checkBox('myChBxX', e =True, v=False) 
            mc.checkBox('myChBxZ', e =True, v=False) 
            
        if axis == 'z':
            mc.checkBox('myChBxY', e =True, v=False) 
            mc.checkBox('myChBxX', e =True, v=False)


    def ScaleVertex(self, scale):
        sub = pm.selected()
        adb.scaleVertex(scale, subject = sub) 

    def RotateVertex(self, scale):
        sub = pm.selected()
        adb.rotateVertex(scale, subject = sub)


    ### DEF JOINT AND BIND ###
           

    def NgskinBA(self):        
        from ngSkinTools.ui.mainwindow import MainWindow
        MainWindow.open()



    ### CONNECTION ####

    @undo
    def addNodeUC(self):
        try:
            self.factor = pm.floatField(self.vfactor, q = True, value = True)
            self.index = pm.floatField(self.vindex, q = True, value = True)

            oDriver = pm.selected()[0]

            All_IncomingConn = []        
            All_DestinationsConn = []
            All_Outputs = []

            for DriverSource, DriverDestination in oDriver.inputs(c=1, p=1):
                All_IncomingConn.append(DriverDestination)
                
            for DriverSource, DriverDestination in oDriver.outputs(c=1, p=1):
                All_DestinationsConn.append(DriverDestination)
               
            for DriverSource, DriverDestination in oDriver.outputs(c=1, p=1):
                All_Outputs.append(DriverSource)
                      
            MDnode =  pm.shadingNode('unitConversion', asUtility=1, n = "{0}__MD__".format(oDriver))                   
            pm.PyNode(MDnode).conversionFactor.set(self.factor)

            # Make Connections
            
            All_Outputs[int(self.index)] >> MDnode.input
            MDnode.output >> All_DestinationsConn[int(self.index)]
                
            ## Clean Unused Conversion Nodes ##            
            pm.mel.hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")    
            print ("// Result: Node was added //")

        except:            
            if pm.selected():
                print ("// Result: Node was added //")
            else:
                print ("// Warning: Nothing is selected!! //")

    @undo
    def addNodeRev(self):
        try:
            self.factor = pm.floatField(self.vfactor, q = True, value = True)
            self.index = pm.floatField(self.vindex, q = True, value = True)

            oDriver = pm.selected()[0]

            All_IncomingConn = []        
            All_DestinationsConn = []
            All_Outputs = []

            for DriverSource, DriverDestination in oDriver.inputs(c=1, p=1):
                All_IncomingConn.append(DriverDestination)
                
            for DriverSource, DriverDestination in oDriver.outputs(c=1, p=1):
                All_DestinationsConn.append(DriverDestination)
               
            for DriverSource, DriverDestination in oDriver.outputs(c=1, p=1):
                All_Outputs.append(DriverSource)
                      
            MDnode =  pm.shadingNode('reverse', asUtility=1, n = "{0}__MD__".format(oDriver))                   

            # Make Connections
            
            All_Outputs[int(self.index)] >> MDnode.inputX
            MDnode.outputX >> All_DestinationsConn[int(self.index)]
                
            ## Clean Unused Conversion Nodes ##            
            pm.mel.hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")    
            print ("// Result: Node was added //")

        except:            
            if pm.selected():
                print ("// Result: Node was added //")
            else:
                print ("// Warning: Nothing is selected!! //")


    def printAllConns(self):
        adb_utils.Class__Transforms.Transform(pm.selected()).getAllConns()

    @undo
    def addNodes(self,node):        
        try:
            oDriver = pm.selected()[0]
            myNode = pm.shadingNode(node, asUtility = 1, n = '{0}_{1}__01'.format(oDriver,node) )
            pm.select(myNode)
            print ("// Result: Node was added //")
            
        except IndexError:
            myNode = pm.shadingNode(node, asUtility = 1)
            pm.select(myNode)
            
            print ("// Result: Node was added //")


    @undo
    def addNodeMD(self):
        ''' 
        Creates Multiply Divide nodes for selected connections
        '''
        try:
            self.factor = pm.floatField(self.vfactor, q = True, value = True)
            self.operation = pm.floatField(self.voperation, q = True, value = True)
            self.index = pm.floatField(self.vindex, q = True, value = True)

            oDriver = pm.selected()[0]

            All_IncomingConn = []        
            All_DestinationsConn = []
            All_Outputs = []

            for DriverSource, DriverDestination in oDriver.inputs(c=1, p=1):
                All_IncomingConn.append(DriverDestination)

            for DriverSource, DriverDestination in oDriver.outputs(c=1, p=1):
                All_DestinationsConn.append(DriverDestination)
               
            for DriverSource, DriverDestination in oDriver.outputs(c=1, p=1):
                All_Outputs.append(DriverSource)
                      
            MDnode =  pm.shadingNode('multiplyDivide', asUtility=1, n = "{0}__MD__".format(oDriver))                       
            pm.PyNode(MDnode).operation.set(self.operation)
            pm.PyNode(MDnode).input2X.set(self.factor)
            pm.PyNode(MDnode).input2Y.set(self.factor)
            pm.PyNode(MDnode).input2Z.set(self.factor)

            ## Make Connections
            
            All_Outputs[int(self.index)] >> MDnode.input1X
            MDnode.outputX >> All_DestinationsConn[int(self.index)]
                
            ## Clean Unused Conversion Nodes ##            
            pm.mel.hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")

            print ("// Result: Node was added //")

        except:            
            if pm.selected():
                print ("// Result: Node was added //")
            else:
                print ("// Warning: Nothing is selected!! //")

    @undo
    def renaming(self):
        '''
        Rename
        '''        
        sel = pm.selected()        
        if len(sel) > 1:
            new_name = pm.textField(self.vnew_name, q = True, text = True)            
            for i,each in enumerate(pm.selected()):
                each.rename(str(new_name) + str(i+1))
        else:
            new_name = pm.textField(self.vnew_name, q = True, text = True)
            pm.rename(sel, str(new_name))

    @undo
    def replace_Name(self):
        '''
        Replace and rename
        '''
        old_name = pm.textField(self.vold_name, q = True, text = True)
        new_name = pm.textField(self.vnew_name, q = True, text = True)
        
        for each in pm.selected():
            each.rename(each.name().replace(str(old_name),str(new_name)))

    @undo
    def no_Pasted(self):
        '''
        Remove all "pasted" 
        '''
        for each in pm.ls('pasted__*'):
            each.rename(each.name().replace('pasted__',''))

    @undo
    def add_Suffix(self):
        ''' 
        Add a Suffix 
        '''
        old_name = pm.textField(self.vold_name, q = True, text = True)
        new_name = pm.textField(self.vnew_name, q = True, text = True)
        
        oColl = pm.selected()

        for each in oColl:
            each.rename(str(each) + new_name)
    
            
    def add_Suffix_predefined(self,suffix):
        ''' 
        Add a Suffix 
        '''    
        oColl = pm.selected()

        for each in oColl:
            each.rename(str(each) + suffix)

    @undo
    def add_Prefix(self):
        ''' 
        Add a Prefix 
        '''
        old_name = pm.textField(self.vold_name, q = True, text = True)
        new_name = pm.textField(self.vnew_name, q = True, text = True)        
        
        oColl = pm.selected()
        for each in oColl:
            each.rename(new_name + str(each) )

    @undo
    def add_Prefix_predefined(self,prefix):
        ''' 
        Add a Prefix 
        '''      
    
        oColl = pm.selected()
        for each in oColl:
            each.rename(prefix + str(each) )

    @undo
    def removeName(self):
        '''
        Remove a part of a name
        '''
        old_name = pm.textField(self.vold_name, q = True, text = True)
        new_name = pm.textField(self.vnew_name, q = True, text = True)

        for each in pm.selected():
            each.rename(each.name().replace(old_name,''))

                        
#-----------------------------------
#  FUNCTIONS
#----------------------------------- 


    @undo
    def shapeColor(self,col):
        ''' 
        Change the color override of the selection 
        '''           
        ctrls = pm.selected()       
        shapes = [x.getShapes() for x in ctrls]                  
        all_shapes = [x for i in shapes for x in i] or []

        if all_shapes != []:
            for ctrl in all_shapes:
                pm.PyNode(ctrl).overrideEnabled.set(1)
                pm.PyNode(ctrl).overrideRGBColors.set(0)
                pm.PyNode(ctrl).overrideColor.set(col)                                                               
            print (col)            
        else:
            for each in  ctrls:   
                ctrl = pm.PyNode(each)
                ctrl.overrideEnabled.set(1)
                ctrl.overrideRGBColors.set(0)
                ctrl.overrideColor.set(col)
                pm.select(None)
            print (col)                

    @changeColor()
    def shape_replacement(self, shape_name):
        ''' 
        Replace Shape according to the ShapesLibrary.py file 
        '''               
        sm = adbShape.shapeManagement(subject = pm.selected())
        sm.shapes = shape_name 
        return sm.shapes




myTools = AudreyToolBox()
