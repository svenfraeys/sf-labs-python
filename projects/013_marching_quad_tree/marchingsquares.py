from PySide2 import QtCore, QtGui


class Cell(object):
    """cell
    """

    def __init__(self, mc, x, y, rect):
        self.rect = rect
        self.mc = mc
        self.x = x
        self.y = y
        self.tl = False
        self.tr = False
        self.bl = False
        self.br = False

        self._topleft = None
        self._topright = None
        self._bottomleft = None
        self._bottomright = None
        self._top = None
        self._left = None
        self._right = None
        self._bottom = None

    def calc_neighbours(self):
        self.calc_bottom()
        self.calc_top()
        self.calc_left()
        self.calc_right()
        self.calc_topleft()
        self.calc_topright()
        self.calc_bottomleft()
        self.calc_bottomright()

    def topleft(self):
        return self._topleft

    def topright(self):
        return self._topright

    def bottomleft(self):
        return self._bottomleft

    def bottomright(self):
        return self._bottomright

    def top(self):
        return self._top

    def bottom(self):
        return self._bottom

    def left(self):
        return self._left

    def right(self):
        return self._right

    def calc_topleft(self):
        y = self.y - 1
        if y < 0:
            return
        x = self.x - 1
        if x < 0:
            return
        self._topleft = self.mc.grid[y][x]

    def calc_topright(self):
        y = self.y - 1
        if y < 0:
            return
        x = self.x + 1
        if x > self.mc.subdiv_x - 1:
            return
        self._topright = self.mc.grid[y][x]

    def calc_bottomleft(self):
        x = self.x - 1
        if x < 0:
            return
        y = self.y + 1
        if y > self.mc.subdiv_y - 1:
            return
        self._bottomleft = self.mc.grid[y][x]

    def calc_bottomright(self):
        y = self.y + 1
        if y > self.mc.subdiv_y - 1:
            return
        x = self.x + 1
        if x > self.mc.subdiv_x - 1:
            return

        self._bottomright = self.mc.grid[y][x]

    def calc_top(self):
        x = self.x
        y = self.y - 1
        if y < 0:
            return None
        self._top = self.mc.grid[y][x]

    def calc_bottom(self):
        x = self.x
        y = self.y + 1
        if y > self.mc.subdiv_y - 1:
            return None
        self._bottom = self.mc.grid[y][x]

    def calc_left(self):
        y = self.y
        x = self.x - 1
        if x < 0:
            return None
        self._left = self.mc.grid[y][x]

    def calc_right(self):
        y = self.y
        x = self.x + 1
        if x > self.mc.subdiv_x - 1:
            return None
        self._right = self.mc.grid[y][x]

    def contains_points(self):
        for p in self.mc.points:
            if self.rect.contains(p.x(), p.y()):
                return True
        return False

    def calculate(self):
        if self.contains_points():
            return

        t = self.top()
        b = self.bottom()
        l = self.left()
        r = self.right()
        tl = self.topleft()
        tr = self.topright()
        bl = self.bottomleft()
        br = self.bottomright()
        self.tl = False
        self.tr = False
        self.bl = False
        self.br = False

        if t and t.contains_points():
            self.tl = True
            self.tr = True
        if l and l.contains_points():
            self.tl = True
            self.bl = True
        if b and b.contains_points():
            self.bl = True
            self.br = True
        if r and r.contains_points():
            self.tr = True
            self.br = True
        if tl and tl.contains_points():
            self.tl = True
        if tr and tr.contains_points():
            self.tr = True
        if br and br.contains_points():
            self.br = True
        if bl and bl.contains_points():
            self.bl = True

    def contour_line(self):
        c = self
        if not c.tl and not c.tr and not c.bl and not c.br:
            return 0
        elif c.bl and not c.br and not c.tl and not c.tr:
            return 1
        elif c.br and not c.bl and not c.tr and not c.tl:
            return 2
        elif c.bl and c.br and not c.tl and not c.tr:
            return 3
        elif c.tr and not c.tl and not c.bl and not c.br:
            return 4
        elif c.bl and c.tr and not c.tl and not c.br:
            return 5
        elif c.tr and c.br and not c.bl and not c.tl:
            return 6
        elif c.bl and c.br and c.tr and not c.tl:
            return 7
        elif c.tl and not c.tr and not c.bl and not c.br:
            return 8
        elif c.tl and c.bl and not c.tr and not c.br:
            return 9
        elif c.tl and c.br and not c.tr and not c.bl:
            return 10
        elif c.tl and c.bl and c.br and not c.tr:
            return 11
        elif c.tr and c.tl and not c.bl and not c.br:
            return 12
        elif c.bl and c.tr and c.tl and not c.br:
            return 13
        elif c.tl and c.tr and c.br and not c.bl:
            return 14
        elif c.tl and c.tr and c.bl and c.br:
            return 15


class MarchingSquares(object):
    """marching squares
    """

    def __init__(self):
        self.rect = QtCore.QRectF()
        self.subdiv_x = 1
        self.subdiv_y = 1
        self.grid = []
        self.points = []

    def calculate_grid(self):
        self.grid = []
        x_step = float(self.rect.width()) / float(self.subdiv_x)
        y_step = float(self.rect.height()) / float(self.subdiv_y)

        for y in range(self.subdiv_y):
            line = []
            self.grid.append(line)

            for x in range(self.subdiv_x):
                c = Cell(self, x, y,
                         QtCore.QRectF(x * x_step, y * y_step, x_step,
                                       y_step))
                line.append(c)

        # calc neighbours
        for y in self.grid:
            for cell in y:
                cell.calc_neighbours()

    def calculate_points(self):
        for y in self.grid:
            for cell in y:
                cell.calculate()


class MarchingCellsPainter(object):
    def __init__(self, painter=None, mc=None):
        self.painter = painter
        self.mc = mc
        self.show_grid = False
        self.show_number = False
        self.show_empty_cells = False

    def style_grid_line(self):
        c = 200
        pen = QtGui.QPen(QtGui.QColor(c, c, c))
        self.painter.setPen(pen)
        brush = QtGui.QBrush()
        self.painter.setBrush(brush)

    def filled(self):
        c = 200
        pen = QtGui.QPen(QtGui.QColor(c, c, c))
        self.painter.setPen(pen)
        brush = QtGui.QBrush(QtGui.QColor(c, c, c))
        self.painter.setBrush(brush)

    def empty(self):
        c = 200
        pen = QtGui.QPen(QtGui.QColor(c, c, c))
        self.painter.setPen(pen)
        brush = QtGui.QBrush()
        self.painter.setBrush(brush)

    def set_blob_style(self):
        c = QtGui.QColor(20, 100, 220)
        p = QtGui.QPen(c)
        p.setWidth(3)
        self.painter.setPen(p)
        self.painter.setBrush(QtGui.QBrush())

    def paint_cell_point(self, x, y, w, h, filled):
        if filled:
            self.filled()
            self.painter.drawRect(x, y, w, h)
        else:
            if self.show_empty_cells:
                self.empty()
                self.painter.drawRect(x, y, w, h)

    def paint_line(self, p1, p2):
        pass
        self.painter.drawLine(p1, p2)

    def paint_cell_line(self, cell):
        center = cell.rect.center()
        w = cell.rect.width()
        h = cell.rect.height()
        w_half = cell.rect.width() / 2.0
        h_half = cell.rect.height() / 2.0
        x = cell.rect.x()
        y = cell.rect.y()
        cr = center + QtCore.QPointF(w_half, 0)
        cl = center + QtCore.QPointF(-w_half, 0)
        ct = center + QtCore.QPointF(0, -h_half)
        cb = center + QtCore.QPointF(0, h_half)

        # cr = QtCore.QPointF(x + w, y + h_half)
        # cl = QtCore.QPointF(x + w_half, y)
        # ct = QtCore.QPointF(x, y + h_half)
        # cb = QtCore.QPointF(x + h_half, y + h)
        # self.painter.drawLine(cl, cb)

        contour_case = cell.contour_line()
        if contour_case == 0:
            return
        elif contour_case == 1:
            self.paint_line(cl, cb)
        elif contour_case == 2:
            self.paint_line(cr, cb)
        elif contour_case == 3:
            self.paint_line(cl, cr)
        elif contour_case == 4:
            self.paint_line(ct, cr)
        elif contour_case == 5:
            self.paint_line(cl, ct)
            self.paint_line(cb, cr)
        elif contour_case == 6:
            self.paint_line(cb, ct)
        elif contour_case == 7:
            self.paint_line(cl, ct)
        elif contour_case == 8:
            self.paint_line(cl, ct)
        elif contour_case == 9:
            self.paint_line(cb, ct)
        elif contour_case == 10:
            self.paint_line(cl, cb)
            self.paint_line(ct, cr)
        elif contour_case == 11:
            self.paint_line(ct, cr)
        elif contour_case == 12:
            self.paint_line(cl, cr)
        elif contour_case == 13:
            self.paint_line(cb, cr)
        elif contour_case == 14:
            self.paint_line(cl, cb)
        elif contour_case == 15:
            return

    def paint_cell(self, cell):
        if self.show_grid:
            self.style_grid_line()
            self.painter.drawRect(cell.rect)

            tl = cell.rect.topLeft()
            tr = cell.rect.topRight()
            bl = cell.rect.bottomLeft()
            br = cell.rect.bottomRight()
            s = cell.rect.width() / 5
            self.style_grid_line()
            self.paint_cell_point(tl.x(), tl.y(), s, s, cell.tl)
            self.paint_cell_point(tr.x(), tr.y(), -s, s, cell.tr)
            self.paint_cell_point(bl.x(), bl.y(), s, -s, cell.bl)
            self.paint_cell_point(br.x(), br.y(), -s, -s, cell.br)

            if self.show_number:
                contour_number = cell.contour_line()
                self.painter.drawText(cell.rect.center(), str(contour_number))

        self.set_blob_style()
        self.paint_cell_line(cell)
        self.empty()

    def paint_grid(self):
        """paint the grid of the marching squares
        """
        if not self.mc:
            return

        for row in self.mc.grid:
            for cell in row:
                self.paint_cell(cell)
