from PySide2 import QtWidgets
from sfwidgets.lsystem import LSystemWidget, Vec2

PRESETS = {
    'Fractal tree': {
        'variables': ['0', '1'],
        'constants': ['[', ']'],
        'axiom': '0',
        'rules': {'1': '11', '0': '1[0]0'}
    }
}


class LSystemMainWindow(QtWidgets.QMainWindow):
    """lsystem widget
    """

    def __init__(self):
        super(LSystemMainWindow, self).__init__()
        self.setWindowTitle('L System')
        main = QtWidgets.QWidget(self)

        layout = QtWidgets.QHBoxLayout()
        main.setLayout(layout)

        tools_layout = QtWidgets.QVBoxLayout()
        layout.addLayout(tools_layout, -1)
        self.lsystem_widget = LSystemWidget()
        layout.addWidget(self.lsystem_widget)

        self.calculate_button = QtWidgets.QPushButton('Calculate')
        self.calculate_button.clicked.connect(self.__do_calculate)

        form_layout = QtWidgets.QFormLayout()
        self.num_iterations_spinbox = QtWidgets.QSpinBox()
        self.num_iterations_spinbox.setValue(1)
        form_layout.addRow('Iterations', self.num_iterations_spinbox)

        self.presets_combobox = QtWidgets.QComboBox()
        self.presets_combobox.addItems(PRESETS.keys())

        tools_layout.addLayout(form_layout)
        tools_layout.addWidget(self.presets_combobox)
        tools_layout.addWidget(self.calculate_button)

        self.setCentralWidget(main)

    def __do_calculate(self):
        data = PRESETS[self.presets_combobox.currentText()]
        self.lsystem_widget.iterations = self.num_iterations_spinbox.value()
        self.lsystem_widget.axiom = data['axiom']
        self.lsystem_widget.constants = data['constants']
        self.lsystem_widget.variables = data['variables']
        self.lsystem_widget.rules = data['rules']
        self.lsystem_widget.scale = Vec2(1.0, 1.0) / self.num_iterations_spinbox.value()
        self.lsystem_widget.calc_result()
        self.lsystem_widget.update()


def main():
    app = QtWidgets.QApplication([])
    w = LSystemMainWindow()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
