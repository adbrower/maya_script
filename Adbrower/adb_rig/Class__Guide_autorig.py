import sys
import traceback
import pymel.core as pm
import maya.cmds as mc
from pprint import pprint

#-----------------------------------
# IMPORT CUSTOM MODULES
#----------------------------------- 

import ShapesLibrary as sl
reload(sl)
from ShapesLibrary import*

import adbrower
reload(adbrower)
adb = adbrower.Adbrower()
from adbrower import lprint


#-----------------------------------
#  DECORATORS
#----------------------------------- 
from adbrower import changeColor
from adbrower import makeroot

#-----------------------------------
# CLASS
#----------------------------------- 

class autoRigGuide(object):
    def __init__(self,**kwargs):
        
        self.all_guide = []
        self.guideCtrl()
        self.connections()
        self.guide_scale_grp = self.jointsSetup()
        self.mainCtrls()
        self.cleanUp()
        


    def guideCtrl(self):  
        #====================
        #Left side
        #=====================
        
        self.all_sphere = []
        @makeroot(suf='connections')
        @makeroot()        
        def left_arm_clav(side = 'l', basename = 'arm_clav', type = 'guide', radius = 2):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _left_arm_clav_gd = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _left_arm_clav_gd.setTranslation((9,100,0), space='object')
            self.all_sphere.append(_left_arm_clav_gd)
            return _left_arm_clav_gd
        
        self.left_arm_clav_gd = left_arm_clav()


        @makeroot(suf='connections')
        @makeroot()        
        def left_arm_elbow(side = 'l', basename = 'arm_elbow', type = 'guide', radius = 2):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _left_arm_elbow_gd = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _left_arm_elbow_gd.setTranslation((28,100,-1), space='object')
            self.all_sphere.append(_left_arm_elbow_gd)
            return _left_arm_elbow_gd
        
        self.left_arm_elbow_gd = left_arm_elbow()

        @makeroot(suf='connections')
        @makeroot()        
        def left_arm_hand(side = 'l', basename = 'arm_hand', type = 'guide', radius = 1):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _left_arm_hand_gd = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _left_arm_hand_gd.setTranslation((43,100,-1), space='object')
            self.all_sphere.append(_left_arm_hand_gd)
            return _left_arm_hand_gd
        
        self.left_arm_hand_gd = left_arm_hand()



        @makeroot(suf='connections')
        @makeroot()        
        def left_leg_main(side = 'l', basename = 'leg_main', type = 'guide', radius = 1):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _left_leg_main_gd = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _left_leg_main_gd.setTranslation((15,64,2), space='object')
            self.all_sphere.append(_left_leg_main_gd)
            return _left_leg_main_gd
        
        self.left_leg_main_gd = left_leg_main()


        @makeroot(suf='connections')
        @makeroot() 
        def left_leg_thigh(side = 'l', basename = 'leg_thigh', type = 'guide', radius = 3):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _left_leg_thigh = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _left_leg_thigh.setTranslation((6,64,1), space='object')
            self.all_sphere.append(_left_leg_thigh)
            return _left_leg_thigh
        
        self.left_leg_thigh = left_leg_thigh()


        @makeroot(suf='connections')
        @makeroot() 
        def left_leg_knee(side = 'l', basename = 'leg_knee', type = 'guide', radius = 3):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _left_leg_knee = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _left_leg_knee.setTranslation((6,35,3.7), space='object')
            self.all_sphere.append(_left_leg_knee)
            return _left_leg_knee
        
        self.left_leg_knee = left_leg_knee()


        @makeroot(suf='connections')
        @makeroot() 
        def left_leg_ankle(side = 'l', basename = 'leg_ankle', type = 'guide', radius = 2):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _left_leg_ankle = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _left_leg_ankle.setTranslation((6,7,0), space='object')
            self.all_sphere.append(_left_leg_ankle)
            return _left_leg_ankle
        
        self.left_leg_ankle = left_leg_ankle()

        @makeroot(suf='connections')
        @makeroot() 
        def left_leg_ball(side = 'l', basename = 'leg_ball', type = 'guide', radius = 1):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _left_leg_ball = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _left_leg_ball.setTranslation((6,3,6.5), space='object')
            self.all_sphere.append(_left_leg_ball)
            return _left_leg_ball
        
        self.left_leg_ball = left_leg_ball()

        @makeroot(suf='connections')
        @makeroot() 
        def left_leg_toe(side = 'l', basename = 'leg_toe', type = 'guide', radius = 1):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _left_leg_toe = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _left_leg_toe.setTranslation((6,0,15), space='object')
            self.all_sphere.append(_left_leg_toe)
            return _left_leg_toe
        
        self.left_leg_toe = left_leg_toe()

        @makeroot(suf='connections')
        @makeroot() 
        def left_leg_heel(side = 'l', basename = 'leg_heel', type = 'guide', radius = 1):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _left_leg_heel = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _left_leg_heel.setTranslation((6,0,-6), space='object')
            self.all_sphere.append(_left_leg_heel)
            return _left_leg_heel
        
        self.left_leg_heel = left_leg_heel()

        pm.parent((self.left_leg_thigh[0].getParent()).getParent(), self.left_leg_main_gd[0])
        pm.parent((self.left_leg_knee[0].getParent()).getParent(), self.left_leg_main_gd[0])
        pm.parent((self.left_leg_ankle[0].getParent()).getParent(), self.left_leg_main_gd[0])
        pm.parent((self.left_leg_ball[0].getParent()).getParent(), self.left_leg_ankle[0])
        pm.parent((self.left_leg_toe[0].getParent()).getParent(), self.left_leg_ankle[0])
        pm.parent((self.left_leg_heel[0].getParent()).getParent(), self.left_leg_ankle[0])


        #====================
        #   Right side
        #=====================
        
        self.all_sphere = []
        @makeroot(suf='connections')
        @makeroot()        
        def right_arm_clav(side = 'r', basename = 'arm_clav', type = 'guide', radius = 2):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _right_arm_clav_gd = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _right_arm_clav_gd.setTranslation((-9,100,0), space='object')
            self.all_sphere.append(_right_arm_clav_gd)
            return _right_arm_clav_gd
        
        self.right_arm_clav_gd = right_arm_clav()

        @makeroot(suf='connections')
        @makeroot()        
        def right_arm_elbow(side = 'r', basename = 'arm_elbow', type = 'guide', radius = 2):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _right_arm_elbow_gd = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _right_arm_elbow_gd.setTranslation((-28,100,-1), space='object')
            self.all_sphere.append(_right_arm_elbow_gd)
            return _right_arm_elbow_gd
        
        self.right_arm_elbow_gd = right_arm_elbow()

        @makeroot(suf='connections')
        @makeroot()        
        def right_arm_hand(side = 'r', basename = 'arm_hand', type = 'guide', radius = 1):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _right_arm_hand_gd = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _right_arm_hand_gd.setTranslation((-43,100,-1), space='object')
            self.all_sphere.append(_right_arm_hand_gd)
            return _right_arm_hand_gd
        
        self.right_arm_hand_gd = right_arm_hand()

        @makeroot(suf='connections')
        @makeroot()        
        def right_leg_main(side = 'r', basename = 'leg_main', type = 'guide', radius = 1):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _right_leg_main_gd = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _right_leg_main_gd.setTranslation((-15,64,2), space='object')
            self.all_sphere.append(_right_leg_main_gd)
            return _right_leg_main_gd
        
        self.right_leg_main_gd = right_leg_main()

        @makeroot(suf='connections')
        @makeroot() 
        def right_leg_thigh(side = 'r', basename = 'leg_thigh', type = 'guide', radius = 3):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _right_leg_thigh = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _right_leg_thigh.setTranslation((-6,64,1), space='object')
            self.all_sphere.append(_right_leg_thigh)
            return _right_leg_thigh
        
        self.right_leg_thigh = right_leg_thigh()


        @makeroot(suf='connections')
        @makeroot() 
        def right_leg_knee(side = 'r', basename = 'leg_knee', type = 'guide', radius = 3):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _right_leg_knee = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _right_leg_knee.setTranslation((-6,35,3.7), space='object')
            self.all_sphere.append(_right_leg_knee)
            return _right_leg_knee
        
        self.right_leg_knee = right_leg_knee()


        @makeroot(suf='connections')
        @makeroot() 
        def right_leg_ankle(side = 'r', basename = 'leg_ankle', type = 'guide', radius = 2):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _right_leg_ankle = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _right_leg_ankle.setTranslation((-6,7,0), space='object')
            self.all_sphere.append(_right_leg_ankle)
            return _right_leg_ankle
        
        self.right_leg_ankle = right_leg_ankle()


        @makeroot(suf='connections')
        @makeroot() 
        def right_leg_ball(side = 'r', basename = 'leg_ball', type = 'guide', radius = 1):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _right_leg_ball = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _right_leg_ball.setTranslation((-6,3,6.5), space='object')
            self.all_sphere.append(_right_leg_ball)
            return _right_leg_ball
        
        self.right_leg_ball = right_leg_ball()

        @makeroot(suf='connections')
        @makeroot() 
        def right_leg_toe(side = 'r', basename = 'leg_toe', type = 'guide', radius = 1):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _right_leg_toe = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _right_leg_toe.setTranslation((-6,0,15), space='object')
            self.all_sphere.append(_right_leg_toe)
            return _right_leg_toe
        
        self.right_leg_toe = right_leg_toe()

        @makeroot(suf='connections')
        @makeroot() 
        def right_leg_heel(side = 'r', basename = 'leg_heel', type = 'guide', radius = 1):
            nameStructure = {
                 'Side':side,
                 'Basename': basename,
                 'Type':type,
                 }
            
            _right_leg_heel = pm.sphere(n='{Side}__{Basename}__{Type}'.format(**nameStructure), r = radius)[0]
            _right_leg_heel.setTranslation((-6,0,-6), space='object')
            self.all_sphere.append(_right_leg_heel)
            return _right_leg_heel
        
        self.right_leg_heel = right_leg_heel()
       
        pm.parent((self.right_leg_thigh[0].getParent()).getParent(), self.right_leg_main_gd[0])    
        pm.parent((self.right_leg_knee[0].getParent()).getParent(), self.right_leg_main_gd[0])              
        pm.parent((self.right_leg_ankle[0].getParent()).getParent(), self.right_leg_main_gd[0])       
        pm.parent((self.right_leg_ball[0].getParent()).getParent(), self.right_leg_ankle[0])       
        pm.parent((self.right_leg_toe[0].getParent()).getParent(), self.right_leg_ankle[0])        
        pm.parent((self.right_leg_heel[0].getParent()).getParent(), self.right_leg_ankle[0])

        
        #=======================
        # SPLINE
        #=======================

        @changeColor('index',col=(14))
        def m_spine_guide(col=(0.341, 0.341, 0.341)):
            _spine_curve = pm.curve(p = [([0.0, 64, 0.83]), ([0.0, 66, 1.42]), ([0.0, 72, 2.60]), ([0.0, 79.73, 3.56]), ([0.0, 87.76, 2.65]), ([0.0, 95.43, 1.31]), ([0.0, 100.76, -0.67]), ([0, 103.33, 0])], 
                                    d=3, 
                                    k=[0.0, 0.0, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.0, 1.0],
                                    n='spine_guide__curve')
            
            shapes = _spine_curve.getShape()                

            pm.PyNode(shapes).overrideEnabled.set(1)
            pm.PyNode(shapes).overrideRGBColors.set(1)
            pm.PyNode(shapes).overrideColorRGB.set(col)

            return _spine_curve
            
        self.spine_curve = m_spine_guide() 
        
        self.all_guide.extend(self.left_arm_clav_gd)
        self.all_guide.extend(self.right_arm_clav_gd)
        self.all_guide.extend(self.left_arm_elbow_gd)
        self.all_guide.extend(self.right_arm_elbow_gd)
        self.all_guide.extend(self.left_arm_hand_gd)
        self.all_guide.extend(self.right_arm_hand_gd)
        self.all_guide.extend(self.left_leg_thigh)
        self.all_guide.extend(self.right_leg_thigh)
        self.all_guide.extend(self.left_leg_knee)
        self.all_guide.extend(self.right_leg_knee)
        self.all_guide.extend(self.left_leg_ankle)
        self.all_guide.extend(self.right_leg_ankle)
        self.all_guide.extend(self.left_leg_ball)
        self.all_guide.extend(self.right_leg_ball)
        self.all_guide.extend(self.left_leg_toe)
        self.all_guide.extend(self.right_leg_toe)        
        self.all_guide.extend(self.left_leg_heel)
        self.all_guide.extend(self.right_leg_heel)
        
    def connections(self):
        def connect(subject1, subject2):
            for sub1, sub2, in zip (subject1, subject2):
                pm.PyNode(sub1).translateZ >> pm.PyNode(sub2).translateZ
                pm.PyNode(sub1).translateY >> pm.PyNode(sub2).translateY
                _rev = pm.shadingNode('reverse', asUtility=True, n = '{}__rev_'.format(sub1))
                pm.PyNode(sub1).tx >> _rev.inputX
                _rev.outputX >> pm.PyNode(sub2).tx                                    
        
        connect(self.left_arm_clav_gd, pm.listRelatives(self.right_arm_clav_gd[0],ap=1))
        connect(self.right_arm_clav_gd, pm.listRelatives(self.left_arm_clav_gd[0],ap=1))
        
        connect(self.left_arm_elbow_gd, pm.listRelatives(self.right_arm_elbow_gd[0],ap=1))
        connect(self.right_arm_elbow_gd, pm.listRelatives(self.left_arm_elbow_gd[0],ap=1))

        connect(self.left_arm_hand_gd, pm.listRelatives(self.right_arm_hand_gd[0],ap=1))
        connect(self.right_arm_hand_gd, pm.listRelatives(self.left_arm_hand_gd[0],ap=1))

        connect(self.left_leg_main_gd, pm.listRelatives(self.right_leg_main_gd[0],ap=1))
        connect(self.right_leg_main_gd, pm.listRelatives(self.left_leg_main_gd[0],ap=1))

        connect(self.left_leg_thigh, pm.listRelatives(self.right_leg_thigh[0],p=1))
        connect(self.right_leg_thigh, pm.listRelatives(self.left_leg_thigh[0],p=1))

        connect(self.left_leg_knee, pm.listRelatives(self.right_leg_knee[0],p=1))
        connect(self.right_leg_knee, pm.listRelatives(self.left_leg_knee[0],p=1))

        connect(self.left_leg_ankle, pm.listRelatives(self.right_leg_ankle[0],p=1))
        connect(self.right_leg_ankle, pm.listRelatives(self.left_leg_ankle[0],p=1))

        connect(self.left_leg_ball, pm.listRelatives(self.right_leg_ball[0],p=1))
        connect(self.right_leg_ball, pm.listRelatives(self.left_leg_ball[0],p=1))

        connect(self.left_leg_toe, pm.listRelatives(self.right_leg_toe[0],p=1))
        connect(self.right_leg_toe, pm.listRelatives(self.left_leg_toe[0],p=1))
        
        connect(self.left_leg_heel, pm.listRelatives(self.right_leg_heel[0],p=1))
        connect(self.right_leg_heel, pm.listRelatives(self.left_leg_heel[0],p=1))    
       
        pm.select(self.right_arm_clav_gd[0].getParent().getParent())
        pm.move(pm.selected()[0],-2, 0, 0, r=1)

        pm.select(self.right_arm_elbow_gd[0].getParent().getParent())
        pm.move(pm.selected()[0],-2, 0, 0, r=1)

        pm.select(self.right_arm_hand_gd[0].getParent().getParent())
        pm.move(pm.selected()[0],-2, 0, 0, r=1)        
        
        pm.select(self.right_leg_main_gd[0].getParent().getParent())
        pm.move(pm.selected()[0],-4, 0, 0, r=1)
        
    def jointsSetup(self):    
        self.all_locs = []   
        self.all_joint = []
        for each in self.all_guide:
            _joint = pm.joint(n=each.name().replace('guide','jnt__'))
            _loc = pm.spaceLocator(n=each.name().replace('guide','loc__'))
            pm.PyNode(_loc).getShape().localScaleX.set(0.2)
            pm.PyNode(_loc).getShape().localScaleY.set(0.2)
            pm.PyNode(_loc).getShape().localScaleZ.set(0.2)
            adb.changeColor_func(_loc, 'index', 14)
            pm.parent(_joint, w=True)            
            self.all_joint.append(_joint)
            self.all_locs.append(_loc)

        for joint, guide in zip(self.all_joint, self.all_guide):
            pm.matchTransform(joint, guide, pos=True) 
            pm.parent(joint,guide)

        for loc, guide in zip(self.all_locs, self.all_guide):
            pm.matchTransform(loc, guide, pos=True) 
            pm.parentConstraint(guide,loc)
        pm.select(None)
                
        ## SCALING
        scaling_grp = pm.group(em=True,n='scaling__grp__')
        pm.parent('l__arm_clav__guide__root__grp__', 'l__arm_elbow__guide__root__grp__', 'l__arm_hand__guide__root__grp__', 'l__leg_main__guide__root__grp__', 'r__arm_clav__guide__root__grp__', 'r__arm_elbow__guide__root__grp__', 'r__arm_hand__guide__root__grp__', 'r__leg_main__guide__root__grp__', 'spine_guide__curve',scaling_grp)
        pm.PyNode(scaling_grp).setScale((0.05,0.05,0.05)) 
        pm.parent(w=True)
        pm.delete(scaling_grp)
        ## -----------------------------------------------

        ## SPINE SUITE
        pm.select(self.spine_curve, r=True)
        sel = pm.select(".cv[*]")
        cvs = pm.filterExpand(fullPath=True, sm=28)
        # Nombre de vertex sur la curve #
        nbCvs=len(cvs)
        oCollClusters = [pm.cluster(cvs[x]) for x in range(0,nbCvs)]            

        self.all_spine_guide = []
        for clus in oCollClusters:
            clus[1].v.set(0)
            spine_guide = pm.sphere(n='m__spine__guide_01',r = 0.05)[0]
            self.all_spine_guide.append(spine_guide)
            pm.matchTransform(spine_guide, clus, pos=True)

        for oClus, spine in zip(oCollClusters,self.all_spine_guide):
            pm.parentConstraint(spine,oClus)

        for spine_guide in self.all_spine_guide:
            pm.select(spine_guide)
            mc.FreezeTransformations()

        pm.PyNode(self.all_spine_guide[1]).v.set(0)
        pm.PyNode(self.all_spine_guide[-2]).v.set(0)

        cluster_grp = pm.group(oCollClusters,n='spine_cls__grp__', w=1)
        all_spine_guide_grp = pm.group(self.all_spine_guide,n='spine_guide__grp__', w=1)

        self.all_guide.extend(self.all_spine_guide)
        

        ## Hide loc 
        self.locs_grp = pm.group(n='x__locs_pos__grp__')
        pm.parent(self.all_locs, self.locs_grp)
        pm.PyNode(self.locs_grp).v.set(0)                
    
        ## associate shader
        spine_shader = pm.shadingNode('lambert', asShader=True, n = 'yellow_guide_shader')
        pm.setAttr(spine_shader+".incandescence", 0, 0.42, 0.06, type='double3')

        pm.select(pm.ls(type='nurbsSurface'))

        for spine_guide in pm.selected():
            pm.select(spine_guide)
            pm.hyperShade(assign=spine_shader)
            
        @changeColor('index',col=(14))
        def create_curve():

            _curve_arm_1 = pm.curve(p=[(2.2,5,-0.05), (1.45,5,-0.05)], k = [0,1], d=1 )
            _curve_arm_2 = pm.curve(p=[(1.45,5,-0.05), (0.5,5,0)], k = [0,1], d=1 )

            _curve_arm_4 = pm.curve(p=[(-2.2,5,-0.05), (-1.45,5,-0.05)], k = [0,1], d=1 )
            _curve_arm_5 = pm.curve(p=[(-1.45,5,-0.05), (-0.5,5,0)], k = [0,1], d=1 )
            
            r_leg_thigh_curve = pm.curve(p=[(-0.4, 3.2, 0.05),(-0.4, 1.75, 0.185)], k=[0,  1], d=1)
            l_leg_thigh_curve = pm.curve(p=[(0.4, 3.2, 0.05),(0.4, 1.75, 0.185)], k=[0,  1], d=1)
            
            r_leg_knee_curve = pm.curve(p=[(-0.4, 1.75, 0.185), (-0.4, 0.35, 0)], k=[0, 1], d=1)
            l_leg_knee_curve = pm.curve(p=[(0.4, 1.75, 0.185), (0.4, 0.35, 0)], k=[0, 1], d=1)

            all_curves = [_curve_arm_1, _curve_arm_2, _curve_arm_4, _curve_arm_5, r_leg_thigh_curve, l_leg_thigh_curve, r_leg_knee_curve, l_leg_knee_curve]

            self.curves_grp = pm.group(em=True,n='x__curves__grp__', w=True)
            
            pm.select(self.all_joint, r =True)
            pm.select(all_curves, add=True)
            
            mc.SmoothBindSkin()
                
            pm.parent(_curve_arm_1, 
                      _curve_arm_2,
                      _curve_arm_4,
                      _curve_arm_5,
                      r_leg_thigh_curve,
                      l_leg_thigh_curve,
                      r_leg_knee_curve,
                      l_leg_knee_curve,
                      self.spine_curve,
                      cluster_grp,
                      self.curves_grp
                      )
                      
            return self.curves_grp                 
        create_curve()
    
        guide_scale_grp = pm.group(em=True,n='x__guide__grp__')  
        pm.parent('l__arm_clav__guide__root__grp__', 
                  'l__arm_elbow__guide__root__grp__', 
                  'l__arm_hand__guide__root__grp__',
                  'l__leg_main__guide__root__grp__', 
                  'r__arm_clav__guide__root__grp__', 
                  'r__arm_elbow__guide__root__grp__', 
                  'r__arm_hand__guide__root__grp__',
                  'r__leg_main__guide__root__grp__',
                  'spine_guide__grp__',
                  guide_scale_grp
                  )      
    
        return guide_scale_grp

    def hiearchySetup(self):
        pass


    def mainCtrls(self):
        @makeroot()
        @changeColor(type = 'index', col = (17))
        def mainCtrl():
            main_ctrl = sl.main_shape()        
            return main_ctrl            
        @makeroot()    
        @changeColor(type = 'index', col = (18))
        def mainCtrl_offset():
            main_ctrl_offset = sl.circleY_shape()    
            main_ctrl_offset.setScale((1.82,1.82,1.82)) 
            mc.FreezeTransformations() 
            return main_ctrl_offset   

        self.main_ctrl = mainCtrl()[0] 
        self.main_ctrl_offset = mainCtrl_offset()[0]  

        pm.parent(pm.PyNode(self.main_ctrl_offset).getParent(), self.main_ctrl)
        pm.scaleConstraint(self.main_ctrl_offset, self.guide_scale_grp )
        pm.parentConstraint(self.main_ctrl_offset, self.guide_scale_grp )

    def cleanUp(self):    
        guide_grp = pm.group(em=True, n = 'x__guide_autoRig__grp__')
        pm.parent(self.guide_scale_grp,
                  self.curves_grp,
                  self.locs_grp,
                  'main_ctrl__root__grp__',                  
                  guide_grp)
                  
        pm.parent(self.all_spine_guide[1],self.all_spine_guide[0])
        pm.parent(self.all_spine_guide[-2],self.all_spine_guide[-1])
        
        
                                                
# f = autoRigGuide()        
      

