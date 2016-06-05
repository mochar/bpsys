from collections import namedtuple

from PySide import QtCore, QtGui
from grandalf.graphs import Vertex, Edge, Graph
from grandalf.layouts import SugiyamaLayout

from .models import GOModel, TreeViewModel, TreeItem


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

    def mousePressEvent(self, event):
        super(Node, self).mousePressEvent(event)


class Path(QtGui.QGraphicsPathItem):
    def __init__(self, path, scene):
        super(Path, self).__init__(path)
        self.setPen(QtGui.QPen(QtCore.Qt.black, 1.75))


class GOWidget(QtGui.QWidget):
    def __init__(self, parent, analysis):
        super(GOWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.node_size = (95, 65)
        self.parent_count = 15
        self.set_up()
        
    def set_up(self):
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
 
        # Graph
        self.graph_widget = self.create_graph_widget()

        # Enriched GO terms
        table_view = QtGui.QTableView(self)
        table_view.setModel(GOModel(self.analysis))
        table_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        table_view.clicked.connect(self.select_term)
            
        layout.addWidget(table_view, 1)
        layout.addWidget(self.graph_widget, 3)
        table_view.selectRow(0)
        
    def select_term(self, index):
        go_id = index.sibling(index.row(), 0).data()
        family_terms = self.find_family_terms(go_id)
        self.graph = self.create_graph(family_terms)
        self.sug = self.create_sug_layout(self.graph)
        self.graph_widget.setScene(self.create_graph_scene())

    def find_family_terms(self, go_id):
        term = self.analysis.go_dag.query_term(go_id)
        all_ids = set() 
        for i, parent in enumerate(term.get_all_parents()):
            all_ids.add(parent)
            #if i == self.parent_count:
            #    break
        all_ids.add(go_id)
        all_terms = [self.analysis.go_dag[term_id] for term_id in all_ids]
        return all_terms

    def create_graph(self, terms):
        def create_edges_with_children(vertex):
            for child_term in vertex.data.children:
                child_vertex = all_vertices.get(child_term.id)
                if child_vertex is None:
                    continue
                edge = Edge(vertex, child_vertex)
                graph.add_edge(edge)
                create_edges_with_children(child_vertex)
                
        graph = Graph()
        ontology_term_id = self.analysis.ontology.id 
        top_term = self.analysis.go_dag.query_term(ontology_term_id)
        all_vertices = {term.id: ViewVertex(term, *self.node_size) for term in terms}
        create_edges_with_children(all_vertices[top_term.id])
        return graph
        
    def create_sug_layout(self, graph):
        sug = SugiyamaLayout(graph.C[0])
        sug.init_all(optimize=True)
        sug.draw(10)
        return sug
        
    def term_to_color(self, term):
        term = self.analysis.go_terms.get(term.id)
        if term is None:
            return QtGui.QColor.fromRgbF(1, 1, 1)
        mean = term.proteins['log_ratio_X'].mean()
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
        #scene = self.create_graph_scene()
        view = QtGui.QGraphicsView(self)
        view.setRenderHint(QtGui.QPainter.Antialiasing)
        return view
        
    def create_edge_path(self, from_x, from_y, to_x, to_y, scene):
        path = QtGui.QPainterPath()
        path.moveTo(from_x, from_y)
        path.lineTo(to_x, to_y)
        return Path(path, scene=scene)
