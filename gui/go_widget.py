from PySide import QtCore, QtGui


class Node(QtGui.QGraphicsRectItem):
    def __init__(self, x, y, w, h, color, term, scene):
        super(Node, self).__init__(QtCore.QRectF(x, y, w, h), scene=scene)
        self.term = term
        self.setZValue(1)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setPen(QtGui.QPen(QtCore.Qt.black, 1.75))
        self.setBrush(QtGui.QBrush(color))

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            self.setPos(value.x(), value.y())
            
    def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget_widget=None):
        super(Node, self).paint(QPainter, QStyleOptionGraphicsItem, QWidget_widget)
        rect = self.boundingRect()
        QPainter.drawText(rect.center(), self.term.id)


class Path(QtGui.QGraphicsPathItem):
    def __init__(self, path, scene):
        super(Path, self).__init__(path)
        self.setPen(QtGui.QPen(QtCore.Qt.red, 1.75))


class GOWidget(QtGui.QWidget):
    def __init__(self, parent, analysis):
        super(GOWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.set_up()
        
    def set_up(self):
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
 
        # GO terms
        terms_layout = QtGui.QVBoxLayout()
        layout.addLayout(terms_layout)
        for go_id in list(self.analysis.go_ids.keys())[:10]:
            terms_layout.addWidget(QtGui.QLabel(go_id))
            
        # Graph
        widget = self.create_graph_widget()
        layout.addWidget(widget)
        
    def term_to_color(self, term):
        proteins = self.analysis.go_ids.get(term.id)
        if proteins is None:
            return QtGui.QColor.fromRgbF(1, 1, 1)
        mean = proteins['log_ratio_X'].mean()
        if mean > 0:
            max = self.analysis.protein_groups['log_ratio_X'].max()
            return QtGui.QColor.fromRgbF(mean / max, 0, 0, .7)
        min = self.analysis.protein_groups['log_ratio_X'].min()
        return QtGui.QColor.fromRgbF(0, mean / min, 0, .7)
        
    def find_all_terms(self):
        all_ids = set()
        for go_id in self.analysis.go_ids:
        # for go_id in ['GO:0042605']:
            all_ids.add(go_id)
            term = self.analysis.go_dag.query_term(go_id)
            for parent in term.get_all_parents():
                all_ids.add(parent)
        print(all_ids)
        return all_ids
     
    def create_graph_widget(self):
        scene = QtGui.QGraphicsScene(self)
        node_size = (75, 50)
        margin = (5, 80)
        
        def add_term_children_to_scene(term, term_x, term_y):
            i = 0
            for child_term in term.children:
                if child_term.id not in all_terms or child_term.id in done:
                    continue
                x = (node_size[0] * i) + (margin[0] * i)
                y = (node_size[1] * child_term.depth) + (margin[1] * child_term.depth)
                color = self.term_to_color(child_term)
                node = Node(x, y, node_size[0], node_size[1], color, child_term, scene)
                scene.addItem(self.create_edge_path(
                    x + (node_size[0] / 2), y,
                    term_x + (node_size[0] / 2), term_y + node_size[1], 
                    scene))
                scene.addItem(node)
                if child_term.children:
                    add_term_children_to_scene(child_term, x, y)
                i += 1
                done.add(child_term.id)
                
        done = set()
        all_terms = self.find_all_terms()
        top_term = self.analysis.go_dag.query_term(self.analysis.ontology.id) 
        color = self.term_to_color(top_term)
        scene.addItem(Node(0, 0, node_size[0], node_size[1], color, top_term, scene))
        add_term_children_to_scene(top_term, 0, 0)
        
        view = QtGui.QGraphicsView(scene, self)
        view.setRenderHint(QtGui.QPainter.Antialiasing)
        return view
        
    def create_edge_path(self, from_x, from_y, to_x, to_y, scene):
        path = QtGui.QPainterPath()
        path.moveTo(from_x, from_y)
        path.lineTo(to_x, to_y)
        return Path(path, scene=scene)