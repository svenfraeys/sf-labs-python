from PySide2 import QtWidgets, QtGui, QtCore
import random
import math


def fibonacci_sequence(size):
    """fibonacci
    """
    sequence = []

    for n in range(size):
        if n == 0:
            sequence.append(1)
        elif n == 1:
            sequence.append(1)
        else:
            sequence.append(sequence[-1] + sequence[-2])
    return sequence


class FibonacciGoldenRatioWidget(QtWidgets.QWidget):
    """fibonacci golden ratio
    """

    def __init__(self, length):
        super(FibonacciGoldenRatioWidget, self).__init__()
        self.length = length
        self.size = 10

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        pos = QtGui.QVector2D(float(self.width()) / 2.0, self.height() / 2.0)
        direction = QtGui.QVector2D(1, 0)
        painter_path = QtGui.QPainterPath()
        painter_path.moveTo(pos.toPoint())

        painter_path_smooth = QtGui.QPainterPath()
        painter_path_smooth.moveTo(pos.toPoint())

        for i in fibonacci_sequence(self.length):
            p = QtGui.QPen(QtGui.QColor(255, 255, 255))
            p.setWidth(1)
            # move forward
            p1 = pos
            p2 = pos + direction.normalized() * i * self.size

            # turn 90 degrees and go forward
            direction = QtGui.QVector2D(direction.y(), direction.x() * -1)
            p3 = p2 + direction.normalized() * i * self.size

            # set new position
            pos = p3

            rect = QtCore.QRectF(p1.toPointF(), p3.toPointF())
            r = int(abs(math.sin(i / 0.5)) * 255)
            g = int(abs(math.cos(i / 0.5)) * 255)
            b = int(255 - abs(math.sin(i / 0.5)) * 255)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(r, g, b)))
            p = QtGui.QPen(QtGui.QColor(r, g, b))
            p.setWidth(0)
            painter.setPen(p)
            painter.drawRect(rect)

            painter.setBrush(QtGui.QBrush())
            painter.setPen(QtGui.QPen())

            painter_path.lineTo(p2.toPoint())
            painter_path.lineTo(p3.toPoint())

            painter_path_smooth.cubicTo(p1.toPoint(), p2.toPoint(),
                                        p3.toPoint())

            # painter.drawLine(p1.toPoint(), p2.toPoint())
            # painter.drawLine(p2.toPoint(), p3.toPoint())

        painter.setBrush(QtGui.QBrush())
        p = QtGui.QPen()
        p.setWidth(1)
        p.setColor(QtGui.QColor(100, 100, 100))
        painter.setPen(p)
        painter.drawPath(painter_path)

        painter.setBrush(QtGui.QBrush())
        p = QtGui.QPen()
        p.setWidth(2)
        p.setColor(QtGui.QColor(50, 50, 50))
        painter.setPen(p)
        painter.drawPath(painter_path_smooth)
