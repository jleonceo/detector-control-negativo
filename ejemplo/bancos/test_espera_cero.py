# -*- coding: utf-8 -*-
"""Banco de ejemplo cuyo brazo negativo es una condicion, y no una palabra.

Aqui esta el caso que hace falta reconocer para que el recuento valga. El proyecto envuelve
la asercion en un helper propio,
`check(...)`,
asi que buscar el nombre de la asercion de la libreria estandar aqui devuelve cero. Lo que
importa es la FORMA de la condicion (esperar cero, vacio, None o False) y no el nombre de la
funcion que la envuelve. Sin esta senal, un banco como este pasaba por carente, y fue uno de
los dos falsos positivos que la revision a mano encontro.
"""


def check(condicion, etiqueta):
    if not condicion:
        raise AssertionError(etiqueta)


def caso_uno():
    check(len(hallazgos("corpus limpio")) == 0, "un corpus limpio deja la lista vacia")


def caso_dos():
    check(permitir is False, "BLOQUEA el documento con dato personal")
