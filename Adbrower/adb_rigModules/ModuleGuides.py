import sys
import os
import ConfigParser
import pymel.core as pm

from CollDict import indexColor, attrDic
from adbrower import lockAttr, makeroot, changeColor
import ShapesLibrary as sl

import adb_core.NameConv_utils as NC
import adb_core.Class__AddAttr as adbAttr
import adb_core.Class__Locator as Locator
import adb_core.Class__Control as Control

import adbrower
adb = adbrower.Adbrower()


PROJECT_DATA_PATH = '/'.join(pm.sceneName().split('/')[:-2]) + '/data/'

# ====================================
# CLASS
# ===================================


class ModuleGuides(object):


    def __init__(self, prefix = 'Audrey', guides=[], path=PROJECT_DATA_PATH):
        if isinstance(guides , str):
            self.guides = [pm.PyNode(guides)]
        elif isinstance(guides , list):
            self.guides = [pm.PyNode(x) for x in guides]
        else:
            self.guides = [pm.PyNode(guides)]

        self.locInstance = Locator.Locator(self.guides)
        self.RIG_NAME = prefix
        self.PATH = path
        self.FOLDER_NAME = self.RIG_NAME + '_DATA'
        self.DATA_PATH = self.PATH + self.FOLDER_NAME
        self.registeredAttributes = []


    @classmethod
    def createFkGuide(cls, prefix='',  guides=[]):
        cls.locInstance = Locator.Locator.create(name='{}__GLOC'.format(prefix, NC.LOC))
        cls.locInstance.AddSeparator(cls.locInstance.locators[0])
        cls.locInstance.addAttr('Shape', 'enum',  eName = sl.sl.keys())
        cls.locInstance.setDefault('Shape', 4)
        cls.locInstance.addAttr('Color', 'enum',  eName = ['auto'] + indexColor.keys())
        cls.locInstance.AddSeparator(cls.locInstance.locators[0])
        adb.changeColor_func(cls.locInstance.locators, 'index', indexColor['lightGrey'])
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            cls.locInstance.addAttr('enable_{}'.format(attr), True)
        return cls(prefix, cls.locInstance.locators)


    def exportData(self, path=None):
        FILE_NAME = self.RIG_NAME + '__GLOC'
        if path is None:
            path = self.PATH

        if os.path.exists(path + '/' + self.FOLDER_NAME + '/'):
            os.chdir(path)
        else:
            os.mkdir(path + '/' + self.FOLDER_NAME + '/')
            os.chdir(path + '/' + self.FOLDER_NAME + '/')
        os.chdir(path + '/' + self.FOLDER_NAME + '/')
        self.DATA_PATH = path + self.FOLDER_NAME + '/'

        with open("{}.ini".format(FILE_NAME),"w+") as wf:
            for guide in self.guides:
                wf.write('[{}] \n'.format(guide))
                for translate in attrDic['Translate']:
                    wf.write(translate + '=' + str(pm.getAttr('{}.{}'.format(guide, translate))) + '\n')
                    self.registeredAttributes.append(translate)

                for rotate in attrDic['Rotate']:
                    wf.write(rotate + '=' + str(pm.getAttr('{}.{}'.format(guide, rotate))) + '\n')
                    self.registeredAttributes.append(rotate)

                for scale in attrDic['Scale']:
                    wf.write(scale + '=' + str(pm.getAttr('{}.{}'.format(guide, scale))) + '\n')
                    self.registeredAttributes.append(scale)

                for key, value in zip(self.locInstance.list_methods.keys(), self.locInstance.list_methods.values()):
                    wf.write(str(key) + '=' + str(pm.getAttr('{}.{}'.format(guide, key))) + '\n')
                    self.registeredAttributes.append(key)

                wf.write('registeredAttributes' + '=' + str(self.registeredAttributes) + '\n')
        wf.close()


    def readData(self, path=None):
        config = ConfigParser.ConfigParser()
        config.read(path)
        return config



# =========================
# BUILD
# =========================


# test = ModuleGuides.createFkGuide('test')
# test.exportData()

# aaa = ModuleGuides('TEST',['Locator1', 'Locator2', 'Locator3'], 'C:/Users/Audrey/Desktop/')
# aaa.exportData()