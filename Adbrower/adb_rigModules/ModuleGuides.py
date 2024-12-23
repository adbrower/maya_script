import sys
import os
import configparser
import pymel.core as pm
import importlib

from CollDict import indexColor, attrDic
from adbrower import lockAttr, makeroot, changeColor
import ShapesLibrary as sl

import adb_core.NameConv_utils as NC
import adb_core.Class__AddAttr as adbAttr
import adb_core.Class__Locator as Locator
import adb_core.Class__Control as Control

import adbrower
adb = adbrower.Adbrower()

importlib.reload(Locator)


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
        self.DATA_PATH = str(self.PATH) + str(self.FOLDER_NAME)
        self.registeredAttributes = []


    @classmethod
    def createFkGuide(cls, prefix='',  guides=[], padding=None):
        cls.locInstance = Locator.Locator.create(name='{}'.format(prefix), padding=padding)
        [pm.rename(loc, loc.replace('LOC', 'GLOC')) for loc in cls.locInstance.locators]
        cls.locInstance.AddSeparator(cls.locInstance.locators[0])
        cls.locInstance.addAttr('Shape', 'enum',  eName = sl.sl.keys())
        cls.locInstance.setDefault('Shape', 4)
        cls.locInstance.addAttr('Color', 'enum',  eName = ['auto'] + indexColor.keys())
        cls.locInstance.AddSeparator(cls.locInstance.locators[0])
        adb.changeColor_func(cls.locInstance.locators, 'index', indexColor['lightGrey'])
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            cls.locInstance.addAttr('enable_{}'.format(attr), True)

        cls.list_methods = cls.locInstance.list_methods
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

                for index, translate in enumerate(attrDic['Translate']):
                    wf.write(translate + '=' + str(pm.xform('{}'.format(guide), rp=True , q=True , ws=True)[index]) + '\n')
                    self.registeredAttributes.append(translate)

                for rotate in attrDic['Rotate']:
                    wf.write(rotate + '=' + str(pm.getAttr('{}.{}'.format(guide, rotate))) + '\n')
                    self.registeredAttributes.append(rotate)

                for scale in attrDic['Scale']:
                    wf.write(scale + '=' + str(pm.getAttr('{}.{}'.format(guide, scale))) + '\n')
                    self.registeredAttributes.append(scale)

                for key, value in zip(self.list_methods.keys(), self.list_methods.values()):
                    wf.write(str(key) + '=' + str(pm.getAttr('{}.{}'.format(guide, key))) + '\n')
                    self.registeredAttributes.append(key)

                wf.write("parent={} \n".format(pm.PyNode(guide).getParent()))
                for index, value in enumerate(sl.sl.keys()):
                    if index == int(pm.getAttr('{}.Shape'.format(guide))):
                        wf.write("shape=" + str([value, index]) + '\n')

                for index, value in enumerate(['auto'] + indexColor.keys()):
                    if index == int(pm.getAttr('{}.Color'.format(guide))):
                        wf.write("color=" + str([value, index]) + '\n')

                wf.write('registeredAttributes' + '=' + str(list(set(self.registeredAttributes))) + '\n')
        wf.close()
        return self.DATA_PATH


    def loadData(self, path=None):
        config = configparser.ConfigParser()
        config.read(path)
        return config



# =========================
# BUILD
# =========================


# test = ModuleGuides.createFkGuide('test')
# test.exportData()

# aaa = ModuleGuides('TEST',['Locator1', 'Locator2', 'Locator3'], 'C:/Users/Audrey/Desktop/')
# aaa.exportData()