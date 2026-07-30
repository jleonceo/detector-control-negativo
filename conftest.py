# -*- coding: utf-8 -*-
"""conftest.py - saca del descubrimiento de pytest las fixtures plantadas del ejemplo.

POR QUE EXISTE. `ejemplo/bancos/` son SIETE FIXTURES PLANTADAS, una por senal del detector, con
el fichero de etiquetas de al lado diciendo que veredicto le toca a cada una. Son el material
que el detector MIDE, y por eso invocan simbolos que no existen: `calcular`, `motor`,
`estado_de`. Nadie las ejecuta, ni aqui ni en el flujo de CI.

Pytest si las recogia, por el nombre, y las ejecutaba. Resultado en un clon recien hecho:

    git clone <repo> && cd <repo> && python -m pytest -q
    9 failed, 30 passed        (codigo de salida 1)

Los nueve fallos eran las fixtures, y los 30 aprobados el banco del detector, que ese mismo dia
crecio a 32 con el caso que vigila este censo y el que le exige a `mutar.py` devolver el fichero
byte a byte. La cifra de arriba es la del defecto y se deja escrita como estaba.

Un repositorio que ensena que una suite verde no prueba nada, puesto en rojo por el primer
comando que teclea quien lo clona, y por un motivo que no tiene nada que ver con su tesis.

POR QUE NO SE RENOMBRAN, que era la salida obvia. El universo del detector se define por el
NOMBRE del fichero (`_RE_BANCO` en verificar_control_negativo.py), asi que una fixture que no se
llame `test_*.py` deja de existir para el. Medido el 30/07/2026 sobre una copia del repositorio,
renombrando las siete a `banco_*.py` y arrastrando el fichero de etiquetas detras:

    tal cual     bancos con casos propios 8 · agregadores 1 · con control negativo 6 · SIN 2
                 el detector contra las etiquetas: 9 de 9
    renombradas  bancos con casos propios 1 · agregadores 1 · con control negativo 1 · SIN 0
                 el detector contra las etiquetas: 2 de 2, y siete etiquetas apuntando a
                 ficheros que ya no estan en el universo

O sea que renombrar rompe el ejemplo por partida doble: pierde siete de sus ocho bancos, y lo
que acaba publicando es que aqui no hay ni uno sin control negativo, con codigo de salida 0. Es
el falso verde que este repositorio persigue, fabricado a mano para que otra herramienta no se
queje. `--excluir` tampoco vale, porque saca rutas del universo y aqui hace falta lo contrario:
que sigan dentro.

LOS DOS LIMITES DE ESTO, escritos aqui y no descubiertos luego:

1. Un banco de verdad puesto en `ejemplo/bancos/` tampoco lo ejecutaria pytest. Esa carpeta es
   material de medicion y solo eso; el dia que haya casos que juzgar, van en otra carpeta.
2. Nombrar una fixture en la linea de comandos (`pytest ejemplo/bancos/test_solo_positivo.py`)
   la ejecuta igual: la exclusion vale para el descubrimiento y no para lo que se pide a mano.
   Ahi el rojo es lo correcto, porque lo ha pedido alguien a proposito.
"""

# Toda la carpeta, y con glob en vez de fichero a fichero: una fixture nueva se planta para
# probar una senal nueva del detector, y tener que acordarse de anotarla aqui es justo el paso
# que no se da.
collect_ignore_glob = ["ejemplo/bancos/*"]
