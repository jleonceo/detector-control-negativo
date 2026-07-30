#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Banco del detector de bancos sin control negativo. CA1-CA6 de la SPEC.

Casi la mitad de los casos son CONTROLES NEGATIVOS, marcados `CN`. En un banco cuyo
objeto es justamente cazar bancos sin control negativo, no tenerlos seria la ironia
mas cara del repositorio.

El caso que mas vale es CN1: comprueba que la senal de nombre NO dispara sobre prosa
con «no» y «sin», que es como la primera version del detector acabo marcando 129 de 129
bancos. Una senal que dispara en el 100 % de la poblacion no separa nada, solo baja el
recuento. Ese fallo tiene que costar un rojo si vuelve.

Dos grupos de casos y dos objetos distintos. Los de fixture prueban el criterio con texto
escrito a mano, para que el veredicto correcto sea evidente al leerlo. Los de `SobreEsteRepo`
lo prueban sobre el arbol de verdad, que es donde aparecen los defectos que nadie imagina:
este repositorio trae bancos plantados a proposito en `ejemplo/bancos/` y su etiqueta al lado.
"""
import os
import shutil
import sys
import tempfile
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import verificar_control_negativo as det  # noqa: E402

# El arbol que se mide es este repositorio, preguntado a git desde la carpeta del banco y no
# desde el directorio de trabajo: asi el resultado no cambia segun desde donde se lance.
RAIZ = det.raiz_git(AQUI)
ETIQUETAS_EJEMPLO = os.path.join(RAIZ or AQUI, "ejemplo", "etiquetas_ejemplo.yaml")


# --- Fixtures: texto de banco, escrito a mano para que el veredicto sea evidente -------

_SOLO_POSITIVO = '''
"""Banco de la cosa. Comprueba que el motor devuelve lo que se espera, sin
tocar nada del disco y sin dependencias externas."""

def test_suma_dos_mas_dos():
    assert calcular(2, 2) == 4

def test_devuelve_el_nombre():
    assert motor.nombre() == "cosa"
'''

_CON_ASSERT_NEG = '''
def test_rechaza_lo_malo():
    self.assertFalse(motor.valida("basura"))
'''

_CON_ESPERA_CERO = '''
def caso_dos():
    check(len(hallazgos) == 0, "un corpus limpio no produce hallazgos")
'''

_CON_IS_FALSE = '''
def caso_tres():
    check(permitir is False, "BLOQUEA el NIF en el pasaje citado")
'''

_CON_NOT_IN = '''
def caso_cuatro():
    check("census_meta.json" not in texto, "el fichero interno no sale en el informe")
'''

_CON_MARCA = '''
# CN1 · control negativo: un fichero normal no se marca
def caso_cinco():
    assert clasificar("informe.md") == "vivo"
'''

# El literal `_CN_` a secas, SIN la frase "control negativo" ni "CN1" al lado. Sin este
# fixture, una mutacion (quitar `_CN_` de `_RE_MARCA`) no rompia NINGUN test: el unico banco
# del arbol donde se calibro que depende en exclusiva de esta forma exacta no estaba en el
# fichero de etiquetas, y este banco solo probaba la frase larga.
_CON_MARCA_LITERAL_CN = '''
def test_CN_evasion_no_pasa():
    assert intento_evasion() == False
'''

# El nombre `_no_`/`_sin_` a secas, sin ninguna otra senal a su lado (sin assert negativo,
# sin "esto NO", sin marca). Mismo motivo que el fixture de arriba: la mutacion que quitaba
# `_no_`/`_sin_` de `_RE_NOMBRE_NEG` no rompia NINGUN test, porque el unico banco real que
# dependia en exclusiva de esta forma tampoco estaba en las etiquetas. Es la senal que mas
# peso tuvo en el recorte de 77 a 48 del historial, y hasta entonces no tenia ni un caso que
# la aislara.
_CON_NOMBRE_NEG_AISLADO = '''
def test_no_permite_duplicados():
    assert deteccion(entrada) == esperado
'''

_CON_ETIQUETA_TABLA = '''
CASOS = (
    ("NO toca un mensaje que ya esta limpio", "entrada", "entrada"),
    ("limpia la coletilla", "entrada+coletilla", "entrada"),
)
def main():
    for nombre, dentro, fuera in CASOS:
        check(filtrar(dentro) == fuera, nombre)
'''

_CON_VEREDICTO_MALO = '''
class Trampa(unittest.TestCase):
    def test_fuente_caducada(self):
        self.assertEqual(S.estado_de(v), "NO_CONFIA")
'''

_AGREGADOR = '''
"""Lanza todos los bancos de la carpeta y agrega su resultado."""
import glob, subprocess, sys

def main():
    fallos = 0
    for ruta in sorted(glob.glob("run_tests_*.py")):
        r = subprocess.run([sys.executable, ruta])
        if r.returncode != 0:
            fallos += 1
    return 1 if fallos else 0
'''

_PROSA_CON_NO_Y_SIN = '''
"""Banco del productor.

Este banco no depende del disco y funciona sin red. No se apoya en fixtures
inventados: usa la plantilla real del repositorio, porque un fixture sin
relacion con el corpus no prueba nada."""

def test_escribe_el_fichero():
    assert os.path.exists(ruta)
'''


class Senales(unittest.TestCase):
    """CA2 · cada veredicto trae su motivo, y el motivo es el correcto."""

    def test_ca2_assert_negativo(self):
        self.assertIn("ASSERT_NEG", det.senales_de(_CON_ASSERT_NEG))

    def test_ca2_espera_cero(self):
        self.assertIn("ESPERA_CERO", det.senales_de(_CON_ESPERA_CERO))

    def test_ca2_is_false_cuenta_como_espera_cero(self):
        # Entro al etiquetar a mano: `check(permitir is False, ...)` es la forma de cinco
        # casos de un banco real, y la comparacion por `==` no la veia.
        self.assertIn("ESPERA_CERO", det.senales_de(_CON_IS_FALSE))

    def test_ca2_not_in_cuenta_como_espera_cero(self):
        self.assertIn("ESPERA_CERO", det.senales_de(_CON_NOT_IN))

    def test_ca2_marca_explicita(self):
        self.assertIn("MARCA", det.senales_de(_CON_MARCA))

    def test_ca2_marca_literal_cn_aislada(self):
        # Mutacion: quitar `_CN_` de `_RE_MARCA` no rompia NINGUN test de este fichero,
        # porque `_CON_MARCA` de arriba tambien dispara por "CN1" y por la frase larga. Este
        # fixture solo lleva el literal `_CN_`, sin ningun otro camino de la misma senal.
        self.assertIn("MARCA", det.senales_de(_CON_MARCA_LITERAL_CN))

    def test_ca2_nombre_neg_no_sin_aislado(self):
        # Mutacion: quitar `_no_`/`_sin_` de `_RE_NOMBRE_NEG` no rompia NINGUN test de este
        # fichero, y es la senal que mas peso tuvo en el recorte de 77 a 48.
        self.assertIn("NOMBRE_NEG", det.senales_de(_CON_NOMBRE_NEG_AISLADO))

    def test_ca2_etiqueta_en_tabla_lejos_de_su_check(self):
        # La etiqueta del caso vive en una tabla de casos, no en la linea de la llamada.
        self.assertIn("ETIQUETA_NEG", det.senales_de(_CON_ETIQUETA_TABLA))

    def test_ca2_afirmar_el_veredicto_malo(self):
        self.assertIn("ETIQUETA_NEG", det.senales_de(_CON_VEREDICTO_MALO))


class ControlesNegativos(unittest.TestCase):
    """Lo que el detector NO debe marcar. Sin estos, el banco no discrimina."""

    def test_cn1_prosa_con_no_y_sin_no_dispara(self):
        # EL CASO QUE IMPORTA. La v1 miraba «no» y «sin» dentro de cualquier cadena y
        # disparaba en 129 de 129 bancos: en castellano esas dos palabras salen en
        # cualquier docstring. Si esto vuelve a pasar, aqui se pone rojo.
        self.assertEqual(det.senales_de(_PROSA_CON_NO_Y_SIN), [])

    def test_cn2_banco_solo_positivo_no_tiene_control(self):
        self.assertEqual(det.senales_de(_SOLO_POSITIVO), [])

    def test_cn3_un_banco_normal_no_es_agregador(self):
        self.assertFalse(det.es_agregador(_SOLO_POSITIVO))

    def test_cn4_agregador_reconocido(self):
        self.assertTrue(det.es_agregador(_AGREGADOR))

    def test_cn5_un_banco_que_lanza_procesos_pero_juzga_no_es_agregador(self):
        # Un banco puede lanzar un subproceso para ejercitar el binario y seguir teniendo
        # casos propios. Confundirlo con un agregador lo sacaria del recuento en silencio.
        texto = _AGREGADOR + "\n".join("    assert r%d.returncode == 0" % i for i in range(8))
        self.assertFalse(det.es_agregador(texto))


class Puntuacion(unittest.TestCase):
    """CA3 · el detector se mide contra las etiquetas, y sabe decir que discrepa."""

    def test_ca3_concuerda(self):
        res = {"a.py": ["MARCA"], "b.py": []}
        fp, fn, mal, ok = det.puntuar(res, [], {"a.py": "true", "b.py": "false"})
        self.assertEqual((fp, fn, mal, ok), ([], [], [], 2))

    def test_ca3_falso_positivo(self):
        # lo senala como carente y la etiqueta dice que SI lo tiene
        fp, fn, mal, ok = det.puntuar({"a.py": []}, [], {"a.py": "true"})
        self.assertEqual(fp, ["a.py"])
        self.assertEqual(ok, 0)

    def test_ca3_falso_negativo(self):
        fp, fn, mal, ok = det.puntuar({"a.py": ["MARCA"]}, [], {"a.py": "false"})
        self.assertEqual(fn, ["a.py"])

    def test_ca3_agregador_mal_clasificado(self):
        fp, fn, mal, ok = det.puntuar({"a.py": ["MARCA"]}, [], {"a.py": "agregador"})
        self.assertEqual(mal, ["a.py"])

    def test_ca3_etiqueta_de_banco_que_ya_no_existe_se_ignora(self):
        fp, fn, mal, ok = det.puntuar({}, [], {"borrado.py": "true"})
        self.assertEqual((fp, fn, mal, ok), ([], [], [], 0))


class Etiquetas(unittest.TestCase):
    """El fichero de verdad de referencia se lee entero y con sus tres valores."""

    def test_lee_los_tres_valores(self):
        e = det.leer_etiquetas(ETIQUETAS_EJEMPLO)
        self.assertGreaterEqual(len(e), 9, "las etiquetas de este repositorio son 9")
        self.assertIn("true", e.values())
        self.assertIn("false", e.values())
        self.assertIn("agregador", e.values())

    def test_cn6_fichero_de_etiquetas_ausente_devuelve_vacio(self):
        # Sin etiquetas el detector NO puede fingir una puntuacion: devuelve {} y el
        # programa sale con 2. Un instrumento que se autoaprueba sin verdad de referencia
        # es el falso verde que este detector persigue.
        self.assertEqual(det.leer_etiquetas("no_existe_este_fichero.yaml"), {})


class SobreEsteRepo(unittest.TestCase):
    """CA1, CA5 y CA6 sobre el arbol de verdad, que es donde aparecen los defectos."""

    @classmethod
    def setUpClass(cls):
        if not RAIZ:
            raise unittest.SkipTest("fuera de un repositorio git no hay arbol que medir")
        cls.res, cls.agr, cls.exc = det.analizar(RAIZ)

    def test_ca1_el_universo_no_esta_vacio(self):
        self.assertGreaterEqual(len(self.res), 7,
                                "descubrimiento roto: sin universo no hay veredicto")

    def test_ca6_determinista(self):
        segunda, agr2, _ = det.analizar(RAIZ)
        self.assertEqual(self.res, segunda)
        self.assertEqual(self.agr, agr2)

    def test_las_etiquetas_apuntan_a_bancos_que_existen(self):
        # Una etiqueta que ya no corresponde a ningun fichero envejece en silencio y hace
        # que la puntuacion mida menos casos de los que dice.
        vivos = set(self.res) | set(self.agr)
        muertas = [r for r in det.leer_etiquetas(ETIQUETAS_EJEMPLO) if r not in vivos]
        self.assertEqual(muertas, [], "etiquetas sin banco: %s" % muertas)

    def test_todos_los_bancos_de_este_repo_estan_etiquetados(self):
        # Al reves que el anterior, y hace falta: si alguien añade un banco y no lo etiqueta,
        # la puntuacion sigue saliendo perfecta sobre los que ya estaban. Un instrumento que
        # se mide contra una muestra que encoge no se entera de nada.
        etiquetados = set(det.leer_etiquetas(ETIQUETAS_EJEMPLO))
        faltan = sorted((set(self.res) | set(self.agr)) - etiquetados)
        self.assertEqual(faltan, [], "bancos sin etiquetar: %s" % faltan)

    def test_el_detector_concuerda_con_todas_las_etiquetas(self):
        fp, fn, mal, ok = det.puntuar(self.res, self.agr,
                                      det.leer_etiquetas(ETIQUETAS_EJEMPLO))
        self.assertEqual(fp, [], "falsos positivos: %s" % fp)
        self.assertEqual(fn, [], "falsos negativos: %s" % fn)
        self.assertEqual(mal, [], "agregadores mal clasificados: %s" % mal)

    def test_los_bancos_plantados_sin_control_negativo_se_cazan(self):
        # El ejemplo trae dos bancos sin control negativo puestos a proposito. Si el detector
        # deja de verlos, este repositorio deja de demostrar lo que dice demostrar.
        sin = sorted(r for r, s in self.res.items() if not s)
        self.assertEqual(sin, ["ejemplo/bancos/test_prosa_con_no_y_sin.py",
                               "ejemplo/bancos/test_solo_positivo.py"])


class Universo(unittest.TestCase):
    """CA5 · sin universo no hay veredicto, y el universo se pregunta a git."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="detcn_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_ca5_carpeta_sin_versionar_no_da_bancos(self):
        # Fuera de un repositorio, `git ls-files` no devuelve nada y el detector devuelve
        # lista vacia. Lo que NO puede hacer es decir «0 bancos sin control negativo».
        bancos, excluidos = det.bancos_del_repo(self.tmp)
        self.assertEqual((bancos, excluidos), ([], []))

    def test_cn7_raiz_git_no_inventa_una_raiz_donde_no_hay(self):
        # Devolver el directorio actual como si fuera la raiz seria medir otra cosa y no
        # decirlo. Aqui vale `None`, y `main()` sale con 3.
        self.assertIsNone(det.raiz_git(self.tmp))

    @unittest.skipUnless(RAIZ, "fuera de un repositorio git no hay arbol que excluir")
    def test_excluir_saca_las_rutas_declaradas_y_las_cuenta(self):
        # El tercero de los tres numeros de CA1 sale de aqui. Sin este caso, `--excluir`
        # podia dejar de excluir y el informe seguiria pareciendo correcto.
        bancos, excluidos = det.bancos_del_repo(RAIZ, ("/ejemplo/",))
        self.assertTrue(excluidos, "no ha excluido ningun banco de ejemplo/")
        self.assertFalse([b for b in bancos if "/ejemplo/" in "/" + b])


if __name__ == "__main__":
    unittest.main(verbosity=2)
