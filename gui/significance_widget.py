from PySide import QtCore, QtGui
import pyqtgraph as pg
import numpy as np

from .models import PandasModel
     

class SignificanceWidget(QtGui.QWidget):
    def __init__(self,parent, analysis=None):
        super(SignificanceWidget, self).__init__(parent=parent)
        self.analysis = analysis
        if analysis is not None:
            self.set_up()
        
    def set_up(self):
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
        
        # Scatterplot
        self.scatter_widget = pg.PlotWidget(self)
        self.scatter_widget.setLabel('left', 'Intensity')
        self.scatter_widget.setLabel('bottom', 'Ratio')
        self.scatter_widget.setLogMode(x=False, y=True)

        # Histogram
        self.hist_widget = pg.PlotWidget(self)
        self.hist_widget.setLabel('left', '# Proteins')
        self.hist_widget.setXLink(self.scatter_widget)
        
        # Tables
        self.tab_widget = QtGui.QTabWidget(self)
        self.tab_widget.setTabPosition(QtGui.QTabWidget.TabPosition.West)
        self.tab_widget.currentChanged.connect(self.on_tab_change)
        for sample in self.analysis.samples:
            columns = ['id', 'protein_ids'] 
            columns += [c for c in self.analysis.protein_groups if c.endswith('_{}'.format(sample))]
            table_view = QtGui.QTableView(self)
            table_view.setModel(PandasModel(self.analysis.protein_groups[columns]))
            self.tab_widget.addTab(table_view, sample)
            
        # Add widgets to layout
        layout.addWidget(self.tab_widget)
        plots_layout = QtGui.QVBoxLayout()
        plots_layout.addWidget(self.hist_widget, 1)
        plots_layout.addWidget(self.scatter_widget, 4)
        layout.addLayout(plots_layout)
        
    def on_tab_change(self, tab_index):
        sample = self.analysis.samples[tab_index]
        self.plot_data(sample)
        
    def plot_data(self, sample):
        colors = ('b', 'r', 'y', 'g')
        pgs = self.analysis.protein_groups
        p_column = pgs['p_{}'.format(sample)]
        data = (pgs[p_column > 0.05], pgs[p_column.between(0.01, 0.05)],
                pgs[p_column.between(0.001, 0.01)], pgs[p_column < 0.001])

        # Scatterplot
        self.scatter_widget.clear()
        for color, points in zip(colors, data):
            self.scatter_widget.plot(
                x=points['log_ratio_{}'.format(sample)],
                y=points['intensity_{}'.format(sample)],
                pen=None, symbolPen=None, symbolSize=7,
                symbolBrush=color, antialias=False)
        
        # Histogram
        self.hist_widget.clear()
        bins = np.linspace(-10, 10, 100)
        data = pgs['log_ratio_{}'.format(sample)]
        y, x = np.histogram(data, bins=bins)
        self.hist_widget.plot(x, y, stepMode=True, fillLevel=0, 
                brush=(0,0,255,150))

