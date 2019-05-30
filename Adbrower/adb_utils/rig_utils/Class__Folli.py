# ------------------------------------------------------
# Class Follicule Module
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
#     Based on Chris Lesage's script 
# ------------------------------------------------------


import sys
import pymel.core as pm
import maya.cmds as mc
import maya.mel as mel


#-----------------------------------
# IMPORT CUSTOM MODULES
#----------------------------------- 


import adbrower

adb = adbrower.Adbrower()

from adbrower import lprint
from adbrower import flatList
import ShapesLibrary as sl

#-----------------------------------
#  DECORATORS
#----------------------------------- 

from adbrower import undo
from adbrower import changeColor


#-----------------------------------
# CLASS
#----------------------------------- 

class Folli(object):
    '''
    Create Follicules on a surface    
    
    @param countU: int
    @param countV: int
    @param vDir: String. Default Value is 'U'
    @param radius : float or int. Default value is 1
    @param sub : Surface on which we build the follicules system.
    
    ## EXTERIOR CLASS BUILD
    #------------------------
    import adb_utils.rig_utils.Class__Folli as adbFolli
    reload (adbFolli)    

    # example:
    test =  adbFolli.Folli(1, 8, radius = 0.5, sub = 'pPlane1')    
    '''
    def __init__(self, 
                 countU,
                 countV,
                 radius = 0.2, 
                 sub = pm.selected(),                               
                 ):
                    
        self.sub = pm.PyNode(sub)
        self.countU = countU
        self.countV = countV
        self.vDir = 'U'
        self.radius = radius
        self.all_foll_list = []
        self.all_joints_list = []
        
        if self.sub.getShape().type() == 'nurbsSurface':
            plugs = pm.listConnections(str(self.sub.getShape())+ '.local',d=True, sh = True)
        else:
            plugs = pm.listConnections(str(self.sub.getShape())+ '.outMesh',d=True, sh = True)
        current_numb_foll = len([x for x in plugs if x.type() == 'follicle']) or []
       
        if current_numb_foll == []:
            self.many_follicles(self.sub, self.countU, self.countV, self.vDir, self.radius)
        else:
            self.add_folli(self.countV, mesh = self.sub)

    def __repr__(self):
        return str('{} : {} \n {}'.format(self.__class__.__name__, self.sub, self.__class__))
        
    @property
    def getFolliGrp(self):
        return self.oRoot
                
    @property
    def getFollicules(self):
        ''' Returns the follicules ''' 
        return self.all_foll_list

    @property
    def getJoints(self):
        ''' Returns the joints ''' 
        return self.all_joints_list


    def create_follicle(self, oNurbs, count, uPos=0.0, vPos=0.0):
        # manually place and connect a follicle onto a nurbs surface.
        if oNurbs.type() == 'transform':
            oNurbs = oNurbs.getShape()
        elif oNurbs.type() == 'nurbsSurface' or 'mesh':
            pass       
        else:
            'Warning: Input must be a nurbs surface.'
            return False
         
        pName = '{}_{}__foll__'.format(oNurbs.name(), count)

        oFoll = pm.createNode('follicle', name='{}'.format(pName))
        oFoll.v.set(1) # hide the little red shape of the follicle
        if oNurbs.type() == 'nurbsSurface':
            oNurbs.local.connect(oFoll.inputSurface)
        if oNurbs.type() == 'mesh':
            # if using a polygon mesh, use this line instead.
            # (The polygons will need to have UVs in order to work.)
            oNurbs.outMesh.connect(oFoll.inputMesh)
         
        for param in pm.listAttr(oFoll, keyable=True):
            if param in ['parameterU', 'parameterV']: pass
            else:
                pm.PyNode(oFoll + '.' + param).setKeyable(False)
     
        oNurbs.worldMatrix[0].connect(oFoll.inputWorldMatrix)
        oFoll.outRotate.connect(oFoll.getParent().rotate)
        oFoll.outTranslate.connect(oFoll.getParent().translate)
        uParam = self.add_keyable_attribute(oFoll.getParent(), 'double', 'u_param', oMin=-100, oMax=100, oDefault=0)
        vParam = self.add_keyable_attribute(oFoll.getParent(), 'double', 'v_param', oMin=-100, oMax=100, oDefault=0)
        self.connect_multiply(oFoll.parameterU, oFoll.getParent().u_param, 0.01)
        self.connect_multiply(oFoll.parameterV, oFoll.getParent().v_param, 0.01)
        uParam.set(uPos)
        vParam.set(vPos)
        oFoll.getParent().t.lock()
        oFoll.getParent().r.lock() 
        return oFoll
     
          
    def add_keyable_attribute(self, myObj, oDataType, oParamName, oMin=None, oMax=None, oDefault=0.0):
        """adds an attribute that shows up in the channel box; returns the newly created attribute"""
        oFullName = '.'.join( [str(myObj),oParamName] )
        if pm.objExists(oFullName):
            return pm.PyNode(oFullName)
        else:
            myObj.addAttr(oParamName, at=oDataType, keyable=True, dv=oDefault)
            myAttr = pm.PyNode(myObj + '.' + oParamName)
            if oMin != None:
                myAttr.setMin(oMin)
            if oMax != None:
                myAttr.setMax(oMax)
            pm.setAttr(myAttr, e=True, channelBox=True)
            pm.setAttr(myAttr, e=True, keyable=True)
            return myAttr
     
     
    def connect_multiply(self, oDriven, oDriver, oMultiplyBy):
        nodeName = oDriven.replace('.','_') + '_mult'
        try:
            testExists = pm.PyNode(nodeName)
            pm.delete(pm.PyNode(nodeName))
            print ('deleting'.format(nodeName))
        except: pass
        oMult = pm.shadingNode('unitConversion', asUtility=True, name=nodeName)
        pm.PyNode(oDriver).connect(oMult.input)
        oMult.output.connect( pm.Attribute(oDriven) )
        oMult.conversionFactor.set(oMultiplyBy)
        return oMult
     

    def many_follicles(self, myObject, countU, countV, vDir='U', radius =1):
        self.countU = countU
        self.countV = countV
        self.vDir = vDir
        self.radius = radius
        obj = self.sub
        pm.select(obj, r = True)
        # myObject = pm.selected()[0]
        pName = str(myObject)
        self.oRoot = pm.spaceLocator(n=pName.replace('_ribbon','') + '_follicles')
        pm.delete(self.oRoot.getShape())
        currentFollNumber = 0      
          
        for i in range(countU):
            for j in range(countV):
                currentFollNumber += 1
                pm.select(None)
                if countU == 1:
                    uPos = 50.0
                else:
                    uPos = (i/(countU-1.00)) * 100.0 #NOTE: I recently changed this to have a range of 0-10
                if countV == 1:
                    vPos = 50.0
                else:
                    vPos = (j/(countV-1.00)) * 100.0 #NOTE: I recently changed this to have a range of 0-10
                if vDir == 'U':
                    oFoll = self.create_follicle(myObject, currentFollNumber, vPos, uPos)
                    self.all_foll_list.append(oFoll)
                else:
                    # reverse the direction of the follicles
                    oFoll = create_follicle(myObject, currentFollNumber, uPos, vPos)
                    self.all_foll_list.append(oFoll)
                    
                pm.rename(oFoll.getParent(), '{}_0{}__foll__'.format(pName, currentFollNumber))
                pm.rename(oFoll, '{}_{}__foll__Shape'.format(pName, currentFollNumber))
                oLoc = pm.group(em=True, n='{}_0{}__grp__'.format(pName, currentFollNumber))
                oLoc.setTranslation(oFoll.getParent().getTranslation(space='world'), space='world')
        
                oJoint = pm.joint(n=pName + '_0{}__jnt__'.format(currentFollNumber), rad = radius)
                self.all_joints_list.append(oJoint)
                oJoint.setTranslation(oFoll.getParent().getTranslation(space='world'), space='world')
                
                # connect the UV params to the joint so you can move the follicle by selecting the joint directly.
                uParam = self.add_keyable_attribute(oJoint, 'double', 'u_param', oMin=-100, oMax=100, oDefault=0)
                vParam = self.add_keyable_attribute(oJoint, 'double', 'v_param', oMin=-100, oMax=100, oDefault=0)
                uParam.set(oFoll.getParent().u_param.get())
                vParam.set(oFoll.getParent().v_param.get())
                uParam.connect(oFoll.getParent().u_param)
                vParam.connect(oFoll.getParent().v_param)
        
                #pm.parent(oJoint, oLoc)
                pm.parent(oLoc, oFoll.getParent())
                pm.parent(oFoll.getParent(), self.oRoot)
                oLoc.rx.set(0.0)
                oLoc.ry.set(0.0)
                oLoc.rz.set(0.0)
                pm.select(None)
                
        return self.all_foll_list


    @changeColor()
    def addControls(self, shape = sl.ball_shape):
        ''' add Controls to the follicules ''' 
        pm.select(self.getJoints, r = True)
        self.create_ctrls = flatList(sl.makeCtrls(shape))
        
        ## get the scale of the joint to add 0.5 on the scale of the controller
        [x.scaleX.set((pm.PyNode(self.getJoints[0]).radius.get()) + 0.5) for x in self.create_ctrls]
        [x.scaleY.set((pm.PyNode(self.getJoints[0]).radius.get()) + 0.5) for x in self.create_ctrls]
        [x.scaleZ.set((pm.PyNode(self.getJoints[0]).radius.get()) + 0.5) for x in self.create_ctrls]
        
        for joints, ctrls in zip (self.getJoints, self.create_ctrls):
            pm.parent(ctrls, pm.PyNode(joints).getParent() )       
                        
        for joints, ctrls in zip (self.getJoints, self.create_ctrls):
            pm.parent(joints,ctrls)
         
        [pm.makeIdentity(x, n=0, s=1, r=1, t=1, apply=True, pn=1) for x in self.create_ctrls]
        
        return self.create_ctrls
            

    def add_folli(self, add_value):   
        '''
        add follicules to an already existing system    
        
        @param add_value: (int) Number of follicules to add
        @param mesh: (str) Mesh having the follicules
     
        '''
        mesh = self.sub
        
        for x in xrange(add_value):
            mesh_shape = pm.PyNode(mesh).getShape()
            
            plugs = pm.listConnections(str(mesh_shape)+ '.outMesh',d=True, sh = True)
            current_numb_foll = len([x for x in plugs if x.type() == 'follicle'])
            oFoll = self.create_follicle(pm.PyNode(mesh), (current_numb_foll+1), 1)
            pName = str(oFoll.getParent()).split('_')[0]
            oRoot = [x for x in plugs if x.type() == 'follicle'][0].getParent().getParent()
            
            pm.rename(oFoll.getParent(), '{}_0{}__foll__'.format(pName, current_numb_foll+1))
            pm.rename(oFoll, '{}_{}__foll__Shape'.format(pName, current_numb_foll))

            oLoc = pm.group(em=True)
            oLoc.setTranslation(oFoll.getParent().getTranslation(space='world'), space='world')

            oJoint = pm.joint( rad = 1)
            # self.all_joints_list.append(oJoint)
            oJoint.setTranslation(oFoll.getParent().getTranslation(space='world'), space='world')

            # connect the UV params to the joint so you can move the follicle by selecting the joint directly.
            uParam = self.add_keyable_attribute(oJoint, 'double', 'u_param', oMin=-100, oMax=100, oDefault=0)
            vParam = self.add_keyable_attribute(oJoint, 'double', 'v_param', oMin=-100, oMax=100, oDefault=0)
            uParam.set(oFoll.getParent().u_param.get())
            vParam.set(oFoll.getParent().v_param.get())
            uParam.connect(oFoll.getParent().u_param)
            vParam.connect(oFoll.getParent().v_param)

            pm.rename(oJoint, '{}_0{}__jnt__'.format(pName, current_numb_foll+1))
            pm.rename(oJoint.getParent(), '{}_0{}__grp__'.format(pName, current_numb_foll+1))

            pm.parent(oLoc, oFoll.getParent())
            pm.parent(oFoll.getParent(), oRoot)
            oLoc.rx.set(0.0)
            oLoc.ry.set(0.0)
            oLoc.rz.set(0.0)
            pm.select(None)
            
            
            
            
# Folli(1, 5, radius = 0.5, sub = 'proxy') 