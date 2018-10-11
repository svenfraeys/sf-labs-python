"""
base geneticAlgorithm
"""
import random

from PySide2 import QtGui, QtCore, QtWidgets

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
        self.total_population = 1200
        self.target = ''
        self.population = []
        self.mutation = 0.00006
        self.generation = 0
        self.found = False

    def generate_random_char(self):
        return chr(random.randint(97, 122))
        return chr(random.randint(32, 122))

    def generate_population(self):
        print("pop")
        new_population = []
        for i in range(self.total_population):
            dna = DNA()
            dna.value = ''
            for _ in range(len(self.target)):
                dna.value += self.generate_random_char()
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
        for _ in self.population:
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
        self.population = new_population
        return

        fitness_chart = []
        for dna in self.population:
            fitness_chart.append(float(dna.fitness) / float(total_fitness))

        def get_dna():
            for j, fitness_i in enumerate(fitness_chart):
                if fitness_i == 0.0:
                    continue

                if random.random() <= fitness_i:
                    return self.population[j]

            print('none')
            return None

        new_population = []
        for _ in self.population:
            first_choice = get_dna()
            second_choice = get_dna()
            new_dna = first_choice.cross_over(second_choice)
            new_population.append(new_dna)

            # mutation
            mutated_value = ''
            for c in new_dna.value:
                if random.random() < self.mutation:
                    mutated_value += self.generate_random_char()
                else:
                    mutated_value += c
            new_dna.value = mutated_value

        self.population = new_population

    def tick(self):
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
        self.genetic_algorithm = GeneticAlgorithm()
        self.genetic_algorithm.target = 'to be or not to be'
        self.genetic_algorithm.target = 'tobeornottobe'
        self.setWindowTitle("GeneticAlgorithm")
        self.tick_timer = QtCore.QTimer()
        self.tick_timer.setInterval(1)
        self.tick_timer.timeout.connect(self.tick)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            self.genetic_algorithm.generate_population()
            self.tick()

        if event.key() == QtCore.Qt.Key_Up:
            self.genetic_algorithm.mutation *= 2.0
            self.genetic_algorithm.generate_population()

        if event.key() == QtCore.Qt.Key_Down:
            self.genetic_algorithm.mutation /= 2.0
            self.genetic_algorithm.generate_population()

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def showEvent(self, event):
        self.genetic_algorithm.generate_population()
        self.genetic_algorithm.generate_fitness()
        self.tick_timer.start()

    def closeEvent(self, event):
        self.tick_timer.stop()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.drawText(20, 20, self.genetic_algorithm.target)
        if DRAW_POPULATION:
            for i, dna_i in enumerate(self.genetic_algorithm.population):
                txt = '{} - {}'.format(dna_i.value, dna_i.fitness)
                painter.drawText(160, 20 + i * 15, txt)

        fittest_dna = self.genetic_algorithm.get_fittest_dna()

        painter.drawText(20, 40, fittest_dna.value)
        painter.drawText(20, 60, 'Fitness {}'.format(fittest_dna.fitness))
        painter.drawText(20, 80, 'Generation {}'.format(
            self.genetic_algorithm.generation))
        painter.drawText(20, 100, 'Mutation {} %'.format(
            self.genetic_algorithm.mutation * 100.0))

    def tick(self):
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
