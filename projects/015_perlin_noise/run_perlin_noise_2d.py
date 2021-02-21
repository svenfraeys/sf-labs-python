from PySide2 import QtGui, QtCore, QtWidgets
import perlinnoise


class PerlinNoise2DPainter(object):
    """pains a perlin 2d noise within a given rect
    """

    def __init__(self, painter, rect, perlin_noise_2d):
        self.painter = painter
        self.rect = rect
        self.perlin_noise_2d = perlin_noise_2d

    def paint(self):
        if not self.perlin_noise_2d.noise:
            return
        p = QtGui.QPen()
        self.painter.setPen(p)

        b = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        self.painter.setBrush(b)
        paint_width = self.rect.width() / self.perlin_noise_2d.width
        paint_height = self.rect.height() / self.perlin_noise_2d.height

        for y in range(self.perlin_noise_2d.height):
            for x in range(self.perlin_noise_2d.width):
                sample = self.perlin_noise_2d.noise[
                    self.perlin_noise_2d.width * y + x]
                c = sample * 255

                b = QtGui.QBrush(QtGui.QColor(c, c, c))
                self.painter.setBrush(b)

                p = QtGui.QPen(QtGui.QColor(c, c, c))
                self.painter.setPen(p)

                paint_x = (x / float(
                    self.perlin_noise_2d.width)) * self.rect.width()
                paint_y = (y / float(
                    self.perlin_noise_2d.height)) * self.rect.height()
                self.painter.drawRect(paint_x, paint_y, paint_width,
                                      paint_height)


class PerlinNoise2DDemoWidget(QtWidgets.QWidget):
    """perlin noise demo
    """

    def __init__(self):
        super(PerlinNoise2DDemoWidget, self).__init__()
        self.setWindowTitle('Perlin Noise 2D')

        self.perlin_noise = perlinnoise.PerlinNoise2D()
        self.perlin_noise.octaves = 10
        self.perlin_noise.bias = 1.0
        self.perlin_noise.width = 128
        self.perlin_noise.height = 128

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            self.perlin_noise.bias -= 0.2
            if self.perlin_noise.bias < 0.2:
                self.perlin_noise.bias = 0.2
            self.perlin_noise.generate_noise()
            self.update()
        if event.key() == QtCore.Qt.Key_Down:
            self.perlin_noise.bias += 0.2
            self.perlin_noise.generate_noise()
            self.update()
        if event.key() == QtCore.Qt.Key_Right:
            self.perlin_noise.octaves += 1
            self.perlin_noise.generate_noise()
            self.update()
        elif event.key() == QtCore.Qt.Key_Left:
            self.perlin_noise.octaves -= 1

            if self.perlin_noise.octaves < 1:
                self.perlin_noise.octaves = 1

            self.perlin_noise.generate_noise()
            self.update()
        elif event.key() == QtCore.Qt.Key_Plus:
            self.perlin_noise.width *= 2
            self.perlin_noise.height *= 2
            self.perlin_noise.generate_seed()
            self.perlin_noise.generate_noise()
            self.update()
        elif event.key() == QtCore.Qt.Key_Minus:
            self.perlin_noise.width /= 2
            self.perlin_noise.height /= 2
            self.perlin_noise.generate_seed()
            self.perlin_noise.generate_noise()
            self.update()
        elif event.key() == QtCore.Qt.Key_Space:
            self.perlin_noise.generate_seed()
            self.perlin_noise.generate_noise()
            self.update()

    def mouseReleaseEvent(self, event):
        self.perlin_noise.generate_seed()
        self.perlin_noise.generate_noise()
        self.update()

    def showEvent(self, event):
        self.perlin_noise.generate_seed()
        self.perlin_noise.generate_noise()
        self.update()

    def resizeEvent(self, event):
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        rect = QtCore.QRect(0, 0, self.width(), self.height())
        p = PerlinNoise2DPainter(painter, rect, self.perlin_noise)
        p.paint()

        c = 230
        painter.setPen(QtGui.QColor(c, c, c))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(c, c, c)))
        painter.drawRect(7, 7, 200, 18)
        painter.setPen(QtGui.QPen())
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        painter.drawText(20, 20, "size {}x{} | octaves {} | bias {}".format(
            self.perlin_noise.width, self.perlin_noise.height,
            self.perlin_noise.octaves,
            self.perlin_noise.bias))

    def sizeHint(self):
        return QtCore.QSize(256, 256)


def main():
    app = QtWidgets.QApplication([])
    w = PerlinNoise2DDemoWidget()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
