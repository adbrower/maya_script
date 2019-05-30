# -------------------------------------------------------------------
# Class Joint  
# -- Method Rigger (Maya)
#
# By: Audrey Deschamps-Brower
#     audreydb23@gmail.com
# -------------------------------------------------------------------

import pymel.core as pm
import maya.OpenMaya as om
from adbrower import makeroot
import adbrower
adb = adbrower.Adbrower()

from adbrower import flatList
import adb_utils.Class__Transforms as adbTransform

#-----------------------------------
# CLASS
#----------------------------------- 


class Joint(adbTransform.Transform):
    """
    A Module containing multiples joint methods
    """
    
    def __init__(self,
                _joint,
                ):
        
        self.joint = _joint
        self._orientAxis = None
        
        if isinstance(self.joint, list):
            self.joint = [pm.PyNode(x) for x in _joint]
        elif isinstance(self.joint, basestring):
            self.joint = [_joint]
        else:
            self.joint = _joint
                       
        super(Joint, self).__init__(self.joint)
                
    def __repr__(self):       
        return str('<{} \'{}\'>'.format(self.__class__.__name__, self.joint))
        
        
    @classmethod
    def findAll(cls):
        ''' Return a Joint instance for every joint node in the scene. '''
        return cls([jnt for jnt in pm.ls(type='joint')])

        
    @classmethod
    def fromSelected(cls):
        ''' Return a instance for a list with all selected '''
        return cls([(jnt) for jnt in pm.selected()])
        
                        
    @classmethod
    def create(cls, numb = 1, name = '', r = 1, ):
        jnt_created = []
        for number in range(numb):
            jnt = pm.joint(n=name, rad=r)
            pm.parent(jnt, w=1)
            jnt_created.append(jnt)
        return cls(jnt_created)

    @property
    def orientAxis(self):              
        dup_jnt = pm.duplicate(self.joint[0], po = True)[0]
        pm.parent(dup_jnt, w=1)
        root_grp = adb.makeroot_func(dup_jnt)
        pm.select(root_grp,  r=1)
        self.ResetAttr()
        
        decNode = pm.shadingNode('decomposeMatrix', au =1)
        pm.PyNode(dup_jnt).worldMatrix >> decNode.inputMatrix
        matrixRotationValue = decNode.getAttr('inputMatrix')[0]
        pm.delete(root_grp)
            
        print matrixRotationValue        
        if '{:.2f}'.format(matrixRotationValue[0]) == '0.00' :
            self._orientAxis = 'Y'
        elif '{:.2f}'.format(matrixRotationValue[0]) == '1.00':
            self._orientAxis = 'X'     
                           
        return self._orientAxis

                            
    @orientAxis.setter
    def orientAxis(self, val):
        self._orientAxis = val
        self.orient_joint()

    @property
    def drawStyle(self):
        if self.joint == None:
            pass
        return pm.PyNode(self.joint[0]).drawStyle.get()
            
    @drawStyle.setter
    def drawStyle(self, value):
        '''
        0 : Bone
        1 : Multi - Child as box
        2 : None
        '''
        for jnt in self.joint:
            pm.PyNode(jnt).drawStyle.set(value)
        
    @property
    def radius(self):  
        if self.joint == None:
            pass
        rad = pm.PyNode(self.joint[0]).radius.get() or []
        if rad:
            self._radius = rad
        else:
            pass
        return self._radius

        
    @radius.setter
    def radius(self, rad):
        self._radius = rad
        for joint in self.joint:
            pm.PyNode(joint).radius.set(rad)
            
    
    def orient_joint(self):        
        if self._orientAxis == 'Y':
            pm.select(self.joint)
            pm.joint(zso=1, ch=1, e=1, oj='yxz', secondaryAxisOrient='xdown')
            pm.select(cl=True)

            #Orient the last joint to the world#
            selLastJnt = pm.select(self.joint[-1])
            pm.joint(e=1, oj='none')
            pm.select(None)

        elif self._orientAxis == 'y':
            pm.select(self.joint)
            pm.joint(zso=1, ch=1, e=1, oj='yxz', secondaryAxisOrient='xup')
            pm.select(cl=True)

            #Orient the last joint to the world#
            selLastJnt = pm.select(self.joint[-1])
            pm.joint(e=1, oj='none')
            pm.select(None)

        elif self._orientAxis == 'X' :  
            pm.select(self.joint)
            pm.joint(zso=1, ch=1, e=1, oj='xyz', secondaryAxisOrient='xup')
            pm.select(cl=True)

            #Orient the last joint to the world#
            selLastJnt = pm.select(self.joint[-1])
            pm.joint(e=1, oj='none') 
            pm.select(None)  

        elif self._orientAxis == 'x' :  
            pm.select(self.joint)
            pm.joint(zso=1, ch=1, e=1, oj='xyz', secondaryAxisOrient='xdown')
            pm.select(cl=True)

            #Orient the last joint to the world#
            selLastJnt = pm.select(self.joint[-1])
            pm.joint(e=1, oj='none') 
            pm.select(None)  
                
        else:
            raise ValueError('That Axis does not exist')        
    
    @staticmethod
    def label_jnts(left_side='L_', right_side='R_'):       
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



