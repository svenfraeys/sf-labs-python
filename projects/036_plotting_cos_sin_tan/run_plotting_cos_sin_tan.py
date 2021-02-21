"""
Example of plotting on a QPixmap
"""
from math import sin, cos, tan

from PySide2.QtCore import QRect, QSize, QTimer
from PySide2.QtGui import QPainter, QColor, QPixmap, QPen
from PySide2.QtWidgets import QWidget, QApplication


def plot_line(x):
    return x


def plot_sin(x, i):
    return sin(x + i)


class Plotting(QWidget):
    """
    Lattice Boltzmann Widget
    """

    def __init__(self):
        super(Plotting, self).__init__()
        self.s = 60  # size
        self.hs = self.s / 2
        self.pixmap = QPixmap(self.s, self.s)
        self.plot_range = 3.0
        # self.plot(plot_sin)

        self.tick_timer = QTimer()
        self.tick_timer.setInterval(50)
        self.tick_timer.timeout.connect(self.tick)
        self.tick_timer.start()
        self.counter = 0.1

        self.painter = QPainter(self.pixmap)

        self.painter.fillRect(QRect(0, 0, self.s, self.s), QColor())
        self.painter.translate(self.hs, self.hs)

    def tick(self):
        self.painter.fillRect(QRect(-self.hs, -self.hs, self.s, self.s),
                              QColor(20, 20, 40))

        c = self.counter
        self.painter.setPen(QPen(QColor(180, 40, 60)))
        self.plot(lambda x: sin(x * 8.0 + c))

        self.painter.setPen(QPen(QColor(40, 180, 60)))
        self.plot(lambda x: cos(x * 8.0 + c))
        # self.plot(lambda x: 1.0 - sin(x))

        self.painter.setPen(QPen(QColor(40, 60, 180)))
        self.plot(lambda x: tan(x))

        # self.painter.setPen(QPen(QColor(180, 40, 60)))
        # self.plot(lambda x: plot_sin(x, math.cos(self.counter) * 20))
        #
        # self.painter.setPen(QPen(QColor(40, 180, 60)))
        # self.plot(lambda x: plot_sin(x, math.sin(self.counter) * 20))
        #
        # self.painter.setPen(QPen(QColor(40, 60, 180)))
        # self.plot(lambda x: math.tan(x * math.cos(self.counter * 20)))
        #
        self.repaint()
        self.counter += 0.05

    def sizeHint(self, *args, **kwargs):
        return QSize(300, 300)

    def paintEvent(self, event):
        # self.image.setPixelColor(0, 0, QColor(0, 255, 0))

        painter = QPainter(self)
        # painter.translate(self.width() / 2, self.height() / 2)
        # painter.drawEllipse(-5, -5, 20, 20)
        r = QRect(0, 0, self.width(), self.height())
        painter.fillRect(r, QColor())
        painter.drawPixmap(r, self.pixmap)

    def plot_point(self, painter, x, y, paintx):
        """
        Plot a point on given floats
        """
        # x = int(x * self.hs)
        x = paintx
        y = int(y / self.plot_range * self.hs) * -1
        painter.drawPoint(x, y)

    def plot(self, func):
        for i in range(self.s):
            x = (i - self.hs) / float(self.s)
            # x = (i - self.s) / float(self.s)
            x *= self.plot_range
            y = func(x)

            # print('x: %s, y: %s' % (x, y))
            paintx = i - self.hs
            self.plot_point(self.painter, x, y, paintx)
            j = y * float(self.s)


app = QApplication([])
w = Plotting()
w.show()
app.exec_()
