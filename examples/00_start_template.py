"""
base template
"""
from PySide2 import QtGui, QtCore, QtWidgets


class TemplateDemoWidget(QtWidgets.QWidget):
    """
    Template
    """

    def __init__(self):
        super(TemplateDemoWidget, self).__init__()
        self.setWindowTitle("Template")

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.drawEllipse(0, 0, self.width(), self.height())

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = TemplateDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
