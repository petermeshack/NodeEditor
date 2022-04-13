import json
import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from nodeeditor.node_editor_widget import NodeEditorWidget


class NodeEditorWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.filename = None
        self.initUI()


    def createAction(self, name, shortcut, tooltip, callback):
        act = QAction(name, self)
        act.setShortcut(shortcut)
        act.setToolTip(tooltip)
        act.triggered.connect(callback)
        return act

    def initUI(self):

        menubar = self.menuBar()

        # initialize menu
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(self.createAction('&New', 'Ctrl+N', "Create new graph", self.onFileNew))
        filemenu.addSeparator()
        filemenu.addAction(self.createAction('&Open', 'Ctrl+O', "Open file", self.onFileOpen))
        filemenu.addAction(self.createAction('&Save', 'Ctrl+S', "Save file", self.onFileSave))
        filemenu.addAction(self.createAction('Save &As', 'Ctrl+Shift+S', "Save File As", self.onFileSaveAs))
        filemenu.addSeparator()
        filemenu.addAction(self.createAction('&Exit', 'Ctrl+Q', "Exit Application", self.close))

        editmenu = menubar.addMenu("Edit")
        editmenu.addAction(self.createAction('&Undo', 'Ctrl+Z', "Undo last Operation", self.onEditUndo))
        editmenu.addAction(self.createAction('&Redo', 'Ctrl+Shift+Z', "Redo Operation", self.onEditRedo))
        editmenu.addSeparator()
        editmenu.addAction(self.createAction('Cu&t', 'Ctrl+X', "Cut from Clipboard", self.onEditCut))
        editmenu.addAction(self.createAction('&Copy', 'Ctrl+C', "Copy to Clipboard", self.onEditCopy))
        editmenu.addAction(self.createAction('&Paste', 'Ctrl+V', "Paste to Clipboard", self.onEditPaste))
        editmenu.addSeparator()
        editmenu.addAction(self.createAction('&Delete', 'Del', "Delete Selected Item", self.onEditDelete))

        nodeeditor = NodeEditorWidget(self)
        nodeeditor.scene.addHasBeenModifiedListener(self.changeTitle)
        self.setCentralWidget(nodeeditor)

        # status bar
        self.statusBar().showMessage("")
        self.status_mouse_pos = QLabel("")
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
        nodeeditor.view.scenePosChanged.connect(self.onscenePosChanged)

        # set window properties
        self.setGeometry(200, 100, 800, 600)
        self.changeTitle()
        self.show()

    def changeTitle(self):
        title = "Node Edditor - "
        if self.filename is None:
            title += "New"
        else:
            title += os.path.basename(self.filename)

        if self.centralWidget().scene.has_been_modified:
            title += "*"
        self.setWindowTitle(title)

    def closeEvent(self, event):
        if self.maybeSaved():
           event.accept()
        else:
          event.ignore()

    def isModified(self):
        return self.centralWidget().scene.has_been_modified

    def maybeSaved(self):
        if not self.isModified():
            return True
        res = QMessageBox.warning(self, "Save your work?",
                                  "the file has been modified,\n Do you want to save your changes?",
                                  QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                                  )
        if res == QMessageBox.Save:
            return self.onFileSave()
        elif res == QMessageBox.Cancel:
            return False
        return True



    def onscenePosChanged(self, x, y):
        self.status_mouse_pos.setText("Scene Pos: [%d, %d]" % (x, y))

    def onFileNew(self):
        if self.maybeSaved():
            self.centralWidget().scene.clear()
            self.filename = None
            self.changeTitle()


    def onFileOpen(self):
        if self.maybeSaved():
            fname, filter, = QFileDialog.getOpenFileName(self, "Open Graph from file")
            if fname == '':
                return
            if os.path.isfile(fname):
                self.centralWidget().scene.loadFromFile(fname)
                self.filename = fname
                self.changeTitle()

    def onFileSave(self):
        if self.filename is None: return self.onFileSaveAs()
        self.centralWidget().scene.saveToFile(self.filename)
        self.statusBar().showMessage("File saved Successfully as %s" % self.filename)
        return True

    def onFileSaveAs(self):
        fname, filter, = QFileDialog.getSaveFileName(self, "Save Graph to file")
        if fname == '':
            return False
        self.filename = fname
        self.onFileSave()
        return True

    def onEditUndo(self):
        self.centralWidget().scene.history.undo()

    def onEditRedo(self):
        self.centralWidget().scene.history.redo()

    def onEditDelete(self):
        self.centralWidget().scene.grScene.views()[0].deleteSelected()

    def onEditCut(self):
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=True)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)

    def onEditCopy(self):
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=False)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self):
        raw_data = QApplication.instance().clipboard().text()
        try:
            data = json.loads(raw_data)
        except ValueError as e:
            print("pasting of non valid json", e)
            return

        # check if json data are correct
        if 'nodes' not in data:
            print("JSON doesnt contain nodes")
            return
        self.centralWidget().scene.clipboard.deserializeFromClipboard(data)
