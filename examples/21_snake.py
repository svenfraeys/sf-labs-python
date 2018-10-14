"""
base SnakeGame
"""
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import QTimer

from sfwidgets.snake import SnakeGame


class SnakeGameDemoWidget(QtWidgets.QWidget):
    """
    SnakeGame
    """

    def __init__(self):
        super(SnakeGameDemoWidget, self).__init__()
        self.resize(QtCore.QSize(300, 300))
        self.setWindowTitle("SnakeGame")
        self.snake_game = SnakeGame()
        self.snake_game.rect = self.rect()
        self.snake_game.width = self.width()
        self.snake_game.height = self.height()
        self.tick_timer = QTimer()
        self.tick_timer.setInterval(100)
        self.tick_timer.timeout.connect(self.tick)

    def showEvent(self, event):
        self.snake_game.rect = self.rect()
        self.tick_timer.start()

    def resizeEvent(self, event):
        self.snake_game.rect = self.rect()

    def closeEvent(self, event):
        self.tick_timer.stop()

    def tick(self):
        self.snake_game.tick()
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.snake_game.paint(painter)

    def keyPressEvent(self, event):
        self.snake_game.key_pressed(event.key())

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = SnakeGameDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
