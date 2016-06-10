from collections import namedtuple
import pdb

from PySide import QtCore, QtGui
from grandalf.graphs import Vertex, Edge, Graph
from grandalf.layouts import SugiyamaLayout
from grandalf.routing import route_with_splines, EdgeViewer
import pyqtgraph as pg

from .models import GOModel, TreeViewModel, TreeItem


class DefaultView(object):
    def __init__(self, w, h):
        self.w, self.h = w, h


class ViewVertex(Vertex):
    def __init__(self, data, w, h):
        super(ViewVertex, self).__init__(data)
        self.view = DefaultView(w, h)


class ViewEdge(Edge):
    def __init__(self, v1, v2):
        super(ViewEdge, self).__init__(v1, v2)
        self.view = EdgeViewer()


class Node(QtGui.QGraphicsRectItem):
    def __init__(self, x, y, w, h, color, term, scene, bold=False):
        super(Node, self).__init__(QtCore.QRectF(x, y, w, h), scene=scene)
        self.term = term
        self.setZValue(1)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setPen(QtGui.QPen(QtCore.Qt.black, 1.75))
        self.setBrush(QtGui.QBrush(color))
        
        self.text = QtGui.QGraphicsTextItem(parent=self)
        html = '<center>{}</center>'
        if bold:
            html = '<center><b>{}</b></center>'
        self.text.setHtml(html.format(self.term.name))
        self.text.setPos(x, y)
        self.text.setTextWidth(w)

    def mousePressEvent(self, event):
        super(Node, self).mousePressEvent(event)
        self.setVisible(not self.isVisible())


class Path(QtGui.QGraphicsPathItem):
    def __init__(self, path, scene):
        super(Path, self).__init__(path)
        self.setPen(QtGui.QPen(QtCore.Qt.black, 1.75))


class GOWidget(QtGui.QWidget):
    def __init__(self, parent, analysis):
        super(GOWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.node_size = (130, 65)
        self.parent_count = 15
        self.set_up()
        
    def set_up(self):
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
 
        # Graph
        self.graph_title = QtGui.QLabel('')
        self.graph_title.setAlignment(QtCore.Qt.AlignHCenter)
        font = QtGui.QFont()
        font.setBold(True)
        self.graph_title.setFont(font)
        self.graph_title.setWordWrap(True)
        self.graph_widget = self.create_graph_widget()
        self.color_map = pg.ColorMap([0, 0.5, 1], [(1., 1., 1.),
            (1., 1., 0.), (1., 0.5, 0.)])
        graph_layout = QtGui.QVBoxLayout()
        graph_layout.addWidget(self.graph_title)
        graph_layout.addWidget(self.graph_widget)

        # Enriched GO terms
        table_view = QtGui.QTableView(self)
        table_view.setModel(GOModel(self.analysis))
        table_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        table_view.clicked.connect(self.select_term)
        table_view.selectRow(0)

        # Proteins in selected GO term
        self.proteins_list = QtGui.QListWidget()
            
        layout.addWidget(table_view, 1)
        layout.addWidget(self.proteins_list, 1)
        layout.addLayout(graph_layout, 2)
        
    def select_term(self, index):
        go_id = index.sibling(index.row(), 0).data()
        self.graph_title.setText(self.analysis.go_dag[go_id].name.upper())
        self.graph = self.create_graph(go_id)
        self.sug = self.create_sug_layout(self.graph)
        self.graph_widget.setScene(self.create_graph_scene())

        # Update list
        term = self.analysis.go_terms[go_id]
        self.proteins_list.clear()
        zipped = zip(term.proteins.protein_ids, term.proteins.log_ratio_X)
        for protein, ratio in zipped:
            item = QtGui.QListWidgetItem(protein, self.proteins_list)
            item.setBackground(self.ratio_to_color(ratio))

    def create_graph(self, go_id):
        done = []

        def create_edges_with_parents(child_vertex):
            for parent_term in child_vertex.data.parents:
                e = (child_vertex.data.id, parent_term.id)
                if e in done:
                    continue
                parent_vertex = vertices[parent_term.id]
                edge = ViewEdge(parent_vertex, child_vertex)
                graph.add_edge(edge)
                done.append(e)
                create_edges_with_parents(parent_vertex)
                
        graph = Graph()
        dag = self.analysis.go_dag
        term = dag[go_id]
        vertices = {term: ViewVertex(dag[term], *self.node_size) for term in term.get_all_parents()}
        create_edges_with_parents(ViewVertex(term, *self.node_size))
        return graph
        
    def create_sug_layout(self, graph):
        sug = SugiyamaLayout(graph.C[0])
        sug.route_edge = route_with_splines
        sug.init_all(optimize=True)
        sug.draw(10)
        return sug
        
    def term_to_color(self, term):
        term = self.analysis.go_terms.get(term.id)
        if term is None:
            return QtGui.QColor.fromRgbF(1, 1, 1)
        size = len(term.proteins)
        max_ = max([len(term.proteins) for term in self.analysis.go_terms.values()])
        return self.color_map.map([size / max_], mode='qcolor')[0]

    def ratio_to_color(self, ratio):
        if ratio > 0:
            max_ = self.analysis.protein_groups['log_ratio_X'].max()
            return QtGui.QColor.fromRgbF(ratio / max_, 0, 0, .7)
        min_ = self.analysis.protein_groups['log_ratio_X'].min()
        return QtGui.QColor.fromRgbF(0, ratio / min_, 0, .7)
     
    def create_graph_scene(self):
        scene = QtGui.QGraphicsScene(self)
        w, h = self.node_size
        for i, layer in enumerate(self.sug.layers):
            for vertex in layer:
                x, y = vertex.view.xy
                try:
                    term = vertex.data
                except AttributeError:
                    continue
                color = self.term_to_color(vertex.data)
                bold = i == len(self.sug.layers) - 1
                scene.addItem(Node(x, y, w, h, color, term, scene, bold))
        for edge in self.sug.g.E():
            scene.addItem(self.create_edge_path(edge.view.splines, scene))
        return scene
        
    def create_graph_widget(self):
        view = QtGui.QGraphicsView(self)
        view.setRenderHint(QtGui.QPainter.Antialiasing)
        return view
        
    def create_edge_path(self, splines, scene):
        path = QtGui.QPainterPath()
        w, h = self.node_size
        for spline in splines:
            spline = [(x + (w / 2), y + (h / 2)) for x, y in spline]
            start, end = spline[0], spline[1]
            path.moveTo(start[0], start[1])
            if len(spline) == 2:
                path.lineTo(end[0], end[1])
            else:
                p1, p2, p3, p4 = spline
                path.cubicTo(p2[0], p2[1], p3[0], p3[1], p4[0], p4[1])
        return Path(path, scene=scene)

