from PySide import QtCore, QtGui


class ClustersWidget(QtGui.QWidget):
    def __init__(self, parent, analysis):
        super(ClustersWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.set_up()
        
    def set_up(self):
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        groups = self.analysis.protein_groups.groupby('cluster').groups
        for cluster, rows in groups.items():
            txt = 'Cluster {}: {} eiwitten'.format(cluster, len(rows))
            layout.addWidget(QtGui.QLabel(txt))

