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

Y DEVUELVE EL FICHERO BYTE A BYTE, que hasta el 30/07/2026 no hacia. Leia con saltos de linea
universales y escribia con `newline=""`, asi que en un clon de Windows (`core.autocrlf=true`)
la restauracion dejaba 387 lineas en LF sobre un fichero que estaba en CRLF: 18.362 bytes
antes, 17.975 despues, y `git status` marcando el detector como modificado. Este es el segundo
comando que manda ejecutar el README, y la primera comprobacion del gate de publicacion es
«arbol limpio», o sea que el gate se ponia rojo por hacer lo que el README pide. Ahora la copia
va y vuelve en binario y la restauracion se RELEE para exigirla byte a byte antes de anunciarla:
la unica forma de que «queda restaurado» no sea una promesa es comprobarlo.

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
# saboteado para siempre. Va declarada en `.gitignore` (`*.intacto`): es un fichero de trabajo
# de esta herramienta, y sin declararla disparaba ella sola la comprobacion de «arbol limpio»
# del gate de publicacion. Que una ejecucion se haya muerto a mitad ya lo canta el objetivo
# saliendo como modificado, asi que la copia no aportaba esa senal, solo el falso rojo.
INTACTO = OBJETIVO + ".intacto"

# (id, que rompe, ancla, sustitucion, quien deberia cazarlo)
MUTACIONES = [
    (1, "borra el literal `_CN_` del reconocimiento de la marca",
     'r"_CN_|control(es)?', 'r"control(es)?',
     "test_ca2_marca_literal_cn_aislada"),

    # El ancla se reescribio el 31/07/2026 al anclar las palabras por los dos lados. La vieja
    # (`(_no_|_sin_|rechaz`) dejo de aparecer en el fichero y el mutador lo canto en vez de dar por
    # cazada una mutacion que nunca se aplico, que es justo su contrato.
    (2, "borra los nombres `no` y `sin` de la senal de nombre",
     r"(?:no|sin|rechaz", r"(?:rechaz",
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


# EL FICHERO MEDIDO SE MANEJA EN BINARIO. La copia buena son los bytes tal cual, y de ahi sale
# todo lo demas. La via de texto era la que perdia los finales de linea, y con una funcion que
# lee texto no hay manera de restaurar lo que habia: cuando llega el momento de escribir, la
# informacion ya se perdio al leer.
def _leer_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def _escribir_bytes(path, datos):
    with open(path, "wb") as fh:
        fh.write(datos)


def _texto_y_salto(datos):
    """El contenido con los saltos normalizados, y el salto de linea que traia el fichero.

    Las dos cosas, y por separado, porque cada una hace falta para algo distinto. Las anclas de
    las mutaciones estan escritas con el salto en `\\n`, asi que la busqueda tiene que ir sobre
    texto normalizado o en un clon de Windows no encontraria ninguna y las seis saldrian como
    «el ancla no aparece en el fichero». La escritura, en cambio, tiene que devolver el salto que
    habia.
    """
    texto = datos.decode("utf-8")
    salto = "\r\n" if "\r\n" in texto else "\n"
    return texto.replace("\r\n", "\n"), salto


def _a_bytes(texto, salto):
    """El texto de vuelta a los bytes que tocan, con el salto original.

    Sirve para la restauracion y tambien para el fichero SABOTEADO. Si la mutacion cambiara
    ademas los 387 finales de linea, un `git diff` durante la ejecucion (o despues de una que se
    muera a mitad) saldria con el fichero entero cambiado y ahi no se ve cual era el sabotaje.
    """
    return texto.replace("\n", salto).encode("utf-8")


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

    original_bytes = _leer_bytes(OBJETIVO)
    original, salto = _texto_y_salto(original_bytes)

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
            _escribir_bytes(OBJETIVO, _a_bytes(mutado, salto))
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
        _escribir_bytes(OBJETIVO, original_bytes)
        if os.path.isfile(INTACTO):
            os.remove(INTACTO)

    # LA RESTAURACION SE COMPRUEBA ANTES DE ANUNCIARLA. Este programa imprimia «el fichero medido
    # queda restaurado» sin haberlo mirado, y durante meses fue mentira en Windows. Releer el
    # fichero cuesta un `open` y convierte la frase de abajo en un hecho.
    devuelto = _leer_bytes(OBJETIVO)
    if devuelto != original_bytes:
        print()
        print("  >> LA RESTAURACION NO DEVOLVIO EL FICHERO BYTE A BYTE: %d bytes antes, %d ahora."
              % (len(original_bytes), len(devuelto)))
        print("     El recuento de mutaciones no se publica, porque el fichero medido no es el")
        print("     que habia. Devuelvelo con: git checkout -- %s" % os.path.basename(OBJETIVO))
        return 2

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
    print("  >> Los %d sabotajes se cazan, sin un hueco. El fichero medido queda restaurado byte"
          " a byte, y comprobado." % len(MUTACIONES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
