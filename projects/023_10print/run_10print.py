"""
base TenPrint
"""
import random

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import QTimer
from PySide2.QtGui import QColor, QPen


class TenPrint:
    FORWARD = 1
    BACKWARD = 0

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rect = None
        self.result = []

    def tick(self):
        i = len(self.result)
        x = i % self.width
        y = (i - x) / self.height

        if y >= self.height:
            return

        self.result.append(random.randint(0, 1))

    def paint(self, painter):
        chunk_x = self.rect.width() / self.width
        chunk_y = self.rect.height() / self.height
        for i, sign in enumerate(self.result):
            x = i % self.width
            y = (i - x) / self.height

            if sign == self.BACKWARD:
                painter.drawLine(chunk_x * x, y * chunk_y, chunk_x * x + chunk_x, y * chunk_y + chunk_y)
            elif sign == self.FORWARD:
                painter.drawLine(chunk_x * x + chunk_x, y * chunk_y, chunk_x * x, y * chunk_y + chunk_y)
            else:
                raise RuntimeError('unknown')

    def reset(self):
        self.result = []


class TenPrintDemoWidget(QtWidgets.QWidget):
    """
    TenPrint
    """

    def __init__(self):
        super(TenPrintDemoWidget, self).__init__()
        self.setWindowTitle("TenPrint")
        self.tenprint = TenPrint(20, 20)
        self.tick_timer = QTimer()
        self.tick_timer.setInterval(10)
        self.tick_timer.timeout.connect(self.tick)

    def tick(self):
        self.tenprint.tick()
        self.update()

    def showEvent(self, event):
        self.tick_timer.start()
        self.tenprint.rect = self.rect()

    def closeEvent(self, event):
        self.tick_timer.stop()

    def resizeEvent(self, event):
        self.tenprint.rect = self.rect()
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QColor(50, 50, 50))
        painter.setPen(QPen(QColor(200, 200, 200)))
        self.tenprint.paint(painter)

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    def mousePressEvent(self, event):
        self.tenprint.reset()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            self.tenprint.width *= 2
            self.tenprint.height *= 2
            self.tenprint.reset()
            self.update()

        if event.key() == QtCore.Qt.Key_Down:
            self.tenprint.width /= 2
            self.tenprint.height /= 2
            self.tenprint.reset()
            self.update()


def main():
    app = QtWidgets.QApplication([])
    widget = TenPrintDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
