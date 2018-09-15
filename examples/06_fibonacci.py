from PySide2 import QtWidgets, QtCore
from sfwidgets.fibonacci import FibonacciGoldenRatioWidget


class FibonacciGoldenRatioDemoWidget(QtWidgets.QWidget):
    def __init__(self):
        super(FibonacciGoldenRatioDemoWidget, self).__init__()
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        self.fibonacci_golden_ratio_widget = FibonacciGoldenRatioWidget(2)
        self.fibonacci_golden_ratio_widget.size = 5.0
        self.fibonacci_golden_ratio_widget.length = 1
        layout.addWidget(self.fibonacci_golden_ratio_widget)

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.fibonacci_golden_ratio_widget.length += 1
        else:
            self.fibonacci_golden_ratio_widget.length -= 1
        self.update()


def main():
    app = QtWidgets.QApplication([])
    w = FibonacciGoldenRatioDemoWidget()
    w.setWindowTitle('Fibonacci Golden Ratio')
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
