from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.QtWidgets import *

from calc_conf import *
from nodeeditor.utils import dumpException


class QDMDragListBox(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # init
        self.setIconSize(QSize(32,32))
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

        self.addMyitems()

    def addMyitems(self):
        self.addMyitem("Inputs", "icons/in.png", OP_NODE_INPUT)
        self.addMyitem("Output", "icons/out.png", OP_NODE_OUTPUT)

        self.addMyitem("Add", "icons/add.png", OP_NODE_ADD)
        self.addMyitem("Subtract", "icons/sub.png", OP_NODE_SUB)
        self.addMyitem("Multiply", "icons/mul.png", OP_NODE_MUL)
        self.addMyitem("Divide", "icons/divide.png", OP_NODE_DIV)

    def addMyitem(self, name, icon=None, op_code=0):
        item =  QListWidgetItem(name, self) # can be (icon, text, parent, <int>type)
        pixmap = QPixmap(icon if icon is not None else ".")
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32,32))
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        # setup data
        item.setData(Qt.UserRole, pixmap)
        item.setData(Qt.UserRole + 1, op_code)

    def startDrag(self,  *args, **kwargs):
        #print("Listbox::startDrag")
        try:
            item = self.currentItem()
            op_code = item.data(Qt.UserRole + 1)
            #print("Dragging Item <%d>" % op_code, item)

            pixmap = QPixmap(item.data(Qt.UserRole))

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            dataStream << pixmap
            dataStream.writeInt(op_code)
            dataStream.writeQString(item.text())

            mimeData = QMimeData()
            mimeData.setData(LISTBOX_MIMETYPE,itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(QPoint(pixmap.width()/2,pixmap.height()/2))
            drag.setPixmap(pixmap)

            drag.exec_(Qt.MoveAction)

        except Exception as e:dumpException(e)