from nodeeditor.node_graphics_edge import QDMGraphicsEdge

DEBUG = False


class SceneHistory():
    def __init__(self, scene):
        self.scene = scene

        self.history_stack = []
        self.history_current_step = -1
        self.histrory_limit = 32

    def undo(self):
        if DEBUG: print("UNDO")
        if self.history_current_step > 0:
            self.history_current_step -= 1
            self.restorHistory()

    def redo(self):
        if DEBUG: print("REDO")
        if self.history_current_step +1 <len(self.history_stack):
            self.history_current_step += 1
            self.restorHistory()

    def restorHistory(self):
        if DEBUG: print("RESTORING HISTORY",
                        " .... current step : @%d" % self.history_current_step,
                        "(%d)" % len(self.history_stack))
        self.restorHistoryStamp(self.history_stack[self.history_current_step])

    def storeHistory(self, desk, setModified = False):
        if setModified:
            self.scene.has_been_modified =True
        if DEBUG: print("STORING HISTORY", '"%s"' % desk,
                        " .... current step : @%d" % self.history_current_step,
                        "(%d)" % len(self.history_stack))

        # if pointer history_current_step is not at the end of history stack
        if self.history_current_step+1 < len(self.history_stack):
            self.history_stack = self.history_stack[0:self.history_current_step+1]

        # if history is outside the limits
        if self.history_current_step + 1 >= self.histrory_limit:
            self.history_stack = self.history_stack[1:]
            self.history_current_step -= 1

        hs = self.createHisroryStamp(desk)

        self.history_stack.append(hs)
        self.history_current_step += 1
        if DEBUG: print(" -- seting step to", self.history_current_step)

    def createHisroryStamp(self, desc):
        sel_obj = {
            'nodes':[],
            'edges':[]
        }
        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'):
                sel_obj['nodes'].append(item.node.id)
            elif isinstance(item, QDMGraphicsEdge):
                sel_obj['edges'].append(item.edge.id)

        hisory_stamp = {
            'desc': desc,
            'snapshot': self.scene.serialize(),
            'selection': sel_obj
        }
        return hisory_stamp

    def restorHistoryStamp(self, history_stamp):
        if DEBUG: print("RHS", history_stamp['desc'])

        self.scene.deserialize(history_stamp['snapshot'])
        # restore selection
        for edge_id in history_stamp['selection']['edges']:
            for edge in self.scene.edges:
                if edge.id == edge_id:
                    edge.grEdge.setSelected(True)
                    break
        for node_id in history_stamp['selection']['nodes']:
            for node in self.scene.nodes:
                if node.id == node_id:
                    node.grNode.setSelected(True)
                    break
