# -*- coding: utf-8 -*-
"""Banco de ejemplo con la forma mas comun: la asercion negativa de la libreria estandar.

Dispara dos senales a la vez, ASSERT_NEG por el `assertFalse` y NOMBRE_NEG por el nombre del
caso, y el informe lo dice. Un veredicto sin su motivo vuelve a ser un contador sin su objeto.
"""
import unittest


class Motor(unittest.TestCase):

    def test_acepta_lo_bueno(self):
        self.assertTrue(motor.valida("entrada correcta"))

    def test_rechaza_lo_malo(self):
        self.assertFalse(motor.valida("basura"))
