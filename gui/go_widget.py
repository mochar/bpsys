from collections import namedtuple

from PySide import QtCore, QtGui
from grandalf.graphs import Vertex, Edge, Graph
from grandalf.layouts import SugiyamaLayout


class DefaultView(object):
    def __init__(self, w, h):
        self.w, self.h = w, h


class ViewVertex(Vertex):
    def __init__(self, data, w, h):
        super(ViewVertex, self).__init__(data)
        self.view = DefaultView(w, h)


class Node(QtGui.QGraphicsRectItem):
    def __init__(self, x, y, w, h, color, term, scene):
        super(Node, self).__init__(QtCore.QRectF(x, y, w, h), scene=scene)
        self.term = term
        self.setZValue(1)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setPen(QtGui.QPen(QtCore.Qt.black, 1.75))
        self.setBrush(QtGui.QBrush(color))
        
        self.text = QtGui.QGraphicsTextItem(self.term.name, parent=self)
        self.text.setPos(x, y)
        self.text.setTextWidth(w)
        print(self.text.boundingRect())

    def mousePressEvent(self, event):
        super(Node, self).mousePressEvent(event)


class Path(QtGui.QGraphicsPathItem):
    def __init__(self, path, scene):
        super(Path, self).__init__(path)
        self.setPen(QtGui.QPen(QtCore.Qt.red, 1.75))


class GOWidget(QtGui.QWidget):
    def __init__(self, parent, analysis):
        super(GOWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.node_size = (75, 50)
        self.graph = self.create_graph()
        self.sug = self.create_sug_layout()
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
        
    def find_all_terms(self):
        all_ids = set()
        for go_id in self.analysis.go_ids:
        # for go_id in ['GO:0042605']:
            all_ids.add(go_id)
            term = self.analysis.go_dag.query_term(go_id)
            for parent in term.get_all_parents():
                all_ids.add(parent)
        print(all_ids)
        return [self.analysis.go_dag[term_id] for term_id in all_ids]

    def create_graph(self):
        def create_edges_with_children(vertex):
            for child_term in vertex.data.children:
                if child_term.id not in all_vertices:
                    continue
                child_vertex = all_vertices[child_term.id]
                edge = Edge(vertex, child_vertex)
                graph.add_edge(edge)
                create_edges_with_children(child_vertex)
                
        graph = Graph()
        all_vertices = {term.id: ViewVertex(term, *self.node_size) for term in self.find_all_terms()}
        top_term = self.analysis.go_dag.query_term(self.analysis.ontology.id) 
        create_edges_with_children(all_vertices[top_term.id])
        return graph
        
    def create_sug_layout(self):
        sug = SugiyamaLayout(self.graph.C[0])
        sug.init_all()
        sug.draw(10)
        return sug
        
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
     
    def create_graph_scene(self):
        scene = QtGui.QGraphicsScene(self)
        w, h = self.node_size
        for layer in self.sug.layers:
            for vertex in layer:
                x, y = vertex.view.xy
                try:
                    term = vertex.data
                except AttributeError:
                    continue
                color = self.term_to_color(vertex.data)
                scene.addItem(Node(x, y, w, h, color, term, scene))
                for edge in vertex.e_out():
                    to_x, to_y = edge.v[1].view.xy
                    scene.addItem(self.create_edge_path(
                        x + (w / 2), y + h, # from
                        to_x + (w / 2), to_y, # to
                        scene))
        return scene
        
    def create_graph_widget(self):
        scene = self.create_graph_scene()
        view = QtGui.QGraphicsView(scene, self)
        view.setRenderHint(QtGui.QPainter.Antialiasing)
        return view
        
    def create_edge_path(self, from_x, from_y, to_x, to_y, scene):
        path = QtGui.QPainterPath()
        path.moveTo(from_x, from_y)
        path.lineTo(to_x, to_y)
        return Path(path, scene=scene)