# -*- coding: utf-8 -*-
"""guardian_gemelo.py - vigila que este repositorio y su gemelo no se separen.

POR QUE EXISTE. Este repositorio y su hermano publican EL MISMO instrumento: uno lleva el
metodo y las cifras, el otro se instala como skill de Claude Code. Tiene que ser el mismo
codigo, porque un metodo que no trae su herramienta no se puede reproducir y un paquete que no
trae la suya no se puede instalar. El coste de eso es que cada arreglo hay que escribirlo dos
veces, a mano, en dos sitios. Sale bien mientras alguien se acuerda. El dia que no se acuerde,
un repositorio queda arreglado y el otro sigue publicando el fallo, y los dos siguen dando
verde por su cuenta, porque cada uno solo se mira a si mismo.

QUE HACE. Se trae la lista de ficheros del gemelo, compara los que estan declarados como
comunes y exige que sean identicos byte a byte. Los que existen solo en uno son de empaquetado
y se declaran aparte. Un fichero que aparece sin declarar tambien suspende: un guardian que
solo mira lo que ya conoce deja de vigilar en cuanto alguien añade algo.

POR QUE NO SE LLAMA `test_gemelo.py`. El criterio del detector que vive en este repositorio es
el NOMBRE del fichero: cualquier `test_*.py` versionado entra en su universo de bancos. Este
guardian no es un banco de pruebas, es una comparacion entre dos repositorios, y llamarlo asi
lo metia en la medicion como si tuviera casos que juzgar. Es la clase de contaminacion que el
propio detector persigue, y la forma de evitarla es nombrar el fichero por lo que hace.

DOS AVISOS HONESTOS:

1. Entre el push a un repositorio y el push al otro, ESTE GUARDIAN SE PONE ROJO A PROPOSITO. No
   es un fallo intermitente: es la unica ventana en la que los dos arboles difieren de verdad, y
   taparla seria devolver el problema. Se arregla subiendo el hermano. El flujo de CI espera y
   vuelve a mirar una vez antes de darlo por real.
2. Sin red no comprueba nada, y en ese caso sale con 2 y no con 0. Un guardian que aprueba
   cuando no ha podido mirar convierte cada duda en una puerta abierta. Mientras el gemelo no
   exista todavia en GitHub, esta es la salida que da.

Uso:
    python guardian_gemelo.py
    GEMELO_LOCAL=../skill-detector-control-negativo python guardian_gemelo.py
"""
import hashlib
import io
import json
import os
import sys

try:
    from urllib.request import urlopen, Request
except ImportError:                                        # Python 2
    from urllib2 import urlopen, Request

AQUI = os.path.dirname(os.path.abspath(__file__))

# El gemelo de este repositorio. Esta linea cambia en cada uno de los dos, y es lo unico que
# cambia entre las dos copias de este fichero.
GEMELO = "jleonceo/skill-detector-control-negativo"
RAMA = "main"

# EL CENSO. Tres listas, y entre las tres cubren todo lo que publica cualquiera de los dos.
# Añadir un fichero obliga a declararlo aqui, que es el momento en que alguien decide si viaja
# al hermano.
VIGILADOS = [
    ".github/workflows/ci.yml",
    ".gitignore",
    "LICENSE",
    "conftest.py",
    "pytest.ini",
    "ejemplo/etiquetas_ejemplo.yaml",
    "ejemplo/bancos/README.md",
    "ejemplo/bancos/run_tests_agregador.py",
    "ejemplo/bancos/test_assert_negativo.py",
    "ejemplo/bancos/test_espera_cero.py",
    "ejemplo/bancos/test_marca_cn.py",
    "ejemplo/bancos/test_nombre_negativo_aislado.py",
    "ejemplo/bancos/test_prosa_con_no_y_sin.py",
    "ejemplo/bancos/test_solo_positivo.py",
    "ejemplo/bancos/test_veredicto_malo.py",
    "skills/detector-control-negativo/SKILL.md",
    "skills/detector-control-negativo/mutar.py",
    "skills/detector-control-negativo/test_detector_control_negativo.py",
    "skills/detector-control-negativo/verificar_control_negativo.py",
]
PUEDEN_DIFERIR = {
    "README.md": "uno cuenta el metodo y el otro explica como se instala",
    "guardian_gemelo.py": "cada copia nombra al OTRO repositorio en su constante GEMELO",
}
SOLO_EN_UNO = {
    ".claude-plugin/marketplace.json": "el manifiesto de plugin, solo en el paquete",
    "skills/detector-control-negativo/LICENSE": "la licencia dentro de la skill empaquetada",
    "SPEC.md": "la especificacion, solo en el repositorio de la herramienta",
}
DECLARADOS = set(VIGILADOS) | set(PUEDEN_DIFERIR) | set(SOLO_EN_UNO)


# Las carpetas de cache de las herramientas, que no publica nadie. Van fuera del paseo porque
# este guardian mira el DISCO y no `git ls-files`: quiere cazar tambien el fichero que alguien
# acaba de crear y todavia no ha commiteado. El precio es que un resto de herramienta le sale
# como fichero sin declarar, y con `.pytest_cache` eso pasaba en cuanto alguien lanzaba pytest
# en el repositorio, que es el primer comando que va a lanzar cualquiera que lo clone.
CACHES = (".git", "__pycache__", ".pytest_cache")


def _andar(raiz):
    """`os.walk` con el error ARRIBA. Sin `onerror`, una carpeta ilegible se traga su subarbol
    entero y el guardian sigue como si lo hubiera mirado."""
    def reventar(err):
        raise err
    return os.walk(raiz, onerror=reventar)


def _sha(datos):
    """Sobre el contenido con los saltos de linea normalizados.

    Sin esto, un clon de Windows con `core.autocrlf` en marcha difiere de la copia del servidor
    en TODOS los ficheros de texto y el guardian grita siempre, que es igual de inutil que
    callarse.
    """
    return hashlib.sha256(datos.replace(b"\r\n", b"\n")).hexdigest()


# UNA VIA LOCAL PARA PODER PROBAR EL GUARDIAN. `GEMELO_LOCAL` apunta a un clon en disco y
# sustituye a la red. No es una comodidad: un guardian que solo se puede ejercitar contra el
# servidor no se puede probar EN LAS DOS DIRECCIONES antes de confiar en el, y uno que nunca ha
# salido rojo no ha demostrado que sepa hacerlo.
LOCAL = os.environ.get("GEMELO_LOCAL")


def _pedir(url):
    req = Request(url, headers={"User-Agent": "guardian-gemelo"})
    return urlopen(req, timeout=30).read()


def _listar_remoto():
    if LOCAL:
        fuera = set()
        for raiz, dirs, ficheros in _andar(LOCAL):
            dirs[:] = [d for d in dirs if d not in CACHES]
            for f in ficheros:
                fuera.add(os.path.relpath(os.path.join(raiz, f), LOCAL).replace(os.sep, "/"))
        return fuera
    arbol = json.loads(_pedir(
        "https://api.github.com/repos/%s/git/trees/%s?recursive=1" % (GEMELO, RAMA)
    ).decode("utf-8"))
    if arbol.get("truncated"):
        raise RuntimeError("la API corto el arbol del gemelo: la lista esta incompleta")
    raros = [n.get("path") for n in arbol.get("tree", []) if n.get("type") not in ("blob", "tree")]
    if raros:
        raise RuntimeError("nodos que no son fichero ni carpeta (submodulos?): %s" % raros)
    return set(n["path"] for n in arbol.get("tree", []) if n.get("type") == "blob")


def _leer_remoto(rel):
    if LOCAL:
        return io.open(os.path.join(LOCAL, rel.replace("/", os.sep)), "rb").read()
    return _pedir("https://raw.githubusercontent.com/%s/%s/%s" % (GEMELO, RAMA, rel))


def main():
    print("=" * 78)
    print("GEMELO  --  este repositorio contra %s" % GEMELO)
    print("=" * 78)

    if LOCAL:
        # Era un interruptor de apagado: `GEMELO_LOCAL=.` comparaba el repositorio consigo
        # mismo y daba verde siempre, con los contadores identicos.
        if os.path.realpath(LOCAL) == os.path.realpath(AQUI):
            print("  GEMELO_LOCAL apunta a este mismo repositorio. Eso no es un gemelo. Sale con 2.")
            return 2
        if os.environ.get("CI"):
            print("  GEMELO_LOCAL dentro de un flujo de CI: ahi la comparacion va contra el")
            print("  servidor, y un clon local la convierte en un interruptor de apagado.")
            return 2
        print("  (comparando contra el clon local %s, no contra el servidor)" % LOCAL)

    try:
        remotos = _listar_remoto()
    except Exception as e:
        print("  NO SE PUDO COMPROBAR: %s" % e)
        print("  Sin poder leer el arbol del gemelo no hay comparacion, y un guardian que")
        print("  aprueba sin haber mirado no es un guardian. Sale con 2 para que no se")
        print("  confunda con un verde.")
        return 2

    if not remotos:
        print("  NO SE PUDO COMPROBAR: el arbol de %s vino vacio." % GEMELO)
        return 2

    locales = set()
    for raiz, dirs, ficheros in _andar(AQUI):
        dirs[:] = [d for d in dirs if d not in CACHES]
        for f in ficheros:
            locales.add(os.path.relpath(os.path.join(raiz, f), AQUI).replace(os.sep, "/"))

    quejas, no_leidos = [], []

    # 1. Lo declarado tiene que ESTAR en los dos: aqui se cazan las bajas, los renombrados, los
    #    cambios de caja y un arbol del gemelo movido bajo otro prefijo.
    for rel in VIGILADOS:
        if rel not in locales:
            quejas.append("declarado y NO esta aqui: %s" % rel)
        if rel not in remotos:
            quejas.append("declarado y NO esta en el gemelo: %s" % rel)

    # 2. Lo que aparece sin declarar tambien suspende.
    for rel in sorted((locales | remotos) - DECLARADOS):
        if rel.startswith(".git/"):
            continue
        quejas.append("sin declarar, decide si tiene que viajar al gemelo: %s" % rel)

    # 3. Y lo declarado que esta en los dos, que coincida.
    for rel in VIGILADOS:
        if rel not in locales or rel not in remotos:
            continue
        try:
            remoto = _leer_remoto(rel)
        except Exception as e:
            no_leidos.append((rel, str(e)))
            continue
        local = io.open(os.path.join(AQUI, rel.replace("/", os.sep)), "rb").read()
        if _sha(local) != _sha(remoto):
            quejas.append("SEPARADOS: %s" % rel)

    print("  vigilados: %d   pueden diferir: %d   solo en uno: %d"
          % (len(VIGILADOS), len(PUEDEN_DIFERIR), len(SOLO_EN_UNO)))

    # El orden importa: la separacion se imprime ANTES que los fallos de lectura. Al reves, un
    # error 500 en un fichero cualquiera tapaba el unico mensaje que este guardian existe para dar.
    if quejas:
        print()
        print("  *** LOS GEMELOS SE HAN SEPARADO ***")
        for q in quejas:
            print("    %s" % q)
        if no_leidos:
            print()
            for rel, e in no_leidos:
                print("    NO LEIDO  %s  (%s)" % (rel, e))
        print()
        print("  Si acabas de arreglar algo aqui, subelo tambien al otro. La ventana entre los")
        print("  dos push es la unica en la que este rojo es esperado, y el CI la reintenta.")
        return 1

    if no_leidos:
        print()
        for rel, e in no_leidos:
            print("  NO LEIDO  %s  (%s)" % (rel, e))
        print("  Un fichero que no se pudo leer no es un fichero que coincida.")
        return 2

    print()
    print("  Los %d ficheros vigilados coinciden, y no ha aparecido ninguno sin declarar."
          % len(VIGILADOS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
