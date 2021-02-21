"""mandelbrot painting
"""
from PySide2 import QtWidgets, QtGui, QtCore


def map_value(value, left_min, left_max, right_min, right_max):
    """map a value between a given min and max
    """
    left_span = left_max - left_min
    right_span = right_max - right_min

    normalized_value = (value - left_min) / left_span
    right_value = (normalized_value * right_span) + right_min
    return right_value


class MandelbrotWidget(QtWidgets.QWidget):
    """mandelbrot widget
    """

    def __init__(self, parent=None):
        super(MandelbrotWidget, self).__init__(parent=parent)
        self.max_iterations = 10
        self.max_value = 16.0
        self.range_min = -1.5
        self.range_max = 1.5
        self.offset_x = -1.0

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        for x in range(self.width()):
            for y in range(self.height()):

                # real component
                a = map_value(float(x), 0.0, float(self.width()),
                              self.range_min + self.offset_x, self.range_max)
                # imaginary component
                b = map_value(float(y), 0.0, float(self.height()),
                              self.range_min, self.range_max)
                original_a = a
                original_b = b
                n = 0
                while n < self.max_iterations:
                    aa = a * a
                    bb = b * b
                    twoab = 2.0 * a * b
                    a = aa - bb + original_a
                    b = twoab + original_b

                    # aa = a * a - b * b
                    # bb = 2 * a * b

                    # a = aa + original_a
                    # b = bb + original_b

                    # not bounded stop it
                    if aa + bb > 16.0:
                        break

                    n += 1
                brightness = 200
                if n == self.max_iterations:
                    brightness = 0
                brightness = map_value(n, 0.0, self.max_iterations, 0.0, 255.0)

                color = QtGui.QColor(brightness, brightness, brightness)
                painter.setPen(color)
                painter.drawPoint(x, y)

    def sizeHint(self):
        return QtCore.QSize(400, 400)
