"""
"""
import random

from PySide2 import QtCore

from PySide2.QtCore import QRect
from PySide2.QtCore import QSize
from PySide2.QtCore import QTimer
from PySide2.QtGui import QPainter
from PySide2.QtGui import QPen
from PySide2.QtWidgets import QWidget, QApplication

from sfwidgets.neuralnetwork import Network, NetworkPainter
from sfwidgets.snake import SnakeGame

TOTAL_POPULATION = 30
MUTATION_RATE = 0.02
START_GENERATION = 0
NO_SCORE_CHANGE_MAX_TICKS = 200

FOOD_POSITIONS = [
    (6, 6),
    (2, 15),
    (17, 3)
]


def make_snake_network(snake):
    n = Network(snake.grid.height * snake.grid.width, [7], 5)
    return n


def make_snake_game():
    snake_game = SnakeGame()
    snake_game.deterministic_food = True
    snake_game.food_positions = list(FOOD_POSITIONS)
    snake_game.setup()
    return snake_game


class SnakeDNA(object):
    def __init__(self, value):
        self.value = value

    def crossover(self, dna):
        if True:
            midpoint = random.randint(0, len(self.value))
            midpoint = int(midpoint)
            part_1_a = self.value[:midpoint]
            part_1_b = dna.value[midpoint:]

            part_2_a = dna.value[:midpoint]
            part_2_b = self.value[midpoint:]

            value_1 = part_1_a + part_1_b
            value_2 = part_2_a + part_2_b

        else:
            average_list = []
            for i, v in enumerate(self.value):
                average_list.append((v + dna.value[i]) / 2.0)
            value = average_list
        dna_1 = SnakeDNA(value_1)
        dna_1.fitness = 0
        dna_2 = SnakeDNA(value_2)
        dna_2.fitness = 0
        return dna_1, dna_2

    def mutate(self, mutation_rate):
        new_value = []
        for v in self.value:
            if random.random() < mutation_rate:
                v = -1 + random.random() * 2
                new_value.append(v)
            else:
                new_value.append(v)

        self.value = new_value


class SnakePhenotype(object):
    """snake phenotype
    """

    @staticmethod
    def apply_network_decision(network, snake):
        outputs = [n.output for n in network.output_layer]
        strongest_index = outputs.index(max(outputs))
        if snake.game_over:
            return

        if strongest_index == 0:
            snake.key_pressed(QtCore.Qt.Key_Left)
        if strongest_index == 1:
            snake.key_pressed(QtCore.Qt.Key_Up)
        if strongest_index == 2:
            snake.key_pressed(QtCore.Qt.Key_Right)
        if strongest_index == 3:
            snake.key_pressed(QtCore.Qt.Key_Down)
        if strongest_index == 4:
            pass

    @staticmethod
    def get_network_response(snake):
        inputs = []
        for y in range(snake.grid.height):
            for x in range(snake.grid.width):
                value = 0.0
                if snake.snake.x == x and snake.snake.y == y:
                    value = 1.0
                for body in snake.bodies:
                    if body.x == x and body.y == y:
                        value = 0.5
                if snake.food.x == x and snake.food.y == y:
                    value = -1.0

                inputs.append(value)

        return inputs

    def __init__(self, dna):
        self.dna = dna
        self.snake = make_snake_game()
        self.network = make_snake_network(self.snake)
        self.network.setup()
        self.network.import_weights(dna.value)
        self.is_finished = False
        self.last_score = 0
        self.fitness = 0
        self.score_check_max_ticks = NO_SCORE_CHANGE_MAX_TICKS
        self.score_check_ticks = 0
        self.has_won = True
        self.snake_tick_count = 0

    def get_network_inputs(self):
        inputs = []
        for y in self.snake.grid.height:
            for x in self.snake.grid.width:
                value = 0.0
                if self.snake.snake.x == x and self.snake.snake.y == y:
                    value = 1.0
                for body in self.snake.bodies:
                    if body.x == x and body.y == y:
                        value = 0.5
                if self.snake.food.x == x and self.snake.food.y == y:
                    value = -1.0

                inputs.append(value)

        return inputs

    def tick(self):
        if self.is_finished:
            return

        self.snake.tick()
        self.snake_tick_count += 1
        response = SnakePhenotype.get_network_response(self.snake)
        self.network.respond(response)
        SnakePhenotype.apply_network_decision(self.network, self.snake)
        self.is_finished = self.snake.game_over
        self.has_won = self.snake.game_won
        if self.has_won:
            self.is_finished = True

        self.score_check_ticks += 1
        if self.score_check_ticks > self.score_check_max_ticks:
            self.score_check_ticks = 0
            if self.last_score == self.snake.score:
                self.is_finished = True
            else:
                self.last_score = self.snake.score

        self.fitness += 1

        if self.is_finished:
            # if we die power up the fitness
            score_fitness = (self.snake.score + 1 * 100.0) * (self.snake.score + 1 * 100.0)
            self.fitness = self.snake_tick_count + score_fitness
            self.fitness *= self.fitness / 1000.0

class SnakeGenetic(object):
    START = 'start'
    CREATE_PHENOTYPES = 'create_phenotypes'
    TICK_PHENOTYPES = 'tick_phenotypes'
    CROSSOVER = 'crossover'
    MUTATE = 'mutate'
    STORE_BEST_PHENOTYPE = 'store best phenotype'
    CHECK_WINNERS = 'check_winners'
    STOP = 'stop'

    def __init__(self):
        self.generation = 0
        self.total_population = TOTAL_POPULATION
        self.population = []
        self.phenotypes = []
        self.state = self.START
        self.best_phenotype = None
        self.generation_incremented_func = None
        self.winners_found_func = None
        self.winning_phenotypes = []

    def create_penhotypes(self):
        self.phenotypes = []
        for dna in self.population:
            phenotype = SnakePhenotype(dna)
            self.phenotypes.append(phenotype)

    def get_best_phenotype(self):
        return self.best_phenotype

    def setup(self):
        self.population = []

        # setup
        for i in range(self.total_population):
            n = make_snake_network(make_snake_game())
            n.setup()

            dna = SnakeDNA(n.export_weights())
            self.population.append(dna)

    def tick_phenotypes(self):
        for phenotype in self.phenotypes:
            phenotype.tick()

    def crossover(self):
        total_fitness = sum([p.fitness for p in self.phenotypes])

        def pick_pheno_type():
            target = random.random()
            count = 0.0

            for pheno_type in self.phenotypes:
                if pheno_type.fitness == 0:
                    continue

                fitness_normal = float(pheno_type.fitness) / float(
                    total_fitness)

                if target <= count + fitness_normal:
                    return pheno_type

                count += fitness_normal

        # generate the new population
        population = []
        for i in range(self.total_population / 2):
            phenotype_a = pick_pheno_type()
            phenotype_b = pick_pheno_type()
            new_dna_1, new_dna_2 = phenotype_a.dna.crossover(phenotype_b.dna)
            population.append(new_dna_1)
            population.append(new_dna_2)

        self.population = population
        self.generation += 1

        if self.generation_incremented_func:
            self.generation_incremented_func()

    def store_best_phenotype(self):
        fitness_list = [p.fitness for p in self.phenotypes]
        print(sum(fitness_list))

        self.best_phenotype = self.phenotypes[
            fitness_list.index(max(fitness_list))]

    def check_winners(self):
        winning_phenotypes = [p for p in self.phenotypes if p.has_won]
        if winning_phenotypes:
            self.winning_phenotypes = winning_phenotypes
            if self.winners_found_func:
                self.winners_found_func()
            return True
        else:
            return False

    def mutate(self):
        for dna in self.population:
            dna.mutate(MUTATION_RATE)

    def tick(self):
        if self.state == self.STOP:
            pass
        elif self.state == self.START:
            self.state = self.CREATE_PHENOTYPES
        elif self.state == self.CREATE_PHENOTYPES:
            self.create_penhotypes()
            self.state = self.TICK_PHENOTYPES
        elif self.state == self.TICK_PHENOTYPES:
            self.tick_phenotypes()
            if all([n.is_finished for n in self.phenotypes]):
                self.state = self.STORE_BEST_PHENOTYPE
        elif self.state == self.STORE_BEST_PHENOTYPE:
            self.store_best_phenotype()
            self.state = self.CHECK_WINNERS
        elif self.state == self.CHECK_WINNERS:
            if self.check_winners():
                self.state = self.STOP
            else:
                self.state = self.CROSSOVER
        elif self.state == self.CROSSOVER:
            self.crossover()
            self.state = self.MUTATE
        elif self.state == self.MUTATE:
            self.mutate()
            self.state = self.CREATE_PHENOTYPES


class SnakeWidget(QWidget):
    def __init__(self):
        super(SnakeWidget, self).__init__()
        self.snake = make_snake_game()
        self.setCursor(QtCore.Qt.BlankCursor)

        self.snakegenetic = SnakeGenetic()
        self.snakegenetic.setup()
        self.snakegenetic.generation_incremented_func = self.generation_incremented
        self.snakegenetic.winners_found_func = self.winners_found

        self.network = make_snake_network(self.snake)
        self.network.setup()
        self.network_painter = NetworkPainter(self.network)

        self.tick_timer = QTimer()
        self.tick_timer.timeout.connect(self.tick)
        self.tick_timer.setInterval(100)

        self.ai_timer = QTimer()
        self.ai_timer.timeout.connect(self.tick_ai)
        self.ai_timer.setInterval(1)

        prev_generation = self.snakegenetic.generation
        while self.snakegenetic.generation < START_GENERATION:
            if self.snakegenetic.winning_phenotypes:
                print("found winning")
                break
            self.snakegenetic.tick()
            if self.snakegenetic.generation != prev_generation:
                print(self.snakegenetic.generation)
                prev_generation = self.snakegenetic.generation

        self.tick_timer.start()
        self.ai_timer.start()

    def tick_ai(self):
        self.snakegenetic.tick()

    def tick(self):

        self.snake.tick()
        response = SnakePhenotype.get_network_response(self.snake)
        self.network.respond(response)
        SnakePhenotype.apply_network_decision(self.network, self.snake)

        self.update()

    def showEvent(self, event):
        r = QRect(0, 0, self.width() / 2, self.height() / 2)
        self.network_painter.rect = r
        self.snake.rect = self.rect()
        self.snake.width = self.width()
        self.snake.height = self.height()
        self.update()

    def sizeHint(self):
        return QSize(300, 300)

    def paintEvent(self, event):
        painter = QPainter(self)
        self.snake.paint(painter)
        self.network_painter.paint(painter)
        painter.setPen(QPen())
        painter.drawText(170, 20, 'state: {}'.format(self.snakegenetic.state))
        painter.drawText(170, 40,
                         'generation: {}'.format(self.snakegenetic.generation))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            self.winners_found()
            return
            phenotype = self.snakegenetic.get_best_phenotype()
            if not phenotype:
                return
            dna = phenotype.dna
            self.network.import_weights(dna.value)
            self.snake.reset()

    def make_snake_game(self):
        snake = make_snake_game()
        self.snake = snake
        self.snake.rect = self.rect()
        self.snake.width = self.width()
        self.snake.height = self.height()

    def winners_found(self):
        self.make_snake_game()
        print("winner found")
        print(len(self.snakegenetic.winning_phenotypes))
        i = random.randint(0, len(self.snakegenetic.winning_phenotypes) - 1)
        print(i)
        print("dna is")

        dna = self.snakegenetic.winning_phenotypes[i].dna
        print(dna.value)
        self.network.import_weights(dna.value)
        self.snake.reset()

    def generation_incremented(self):
        self.make_snake_game()
        dna = self.snakegenetic.get_best_phenotype().dna
        self.network.import_weights(dna.value)
        self.snake.reset()


def main():
    app = QApplication([])
    w = SnakeWidget()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
