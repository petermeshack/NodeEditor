from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from nodeeditor.node_editor_widget import NodeEditorWidget


class CulculatorSubWindow(NodeEditorWidget):
    def __init__(self):
        super().__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setTitle()
        self.scene.addHasBeenModifiedListener(self.setTitle)

    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFilename())
