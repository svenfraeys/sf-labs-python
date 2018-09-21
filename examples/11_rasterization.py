from PySide2 import QtWidgets, QtGui, QtCore


class RasterizationDemoWidget(QtWidgets.QWidget):
    """rotating cube
    """

    def __init__(self):
        super(RasterizationDemoWidget, self).__init__()
        self.res_width = 50
        self.res_height = 50
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.tick)
        self.timer.start()
        self.setWindowTitle("Rasterization")

        cube_struct = [
            1, -1, -1,
            -1, -1, -1,
            -1, -1, 1,
            -1, -1, 1,
            1, -1, 1,
            1, -1, -1,
            1, -1, -1,
            1, -1, 1,
            1, 1, -1,
            1, 1, -1,
            1, -1, 1,
            1, 1, 1,
            1, -1, 1,
            1, 1, 1,
            -1, 1, 1,
            -1, 1, 1,
            1, -1, 1,
            -1, -1, 1,
            -1, -1, 1,
            -1, -1, -1,
            -1, 1, 1,
            -1, 1, 1,
            -1, -1, -1,
            -1, 1, -1,
            -1, 1, 1,
            1, 1, 1,
            1, 1, -1,
            1, 1, -1,
            -1, 1, 1,
            -1, 1, -1
        ]
        self.tris = []
        self.total_tris = (len(cube_struct) / 3) / 3
        for i in range(0, len(cube_struct), 3):
            x = cube_struct[i]
            y = cube_struct[i + 1]
            z = cube_struct[i + 2]
            self.tris.append(QtGui.QVector3D(x * 2, y * 2, z * 2))

        self.model = QtGui.QMatrix4x4()

        self.view = QtGui.QMatrix4x4()
        self.view.lookAt(QtGui.QVector3D(-2, -2, -2), QtGui.QVector3D(0, 0, 0),
                         QtGui.QVector3D(0, 1, 0))
        self.perspective = QtGui.QMatrix4x4()

        self.perspective.perspective(45, self.width() / self.height(), 1.0,
                                     10000.0)
        self.perspective, _ = self.perspective.inverted()

    def tick(self):
        self.model.rotate(20, QtGui.QVector3D(0, 1, 0))
        self.update()

    def world_to_screen(self, p, mvp):
        pa = mvp * QtGui.QVector4D(p, 1)
        screenpos = pa.toVector3DAffine()

        x = ((screenpos.x() + 1) / 2) * self.width()
        y = ((screenpos.y() + 1) / 2) * self.height()
        return QtGui.QVector3D(x, y, 0)

    def _sign(self, p1, p2, p3):
        return (p1.x() - p3.x()) * (p2.y() - p3.y()) - (p2.x() - p3.x()) * (
            p1.y() - p3.y())

    def point_in_triangle(self, pt, v1, v2, v3):
        b1 = self._sign(pt, v1, v2) < 0
        b2 = self._sign(pt, v2, v3) < 0
        if not b1 == b2:
            return False
        b3 = self._sign(pt, v3, v1) < 0
        return b1 == b2 and b2 == b3

    def sizeHint(self, *args, **kwargs):
        return QtCore.QSize(200, 200)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            self.res_width = int(self.res_width * 2)
            self.res_height = int(self.res_height * 2)
            self.update()
        if event.key() == QtCore.Qt.Key_Down:
            self.res_width = int(self.res_width / 2)
            self.res_height = int(self.res_height / 2)
            self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        b = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        b.setColor(QtGui.QColor(0, 0, 0))
        painter.setBrush(b)
        mvp = self.perspective * self.view * self.model

        w_chunks = self.width() / self.res_width
        h_chunks = self.height() / self.res_height

        for x in range(self.res_width):
            for y in range(self.res_height):
                sx = (x / float(self.res_width)) * float(self.width())
                sy = (y / float(self.res_height)) * float(self.height())

                for i in range(0, self.total_tris * 3, 3):
                    t1 = self.tris[i]
                    t2 = self.tris[i + 1]
                    t3 = self.tris[i + 2]
                    t1s = self.world_to_screen(t1, mvp)
                    t2s = self.world_to_screen(t2, mvp)
                    t3s = self.world_to_screen(t3, mvp)
                    p = QtGui.QVector3D(sx, sy, 0)

                    if self.point_in_triangle(p, t1s, t2s, t3s):
                        # painter.drawPoint(sx, sy)
                        painter.drawRect(x * w_chunks, y * h_chunks, w_chunks,
                                         h_chunks)
                        break
        painter.drawText(20, 20,
                         "res: {}x{}".format(self.res_width, self.res_height))


def main():
    app = QtWidgets.QApplication([])
    w = RasterizationDemoWidget()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
