# test FrameLayout
try:
	import PySide2.QtCore as QtCore
	import PySide2.QtWidgets as QtWidgets
	import PySide2.QtGui as QtGui
except:
	print('Fail to import PySide2')
	import PySide.QtCore as QtCore
	import PySide.QtGui as QtWidgets
	import PySide.QtGui as QtGui

class frameLayout(QtWidgets.QFrame):
    def __init__(self,parent = None):
        QtWidgets.QFrame.__init__(self,parent = parent)

        self.mainLayout = None
        self.titleFrame = None
        self.contentFrame = None
        self.contentLayout = None
        self.isCollapsed = False
        self.title = ''
        self.colorText = '#c9c9c9'

        # init frame layout
        self.initFrameLayout()
        
    def initFrameLayout(self):
        # main layout
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)
        self.setLayout(self.mainLayout)
        # title frame
        self.titleFrame = QtWidgets.QFrame()
        self.titleFrame.setContentsMargins(1,1,1,1)
        self.titleFrame.setFixedHeight(22)

        # titlePalette = QtGui.QPalette()
        # titlePalette.setColor(titlePalette.Background,QtGui.QColor('#81DAF5'))
        # self.titleFrame.setAutoFillBackground(True)
        # self.titleFrame.setPalette(titlePalette)

        self.mainLayout.addWidget(self.titleFrame)
        # content frame
        self.contentFrame = QtWidgets.QFrame()
        self.contentFrame.setContentsMargins(0,0,0,0)
        #self.contentFrame.setFrameStyle(self.contentFrame.StyledPanel|self.contentFrame.Plain)
        self.mainLayout.addWidget(self.contentFrame)
        # content layout
        self.contentLayout = QtWidgets.QVBoxLayout()
        self.contentLayout.setContentsMargins(5,5,5,5)
        self.contentLayout.setSpacing(2)
        self.contentFrame.setLayout(self.contentLayout)

    def expandCollapseRect(self):
        """ area where the toggle happen"""
        return QtCore.QRect(0,0,self.titleFrame.rect().width(),self.titleFrame.rect().height())
      
    def mousePressEvent(self,event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton and self.expandCollapseRect().contains(event.pos()):
            if self.isCollapsed == False:
                self.isCollapsed = True
                # self.setMinimumHeight(22)
                # self.setMaximumHeight(22)
                self.contentFrame.setVisible(False)
                # print('Hide')
            else:
                self.isCollapsed = False
                # self.setMinimumHeight(22)
                # self.setMaximumHeight(10000)
                self.contentFrame.setVisible(True)
                # print('vis')
            event.accept()
        else:
            event.ignore()

    def addWidget(self,widget):
        self.contentLayout.addWidget(widget)

                
    def addLayout(self,layout):
        self.contentLayout.addLayout(layout)        
        

    def paintEvent(self,event):
        painter = QtGui.QPainter()
        painter.setRenderHint(painter.Antialiasing)
        painter.begin(self)
        
        self.drawText(painter)
        self.drawTriangle(painter)

        painter.end()

    def drawText(self,painter):
        painter.setPen(QtGui.QColor('#333333'))
        painter.setBrush(QtGui.QColor('#333333'))
        painter.drawRect(0,0,self.titleFrame.rect().width(),self.titleFrame.rect().height())

        font = QtGui.QFont('Alias',8)
        font.setBold(False)
        painter.setPen(QtGui.QColor(self.colorText))
        painter.setFont(font)
        painter.drawText(26,6,self.titleFrame.rect().width(),50,QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop,self.title)


    def drawTriangle(self,painter):
        if self.isCollapsed:
            tl,tr,tp = QtCore.QPoint(11,6),QtCore.QPoint(16,11),QtCore.QPoint(11,16)
        else:
            tl,tr,tp = QtCore.QPoint(9,8),QtCore.QPoint(19,8),QtCore.QPoint(14,13)

        points = [tl,tr,tp]
        triangle = QtGui.QPolygon(points)
        painter.setPen(QtGui.QColor('#c9c9c9'))
        painter.setBrush(QtGui.QColor('#c9c9c9'))
        painter.drawPolygon(triangle)


