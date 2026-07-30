# -*- coding: utf-8 -*-
"""mutar.py - sabotea el detector a proposito y comprueba que su banco se pone rojo.

POR QUE EXISTE. Un banco verde solo demuestra que el codigo pasa SUS casos. No demuestra que
el banco sepa distinguir el codigo bueno del roto, y esa es otra pregunta. La unica forma de
contestarla es romper el codigo a mano y mirar si alguien se queja.

Aqui no es teorico. Cuatro mutaciones al detector, antes de publicarlo, dieron este reparto:
la logica mas critica aguantaba, y DOS senales tenian un agujero real. Al borrar el literal
`_CN_` del reconocimiento de la marca, y al borrar los nombres `_no_`/`_sin_`, no caia NI UN
test: cada una de esas dos formas dependia en exclusiva de un unico banco del arbol privado, y
ninguno de los dos estaba en el fichero de etiquetas. Un banco de 24 casos, verde, y dos lineas
del criterio que cualquiera podia borrar sin que nadie se enterase. El banco crecio a 26 casos
por eso, con un fixture que aisla cada una de las dos formas, y esos dos casos son los que aqui
se comprueban.

EL MUTADOR FALLA CERRADO, y es la parte que mas facil se hace mal. Si el ancla de una mutacion
no aparece en el fichero (porque alguien renombro una constante), esa mutacion no se aplica, y
un mutador ingenuo la contaria como «cazada» sin haber cambiado una coma. Aqui eso sale con
ERROR y tumba la ejecucion: un arnes que aprueba sin haber mordido no es un arnes.

Uso:
    python mutar.py
    python mutar.py --ver 3      # imprime la salida del banco para la mutacion 3
"""
import argparse
import os
import shutil
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
OBJETIVO = os.path.join(AQUI, "verificar_control_negativo.py")
BANCO = os.path.join(AQUI, "test_detector_control_negativo.py")

# La copia intacta vive en DISCO y no en la memoria de este programa. Si alguien mata el
# proceso a mitad, la ejecucion siguiente repara desde aqui en vez de dejar el detector
# saboteado para siempre.
INTACTO = OBJETIVO + ".intacto"

# (id, que rompe, ancla, sustitucion, quien deberia cazarlo)
MUTACIONES = [
    (1, "borra el literal `_CN_` del reconocimiento de la marca",
     'r"_CN_|control(es)?', 'r"control(es)?',
     "test_ca2_marca_literal_cn_aislada"),

    (2, "borra los nombres `_no_` y `_sin_` de la senal de nombre",
     r"(_no_|_sin_|rechaz", r"(rechaz",
     "test_ca2_nombre_neg_no_sin_aislado"),

    (3, "deja de reconocer los agregadores, que fue el fallo de la primera pasada",
     "    return len(sitios) <= 3", "    return False",
     "test_cn4_agregador_reconocido y el acuerdo con las etiquetas"),

    (4, "ensancha la senal de etiqueta a cualquier «no» o «sin», que es la v1 que marcaba 129 de 129",
     '_RE_NO_ENFATICO = re.compile(r"[\\"\'][^\\"\'\\n]*\\bNO\\b\\s+[a-zñáéíóúü]{2,}[^\\"\'\\n]*[\\"\']")',
     '_RE_NO_ENFATICO = re.compile(r"\\bno\\b|\\bsin\\b", re.I)',
     "test_cn1_prosa_con_no_y_sin_no_dispara"),

    (5, "borra `is False` de la senal de significado",
     r"|is\s+(None|False)\b", r"|is\s+(None)\b",
     "test_ca2_is_false_cuenta_como_espera_cero"),

    (6, "inventa una raiz donde no hay repositorio, en vez de devolver None",
     "    if salida.returncode != 0:\n        return None\n    return salida.stdout.strip() or None",
     "    if salida.returncode != 0:\n        return desde or os.getcwd()\n    return salida.stdout.strip() or os.getcwd()",
     "test_cn7_raiz_git_no_inventa_una_raiz_donde_no_hay"),
]


def _leer(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _escribir(path, texto):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(texto)


def _lanzar_banco():
    """Devuelve (codigo, salida). El banco se lanza como proceso aparte para que importe la
    version saboteada del modulo y no la que este programa ya tenga cargada."""
    r = subprocess.run([sys.executable, "-B", BANCO], cwd=AQUI,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Sabotea el detector y exige que su banco caiga.")
    ap.add_argument("--ver", type=int, metavar="N",
                    help="imprime la salida del banco para la mutacion N")
    args = ap.parse_args(argv)

    # Reparacion de arranque: si quedo una copia intacta de una ejecucion muerta a mitad, el
    # fichero de trabajo esta saboteado y hay que devolverlo antes de medir nada.
    if os.path.isfile(INTACTO):
        print("  (habia una copia intacta de una ejecucion anterior: reparando el objetivo)")
        shutil.copyfile(INTACTO, OBJETIVO)
        os.remove(INTACTO)

    original = _leer(OBJETIVO)

    print("=" * 78)
    print("MUTACION  --  %d sabotajes contra el banco del detector" % len(MUTACIONES))
    print("=" * 78)

    # EL CONTROL NULO, primero y sin excepcion. Si el banco ya esta rojo sin tocar nada, todo
    # lo de abajo mide otra cosa y el aval no vale.
    codigo, salida = _lanzar_banco()
    if codigo != 0:
        print("  CONTROL NULO EN ROJO: el banco falla sin ninguna mutacion.")
        print("  Sin banco verde de partida no se puede avalar nada. Sale con 2.")
        print(salida[-2000:])
        return 2
    print("  control nulo ..... el banco esta verde antes de tocar nada")
    print()

    cazadas, escapadas, errores = 0, [], []
    shutil.copyfile(OBJETIVO, INTACTO)
    try:
        for num, que, ancla, sustituto, quien in MUTACIONES:
            if ancla not in original:
                # FALLA CERRADO. Una mutacion que no muerde no es una mutacion cazada.
                errores.append((num, que))
                print("  %d. ERROR: el ancla no aparece en el fichero, la mutacion NO se aplico"
                      % num)
                print("     %s" % que)
                continue
            mutado = original.replace(ancla, sustituto, 1)
            if mutado == original:
                errores.append((num, que))
                print("  %d. ERROR: la sustitucion no cambio nada" % num)
                continue
            _escribir(OBJETIVO, mutado)
            codigo, salida = _lanzar_banco()
            if args.ver == num:
                print(salida)
            if codigo != 0:
                cazadas += 1
                print("  %d. CAZADA   %s" % (num, que))
                print("             lo caza: %s" % quien)
            else:
                escapadas.append((num, que, quien))
                print("  %d. ESCAPA   %s" % (num, que))
                print("             deberia cazarla: %s" % quien)
    finally:
        _escribir(OBJETIVO, original)
        if os.path.isfile(INTACTO):
            os.remove(INTACTO)

    print()
    print("-" * 78)
    print("  cazadas %d de %d   escapadas %d   errores del mutador %d"
          % (cazadas, len(MUTACIONES), len(escapadas), len(errores)))

    if errores:
        print()
        print("  >> HAY MUTACIONES QUE NO SE APLICARON. El resultado de arriba no avala nada:")
        print("     un sabotaje que no muerde no demuestra que el banco vigile esa linea.")
        return 1

    if escapadas:
        print()
        print("  >> SABOTAJES QUE PASAN CALLANDO:")
        for num, que, quien in escapadas:
            print("     %d. %s" % (num, que))
        print()
        print("     Un sabotaje que nadie caza no es un fallo del codigo: es una linea que el")
        print("     banco no vigila. Se arregla añadiendo el caso que falta, no el codigo.")
        return 1

    print()
    print("  >> Los %d sabotajes se cazan, sin un hueco. El fichero medido queda restaurado."
          % len(MUTACIONES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
