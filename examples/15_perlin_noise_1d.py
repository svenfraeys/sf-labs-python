from PySide2 import QtGui, QtCore, QtWidgets

import sfwidgets.perlinnoise


class PerlinNoisePainter(object):
    """perlin noise painter
    """

    def __init__(self, painter, rect, perlin_noise):
        self.painter = painter
        self.rect = rect
        self.perlin_noise = perlin_noise

    def paint(self):
        p = QtGui.QPen(QtGui.QColor(0, 0, 0))
        self.painter.setPen(p)
        b = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        self.painter.setBrush(b)
        p = QtGui.QPainterPath()
        p.moveTo(self.rect.bottomLeft())
        for x, n in enumerate(self.perlin_noise.perlin_noise_1d):

            n = n * (float(self.rect.height()) / 2.0) + float(
                self.rect.height()) / 3.0
            if x == 0:
                p.lineTo(QtCore.QPoint(x, n))
            else:
                p.lineTo(QtCore.QPoint(x, n))
        p.lineTo(self.rect.bottomRight())

        self.painter.drawPath(p)


class PerlinNoise1DDemoWidget(QtWidgets.QWidget):
    """perlin noise demo
    """

    def __init__(self):
        super(PerlinNoise1DDemoWidget, self).__init__()
        self.setWindowTitle('Perlin Noise 1D')

        self.perlin_noise = sfwidgets.perlinnoise.PerlinNoise1D()
        self.perlin_noise.total_octaves = 4

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            self.perlin_noise.bias -= 0.2
            self.perlin_noise.generate_noise()
            self.update()
        if event.key() == QtCore.Qt.Key_Down:
            self.perlin_noise.bias += 0.2
            self.perlin_noise.generate_noise()
            self.update()
        if event.key() == QtCore.Qt.Key_Right:
            self.perlin_noise.total_octaves += 1

            # depending on the size we can do x amount of octaves
            # if self.perlin_noise.total_octaves == 9:
            #     self.perlin_noise.total_octaves = 8
            self.perlin_noise.generate_noise()
            self.update()
        elif event.key() == QtCore.Qt.Key_Left:
            self.perlin_noise.total_octaves -= 1

            if self.perlin_noise.total_octaves < 1:
                self.perlin_noise.total_octaves = 1

            self.perlin_noise.generate_noise()
            self.update()

    def mouseReleaseEvent(self, event):
        self.perlin_noise.generate_seed()
        self.perlin_noise.generate_noise()
        self.update()

    def showEvent(self, event):
        self.perlin_noise.total_count = self.width()
        self.perlin_noise.generate_seed()
        self.perlin_noise.generate_noise()
        self.update()

    def resizeEvent(self, event):
        self.perlin_noise.total_count = self.width()
        self.perlin_noise.generate_seed()
        self.perlin_noise.generate_noise()
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        painter.drawText(20, 20, "count {} | octaves {} | bias {}".format(
            self.perlin_noise.total_count, self.perlin_noise.total_octaves,
            self.perlin_noise.bias))

        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        rect = QtCore.QRect(0, 0, self.width(), self.height())
        p = PerlinNoisePainter(painter, rect, self.perlin_noise)
        p.paint()

    def sizeHint(self):
        return QtCore.QSize(256, 256)


def main():
    app = QtWidgets.QApplication([])
    w = PerlinNoise1DDemoWidget()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
