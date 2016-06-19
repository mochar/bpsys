from PySide import QtCore, QtGui
from scipy.cluster.hierarchy import dendrogram
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


class ClustersWidget(QtGui.QWidget):
    def __init__(self, parent, analysis):
        super(ClustersWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.set_up()
        
    def set_up(self):
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        pgs = self.analysis.protein_groups
        significant = pgs[pgs.significant == True]
        groups = significant.groupby('cluster').groups
        for cluster, rows in groups.items():
            txt = 'Cluster {}: {} eiwitten'.format(cluster, len(rows))
            # layout.addWidget(QtGui.QLabel(txt))

        figure = plt.figure()
        dendrogram(self.analysis.z, color_threshold=2)
        plt.axhline(y=2, c='k')
        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar(canvas, self)
        layout.addWidget(toolbar)
        layout.addWidget(canvas)