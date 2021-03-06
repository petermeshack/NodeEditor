from collections import OrderedDict
from nodeeditor.node_serializable import Serializable
from nodeeditor.node_graphics_socket import QDMGraphicsSocket

LEFT_TOP = 1
LEFT_BOTTOM = 2
RIGHT_TOP = 3
RIGHT_BOTTOM = 4

DEBUG = False


class Socket(Serializable):
    def __init__(self, node, index=0, position=LEFT_TOP, socket_type=1, multi_edges=True):
        super().__init__()
        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.is_multi_edges = multi_edges

        # debug socket
        if DEBUG: print("Socket == creating with ", "index:", self.index, "position:", self.position, "for node",
                        self.node)
        self.grSocket = QDMGraphicsSocket(self, self.socket_type)
        self.grSocket.setPos(*self.node.getSocketPositon(index, position))

        self.edges = []

    def __str__(self):
        return "<Socket %s %s..%s>" % ("ME" if self.is_multi_edges else "SE", hex(id(self))[2:5], hex(id(self))[-3:])

    def getSocketPosition(self):
        # debug socket positions GetSocketPosition (GSP), Position Result (RES)
        if DEBUG: print(" GSP: ", self.index, self.position, " NODE:", self.node)
        res = self.node.getSocketPositon(self.index, self.position)
        if DEBUG: print(" RES: ", res)

        return res

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeEdge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            print("!W:", "Socket::removeEdge", "want to remove edge", edge, "from self.edges but not in the list")

    def removeAllEdges(self):
        while self.edges:
            edge = self.edges.pop(0)
            edge.remove()
        # self.edges.clear()

    # def hasEdge(self):
    #     return self.edges is not None
    def determineMultiEdges(self,data):
        if 'multi_edges' in data:
            return data['multi_edges']
        else:
            # OLDER VERSION OF FILE
            return data['position'] in (RIGHT_TOP ,RIGHT_BOTTOM)


    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('index', self.index),
            ('multi_edges', self.is_multi_edges),
            ('position', self.position),
            ('socket_type', self.socket_type),
        ])

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id: self.id = data["id"]
        self.is_multi_edges =self.determineMultiEdges(data)
        hashmap[data["id"]] = self
        return True
