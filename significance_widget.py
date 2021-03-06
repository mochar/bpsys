from pprint import pprint
from enum import Enum

from PySide import QtCore, QtGui
import pyqtgraph as pg
import numpy as np

from models import PandasModel
     

class Color(Enum):
    blue = 1
    red = 2
    yellow = 3
    green = 4


class FilterCheckBox(QtGui.QCheckBox):
    changed = QtCore.Signal(object)

    def __init__(self, name, color):
        super(FilterCheckBox, self).__init__(name)
        self.color = color
        self.setStyleSheet('color: {}'.format(color.name))
        self.clicked.connect(lambda: self.changed.emit(self.color))


class SignificanceWidget(QtGui.QWidget):
    def __init__(self, parent, analysis):
        super(SignificanceWidget, self).__init__(parent=parent)
        self.analysis = analysis
        self.set_up()
        
    def set_up(self):
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
        
        # Scatterplot
        self.scatter_widget = pg.PlotWidget(self, enableMenu=False)
        self.scatter_widget.setLabel('left', 'Intensity')
        self.scatter_widget.setLabel('bottom', 'Log ratio')
        self.scatter_widget.setLogMode(x=False, y=True)

        # Histogram
        self.hist_widget = pg.PlotWidget(self)
        self.hist_widget.setLabel('left', '# Proteins')
        self.hist_widget.setXLink(self.scatter_widget)
        
        # Tables
        self.tab_widget = QtGui.QTabWidget(self)
        self.tab_widget.setTabPosition(QtGui.QTabWidget.TabPosition.West)
        self.tab_widget.currentChanged.connect(self.on_tab_change)
        self.table_views = {}
        for sample in self.analysis.samples:
            table_view = QtGui.QTableView(self)
            self.table_views[sample] = table_view
            table_model = PandasModel(self.analysis.protein_groups, sample, parent=self)
            table_view.setModel(table_model)
            table_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
            table_view.verticalHeader().setVisible(False)
            self.tab_widget.addTab(table_view, sample)

        # Filter boxes
        filter_layout = QtGui.QHBoxLayout()
        self.filter_boxes = [
            FilterCheckBox('p > 0.05', Color.blue),
            FilterCheckBox('0.01 < p < 0.05', Color.red),
            FilterCheckBox('0.001 < p < 0.01', Color.yellow),
            FilterCheckBox('p < 0.001', Color.green)
        ]
        for box in self.filter_boxes:
            box.changed.connect(self.filter_table)
            filter_layout.addWidget(box)
            
        # Add widgets to layout
        table_layout = QtGui.QVBoxLayout()
        table_layout.addLayout(filter_layout)
        table_layout.addWidget(self.tab_widget)
        layout.addLayout(table_layout)
        plots_layout = QtGui.QVBoxLayout()
        plots_layout.addWidget(self.hist_widget, 1)
        plots_layout.addWidget(self.scatter_widget, 4)
        layout.addLayout(plots_layout)

    def filter_table(self, color):
        for b in self.filter_boxes: b.setChecked(False)
        if color == Color.green:
            self.filter_boxes[3].setChecked(True)
            max_p = 0.001
        elif color == Color.yellow:
            for b in self.filter_boxes[2:]: b.setChecked(True)
            max_p = 0.01
        elif color == Color.red:
            for b in self.filter_boxes[1:]: b.setChecked(True)
            max_p = 0.05
        else:
            for b in self.filter_boxes: b.setChecked(True)
            max_p = None
       
        for sample, table_view in self.table_views.items():
            model = PandasModel(self.analysis.protein_groups, sample, max_p, self)
            table_view.setModel(model)

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
            plot = self.scatter_widget.plot(
                x=points['log_ratio_{}'.format(sample)],
                y=points['intensity_{}'.format(sample)],
                pen=None, symbolPen=None, symbolSize=7,
                symbolBrush=color, antialias=False)
            plot.sigPointsClicked.connect(self.select_protein)
        
        # Histogram
        self.hist_widget.clear()
        bins = np.linspace(-10, 10, 100)
        data = pgs['log_ratio_{}'.format(sample)]
        y, x = np.histogram(data, bins=bins)
        self.hist_widget.plot(x, y, stepMode=True, fillLevel=0, 
                brush=(0,0,255,150))

    def select_protein(self, plot, points):
        point = points[0]
        text_item = pg.TextItem('sel', anchor=(1, 1), color=(0, 0, 0))
        text_item.setPos(point.pos())
        self.scatter_widget.addItem(text_item)

    def select_pg(self, pg_id):
        table = self.tab_widget.currentWidget()
        table_data = table.model()._data
        i = table_data['id'].tolist().index(pg_id)
        table.selectRow(i)
