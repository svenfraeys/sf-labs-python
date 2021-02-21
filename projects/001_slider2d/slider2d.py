import math
from PySide2 import QtWidgets, QtGui, QtCore


class Slider2DWidget(QtWidgets.QWidget):
    """slider 2d widget
    """
    # signals
    on_value_x_changed = QtCore.Signal(float)
    on_value_y_changed = QtCore.Signal(float)

    def __init__(self, parent=None):
        """construct the slider 2D widget

        :param parent: parent widget
        :type parent: QtWidgets.QWidget
        """
        super(Slider2DWidget, self).__init__(parent=parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)

        self.__is_mouse_over = False
        self.__value_x = 0.0
        self.__value_y = 0.0

        self.__controller_radius = 20
        self.__dragging_controller = False
        self.__drag_offset = QtCore.QPoint()

    def __controller_draw_center(self):
        """return the center point where the controller is drawn
        """
        x = (self.width() / 2.0) + self.__value_x * (self.width() / 2.0)
        y = (self.height() / 2.0) + self.__value_y * -1 * (self.height() / 2.0)
        return QtCore.QPoint(x, y)

    def paintEvent(self, event):
        """start painting the slider 2D
        """
        painter = QtGui.QPainter(self)

        # draw the background
        brush = self.palette().light().color()
        pen = self.palette().dark().color()
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        # get the color of the circle
        if self.__dragging_controller:
            brush = self.palette().dark().color()
            dark_pen = self.palette().highlight().color()
        elif self.__is_mouse_over:
            brush = self.palette().button().color()
            dark_pen = self.palette().highlight().color()
        else:
            brush = self.palette().button().color()
            dark_pen = self.palette().dark().color()

        # pain the circle
        painter.begin(self)
        painter.setPen(dark_pen)
        painter.setBrush(brush)
        width = self.__controller_radius
        height = self.__controller_radius
        point = self.__controller_draw_center()

        # draw the ellipse
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawEllipse(point.x() - width / 2.0, point.y() - height / 2.0,
                            self.__controller_radius,
                            self.__controller_radius)

        painter.end()

        # draw the dark rect border
        painter.begin(self)

        if self.hasFocus():
            pen = self.palette().highlight().color()
        elif self.underMouse():
            pen = self.palette().shadow().color()
        else:
            pen = self.palette().dark().color()

        painter.setPen(pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        painter.end()

    def keyPressEvent(self, event):
        """moving the controller around with the keyboard
        """
        speed = 0.05
        if event.modifiers() == QtCore.Qt.ShiftModifier:
            speed *= 6

        if event.key() == QtCore.Qt.Key_Up:
            self.set_value_y(self.value_y() + speed)
        elif event.key() == QtCore.Qt.Key_Down:
            self.set_value_y(self.value_y() - speed)
        elif event.key() == QtCore.Qt.Key_Left:
            self.set_value_x(self.value_x() - speed)
        elif event.key() == QtCore.Qt.Key_Right:
            self.set_value_x(self.value_x() + speed)

    def sizeHint(self):
        """return the size hint
        """
        return QtCore.QSize(250, 250)

    def __get_controller_center_difference(self, point):
        """return the distance between the point and the controller
        """
        difference = self.__controller_draw_center() - point
        length = math.sqrt(difference.x() ** 2 + difference.y() ** 2)
        return length

    def __contains_controller(self, point):
        """return if the point contains the controller
        """
        length = self.__get_controller_center_difference(point)
        if length <= (self.__controller_radius / 2.0):
            return True
        else:
            return False

    def mouseReleaseEvent(self, event):
        """on mouse click release
        """
        self.__dragging_controller = False
        self.update()

    def __map_to_coordinates(self, point):
        """convert a point to the value
        """
        x = (point.x() - self.width() / 2.0) / (self.width() / 2.0)
        y = (point.y() - self.height() / 2.0) / (self.height() / 2.0)
        y *= -1.0
        return x, y

    def mouseMoveEvent(self, event):
        """mouse move
        """
        if self.__dragging_controller:
            x, y = self.__map_to_coordinates(event.pos() + self.__drag_offset)
            self.set_value_xy(x, y)

        if self.__contains_controller(event.pos()):
            if not self.__is_mouse_over:
                self.__is_mouse_over = True
                self.update()
        else:
            if self.__is_mouse_over:
                self.__is_mouse_over = False
                self.update()

    def leaveEvent(self, event):
        """on leave we want to redraw
        """
        self.update()

    def enterEvent(self, event):
        """on mouse enter we want to redraw
        """
        self.update()

    def mousePressEvent(self, event):
        """pressing will move the controller around
        """
        if event.button() == QtCore.Qt.LeftButton:
            if self.__contains_controller(event.pos()):
                self.__dragging_controller = True
                center = self.__controller_draw_center()
                self.__drag_offset = center - event.pos()
                self.update()
            else:
                x, y = self.__map_to_coordinates(event.pos())
                self.set_value_xy(x, y)
                self.__drag_offset = QtCore.QPoint()
                self.__dragging_controller = True
                self.__is_mouse_over = True

    def value_xy(self):
        """return the xy value stored for the slider as a tuple

        :rtype: (float, float)
        """
        return self.__value_x, self.__value_y

    def value_x(self):
        """returns the x value

        :rtype: float
        """
        return self.__value_x

    def value_y(self):
        """return the y value

        :rtype: float
        """
        return self.__value_y

    def set_value_x(self, value):
        """set the x value of the controller

        :param value: value X to set
        :type value: float
        """
        self.__value_x = value
        self.update()
        self.on_value_x_changed.emit(self.__value_x)

    def set_value_y(self, value):
        """set the y value

        :param value: the Y value to set
        :type value: float
        """
        self.__value_y = value
        self.update()
        self.on_value_y_changed.emit(self.__value_y)

    def set_value_xy(self, x, y):
        """set the xy value

        :param x: x value to set
        :type x: float

        :param y: y value to set
        :type y: float
        """
        self.__value_x = x
        self.__value_y = y
        self.update()
        self.on_value_x_changed.emit(self.__value_x)
        self.on_value_y_changed.emit(self.__value_y)

    def set_controller_radius(self, value):
        """set the radius of the controller

        :param value: radius to set
        :type value: float
        """
        self.__controller_radius = value
        self.update()

    def controller_radius(self):
        """return the controller radius

        :rtype: float
        """
        return self.__controller_radius
