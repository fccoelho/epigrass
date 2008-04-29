
import sys
from PyQt4 import QtGui, QtCore, QtOpenGL
import elasticnodes as EN
import math

class MainWindow(QtGui.QGraphicsView):
    def __init__(self,parent = None,name = None,fl = 0):
        QtGui.QGraphicsView.__init__(self)

        self.timerId = 0
        scene = QtGui.QGraphicsScene(self)
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        scene.setSceneRect(-200, -200, 400, 400)
        self.setScene(scene)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

        self.scale(0.8, 0.8)
        self.setMinimumSize(400, 400)
        self.setWindowTitle(self.tr("Simulation Display"))


        # test code
##        self.node1 = Node(self.canvas, pos=(10,10,2))
##        self.node2 = Node(self.canvas,pos=(100,100,2))
##        self.edge = Edge(self.canvas,(10,10,100,100))
#        self.map = Map('limites.map',self.canvas)
#        self.canvas.update()
#        self.view.resize(self.view.sizeHint())
    def itemMoved(self):
        if not self.timerId:
            self.timerId = self.startTimer(1000 / 25)

    def keyPressEvent(self, event):
        key = event.key()

        if key == QtCore.Qt.Key_Up:
            self.centerNode.moveBy(0, -20)
        elif key == QtCore.Qt.Key_Down:
            self.centerNode.moveBy(0, 20)
        elif key == QtCore.Qt.Key_Left:
            self.centerNode.moveBy(-20, 0)
        elif key == QtCore.Qt.Key_Right:
            self.centerNode.moveBy(20, 0)
        elif key == QtCore.Qt.Key_Plus:
            self.scaleView(1.2)
        elif key == QtCore.Qt.Key_Minus:
            self.scaleView(1 / 1.2)
        elif key == QtCore.Qt.Key_Space or key == QtCore.Qt.Key_Enter:
            for item in self.scene().items():
                if isinstance(item, Node):
                    item.setPos(-150 + QtCore.qrand() % 300, -150 + QtCore.qrand() % 300)
        else:
            QtGui.QGraphicsView.keyPressEvent(self, event)

    def timerEvent(self, event):
        nodes = [item for item in self.scene().items() if isinstance(item, Node)]

        for node in nodes:
            node.calculateForces()

        itemsMoved = False
        for node in nodes:
            if node.advance():
                itemsMoved = True

        if not itemsMoved:
            self.killTimer(self.timerId)
            self.timerId = 0

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 240.0))

    def drawBackground(self, painter, rect):
        # Shadow.
        sceneRect = self.sceneRect()
        rightShadow = QtCore.QRectF(sceneRect.right(), sceneRect.top() + 5, 5, sceneRect.height())
        bottomShadow = QtCore.QRectF(sceneRect.left() + 5, sceneRect.bottom(), sceneRect.width(), 5)
        if rightShadow.intersects(rect) or rightShadow.contains(rect):
            painter.fillRect(rightShadow, QtCore.Qt.darkGray)
        if bottomShadow.intersects(rect) or bottomShadow.contains(rect):
            painter.fillRect(bottomShadow, QtCore.Qt.darkGray)

        # Fill.
        gradient = QtGui.QLinearGradient(sceneRect.topLeft(), sceneRect.bottomRight())
        gradient.setColorAt(0, QtCore.Qt.white)
        gradient.setColorAt(1, QtCore.Qt.lightGray)
        painter.fillRect(rect.intersect(sceneRect), QtGui.QBrush(gradient))
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(sceneRect)

        # Text.
        textRect = QtCore.QRectF(sceneRect.left() + 4, sceneRect.top() + 4,
                                 sceneRect.width() - 4, sceneRect.height() - 4)
        message = self.tr("Click and drag the nodes around, and zoom with the "
                          "mouse wheel or the '+' and '-' keys")

        font = painter.font()
        font.setBold(True)
        font.setPointSize(14)
        painter.setFont(font)
        painter.setPen(QtCore.Qt.lightGray)
        painter.drawText(textRect.translated(2, 2), message)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(textRect, message)

    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        if factor < 0.07 or factor > 100:
            return

        self.scale(scaleFactor, scaleFactor)
#class Canvas(QtGui.QCanvas):
#    pass

class Node(EN.Node):
    def __init__(self,display,width=50.,height=50., name='Node',pos=(1,1,2),color=(0.,255.,0.)):
        self.parent.__init__(display)

    def setLabel(self,canvas,text,pos):
        """
        Set the node label
        """
        x,y,z = pos
        l = QCanvasText(canvas)
        l.setText(text)
        l.setColor(Qt.black)
        l.setFont(QFont('Times',12,50))
        painter = QPainter()
        self.setX(float(x))
        self.setY(float(y))
        self.setZ(float(1))
        l.show()
        return l

class Line(QtCore.QLineF):
    def __init__(self,display, points, painter,color=(0,0,0)):
        self.parent.__init__(points[0],points[1])

        if self.length() == 0.0:
            return
        #draw Line
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawLine(self)

class Edge(EN.Edge):
    def __init__(self,sourcenode,destnode):
        self.parent.__init__(sourcenode,destnode)

class Map:
    """
    Draws maps as poligons
    """
    def __init__(self,fname, canvas):
        #self.display = visual.display(title='Brasil', ambient=0.5)
        self.canvas = canvas
        self.Reader(fname)


    def Reader(self, fname):
        """
        Reads Grass 5.x ascii vector files.
        """
        f = open(fname,'r')
        all = f.readlines()
        f.close()
        pol = []
        inicioP = [all.index(i) for i in all if i.startswith('B')]
        for i in inicioP:
            size = int(all[i].split()[-1])
            a = [i.split() for i in all[i+1:i+1+size]]
            #print a
            for n,i in enumerate(a[:-1]):
                x1,y1,x2,y2 = float(i[1]),float(i[0]),float(a[n+1][1]),float(a[n+1][0])
                Line(self.canvas,(850+10*x1,-10*y1+50,850+10*x2,-10*y2+50))
            #self.dbound(pta) #Draws the polygon
        self.canvas.update()

    def dbound(self,pol):
        """
        Draws a polygon
        pol: list of points forming the polygon
        canvas: Canvas where it'll be drawn
        """
        P = QCanvasPolygon(self.canvas)
        P.setPen(QPen(Qt.black,10))
        P.setPoints(pol)
        P.show()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    QtCore.QObject.connect(app,QtCore.SIGNAL("lastWindowClosed()"),app,QtCore.SLOT("quit()"))
    w = MainWindow()
#    app.setMainWidget(w)
    w.show()
    sys.exit(app.exec_())
    
