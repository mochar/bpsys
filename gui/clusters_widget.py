from PySide import QtCore, QtGui
from scipy.cluster.hierarchy import dendrogram
import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import pylab


class ClustersWidget(QtGui.QWidget):
    def __init__(self, parent, analysis):
        super(ClustersWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.set_up()
        
    def set_up(self):
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)

        pgs = self.analysis.protein_groups
        significant = pgs[pgs.significant == True]
        groups = significant.groupby('cluster').groups
        for cluster, rows in groups.items():
            txt = 'Cluster {}: {} eiwitten'.format(cluster, len(rows))
            # layout.addWidget(QtGui.QLabel(txt))

        # Data
        cols = [('log_ratio_{}'.format(sample), 'log_ratio_{}'.format(replica))
                for sample, replica 
                in zip(self.analysis.samples, self.analysis.replicas)]
        cols = [s for group in cols for s in group]
        D = significant.as_matrix(cols)
        
        # Compute and plot dendrogram.
        fig = pylab.figure(figsize=(8,8))
        ax1 = fig.add_axes([0.09, 0.1, 0.2, 0.8])
        Z1 = dendrogram(self.analysis.z, color_threshold=self.analysis.distance_treshold,
                        orientation='left', no_labels=True)
        ax1.set_xticks([])
        ax1.set_yticks([])

        # Plot distance matrix.
        axmatrix = fig.add_axes([0.3, 0.1, 0.6, 0.8])
        idx1 = Z1['leaves']
        D = D[idx1,:]
        im = axmatrix.matshow(D, aspect='auto', origin='lower', cmap=pylab.cm.YlGnBu)
        axmatrix.set_xticks([])
        axmatrix.set_yticks([])

        # Plot colorbar.
        axcolor = fig.add_axes([0.91, 0.1, 0.02, 0.8])
        pylab.colorbar(im, cax=axcolor)
        
        # Add widget
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)