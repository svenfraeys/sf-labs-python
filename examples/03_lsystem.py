from PySide2 import QtWidgets, QtGui, QtCore
from sfwidgets.lsystem import LSystemWidget, Vec2, calc_lsystem
import sfwidgets.lsystem as lsys


class LSystemMainWindow(QtWidgets.QWidget):
    """lsystem widget
    """

    def __init__(self):
        super(LSystemMainWindow, self).__init__()
        self.index = 0
        self.pen = QtGui.QPen(QtGui.QColor(255, 0, 0))
        self.presets = [
            ('fractal_binary_tree', 2, (350.0, 400.0), 50.0),
            ('fractal_binary_tree', 4, (350.0, 400.0), 15.0),
            ('fractal_binary_tree', 6, (350.0, 400.0), 5.0),
            ('fractal_binary_tree', 9, (350.0, 400.0), 0.6),
            ('fractal_binary_tree', 10, (350.0, 400.0), 0.3),
            ('koch_curve', 2, (150.0, 400.0), 50.0),
            ('koch_curve', 4, (150.0, 400.0), 5.0),
            ('koch_curve', 6, (100.0, 400.0), 0.7),
            ('sierpinski_triangle', 4, (150.0, 400.0), 25.0),
            ('sierpinski_triangle', 8, (150.0, 400.0), 1.5),
            ('sierpinski_arrow_head_curve', 2, (150.0, 125.0), 100.0),
            ('sierpinski_arrow_head_curve', 5, (150.0, 325.0), 10.0),
            ('sierpinski_arrow_head_curve', 8, (50.0, 20.0), 2.0),
            ('fractal_plant', 1, (200.0, 250.0), 100.0),
            ('fractal_plant', 3, (200.0, 250.0), 20.0),
            ('fractal_plant', 6, (200.0, 250.0), 2.0),
            ('dragon_curve', 2, (250.0, 150.0), 7.0),
            ('dragon_curve', 5, (250.0, 150.0), 7.0),
            ('dragon_curve', 7, (250.0, 150.0), 7.0),
            ('dragon_curve', 8, (250.0, 150.0), 7.0),
            ('dragon_curve', 9, (250.0, 150.0), 7.0),
            ('dragon_curve', 10, (250.0, 150.0), 7.0),

        ]

    def paintEvent(self, event):
        super(LSystemMainWindow, self).paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.resetTransform()
        painter.setPen(self.pen)

        type_, iterations, pos, scale = self.presets[self.index]
        txt = '{} n={}'.format(type_, iterations)
        painter.drawText(QtCore.QPointF(250, 20), txt)
        painter.translate(QtCore.QPoint(pos[0], pos[1]))
        if type_ == 'fractal_plant':
            value = lsys.calc_fractal_plant(iterations)
            lsys.paint_fractal_plant(painter, value, size=scale)
        elif type_ == 'dragon_curve':
            value = lsys.calc_dragon_curve(iterations)
            lsys.paint_dragon_curve(painter, value, size=scale)
        elif type_ == 'sierpinski_arrow_head_curve':
            value = lsys.calc_sierpinski_arrow_head_curve(iterations)
            lsys.paint_sierpinski_arrow_head_curve(painter, value, size=scale)
        elif type_ == 'sierpinski_triangle':
            value = lsys.calc_sierpinski_triangle(iterations)
            lsys.paint_sierpinski_triangle(painter, value, size=scale)
        elif type_ == 'koch_curve':
            value = lsys.calc_koch_curve(iterations)
            lsys.paint_koch_curve(painter, value, size=scale)
        elif type_ == 'fractal_binary_tree':
            value = lsys.calc_fractal_binary_tree(iterations)
            lsys.paint_fractal_binary_tree(painter, value, size=scale)

        # painter.drawLine(0.0, 0.0, 20.0, 20.0)

        head_curve = lsys.calc_sierpinski_arrow_head_curve(5)
        # lsys.paint_sierpinski_arrow_head_curve(painter, head_curve)

        # result = lsys.calc_koch_curve(5)
        # lsys.paint_koch_curve(painter, result, 20)
        # dc = lsys.calc_dragon_curve(10)
        # lsys.paint_dragon_curve(painter, dc)

        # triangle = lsys.calc_sierpinski_triangle(4)
        # lsys.paint_sierpinski_triangle(painter, triangle, size=20.0)
        # fractal_plant = lsys.calc_fractal_plant(6)
        # lsys.paint_fractal_plant(painter, fractal_plant)

    def mousePressEvent(self, *args, **kwargs):
        self.index += 1
        if self.index + 1 > len(self.presets):
            self.index = 0
        self.update()


def main():
    app = QtWidgets.QApplication([])
    w = LSystemMainWindow()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
