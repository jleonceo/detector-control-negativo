# -*- coding: utf-8 -*-
"""Banco de ejemplo que solo comprueba que lo bueno pasa.

Esta plantado a proposito: es el caso que el detector tiene que senalar. Da verde con el
codigo bueno y tambien con el roto, porque nunca le pregunta al motor por una entrada mala.

Fijate en lo que falta, que es lo unico que hay que ver aqui: ni una comprobacion de que el
motor rechace una entrada mala, ni una que espere cero, ni un caso que afirme el veredicto
malo. El detector se apoya en la ausencia de todas esas formas a la vez.
"""


def test_suma_dos_mas_dos():
    assert calcular(2, 2) == 4


def test_devuelve_el_nombre():
    assert motor.nombre() == "cosa"
