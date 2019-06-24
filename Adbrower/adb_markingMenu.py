
# ------------------------------------------------------
# adbrower custom marking menu
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# Ref: http://bindpose.com/custom-marking-menu-maya-python/
# ------------------------------------------------------

import maya.OpenMaya as om
import maya.cmds as mc
import pymel.core as pm
import traceback
import maya.mel as mel
import sys

#-----------------------------------
# IMPORT CUSTOM MODULES
#-----------------------------------

import adbrower
adb = adbrower.Adbrower()

from adbrower import lprint
from ShapesLibrary import*
from adbrower import changeColor

import adb_utils.adb_script_utils.Script__WrapDeformer as adbWrap
import adb_utils.Class__Skinning as skin
import ShapesLibrary as sl
import adb_utils.adb_script_utils.Functions__Rivet as adbRivet


## Import Tools
import adb_tools.Tool__Joint_Generator__Pyside
import adb_tools.Tool__ConnectionTool as Tool__ConnectionTool
import adb_tools.Tool__Tilt as Tool__Tilt
import adb_tools.Tool__IKFK_Switch__PySide as Tool__IKFK_Switch__PySide
import adb_tools.Tool__Match_IkFK_PySide as Tool__Match_IkFK_PySide
import adb_tools.Tool__adbModule as Tool__adbModule
import adb_tools.Tool__CopyWeight_Skin as Tool__CopyWeight_Skin     
import adb_tools.Tool__AutoRig as Tool__AutoRig 
import adb_tools.Tool__CFX__PySide as Tool__adbCFX



#-----------------------------------
# CLASS
#-----------------------------------


MENU_NAME = "adbrower_markingMenu"


class markingMenu():
    '''The main class, which encapsulates everything we need to build and rebuild our marking menu. All
    that is done in the constructor, so all we need to do in order to build/update our marking menu is
    to initialize this class.'''

    def __init__(self):

        self.adb_Menu = "adb_CustomMenu"
        self.labelMenu = "Adbrower"

        self._removeOld()
        self._build()

    def _build(self):
        '''Creates the marking menu context and calls the _buildMarkingMenu() method to populate it with all items.'''
        
        ## Marking Menu
        menu = mc.popupMenu(MENU_NAME, mm=1, b=2, aob=1, ctl=1, alt=1, sh=0, p="viewPanes", pmo=1, pmc=self._buildMarkingMenu)
        
        ## Maya Menu
        if mc.menu( self.adb_Menu, q=1, ex=1 ):
            mc.deleteUI( self.adb_Menu )             

        self.customMenu = mc.menu( self.adb_Menu, l=self.labelMenu, tearOff = True, p='MayaWindow' )  
        self._buildCustomMenu()
        

    def _removeOld(self):
        '''Checks if there is a marking menu with the given name and if so deletes it to prepare for creating a new one.
        We do this in order to be able to easily update our marking menus.'''
        if mc.popupMenu(MENU_NAME, ex=1):
            mc.deleteUI(MENU_NAME)

    def _buildMarkingMenu(self, menu, parent):
        '''This is where all the elements of the marking menu our built.'''

        mc.menuItem(p=menu, l="Match All Transform", rp="E", c = pm.Callback(self.MatchTransformRT, True, True))
        mc.menuItem(p=menu, l="Print List", rp="NW", c = pm.Callback(adb.List))
        mc.menuItem(p=menu, l="LOCK ALL WEIGHTS", rp="S",c = pm.Callback(self.lock_unlock_All_Weight, lock = 1) )
        mc.menuItem(p=menu, l="Add Influence", rp = "SE",c = pm.Callback(self.addInfluence), i = 'addWrapInfluence.png')
        
        transformMenu = mc.menuItem(p=menu, l="Match Transform Separate", rp="NE",i ='parentConstraint.png', subMenu=1)
        mc.menuItem(p=transformMenu, l="Match position", rp="N", c = pm.Callback(self.MatchTransformRT, True, False))
        mc.menuItem(p=transformMenu, l="Match rotation", rp="S", c = pm.Callback(self.MatchTransformRT, False, True))
        
        ConsMenu = mc.menuItem(p=menu, l="Constraint ", rp="SW",subMenu=1)
        mc.menuItem(p=ConsMenu, l="Maintain offset", en = 0 )        
        mc.menuItem(p=ConsMenu, l="Remove all Constraint",rp="SE", c = pm.Callback(self.rmvConstraint))
        mc.menuItem(p=ConsMenu, l="Parent-Scale", rp="NE",c = pm.Callback(self.parent_scale_cons), i ='parentConstraint.png', cl = 'Parent-Scale')
        mc.menuItem(p=ConsMenu, l="Parent", c = lambda *args:pm.parentConstraint(mo=True),i = "parentConstraint.png")
        mc.menuItem(p=ConsMenu, l="Point", c = lambda *args:pm.pointConstraint(mo=True), i = "posConstraint.png")
        mc.menuItem(p=ConsMenu, l="Orient", c = lambda *args:pm.orientConstraint(mo=True), i = "orientConstraint.png")
        mc.menuItem(p=ConsMenu, l="Scale", c = lambda *args:pm.scaleConstraint(mo=True), i = "scaleConstraint.png")
        mc.menuItem(p=ConsMenu, l="Aim", c = lambda *args:pm.aimConstraint(mo=True),i = "aimConstraint.png")
        mc.menuItem(p=ConsMenu, l="Pole Vector", c = lambda *args:pm.poleVectorConstraint(), i = "poleVectorConstraint.png")               
        mc.menuItem(p=ConsMenu, l="Get Constraint Target", rp="W", c =  lambda *args:adb.ConsTarget(pm.selected()))
        mc.menuItem(p=ConsMenu, l="Get Constraint Driver", rp="SW", c = lambda *args:adb.ConsDriver(pm.selected()))

        InfoMenu = mc.menuItem(p=menu, l="Information", rp="W",subMenu=1)
        mc.menuItem(p=InfoMenu, l="Information", en = 0 )
        mc.menuItem(p=InfoMenu, l="Print List", c = pm.Callback(adb.List))
        mc.menuItem(p=InfoMenu, l="Print Loop List", c = lambda *args:lprint(pm.selected()))
        mc.menuItem(p=InfoMenu, l="Print Type", c = lambda *args:lprint(adb.Type(pm.selected())))
        mc.menuItem(p=InfoMenu, l="Print PyMel Type", c =lambda *args:lprint(adb.TypePymel()))
        mc.menuItem(p=InfoMenu, l="Get Node Type", c = pm.Callback(self.NodeType))

        SkinMenu = mc.menuItem(p=menu, l="Skinning", rp="N", i ='paintSkinWeights.png',subMenu=1)
        mc.menuItem(p=SkinMenu, l="Skinning", en = 0 )
        mc.menuItem(p=SkinMenu, l="Bind", c = mc.SmoothBindSkin, rp = 'W' )
        mc.menuItem(p=SkinMenu, l="Unbind Skin", c = mc.DetachSkin, rp = 'SW'  )
        mc.menuItem(p=SkinMenu, l="Reset Skin", c = pm.Callback(adb.resetSkin))
        mc.menuItem(p=SkinMenu, l="Remove Unused", c = lambda *args:pm.mel.removeUnusedInfluences(), rp ='NE' )
        mc.menuItem(p=SkinMenu, l="Add Influence", c = pm.Callback(self.addInfluence), rp = "SE")
        mc.menuItem(p=SkinMenu,  d = True)
        mc.menuItem(p=SkinMenu, l="LOCK All Weights", c = pm.Callback(self.lock_unlock_All_Weight, lock = 1))
        mc.menuItem(p=SkinMenu, l="UNLOCK All Weights", c = pm.Callback(self.lock_unlock_All_Weight, lock = 0))
        mc.menuItem(p=SkinMenu, l="Mirror Weight", c = lambda *args:adb.quickMirrorWeights(), rp = 'N' )
        mc.menuItem(p=SkinMenu,  d = True)
        mc.menuItem(p=SkinMenu, l="Solve Btw", c = lambda *args:skin.Skinning(pm.selected()[0]).solveBtwn() )
        mc.menuItem(p=SkinMenu, l="Conform Weights", c = pm.Callback(self.conform_weights))
        mc.menuItem(p=SkinMenu, l="Label Joints", c = pm.Callback(self.label_jnts))

        ## List
        mc.menuItem(p=menu, l=" --- Create ---", en = 0 )
        mc.menuItem(p=menu, l="Locator", c = pm.Callback(self.createloc))
        mc.menuItem(p=menu, l="Make Root",  c = pm.Callback(self.makeroot))
        mc.menuItem(p=menu, l="Center Joint",  c = pm.Callback(self.centre_joint))        
        nurbsPlaneMenu = mc.menuItem(p=menu, l="Create Nurbs Plane", subMenu=1)
        mc.menuItem(p=nurbsPlaneMenu, l="Plane X axis",  c = pm.Callback(self.create_nurbs_selected_objs,'x'))
        mc.menuItem(p=nurbsPlaneMenu, l="Plane Y axis",  c = pm.Callback(self.create_nurbs_selected_objs,'y'))
        mc.menuItem(p=nurbsPlaneMenu, l="Plane Z axis",  c = pm.Callback(self.create_nurbs_selected_objs,'z'))      
        
        imageColorLambert = mc.internalVar(upd = True)+"scripts/ModIt_script/Icons/ColorLambert.png"
        imageColorGreen = mc.internalVar(upd = True)+"scripts/ModIt_script/Icons/ColorGreen.png"
        imageColorRed = mc.internalVar(upd = True)+"scripts/ModIt_script/Icons/ColorRed.png"
        imageColorBlue = mc.internalVar(upd = True)+"scripts/ModIt_script/Icons/ColorBlue.png"
        imageColorYellow = mc.internalVar(upd = True)+"scripts/ModIt_script/Icons/ColorYellow.png"
        imageColorDarkGrey = mc.internalVar(upd = True)+"scripts/ModIt_script/Icons/ColorDarkGRey.png"
        
        materialMenu = mc.menuItem(p=menu, l="Create Material", subMenu=1)
        mc.menuItem(p=materialMenu, image= imageColorLambert, l="Lambert",  c =  lambda*args:mc.hyperShade( assign= "lambert1" ))
        mc.menuItem(p=materialMenu, image= imageColorYellow, l="Yellow",  c = pm.Callback(self.add_material,'mat_yellow'))
        mc.menuItem(p=materialMenu, image= imageColorBlue, l="Blue",  c = pm.Callback(self.add_material,'mat_bleu'))
        mc.menuItem(p=materialMenu, image= imageColorRed, l="Red",  c = pm.Callback(self.add_material,'mat_red'))      
        mc.menuItem(p=materialMenu, image= imageColorGreen, l="Green",  c = pm.Callback(self.add_material,'mat_green'))      
        mc.menuItem(p=materialMenu, image= imageColorDarkGrey, l="Dark Grey",  c = pm.Callback(self.add_material,'mat_darkGrey'))                  
          
        mc.menuItem(p=menu,  d = True)
        mc.menuItem(p=menu, l=" --- Deformers ---", en = 0 )
        mc.menuItem(p=menu, l="Cluster",  c = lambda *args:pm.mel.newCluster(" -envelope 1"))
        mc.menuItem(p=menu, l="Blendshape - Local",  c = lambda *args:adb.blendshape(pm.selected(),"local"))
        mc.menuItem(p=menu, l="Blendshape - World (snap to position)",  c = lambda *args:adb.blendshape(pm.selected(),"world"))
        mc.menuItem(p=menu, l="Wrap",  c = lambda *args:adbWrap.wrapDeformer(_HiRez = pm.selected(), _LoRez=pm.selected()))
        mc.menuItem(p=menu, l="Rivet From Face",  c = lambda*args: adbRivet.rivet_from_faces(scale = 0.2)) 
        mc.menuItem(p=menu, l="Sticky From Face",  c = lambda*args: adbRivet.sticky_from_faces(scale = 0.2)) 

        mc.menuItem(p=menu,  d = True)
        controlMenu = mc.menuItem(p=menu, l="Control Shapes", subMenu=1)
        mc.menuItem(p=controlMenu, l="Circle", c =pm.Callback(self.makeCtrl,sl.circleX_shape))
        mc.menuItem(p=controlMenu, l="Square", c =pm.Callback(self.square_prop_shape))
        mc.menuItem(p=controlMenu, l="Cube", c =pm.Callback(self.makeCtrl,sl.cube_shape))
        mc.menuItem(p=controlMenu, l="Ball", c =pm.Callback(self.makeCtrl,sl.ball2_shape))
        mc.menuItem(p=controlMenu, l="Diamond", c =pm.Callback(self.makeCtrl,sl.diamond_shape))
        mc.menuItem(p=controlMenu, l="Cog", c =pm.Callback(self.makeCtrl,sl.cog_shape))
        mc.menuItem(p=menu,  d = True)

        mc.menuItem(p=menu, l=" --- Quick access ---", en = 0 )
        mc.menuItem(p=menu, l="No Pasted",  c = pm.Callback(self.no_Pasted))
        mc.menuItem(p=menu, l="Auto Suffix", c = lambda *args:adb.AutoSuffix(pm.selected()) )
        mc.menuItem(p=menu, l="Select Edges by 2", c = lambda *args:pm.mel.polySelectEdgesEveryN("edgeRing", 2) )

    def _buildCustomMenu(self):
        '''Build the options for the Maya Menu bar '''
        mc.menuItem(p=self.customMenu, l="adbrower's Tools", d = True)
        mc.menuItem(p=self.customMenu, l="Main Toolbox", c = pm.Callback(self.adbToolbox))
        mc.menuItem(p=self.customMenu, l="adb Module Tool", c = lambda *arg:Tool__adbModule.adbModule())
        mc.menuItem(p=self.customMenu, l="Joint Generator Tool", c = lambda *arg:adb_tools.Tool__Joint_Generator__Pyside.showUI()) 
        mc.menuItem(p=self.customMenu, l="Connection Tool", c = lambda *arg:Tool__ConnectionTool.connectionTool())    
        mc.menuItem(p=self.customMenu, l="Tilt Tool", c = lambda *arg:Tool__Tilt.TiltTool() )    
        mc.menuItem(p=self.customMenu, l="Copy Weights", c = lambda *arg:Tool__CopyWeight_Skin.showUI())
        mc.menuItem(p=self.customMenu, l="IK FK Switch", c = lambda *arg:Tool__IKFK_Switch__PySide.ui())
        mc.menuItem(p=self.customMenu, l="IK FK Match", c = lambda *arg:Tool__Match_IkFK_PySide.ui())
        mc.menuItem(p=self.customMenu, l="CFX Tool", c = lambda *arg:Tool__adbCFX.showUI())
        mc.menuItem(p=self.customMenu, l="Auto Rig Tool", c = lambda*arg:Tool__AutoRig.adbAutoRig())


#-----------------------------------
# FUNCTIONS
#-----------------------------------

# ------------ SKINNING

    def addInfluence(self):
        mesh = pm.ls(sl=1, type='transform')
        skinCls = adb.findSkinCluster(pm.selected()[-1])
        jnts = pm.ls(sl=1, type='joint')    
        for joint in jnts: 
            try:
                pm.skinCluster(skinCls[0], ai=joint, dr=0.1, wt=0, e=1, lw=True)
            except RuntimeError:
                pass

    def lock_unlock_All_Weight(self, lock = True):  
        mesh = pm.selected()[0]
        node = skin.Skinning(mesh)
        if lock:
            node.lockAll_Weight()
        else:
            node.unlockAll_Weight()
        pm.select(mesh, r =1)
        if pm.currentCtx() != "artAttrSkinContext":
            mel.eval("ArtPaintSkinWeightsTool;")

    @staticmethod
    def create_nurbs_selected_objs(_offset_axis):
        selection = mc.ls(sl=1)
        points0 = []
        points1 = []
        offset = 2.0
        offset_axis = _offset_axis
        for o, obj in enumerate(selection):
            matrix = mc.xform(obj, q=1, m=1, ws=1)
            c_pos = [om.MDistance.internalToUI(v) for v in matrix[12:15]]

            axis = dict(x=[om.MDistance.internalToUI(v) for v in matrix[0:3]],
                        y=[om.MDistance.internalToUI(v) for v in matrix[4:7]],
                        z=[om.MDistance.internalToUI(v) for v in matrix[8:11]])
            dir_pos = axis[offset_axis]
            if o < len(selection) - 1:
                next_matrix = mc.xform(selection[o + 1], q=1, m=1, ws=1)
            else:
                next_matrix = mc.xform(selection[o - 1], q=1, m=1, ws=1)
            next_c_pos = [om.MDistance.internalToUI(v) for v in next_matrix[12:15]]
            if o < len(selection) - 1:
                inb_pos_v = [n - c for n, c in zip(next_c_pos, c_pos)]
            else:
                inb_pos_v = [c - n for n, c in zip(next_c_pos, c_pos)]
            inb_pos = [inb_pos_v[0] * 0.5, inb_pos_v[1] * 0.5, inb_pos_v[2] * 0.5]
            if o == 0:
                points0.append([((c - i) + (d * offset)) for c, i, d in zip(c_pos, inb_pos, dir_pos)])
                points1.append([((c - i) - (d * offset)) for c, i, d in zip(c_pos, inb_pos, dir_pos)])
                points0.append([((c - i) + (d * offset)) for c, i, d in zip(c_pos, inb_pos, dir_pos)])
                points1.append([((c - i) - (d * offset)) for c, i, d in zip(c_pos, inb_pos, dir_pos)])
            if o < len(selection) - 1:
                points0.append([((c + i) + (d * offset)) for c, i, d in zip(c_pos, inb_pos, dir_pos)])
                points1.append([((c + i) - (d * offset)) for c, i, d in zip(c_pos, inb_pos, dir_pos)])
            else:
                points0.append([((c - i) + (d * offset)) for c, i, d in zip(c_pos, inb_pos, dir_pos)])
                points1.append([((c - i) - (d * offset)) for c, i, d in zip(c_pos, inb_pos, dir_pos)])
                points0.append([((c + i) + (d * offset)) for c, i, d in zip(c_pos, inb_pos, dir_pos)])
                points1.append([((c + i) - (d * offset)) for c, i, d in zip(c_pos, inb_pos, dir_pos)])
        curve0 = mc.curve(d=3, p=points0)
        curve1 = mc.curve(d=3, p=points1)
        nurbs = mc.loft(curve0, curve1, ch=1, u=1, c=0, ar=1, d=3, ss=1, rn=0, po=0, rsn=True)
        mc.delete([curve0, curve1])
        return nurbs   

    
    def conform_weights(self):
        """
        It conforms the weights of the selected vertices. The selection needs to be vertices of a mesh and
        the mesh should have attached a skinCluster.
        
        Returns:

        """
        weights_data = dict()
        selection = mc.ls(sl=1, fl=1)
        mc.select(cl=1)
        for component in selection:
            if mc.objectType(component, i='mesh'):
                mesh = mc.listRelatives(component, p=1)[0]
                for skn in mc.ls(typ='skinCluster'):
                    if mc.skinCluster(skn, q=1, g=1)[0] == mesh:
                        for influence, weight in zip(mc.skinCluster(skn, inf=1, q=1),
                                                     mc.skinPercent(skn, component, q=1, v=1)):
                            if weight != 0 and influence in weights_data.keys():
                                weights_data[influence] += weight
                            elif weight != 0 and influence not in weights_data.keys():
                                weights_data[influence] = weight
                            else:
                                pass
                        break
        
        transformation_value = [(influence, weight / len(selection)) for influence, weight in weights_data.items()]
        
        for component in selection:
            mc.skinPercent(skn, component, transformValue=transformation_value)  



# ------------ CONSTRAINTS
        
    def parent_scale_cons(self):
        mylist = mc.ls(sl=True)
        Driver = mylist[0] #mon controleur mere
        targets = mylist[1:]
        for  each in targets:
            mc.parentConstraint(Driver,each, mo=True)
            mc.scaleConstraint(Driver,each, mo=True)

    def rmvConstraint(self):
        adb.removeCons(subject = pm.selected(), constraint_type = ['parentConstraint','scaleConstraint','orientConstraint','pointConstraint', 'aimConstraint'])        
        sys.stdout.write('// Result: Removed all constraints //') 

    def MatchTransformRT(self, pos = True, rot = True):
        '''Match the Rotation and Position of 2 objects '''
        mylist = mc.ls(sl=True)
        Driver = mylist[0] #mon controleur mere
        targets = mylist[1:]
        for each in targets:
            mc.matchTransform(targets,Driver,rot=rot, pos=pos)            
        sys.stdout.write('Match Transformed ')
        
        
# ------------ CREATE

    @changeColor('index', col = (17))
    def createloc(self):
        '''Creates locator at the Pivot                of the object selected '''
        if pm.selected():
            try:
                loc = adb.LocOnVertex()
            except AttributeError:                            
                locs = []
                for sel in pm.selected():                           

                    try:
                        _name = sel.name().split('__')[1]  
                    except:
                        _name = sel.name()
                    
                    loc_align = pm.spaceLocator(n=_name + '__loc__')
                    locs.append(loc_align)
                    pm.matchTransform(loc_align,sel,rot=True, pos=True)
                    pm.select(locs, add = True)
                return locs
        else:
            locs = pm.spaceLocator(n='Locator1')
            return locs

    def makeroot(self):
        oColl = pm.selected()
        newSuffix = 'root__grp'
        for each in oColl:
            try:
                suffix = each.name().split('__')[-2]
                cutsuffix = '__{}__'.format(suffix)
            except:
                suffix, cutsuffix = '', ''
            oRoot = pm.group(n=each.name().replace(cutsuffix,'') + '_{}__{}__'.format(suffix, newSuffix), em=True)

            for i in xrange(4):
                oRoot.rename(oRoot.name().replace('___','__'))
            oRoot.setTranslation(each.getTranslation(space='world'), space='world')
            oRoot.setRotation(each.getRotation(space='world'), space='world')
            try:
                pm.parent(oRoot, each.getParent())
            except:
                pass
            pm.parent(each, oRoot)
            pm.setAttr(oRoot.v, keyable=False, cb=False)
            pm.makeIdentity(n=0, s=1, r=1, t=1, apply=True, pn=1)
            # oRoot.v.lock()
        pm.select(oColl)


    def label_jnts(self, left_side='L_', right_side='R_'):       
        for sel in pm.ls(type='joint'):
            short = sel.split('|')[-1].split(':')[-1]
            if short.startswith(left_side):
                side = 1
                other = short.split(left_side)[-1]
            elif short.startswith(right_side):
                side = 2
                other = short.split(right_side)[-1]
            else:
                side = 0
                other = short
            pm.setAttr('{0}.side'.format(sel), side)
            pm.setAttr('{0}.type'.format(sel), 18)
            pm.setAttr('{0}.otherType'.format(sel), other, type='string')
        sys.stdout.write('// Result: Joints are label')



    def centre_joint(self):
        """
        Creates a joint in the centre of the selection. You can select objects, components...
        """
        # logger.info('.. Create a joint in the centre of the selection ..')
        sel = mc.ls(sl=1, fl=1)
        if len(sel) == 1:
            # Get the bounding box values of the object
            pos = mc.xform(q=1, ws=1, bb=1)
            mc.select(cl=True)
            return mc.joint(p=((pos[0] + pos[3]) / 2, (pos[1] + pos[4]) / 2, (pos[2] + pos[5]) / 2))
        elif len(sel) > 1:
            bb = [0, 0, 0, 0, 0, 0]
            for obj in sel:
                pos = mc.xform(obj, q=1, ws=1, bb=1)
                for i in range(6):
                    bb[i] += pos[i]
            for i in range(6):
                bb[i] /= len(sel)
            mc.select(cl=True)
            return mc.joint(p=((bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, (bb[2] + bb[5]) / 2))
        else:
            sys.stdout.write('// Result : Nothing selected. Please select at least one object //')


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
            
            



# ------------ INFORMATIONS

    def NodeType(self):
        """ Get the type of all connected nodes """
        oColl = pm.selected()
        Nodes = [x for x in pm.listConnections(oColl, et=True, skipConversionNodes = True) ]
        NodeType = list(set([pm.objectType(x) for x in Nodes]))
        try:
            NodeType.remove("nodeGraphEditorInfo")
        except:
            pass
        if NodeType != []:
            print ('// Result: //')
            for types in NodeType:
                print ("     " + types)
        else:
            print ('// Result: No Nodes //')


# ------------ CONTROLS

    @changeColor()
    def makeCtrl(self,shape_name):
        ''' Controller builder

        If something is selected :
            - Creates a controller according to the shape. Match the rotation, position, and name of the selection

        if nothing selected
            -Creates a controller in the center at 0,0,0

        '''
        if pm.selected():
            _ctrl = sl.makeCtrls(shape_name)
        else:
            _ctrl = shape_name()
        return _ctrl

    def square_prop_shape(self):        
        selection = pm.selected()                   
        if pm.selected():        
            for sel in selection:
                sl.square_prop_shape()
        else:
            @changeColor()
            def singleSquare():
                _ctrl = pm.curve(p=[(0.55, 0.02, 0.55), (0.55, 0.02, -0.55), (-0.55, 0.02, -0.55), (-0.55, 0.02, 0.55), (0.55, 0.02, 0.55)],k=[0.0, 1.0, 2.0, 3.0, 4.0], d=1, n = "square_ctrl")
                return _ctrl
            singleSquare()


# ------------ TOOLS

    def adbToolbox(self):
        import audrey_toolbox_V03

# ------------ NAMING

    def no_Pasted(self):
        '''Remove all "pasted" '''
        for each in pm.ls('pasted__*'):
            each.rename(each.name().replace('pasted__',''))


markingMenu()