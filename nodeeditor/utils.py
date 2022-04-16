import traceback

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


def dump_exeption(e):
    print(e)
    traceback.print_tb(e.__traceback__)


def loadStylesheet(filename):
    print("STYLE loading:", filename)
    file = QFile(filename)
    file.open(QFile.ReadOnly | QFile.Text)
    stylesheet = file.readAll()
    QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf8'))


def loadStylesheets(*args):
    res = ''
    for arg in args:
        file = QFile(arg)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        res += '\n' + str(stylesheet, encoding='utf8')
    QApplication.instance().setStyleSheet(res)
