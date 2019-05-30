# ------------------------------------------------------------------------------------------------------
# Double Constraints Checking Script
# -- Version 1.0.0    
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# ------------------------------------------------------------------------------------------------------

from pymel.core import * 
import maya.cmds as mc
import pymel.core as pm

import maya.mel as mm

#custom module
from CollDict import colordic

#-----------------------------------
#  DECORATORS
#----------------------------------- 
from adbrower import undo


#-----------------------------------
#  CLASS
#----------------------------------- 


class CheckUp():
    """This is a checkup Tool  """
    def __init__(self, **kwargs):
       
        self.name = "CheckUp_win" 
        self.oGeo = pm.selected()
        self.ParentConstraints = None
        self.ScaleConstraints = None
        self.sourceNodes = []
        self.sourceNodes0 = []
        self.targetNodes = None
        self.constraints = None   
        
        self.NewRestTranslate = None
        self.OriRestTranslate = None        
        
        self.NewRestTranslateR = None
        self.OriRestTranslateR = None
        
        self.outputWin = None
        
        self.ui()


    def ui(self):

        template = uiTemplate('ExampleTemplate', force=True )
        template.define( button, width=200, height=32)
        template.define( frameLayout, borderVisible=False, labelVisible=False)

        if pm.window(self.name, q=1, ex=1):
            pm.deleteUI(self.name)

        with window(self.name, t= "adbrower - Check Tool v2.0" , tlb = True, s=True) as self.win:

            with template:
                with frameLayout():
                    with columnLayout(adj=True, rs = 1):
                        text( label="CHECK UP" , h=30,)
                        
                        with rowLayout(adj=True,  numberOfColumns=1):
                            button(label="Constraint Check", backgroundColor = colordic['grey'], c= pm.Callback(self.ConstraintChek) )                        
                        
                        with rowLayout(adj=True,  numberOfColumns=1):
                            button(label="Controls Check",  backgroundColor = colordic['grey'], c= pm.Callback(self.FindCtrl)  )                        

                        with rowLayout(adj=True,  numberOfColumns=1):
                            button(label="NgSking Node Check",  backgroundColor = colordic['grey'], c= pm.Callback(self.NgSkin)  )   

                        with rowLayout(adj=True,  numberOfColumns=1):
                            button(label="Lock and Hide",  backgroundColor = colordic['grey'], c= pm.Callback(self.LockHide) )

                        with rowLayout(numberOfColumns=2):
                            button(label="Find Mesh",  backgroundColor = colordic['grey'], c= pm.Callback(self.FindMesh), w = 128 )  
                            button(label="Repair Mesh",  backgroundColor = colordic['grey'], c= pm.Callback(self.RepairMesh), w =128 )  
                            
                        with rowLayout(adj=True,  numberOfColumns=1):
                            button(label="Check All at Once",  backgroundColor = colordic['grey2'], c= pm.Callback(self.CheckAll)  )                           
                            
                        with rowLayout(adj=True,  numberOfColumns=1):
                            button(label="Chris's Clean Up",  backgroundColor = colordic['green3'], c= pm.Callback(self.ChrisCleanUp)  )   
                        
                with frameLayout():
                    with columnLayout(adj=True, rs = 5):
                        text( label="Output Window" , h=10)
                        
                        with rowLayout(adj=True,  numberOfColumns=1):
                            self.outputWin = textScrollList(h=90)

                        with rowLayout(adj=True,  numberOfColumns=1):
                            button(label="Refresh",  backgroundColor = colordic['grey1'], c= lambda *args:pm.textScrollList(self.outputWin,  edit=True, removeAll=True), h=25  )   

                    with frameLayout( cll = True, bgc=(0.202, 0.202, 0.202), labelVisible=True , cl = True, cc =pm.Callback(self.winColl), label = "Double Constraint Check") as self.BC_layout:
                        with frameLayout():
                            with columnLayout(adj=True, rs = 1):
                                
                                with rowLayout(adj=True,  numberOfColumns=1):
                                    button(label="Check Model", backgroundColor = (0.369, 0.441, 0.333), c = pm.Callback(self.GetSubject) )
                                
                                with rowLayout(adj=True,  numberOfColumns=1):
                                    button(label="Find Sources",  backgroundColor =(0.213, 0.265, 0.219), c = pm.Callback(self.FindSources) )
                                
                                with rowLayout(adj=True,  numberOfColumns=1):
                                    button(label="Find Main Source",  backgroundColor = colordic['green'], c = pm.Callback(self.FindSourcesMainSource) )
                                
                                with rowLayout(adj=True,  numberOfColumns=1):
                                    button(label="Repair All",  backgroundColor = colordic['blue'], c = pm.Callback(self.Repair2Conn) )                        
                                
                                
                                                  
#-----------------------------------
#  SLOTS
#----------------------------------- 

    def winColl(self):
        val = pm.frameLayout(self.BC_layout, q = True, cl = True)
        self.win.setHeight(200)

    """ Publish Check Up """ 

    def ConstraintChek(self):
        """ Find all constraints under the 'x__model__grp' and puts its under a new group"""

        pm.select(None)
        def cleaninMesh():
            '''Puts all the meshes constraints under a group '''
            
            cons = "*msh**Constraint1*"
            oParent = "*x__constraints__grp__*"
            cons2 = "x__model__grp**Constraint1*"
            parentGrp = "x__additive_rig__grp__"

            if mc.objExists(cons):
                pm.select(cons)
            else:
                pass
            
            if mc.objExists(cons2):
                pm.select(cons2)
            else:
                pass

            oColl = pm.PyNode('x__constraints__grp__').getChildren(ad=True, type='constraint')
            pm.select(oColl, d =1)

            oChildren = pm.selected()
            pm.parent(oChildren,oParent)
            # pm.parent(consGrp,parentGrp)
               
        try:
            if mc.objExists('*x__constraints__grp__*'):

                cleaninMesh()    
                    
            else:
                 pm.group(parent = "x__additive_rig__grp__", n = 'x__constraints__grp__')
                 cleaninMesh() 

        except RuntimeError:  
            print ('// Result: //' )        
            print ('// Result: No constraints under meshes //')      


    def FindMesh(self):
        
        pm.select(None)
                 
        stringV = []
        Mesh = []
        FinalMeshSel = []
               
        all_msh = pm.PyNode('x__model__grp__').getChildren()

        ## unlock parameter     
        attrLock = [x.listAttr(cb=False,l=True) for x in all_msh]
        all_attrLock = [x for i in attrLock for x in i]

        print (all_attrLock)

        for attr in all_attrLock:
            attr.unlock()
     
        translation = [x.getTranslation(space='world') for x in all_msh]

        for each in translation:
            stringV.append(str(each))
            
        for mesh, trans in zip (all_msh,stringV):

            if trans == '[0.0, 0.0, 0.0]':
                pass
                
            else:
                Mesh.append(mesh) 
                # print (mesh, trans)


        if Mesh:
            for mesh in Mesh:            
                ConstraintNode = [ x for x in pm.listConnections(mesh+'.tx', s=1)]
                
                if ConstraintNode:
                    for constraint in ConstraintNode:           
                       self.OriRestTranslate = [ x.restTranslate.get() for x in ConstraintNode]
           

            ## AT MESH TO 0,0,0
            
            for mesh in Mesh:
                old_trans = pm.PyNode(mesh).translate.get()
                pm.PyNode(mesh).translate.set(0,0,0)
                
                ConstraintNode = [ x for x in pm.listConnections(mesh+'.tx', s=1)]
                
                if ConstraintNode:
                    for constraint in ConstraintNode:           
                       self.NewRestTranslate = [ x.restTranslate.get() for x in ConstraintNode]

                for valueOri, valueNew in zip (self.OriRestTranslate, self.NewRestTranslate):
                    
                    if valueOri != valueNew:
                        FinalMeshSel.append(mesh)
                        print ('old:' + str(valueOri), 'new:' +str( valueNew))
                
                pm.PyNode(mesh).translate.set(old_trans)

                ## relock param
                for attr in all_attrLock:
                    attr.lock()
            
                        
            if FinalMeshSel != []:
                pm.textScrollList(self.outputWin, edit=True, append = ['    Warning: Somes meshes are not at 0,0,0 ']) 
                pm.warning('Warning: Somes meshes are not at 0,0,0')
                pm.select(FinalMeshSel)
                
                  
            else:
                pm.textScrollList(self.outputWin, edit=True, append = ['Result: All mesh are at 0,0,0']  ) 
                print  ('// Result: //')                
                print  ('// Result: All mesh are at 0,0,0 //')

        else:
            pm.textScrollList(self.outputWin, edit=True, append = ['Result: All mesh are at 0,0,0']  ) 
            print  ('// Result: //')
            print  ('// Result: All mesh are at 0,0,0 //')



    def RepairMesh(self):
        """repair """  

        pm.select(None)
                 
        stringV = []
        MeshR = []
        FinalMeshR = []
        
        all_msh = pm.PyNode('x__model__grp__').getChildren()

        ## unlock parameter     
        attrLock = [x.listAttr(cb=False,l=True) for x in all_msh]
        all_attrLock = [x for i in attrLock for x in i]

        print (all_attrLock)

        for attr in all_attrLock:
            attr.unlock()

        ## get translations
        translation = [x.getTranslation(space='world') for x in all_msh]

        for each in translation:
            stringV.append(str(each))
            
        for mesh, trans in zip (all_msh,stringV):

            if trans == '[0.0, 0.0, 0.0]':
                pass
                
            else:
                MeshR.append(mesh) 
                # print (mesh, trans)

        for mesh in MeshR:            
            ConstraintNode = [ x for x in pm.listConnections(mesh+'.tx', s=1)]
            
            if ConstraintNode:
                for constraint in ConstraintNode:           
                   self.OriRestTranslateR = [ x.restTranslate.get() for x in ConstraintNode]
       

        ## AT MESH TO 0,0,0
        
        for mesh in MeshR:
            old_trans = pm.PyNode(mesh).translate.get()
            pm.PyNode(mesh).translate.set(0,0,0)
            
            ConstraintNode = [ x for x in pm.listConnections(mesh+'.tx', s=1)]
            
            if ConstraintNode:
                for constraint in ConstraintNode:           
                   self.NewRestTranslateR = [ x.restTranslate.get() for x in ConstraintNode]

            for valueOri, valueNew in zip (self.OriRestTranslateR, self.NewRestTranslateR):
                
                if valueOri != valueNew:
                    FinalMeshR.append(mesh)
            
            pm.PyNode(mesh).translate.set(old_trans)
                

        ## repair
        pm.select(None)
        pm.select(FinalMeshR)
        self.ResetAttr()
        
        for mesh in FinalMeshR:            
            ConstraintNode = [ x for x in pm.listConnections(mesh+'.tx', s=1)]

                
            if ConstraintNode:
                for constraint in ConstraintNode:           
                   Ctrl_list = [ x for x in pm.listConnections(constraint+'.target[0].targetTranslate', s=1)]

            pm.select(FinalMeshR)
            self.rmvCons()

                  
            for ctrl in Ctrl_list:
                pm.parentConstraint(ctrl,mesh, maintainOffset=1)    
                pm.scaleConstraint(ctrl,mesh, maintainOffset=1)    
   

            ## relock param
            for attr in all_attrLock:
                attr.lock()        

        

    ### CHECK 3 ################################
    def LockHide(self):
        """Lock and Hide scale and visibility for all '__ctrl__' """  
            
        ctrlColl = pm.ls("*__ctrl__")

        for ctrl in ctrlColl:
            pm.PyNode(ctrl).v.set(keyable=False, cb=False)
            pm.PyNode(ctrl).sx.set(keyable=False, cb=False, lock=True)
            pm.PyNode(ctrl).sy.set(keyable=False, cb=False, lock=True)
            pm.PyNode(ctrl).sz.set(keyable=False, cb=False, lock=True)
        
        pm.textScrollList(self.outputWin, edit=True, append = ['Result: Controls has been Lock and Hide']) 
        print "// Result: //"
        print "// Result: Controls has been Lock and Hide //"
 


    ### CHECK 4 ################################ 
    def LightsLocator(self):
        if mc.objExists('*x__light_constraint__grp__*'):
            
            pm.textScrollList(self.outputWin, edit=True, append = ['Result: Contains a light grp '])
            print ("// Result:  //")
            print ("// Result: Contains a light grp //")

        else:
            pm.textScrollList(self.outputWin, edit=True, append = ['Warning: NO LIGHT CONSTRAINT GROUP']  )
            pm.warning('Warning: NO LIGHT CONSTRAINT GROUP')




    ### CHECK 5 ################################ 
    def FindCtrl(self):
        """Find all ctrl who translation are not to 0,0,0 values"""

        stringVC = []
        FinalCtrl = []


        all_ctrls = pm.ls("*__ctrl__")
        Ctranslation = [x.getTranslation() for x in all_ctrls]


        for each in Ctranslation:
            stringVC.append(str(each))
            

        for ctrl, values in zip (all_ctrls,stringVC):
            

            if values == '[0.0, 0.0, 0.0]':
                pass
                
            else:
                FinalCtrl.append(ctrl)
                print (ctrl, values)             
                    
        
        if FinalCtrl:
            pm.warning("Warning: Somes ctrls are not at 0,0,0")
            
            pm.textScrollList(self.outputWin, edit=True, append = ['    Warning: Somes ctrls are not at 0,0,0']  ) 
            pm.select(FinalCtrl, add = True)   
        else:
            
            pm.textScrollList(self.outputWin, edit=True, append = ['Result: "All ctrls is at 0,0,0']  ) 
            print  ('// Result: //')
            print  ('// Result: "All ctrls is at 0,0,0 "//')



    ### CHECK 6 ################################ 
    def NgSkin(self):
        if mc.objExists('*ngSkinToolsData_skinCluster1*'):
            
            pm.textScrollList(self.outputWin, edit=True, append = ['    Warning: Contains NgSkin Nodes']  )
            pm.warning("Warning: Contains NgSkin Nodes")

        else:
            pm.textScrollList(self.outputWin, edit=True, append = ['Result: No NgSkin Nodes']  )
            print ("// Result: //")
            print ("// Result: No NgSkin Nodes //")


    ### CHECK 7 ################################ 
    def CheckAll(self):

        pm.select(None)
        
        pm.textScrollList(self.outputWin,  edit=True, removeAll=True)
        self.LockHide()
        self.FindCtrl()
        self.NgSkin()
        self.FindMesh()


    """ Double Constraint Check """ 
                           
    @undo
    def GetSubject(self):
        
        self.targetNodes = []
        constraints = pm.ls(type="constraint")               
        pm.select(None)
        if constraints:
            for constraint in constraints:
                self.targetNodes.extend([
                                    targetNode for targetNode in pm.listConnections(constraint+'.constraintParentInverseMatrix', d=1) 
                                    if (pm.objExists(targetNode) 
                                    and targetNode not in self.targetNodes) 
                                    and len(pm.listConnections(constraint+'.target[*].targetParentMatrix', d=1))>1
                                    ])
        if self.targetNodes:
            pm.select(self.targetNodes)
        
        else:
            pm.select(None)
            pm.textScrollList(self.outputWin, edit=True, append = ['Result:NO Double Constraints, THE SCENE IS CLEAN']  )
            print ("// Result: //")
            print ("// Result:NO Double Constraints, THE SCENE IS CLEAN //" )                           

    @undo
    def FindSources(self):
        
        sourceNodes = []        
        for i, each in enumerate(pm.selected()):   
            constraints = list(set([x for x in each.inputs() if type(x) == pm.nodetypes.ParentConstraint or type(x) == pm.nodetypes.ScaleConstraint]))
            if constraints:
                for constraint in constraints:
                    sourceNodes.extend([sourceNode for sourceNode in pm.listConnections(constraint+'.target[*].targetParentMatrix', s=1) if (pm.objExists(sourceNode) and sourceNode not in sourceNodes)])
            if sourceNodes:                    
                print (" The sources are : ")                   
                for i,each in enumerate(sourceNodes):               
                    pm.select(sourceNodes)  
                    print ("    " + each,i)                                           
            else:
                pm.textScrollList(self.outputWin, edit=True, append = ['Result: There is NO Sources']  )
                print ("// Result: //")
                print ('// Result: There is NO Sources //')     


    @undo
    def FindSourcesMainSource(self):        
        geo = pm.selected()
        sourceNodes0 = []        
        for i, each in enumerate(pm.selected()):
            constraints = list(set([x for x in each.inputs() if type(x) == pm.nodetypes.ParentConstraint or type(x) == pm.nodetypes.ScaleConstraint]))            
            if constraints:
                for constraint in constraints:
                    sourceNodes0.extend([
                                        sourceNode for sourceNode in pm.listConnections(constraint+'.target[0].targetParentMatrix', s=1) 
                                        if (pm.objExists(sourceNode) 
                                        and sourceNode not in sourceNodes0) 
                                        ])
        if sourceNodes0:
            for each in sourceNodes0:
                pm.select(None)               
                pm.select(sourceNodes0,add =True)
                pm.select(geo, d = True)
        
                print ("The main Sources is : " + each)

        else:
            pm.textScrollList(self.outputWin, edit=True, append = ['Result: There is NO Sources ']  )
            print ("// Result: //")
            print  ('// Result: There is NO Sources //')
        
       

    @undo
    def Repair2Conn(self): 
        def repair(var):
                for i, each in enumerate(pm.selected()):
                    self.constraints = list(set([x for x in each.inputs() if type(x) == pm.nodetypes.ParentConstraint or type(x) == pm.nodetypes.ScaleConstraint]))
                    if self.constraints:
                        for constraint in self.constraints:
                            self.sourceNodes0.extend([
                                                sourceNode for sourceNode in pm.listConnections(constraint+'.target[0].targetParentMatrix', s=1) 
                                                if (pm.objExists(sourceNode) 
                                                and sourceNode not in self.sourceNodes0) 
                                                ])
                    if self.sourceNodes0:                        
                        for sources in self.sourceNodes0:                                              
                            self.ParentConstraints = list(set([x for x in each.inputs() if type(x) == pm.nodetypes.ParentConstraint]))
                            self.ScaleConstraints = list(set([x for x in each.inputs() if type(x) == pm.nodetypes.ScaleConstraint]))
 
                            if self.ParentConstraints or self.ScaleConstraints:                          
                                pm.delete(self.ParentConstraints)
                                pm.delete(self.ScaleConstraints)
                                pm.parentConstraint(sources,each, mo = 1)
                                pm.scaleConstraint(sources,each, mo = 1)
                                pm.select(None)
        repair(self.oGeo)



    """ Chris Clean Up button """
    
    def ChrisCleanUp(self):    
        def add_controls_to_set():
            # Add all ctrls to the control set.
            oControls = pm.ls('*__ctrl__', type='transform')
            setName = 'm__element__anim__set__'
            if not pm.objExists(setName):
                selSet = pm.createNode('objectSet', n=setName)
            else:
                selSet = pm.PyNode('m__element__anim__set__')
            setMembers = selSet.members()

            controlsToAdd = [x for x in oControls if x not in setMembers]
            controlsToRemove = [x for x in selSet.members() if not x.endswith('__ctrl__')]
            [selSet.remove(x) for x in controlsToRemove]
            [selSet.add(x) for x in controlsToAdd]

            if controlsToAdd:
                print('Added {} controls to selection set:'.format(len(controlsToAdd)))
                for each in controlsToAdd:
                    print('  {}'.format(each.name()))

            if controlsToRemove:
                print('Removed {} non-controls from selection set:'.format(len(controlsToRemove)))
                for each in controlsToRemove:
                    print('  {}'.format(each.name()))

        def remove_all_materials():
            """ This removes all materials by first assigning all geometry to Lambert1. It then runs
            the MEL command from the Hypershade to remove unused materials and shading groups. """

            allGeo = [x.getTransform() for x in pm.ls(type=['mesh', 'nurbsSurface'])]
            # restore the user's previous selection after running this.
            # The MEL command requires a selection I think.
            oldSel = pm.selected()
            pm.select(allGeo)
            pm.hyperShade(assign='lambert1')
            #TODO: debug this to make sure it is always "hyperShadePanel1"
            pm.mel.hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")
            pm.select(oldSel)
   


        add_controls_to_set()
        # remove_all_materials()
        self.hideAllJoint()


#-----------------------------------
#  FUNCTIONS
#----------------------------------- 



    def rmvCons(self):        
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


    def ResetAttr(self):    
        def main(selectedChannels=True, transformsOnly=False, excludeChannels=None):
            '''
            Resets selected channels in the channel box to default, or if nothing's
            selected, resets all keyable channels to default.
            '''
            gChannelBoxName = mm.eval('$temp=$gChannelBoxName')
            
            sel = mc.ls(sl=True)
            if not sel:
                return
            
            if excludeChannels and not isinstance(excludeChannels, (list, tuple)):
                excludeChannels = [excludeChannels]
            
            chans = None
            if selectedChannels:
                chans = mc.channelBox(gChannelBoxName, query=True, sma=True)
            
            testList = ['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ',
                        'tx','ty','yz','rx','ry','rz','sx','sy','sz']
            for obj in sel:
                attrs = chans
                if not chans:
                    attrs = mc.listAttr(obj, keyable=True, unlocked=True)
                    if excludeChannels:
                        attrs = [x for x in attrs if x not in excludeChannels]
                if transformsOnly:
                    attrs = [x for x in attrs if x in testList]
                if attrs:
                    for attr in attrs:
                        try:
                            default = mc.attributeQuery(attr, listDefault=True, node=obj)[0]
                            mc.setAttr(obj+'.'+attr, default)
                        except StandardError:
                            pass
                                
        def resetPuppetControl(*args):
            main(excludeChannels=['rotateOrder', 'pivotPosition', 'spaceSwitch'])

        if __name__ == '__main__':
            resetPuppetControl()


    def hideAllJoint(self):
        """ Hide all bones in a scene. Set there drawStyle to None """
        def hide_and_show_all_bones(oColl, pDrawStyle):
            for each in oColl:
                try: each.drawStyle.set(pDrawStyle)
                except: continue
        
        oColl = pm.ls('*', type='joint')
        hide_and_show_all_bones(oColl, 2)   



CheckUp()


