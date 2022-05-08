import os.path

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import json
from collections import OrderedDict

from nodeeditor.node_edge import Edge
from nodeeditor.node_node import Node
from nodeeditor.node_scene_clipboard import SceneClipboard
from nodeeditor.node_serializable import Serializable
from nodeeditor.node_graphics_scene import QDMGraphicsScene
from nodeeditor.node_scene_history import SceneHistory
from nodeeditor.utils import dumpException


class InvalidFile(Exception): pass


class Scene(Serializable):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []

        self.scene_width = 64000
        self.scene_height = 64000
        self._has_been_modified = False
        self._last_selected_items = []

        # initialize all listeners
        self._has_been_modified_listeners = []
        self._item_selected_listeners = []
        self._items_deselected_listeners = []

        self.initUI()
        self.history = SceneHistory(self)
        self.clipboard = SceneClipboard(self)

        self.grScene.itemSelected.connect(self.onItemSelected)
        self.grScene.itemsDeselected.connect(self.onItemsDeselected)

    def initUI(self):
        # create graphics scene
        self.grScene = QDMGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)

    def onItemSelected(self):
        current_selected_item = self.getSelectedItems()
        if current_selected_item != self._last_selected_items:
            self._last_selected_items = current_selected_item
            self.history.storeHistory("Selection changed")
            for callback in self._item_selected_listeners: callback()

    def onItemsDeselected(self):
        self.resetLastSelectedStates()
        if self._last_selected_items != []:
            self._last_selected_items = []
            self.history.storeHistory("Deselection everything")
            for callback in self._items_deselected_listeners: callback()

    def isModified(self):
        return self._has_been_modified

    def getSelectedItems(self):
        return self.grScene.selectedItems()

    @property
    def has_been_modified(self):
        # return False
        return self._has_been_modified

    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:
            # set to be read soon
            self._has_been_modified = value

            # call all the registered listeners
            for callback in self._has_been_modified_listeners: callback()

        self._has_been_modified = value

    # helper listener functions
    def addHasBeenModifiedListener(self, callback):
        self._has_been_modified_listeners.append(callback)

    def addItemSelectedListener(self, callback):
        self._item_selected_listeners.append(callback)

    def addItemsDeselectedListener(self, callback):
        self._items_deselected_listeners.append(callback)

    def addDragEnterListener(self, callback):
        self.grScene.views()[0].addDragEnterListener(callback)

    def addDropListener(self, callback):
        self.grScene.views()[0].addDropListener(callback)

    # putting flags to detect node or edge has been selected
    def resetLastSelectedStates(self):
        for node in self.nodes:
            node.grNode._last_selected_state = False
        for edge in self.edges:
            edge.grEdge._last_selected_state = False

    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        if node in self.nodes:
            self.nodes.remove(node)
        else:
            print("!W:", "Scene::removeNode", "want to remove node", node, "from self.nodes but not in the list")

    def removeEdge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            print("!W:", "Scene::removeEdge", "want to remove edge", edge, "from self.edges but not in the list")

    def clear(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()
        self._has_been_modified = False

    def saveToFile(self, filename):
        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
            print("saving to", filename, "successfully")
            self._has_been_modified = False

    def loadFromFile(self, filename):
        with open(filename, "r") as file:
            raw_data = file.read()
            try:
                data = json.loads(raw_data, encoding='utf-8')
                self.deserialize(data)
                self._has_been_modified = False
            except json.JSONDecodeError:
                raise InvalidFile("%s is an invalid json file" % os.path.basename(filename))
            except Exception as e:
                dumpException(e)

    def serialize(self):
        nodes, edges = [], []
        for node in self.nodes: nodes.append(node.serialize())
        for edge in self.edges: edges.append(edge.serialize())
        return OrderedDict([
            ('id', self.id),
            ('scene_width', self.scene_width),
            ('scene_height', self.scene_height),
            ('nodes', nodes),
            ('edges', edges),
        ])

    def deserialize(self, data, hashmap={}, restore_id=True):

        self.clear()
        hashmap = {}

        if restore_id: self.id = data["id"]

        # create nodes
        for node_data in data['nodes']:
            Node(self).deserialize(node_data, hashmap, restore_id)
        # # create edges
        for edge_data in data['edges']:
            Edge(self).deserialize(edge_data, hashmap, restore_id)
        return True
