from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from node_edge import Edge,EDGE_TYPE_BEZIER
from node_node import Node
from node_scene import Scene

from node_graphics_view import QDMGraphicsView

DEBUG = True


class NodeEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.stylesheet_filename = 'qss/nodestyle.qss'
        self.loadStylesheet(self.stylesheet_filename)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # create graphics scene
        self.scene = Scene()

        self.addNodes()

        # create graphics view
        self.view = QDMGraphicsView(self.scene.grScene, self)
        self.layout.addWidget(self.view)



    def addNodes(self):
        node = Node(self.scene, "My new Node ", inputs=[0, 1, 6], outputs=[1])
        node1 = Node(self.scene, "My new Node1", inputs=[0, 2, 7], outputs=[1])
        node2 = Node(self.scene, "My new Node2", inputs=[4, 3, 5], outputs=[1])

        node.setPos(-350, -250)
        node1.setPos(-75, 0)
        node2.setPos(200, -150)

        edge1 = Edge(self.scene, node.outputs[0], node1.inputs[0], edge_type=EDGE_TYPE_BEZIER)
        edge2 = Edge(self.scene, node1.outputs[0], node2.inputs[2], edge_type=EDGE_TYPE_BEZIER)

    def loadStylesheet(self, filename):
        if DEBUG: print("STYLE loading:", filename)
        file = QFile(filename)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf8'))
