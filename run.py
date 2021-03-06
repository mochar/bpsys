import sys

from PySide import QtGui
import pyqtgraph as pg

from main_window import MainWindow
from analysis import Analysis


if __name__ == '__main__':
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    pg.setConfigOptions(antialias=True)

    app = QtGui.QApplication([])
    gui = MainWindow(Analysis())
    sys.exit(app.exec_())
