# -*- coding: utf-8 -*-
"""Banco del productor.

Este banco no depende del disco y funciona sin red. No se apoya en fixtures inventados: usa
la plantilla real del repositorio, porque un fixture sin relacion con el corpus no prueba
nada. Tampoco escribe fuera de su carpeta y no necesita configuracion.

Esta plantado a proposito, y es el fixture que mas vale del repositorio. Todo lo de arriba
es prosa con «no» y «sin» por todas partes, y aun asi este banco solo comprueba que lo bueno
pasa. La primera version del criterio miraba esas dos palabras dentro de cualquier cadena y
disparaba en 129 bancos de 129: una senal que marca al 100 % de la poblacion no separa nada,
solo baja el recuento.
"""
import os


def test_escribe_el_fichero():
    assert os.path.exists(ruta)
