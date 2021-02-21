from PySide2 import QtWidgets, QtGui, QtCore
import marchingsquares
import random


class Particle(object):
    gravity = QtGui.QVector2D(0.0, 9.8 * 0.001)

    def __init__(self):
        self.pos = QtGui.QVector2D()
        self.velocity = QtGui.QVector2D()
        self.life = 0
        self.max_life = 20

    def tick(self):
        self.life += 1
        self.velocity += self.gravity
        self.pos += self.velocity

    def paint(self, painter):
        painter.drawPoint(QtCore.QPoint(self.pos.x(), self.pos.y()))


class ParticleEmitter(object):
    def __init__(self):
        self.pos = QtGui.QVector2D()
        self.direction = QtGui.QVector2D(0.0, -25.0)
        self.particles = []

    def tick(self):
        for p in self.particles:
            p.tick()

        for p in self.particles:
            if p.life > p.max_life:
                self.particles.pop(self.particles.index(p))

    def emit(self, amount):
        for i in range(amount):
            p = Particle()
            p.pos.setX(self.pos.x())
            p.pos.setY(self.pos.y())
            x = self.direction.x() * random.random() + random.random() * 0.1
            x -= 0
            x *= 20
            p.max_life = random.randint(20, 30)
            y = self.direction.y() * random.random() * random.random()

            p.velocity.setX(x)
            p.velocity.setY(y)
            p.velocity.normalize()
            p.velocity *= random.random() * 10.0

            self.particles.append(p)

    def paint(self, painter):
        for p in self.particles:
            p.paint(painter)


class FountainDemoWidget(QtWidgets.QWidget):
    """
    fountain widget
    """

    def __init__(self):
        super(FountainDemoWidget, self).__init__()
        self.setWindowTitle("Fountain")
        self.emitter = ParticleEmitter()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.setInterval(10)

        self.emit_timer = QtCore.QTimer()
        self.emit_timer.timeout.connect(self.emit)
        self.emit_timer.setInterval(5)
        self.mc = marchingsquares.MarchingSquares()
        self.mc.subdiv_x = 30
        self.mc.subdiv_y = 30

        self.mcp = marchingsquares.MarchingCellsPainter(mc=self.mc)
        self.mcp.show_grid = False

    def emit(self):
        self.emitter.emit(1)

    def tick(self):
        self.emitter.tick()
        self.mc.points = [p.pos for p in self.emitter.particles]
        self.mc.calculate_points()
        self.update()

    def pos_emitter(self):
        self.emitter.pos.setX(self.width() / 2)
        self.emitter.pos.setY(self.height())

    def showEvent(self, event):
        self.mc.rect = QtCore.QRect(0, 0, self.width(), self.height())
        self.mc.calculate_grid()
        self.pos_emitter()
        self.timer.start()
        self.emit_timer.start()

    def resizeEvent(self, event):
        self.mc.calculate_grid()
        self.pos_emitter()

    def hideEvent(self, event):
        self.timer.stop()
        self.emit_timer.stop()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        p = QtGui.QPen(QtGui.QColor(0, 0, 0))
        painter.setPen(p)
        self.emitter.paint(painter)
        self.mcp.painter = painter
        self.mcp.paint_grid()
        self.mcp.painter = None

    def sizeHint(self):
        return QtCore.QSize(150, 150)

def main():
    app = QtWidgets.QApplication([])
    w = FountainDemoWidget()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
