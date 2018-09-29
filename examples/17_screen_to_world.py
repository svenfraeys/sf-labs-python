"""small test setup for converting 2D vectors to 3D vectors"""
from PySide2 import QtWidgets, QtGui, QtCore

DEBUG = True


class Demo(QtWidgets.QWidget):
    def __init__(self):
        super(Demo, self).__init__()
        self.setMouseTracking(True)

        proj = QtGui.QMatrix4x4()
        proj.perspective(40, 1, 1, 1000000)
        proj = proj.inverted()[0]
        self.projection = proj

        self.verts = []
        for i in range(10):
            self.verts.append(QtGui.QVector3D(i, 0, 0))
            self.verts.append(QtGui.QVector3D(0, i, 0))
            self.verts.append(QtGui.QVector3D(0, 0, i))

        self.view = QtGui.QMatrix4x4()
        # self.view.translate(QtGui.QVector3D(-1, -1, -1))
        self.view.lookAt(QtGui.QVector3D(5, 5, 5), QtGui.QVector3D(),
                         QtGui.QVector3D(1, 0, 0))
        self.mouse_pos = QtGui.QVector3D()
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseMove:
            pos = QtGui.QVector3D(event.pos())
            pos = self.device_to_screen(pos)
            self.mouse_pos.setX(pos.x())
            self.mouse_pos.setY(pos.y())
            self.update()
        return False

    def device_to_screen(self, v):
        x = ((v.x() / self.width()) * 2.0) - 1
        y = (((v.y() / self.height()) * 2.0) - 1) * -1
        return QtGui.QVector3D(x, y, 0)

    def world_to_screen(self, v):
        v4 = (self.projection * self.view) * QtGui.QVector4D(v, 1)
        return v4.toVector3DAffine()

    def screen_to_device(self, v):
        x = ((v.x() + 1.0) / 2.0) * self.width()
        y = ((-v.y() + 1.0) / 2.0) * self.height()
        return QtGui.QVector3D(x, y, 0)

    def paint_vertex(self, painter, v3d):
        v = self.world_to_screen(v3d)
        v = self.screen_to_device(v)
        painter.drawRect(v.x() - 3, v.y() - 3, 6, 6)

        if DEBUG:
            painter.drawText(v.x() + 2, v.y() - 5,
                             'x: {} y: {} z: {}'.format(v3d.x(), v3d.y(),
                                                        v3d.z()))

    def paint_screen(self, painter, v2d):
        v = self.screen_to_device(v2d)
        painter.drawRect(v.x() - 3, v.y() - 3, 6, 6)
        painter.drawText(v.x() + 2, v.y() - 5,
                         'x: {} y: {} z: {}'.format(v2d.x(), v2d.y(), v2d.z()))

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        for v in self.verts:
            self.paint_vertex(p, v)

        mouse = QtGui.QVector4D(self.mouse_pos.x(), self.mouse_pos.y(), -1, 1)
        mouse_4d = (self.projection * self.view).inverted()[0] * mouse
        mouse_3d = mouse_4d.toVector3DAffine()
        self.paint_vertex(p, mouse_3d)

        mouse = QtGui.QVector4D(self.mouse_pos.x(), self.mouse_pos.y(), 1, 1)
        mouse_4d = (self.projection * self.view).inverted()[0] * mouse
        mouse_3d = mouse_4d.toVector3DAffine()
        self.paint_vertex(p, mouse_3d)


def main():
    app = QtWidgets.QApplication([])
    w = Demo()
    w.show()
    app.exec_()


main()
