"""
EvoLisa implementation based on the paper using numpy, PySide, imageio

Evolved Art with Transparent, Overlapping, and Geometric Shapes
https://arxiv.org/pdf/1904.06110.pdf
"""
import random

import imageio
import numpy as np
from PySide2.QtCore import QPoint, QSize, QObject, Signal, QThread
from PySide2.QtGui import QPainter, QPainterPath, Qt, QPixmap, QBrush, QColor, QImage
from PySide2.QtWidgets import QWidget, QApplication

TRIANGLE_SIZE = 10
WIDTH = 250
HEIGHT = 250
POPULATION_SIZE = 60
TOTAL_TRIANGLES = 80
MUTATION_RATE = 0.01
NUM_CHANNELS = 4


def _random_triangle():
    data = []
    for i in range(TRIANGLE_SIZE + 1):
        data.append(random.random())
    return data


def _generate_random_chromosone(amount):
    return np.random.rand(TRIANGLE_SIZE * amount)


def _initialize_population(size, total_triangles):
    population = []
    for i in range(size):
        chromosome = _generate_random_chromosone(total_triangles)
        population.append(chromosome)
    return population


def _calculate_fitness_phenotypes(chromosone_phenotype, target_phenotype):
    chromosone_phenotype = chromosone_phenotype / 255.0
    sub = np.subtract(target_phenotype, chromosone_phenotype)
    diff = np.abs(sub)
    diff = 1.0 - diff
    fitness = np.sum(diff) / (WIDTH * HEIGHT * NUM_CHANNELS)
    return fitness


def _calculate_fitness(chromosone, total_triangles, size, target_image):
    arr = _chromosone_to_phenotype(chromosone, size, total_triangles)
    fitness = _calculate_fitness_phenotypes(arr, target_image)
    return fitness


def _read_target_phenotype():
    return imageio.imread('evolisa.png')


def _calculate_population_fitness(population_size, population, total_triangles, size, target_image):
    results = []
    for i in range(population_size):
        chromosome = population[i]
        fitness = _calculate_fitness(chromosome, total_triangles, size, target_image)
        results.append(fitness)
    return results


def _create_brush(r, g, b, a):
    brush = QBrush()
    brush.setStyle(Qt.SolidPattern)
    color = QColor()
    color.setRed(r)
    color.setGreen(g)
    color.setBlue(b)
    color.setAlpha(a)
    brush.setColor(color)
    return brush


def _set_brush(brush, r, g, b, a):
    color = QColor()
    color.setRed(r)
    color.setGreen(g)
    color.setBlue(b)
    color.setAlpha(a)
    brush.setColor(color)


def _draw_triangle(brush, painter_path, painter, data, offset=0, size=(250, 250)):
    offset = offset * TRIANGLE_SIZE
    width, height = size
    r = int(data[offset + 6] * 255.0)
    g = int(data[offset + 7] * 255.0)
    b = int(data[offset + 8] * 255.0)
    a = int(data[offset + 9] * 255.0)

    _set_brush(brush, r, g, b, a)
    painter.setBrush(brush)

    painter_path.moveTo(data[offset + 0] * width, data[offset + 1] * height)
    painter_path.lineTo(data[offset + 2] * width, data[offset + 3] * height)
    painter_path.lineTo(data[offset + 4] * width, data[offset + 5] * height)
    painter.drawPath(painter_path)


def _draw_chromosone(painter, chromosone, total_triangles, size=(250, 250)):
    brush = _create_brush(0, 0, 0, 0)
    painter_path = QPainterPath()
    for i in range(total_triangles):
        _draw_triangle(brush, painter_path, painter, chromosone, offset=i, size=size)
        painter_path.clear()


def _fittest_population_indices(size, population_fitness):
    results = []
    results_indices = []
    for i in range(size):
        fitness = population_fitness[i]
        if not results:
            results.append(fitness)
            results_indices.append(i)
            continue
        for k, j in enumerate(results):
            if fitness <= j:
                continue
            else:
                results.insert(k, fitness)
                results_indices.insert(k, i)
                break
        else:
            results.append(fitness)
            results_indices.append(i)
    return results_indices


def _chromosone_to_pixmap(chromosone, total_triangles, size):
    width, height = size
    pixmap = QPixmap(width, height)
    painter = QPainter(pixmap)
    painter.fillRect(0, 0, width, height, Qt.gray)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(Qt.transparent)
    _draw_chromosone(painter, chromosone, total_triangles, size=size)
    return pixmap


def _selection(population, fittest_indices, population_size, fitness_values):
    fittest_index = fittest_indices[0]
    highest_fitness = max(fitness_values)
    indices = [
        fittest_index
    ]
    while len(indices) < population_size / 2:
        for i in fittest_indices[:int(population_size / 2)]:
            if random.random() < fitness_values[i] / highest_fitness:
                indices.append(i)

    return indices


def _cross_over(partner_a, partner_b):
    partner_a_half = np.split(partner_a, 2)[0]
    partner_b_half = np.split(partner_b, 2)[-1]
    new_chromosone = np.concatenate((partner_a_half, partner_b_half))
    new_chromosone = np.copy(new_chromosone)
    return new_chromosone


def _pick_candicate(population, fitness_values, selected_indices):
    max_fitness = max(fitness_values)
    min_fitness = min(fitness_values)
    cap = (max_fitness - min_fitness)
    while True:
        for i in selected_indices:
            chromosone = population[i]
            fitness = fitness_values[i]
            fitness_rank = (fitness - min_fitness) / cap
            chance_of_selection = fitness_rank * 0.4
            if random.random() < chance_of_selection:
                return chromosone


def _generate_population(population, selected_indices, population_size, mutation_rate, total_triangles, fitness_values):
    new_population = []

    for i in selected_indices:
        new_population.append(np.copy(population[i]))
    total_new_random = 2
    while len(new_population) < (population_size - total_new_random):
        partner_a = _pick_candicate(population, fitness_values, selected_indices)
        partner_b = _pick_candicate(population, fitness_values, selected_indices)

        new_chromosone = _cross_over(partner_a, partner_b)
        new_population.append(new_chromosone)
    for i in range(total_new_random):
        new_population.append(_generate_random_chromosone(total_triangles))
    _mutate_population(new_population, mutation_rate)

    return new_population


def _mutate_population(population, mutation_rate):
    for j, chromosone in enumerate(population):
        if j == 0:
            continue
        for i, gene in enumerate(chromosone):
            if random.random() < mutation_rate:
                chromosone[i] = random.random()


def _chromosone_to_phenotype(chromosone, size, total_triangles):
    width, height = size
    pixmap = _chromosone_to_pixmap(chromosone, total_triangles, (width, height))
    image = pixmap.toImage()
    image = image.rgbSwapped()
    ptr = image.constBits()

    data = np.array(ptr)
    arr = data.reshape((width, height, NUM_CHANNELS))

    return arr


class EvoLisaWorker(QObject):
    finished = Signal()
    progress = Signal(object, int)

    def __init__(self):
        super(EvoLisaWorker, self).__init__()
        self.size = (WIDTH, HEIGHT)
        self.__population_size = POPULATION_SIZE
        self.__total_triangles = TOTAL_TRIANGLES
        self.__mutation_rate = MUTATION_RATE

        self.__target_image = _read_target_phenotype()
        self.__target_phenotype = self.__target_image / 255.0

        population = _initialize_population(self.__population_size, self.__total_triangles)
        self.__population = population
        self.__generation = 0
        self.__width = WIDTH
        self.__height = HEIGHT
        self.__is_running = False

    def population_size(self):
        return self.__population_size

    def width(self):
        return self.__width

    def height(self):
        return self.__height

    def total_triangles(self):
        return self.__total_triangles

    def stop(self):
        self.__is_running = False

    def run(self):
        self.__is_running = True
        while self.__is_running:
            size = (self.__width, self.__height)
            population_size = self.__population_size
            total_triangles = self.__total_triangles
            population = self.__population

            target_image = self.__target_phenotype

            population_fitness = _calculate_population_fitness(population_size, population, total_triangles, size,
                                                               target_image)

            fittsest_indices = _fittest_population_indices(population_size, population_fitness)
            fittest_index = fittsest_indices[0]

            fitest_chromosone = population[fittest_index]

            self.progress.emit(np.copy(fitest_chromosone), self.__generation)
            selected_indices = _selection(population, fittsest_indices, population_size, population_fitness)
            new_population = _generate_population(population, selected_indices, population_size, self.__mutation_rate,
                                                  total_triangles, population_fitness)

            # self.update()
            self.__population = new_population
            self.__generation += 1


class EvoLisaWidget(QWidget):
    def __init__(self):
        super(EvoLisaWidget, self).__init__()
        self.__image = QImage('evolisa.png')
        self.__thread = QThread()
        self.__worker = EvoLisaWorker()
        self.__worker.moveToThread(self.__thread)
        self.__thread.started.connect(self.__worker.run)
        self.__thread.finished.connect(self.__thread.quit)
        self.__worker.progress.connect(self.__report_progress)

        self.__pixmap = None

        self.setWindowTitle('EvoLisa')

    def __report_progress(self, chromosone, generation):
        size = 250, 250
        total_triangles = self.__worker.total_triangles()
        self.__pixmap = _chromosone_to_pixmap(chromosone, total_triangles, size)
        self.setWindowTitle('EvoLisa g={}'.format(generation))

        self.update()

    def mousePressEvent(self, event):
        event.accept()

    def showEvent(self, event):
        self.__thread.start()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.drawPixmap(QPoint(), self.__pixmap)
        painter.drawImage(QPoint(250, 0), self.__image)

    def sizeHint(self):
        return QSize(500, 250)

    def closeEvent(self, event):
        self.__worker.stop()


def main():
    app = QApplication([])
    widget = EvoLisaWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
