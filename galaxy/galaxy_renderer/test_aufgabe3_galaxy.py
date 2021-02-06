import pytest
import Praktikum.Abgabe3.aufgabe3_galaxy
import scipy.constants
import unittest
from unittest import mock
import numpy as np

au = scipy.constants.au
delta_time = 3600
planets = []

with mock.MagicMock() as Planet:
    earth = Planet()
    earth.get_position.return_value = np.array([au, 0, 0])
    earth.get_velocity.return_value = np.array([29790, 0, 0])
    earth.get_mass.return_value = 5.9722 * 10 ** 24
    earth.get_acceleration.return_value = np.zeros(3, dtype=np.float64)

    planets.append(earth)

with mock.MagicMock() as Planet:
    sun = Planet()
    sun.get_position.return_value = np.array([au, au, 0])
    sun.get_velocity.return_value = np.array([0, 0, 0])
    sun.get_mass.return_value = 1.9885 * 10 ** 30
    sun.get_acceleration.return_value = np.zeros(3, dtype=np.float64)
    planets.append(sun)


class TestGalaxy(unittest.TestCase):

    def test_calculate_acceleration(self):
        temp = planets[0].calculate_acceleration(planets)
        # Planet.acceleration = Planet.calculate_acceleration(planets)
        # planets[0].acceleration = planets[0].calculate_acceleration(planets)
        # self.assertTrue(all([a == b for a, b in zip(self.__planet.position, self.test_pos_array)]))
        self.assertEquals(earth.get_acceleration)
        self.assertNotEquals(sun.return_value, [0.00000000e+00, -1.78223713e-08, 0.00000000e+00], True)

    def test_calculate_position(self):
        position = planets[1].test_calculate_position(planets)
        self.assertEqual(position, 1)

    def test_calculate_velocity(self):
        velocity = planets[1].test_calculate_velocity(planets)
        self.assertEqual(velocity, 1)

    def test_calculate_grav_force(self):
        grav_force = planets[1].test_calculate_grav_force(planets)
        self.assertEqual(1, 1)

    # def test_calculate_gravitational_force():

    # def test_calculate_velocity():

    # def test_update_step():

    # def test_update():
