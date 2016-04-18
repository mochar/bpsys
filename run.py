import sys

from PySide import QtGui

from gui.main_window import MainWindow
from analysis import Analysis


if __name__ == '__main__':
    app = QtGui.QApplication([])
    gui = MainWindow(Analysis())
    sys.exit(app.exec_())