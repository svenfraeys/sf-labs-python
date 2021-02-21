"""charts
"""
import math
from PySide2.QtCore import QRect
from PySide2.QtGui import QColor


class LineChart(object):
    """
    linegraph
    """

    def __init__(self, data=None):
        if data is None:
            data = []
        self.data = data
        self.rect = QRect()
        self.color = QColor(0, 0, 200)
        self.background_color = QColor(255, 255, 255)

    def paint(self, painter):
        painter.fillRect(self.rect, self.background_color)
        if not self.data:
            return
        min_data = float(min(self.data))
        max_data = float(max(self.data))

        max_data += max_data / 2
        min_data -= min_data / 2
        diff = (max_data - min_data)

        multplier = self.rect.height() / diff
        w_multiplier = self.rect.width() / float(len(self.data))

        for i, d in enumerate(self.data):
            y = self.rect.height() - ((d - min_data) * multplier)
            x = i * w_multiplier
            draw_width = w_multiplier if w_multiplier > 1 else 1
            painter.fillRect(int(self.rect.x() + x), int(self.rect.y() + y),
                             int(math.ceil(draw_width)),
                             int(math.ceil(self.rect.height() - y)),
                             self.color)
