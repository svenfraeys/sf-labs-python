from PySide2 import QtCore
from PySide2 import QtWidgets
from slider2d import Slider2DWidget


class MyWidget(QtWidgets.QWidget):
    """example widget
    """

    def __init__(self, parent=None):
        super(MyWidget, self).__init__(parent=parent)
        self.setWindowTitle("Slider2D")

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.__slider2d_widget = Slider2DWidget()
        self.__slider2d_widget.set_value_xy(0.0, 0.0)
        self.__slider2d_widget.set_controller_radius(30)
        self.__slider2d_widget.on_value_x_changed.connect(
            self.__handle_value_x_changed)
        self.__slider2d_widget.on_value_y_changed.connect(
            self.__handle_value_y_changed)

        layout.addWidget(self.__slider2d_widget)
        horizontal_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(horizontal_layout)
        self.__x_spinbox = QtWidgets.QDoubleSpinBox()
        self.__x_spinbox.setMinimum(-100)
        self.__y_spinbox = QtWidgets.QDoubleSpinBox()
        self.__y_spinbox.setMinimum(-100)
        self.__reset_button = QtWidgets.QPushButton("Reset")
        self.__reset_button.clicked.connect(self.__reset)
        horizontal_layout.addWidget(self.__x_spinbox)
        horizontal_layout.addWidget(self.__y_spinbox)
        horizontal_layout.addWidget(self.__reset_button)

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    def __reset(self):
        self.__slider2d_widget.set_value_xy(0.0, 0.0)

    def __handle_value_x_changed(self, value):
        self.__x_spinbox.setValue(value)

    def __handle_value_y_changed(self, value):
        self.__y_spinbox.setValue(value)


def main():
    app = QtWidgets.QApplication([])
    widget = MyWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
