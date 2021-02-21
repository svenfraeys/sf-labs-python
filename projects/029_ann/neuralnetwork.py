import copy
from PySide2.QtGui import QBrush
from PySide2.QtGui import QColor
from PySide2.QtGui import QPen
import math
import random


class Neuron:
    def __init__(self, previous=None):
        self.inputs = []
        self.weights = []
        self.output = 0.0

        if previous:
            for input_ in previous:
                self.inputs.append(input_)
                self.weights.append(-1.0 + random.random() * 2.0)

    def respond(self):
        sum_input = 0.0
        for i, input_ in enumerate(self.inputs):
            sum_input += input_.output * self.weights[i]
        self.output = Network.sigmoid(sum_input)


class Network:
    def __init__(self, inputs, layers, outputs):
        self.total_inputs = inputs
        self.total_layers = layers
        self.total_outputs = outputs

        self.input_layer = []
        self.hidden_layers = []
        self.output_layer = []

    @classmethod
    def from_json(cls, data):
        nw = cls(data['total_inputs'], data['total_layers'],
                 data['total_outputs'])
        nw.setup()
        nw.import_weights(data['weights'])
        return nw

    def json(self):
        return {
            'total_inputs': copy.deepcopy(self.total_inputs),
            'total_layers': copy.deepcopy(self.total_layers),
            'total_outputs': copy.deepcopy(self.total_outputs),
            'weights': self.export_weights()
        }

    def export_weights(self):
        weights_list = []

        for layer in self.hidden_layers:
            for neuron in layer:
                weights_list += neuron.weights

        for neuron in self.output_layer:
            weights_list += neuron.weights
        return weights_list

    def import_weights(self, weights):
        weights = list(reversed(weights))

        def fill_neuron(n):
            tw = len(n.inputs)

            for i in range(tw):
                n.weights[i] = weights.pop()

        for layer in self.hidden_layers:
            for neuron in layer:
                fill_neuron(neuron)

        for neuron in self.output_layer:
            fill_neuron(neuron)

    def transfer_neuron_data(self, from_n, to_n):
        to_n.weights = list(from_n.weights)
        to_n.output = from_n.output

    def clone(self):
        cp = Network(self.total_inputs, list(self.total_layers),
                     self.total_outputs)
        cp.setup()
        for i, n in enumerate(self.input_layer):
            self.transfer_neuron_data(n, cp.input_layer[i])

        for i, n in enumerate(self.output_layer):
            self.transfer_neuron_data(n, cp.input_layer[i])

        for i, layer in enumerate(self.hidden_layers):
            for j, neuron in enumerate(layer):
                self.transfer_neuron_data(neuron, cp.hidden_layers[i][j])
        return cp

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
        self.hidden_layers = []
        self.input_layer = []
        self.output_layer = []

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
        self.draw_output_value = False
        self.network = network
        self.rect = None
        self.neuron_pen = QPen()
        self.neuron_brush = QBrush(QColor())

    def get_neuron_size(self):
        s = self.rect.width()
        if self.rect.height() < s:
            s = self.rect.height()
        return s * 0.1

    def paint(self, painter):

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
                neuron_pos[neuron] = (x, y)
                y += chunk_y

            x += chunk_x

        # draw connections
        for layer in layers:
            for neuron in layer:
                x, y = neuron_pos[neuron]
                for i, neuron_input in enumerate(neuron.inputs):
                    w = neuron.weights[i]

                    if w >= 0.0:
                        c = QColor(0, 0, 100 * w)
                    elif w < 0.0:
                        c = QColor(w * -1.0 * 100, 0, 0)

                    painter.setPen(QPen(c))
                    input_x, input_y = neuron_pos[neuron_input]
                    painter.drawLine(self.rect.x() + x, self.rect.y() + y, self.rect.x() + input_x, self.rect.y() + input_y)

        n_size = self.get_neuron_size()
        h_size = n_size / 2
        for n, pos in neuron_pos.items():
            x, y = pos
            o = (n.output + 1.0) / 2.0
            b = QBrush(QColor(o * 255, o * 255, o * 255))
            p = QPen(QColor())
            painter.setPen(p)
            painter.setBrush(b)
            painter.drawEllipse(self.rect.x() + x - h_size, self.rect.y() + y - h_size, n_size, n_size)
            if self.draw_output_value:
                painter.drawText(x, y - 20, str('{:.2f}'.format(n.output)))
