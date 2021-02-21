from PySide2 import QtWidgets, QtCore

from mandelbrot import MandelbrotWidget

app = QtWidgets.QApplication([])


class MandelbrotDemoWidget(QtWidgets.QWidget):
    def __init__(self):
        super(MandelbrotDemoWidget, self).__init__()
        self.iterations = [
            2,
            4,
            8,
            16,
            32,
            64,
            100
        ]
        self.iteration_index = 0
        self.setWindowTitle("Mandelbrot Demo")
        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel()
        self.mandelbrot_widget = MandelbrotWidget()
        self.mandelbrot_widget.max_iterations = 100

        layout.addWidget(self.label)
        layout.addWidget(self.mandelbrot_widget)
        self.setLayout(layout)
        self._update_label()

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    def _update_label(self):
        self.label.setText(
            "Mandelbrot iteration {}".format(
                self.mandelbrot_widget.max_iterations))

    def mouseReleaseEvent(self, event):
        i = self.iterations[self.iteration_index % len(self.iterations)]
        self.mandelbrot_widget.max_iterations = i
        self.mandelbrot_widget.update()
        self._update_label()
        self.iteration_index += 1


def main():
    w = MandelbrotDemoWidget()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
