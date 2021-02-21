"""
base StarField
"""
import random
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import QPoint
from PySide2.QtGui import QVector3D, QPen, QColor, QBrush, QPainterPath


class Star:
    """
    star in space
    """
    def __init__(self):
        self.pos = QVector3D()
        self.prev_z = 0.0
        self.prev_zs = []
        self.tail_length = 5
        self.size = 3.0
        self.max_star_white = 255
        self.max_tail_white = 200

    def set_z(self, value):
        self.prev_zs.append(self.pos.z())
        if len(self.prev_zs) > self.tail_length:
            self.prev_zs.pop(0)

        self.prev_z = self.pos.z()
        self.pos.setZ(value)


class StarField:
    """
    our star field logic
    """
    def __init__(self):
        self.total_stars = 10000
        self.stars = []
        self.width = 200
        self.height = 200
        self.speed = 0.001
        self.star_color = QColor(255, 255, 255)
        self.sky_color = QColor()
        self.size_scale = 2.0

    def initialize_star(self, star):
        star.pos.setX(random.random() * self.size_scale - self.size_scale / 2.0)
        star.pos.setY(random.random() * self.size_scale - self.size_scale / 2.0)
        star.pos.setZ(random.random())
        star.tail_length = random.randint(4, 10)
        star.max_star_white = random.random() * 250
        star.max_tail_white = star.max_star_white - random.random() * star.max_star_white

    def generate(self):
        for i in range(self.total_stars):
            star = Star()
            self.initialize_star(star)
            self.stars.append(star)

    def tick(self):
        for star in self.stars:
            z = star.pos.z() + self.speed
            if z > 1.0:
                z = 0.0
                self.initialize_star(star)
            star.set_z(z)

    def paint(self, painter):
        painter.setPen(QPen(self.sky_color))
        painter.setBrush(QBrush(self.sky_color))
        painter.drawRect(0, 0, self.width, self.height)

        hwidth = self.width / 2
        hheight = self.height / 2
        for star in self.stars:
            x = hwidth + star.pos.x() * star.pos.z() * hwidth * 2
            y = hheight + star.pos.y() * star.pos.z() * hheight * 2

            prev_x = hwidth + star.pos.x() * star.prev_z * hwidth * 2
            prev_y = hheight + star.pos.y() * star.prev_z * hheight * 2

            size = 3.0 * star.pos.z()
            c = star.pos.z() * star.max_star_white
            star_color = QColor(c, c, c)
            painter.setPen(QPen(star_color))
            painter.setBrush(QBrush(star_color))
            painter.drawEllipse(x - size / 2, y - size / 2, size, size)
            painter.drawLine(x, y, prev_x, prev_y)

            painter_path = QPainterPath()

            painter_path.moveTo(QPoint(x, y))
            for prev_i_z in star.prev_zs:
                prev_i_x = hwidth + star.pos.x() * prev_i_z * hwidth * 2
                prev_i_y = hheight + star.pos.y() * prev_i_z * hheight * 2
                painter_path.lineTo(QPoint(prev_i_x, prev_i_y))

            c = star.pos.z() * star.max_tail_white
            trail_color = QColor(c, c, c)
            painter.setPen(QPen(trail_color))
            painter.drawPath(painter_path)



class StarFieldDemoWidget(QtWidgets.QWidget):
    """
    StarField
    """

    def __init__(self):
        super(StarFieldDemoWidget, self).__init__()
        self.setWindowTitle("StarField")
        self.tick_timer = QtCore.QTimer()
        self.tick_timer.setInterval(1)
        self.tick_timer.timeout.connect(self.tick)
        self.star_field = StarField()
        self.star_field.total_stars = 1000
        self.star_field.width = self.width()
        self.star_field.height = self.height()
        self.setCursor(QtCore.Qt.BlankCursor)

    def resizeEvent(self, e):
        self.star_field.width = self.width()
        self.star_field.height = self.height()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            self.star_field.speed *= 2.0
        elif event.key() == QtCore.Qt.Key_Down:
            self.star_field.speed /= 2.0

    def showEvent(self, event):
        self.star_field.generate()
        self.tick_timer.start()

    def closeEvent(self, event):
        self.tick_timer.stop()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.star_field.paint(painter)

    def tick(self):
        self.star_field.tick()
        self.update()

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = StarFieldDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
