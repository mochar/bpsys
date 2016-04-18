from PySide import QtCore, QtGui
import pyqtgraph as pg


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None
     

class CentralWidget(QtGui.QWidget):
    def __init__(self, analysis, parent):
        super(CentralWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.set_up()
        self.plot_data()
        
    def set_up(self):
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
        
        # Table
        table_view = QtGui.QTableView(self)
        table_view.setModel(PandasModel(self.analysis.protein_groups))
        layout.addWidget(table_view)
        layout.addWidget(QtGui.QWidget())
        
        # Graph
        self.plot_widget = pg.PlotWidget(self, left='Log ratio')
        graph_layout = QtGui.QVBoxLayout()
        graph_layout.addWidget(self.plot_widget)
        graph_layout.addSpacing(1)
        layout.addLayout(graph_layout)
    
    def plot_data(self):
        self.plot_widget.plot(self.analysis.protein_groups.log_ratio)