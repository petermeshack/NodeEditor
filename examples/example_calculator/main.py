import os.path
import sys

from PyQt5.QtWidgets import *



sys.path.insert(0,os.path.join( os.path.dirname(__file__), "..", ".."))
from examples.example_calculator.calc_window import CalculatorWindow
if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyle('Fusion')
    wnd = CalculatorWindow()
    wnd.show()

    sys.exit(app.exec_())