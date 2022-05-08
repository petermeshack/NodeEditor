import json
import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from nodeeditor.node_editor_widget import NodeEditorWidget


class NodeEditorWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.name_company = "Pmesh"
        self.name_product = "NodeEditor"


        self.initUI()

    def initUI(self):

        self.createActions()
        self.createMenus()

        self.nodeeditor = NodeEditorWidget(self)
        self.nodeeditor.scene.addHasBeenModifiedListener(self.setTitle)
        self.setCentralWidget(self.nodeeditor)
        self.createStatusBar()

        # status bar
        self.statusBar().showMessage("")
        self.status_mouse_pos = QLabel("")
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
        self.nodeeditor.view.scenePosChanged.connect(self.onscenePosChanged)

        # set window properties
        self.setGeometry(200, 100, 800, 600)
        self.setTitle()
        self.show()

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def createActions(self):

        self.actNew = QAction('&New', self, shortcut='Ctrl+N', statusTip="Create new graph", triggered=self.onFileNew)
        self.actOpen = QAction('&Open', self, shortcut='Ctrl+O', statusTip="Open file", triggered=self.onFileOpen)
        self.actSave = QAction('&Save', self, shortcut='Ctrl+S', statusTip="Save file", triggered=self.onFileSave)
        self.actSaveAs = QAction('Save &As', self, shortcut='Ctrl+Shift+S', statusTip="Save File As",
                                 triggered=self.onFileSaveAs)
        self.actExit = QAction('&Exit', self, shortcut='Ctrl+Q', statusTip="Exit Application", triggered=self.close)

        self.actUndo = QAction('&Undo', self, shortcut='Ctrl+Z', statusTip="Undo last Operation",
                               triggered=self.onEditUndo)
        self.actRedo = QAction('&Redo', self, shortcut='Ctrl+Shift+Z', statusTip="Redo Operation",
                               triggered=self.onEditRedo)
        self.actCut = QAction('Cu&t', self, shortcut='Ctrl+X', statusTip="Cut from Clipboard", triggered=self.onEditCut)
        self.actCopy = QAction('&Copy', self, shortcut='Ctrl+C', statusTip="Copy to Clipboard",
                               triggered=self.onEditCopy)
        self.actPaste = QAction('&Paste', self, shortcut='Ctrl+V', statusTip="Paste to Clipboard",
                                triggered=self.onEditPaste)
        self.actDelete = QAction('&Delete', self, shortcut='Del', statusTip="Delete Selected Item",
                                 triggered=self.onEditDelete)

    def createMenus(self):
        menubar = self.menuBar()
        # initialize menu
        self.filemenu = menubar.addMenu('&File')
        self.filemenu.addAction(self.actNew)
        self.filemenu.addSeparator()
        self.filemenu.addAction(self.actOpen)
        self.filemenu.addAction(self.actSave)
        self.filemenu.addAction(self.actSaveAs)
        self.filemenu.addSeparator()
        self.filemenu.addAction(self.actExit)

        self.editmenu = menubar.addMenu("Edit")
        self.editmenu.addAction(self.actUndo)
        self.editmenu.addAction(self.actRedo)
        self.editmenu.addSeparator()
        self.editmenu.addAction(self.actCut)
        self.editmenu.addAction(self.actCopy)
        self.editmenu.addAction(self.actPaste)
        self.editmenu.addSeparator()
        self.editmenu.addAction(self.actDelete)

    def setTitle(self):
        title = "Node Edditor - "
        title += self.getCurrentNodeEditorWidget().getUserFriendlyFilename()

        self.setWindowTitle(title)

    def closeEvent(self, event):
        if self.maybeSaved():
            event.accept()
        else:
            event.ignore()

    def isModified(self):
        return self.getCurrentNodeEditorWidget().scene.isModified()

    def getCurrentNodeEditorWidget(self):
        return self.centralWidget()


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
            self.getCurrentNodeEditorWidget().scene.clear()
            self.getCurrentNodeEditorWidget().filename = None
            self.setTitle()

    def onFileOpen(self):
        if self.maybeSaved():
            fname, filter, = QFileDialog.getOpenFileName(self, "Open Graph from file")
            if fname == '':
                return
            if os.path.isfile(fname):
                self.getCurrentNodeEditorWidget().fileLoad(fname)

    def onFileSave(self):
        current_nodeeditor =  self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            if not current_nodeeditor.isFilenameSet(): return self.onFileSaveAs()

            current_nodeeditor.fileSave()
            self.statusBar().showMessage("File saved Successfully %s" % current_nodeeditor.filename, 5000)

            # support for mdi application
            if hasattr(current_nodeeditor, "setTitle"): current_nodeeditor.setTitle()
            else:self.setTitle()
            return True


    def onFileSaveAs(self):
        current_nodeeditor =  self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            fname, filter, = QFileDialog.getSaveFileName(self, "Save Graph to file")

            if fname == '': return False
            current_nodeeditor.fileSave(fname)
            self.statusBar().showMessage("File saved Successfully as %s" % current_nodeeditor.filename, 5000)

            # support for mdi application
            if hasattr(current_nodeeditor, "setTitle"): current_nodeeditor.setTitle()
            else:  self.setTitle()
            return True


    def onEditUndo(self):
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.undo()

    def onEditRedo(self):
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.redo()

    def onEditDelete(self):
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.grScene.views()[0].deleteSelected()

    def onEditCut(self):
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=True)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)

    def onEditCopy(self):
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=False)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self):
        if self.getCurrentNodeEditorWidget():
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
            self.getCurrentNodeEditorWidget().scene.clipboard.deserializeFromClipboard(data)

    def readSettings(self):
        settings = QSettings(self.name_company, self.name_product)
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QSettings(self.name_company, self.name_product)
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())
