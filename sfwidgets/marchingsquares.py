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

    def topleft(self):
        y = self.y - 1
        if y < 0:
            return None
        x = self.x - 1
        if x < 0:
            return None
        return self.mc.grid[y][x]

    def topright(self):
        y = self.y - 1
        if y < 0:
            return None
        x = self.x + 1
        if x > self.mc.subdiv_x - 1:
            return None
        return self.mc.grid[y][x]

    def bottomleft(self):
        x = self.x - 1
        if x < 0:
            return None
        y = self.y + 1
        if y > self.mc.subdiv_y - 1:
            return None
        return self.mc.grid[y][x]

    def bottomright(self):
        y = self.y + 1
        if y > self.mc.subdiv_y - 1:
            return None
        x = self.x + 1
        if x > self.mc.subdiv_x - 1:
            return None
        return self.mc.grid[y][x]

    def top(self):
        x = self.x
        y = self.y - 1
        if y < 0:
            return None
        return self.mc.grid[y][x]

    def bottom(self):
        x = self.x
        y = self.y + 1
        if y > self.mc.subdiv_y - 1:
            return None
        return self.mc.grid[y][x]

    def left(self):
        y = self.y
        x = self.x - 1
        if x < 0:
            return None
        return self.mc.grid[y][x]

    def right(self):
        y = self.y
        x = self.x + 1
        if x > self.mc.subdiv_x - 1:
            return None
        return self.mc.grid[y][x]

    def contains_points(self):
        for p in self.mc.points:
            if self.rect.contains(p):
                return True
        return False

    def calculate(self):
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

        if self.contains_points():
            return

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
        x_step = self.rect.width() / self.subdiv_x
        y_step = self.rect.height() / self.subdiv_y
        for y in range(self.subdiv_y):
            line = []
            self.grid.append(line)

            for x in range(self.subdiv_x):
                c = Cell(self, x, y,
                         QtCore.QRectF(x * x_step, y * y_step, x_step,
                                       y_step))
                line.append(c)

    def calculate_points(self):
        for y in self.grid:
            for cell in y:
                cell.calculate()


class MarchingCellsPainter(object):
    def __init__(self, painter=None, mc=None):
        self.painter = painter
        self.mc = mc
        self.show_grid = False

    def style_grid_line(self):
        pen = QtGui.QPen(QtGui.QColor(100, 100, 100))
        self.painter.setPen(pen)
        brush = QtGui.QBrush()
        self.painter.setBrush(brush)

    def filled(self):
        pen = QtGui.QPen(QtGui.QColor(100, 100, 100))
        self.painter.setPen(pen)
        brush = QtGui.QBrush(QtGui.QColor(100, 100, 100))
        self.painter.setBrush(brush)

    def empty(self):
        pen = QtGui.QPen(QtGui.QColor(100, 100, 100))
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
        else:
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
            s = 3
            self.style_grid_line()
            self.paint_cell_point(tl.x(), tl.y(), s, s, cell.tl)
            self.paint_cell_point(tr.x(), tr.y(), -s, s, cell.tr)
            self.paint_cell_point(bl.x(), bl.y(), s, -s, cell.bl)
            self.paint_cell_point(br.x(), br.y(), -s, -s, cell.br)
            contour_number = cell.contour_line()
            self.painter.drawText(cell.rect.center(), str(contour_number))

        self.set_blob_style()
        self.paint_cell_line(cell)
        self.empty()

    def paint_grid(self):
        """paint the grid of the marching squares
        """
        for row in self.mc.grid:
            for cell in row:
                self.paint_cell(cell)
