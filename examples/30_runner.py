"""
base Runner
"""
import random

import math
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import QRect

from sfwidgets.neuralnetwork import Network, NetworkPainter
from sfwidgets.runner import Runner
from sfwidgets.runner import RunnerPainter


class DNA:
    def __init__(self):
        self.value = []
        self.fitness = 0

    def cross_over(self, dna):
        average_list = []
        for i, v in enumerate(self.value):
            average_list.append((v + dna.value[i]) / 2.0)

        if False:
            midpoint = len(self.value) / 2
            midpoint = int(midpoint)
            part_a = self.value[:midpoint]
            part_b = dna.value[midpoint:]
            value = part_a + part_b

        dna = DNA()
        dna.value = average_list
        dna.fitness = 0
        return dna


class PhenoType:
    def __init__(self, dna):
        self.dna = dna
        self.network = Network(3, [10, 10, 10], 3)
        self.network.import_weights(dna.value)
        self.runner = Runner()
        self.is_running = False
        self.fitness = 0

    def tick_neural_network(self):
        data = [
            self.runner.player.pos.x(),
            self.runner.player.pos.y(),
            self.runner.distance_next_obstacle()
        ]
        self.network.respond(data)
        outputs = [n.output for n in self.network.output_layer]
        if not outputs:
            return
        i = outputs.index(max(outputs))

        if i == 0:
            return
        elif i == 1:
            self.runner.player_up()
        elif i == 2:
            self.runner.player_down()

            # @property
            # def fitness(self):
            # return self.runner.total_ticks_alive

    def start(self):
        self.is_running = True
        self.runner.reset()

    def tick(self):
        self.runner.tick()
        self.tick_neural_network()
        self.is_running = not self.runner.stopped
        if not self.runner.stopped:
            self.fitness += math.floor(
                (1.0 - abs(self.runner.player.pos.y()))) * 20


class GeneticAlgorithm:
    GENERATING_FITNESS = 'generating_fitness'
    MUTATE = 'mutate'
    START = 'start'
    TRANSFER_FITNESS = 'transfer_fitness'
    CROSS_OVER = 'cross_over'
    STOP = 'stop'

    def __init__(self):
        self.structure_network = Network(3, [10, 10, 10], 3)
        self.total_population = 20
        self.population = []
        self.mutation = 0.01
        self.generation = 0
        self.pauzed = False
        self.state = self.START
        self.pheno_types = []

    def setup(self):
        self.structure_network.setup()
        self.generate_population()
        self.generation = 0

    def generate_population(self):
        # make the population
        self.population = []
        for i in range(self.total_population):
            w = self.structure_network.clone().export_weights()
            dna = DNA()
            dna.value = w
            self.population.append(dna)

    def generate_pheno_types(self):
        self.pheno_types = []
        for i in range(self.total_population):
            dna = self.population[i]
            pheno_type = PhenoType(dna)
            self.pheno_types.append(pheno_type)
            pheno_type.start()

    def get_fittest_dna(self):
        fittest_dna = sorted(self.population, key=lambda x: x.fitness)
        return fittest_dna[-1]

    def do_cross_over(self):
        pheno_types = sorted(self.pheno_types, key=lambda x: x.fitness,
                             reverse=True)
        total_fitness = sum([p.fitness for p in self.pheno_types])

        def pick_pheno_type():
            target = random.random()
            count = 0.0

            for pheno_type in pheno_types:
                if pheno_type.fitness == 0:
                    continue

                fitness_normal = float(pheno_type.fitness) / float(
                    total_fitness)

                if target <= count + fitness_normal:
                    return pheno_type

                count += fitness_normal

        new_population = []
        for i in range(self.total_population - 1):
            pheno_type_a = pick_pheno_type()
            pheno_type_b = pick_pheno_type()
            pheno_type_new = pheno_type_a.dna.cross_over(pheno_type_b.dna)
            new_population.append(pheno_type_new)

        nn = self.structure_network.clone()
        dna = DNA()
        w = nn.export_weights()
        weights = []
        for _ in range(len(w)):
            weights.append(-1 + random.random() * 2)

        dna.value = weights
        new_population.append(dna)

        self.population = new_population
        self.generation += 1
        print(self.generation)

    def tick(self):
        if self.state == self.START:
            self.generate_pheno_types()
            self.state = self.GENERATING_FITNESS

        if self.state == self.GENERATING_FITNESS:

            all_done = True
            for pheno_type in self.pheno_types:
                pheno_type.tick()
                if pheno_type.is_running:
                    all_done = False
            if all_done:
                self.state = self.TRANSFER_FITNESS
        if self.state == self.TRANSFER_FITNESS:
            for pheno_type in self.pheno_types:
                pheno_type.dna.fitness = pheno_type.fitness
            if self.generation < 2000:
                self.state = self.CROSS_OVER
            else:
                self.state = self.STOP

        if self.state == self.CROSS_OVER:
            self.do_cross_over()
            self.state = self.START

        if self.state == self.STOP:
            pass


class RunnerTrainer:
    """trainer for runner
    """

    def __init__(self, network, runner):
        self.network = network
        self.runner = runner

    def tick_neural_network(self):
        data = [
            self.runner.player.pos.x(),
            self.runner.player.pos.y(),
            self.runner.distance_next_obstacle()
        ]
        self.network.respond(data)
        outputs = [n.output for n in self.network.output_layer]
        i = outputs.index(max(outputs))

        if i == 0:
            return
        elif i == 1:
            self.runner.player_up()
        elif i == 2:
            self.runner.player_down()

    def tick(self):
        self.runner.tick()
        self.tick_neural_network()


class RunnerAI:
    def __init__(self, network):
        """give the network to train
        """
        self.network = network
        self.total_population = 20
        self.runner_games = []
        self.trainers = []
        self.best_neural_network = network
        self.is_training = False
        self.on_training_finished = None

    def train(self):
        self.is_training = True

    def setup(self):
        for i in range(self.total_population):
            r = Runner()
            t = RunnerTrainer(self.network.clone(), r)
            self.runner_games.append(r)
            self.trainers.append(t)

    def all_games_stopped(self):
        for game in self.runner_games:
            if not game.stopped:
                return False
        return True

    def tick(self):
        if not self.is_training:
            return

        for g in self.runner_games:
            g.tick()

        if not self.all_games_stopped():
            return

        fitness = [g.total_ticks_alive for g in self.runner_games]
        i = fitness.index(max(fitness))
        self.best_neural_network = self.trainers[i].network
        self.is_training = False
        if self.on_training_finished:
            self.on_training_finished()


class RunnerDemoWidget(QtWidgets.QWidget):
    """
    Runner
    """

    def __init__(self):
        super(RunnerDemoWidget, self).__init__()
        self.setCursor(QtCore.Qt.BlankCursor)
        self.setWindowTitle("Runner")
        self.tick_timer = QtCore.QTimer()
        self.tick_timer.setInterval(10)
        self.tick_timer.timeout.connect(self.tick)
        self.runner = Runner()
        self.runner_painter = RunnerPainter(self.runner, self.rect())

        self.network = Network(3, [10, 10, 10], 3)
        self.runner_ai = RunnerAI(self.network)
        self.runner_ai.on_training_finished = self.training_finished
        self.runner_ai.setup()
        self.network_painter = NetworkPainter(self.network)
        self.network_painter.rect = QRect(0, 0, self.width() / 2,
                                          self.height() / 2)
        self.network.setup()
        self.runner_trainer = RunnerTrainer(self.network, self.runner)
        self.genetic_algorithm = GeneticAlgorithm()
        self.genetic_algorithm.setup()

    def training_finished(self):
        self.network = self.runner_ai.best_neural_network

    def resizeEvent(self, event):
        r = QRect(self.width() / 2, self.height() / 2, self.width() / 2,
                  self.height() / 2)
        self.runner_painter.rect = r
        self.network_painter.rect = QRect(0, 0, self.width() / 2,
                                          self.height() / 2)
        self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter:
            self.network = self.runner_ai.best_neural_network
            self.runner.reset()

        if event.key() == QtCore.Qt.Key_Space:
            fittest_dna = self.genetic_algorithm.get_fittest_dna()
            print(fittest_dna.fitness)
            self.network.import_weights(
                fittest_dna.value)
            # self.network.setup()
            self.runner.reset()
            # self.runner_ai.train()

        if event.key() == QtCore.Qt.Key_Up:
            self.runner.player_up()
            self.update()

        if event.key() == QtCore.Qt.Key_Down:
            self.runner.player_down()
            self.update()

    def showEvent(self, event):
        r = QRect(self.width() / 2, 0, self.width() / 2,
                  self.height() / 2)
        self.runner_painter.rect = r
        self.tick_timer.start()

    def closeEvent(self, event):
        self.tick_timer.stop()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.drawText(100, 100,
                         "Fitness: {}".format(self.runner.total_ticks_alive))
        self.runner_painter.paint(painter)
        self.network_painter.paint(painter)

    def tick(self):
        self.runner_ai.tick()
        self.runner_trainer.tick()
        self.update()
        self.genetic_algorithm.tick()

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = RunnerDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
