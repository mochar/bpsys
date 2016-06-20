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
        if self.analysis.replicas:
            names = [(sample, replica) for sample, replica 
                     in zip(self.analysis.samples, self.analysis.replicas)]
            names = [s for group in names for s in group]
        else:
            names = self.analysis.samples
        cols = ['log_ratio_{}'.format(name) for name in names]
        D = significant.as_matrix(cols)
        
        # Compute and plot dendrogram.
        fig = pylab.figure(figsize=(8,8), facecolor='white')
        ax1 = fig.add_axes([0.01, 0.01, 0.2, 0.91])
        Z1 = dendrogram(self.analysis.z, color_threshold=self.analysis.distance_treshold,
                        orientation='left', no_labels=True)
        plt.axvline(x=self.analysis.distance_treshold, color='k')
        ax1.xaxis.tick_top()
        ax1.set_yticks([])

        # Plot distance matrix.
        axmatrix = fig.add_axes([0.23, 0.01, 0.65, 0.91])
        idx1 = Z1['leaves']
        D = D[idx1,:]
        im = axmatrix.matshow(D, aspect='auto', origin='lower', cmap=pylab.cm.RdYlGn)
        axmatrix.set_xticklabels([''] + names)
        axmatrix.xaxis.set_ticks_position('none')
        axmatrix.set_yticks([])

        # Plot colorbar.
        axcolor = fig.add_axes([0.91, 0.01, 0.02, 0.91])
        pylab.colorbar(im, cax=axcolor)
        
        # Add widget
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)