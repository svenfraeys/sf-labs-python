"""ann
"""
from PySide2.QtGui import QBrush
from PySide2.QtGui import QColor
from PySide2.QtGui import QPen
from PySide2 import QtGui, QtCore, QtWidgets
import math
import random


class Neuron:
    def __init__(self, previous=None):
        self.inputs = []
        self.weigths = []
        self.output = 0.0

        if previous:
            for input_ in previous:
                self.inputs.append(input_)
                self.weigths.append(-1.0 + random.random() * 2.0)

    def respond(self):
        sum_input = 0.0
        for i, input_ in enumerate(self.inputs):
            sum_input += input_.output * self.weigths[i]
        self.output = Network.sigmoid(sum_input)


class Network:
    def __init__(self, inputs, layers, outputs):
        self.total_inputs = inputs
        self.total_layers = layers
        self.total_outputs = outputs

        self.input_layer = []
        self.hidden_layers = []
        self.output_layer = []

    def respond(self, data):
        for i, n in enumerate(self.input_layer):
            n.output = data[i]

        for layer in self.hidden_layers:
            for neuron in layer:
                neuron.respond()

        for neuron in self.output_layer:
            neuron.respond()

    @classmethod
    def sigmoid(cls, x):
        return 2.0 / (1.0 + math.exp(-2.0 * x)) - 1.0

    def setup(self):
        for i in range(self.total_inputs):
            self.input_layer.append(Neuron())

        prev_layer = self.input_layer

        for i, layer_count in enumerate(self.total_layers):
            hidden_layer_i = []

            for j in range(layer_count):
                n = Neuron(previous=prev_layer)
                hidden_layer_i.append(n)
            self.hidden_layers.append(hidden_layer_i)
            prev_layer = hidden_layer_i

        for i in range(self.total_outputs):
            self.output_layer.append(Neuron(prev_layer))


class NetworkPainter:
    def __init__(self, network):
        self.network = network
        self.rect = None
        self.neuron_pen = QPen()
        self.neuron_brush = QBrush(QColor())

    def paint(self, painter):
        painter.drawText(20, 20, str(len(self.network.input_layer)))
        total_layers = len(self.network.hidden_layers) + 2
        chunk_x = float(self.rect.width()) / (total_layers + 1)
        layers = [self.network.input_layer] + self.network.hidden_layers + [
            self.network.output_layer]

        x = chunk_x
        neuron_pos = {}
        # draw neurons
        painter.setPen(self.neuron_pen)
        painter.setBrush(self.neuron_brush)
        for i in range(total_layers):
            layer = layers[i]
            total_neurons = len(layer)
            chunk_y = float(self.rect.height()) / (total_neurons + 1)
            y = chunk_y
            for j in range(total_neurons):
                neuron = layer[j]

                painter.drawEllipse(x - 10, y - 10, 20, 20)
                neuron_pos[neuron] = (x, y)
                y += chunk_y

            x += chunk_x

        # draw connections
        for layer in layers:
            for neuron in layer:
                x, y = neuron_pos[neuron]
                for i, neuron_input in enumerate(neuron.inputs):
                    w = neuron.weigths[i]

                    if w >= 0.0:
                        c = QColor(0, 0, 100 * w)
                    elif w < 0.0:
                        c = QColor(w * -1.0 * 100, 0, 0)

                    painter.setPen(QPen(c))
                    input_x, input_y = neuron_pos[neuron_input]
                    painter.drawLine(x, y, input_x, input_y)

        for n, pos in neuron_pos.items():
            x, y = pos
            o = (n.output + 1.0) / 2.0
            b = QBrush(QColor(o * 255, o * 255, o * 255))
            painter.setBrush(b)
            painter.drawEllipse(x - 10, y - 10, 20, 20)
            painter.drawText(x, y - 20, str('{:.2f}'.format(n.output)))


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

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            self.give_network_random_input()
            self.update()

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def give_network_random_input(self):
        data = []
        for i in range(len(self.network.input_layer)):
            v = random.random()
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
        painter.drawEllipse(0, 0, self.width(), self.height())
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
