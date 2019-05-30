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


#-----------------------------------
#  CUSTOM IMPORT
#----------------------------------- 

import CollDict
from CollDict import colordic    

import adbrower
adb = adbrower.Adbrower()
import ShapesLibrary as sl

from adbrower import lprint
from adbrower import flatList

from adb_utils.adb_script_utils.Pretty_DocString import *
import adb_utils.adb_script_utils.Script__WrapDeformer as adbWrap
import adb_utils.adb_script_utils.Script__WrapDeformer_Setup as adbWrapSetUp
import adb_utils.adb_script_utils.Script__ProxyPlane as adbProxy
import adb_utils.rig_utils.Class__Folli as adbFolli
import adb_utils.adb_script_utils.Functions__Rivet as adbRivet
import adb_utils.Class__Transforms as adbTransform

#-----------------------------------
#  DECORATORS
#----------------------------------- 

from adbrower import undo
from adbrower import changeColor

#-----------------------------------
#  CLASS
#----------------------------------- 

class adbModule():
    '''This Tool makes a tilt fonction on any object  '''

    def __init__(self, **kwargs): 
        self.win = window(t= "adbrower - Module v1.0" , tlb = True, s=True, rtf=True)    
        pm.scrollLayout(horizontalScrollBarThickness=16,verticalScrollBarThickness=16,) 
        if pm.dockControl('adb_Module', q=1, ex=1):
            pm.deleteUI('adb_Module')        
        self.ui()
        
    def ui(self):  
        template = uiTemplate('ExampleTemplate', force = True )
        template.define( button, width=200, height = 25)
        template.define( frameLayout, borderVisible = False, labelVisible = False)
        
        with template:      
            with formLayout():
                pm.dockControl("adb_Module", content=self.win, a="left")
                with columnLayout(adj=True, rs = 1):                     
                    with columnLayout(adj=True, rs = 4):                                                
                            self.docString = checkBox(l='Doc String')                        
                    with frameLayout( cll = True, bgc=(0.202, 0.202, 0.202), labelVisible=True , cl = False, label = "INFORMATION"):                    
                        with columnLayout(adj=True, rs = 4):                    
                                button(label="Print List",  backgroundColor = colordic['grey1'], c= Callback(adb.List)  )   
                                button(label="Print Type",  backgroundColor = colordic['grey1'], c= pm.Callback(self.Type))                                                 
                                button(label="Print Type PyMel",  backgroundColor = colordic['grey1'], c= pm.Callback(self.TypePymel) )   

                    with frameLayout( cll = True, bgc=(0.202, 0.202, 0.202), labelVisible=True , cl = False, label = "RIGGING"):         
                        with columnLayout(adj=True, rs = 4):
                            button(label="Pv Guide",  backgroundColor = colordic['grey1'], c= pm.Callback(self._pvGuide) )
                            button(label="Find Constraint Driver",  backgroundColor = colordic['grey1'], c = pm.Callback(self.consDriver) )
                            button(label="Find Constraint Target",  backgroundColor = colordic['grey1'], c = pm.Callback(self.consTarget) )
                            button(label="DrivenKeys to Remap Value",  backgroundColor = colordic['grey1'],  c = pm.Callback(self.DkToRv)) 
                            button(label="Rivet From Face",  backgroundColor = colordic['grey1'],  c = lambda*args: adbRivet.rivet_from_faces(scale = 0.2)) 
                            button(label="Sticky From Face",  backgroundColor = colordic['grey1'],  c = lambda*args: adbRivet.sticky_from_faces(scale = 0.2)) 
                       
                            def proxyPlane(axis):
                                if axis == "                       - X AXIS -":
                                    adbProxy.plane_proxy(pm.selected(), 'proxy_plane', 'x')                                        
                                elif axis == "                       - Y AXIS -":
                                    adbProxy.plane_proxy(pm.selected(), 'proxy_plane', 'y')                                 
                                elif axis == "                       - Z AXIS -":
                                    adbProxy.plane_proxy(pm.selected(), 'proxy_plane', 'z')                                           
                                elif axis == "               - Create Proxy Plane -":
                                    pass                                           
                                else:
                                    pm.warning('Choice None Existant')
                                                                                                                                          
                            optionMenu(w=200, h=30,  cc = proxyPlane )
                            menuItem(label = "               - Create Proxy Plane -")
                            menuItem(label = "                       - X AXIS -")
                            menuItem(label = "                       - Y AXIS -")
                            menuItem(label = "                       - Z AXIS -")
                                                                                                                                                                                                                  
                            def mirrorChoice(axis):
                                if axis == "                       - X AXIS -":
                                    adbTransform.Transform(pm.selected()).mirror(axis='x')                                      
                                elif axis == "                       - Y AXIS -":
                                    adbTransform.Transform(pm.selected()).mirror(axis='y')                                             
                                elif axis == "                       - Z AXIS -":
                                    adbTransform.Transform(pm.selected()).mirror(axis='z')                                             
                                elif axis == "               - Choose Axis Mirror -":
                                    pass
                                else:
                                    pm.warning('Choice None Existant')
                                                                                                                                          
                            optionMenu(w=200, h=30,  cc = mirrorChoice )
                            menuItem(label = "               - Choose Axis Mirror -")
                            menuItem(label = "                       - X AXIS -")
                            menuItem(label = "                       - Y AXIS -")
                            menuItem(label = "                       - Z AXIS -")
                                                                                                        
                        with rowLayout( adj=True, numberOfColumns=2):
                            button(label="Get Node Type",  backgroundColor = colordic['green3'], c= pm.Callback(self.NodeType), w= 20, h=25 )
                            self.nodeName  = textField(pht= "Name the animation node",  tx='animCurve',)
                        with columnLayout( adj=True,rs=4):                                                        
                            button(label="DrivenKeys to Remap Value",  backgroundColor = colordic['grey1'],  c = pm.Callback(self.DkToRv)) 
                            
                        separator(h=2)
                        
                        with rowLayout( adj=True, numberOfColumns=1):
                            text(label="Follicules Options" , h=20,)

                        with rowLayout(adj=True, numberOfColumns=4):
                            text(label="Number")
                            self.folli  = floatField(v = 5, precision=1, showTrailingZeros=0)
                            text(label=" Radius ")
                            self.radius  = floatField(v = 1, precision=2,  showTrailingZeros=0)

                        self.folli_ctrl = checkBox(l='With Controls', v=True)        
                        button(label="Create Follicules",  backgroundColor = colordic['grey1'], c= pm.Callback(self.Folli)) 
                        button(label="Add Controls",  backgroundColor = colordic['grey1'], c= pm.Callback(self._addControls)) 
                
                    with frameLayout( cll = True, bgc=(0.202, 0.202, 0.202), labelVisible=True , cl = False, label = "OUTPUT WINDOW"):  
                        with columnLayout(adj=True, rs = 5):
                            text( label="Output Window" , h=20)                            
                            self.outputWin = textScrollList(w=150,h=60)
                            button(label="Refresh",  backgroundColor = colordic['grey2'], c= lambda *args:pm.textScrollList(self.outputWin,  edit=True, removeAll=True), h=25  )  

                    with frameLayout( cll = True, bgc=(0.202, 0.202, 0.202), labelVisible=True , cl = False, label = "SKINNING"):         
                        with columnLayout(adj=True, rs = 4):
                            button(label="Reset Skin",  backgroundColor = colordic['grey1'], c= Callback(adb.resetSkin) )
                            button(label="Replace Lattice",  backgroundColor = colordic['grey1'], c= Callback(adb.find_and_replace_lattices) )
                            button(label="Blend Two Groups",  backgroundColor = colordic['grey1'], c = pm.Callback(self._blend2grps) )
                            button(label="Wrap",  backgroundColor = colordic['grey1'], c=  pm.Callback(self._wrap) )
                            button(label="Wrap SetUp",  backgroundColor = colordic['grey1'], c = pm.Callback(self._wrapSetup) )

                    with frameLayout( cll = True, bgc=(0.202, 0.202, 0.202), labelVisible=True , cl = False, label = "CONTROLS"):         
                        with columnLayout(adj=True, rs = 4):                         
                            button(label="Get Curve Information",  backgroundColor = colordic['grey1'], c= Callback(adb.GetCurveShape) ) 
                            button(label="Combine Shapes",  backgroundColor = colordic['grey1'], c= lambda * agrs: adb.CombineShape(oNurbs = pm.selected()) )                                                          
                            button(label="Replace Shape",  backgroundColor = colordic['grey1'], c = pm.Callback(self._ReplaceShape)) 
                            
                                                                             
#-----------------------------------
#  SLOTS
#----------------------------------- 


# INFORMATION
#===================================== 
 
    
    def Type(self):
        '''Print selection Type '''
        sel = pm.selected()

        try:
            pm.textScrollList(self.outputWin,  edit=True, removeAll=True)
            for each in sel:            
                print (pm.objectType(pm.PyNode(each).getShape()) )                   
                pm.textScrollList(self.outputWin, edit=True, append = ['{}: {}'.format(each, pm.objectType(pm.PyNode(each).getShape()))])     
        except:
            pm.textScrollList(self.outputWin,  edit=True, removeAll=True)
            for each in sel:
                print (pm.objectType(pm.PyNode(each)))                  
                pm.textScrollList(self.outputWin, edit=True, append = ['{}: {}'.format(pm.objectType(pm.PyNode(each)))])             

                                
    def TypePymel(self):    
        sel = pm.selected()
        all_types = []
        pm.textScrollList(self.outputWin,  edit=True, removeAll=True)   
        for each in sel:
            try:
                _type = (type(pm.PyNode(each).getShape()) )
            except:  
                _type =_type = (type(pm.PyNode(each)))
            all_types.append(_type)                
            pm.textScrollList(self.outputWin, edit=True, append = ['{} : {}'.format(each,_type)]) 
            print _type  
        
   

# RIGGING
#===================================== 

    @undo
    def _pvGuide(self):
        if pm.checkBox(self.docString, q =True, v=True,) == False:
           adb.PvGuide(pm.selected()[0], pm.selected()[1])
        else:
            doc_string(adb.PvGuide)

    @undo
    def consTarget(self):
        ''' Get the target from a constraint object'''
        if pm.checkBox(self.docString, q =True, v=True,) == False:
            target = adb.ConsTarget(pm.selected())
            pm.textScrollList(self.outputWin,  edit=True, removeAll=True)        
            if target:
                pm.textScrollList(self.outputWin, edit=True, append = ['Targets are :']) 
                for each in target:
                    pm.textScrollList(self.outputWin, edit=True, append = ['        ' + str(each)])  
            else:
                pm.textScrollList(self.outputWin, edit=True, append = ['No Constraint'])  
        else:
            print(self.consTarget.__doc__)
            
    @undo
    def consDriver(self):
        sources = adb.ConsDriver(pm.selected())
        pm.textScrollList(self.outputWin,  edit=True, removeAll=True)        
        if sources:
            pm.textScrollList(self.outputWin, edit=True, append = ['Sources are :']) 
            for each in sources:
                pm.textScrollList(self.outputWin, edit=True, append = ['        ' + str(each)])          
        else:
            pm.textScrollList(self.outputWin, edit=True, append = ['No Constraint'])               
   

    @undo
    def DkToRv(self):
        '''Transform driven Key Nodes to Remap Value. Instruction : Put the nodeType in your function '''
            
        nodeType = pm.textField(self.nodeName , q=True, tx = True)
        # nodeType = 'animCurveUL'
        allNodes = pm.ls(type=nodeType)
        # pm.select(allNodes)

        pm.select(None)

        for each in allNodes:
            list = pm.listConnections(each+'.output') or []
            # print (list)
            if list == []:
                # pm.select(each, add = True)
                pm.delete(each)
                
        Nodes = pm.ls(type=nodeType)

        for eachKey in Nodes:

            ## get the controllers
            oControl = eachKey.inputs()[0]
            oDriven = eachKey.outputs()[0]
            
            ## get the control plugs (the actual attributes)
            paramControl = eachKey.inputs(plugs=True)[0]
            paramDriven = eachKey.outputs(plugs=True)[0]
            
            ## create a remapValue with the name of the old curve
            remapName = eachKey.split('__grp__')[0] + '_remap__'
            oMap = pm.createNode('remapValue', n=remapName)

            ## get the current value of the driven controller.

            "Set the inMin value on the last postion of the Set Driven Key, in this case is number 2"

            inMax = mc.getAttr(eachKey + ".keyTimeValue[0].keyTime")
            inMin = mc.getAttr(eachKey + ".keyTimeValue[1].keyTime")


            outMax = mc.getAttr(eachKey + ".keyTimeValue[0].keyValue")
            outMin = mc.getAttr(eachKey + ".keyTimeValue[1].keyValue")

            ## set the remapValue parameters to the same values as the Driven Key.
            oMap.inputMin.set(inMin)
            oMap.inputMax.set(inMax)
            oMap.outputMin.set(outMin)
            oMap.outputMax.set(outMax)

            paramControl.connect(oMap.inputValue)
            oMap.outValue.connect(paramDriven, force=True)

            pm.delete(eachKey)        


    @undo
    def NodeType(self):
        ''' Get the type of all connected nodes '''        
        oColl = pm.selected()
        Nodes = [x for x in pm.listConnections(oColl, et=True, skipConversionNodes = True,) ]
        NodeType = list(set([pm.objectType(x) for x in Nodes]))
        
        try:
            NodeType.remove("nodeGraphEditorInfo")
        except:
            pass

        if NodeType != []:
            print ('// Result: //')
            for types in NodeType:
                print ("     " + types)
                pm.textScrollList(self.outputWin,  edit=True, removeAll=True)
                pm.textScrollList(self.outputWin, edit=True, append = ["Node Type : " + types]) 

        else:
            print ('// Result: No Nodes //') 
            pm.textScrollList(self.outputWin,  edit=True, removeAll=True)
            pm.textScrollList(self.outputWin, edit=True, append = ['Result: No Nodes']) 


    @undo
    def Folli(self):
        if pm.checkBox(self.folli_ctrl, q =True, v=True,) == False:        
            radius = pm.floatField(self.radius , q=True, value = True)            
            countV = int(pm.floatField(self.folli , q=True, value = True))

            [adbFolli.Folli(1, countV, radius = radius, sub = x) for x in pm.selected()]
        
        else:
            radius = pm.floatField(self.radius , q=True, value = True)            
            countV = int(pm.floatField(self.folli , q=True, value = True))

            folli = [adbFolli.Folli(1, countV, radius = radius, sub = x) for x in pm.selected()]
            [x.addControls() for x in folli]

    @undo
    @changeColor()
    def _addControls(self):
        ''' add controls to the follicules '''
        oJoints = pm.selected()
        create_ctrls = flatList(sl.makeCtrls(sl.ball_shape))
        
        ## get the scale of the joint to add 0.5 on the scale of the controller
        [x.scaleX.set((pm.PyNode(oJoints[0]).radius.get()) + 0.5) for x in create_ctrls]
        [x.scaleY.set((pm.PyNode(oJoints[0]).radius.get()) + 0.5) for x in create_ctrls]
        [x.scaleZ.set((pm.PyNode(oJoints[0]).radius.get()) + 0.5) for x in create_ctrls]
        
        for joints, ctrls in zip (oJoints, create_ctrls):
            pm.parent(ctrls, pm.PyNode(joints).getParent() )       
                        
        for joints, ctrls in zip (oJoints, create_ctrls):
            pm.parent(joints,ctrls)
         
        [pm.makeIdentity(x, n=0, s=1, r=1, t=1, apply=True, pn=1) for x in create_ctrls]
        
        return create_ctrls
        
        

# SKINNING
#===================================== 

    @undo
    def _blend2grps(self):
        if pm.checkBox(self.docString, q =True, v=True,) == False:
           adb.blend2grps()
        else:            
            doc_string(adb.blend2grps)                   

    @undo
    def _wrap(self):
        if pm.checkBox(self.docString, q =True, v=True,) == False:
            adbWrap.wrapDeformer(_HiRez = pm.selected(), _LoRez=pm.selected())
        else:
            doc_string(adbWrap.wrapDeformer)

    @undo
    def _wrapSetup(self):
        if pm.checkBox(self.docString, q =True, v=True,) == False:
            adbWrapSetUp.wrapSetUp(_HiRez = pm.selected(), _LoRez=pm.selected())
        else:
            doc_string(adbWrapSetUp.wrapSetUp)


# CONTROLS
#===================================== 

    @undo
    def _ReplaceShape(self):
        if pm.checkBox(self.docString, q =True, v=True,) == False:
           adb.ReplaceShape()
        else:            
            doc_string(adb.ReplaceShape)  

    def ScaleVertex(self, scale):
        sub = pm.selected()
        adb.scaleVertex(scale, subject = sub) 

    def RotateVertex(self, scale):
        sub = pm.selected()
        adb.rotateVertex(scale, subject = sub)


# adbModule()
