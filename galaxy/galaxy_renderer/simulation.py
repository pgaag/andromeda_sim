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
import multiprocessing
import sys

from PyQt5 import uic
from PyQt5 import QtWidgets

# from Semesterprojekt.galaxy.galaxy_renderer import simulation_mockup, galaxy_renderer
# from Semesterprojekt.galaxy.galaxy_renderer.simulation_constants import END_MESSAGE
from Semesterprojekt.galaxy.galaxy_renderer.simulation_constants import END_MESSAGE
from Semesterprojekt.galaxy.galaxy_renderer import simulation_mockup, andromeda_controller
from Semesterprojekt.galaxy.galaxy_renderer import galaxy_renderer


class SimulationGUI(QtWidgets.QWidget):
    """
        Widget with two buttons
    """

    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        # Set up the user interface from Designer.
        self.ui = uic.loadUi('simulation.ui')
        # self.ui = uic.loadUi("simulation.ui")
        self.ui.show()

        self.ui.start_button.clicked.connect(self.start_simulation)
        self.ui.stop_button.clicked.connect(self.stop_simulation)
        self.ui.quit_button.clicked.connect(self.exit_application)

        self.renderer_conn, self.simulation_conn = None, None
        self.render_process = None
        self.simulation_process = None

    def start_simulation(self):
        """
            Start simulation and render process connected with a pipe.
        """
        num_of_planets = eval(self.ui.num_of_planets.text())
        delta_t = eval(self.ui.delta_t.text())
        sim_speed = eval(self.ui.sim_speed.text())

        self.renderer_conn, self.simulation_conn = multiprocessing.Pipe()

        self.simulation_process = \
            multiprocessing.Process(target=andromeda_controller.startup,
                                    args=(self.simulation_conn,
                                          num_of_planets,
                                          delta_t,
                                          sim_speed))
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
        self.close()
        exit()


def _main(argv):
    """
        Main function to avoid pylint complains concerning constant names.
    """

    app = QtWidgets.QApplication(argv)
    simulation_gui = SimulationGUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    _main(sys.argv)
