from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from nodeeditor.node_edge import Edge, EDGE_TYPE_BEZIER
from nodeeditor.node_graphic_cutline import QDMCutline
from nodeeditor.node_graphics_edge import QDMGraphicsEdge
from nodeeditor.node_graphics_socket import QDMGraphicsSocket

MODE_NOOP = 1
MODE_EDGE_DRAG = 2
MODE_EDGE_CUT = 3
EDGE_DRAG_START_THRESHOLD = 50

DEBUG = True


class QDMGraphicsView(QGraphicsView):
    scenePosChanged = pyqtSignal(int, int)

    def __init__(self, grScene, parent=None):
        super().__init__(parent)
        self.grScene = grScene

        self.initUI()
        self.setScene(self.grScene)

        self.mode = MODE_NOOP
        self.editingFlag = False
        self.rubberBandDraggingRectangle = False

        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0, 10]

        # cutline
        self.cutline = QDMCutline()
        self.grScene.addItem(self.cutline)

    def initUI(self):
        self.setRenderHints(
            QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QDMGraphicsView.AnchorUnderMouse)

        self.setDragMode(QGraphicsView.RubberBandDrag)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)

        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.leftMouseButtonRelease(event)

        else:
            super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event):
        # print("MMB pressed")
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())

        super().mousePressEvent(fakeEvent)

    def middleMouseButtonRelease(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() & Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def leftMouseButtonPress(self, event):
        """# get clicked item on"""
        item = self.getItemAtClick(event)

        """ store position of leftmouse button click"""
        self.last_lmb_click_pos = self.mapToScene(event.pos())

        # if DEBUG: print("LMB Click on", item, self.debug_modifiers(event))

        """logic"""
        if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fake_event = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                                         Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                         event.modifiers() | Qt.ControlModifier)
                super().mousePressEvent(fake_event)
                return

        if type(item) is QDMGraphicsSocket:
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG
                self.edgeDragStart(item)
                return
        if self.mode == MODE_EDGE_DRAG:
            res = self.edgeDragEnd(item)
            if res: return

        if item is None:
            if event.modifiers() & Qt.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fake_event = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                         Qt.LeftButton, Qt.NoButton, event.modifiers())
                super().mouseReleaseEvent(fake_event)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return
            else:
                self.rubberBandDraggingRectangle = True

        return super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event):
        """# get released mousebtn  on"""
        item = self.getItemAtClick(event)
        """# logic"""
        if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                         Qt.LeftButton, Qt.NoButton,
                                         event.modifiers() | Qt.ControlModifier)
                super().mouseReleaseEvent(fake_event)
                return

        if self.mode == MODE_EDGE_DRAG:
            if self.distanceBetweenClickAndReleaseIsOff(event):
                res = self.edgeDragEnd(item)
                if res: return

        if self.mode == MODE_EDGE_CUT:
            self.cutIntersectingEdges()
            self.cutline.line_points = []
            self.cutline.update()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.mode = MODE_NOOP
            return
        # if self.dragMode() ==  QGraphicsView.RubberBandDrag:
        if self.rubberBandDraggingRectangle:
            self.grScene.scene.history.storeHistory("Selection changed")
            self.rubberBandDraggingRectangle = False

        super().mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)
        item = self.getItemAtClick(event)
        if DEBUG:
            if isinstance(item, QDMGraphicsEdge): print("RMB DEBUG::", item.edge, "connecting sockets:",
                                                        item.edge.start_socket, "<-->", item.edge.end_socket)
            if type(item) is QDMGraphicsSocket: print("RMB DEBUG::", "socket:", item.socket, "has edges:",
                                                      item.socket.edges)
            if item is None:
                print("SCENE: ")
                print(" Nodes: ")
                for node in self.grScene.scene.nodes: print('   ', node)
                print(" Edges: ")
                for edge in self.grScene.scene.edges: print('   ', edge)

    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.mode == MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.drag_edge.grEdge.setDestination(pos.x(), pos.y())
            self.drag_edge.grEdge.update()

        if self.mode == MODE_EDGE_CUT:
            pos = self.mapToScene(event.pos())
            self.cutline.line_points.append(pos)
            self.cutline.update()

        self.last_scene_mouse_position = self.mapToScene(event.pos())

        self.scenePosChanged.emit(
            int(self.last_scene_mouse_position.x()),
            int(self.last_scene_mouse_position.y())
        )
        super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            if not self.editingFlag:
                self.deleteSelected()
                self.grScene.scene.history.storeHistory("Delete Selected", setModified=True)

            else:
                super().keyPressEvent(event)
            # elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
            #     self.grScene.scene.saveToFile("graph.json01.text")
            # elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
            #     self.grScene.scene.loadFromFile("graph.json01.text")
            # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and not event.modifiers() & Qt.ShiftModifier:
            #     self.grScene.scene.history.undo()
            # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
            #     self.grScene.scene.history.redo()
            # elif event.key() == Qt.Key_H:
            #     print("HISTORY: len(%d)" % len(self.grScene.scene.history.history_stack),
            #           " -- current_step", self.grScene.scene.history.history_current_step)
            #     ix = 0
            #     for item in self.grScene.scene.history.history_stack:
            #         print("#", ix, "---", item['desc'])
            #         ix += 1
            #
            # else:
            super().keyPressEvent(event)

    def cutIntersectingEdges(self):
        for ix in range(len(self.cutline.line_points) - 1):
            p1 = self.cutline.line_points[ix]
            p2 = self.cutline.line_points[ix + 1]
            for edge in self.grScene.scene.edges:
                if edge.grEdge.intersectWith(p1, p2):
                    edge.remove()
        # self.grScene.scene.history.storeHistory("Cut EdgeMode Selected")

    def deleteSelected(self):
        for item in self.grScene.selectedItems():
            if isinstance(item, QDMGraphicsEdge):
                item.edge.remove()
            elif hasattr(item, "node"):
                item.node.remove()
                self.grScene.scene.history.storeHistory("Delete Selected", setModified=True)

    def debug_modifiers(self, event):
        out = "MODES: "
        if event.modifiers() & Qt.ShiftModifier: out += "SHIFT "
        if event.modifiers() & Qt.ControlModifier: out += "CTRL "
        if event.modifiers() & Qt.AltModifier: out += "ALT "
        return out

    def getItemAtClick(self, event):
        """return clicked on object /released"""
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def edgeDragStart(self, item):
        if DEBUG: print("View edgeDragStart - Start dragging edge")
        if DEBUG: print("View edgeDragStart - Assign Start Socket to:", item.socket)
        # self.previousEdge = item.socket.edges
        self.drag_start_socket = item.socket
        self.drag_edge = Edge(self.grScene.scene, item.socket, None, EDGE_TYPE_BEZIER)
        if DEBUG: print("View edgeDragStart - dragEdge:", self.drag_edge)

    def edgeDragEnd(self, item):
        """ # return true if you want to skip the rest of the code"""
        self.mode = MODE_NOOP
        if DEBUG: print("View edgeDragEnd - dragging edge")
        self.drag_edge.remove()
        self.drag_edge = None

        if type(item) is QDMGraphicsSocket:
            if item.socket != self.drag_start_socket:
                # if we release dragging on a socket (other than the beginning socket)
                # if DEBUG: print("View edgeDragEnd - previous edge", self.previousEdge)

                # if item.socket.hasEdge(): item.socket.edge.remove()

                # for edge in item.socket.edges:
                #     if DEBUG: print("View edgeDragEnd - cleanup edge IN target",edge)
                #     edge.remove()
                #     if DEBUG: print("View edgeDragEnd - cleanup edge IN target", edge, "removed..")

                # keep all edges coming from target socket
                if not item.socket.is_multi_edges:
                    item.socket.removeAllEdges()

                # keep all edges coming from start socket
                if not self.drag_start_socket.is_multi_edges:
                    self.drag_start_socket.removeAllEdges()

                # if DEBUG: print("View edgeDragEnd -  Assign End socket", item.socket)
                # if self.previousEdge is not None: self.previousEdge.remove()
                # if DEBUG: print("View edgeDragEnd -  previous edge removed")
                # self.drag_edge.start_socket = self.drag_start_socket
                # self.drag_edge.end_socket = item.socket
                # self.drag_edge.start_socket.addEdge(self.drag_edge)
                # self.drag_edge.end_socket.addEdge(self.drag_edge)
                # if DEBUG: print("View edgeDragEnd -  Reassigned Start and End sockets to drag edge")
                # self.drag_edge.updatePositions()

                new_edge = Edge(self.grScene.scene, self.drag_start_socket, item.socket, edge_type=EDGE_TYPE_BEZIER)
                if DEBUG: print("View edgeDragEnd - created new ed edge:", new_edge, "connecting",
                                new_edge.start_socket, "<-->", new_edge.end_socket)

                self.grScene.scene.history.storeHistory("Created new edge by dragging", setModified=True)
                return True

        # if DEBUG: print("View edgeDragEnd - about to set socket to previous edge", self.previousEdge)
        # if self.previousEdge is not None:
        #     self.previousEdge.start_socket.edge = self.previousEdge

        if DEBUG: print("View edgeDragEnd - everything done.")
        return False

    def distanceBetweenClickAndReleaseIsOff(self, event):
        """ messures if too far from LMB click scene pos"""
        new_last_lmb_click_pos = self.mapToScene(event.pos())
        dist_scene = new_last_lmb_click_pos - self.last_lmb_click_pos
        edge_drag_threshold_aq = EDGE_DRAG_START_THRESHOLD * EDGE_DRAG_START_THRESHOLD
        return (dist_scene.x() * dist_scene.x() + dist_scene.y() * dist_scene.y()) > edge_drag_threshold_aq

    def wheelEvent(self, event):
        # calculate our zoom factor
        zoomOutFactor = 1 / self.zoomInFactor

        # calculate zoom
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep

        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep
        clamped = False

        if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True

        # set scene scale
        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)

