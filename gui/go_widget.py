import re

from PySide import QtCore, QtGui
from grandalf.graphs import Vertex, Edge, Graph
from grandalf.layouts import SugiyamaLayout
from grandalf.routing import route_with_splines, EdgeViewer
import pyqtgraph as pg
import numpy as np

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
        ratio_cols = ['log_ratio_{}'.format(sample) for sample in self.analysis.samples] 
        self._max = self.analysis.protein_groups[ratio_cols].max().max()
        self._min = self.analysis.protein_groups[ratio_cols].min().min()
        self.set_up()
        
    def set_up(self):
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
 
        # Graph
        graph_container = QtGui.QWidget()
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
        graph_container.setLayout(graph_layout)

        # Enriched GO terms
        go_table = pg.TableWidget()
        go_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        go_table.clicked.connect(self.select_term)
        data = np.array(
            [(term[0], float(term[1]), len(term[2])) 
             for term in self.analysis.go_terms.values()],
            dtype=[('GO ID', object), ('P-waarde', float), ('Eiwitten', int)])
        go_table.setData(data)

        # Proteins in selected GO term
        self.proteins_table = pg.TableWidget()
        self.proteins_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
            
        # Splitter with widgets
        splitter = QtGui.QSplitter(self)
        splitter.addWidget(go_table)
        splitter.addWidget(self.proteins_table)
        splitter.addWidget(graph_container)
        splitter.setSizes([1, 1, 1])
        layout.addWidget(splitter)
        
    def select_term(self, index):
        go_id = index.sibling(index.row(), 0).data()
        self.graph_title.setText(self.analysis.go_dag[go_id].name.upper())
        self.graph = self.create_graph(go_id)
        self.sug = self.create_sug_layout(self.graph)
        self.graph_widget.setScene(self.create_graph_scene())

        # Update table
        regex = re.compile(self.analysis.id_regex)
        term = self.analysis.go_terms[go_id]
        cols = ['protein_ids']
        cols += ['log_ratio_{}'.format(sample) for sample in self.analysis.samples]
        dtype = [('Eiwit', object)] + [(col, float) for col in cols][1:]
        data = []
        for row in term.proteins[cols].as_matrix():
            id = regex.findall(row[0].split(';')[0])[0]
            data.append(tuple([id] + [float(x) for x in row[1:]]))
        data = np.array(data, dtype=dtype)
        self.proteins_table.setData(data)

        for i in range(self.proteins_table.rowCount()):
            for j, sample in enumerate(self.analysis.samples, 1):
                item = self.proteins_table.item(i, j)
                ratio = float(item.text())
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
            return QtGui.QColor.fromRgbF(ratio / self._max, 0, 0, .7)
        return QtGui.QColor.fromRgbF(0, ratio / self._min, 0, .7)
     
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

