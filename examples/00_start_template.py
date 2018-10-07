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
        self.tick_timer = QtCore.QTimer()
        self.tick_timer.setInterval(100)
        self.tick_timer.timeout.connect(self.tick)

    def showEvent(self, event):
        self.tick_timer.start()

    def closeEvent(self, event):
        self.tick_timer.stop()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.drawEllipse(0, 0, self.width(), self.height())

    def tick(self):
        print("tick")

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = TemplateDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
