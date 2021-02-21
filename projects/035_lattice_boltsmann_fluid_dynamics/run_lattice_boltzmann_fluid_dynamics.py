"""
Fluid dynamics

http://physics.weber.edu/schroeder/javacourse/LatticeBoltzmann.pdf
https://physics.weber.edu/schroeder/fluids/
https://www.math.nyu.edu/~billbao/report930.pdf

This is a work in progress need to improve my understanding on this
"""
import numpy as np
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QWidget, QApplication


class LatticeBoltzmannWidget(QWidget):
    """
    Lattice Boltzmann Widget
    """

    def _create_zeros(self):
        return np.zeros(self.lattice_size)

    def _create_ones(self):
        return np.ones(self.lattice_size)

    def calc_probability_distribution(self, x, y):
        n_0 = self.n_0[x][y]
        n_n = self.n_n[x][y]
        n_ne = self.n_ne[x][y]
        n_e = self.n_e[x][y]
        n_se = self.n_se[x][y]
        n_s = self.n_s[x][y]
        n_sw = self.n_sw[x][y]
        n_w = self.n_w[x][y]
        n_nw = self.n_nw[x][y]
        elements = [n_0, n_n, n_ne, n_e, n_se, n_s, n_sw, n_w, n_nw]
        e = np.random.choice(elements, 1, p=self.w)

    def calc_macroscopic_densities(self):
        """
        Calculates p
        """
        for x in range(self.lattice_size[0]):
            for y in range(self.lattice_size[1]):
                self.calc_probability_distribution(x, y)

        # sum up all the microscopic densities
        self.p = (self.n_0 + self.n_n + self.n_ne + self.n_e + self.n_se +
                  self.n_s + self.n_sw + self.n_w + self.n_nw)

    def calc_velocity_components(self):
        """
        Calculates u_x and u_y
        """
        # calculate the average x
        self.u_x = (self.n_ne + self.n_e + self.n_se +
                    self.n_sw + self.n_w + self.n_nw) / 6.0

        # calculate the average y
        self.u_y = (self.n_nw + self.n_n + self.n_ne +
                    self.n_se + self.n_s + self.n_sw) / 6.0

    def calc_equilibrium_densities(self):
        """
        Calculate the equilibrium densities (equation 8)
        """
        eq = self._create_zeros()

    def update_microscopic_densities(self):
        """
        Update the microscopic densities (equation 9)
        """

    def move_molecules(self):
        """
        Move the molecules
        """

    def __init__(self):
        super(LatticeBoltzmannWidget, self).__init__()

        self.lattice_size = (200, 100)

        # velocities
        self.e0 = np.array([0.0, 0.0])
        self.e1 = np.array([1.0, 0.0])
        self.e2 = np.array([0.0, 1.0])
        self.e3 = np.array([-1.0, 0.0])
        self.e4 = np.array([0.0, -1.0])
        self.e5 = np.array([1.0, 1.0])
        self.e6 = np.array([-1.0, 1.0])
        self.e7 = np.array([-1.0, -1.0])
        self.e8 = np.array([1.0, -1.0])

        # weights
        self.w0 = 4.0 / 9.0
        self.w1_4 = 1.0 / 9.0
        self.w5_w8 = 1.0 / 36.0

        # weights stored as the list
        self.w = np.array(
            [
                self.w0,
                self.w1_4, self.w1_4, self.w1_4, self.w1_4,
                self.w5_w8, self.w5_w8, self.w5_w8, self.w5_w8
            ]
        )

        # microscopic densities
        self.n_0 = self._create_ones()
        self.n_n = self._create_ones()
        self.n_ne = self._create_ones()
        self.n_e = self._create_ones()
        self.n_se = self._create_ones()
        self.n_s = self._create_ones()
        self.n_sw = self._create_ones()
        self.n_w = self._create_ones()
        self.n_nw = self._create_ones()

        # total density (macroscopic density)
        self.p = self._create_zeros()

        # average macroscopic velocity
        self.u_x = self._create_zeros()
        self.u_y = self._create_zeros()

        self.obstacles = self._create_zeros()
        self.tick()

    def tick(self):
        # collision
        self.calc_macroscopic_densities()
        self.calc_velocity_components()
        self.calc_equilibrium_densities()
        self.calc_equilibrium_densities()

        # streaming
        self.move_molecules()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.drawEllipse(-5, -5, 20, 20)


# elements = [1.1, 2.2, 3.3]
# probabilities = [0.2, 0.5, 0.3]
# print(np.random.choice(elements, 10, p=probabilities))

app = QApplication([])
w = LatticeBoltzmannWidget()
w.show()
app.exec_()
