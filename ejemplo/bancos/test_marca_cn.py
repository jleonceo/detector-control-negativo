# -*- coding: utf-8 -*-
"""Banco de ejemplo que marca su brazo de control con la marca explicita del proyecto.

La marca es la senal mas barata de reconocer y la mas facil de romper sin que nadie se
entere: al quitarla del criterio, el unico banco que la necesitaba en exclusiva estaba fuera
del fichero de etiquetas, asi que la mutacion pasaba callando. De ahi que el banco del
detector traiga hoy un caso que aisla el literal `_CN_` de la frase larga.
"""


def test_clasifica_un_documento_vivo():
    assert clasificar("informe.md") == "vivo"


# CN1 · un fichero recien escrito sigue vivo, aunque el barrido pase por encima
def test_CN_un_fichero_recien_escrito_sigue_vivo():
    barrido()
    assert clasificar("informe.md") == "vivo"
