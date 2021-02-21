from PySide2 import QtWidgets, QtCore
from diamondsquare import DiamondSquareWidget


class DiamondSquareDemoWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DiamondSquareDemoWidget, self).__init__()
        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel("d")
        self.setLayout(layout)
        layout.addWidget(self.label)

        self.diamond_square_widget = DiamondSquareWidget(2)
        self.update_label()

        layout.addWidget(self.diamond_square_widget)

    def update_label(self):
        self.label.setText(
            "n = {}".format(self.diamond_square_widget.diamond_square.n))

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.diamond_square_widget.diamond_square.set_n(
                self.diamond_square_widget.diamond_square.n + 1)
            self.diamond_square_widget.diamond_square.generate()
        elif event.button() == QtCore.Qt.MiddleButton:
            self.diamond_square_widget.diamond_square.generate()
        else:
            self.diamond_square_widget.diamond_square.set_n(
                self.diamond_square_widget.diamond_square.n - 1)
            self.diamond_square_widget.diamond_square.generate()
        self.update_label()
        self.update()


def main():
    app = QtWidgets.QApplication([])
    w = DiamondSquareDemoWidget()
    w.setWindowTitle('Diamond Square')
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
