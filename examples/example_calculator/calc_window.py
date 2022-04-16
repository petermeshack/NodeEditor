import os.path

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from examples.example_calculator.calc_sub_window import CulculatorSubWindow
from nodeeditor.node_editor_window import NodeEditorWindow
from nodeeditor.utils import dump_exeption, loadStylesheets

# images for the darkskin
import examples.example_calculator.qss.nodeeditor_dark_resources

class CalculatorWindow(NodeEditorWindow):
    def initUI(self):
        self.name_company = "Pmesh"
        self.name_product = "Calculator NodeEditor"

        self.stylesheet_filename = os.path.join(os.path.dirname(__file__),'qss/nodeeditor.qss')
        loadStylesheets(
            os.path.join(os.path.dirname(__file__), 'qss/nodeeditor-dark.qss'),
            self.stylesheet_filename
        )

        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QMdiArea.TabbedView)
        self.mdiArea.setDocumentMode(True)
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.createNodeDock()

        self.readSettings()

        self.setWindowTitle("NodeEditor for Calculator Example")

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()

    def updateMenus(self):
        pass

    def createActions(self):
        super().createActions()
        self.closeAct = QAction("Cl&ose", self, statusTip="Close the active window",
                                triggered=self.mdiArea.closeActiveSubWindow)
        self.closeAllAct = QAction("Close &All", self, statusTip="Close all the windows",
                                   triggered=self.mdiArea.closeAllSubWindows)
        self.tileAct = QAction("&Tile", self, statusTip="Tile the windows", triggered=self.mdiArea.tileSubWindows)
        self.cascadeAct = QAction("&Cascade", self, statusTip="Cascade the windows",
                                  triggered=self.mdiArea.cascadeSubWindows)
        self.nextAct = QAction("Ne&xt", self, shortcut=QKeySequence.NextChild,
                               statusTip="Move the focus to the next window",
                               triggered=self.mdiArea.activateNextSubWindow)
        self.previousAct = QAction("Pre&vious", self, shortcut=QKeySequence.PreviousChild,
                                   statusTip="Move the focus to the previous window",
                                   triggered=self.mdiArea.activatePreviousSubWindow)

        self.separatorAct = QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = QAction("&About", self, statusTip="Show the application's About box", triggered=self.about)

    def onFileNew(self):
        subwnd = self.createMDiChild()
        subwnd.show()

    def about(self):
        QMessageBox.about(self, "About Calculator Node Editor example",
                          "The <b>Calculator</b> example demonstrates how to write multiple "
                          "document interface applications using PyQt5 and NodeEditor. For More Information visit:"
                          "<a href='https://www.petermeshack.com'></a>")

    def createMenus(self):
        super().createMenus()
        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)

    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)

        windows = self.mdiArea.subWindowList()
        self.separatorAct.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.getUserFriendlyFilename())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.activeMdiChild())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def createToolBars(self):
        pass

    def createNodeDock(self):
        self.listWidget = QListWidget()
        self.listWidget.addItem("Add")
        self.listWidget.addItem("Subtract")
        self.listWidget.addItem("Multiply")
        self.listWidget.addItem("Devide")

        self.items = QDockWidget("Nodes")
        self.items.setWidget(self.listWidget)
        self.items.setFloating(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.items)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def createMDiChild(self):
        nodeeditor = CulculatorSubWindow()
        subwnd = self.mdiArea.addSubWindow(nodeeditor)
        return subwnd

    def activeMdiChild(self):
        """we are returning node editor widget"""
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)
