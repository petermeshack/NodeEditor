from PyQt5.QtWidgets import *
from nodeeditor.node_node import Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode



class CalcGraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 160
        self.height = 74
        self.edge_size = 5
        self.padding = 8


class CalcContent(QDMNodeContentWidget):
    def initUI(self):
        lbl = QLabel("", self)


class CalcNode(Node):
    def __init__(self, scene, op_code, op_title, inputs=[2, 2], outputs=[1]):
        self.op_code = op_code
        self.op_title = op_title

        super().__init__(scene, self.op_title, inputs, outputs)

    def initInnerClasses(self):
        self.content = QDMNodeContentWidget(self)
        self.grNode = QDMGraphicsNode(self)
