# -------------------------------------------------------------------
# adb AUTO RIG   
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# -------------------------------------------------------------------

from pymel.core import *
import traceback
import pymel.core as pm
import maya.cmds as mc


#-----------------------------------
#  CUSTOM IMPORT
#----------------------------------- 

from adbrower import lprint
from adbrower import flatList
import CollDict
import ShapesLibrary as sl
from CollDict import colordic    

import adbrower
adb = adbrower.Adbrower()

from adb_utils.adb_script_utils.Pretty_DocString  import *
import adb_rig.Class__Guide_autorig as adb_guide_autoRig
import adb_rig.Class__Build_autorig as adb_build_autoRig
import adb_utils.rig_utils.Class__ShapeManagement as adbShape

#-----------------------------------
#  DECORATORS
#----------------------------------- 

from adbrower import undo
from adbrower import changeColor

#-----------------------------------
#  CLASS
#----------------------------------- 

class adbAutoRig():
    '''Auto Rig Toolbox  '''

    def __init__(self, **kwargs): 
        self.win = window(t= "adbrower - AutoRig v1.0" , tlb = True, s=True, rtf=True, w = 255)    
        pm.scrollLayout(horizontalScrollBarThickness=16,verticalScrollBarThickness=16,) 
        if pm.dockControl('adb_AutoRig', q=1, ex=1):
            pm.deleteUI('adb_AutoRig')        
        self.ui()
        self.allgrey()
        
    def ui(self):  
        template = uiTemplate('ExampleTemplate', force = True )
        template.define( button, width=250, height = 25)
        template.define( frameLayout, borderVisible = False, labelVisible = False)
        
        with template:      
            with formLayout():
                pm.dockControl("adb_AutoRig", content=self.win, a="right")
                with columnLayout(adj=True, rs = 4):                 
                    with rowLayout(numberOfColumns=2):
                        text(label='Name: ')
                        self.namespace_txt = textField(pht = 'Untilted', w=215) 
                        
                    button(l='Add Namespace',  bgc = colordic['grey'], c = pm.Callback(self.createNamespace))                               
                    button(l='Namespace Editor',  bgc = colordic['grey'], c = pm.Callback(mc.NamespaceEditor))                               

                    with rowLayout(adj=True, numberOfColumns = 3): 
                        separator(w=5, vis=True, bgc = colordic['grey4'], h = 1)  
                        text(label=' NUMBER OF JOINTS : ', fn = 'boldLabelFont')
                        separator(w=90, vis=True, bgc = colordic['grey4'], h = 1)
                        
                    with rowLayout( numberOfColumns=4):
                        text(label="Spine")
                        self.spine_float = floatField(v = 5, precision=1, showTrailingZeros=0)
                        text(label=" Neck ")
                        self.neck_float  = floatField(v = 4, precision=2,  showTrailingZeros=0)

                    with rowLayout(adj=True, numberOfColumns = 3): 
                        separator(w=5, vis=True, bgc = colordic['grey4'], h = 1)  
                        text(label=' CREATE GUIDE : ', fn = 'boldLabelFont')
                        separator(w=120, vis=True, bgc = colordic['grey4'], h = 1)
                        
                    with columnLayout(rs=5):
                        button(l='BUILD GUIDE',  bgc = colordic['green'], c = pm.Callback(self.build_guide))
                        
                    with rowLayout(adj=True, numberOfColumns = 3): 
                        separator(w=5, vis=True, bgc = colordic['grey4'], h = 1)  
                        text(label=' CREATE RIG : ', fn = 'boldLabelFont')
                        separator(w=120, vis=True, bgc = colordic['grey4'], h = 1)
                    with columnLayout(rs=5):                       
                        button(l='BUILD ALL RIG',  bgc = colordic['green3'], c = pm.Callback(self.build_all_rig))
    
                    # TODO
                    with frameLayout( cll = True, nbg=False, bgc=colordic['grey1'], labelVisible=True , cl = True, label = " BY PART"):  
                        # with frameLayout( cll = True, nbg=False, labelVisible=True , cl = True, label = "LEG"):  
                        #     with rowLayout(numberOfColumns=2):
                        #         checkBox("leg_cbx", l = "leg", h = 20)
                        #         checkBox("foot_cbx", l = "foot", h = 20)
                        # with frameLayout( cll = True, nbg=False, labelVisible=True , cl = True, label = "ARM"):  
                        #     with rowLayout(numberOfColumns=2):
                        #         checkBox("arm_cbx", l = "arm", h = 20)
                        #         checkBox("hand_cbx", l = "hand", h = 20)                 
                        # with frameLayout( cll = True, nbg=False, labelVisible=True , cl = True, label = "SPINE"):  
                        #     with rowLayout(adj=True, numberOfColumns=3):
                        #         button(l='Guide', w = 50)                    
                        # with frameLayout( cll = True, nbg=False, labelVisible=True , cl = True, label = "NECK"):  
                        #     with rowLayout(adj=True, numberOfColumns=3):
                        #         button(l='Guide', w = 50)                    
 
                        button(l='GUIDE CUSTOM RIG',  bgc = colordic['green'])      
                                         
                    with rowLayout(adj=True, numberOfColumns = 3): 
                        separator(w=5, vis=True, bgc = colordic['grey4'], h = 1)  
                        text(label=' RIG OPTIONS : ', fn = 'boldLabelFont')
                        separator(w=120, vis=True, bgc = colordic['grey4'], h = 1)  
                    with columnLayout(rs=5):                                              
                        button(l='Show / Hide Feet Locators',  bgc = colordic['grey'], c = pm.Callback(self.show_hide_foot_locs))
                        button(l='Show / Hide Proxy Plane',  bgc = colordic['grey'], c = pm.Callback(self.show_hide_proxy_planes))

                    with frameLayout( cll = True, bgc=colordic['grey1'], labelVisible=True , cl = False, label = "CONTROLS OPTIONS"):  

                        with columnLayout(rs=5):
                            text(label=' Control size : ')
                            
                        with rowLayout( numberOfColumns = 3):
                            button(l='Reduce Size',  bgc = colordic['grey'], w=124, c = pm.Callback(self.ScaleVertex,'-'))
                            button(l='Increase Size',  bgc = colordic['grey'], w=124, c = pm.Callback(self.ScaleVertex,'+'))
                            
                        with columnLayout(rs=5):
                            text(label=' Control axis : ')
                        with rowLayout( numberOfColumns = 3):
                            button(l='Rotate X',  bgc = colordic['grey'], w=82, c = pm.Callback(self.RotateVertex,'x'))
                            button(l='Rotate Y',  bgc = colordic['grey'], w=82, c = pm.Callback(self.RotateVertex,'y'))
                            button(l='Rotate Z',  bgc = colordic['grey'], w=82, c = pm.Callback(self.RotateVertex,'z'))

                        with columnLayout(rs=5):
                            text(label=' Control Shape : ')
                            with rowLayout(adj=True, numberOfColumns = 4):
                                pm.checkBox('myChBxX', l = "X", h = 20, v = True, cc = pm.Callback(self.cCommand_axis,'x'))
                                pm.checkBox('myChBxY', l = "Y", h = 20, cc = pm.Callback(self.cCommand_axis,'y'))
                                pm.checkBox('myChBxZ',  l = "Z", h = 20,cc = pm.Callback(self.cCommand_axis,'z'))
                                                                                                                                                                                        
                            pm.optionMenu(w=220, cc = self.createctrl)
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

                    
                        with tabLayout('indexRGBTab',innerMarginWidth=5, innerMarginHeight=5) as tabs:                                                  
                            with rowColumnLayout(numberOfColumns=2) as child1:

                                '''Index'''

                                with gridLayout(numberOfColumns=7, cellWidthHeight=(35, 20)):                   
                                    pm.iconTextButton(bgc=(.000, .000, .000), command= pm.Callback(self.shapeColor,1))
                                    pm.iconTextButton(bgc=(.247, .247, .247), command= pm.Callback(self.shapeColor,2))
                                    pm.iconTextButton(bgc=(.498, .498, .498), command= pm.Callback(self.shapeColor,3))
                                    pm.iconTextButton(bgc=(0.608, 0, 0.157), command= pm.Callback(self.shapeColor,4)) 
                                    pm.iconTextButton( bgc=(0, 0.016, 0.373), command= pm.Callback(self.shapeColor,5))        
                                    pm.iconTextButton(bgc=(0, 0, 1), command= pm.Callback(self.shapeColor,6))

                                    pm.iconTextButton(bgc=(0, 0.275, 0.094), command= pm.Callback(self.shapeColor,7))
                                    pm.iconTextButton(bgc=(0.145, 0, 0.263), command= pm.Callback(self.shapeColor,8)) #
                                    pm.iconTextButton(bgc=(0.78, 0, 0.78), command= pm.Callback(self.shapeColor,9))
                                    pm.iconTextButton(bgc=(0.537, 0.278, 0.2), command= pm.Callback(self.shapeColor,10))    
                                    pm.iconTextButton(bgc=(0.243, 0.133, 0.122), command= pm.Callback(self.shapeColor,11))        
                                    pm.iconTextButton(bgc=(0.6, 0.145, 0), command= pm.Callback(self.shapeColor,12)) #          

                                    pm.iconTextButton(bgc=(1, 0, 0), command= pm.Callback(self.shapeColor,13))  
                                    pm.iconTextButton(bgc=(0, 1, 0), command= pm.Callback(self.shapeColor,14))        
                                    pm.iconTextButton(bgc=(0, 0.255, 0.6), command= pm.Callback(self.shapeColor,15)) #
                                    pm.iconTextButton(bgc=(1, 1, 1), command= pm.Callback(self.shapeColor,16)) #   
                                    pm.iconTextButton(bgc=(1, 1, 0), command= pm.Callback(self.shapeColor,17))  
                                    pm.iconTextButton(bgc=(0.388, 0.863, 1), command= pm.Callback(self.shapeColor,18))

                                    pm.iconTextButton(bgc=(0.263, 1, 0.635), command= pm.Callback(self.shapeColor,19)) #         
                                    pm.iconTextButton(bgc=(1, 0.686, 0.686), command= pm.Callback(self.shapeColor,20))
                                    pm.iconTextButton(bgc=(0.89, 0.675, 0.475), command= pm.Callback(self.shapeColor,21))
                                    pm.iconTextButton(bgc=(1, 1, 0.384), command= pm.Callback(self.shapeColor,22))            
                                    pm.iconTextButton(bgc=(0, 0.6, 0.325), command= pm.Callback(self.shapeColor,23))
                                    pm.iconTextButton(bgc=(0.627, 0.412, 0.188), command= pm.Callback(self.shapeColor,24)) #  

                                    pm.iconTextButton(bgc=(0.62, 0.627, 0.188), command= pm.Callback(self.shapeColor,25))        
                                    pm.iconTextButton(bgc=(0.408, 0.627, 0.188), command= pm.Callback(self.shapeColor,26)) #        
                                    pm.iconTextButton(bgc=(0.188, 0.627, 0.365), command= pm.Callback(self.shapeColor,27)) #  
                                    pm.iconTextButton(bgc=(0.188, 0.627, 0.627), command= pm.Callback(self.shapeColor,28))
                                    pm.iconTextButton(bgc=(0.188, 0.404, 0.627), command= pm.Callback(self.shapeColor,29))
                                    pm.iconTextButton(bgc=(0.435, 0.188, 0.627), command= pm.Callback(self.shapeColor,30))

                                    pm.iconTextButton(bgc=(0.507, 0.041, 0.277), command= pm.Callback(self.shapeColor,31))       

                            ''' RGB '''
                            with frameLayout() as child2:
                                with rowLayout(numberOfColumns=2):
                                    colorInputWidgetGrp('RGB', label='Color', rgb=(1, 0, 0), cw3=(0, 30, 162))                    
                            tabLayout( tabs, edit=True, tabLabel=((child1, 'Index'), (child2, 'RGB')) )   
                            
                        with rowLayout(numberOfColumns=2):
                            pm.button(l = "Default color", w =124, backgroundColor = colordic['grey'], c = pm.Callback(self.colordefault))
                            pm.button(l = "Set RGB Color", w =124, backgroundColor = colordic['grey'])
                        
                        with frameLayout():                          
                            pm.palettePort( 'scenePalette', dim=(10, 1), h =20, ced= True, r= True, scc = 0, cc = self.cCommand)


        
#-----------------------------------
#  SLOTS
#----------------------------------- 

    def createNamespace(self):
        self.namespace_name = pm.textField(self.namespace_txt, q=True, text=True)
        pm.namespace( add=self.namespace_name)

    def build_guide(self):
        adb_guide_autoRig.autoRigGuide()
        
    def build_all_rig(self):         
        self.namespace_name = pm.textField(self.namespace_txt, q=True, text=True)
        self.spine_num = pm.floatField(self.spine_float, q=True, v=True)
        self.neck_num = pm.floatField(self.neck_float, q=True, v=True)

        if self.namespace_name != '':
            pm.namespace( add=self.namespace_name)
        else:
            pass
        
        self.Rig = adb_build_autoRig.autoRig()
        self.Rig.build_legs()
        self.Rig.build_arms()
        self.Rig.build_spine(int(self.spine_num))
            
        pm.PyNode('x__guide_autoRig__grp__').v.set(0)
        sys.stdout.write('Auto rig is build \n')

    def show_hide_foot_locs(self):       
        try:
            CurrentIndex = self.Rig.getFeetLocators[0].v.get()
            if CurrentIndex == True:
                [x.v.set(0) for x in self.Rig.getFeetLocators]
            else:
               [x.v.set(1) for x in self.Rig.getFeetLocators] 
        except AttributeError:
            foot_locs = ['l__Foot__pos_locatorTZnegative', 'l__Foot__pos_locatorTXpositive', 'l__Foot__pos_locatorTZpositive', 'r__Foot__pos_locatorTXpositive', 'l__Foot__pos_locatorTXnegative', 'r__Foot__pos_locatorTZpositive', 'r__Foot__pos_locatorTXnegative', 'r__Foot__pos_locatorTZnegative']
            CurrentIndex = pm.PyNode(foot_locs[0]).v.get()            
            if CurrentIndex == True:
                [pm.PyNode(x).v.set(0) for x in foot_locs]
            else:
               [pm.PyNode(x).v.set(1) for x in foot_locs] 
               
    def show_hide_proxy_planes(self):
        proxy_planes = ['r__Arm__proxy_plane_skin__msh__', 'r__Arm__proxy_plane_offset__msh__', 'm__spine__ik_proxy_plane_skin', 'l__Arm__proxy_plane_skin__msh__', 'l__Arm__proxy_plane_offset__msh__', 'l__Leg__proxy_plane_skin__msh__', 'l__Leg__proxy_plane_offset__msh__', 'r__Leg__proxy_plane_skin__msh__', 'r__Leg__proxy_plane_offset__msh__']

        CurrentIndex = pm.PyNode(proxy_planes[0]).v.get()            
        if CurrentIndex == True:
            [pm.PyNode(x).v.set(0) for x in proxy_planes]
        else:
           [pm.PyNode(x).v.set(1) for x in proxy_planes] 

    def RotateVertex(self, scale):
        sub = pm.selected()
        adb.rotateVertex(scale, subject = sub)
 

    def ScaleVertex(self, scale):
        sub = pm.selected()
        adb.scaleVertex(scale, subject = sub)
 

##=================
# CONTROLS
##=================

    def createctrl(self,shape): 
        '''
        Creates a new controler or change controler shape
        '''
        if shape == "Cube" : 
            sel = pm.selected()                                  
            self.shape_replacement(sl.cube_shape)
            pm.select(sel)
        
        elif shape == "Square": 
            sel = pm.selected()   
            self.shape_replacement(sl.square_shape)
                                    
        elif shape == "Circle":  
            sel = pm.selected()                               
            if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                self.shape_replacement(sl.circleX_shape)
            elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                self.shape_replacement(sl.circleY_shape)
            elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:
                self.shape_replacement(sl.circleZ_shape)
            pm.select(sel)
            
        elif shape == "Ball":    
            sel = pm.selected()                         
            self.shape_replacement(sl.ball2_shape)
            pm.select(sel)
                      
        elif shape == "Diamond": 
            sel = pm.selected()               
            self.shape_replacement(sl.diamond_shape)
            pm.select(sel)
            
        elif shape == "Main":  
            sel = pm.selected()
            self.shape_replacement(sl.main_shape)
            pm.select(sel)
                                
        elif shape == "Fleches":  
            sel = pm.selected()             
            self.shape_replacement(sl.fleches_shape)
            pm.select(sel)
                                     
        elif shape == "Arrow":       
            sel = pm.selected()                          
            if mc.checkBox('myChBxX', q =True, v=True,) == 1:
                self.shape_replacement(sl.Xarrow_shape)
            elif mc.checkBox('myChBxY', q =True, v=True,) == 1:
                self.shape_replacement(sl.Yarrow_shape)
            elif mc.checkBox('myChBxZ', q =True, v=True,) == 1:
                self.shape_replacement(sl.Zarrow_shape)
            pm.select(sel)
            
        elif shape == "Double_fleches_ctrl":
            sel = pm.selected()
            self.shape_replacement(sl.double_fleches_shape)
            pm.select(sel)
            
        elif shape == "Arc_fleches_ctrl":               
            sel = pm.selected()
            self.shape_replacement(sl.arc_fleches_shape)
            pm.select(sel)
            
        elif shape == "Locator_shape" :  
            sel = pm.selected()
            self.shape_replacement(sl.locator_shape)
            pm.select(sel)
            
        elif shape == "Double_Pin" :  
            sel = pm.selected()
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
            pm.select(sel)
            
        elif shape == "Pin" :  
            sel = pm.selected()
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
            pm.select(sel)
            
        elif shape == "Cylinder" :  
            sel = pm.selected()
            self.shape_replacement(sl.cylinder_shape)
            pm.select(sel)
            
        elif shape == "Circle_Cross" :  
            sel = pm.selected()
            self.shape_replacement(sl.circleCross_shape)
            pm.select(sel)
            
        elif shape == "Cog" :
            sel = pm.selected()
            self.shape_replacement(sl.cog_shape)
            pm.select(sel)

    def shapeColor(self,col):
        ''' Change the color override of the selection '''           
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


    def colordefault(self):    
        ''' Reset default color '''   
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

    def cCommand(self):
        '''Change or updates the color of the RGB palette case when there is a change state '''
        rbgV = (pm.palettePort('scenePalette', q=True, rgbValue=True))             
        (pm.colorInputWidgetGrp('RGB', e = True, rgbValue=(rbgV[0],rbgV[1],rbgV[2])))
                
        if rbgV != [0.16099999845027924, 0.16099999845027924, 0.16099999845027924]:
            print '('+ str('{:.3f}'.format(rbgV[0])) + ', ' + str('{:.3f}'.format(rbgV[1])) + ', ' + str('{:.3f}'.format(rbgV[2]))+')'            
        else: 
            pass        
        self.allgrey()

    def colorRGB(self, foo):
        '''Change RGB Colors'''        
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

                                
    def allgrey(self):                 
        ''' Puts all the unused case of the RGB Palette grey '''
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

                        
    @changeColor()
    def shape_replacement(self, shape_name):
        ''' Replace Shape according to the ShapesLibrary.py file '''               
        sm = adbShape.shapeManagement(subject = pm.selected())
        sm.shapes = shape_name 
        return sm.shapes




                                                                                                    
# adbAutoRig()