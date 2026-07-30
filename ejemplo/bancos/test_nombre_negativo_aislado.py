# -*- coding: utf-8 -*-
"""Banco de ejemplo cuyo brazo negativo esta solo en el NOMBRE del caso.

Ninguna otra senal lo acompana: la asercion es una igualdad corriente y el fichero no lleva
marca. Este fixture existe porque la senal del nombre era la que mas peso tenia en el recuento
(48 bancos del arbol donde se calibro dependen de ella) y era tambien la que ninguna prueba
aislaba: la mutacion que la borraba salia limpia.
"""


def test_no_permite_duplicados():
    assert deteccion(entrada_con_duplicados) == esperado
