"""ann
"""
import json
import random

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtWidgets import QFileDialog

from sfwidgets.neuralnetwork import Network, NetworkPainter


class NeuralNetworkDemoWidget(QtWidgets.QWidget):
    """
    NeuralNetwork
    """

    def __init__(self):
        super(NeuralNetworkDemoWidget, self).__init__()
        self.setWindowTitle("NeuralNetwork")
        self.tick_timer = QtCore.QTimer()
        self.tick_timer.setInterval(100)
        self.tick_timer.timeout.connect(self.tick)
        self.network = Network(5, [4, 2, 5], 4)
        self.network.setup()
        self.network_painter = NetworkPainter(self.network)
        self.network_painter.rect = self.rect()
        self.exported_weights = []
        self.setCursor(QtCore.Qt.BlankCursor)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_S:
            self.exported_weights = self.network.export_weights()
            res = QtWidgets.QFileDialog.getSaveFileName(self, "Save")
            print(res)
            if res[0]:
                n = self.network.json()
                with open(res[0], 'w') as fp:
                    json.dump(n, fp)

        if event.key() == QtCore.Qt.Key_H:
            self.network_painter.draw_output_value = not self.network_painter.draw_output_value
        if event.key() == QtCore.Qt.Key_L:
            # self.network.import_weights(self.exported_weights)
            res = QFileDialog.getOpenFileName(self, "Load")
            if res[0]:
                with open(res[0], 'r') as fp:
                    data = json.load(fp)
                self.set_network(Network.from_json(data))

        if event.key() == QtCore.Qt.Key_Space:
            self.give_network_random_input()
            self.update()

    def set_network(self, network):
        self.network = network
        self.network_painter.network = network
        self.update()

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def give_network_random_input(self):
        data = []
        for i in range(len(self.network.input_layer)):
            v = -1 + random.random() * 2
            data.append(v)
        self.network.respond(data)

    def showEvent(self, event):
        self.tick_timer.start()
        self.network_painter.rect = self.rect()
        self.give_network_random_input()

    def closeEvent(self, event):
        self.tick_timer.stop()

    def resizeEvent(self, event):
        self.network_painter.rect = self.rect()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.network_painter.paint(painter)

    def tick(self):
        self.update()

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = NeuralNetworkDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
