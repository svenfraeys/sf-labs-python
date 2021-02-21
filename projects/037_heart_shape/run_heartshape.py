"""
base HeartShape
"""
import math
from PySide2 import QtGui, QtCore, QtWidgets
from math import cos, sin, pow
from PySide2.QtGui import QPainterPath, QPolygon

TWO_PI = math.pi * 2


class HeartShapeDemoWidget(QtWidgets.QWidget):
    """
    HeartShape
    """

    def __init__(self):
        super(HeartShapeDemoWidget, self).__init__()
        self.setWindowTitle("HeartShape")
        # self.setCursor(QtCore.Qt.BlankCursor)
        self.tick_timer = QtCore.QTimer()
        self.tick_timer.setInterval(10)
        self.tick_timer.timeout.connect(self.tick)
        self.timedelta = 0.0
        self.shape_to_draw = 'heart2'

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            pass

    def mousePressEvent(self, event):
        self.shape_to_draw = 'circle'

    def mouseMoveEvent(self, event):
        pass

    def showEvent(self, event):
        self.tick_timer.start()

    def closeEvent(self, event):
        self.tick_timer.stop()

    def paintEvent(self, event):
        ptr = QtGui.QPainter(self)
        ptr.translate(150, 150)
        ptr.setRenderHint(QtGui.QPainter.Antialiasing, True)
        path = QPainterPath()
        segments = 200
        for i in range(segments):
            a = i * TWO_PI / (segments - 1)

            r = 7.0  # radius
            r = 1.0 + 7.0 * abs(cos(self.timedelta))

            # circle
            if self.shape_to_draw == 'circle':
                x = r * cos(a) * 5.0
                y = r * sin(a) * 5.0
            elif self.shape_to_draw == 'heart':
                # heart
                x = r * 16 * pow(sin(a), 3)
                y = -r * (13 * cos(a) - 5 * cos(2 * a) - 2 * cos(3 * a) - cos(4 * a))
            elif self.shape_to_draw == 'heart2':
                # heart

                l = 0.0 if a == 0.0 else math.log(abs(a))
                # l = 0
                x = sin(a) * cos(a) * l
                if a != 0:
                    y = pow(abs(a), 0.3) * math.sqrt(cos(a))
                else:
                    y = 0
            else:
                raise RuntimeError('invalid')

            draw_x = 0.0 + x
            draw_y = 0.0 + y
            if i == 0:
                path.moveTo(draw_x, draw_y)
            else:
                path.lineTo(draw_x, draw_y)

        ptr.drawPath(path)

    def tick(self):
        self.update()
        self.timedelta += 0.02

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = HeartShapeDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
