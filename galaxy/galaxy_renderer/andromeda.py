""" simple PyQt5 simulation controller """
#
# Copyright (C) 2017  "Peter Roesch" <Peter.Roesch@fh-augsburg.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# or open http://www.fsf.org/licensing/licenses/gpl.html
#
import sys
import multiprocessing

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from Semesterprojekt.galaxy.galaxy_renderer import simulation_mockup, galaxy_renderer, andromeda_controller
from Semesterprojekt.galaxy.galaxy_renderer.simulation_constants import END_MESSAGE


class SimulationGUI(QtWidgets.QWidget):
    """
        Widget with two buttons
    """
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setGeometry(0, 0, 300, 300)
        self.setWindowTitle('Simulation')

        self.start_button = QtWidgets.QPushButton('Start', self)
        self.start_button.setGeometry(10, 10, 60, 35)
        self.start_button.clicked.connect(self.start_simulation)

        self.stop_button = QtWidgets.QPushButton('Stop', self)
        self.stop_button.setGeometry(100, 10, 60, 35)
        self.stop_button.clicked.connect(self.stop_simulation)

        self.quit_button = QtWidgets.QPushButton('Quit', self)
        self.quit_button.setGeometry(190, 10, 60, 35)
        self.quit_button.clicked.connect(self.exit_application)

        self.slider = QtWidgets.QSlider(self)
        self.slider.setValue(1)
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setTickInterval(25)
        self.slider.setGeometry(10, 100, 280, 20)
        self.slider.setRange(0, 100)
        self.slider.valueChanged.connect(self.application_speed)

        self.slider_delta = QtWidgets.QSlider(self)
        self.slider_delta.setValue(3600)
        self.slider_delta.setOrientation(Qt.Horizontal)
        self.slider_delta.setTickInterval(100)
        self.slider_delta.setGeometry(10, 150, 280, 20)
        self.slider_delta.setRange(3600, 360000)
        self.slider_delta.valueChanged.connect(self.application_deltav)

        self.slider_planets = QtWidgets.QSlider(self)
        self.slider_planets.setValue(9)
        self.slider_planets.setOrientation(Qt.Horizontal)
        self.slider_planets.setTickInterval(1)
        self.slider_planets.setGeometry(10, 200, 280, 20)
        self.slider_planets.setRange(5, 100)
        self.slider_planets.valueChanged.connect(self.planetcounter)

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(10, 80, 200, 20)
        self.label.setText("Speed: ... times")

        self.label_delta = QtWidgets.QLabel(self)
        self.label_delta.setGeometry(10, 130, 200, 20)
        self.label_delta.setText("Delta t, Default: 3600")

        self.label_counter_planets = QtWidgets.QLabel(self)
        self.label_counter_planets.setGeometry(10, 180, 250, 20)
        self.label_counter_planets.setText("Sonnensystem Größe von innen")

        self.renderer_conn, self.simulation_conn = None, None
        self.render_process = None
        self.simulation_process = None
        self.simulation_speed = 1
        self.simulation_delta_v = 3600
        self.counter_planets = 50

    def start_simulation(self):
        """
            Start simulation and render process connected with a pipe.
        """
        self.renderer_conn, self.simulation_conn = multiprocessing.Pipe()
        self.simulation_process = \
            multiprocessing.Process(target=andromeda_controller.startup,
                                    args=(self.simulation_conn,
                                          self.counter_planets,
                                          self.simulation_delta_v,
                                          self.simulation_speed))
        self.render_process = \
            multiprocessing.Process(target=galaxy_renderer.startup,
                                    args=(self.renderer_conn, 60), )

        self.simulation_process.start()
        self.render_process.start()

    def stop_simulation(self):
        """
            Stop simulation and render process by sending END_MESSAGE
            through the pipes.
        """
        if self.simulation_process is not None:
            self.simulation_conn.send(END_MESSAGE)
            self.simulation_process = None

        if self.render_process is not None:
            self.renderer_conn.send(END_MESSAGE)
            self.render_process = None

    def exit_application(self):
        """
            Stop simulation and exit.
        """
        self.stop_simulation()
        self.exit_application()
        self.close()

    def application_speed(self):
        self.simulation_speed = self.slider.value()
        self.label.setText("Speed: " + str(self.slider.value()))

    def application_deltav(self):
        self.simulation_delta_v = self.slider_delta.value()
        self.label_delta.setText("Delta t (Default 3600): " + str(self.slider_delta.value()))

    def planetcounter(self):
        self.counter_planets = self.slider_planets.value()
        self.label_counter_planets.setText("Sonnensystem Größe von innen: " + str(self.slider_planets.value()))


def _main(argv):
    """
        Main function to avoid pylint complains concerning constant names.
    """
    app = QtWidgets.QApplication(argv)
    simulation_gui = SimulationGUI()
    simulation_gui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    _main(sys.argv)