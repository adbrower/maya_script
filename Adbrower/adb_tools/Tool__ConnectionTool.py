# ------------------------------------------------------------------------------------------------------
# Rigging Connection Tool
# -- Version 1.3.0    
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------------------------------------------------------

import maya.cmds as mc
import pymel.core as pm
import sys


#-----------------------------------
#  CLASS
#----------------------------------- 

class connectionTool():
    def __init__(self, **kwargs):
        
        self.version = "1.3.0"
        self.title = "adbrower - ConnectionTool"
        self.name = "ConnTool_win"

        self.Drivers = None
        self.Targets = None
        self.outputs = None
        self.inputs = None
        self.Tab = None
        
        self.ui()

    def ui(self):

        template = pm.uiTemplate('ExampleTemplate', force=True )
        template.define( pm.button, width=200, height=25)
        template.define( pm.frameLayout, mh=2, borderVisible=False, labelVisible=False )


        if pm.window(self.name, q=1, ex=1):
            pm.deleteUI(self.name)

        with pm.window(self.name, t= self.title + " v." + str(self.version), s=True, tlb = True, mxb=False) as self.win:

            with template:
                with pm.frameLayout(mw=4):                    
                    with pm.columnLayout(adj=True, rs = 10):
                            pm.text( label="MULTI ACTION TOOL" , h=30)
                            
                    with pm.frameLayout():
                        with pm.columnLayout(adj=True):

                            with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=2):
                                pm.button(label="Load Driver", w=255, backgroundColor = (0.17, 0.17, 0.17), c = pm.Callback(self.getDriverList))
                                pm.button(label="Load Target", w=256, backgroundColor = (0.17, 0.17, 0.17), c = pm.Callback(self.getTargetList))

                            with pm.rowLayout( numberOfColumns=4):
                                self.Drivers = pm.textScrollList( numberOfRows=8, allowMultiSelection=True, dcc = pm.Callback(self.DccD))
                                self.Targets = pm.textScrollList( numberOfRows=8, allowMultiSelection=True, dcc = pm.Callback(self.DccT)) 
                   
                            with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=6):
                                pm.button(label="Add", w=85, backgroundColor = (0.365, 0.365, 0.365), c = pm.Callback(self.AddDriver,))
                                pm.button(label="Replace ", w=80, backgroundColor =  (0.365, 0.365, 0.365),  c = pm.Callback(self. ReplaceDriver)) 
                                pm.button(label="Remove ", w=85, backgroundColor =(0.365, 0.365, 0.365),c = pm.Callback(self.RemoveDriver))
                                
                                pm.button(label="Add", w=85, backgroundColor = (0.365, 0.365, 0.365), c = pm.Callback(self.AddTarget))
                                pm.button(label="Replace ", w=80, backgroundColor = (0.365, 0.365, 0.365), c = pm.Callback(self. ReplaceTarget))
                                pm.button(label="Remove ", w=85, backgroundColor = (0.365, 0.365, 0.365), c = pm.Callback(self.RemoveTarget) )

                        with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=2):
                            pm.button(label="Refresh", w=255, backgroundColor = (0.202, 0.202, 0.202), c = pm.Callback(self.RefreshDriver))
                            pm.button(label="Refresh ", w=256, backgroundColor = (0.202, 0.202, 0.202),c = pm.Callback(self.RefreshTarget))
                             
                    with pm.frameLayout():
                        with pm.columnLayout(adj=True, rs = 10):
                            pm.separator() 
                            pm.text( label="QUICK  CONNECTION" , h=15)        
                            pm.separator()   
                            
                        with pm.columnLayout(adj=True):                               
                            with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=4):
                                pm.button(label="Translate to Translate ", w=170, h=30, bgc = (0.602, 0.602, 0.602), c = pm.Callback(self.QuickConnT))                                                                                  
                                pm.button(label="Rotate to Rotate", w=170, h=30, bgc = (0.602, 0.602, 0.602), c = pm.Callback(self.QuickConnR)) 
                                pm.button(label="Scale to Scale", w=170, h=30, bgc = (0.602, 0.602, 0.602), c = pm.Callback(self.QuickConnS))                             
                            
                            pm.separator(h=10,w=500)                            
                            pm.text( label="MANUEL CONNECTION" , h=25, )                            
                            pm.separator(h=10,w=500)
                                        
                            with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=6):
                                pm.separator(w=51, vis=False)
                                pm.button(label="Add Outputs", w=190, backgroundColor = (0.202, 0.202, 0.202), c = pm.Callback(self.AddOutputs))
                                pm.separator(w=40, vis=False)
                                pm.button(label="Add Inputs ", w=220, backgroundColor = (0.202, 0.202, 0.202), c = pm.Callback(self.AddInputs))

                            with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=5):
                                pm.text( label="  Output   ",align = 'left')
                                self.Output1  = pm.textFieldGrp(w=190, pht= "Type output", columnWidth1=189)

                                pm.text( label="   Input  ",align = 'left')
                                self.Input1  = pm.textFieldGrp(w=220, pht= "Type input", columnWidth1=219)

                        with pm.columnLayout(adj=True, rs = 10):                    
                                with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=5):
                                    pm.text( label="  Output   ",align = 'left')
                                    self.Output2  = pm.textFieldGrp(w=190, pht= "Type output", columnWidth1=189)

                                    pm.text( label="   Input  ",align = 'left')
                                    self.Input2  = pm.textFieldGrp(w=220, pht= "Type input", columnWidth1=219)

                        with pm.columnLayout(adj=True, rs = 5):                    
                                with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=5):
                                    pm.text( label="  Output   ",align = 'left')                                                                      
                                    self.Output3  = pm.textFieldGrp(w=190, pht= "Type output", columnWidth1=189)                                                                                                         
                                    pm.text( label="   Input  ",align = 'left')
                                    self.Input3  = pm.textFieldGrp(w=220, pht= "Type input", columnWidth1=219)

                        pm.separator()  
                    
                    with pm.frameLayout():
                        with pm.formLayout():                                                   
                            with pm.tabLayout(innerMarginWidth=5, innerMarginHeight=5) as tabs:                            
                                with pm.frameLayout()as child1:
                                    with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=2):
                                        pm.button(label="Connect One to Many ", w=256, h=30, bgc = (0.17, 0.17, 0.17),c = pm.Callback(self.ConAll))                                                                                  
                                        pm.button(label="Connect Each Other", w=256, h=30, bgc = (0.17, 0.17, 0.17),c = pm.Callback(self.pairing_AttrConn)) 

                                with pm.frameLayout()as child2:
                                    with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=4):                                        
                                        pm.button(label="Parent + Scale", w=340, h=30, bgc = (0.349, 0.478, 0.349),c = pm.Callback(self.ParentScaleCons))  
                                        pm.button(label="Parent Constraint", w=170, h=30, bgc = (0.17, 0.17, 0.17),c = pm.Callback(self.ParentCons))  

                                    with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=6):
                                        pm.button(label="Point Constraint ", w=170, h=30, bgc = (0.17, 0.17, 0.17),c = pm.Callback(self.PointCons))                                                                                  
                                        pm.button(label="Scale Constraint ", w=170, h=30, bgc = (0.17, 0.17, 0.17),c = pm.Callback(self.ScaleCons))                                                                                  
                                        pm.button(label="Orient Constraint ", w=170, h=30, bgc = (0.17, 0.17, 0.17),c = pm.Callback(self.OrientCons))                                                                                  
 
                                with pm.frameLayout()as child3:  
                                    with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=6):
                                        pm.button(label="BlendShapes", w=170, h=30, bgc = (0.349, 0.478, 0.349),c = pm.Callback(self.BlendShape_connect))    
                                        pm.button(label="Parent",  w=170, h=30, bgc = (0.349, 0.478, 0.349), c = pm.Callback(self.parent_2List)) 
                                        pm.button(label="Match Transform",  w=170, h=30, bgc = (0.349, 0.478, 0.349), c = pm.Callback(self.MatchTransformRT))  
                                        pm.popupMenu()
                                        pm.menuItem('Match Postion', c = pm.Callback(self.MatchTransformRT, False, True))                                                                             
                                        pm.menuItem('Match Rotation', c = pm.Callback(self.MatchTransformRT, True, False))   
                            
                                                                                           
                                pm.tabLayout( tabs, edit=True, tabLabel=((child1, 'BY CONNECTIONS'),(child2, 'BY CONSTRAINTS'),(child3, 'OTHER OPTIONS')) )

                with pm.frameLayout( cll = True, bgc=(0.202, 0.202, 0.202), labelVisible=True , cl = True, label = "Break Connection", cc =pm.Callback(self.winResize) ) as self.BC_layout:                    
                    with pm.frameLayout():
                        with pm.columnLayout(adj=True,rs = 15):                                    
                            pm.text(label = 'Select the Driver from which you want to break connection', al = 'center')                  
                              
                            with pm.rowLayout(columnWidth3=(0, 0, 0),  numberOfColumns=6):
                                    pm.button(label="Add Connection", w=100, backgroundColor = (0.202, 0.202, 0.202), c = pm.Callback(self.AddOutputsBC))                               
                                    self.BConn  = pm.textFieldGrp( pht= "Type output")
                                    pm.text( label="   ",align = 'left')
                                    pm.button(label="Break Connection", w=150, backgroundColor = (0.602, 0.602, 0.602), c = pm.Callback(self.BreakConnection))




#-----------------------------------
#  FUNCTIONS
#----------------------------------- 


    def winResize(self):
        val = pm.frameLayout(self.BC_layout, q = True, cl = True)                   
        self.win.setHeight(400)



    def getList(self):                
        '''Print my selection's names into a list'''    
        
        oColl = pm.selected()

        for each in oColl:
            try:        
                mylist = [ x.name() for x in pm.selected()]
            except:
                mylist = [ x.getTransform().name() for x in pm.selected()]

        return mylist

#-----------------------------------
#  SLOTS
#-----------------------------------  

    def getDriverList(self): 
        try:                       
            pm.textScrollList(self.Drivers,  edit=True, removeAll=True) 
            self.DriverList  = []
            
            result2 = self.getList()
            self.DriverList = [x for x in result2]            
            pm.textScrollList(self.Drivers, edit=True, append = self.DriverList  )            
            print (self.DriverList ) 
  
        except:
            pm.warning("Nothing Selected!")


    def getTargetList(self): 
        try:                       
            pm.textScrollList(self.Targets,  edit=True, removeAll=True) 
            self.TargetList =[]
            
            result1 = self.getList()
            self.TargetList = [x for x in result1]

            pm.textScrollList(self.Targets, edit=True, append = self.TargetList  )
            print (self.TargetList)                              
        except:
            pm.warning("Nothing Selected!")

    def BlendShape_connect(self):
        Driver = self.DriverList
        Targets = self.TargetList
 
        def connect_bls(source,target):
            '''
            This function connects input|source to output|target with a blendShape.
            If the source and target are of type list, it will blendShape each of those lists together.
            Else it will take the children of each and blendShape those together
            '''
            
            # Define Variable type
            if isinstance(source, list) and isinstance(target, list):
                inputs = [x for x in source]
                outputs = [x for x in target]   
            else:    
                # get all children in group    
                inputs = pm.listRelatives(source, children = True,path = True)
                outputs = pm.listRelatives(target, children = True, path = True)

            for _input, _output in zip(inputs,outputs):
                blendShapeNode = ('{}_BLS'.format(_input)).split('|')[-1]
                if not mc.objExists(blendShapeNode):
                    pm.blendShape(_input, _output, name = blendShapeNode, o = "world", w = [(0, 1.0)], foc = False)
                else:
                    pm.warning('{} already Exist'.format(blendShapeNode))

            sys.stdout.write('// Result: Connection Done // \n ')   
        
        connect_bls(Driver,Targets)
                             

    def MatchTransformRT(self, rot, pos):
        '''Match the Rotation and Position of 2 objects '''

        Driver = self.DriverList
        Targets = self.TargetList

        if len(Driver) != len(Targets):            
            for oTargets in Targets:
                mc.matchTransform(oTargets,Driver,rot=rot, pos=pos)  
        else:            
            for oDriver, oTargets in zip (Driver,Targets):
                mc.matchTransform(oTargets,oDriver,rot=rot, pos=pos)   
        
        sys.stdout.write('// Result: Match Transformed! //')          


    def PointCons(self):
        '''Match the Rotation and Position of 2 objects '''
        
        Driver = self.DriverList
        Targets = self.TargetList
        
        if len(Driver) != len(Targets):
            for oTargets in Targets:
                pm.pointConstraint(Driver,oTargets, mo = True)         
        else:
            for oDriver, oTargets in zip (Driver,Targets):
                pm.pointConstraint(oDriver,oTargets, mo = True) 
        
        sys.stdout.write('// Result: Point Constraint applied //') 

    def ScaleCons(self):
        '''Match the Rotation and Position of 2 objects '''

        Driver = self.DriverList
        Targets = self.TargetList

        if len(Driver) == len(Targets):

            for oDriver, oTargets in zip (Driver,Targets):
                pm.scaleConstraint(oDriver,oTargets, mo = True) 

        else:
            for oTargets in Targets:
                pm.scaleConstraint(Driver,oTargets, mo = True) 
        
        sys.stdout.write('// Result: Scale Constraint applied //') 


    def ParentCons(self):
        Driver = self.DriverList
        Targets = self.TargetList
        
        if len(Driver) != len(Targets):
            for oTargets in Targets:
                pm.parentConstraint(Driver,oTargets, mo = True) 

        else:
            for oDriver, oTargets in zip (Driver,Targets):
                pm.parentConstraint(oDriver,oTargets, mo = True) 

        sys.stdout.write('// Result: Parent Constraint applied //') 
    
    def OrientCons(self):
        Driver = self.DriverList
        Targets = self.TargetList
        
        if len(Driver) != len(Targets):
            for oTargets in Targets:
                pm.orientConstraint(Driver,oTargets, mo = False) 

        else:
            for oDriver, oTargets in zip (Driver,Targets):
                pm.orientConstraint(oDriver,oTargets, mo = False) 
        
        sys.stdout.write('// Result: Orient Constraint applied //') 

    def ParentScaleCons(self):
        '''Match the Rotation and Position of 2 objects '''

        Driver = self.DriverList
        Targets = self.TargetList

        if len(Driver) != len(Targets):            
            for oTargets in Targets:
                pm.parentConstraint(Driver,oTargets, mo = True) 
                pm.scaleConstraint(Driver,oTargets, mo = True) 
        else:
            for oDriver, oTargets in zip (Driver,Targets):
                pm.parentConstraint(oDriver,oTargets, mo = True) 
                pm.scaleConstraint(oDriver,oTargets, mo = True) 
        
        sys.stdout.write('// Result: Parent + Scale Constraint applied //') 

    def pairing_AttrConn(self):
        '''Pairing 2 list by connecting attributs - There is 1 Driver per Driven  '''         
        try:  
            Driver = self.DriverList
            Targets = self.TargetList
            
            self.outputs1 = pm.textFieldGrp(self.Output1, q = True, tx = True)
            self.inputs1 = pm.textFieldGrp(self.Input1, q = True, tx = True)

            self.outputs2 = pm.textFieldGrp(self.Output2, q = True, tx = True)
            self.inputs2 = pm.textFieldGrp(self.Input2, q = True, tx = True)            

            self.outputs3 = pm.textFieldGrp(self.Output3, q = True, tx = True)
            self.inputs3 = pm.textFieldGrp(self.Input3, q = True, tx = True)            

                   
            for oDriver, oTargets in zip (Driver,Targets):
                try:
                    pm.connectAttr( str(oDriver)+'.'+str(self.outputs1), str(oTargets)+'.'+str(self.inputs1) )            
                except RuntimeError:
                    pass

                try:
                    pm.connectAttr( str(oDriver)+'.'+str(self.outputs2), str(oTargets)+'.'+str(self.inputs2) )                
                except RuntimeError:
                    pass

                try:
                    pm.connectAttr( str(oDriver)+'.'+str(self.outputs3), str(oTargets)+'.'+str(self.inputs3) )                
                except RuntimeError:
                    pass

            sys.stdout.write('// Result: Connect each other //') 
        except:
            pm.warning("Fulfill the UI!")
 
    def ConAll(self):        
     
        try:                
            Driver =  self.DriverList[0]
            Targets = self.TargetList    

            self.outputs1 = pm.textFieldGrp(self.Output1, q = True, tx = True)
            self.inputs1 = pm.textFieldGrp(self.Input1, q = True, tx = True)

            self.outputs2 = pm.textFieldGrp(self.Output2, q = True, tx = True)
            self.inputs2 = pm.textFieldGrp(self.Input2, q = True, tx = True)            

            self.outputs3 = pm.textFieldGrp(self.Output3, q = True, tx = True)
            self.inputs3 = pm.textFieldGrp(self.Input3, q = True, tx = True)            

            for each in Targets:            
                pm.connectAttr(str(Driver)+'.'+str(self.outputs1), str(each)+'.'+str(self.inputs1))

                try:
                    pm.connectAttr(str(Driver)+'.'+str(self.outputs2), str(each)+'.'+str(self.inputs2))
                 
                except:
                    pass

                try:
                    pm.connectAttr(str(Driver)+'.'+str(self.outputs3), str(each)+'.'+str(self.inputs3))           
                except:
                    pass 

            sys.stdout.write('// Result: Connect one to many//') 
        except:
            pm.warning("Fulfill the UI")

    def auto_Connect(self):
        Driver = self.DriverList
        Targets = self.TargetList

        if len(Driver) != len(Targets):  
            self.ConAll()
            
        else:
            self.pairing_AttrConn

    def RefreshDriver(self):
        pm.textScrollList(self.Drivers,  edit=True, removeAll=True) 
        self.DriverList = []

    def RefreshTarget(self):
        pm.textScrollList(self.Targets,  edit=True, removeAll=True) 
        self.TargetList = []


    def AddDriver(self):
        try: 
            result2 = self.getList()
            tempList = [x for x in result2]    
            pm.textScrollList(self.Drivers, edit=True, append = tempList )           
            pm.textScrollList(self.Targets, q=True, sii=-1)     
                   
        ## list management                    

            self.DriverList.extend(tempList)
            
        except AttributeError :  
            pass     

    def AddTarget(self):
        try:
            result2 = self.getList()
            tempList = [x for x in result2]      
            pm.textScrollList(self.Targets, edit=True, append = tempList )           
            
         ## list management           
            nb = len(tempList)            
            for i in range(0,nb):
                self.TargetList.append(tempList[i])

        except AttributeError :  
            pass   


    def RemoveDriver(self):        
        selectItem = mc.pm.textScrollList(self.Drivers, q=True, selectItem=True)
        pm.textScrollList(self.Drivers, edit=True, ri = selectItem )

        ## list management
        pm.select(selectItem)

        rmv = pm.selected()
        tempList = [x for x in rmv]  
       
        nb = len(tempList)            
        for i in range(0,nb):
       
            self.DriverList.remove(tempList[i])
            
        pm.select(None)


    def RemoveTarget(self):
        selectItem = mc.pm.textScrollList(self.Targets, q=True, selectItem=True)
        pm.textScrollList(self.Targets, edit=True, ri = selectItem )

        ## list management
        pm.select(selectItem)

        rmv = pm.selected()
        tempList = [x for x in rmv]  
       
        nb = len(tempList)            
        for i in range(0,nb):       
            self.TargetList.remove(tempList[i])                    
        pm.select(None)       


    def ReplaceDriver(self):
        try:
            newSel = self.getList()        
            selectItem = mc.pm.textScrollList(self.Drivers, q=True, selectItem=True)
            pm.textScrollList(self.Drivers, edit=True, append = newSel  )
            pm.textScrollList(self.Drivers, edit=True, ri = selectItem )

            ## list management
            pm.select(selectItem)
            rpl = pm.selected()
            tempList = [x for x in rpl]
           
            nb = len(tempList)            
            for i in range(0,nb):
           
                self.DriverList.remove(tempList[i])
            
            nb2 = len(newSel)            
            for i in range(0,nb2):
           
                self.DriverList.append(newSel[i])                   
            pm.select(None)      

        except: 
            pass 



    def ReplaceTarget(self):
        try:
            newSel = self.getList()        
            selectItem = mc.pm.textScrollList(self.Targets, q=True, selectItem=True)
            pm.textScrollList(self.Targets, edit=True, append = newSel  )
            pm.textScrollList(self.Targets, edit=True, ri = selectItem )

            ## list management
            pm.select(selectItem)
            rpl = pm.selected()
            tempList = [x for x in rpl] 
           
            nb = len(tempList)            
            for i in range(0,nb):
           
                self.TargetList.remove(tempList[i])
            
            nb2 = len(newSel)            
            for i in range(0,nb2):
           
                self.TargetList.append(newSel[i])                               
            pm.select(None)      
        except: 
            pass 


    def BreakConnection(self):
        try:            
            selAttrs = [ x for x in pm.channelBox("mainChannelBox", q=1, selectedMainAttributes = 1)]                      
            param = [x for x in selAttrs]            
            sub = len(pm.selected())
           
            for i in range(0,sub):
                for each in param:                
                    sub1 = str(pm.selected()[i])
                    sub2 = str(each)
     
                    fullsub = sub1+'.'+sub2            
                    attribute = str(fullsub)

                    destinationAttrs = mc.listConnections(attribute, plugs=True, source=False) or []
                    sourceAttrs = mc.listConnections(attribute, plugs=True, destination=False) or []
     
                    for destAttr in destinationAttrs:
                        mc.disconnectAttr(attribute, destAttr)
                    for srcAttr in sourceAttrs:
                        mc.disconnectAttr(srcAttr, attribute)
                        
            sys.stdout.write('// Result: Break Connection //')
             
        except IndexError: 
            pass 

    def parent_2List(self):
        '''Pairing 2 list by parenting - There is 1 Driver per Driven  '''

        Drivers = self.DriverList
        Targets = self.TargetList
        
        if len(Drivers) == len(Targets):
            for oDriver, oTargets in zip (Drivers,Targets):
                pm.parent(oTargets,oDriver)

        else:
            pm.select(Targets)
            pm.select(Drivers, add=True)
            pm.parent(pm.selected()[0:-1],pm.selected()[-1])
            pm.select(None)

        sys.stdout.write('// Result: Parent pm.button applied //') 

    def DccD(self):
        selectItem = mc.pm.textScrollList(self.Drivers, q=True, selectItem=True)
        pm.select(selectItem, r= True)

    def DccT(self):
        selectItem = mc.pm.textScrollList(self.Targets, q=True, selectItem=True)
        pm.select(selectItem, r= True)

  
    def QuickConnT(self):
        try:
            Drivers = self.DriverList 
            Targets = self.TargetList 
            
            for oDriver, oTargets in zip (Drivers,Targets):
                pm.PyNode(oDriver).tx >> pm.PyNode(oTargets).tx
                pm.PyNode(oDriver).ty >> pm.PyNode(oTargets).ty
                pm.PyNode(oDriver).tz >> pm.PyNode(oTargets).tz

            sys.stdout.write('// Result: Connect Translate to Translate //') 
        except AttributeError:
            pass
 
    def QuickConnR(self):
        try:
            Drivers = self.DriverList 
            Targets = self.TargetList 
            
            for oDriver, oTargets in zip (Drivers,Targets):
                pm.PyNode(oDriver).rotateX >> pm.PyNode(oTargets).rotateX
                pm.PyNode(oDriver).rotateY >> pm.PyNode(oTargets).rotateY
                pm.PyNode(oDriver).rotateZ >> pm.PyNode(oTargets).rotateZ
            
            sys.stdout.write('// Result: Connect Rotate to Rotate //') 
        except AttributeError:
            pass 
 
    def QuickConnS(self):
        try:
            Drivers = self.DriverList 
            Targets = self.TargetList 
            
            for oDriver, oTargets in zip (Drivers,Targets):
                pm.PyNode(oDriver).scaleX >> pm.PyNode(oTargets).scaleX
                pm.PyNode(oDriver).scaleY >> pm.PyNode(oTargets).scaleY
                pm.PyNode(oDriver).scaleZ >> pm.PyNode(oTargets).scaleZ
            
            sys.stdout.write('// Result: Connect Scale to Scale //') 
        except AttributeError:
            pass  

 
    def AddOutputs(self):        
        try:
            selAttrs = [ x for x in pm.channelBox("mainChannelBox", q=1, selectedMainAttributes = 1)]
            
            ## UI management
            self.outputs1 = pm.textFieldGrp(self.Output1, e = True, tx = selAttrs[0])
            
            try:
                self.outputs2 = pm.textFieldGrp(self.Output2, e = True, tx = selAttrs[1])
            except IndexError:
                pass
                
            try:
                self.outputs3 = pm.textFieldGrp(self.Output3, e = True, tx = selAttrs[2])
            except IndexError:
                pass

        except TypeError:
            pass

 
    def AddInputs(self):        
        try:
            selAttrs = [ x for x in pm.channelBox("mainChannelBox", q=1, selectedMainAttributes = 1)]
            
            ## UI management                               
            self.inputs1 = pm.textFieldGrp(self.Input1, e = True, tx = selAttrs[0])
            try:
                self.inputs2 = pm.textFieldGrp(self.Input2, e = True, tx = selAttrs[1]) 
            except IndexError:
                pass
            
            try:
                self.inputs3 = pm.textFieldGrp(self.Input3, e = True, tx = selAttrs[2])    
            except IndexError:
                pass 
        
        except TypeError:
            pass


    def AddOutputsBC(self):
        try:
            selAttrs = [ x for x in pm.channelBox("mainChannelBox", q=1, selectedMainAttributes = 1)]

            self.BConns  = pm.textFieldGrp( self.BConn ,e = True, tx = str(selAttrs).replace("u'","").replace("'"," ").replace("["," ").replace("]"," "))

        except TypeError:
            pm.warning("Select Attribute in the Channel Box")


# connectionTool()