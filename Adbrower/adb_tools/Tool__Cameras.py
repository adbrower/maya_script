# ------------------------------------------------------------------------------------------------------
# Rigging Cameras Tool
# -- Version 1.3.0    
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------------------------------------------------------

import maya.cmds as mc
import pymel.core as pm
import sys

import adbrower
adb = adbrower.Adbrower()

from CollDict import colordic

#-----------------------------------
#  CLASS
#----------------------------------- 

class cameraTools():
    def __init__(self, **kwargs):
        
        self.version = "1.0.0"
        self.title = "adbrower - Cameras Tool"
        self.name = "CamTool_win"

        self.currentCam=pm.lookThru(q=1)
        self.allCam=pm.listCameras(o=False, p = True)
        
        self.ui()

    def ui(self):

        template = pm.uiTemplate('ExampleTemplate', force=True )
        template.define( pm.button, width=120, height=25)
        template.define( pm.frameLayout, mh=2, borderVisible=False, labelVisible=False )


        if pm.window(self.name, q=1, ex=1):
            pm.deleteUI(self.name)

        with pm.window(self.name, t= self.title + " v." + str(self.version), s=True, tlb = True) as self.win:

            with template:                            
                    with pm.frameLayout():
                        with pm.columnLayout(adj=True,rs=2):
                            with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=2):
                                pm.text(label="All Cameras", w = 120)
                                pm.text(label="Selected Cameras",  w = 120)

                            with pm.rowLayout( numberOfColumns=4):
                                self.all_cams = pm.textScrollList(h=120, allowMultiSelection=True, append=self.allCam, dcc = pm.Callback(self.getSelected), w = 120 )
                                self.sel_cam = pm.textScrollList(h=120, allowMultiSelection=True, w = 120, dcc = pm.Callback(self.getSelected2)) 
                                  
                            with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=2):
                                pm.button(label="Refresh", backgroundColor = (0.373, 0.404, 0.459), c = pm.Callback(self.refresh_allCam))                                        
                                pm.button(label="Reset", backgroundColor = (0.373, 0.404, 0.459), c = pm.Callback(self.refresh_selCam))                                        

                            with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=2):
                                pm.button(label="Add Custom Cam",  w=240, backgroundColor = colordic['darkblue'], c = pm.Callback(self.AddCams))  
                                               
                            with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=2):
                                pm.button(label="Remove Custom Cam",  w=240, backgroundColor = colordic['darkblue'], c = pm.Callback(self.removeCam))                                                           

                            with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=1):
                                pm.button(label="Toggle", w=240,  backgroundColor =colordic['green3'], c = pm.Callback(self.toggleCam))
                                                                            
#-----------------------------------
#  SLOTS
#-----------------------------------                                                                                                                                                                                                                                      
    def getSelected(self):
        self.viewCam = pm.textScrollList(self.all_cams, q=True, selectItem=True)
        pm.lookThru(self.viewCam)                                                                                                              

    def getSelected2(self):
        self.viewCam = pm.textScrollList(self.all_cams, q=True, selectItem=True)
        pm.lookThru(self.viewCam)  

    def AddCams(self):
        self.sel_cams = pm.textScrollList(self.all_cams, q=True, selectItem=True) 
        pm.textScrollList(self.sel_cam, edit=True, append = self.sel_cams )

    def removeCam(self):
        selectItem = mc.textScrollList(self.sel_cam, q=True, selectItem=True)
        pm.textScrollList(self.sel_cam, edit=True, ri = selectItem )

        ## list management
        pm.select(selectItem)
        rmv = pm.selected()
        tempList = [x for x in rmv]  
           
        for i in range(0,len(tempList)):       
            self.sel_cams.remove(tempList[i])
            
        pm.select(None)

    def toggleCam(self):
        currentCam=pm.lookThru(q=1)
        allCam=self.sel_cams

        for pos in range(0,len(allCam)):
            if currentCam == allCam[pos]:
                nextCam=int(pos + 1)                 
        if nextCam>=len(allCam):
            nextCam=0            
        pm.lookThru(allCam[nextCam])

    def refresh_allCam(self):
        self.allCam=pm.listCameras(o=False, p = True)
        pm.textScrollList( self.all_cams,  edit = True, removeAll=True)
        pm.textScrollList( self.all_cams,  edit = True, append=self.allCam, )

    def refresh_selCam(self):
        pm.textScrollList(self.sel_cam,   edit=True, removeAll=True) 
        self.sel_cams = []
    




cameraTools()

























