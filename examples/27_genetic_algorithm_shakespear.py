"""
base geneticAlgorithm
"""
import random

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import QColor
from PySide2.QtGui import QPen

DRAW_POPULATION = True


class DNA:
    def __init__(self):
        self.value = ''
        self.fitness = 0

    def cross_over(self, dna):
        midpoint = len(self.value) / 2
        midpoint = int(midpoint)
        part_a = self.value[:midpoint]
        part_b = dna.value[midpoint:]
        dna = DNA()
        dna.value = part_a + part_b
        dna.fitness = 0
        return dna


class GeneticAlgorithm:
    def __init__(self):
        self.total_population = 500
        self.target = ''
        self.population = []
        self.mutation = 0.00024
        self.generation = 0
        self.found = False
        self.pauzed = False

    def generate_random_char(self):
        return chr(random.randint(97, 122))

    def generate_dna(self):
        dna = DNA()
        dna.value = ''
        for _ in range(len(self.target)):
            dna.value += self.generate_random_char()
        return dna

    def generate_population(self):
        new_population = []
        for i in range(self.total_population):
            dna = self.generate_dna()
            new_population.append(dna)
        self.population = new_population
        self.generation = 0
        self.found = False

    def generate_fitness(self):
        for dna in self.population:
            dna.fitness = 0
            for i in range(len(self.target)):
                if dna.value[i] == self.target[i]:
                    dna.fitness += 1

    def get_fittest_dna(self):
        sorted_dna = sorted(self.population, key=lambda x: x.fitness)
        return sorted_dna[-1]

    def natural_selection(self):
        total_fitness = 0

        for dna in self.population:
            total_fitness += dna.fitness

        if total_fitness == 0:
            return

        mating_pool = []
        for dna in self.population:
            for _ in range(dna.fitness):
                mating_pool.append(dna)

        new_population = []
        for _ in self.population[:-1]:
            chosen_mate_a = mating_pool[
                random.randint(0, len(mating_pool) - 1)]
            chosen_mate_b = mating_pool[
                random.randint(0, len(mating_pool) - 1)]
            new_dna = chosen_mate_a.cross_over(chosen_mate_b)
            # mutation
            mutated_value = ''
            for c in new_dna.value:
                if random.random() < self.mutation:
                    mutated_value += self.generate_random_char()
                else:
                    mutated_value += c

            new_dna.value = mutated_value
            new_population.append(new_dna)

        dna = self.generate_dna()
        new_population.append(dna)

        self.population = new_population
        return

    def tick(self):
        if self.pauzed:
            return

        if self.found:
            return

        self.generate_fitness()
        self.natural_selection()
        self.generate_fitness()
        if self.get_fittest_dna().value == self.target:
            self.found = True

        self.generation += 1


class GeneticAlgorithmDemoWidget(QtWidgets.QWidget):
    """
    GeneticAlgorithm
    """

    def __init__(self):
        super(GeneticAlgorithmDemoWidget, self).__init__()
        self.words = [
            "zuccini",
            "tripod",
            "unicorn",
            "brugola",
            "watermeloen",
        ]
        self.genetic_algorithm = GeneticAlgorithm()
        self.genetic_algorithm.target = self.words[0]
        self.setWindowTitle("GeneticAlgorithm")
        self.tick_timer = QtCore.QTimer()
        self.tick_timer.setInterval(1)
        self.tick_timer.timeout.connect(self.tick)
        self.ticks_per_tick = 2
        self.setCursor(QtCore.Qt.BlankCursor)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            if self.genetic_algorithm.pauzed:
                self.genetic_algorithm.pauzed = False
                return
            current_index = self.words.index(self.genetic_algorithm.target)
            next_index = current_index + 1
            if next_index >= len(self.words):
                next_index = 0
            self.genetic_algorithm.target = self.words[next_index]

            self.genetic_algorithm.generate_population()
            self.tick()

        if event.key() == QtCore.Qt.Key_Up:
            self.genetic_algorithm.mutation *= 2.0
            self.genetic_algorithm.generate_population()

        if event.key() == QtCore.Qt.Key_Down:
            self.genetic_algorithm.mutation /= 2.0
            self.genetic_algorithm.generate_population()

    def showEvent(self, event):
        self.genetic_algorithm.pauzed = True
        self.genetic_algorithm.generate_population()
        self.genetic_algorithm.generate_fitness()
        self.tick_timer.start()

    def closeEvent(self, event):
        self.tick_timer.stop()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        font = painter.font()
        font.setFamily("Consolas")
        font.setPointSize(12)
        painter.setPen(QPen(QColor(120, 120, 120)))
        if DRAW_POPULATION:
            for i, dna_i in enumerate(sorted(self.genetic_algorithm.population,
                                             key=lambda x: x.fitness,
                                             reverse=True)):
                txt = '{} | {}'.format(dna_i.value, dna_i.fitness)
                painter.drawText(210, 35 + i * 15, txt)
        painter.setPen(QPen(QColor()))
        font.setPointSize(30)
        painter.setFont(font)
        painter.drawText(20, 50, self.genetic_algorithm.target)

        fittest_dna = self.genetic_algorithm.get_fittest_dna()
        progress_normalized = fittest_dna.fitness / float(
            len(self.genetic_algorithm.target))
        c = 20 + progress_normalized * 150.0
        painter.setPen(QPen(QColor(10, c, 10)))
        painter.drawText(20, 100, fittest_dna.value)

        painter.setPen(QPen(QColor(80, 80, 80)))
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(20, 140,
                         'Progress: {:.2f}%'.format(
                             progress_normalized * 100.0))
        painter.drawText(20, 170,
                         'Max Fitness: {}'.format(fittest_dna.fitness))
        painter.drawText(20, 200, 'Generation: {}'.format(
            self.genetic_algorithm.generation))
        painter.drawText(20, 230, 'Mutation: {} %'.format(
            self.genetic_algorithm.mutation * 100.0))
        painter.drawText(20, 260, 'Population: {}'.format(
            self.genetic_algorithm.total_population))

    def tick(self):
        for i in range(self.ticks_per_tick):
            self.genetic_algorithm.tick()
        self.update()

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = GeneticAlgorithmDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
