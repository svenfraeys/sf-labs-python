import random

import math
from PySide2 import QtWidgets
from PySide2.QtCore import QRect
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QApplication
from sfwidgets.charts import LineChart


class GraphsDemoWidget(QtWidgets.QWidget):
    def __init__(self):
        super(GraphsDemoWidget, self).__init__()

        data = [math.cos(_ * 0.1) for _ in range(120)]

        self.line_graph = LineChart(data)
        self.line_graph.rect = QRect(20, 20, 200, 100)

    def mousePressEvent(self, event):
        data = [random.random() for _ in range(10)]
        self.line_graph.data = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.line_graph.paint(painter)

    def resizeEvent(self, event):
        pass
        # self.line_graph.rect = self.rect()


app = QApplication([])
w = GraphsDemoWidget()
w.show()
app.exec_()
