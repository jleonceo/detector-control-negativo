# -*- coding: utf-8 -*-
"""Lanza todos los bancos de la carpeta y agrega su resultado.

Este fichero es el tercer valor de la etiqueta, y no un si ni un no. Se llama como un banco y
git lo publica, pero no tiene un solo caso propio que juzgar: descubre otros ficheros y los
lanza. Contarlo entre los que solo comprueban que lo bueno pasa es contar el objeto
equivocado, y en la primera pasada del detector cinco de los veinticuatro senalados eran esto.
"""
import glob
import os
import subprocess
import sys


def main():
    aqui = os.path.dirname(os.path.abspath(__file__))
    fallos = 0
    for ruta in sorted(glob.glob(os.path.join(aqui, "test_*.py"))):
        if subprocess.run([sys.executable, ruta]).returncode != 0:
            fallos += 1
    print("bancos lanzados con fallo: %d" % fallos)
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
