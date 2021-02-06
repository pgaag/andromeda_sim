""" Erster Prototyp für die Galaxien-Simulation """
import random

import numpy as np
import scipy
from scipy.constants import astronomical_unit

DISTANCE_SUN = astronomical_unit / 1000


class Planet:
    """
    Klasse Planet zu Reise durch die Galaxie
    Einheiten in meter
    """

    def __init__(self, index, pos_np_array, vel_np_array, mass):
        self.index = index
        self.position = pos_np_array
        self.velocity = vel_np_array
        self.mass = mass
        self.acceleration = np.zeros(3, dtype="float64")
        self.next_position = np.zeros(3, dtype="float64")
        self.next_velocity = np.zeros(3, dtype="float64")

    def update_acceleration(self, planets):
        self.acceleration = self.calculate_acceleration(planets)

    def update_next_position(self, delta_time):
        self.next_position = self.calculate_position(delta_time)

    def update_next_velocity(self, delta_time):
        self.next_velocity = self.calculate_velocity(delta_time)

    def calculate_acceleration(self, planets, galaxy):
        """
        Berechnet die Beschleunigung eines Planeten.

        Args:
            planets: Die Liste an Planeten, die für die Berechnung
                     berücksichtigt werden sollen.
            self: Der Planet, dessen Beschleunigung berechnet werden soll.

        Returns:
            Die Beschleunigung des Planeten als np-Array.
        """
        total_force = np.zeros(3, dtype="float64")

        for key, planet in planets.items():
            if planet is self:
                continue
            temp = self.calculate_gravitational_force(planet, galaxy)

            total_force += temp
        new_acceleration = total_force / self.mass
        return new_acceleration

    def calculate_gravitational_force(self, target, galaxy):
        """
        Berechnet die Gravitationskraft zwischen zwei Planeten.

        Args:
            self: Der Planet, der angezogen wird.
            target: Der Planet, der den anderen Planeten anzieht.

        Returns:
            Die Gravitationskraft zwischen den Planeten.
        """
        distance = target.position - self.position
        distance_abs = np.linalg.norm(distance)
        mass = self.mass * target.mass

        # Anwendung der Formel aus Abschnitt 5.3 (Die Gravitationskraft)
        gravitational_force = 6.672e-11 \
                              * (mass / distance_abs ** 3) * distance

        return gravitational_force

    def calculate_position(self, delta_time):
        """
        Berechnet die neue Position eines Planeten zu einem gewissen Zeitpunkt.

        Args:
            self: Der Planet, dessen Position berechnet werden soll.
            delta_time: Der Zeitpunkt, für die die Position berechnet werden
                        soll.

        Returns:
            Die neue Position des Planeten als np-Array.
        """
        new_velocity = delta_time * self.velocity
        new_acceleration = (delta_time ** 2 / 2) * self.acceleration

        # Anwendung der Taylor-Formel aus 5.2 (Schrittweise Simulation)
        new_position = self.position + new_velocity + new_acceleration
        return new_position

    def calculate_velocity(self, delta_time):
        """
        Berechnet die Geschwindigkeit eines Planeten zu einem gewissen
        Zeitpunkt.

        Args:
            self: Der Planet, dessen Geschwindigkeit berechnet werden soll.
            delta_time: Der Zeitpunkt, für die die Geschwindigkeit berechnet
                        werden soll.

        Returns:
            Die neue Geschwindigkeit des Planeten als np-Array.
        """
        new_velocity = self.velocity + self.acceleration * delta_time
        return new_velocity


class OurRandom:
    """ Klasse zur generieren von zufälligen Zahlen"""

    def __init__(self, rangeLow, rangeHigh):
        self.range_low_distance = rangeLow
        self.range_high_distance = rangeHigh

    def generate_random(self):
        """
        Generiert eine Zahl im vorgegebenen Bereich
        """
        return random.uniform(self.range_low_distance, self.range_high_distance)


class Galaxy:
    """ Klasse Galaxy zur Simulation """
    index = 0

    def __init__(self, nr_of_bodies):
        self.total_mass = 0
        self.planets = Galaxy.initialize_planets(nr_of_bodies)
        self.calc_init_velocity()

    def calc_total_mass(self):
        """ Summiert die Masse aller Planeten"""
        mass = 0
        for key, planet in self.planets.items():
            mass += planet.mass
        self.total_mass = mass
        return mass

    def calc_center_mass_point(self):
        """ Berechnet den Masseschwerpunkt des gesamten System"""
        mass = 0
        for key, planet in self.planets.items():
            mass += planet.mass * planet.position
        return (1 / self.calc_total_mass()) * mass

    def calc_specific_mass_center(self, this_planet):
        """ Formel  (5) aus der Aufgabenstellung """
        spec_place = np.zeros(3, dtype=np.float64)
        for key, planet in self.planets.items():
            if planet != this_planet:
                spec_place += planet.mass * (planet.position - DISTANCE_SUN)
        return spec_place / (self.total_mass - this_planet.mass)

    def calc_init_velocity(self):
        """
        Berechnet die intiale Geschwindigkeit aller planeten
        Verwendet Formel  (8) und (9) aus der Aufgabenstellung
        """
        self.calc_center_mass_point()
        for key, planet in self.planets.items():
            center_mass_planet = self.calc_specific_mass_center(planet)
            initial_velocity = np.cross(
                ((planet.position - DISTANCE_SUN) - center_mass_planet),
                [0, 0, 1])
            initial_velocity_abs = (
                ## Formel (8) Semesterprojekt
                    ((self.total_mass - planet.mass) / self.total_mass) *
                    np.sqrt(
                        (scipy.constants.G * self.total_mass) /
                        # Formel (8): folgender Ausdruck entspricht r = |r(i) - r (s,i)|
                        np.linalg.norm((planet.position - DISTANCE_SUN) - center_mass_planet)
                    )
            )
            # Formel (9): Berechnung der initialen Geschwindigkeit mit einer Umformung der Formel
            planet.velocity = (initial_velocity / np.linalg.norm(initial_velocity)) \
                              * initial_velocity_abs
        self.planets[0].velocity = 0

    def update_acceleration_for_plaent_with_index(self, i, acceleration):
        self.planets[i].acceleration = acceleration

    def calc_and_update_all_acceleration(self):
        for key, planet in self.planets.items():
            planet.update_acceleration(self.planets)

    def calc_all_next_positions_and_velocities(self, delta_time):
        for key, planet in self.planets.items():
            planet.update_next_position(delta_time)
            planet.update_next_velocity(delta_time)
        for key, planet in self.planets.items():  # Nach der Simulation
            planet.position = planet.next_position  # die Pos. + Ges. aller
            planet.velocity = planet.next_velocity  # Planeten aktualisieren

    def extract_all_planets_as_position_and_mass_dictionary(self):
        planet_dict = dict()
        for key, planet in self.planets.items():
            values = np.zeros(4, dtype="float64")
            values[0] = planet.position[0]
            values[1] = planet.position[1]
            values[2] = planet.position[2]
            values[3] = planet.mass
            planet_dict[planet.index] = values
        return planet_dict

    @staticmethod
    def initialize_planets(nr_of_bodies):
        """
        Initialisiert die Planeten für die Gravitations-Simulation.

        Returns:
            Liste der initialisierten Planeten
        """
        planets = dict()
        planets[Galaxy.index] = Planet(
                                    Galaxy.index,
                                    # Position  x y z
                                    np.array([DISTANCE_SUN, DISTANCE_SUN, DISTANCE_SUN]),
                                    # Velocity
                                    np.array([0, 0, 0]),
                                    # Mass
                                    1.989 * 10 ** 22)

        for _ in range(nr_of_bodies):
            Galaxy.index += 1
            planets[Galaxy.index] = Galaxy.generate_random_objects()
        return planets


    @staticmethod
    def generate_random_objects():
        """
        Generiert einen zufälligen Planeten in einer festgelegten range ( hardcodiert)
        """
        rand_mass = OurRandom(1e8, 10e12)
        rand_pos = OurRandom(-DISTANCE_SUN + 1, DISTANCE_SUN - 1)
        return Planet(
            # index
            Galaxy.index,
            # positions
            np.array([rand_pos.generate_random() + DISTANCE_SUN,
                      rand_pos.generate_random() + DISTANCE_SUN,
                      rand_pos.generate_random() / 10 + DISTANCE_SUN]),
            # velocity
            np.zeros(3, dtype="float64"),
            # mass
            rand_mass.generate_random())
