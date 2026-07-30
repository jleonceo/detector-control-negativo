# -*- coding: utf-8 -*-
"""Banco de ejemplo donde el caso entero es la trampa.

No hay ninguna asercion negativa a la vista: lo que hay es una asercion de igualdad contra el
veredicto MALO. El caso monta una fuente caducada y exige que la herramienta responda
`NO_CONFIA`. Reconocerlo obliga a mirar el VALOR que se afirma, y no la forma de la asercion.
"""
import unittest


class Trampa(unittest.TestCase):

    def test_fuente_caducada(self):
        self.assertEqual(estado_de(fuente_caducada()), "NO_CONFIA")
