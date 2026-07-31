# -*- coding: utf-8 -*-
"""verificar_control_negativo.py - cuantos bancos comprueban solo que lo bueno pasa.

Un banco sin control negativo da verde con el codigo bueno y con el roto. Este detector
cuenta cuantos hay, y sobre todo dice CUALES y POR QUE, que es lo que faltaba.

Por que se escribio con verdad de referencia. En el proyecto donde nacio, la cifra fue
112 -> 77 -> 48 -> 31 en cuatro afinados del criterio, y una revision a mano de tres casos
encontro dos falsos positivos. Un numero que solo baja conforme se mira mejor no ha
convergido en ninguna parada anterior, y en las tres primeras se habria actuado sobre el.
Aqui una version nueva del criterio no se juzga por dar menos: se puntua contra un fichero
de etiquetas escrito a mano.

Por eso el codigo de salida habla del INSTRUMENTO y no del repositorio:
    0  el detector concuerda con todas las etiquetas
    1  discrepa de alguna (falso positivo o falso negativo)
    2  no hay etiquetas con las que medirse
    3  no hay universo: ninguna raiz de git, o el descubrimiento no encontro un solo banco

Uso:
    python verificar_control_negativo.py
    python verificar_control_negativo.py --raiz ../mi-repo --etiquetas mis_etiquetas.yaml
    python verificar_control_negativo.py --listar
    python verificar_control_negativo.py --etiquetar
"""
import argparse
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))

# El fichero de etiquetas por defecto vive al lado del script. Si no existe, el programa lo
# dice y sale con 2 en vez de fingir una puntuacion: un instrumento que se autoaprueba sin
# verdad de referencia es el falso verde que este detector persigue.
ETIQUETAS = os.path.join(AQUI, "etiquetas_control_negativo.yaml")

# Nombre, no contenido. Un banco que no se llame asi no entra, y es un suelo declarado.
_RE_BANCO = re.compile(r"(^|/)(test_[^/]*\.py|run_tests[^/]*\.py|[^/]*_test\.py)$")

# --- Las senales. Cada una responde "que reconoce", y el informe dice cual disparo. ---

# La marca explicita con la que un proyecto senala un caso negativo.
_RE_MARCA = re.compile(r"_CN_|control(es)?\s+negativ|\bCN\d|\(CN\)|\bCN\b\s*[:·-]", re.I)

# Aserciones negativas de las librerias estandar.
_RE_ASSERT_NEG = re.compile(
    r"assert(Not|False|Raises|IsNone|IsNot\b)"      # unittest
    r"|pytest\.raises|with\s+raises\("              # pytest
    r"|assert\s+not\s",                             # assert desnudo
    re.I)

# Negativo por SIGNIFICADO: esperar cero, vacio, None o False. Cuenta dentro de `assert`,
# de `check(` o de cualquier envoltorio, porque lo que importa es la forma de la condicion
# y no el nombre de la funcion que la envuelve. Sin esto, un helper propio que envuelve la
# asercion pasaba por banco sin control negativo, y ese fue uno de los dos falsos positivos
# que la revision a mano encontro.
#
# `is False` y `not in` entraron al etiquetar a mano: seis bancos etiquetados como CON
# control negativo lo expresaban asi (`check(permitir is False, "BLOQUEA...")`,
# `check("F" not in filas, ...)`) y la comparacion por `==` no los veia. Cada forma nueva
# de esta lista sale de un caso etiquetado, no de una intuicion.
_RE_ESPERA_CERO = re.compile(
    r"==\s*(0|\[\]|\{\}|None|False|\"\"|'')"
    r"|is\s+(None|False)\b"
    r"|len\([^)]*\)\s*==\s*0"
    r"|\bnot\s+in\b"
    r"|\bnot\s+\w+[\.\[(]",
    re.I)

# La etiqueta del caso, cuando el brazo negativo se declara en el TEXTO y no en el nombre
# de la funcion: `@caso("CA3 sin proposito: resumen intacto (no-regresion)")`,
# `check("los casos de eval NO se marcan", ...)`.
#
# Estrecha a proposito. La primera version miraba cualquier cadena con «no» o «sin» y
# disparaba en el 100 % de los bancos, porque en castellano esas dos palabras salen en
# cualquier docstring. Aqui solo cuentan el «NO» enfatico en mayusculas y las formas
# compuestas que se usan para nombrar un brazo de control.
_RE_ETIQUETA_NEG = re.compile(
    r"\bNO\b(?![_A-Z])"                     # el NO enfatico: "NO tumba", "NO borra"
    r"|no[- ]regresi|no[- ]dano|0-FP"       # nombres propios de este tipo de caso
    r"|\bno\s+(se\s+\w+|cruza|aparece|toca|borra|tumba|rompe|entra|cuenta|marca)\b",
    re.I | re.M)

# Donde vive la etiqueta de un caso. Fuera de estas llamadas, una cadena es prosa.
_RE_SITIO_ETIQUETA = re.compile(r"@?\bcaso\(|\bcheck\(|\b_check\(|\bCA\d", re.I)

# Dos formas mas que NO viven en la linea de la llamada, y por eso van aparte. Cada una
# entro porque un caso ETIQUETADO A MANO la exigia, no porque bajara el recuento:
#
#  · la etiqueta dentro de una tabla de casos, lejos de su `check(`. Estrecha por dos
#    condiciones a la vez: el NO va en MAYUSCULAS (enfatico, deliberado) y le sigue un
#    verbo en minusculas. Dispara en el 59 % de los bancos del arbol donde se calibro.
_RE_NO_ENFATICO = re.compile(r"[\"'][^\"'\n]*\bNO\b\s+[a-zñáéíóúü]{2,}[^\"'\n]*[\"']")
#
#  · afirmar el veredicto MALO: `assertEqual(estado_de(v), "NO_CONFIA")`. Ahi el caso
#    entero es la trampa. Dispara en el 32 %.
_RE_VEREDICTO_MALO = re.compile(
    r"[\"'](NO_\w+|RECHAZ\w*|BLOQUE\w*|INVALID\w*|ROJO|ENFERMO|FALLO|KO)[\"']")

# Nombres de caso que declaran el brazo negativo. SOLO en la firma de la funcion.
#
# La primera version tambien miraba dentro de las cadenas ("...no...", "...sin..."), y
# disparaba en 129 de 129 bancos: en castellano «no» y «sin» salen en cualquier docstring.
# Una senal que marca al 100 % de la poblacion no separa nada, solo baja el recuento, que
# es como se fabricaron los 112 -> 31 del historial de arriba. Se caza porque el informe
# imprime el reparto por senal; con el total a secas habria pasado por buena.
# LAS PALABRAS VAN ANCLADAS A UN TROZO DE NOMBRE, no sueltas dentro de otra palabra.
#
# Antes iban entre dos `\w*` y cazaban por subcadena: `test_protocolo_de_arranque` disparaba porque
# «protocolo» contiene «roto», y `test_invalidate_cache_refreshes` porque «invalidate» contiene
# «invalid». Lo encontro una auditoria independiente el 31/07/2026, y no era un suelo declarado:
# era que la senal con mas peso del recuento daba por cubierto lo que no lo estaba.
#
# SE ANCLA POR LOS DOS LADOS, y el del final es el que costo. Cada palabra tiene que empezar tras
# `_` y terminar donde acaba el trozo de nombre, con sus terminaciones de genero y numero escritas
# una a una. Solo con el ancla de delante, `test_invalidate_cache` seguia disparando: «invalidate»
# empieza tras un guion bajo y ahi el problema estaba al otro lado de la palabra.
_RE_NOMBRE_NEG = re.compile(
    r"def\s+\w*?(?:^|_)(?:no|sin|rechaz(?:a|ar|an|o)?|bloque(?:a|ar|an|o)?|invalid(?:[ao]s?)?|"
    r"fall(?:a|o|an|as|os)?|mal[ao]s?|rot[ao]s?|vaci[ao]s?)(?![a-zA-ZáéíóúñÁÉÍÓÚÑ])", re.I)

# Donde vive una asercion. Se busca la senal de significado SOLO en estas lineas: un `== 0`
# suelto dentro de la construccion del fixture no es un control negativo, es aritmetica.
_RE_SITIO_ASERCION = re.compile(r"\bassert\b|\bcheck\(|\bself\.assert|\braises\(", re.I)

_ORDEN = ("MARCA", "ASSERT_NEG", "ESPERA_CERO", "NOMBRE_NEG", "ETIQUETA_NEG")

# Un agregador no tiene casos propios: descubre otros bancos y los lanza. Contarlo como
# «banco sin control negativo» es contar el objeto equivocado, y cinco de los veinticuatro
# senalados en la primera pasada eran esto. Se reconoce por lo que HACE (lanzar procesos y
# descubrir ficheros de test) unido a no tener sitios de asercion propios.
_RE_LANZA = re.compile(r"subprocess\.(run|Popen|check_)", re.I)
_RE_DESCUBRE = re.compile(r"glob\(|iglob\(|listdir\(|os\.walk\(|rglob\(", re.I)


def raiz_git(desde=None):
    """La raiz del arbol que se mide, preguntada a git. `None` si no hay ninguna.

    Se pregunta y no se deduce contando niveles desde el script: instalada como plugin, la
    skill vive en la cache de Claude Code, lejos de cualquier repositorio, y contar niveles
    habria medido la carpeta equivocada sin decir una palabra.
    """
    try:
        salida = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                cwd=desde or os.getcwd(), capture_output=True,
                                text=True, encoding="utf-8", errors="replace", timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if salida.returncode != 0:
        return None
    return salida.stdout.strip() or None


def bancos_del_repo(raiz, excluir=()):
    """Devuelve (bancos, excluidos). Solo lo versionado: git es la autoridad del universo.

    Que la autoridad sea `git ls-files` y no un paseo por el disco no es un detalle: mide lo
    que el repositorio PUBLICA. Un banco que vive en el arbol de trabajo y nadie ha añadido
    no lo ve nadie mas, y contarlo infla el problema con ficheros que no existen para el
    resto del mundo.
    """
    try:
        salida = subprocess.run(["git", "ls-files"], cwd=raiz, capture_output=True,
                                text=True, encoding="utf-8", errors="replace", timeout=120)
    except (OSError, subprocess.SubprocessError):
        return [], []
    if salida.returncode != 0:
        return [], []
    bancos, excluidos = [], []
    for linea in salida.stdout.splitlines():
        ruta = linea.strip().replace("\\", "/")
        if not ruta or not _RE_BANCO.search(ruta):
            continue
        if any(x in "/" + ruta for x in excluir):
            excluidos.append(ruta)
        else:
            bancos.append(ruta)
    return sorted(bancos), sorted(excluidos)


def es_agregador(texto):
    """¿Este fichero lanza otros bancos en vez de tener casos propios?"""
    if not (_RE_LANZA.search(texto) and _RE_DESCUBRE.search(texto)):
        return False
    sitios = [l for l in texto.splitlines() if _RE_SITIO_ASERCION.search(l)]
    # Los agregadores tienen 0-2 lineas asi (el propio recuento de fallos); un banco con
    # casos propios tiene decenas. El corte se fija por esa distancia, no ajustado a mano.
    return len(sitios) <= 3


def senales_de(texto):
    """Las senales que dispara un banco, en orden. Lista vacia = sin control negativo."""
    encontradas = []
    if _RE_MARCA.search(texto):
        encontradas.append("MARCA")
    sitios = [l for l in texto.splitlines() if _RE_SITIO_ASERCION.search(l)]
    unidos = "\n".join(sitios)
    if _RE_ASSERT_NEG.search(unidos):
        encontradas.append("ASSERT_NEG")
    if _RE_ESPERA_CERO.search(unidos):
        encontradas.append("ESPERA_CERO")
    if _RE_NOMBRE_NEG.search(texto):
        encontradas.append("NOMBRE_NEG")
    etiquetas = "\n".join(l for l in texto.splitlines() if _RE_SITIO_ETIQUETA.search(l))
    if (_RE_ETIQUETA_NEG.search(etiquetas)
            or _RE_NO_ENFATICO.search(texto)
            or _RE_VEREDICTO_MALO.search(texto)):
        encontradas.append("ETIQUETA_NEG")
    return [s for s in _ORDEN if s in encontradas]


def analizar(raiz, excluir=()):
    """({ruta: [senales]}, agregadores, excluidos) para el universo de bancos."""
    bancos, excluidos = bancos_del_repo(raiz, excluir)
    resultado, agregadores = {}, []
    for ruta in bancos:
        completa = os.path.join(raiz, ruta)
        try:
            with open(completa, encoding="utf-8", errors="replace") as fh:
                texto = fh.read()
        except (OSError, IOError):
            texto = ""
        if es_agregador(texto):
            agregadores.append(ruta)
        else:
            resultado[ruta] = senales_de(texto)
    return resultado, agregadores, excluidos


# --- La verdad de referencia -------------------------------------------------------------

def leer_etiquetas(path=ETIQUETAS):
    """Lector minimo del YAML de etiquetas: {ruta: 'true'|'false'|'agregador'}.

    A mano y no con PyYAML a proposito: el fichero es una lista plana de tres campos y esta
    herramienta no debe arrastrar una dependencia por eso. Si el formato crece, se cambia.
    """
    if not os.path.isfile(path):
        return {}
    etiquetas, actual = {}, None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            l = linea.strip()
            if l.startswith("- banco:"):
                actual = l.split(":", 1)[1].strip().strip("\"'")
            elif l.startswith("tiene_control_negativo:") and actual:
                valor = l.split(":", 1)[1].strip().lower()
                # Se corta el comentario de la plantilla ANTES de juzgar el valor, para que
                # `true   # true | false | agregador` valga y `# true | false` a secas no.
                valor = valor.split("#", 1)[0].strip()
                clave = actual.replace("\\", "/")
                actual = None
                if valor.startswith("agregador"):
                    etiquetas[clave] = "agregador"
                elif valor in ("true", "si", "sí", "yes"):
                    etiquetas[clave] = "true"
                elif valor in ("false", "no", "not"):
                    etiquetas[clave] = "false"
                else:
                    # SE PARA. Antes cualquier valor no reconocido pasaba a `false` en silencio,
                    # asi que la plantilla sin rellenar y la palabra `verdadero` envenenaban la
                    # verdad de referencia, el detector salia con 1, y el programa aconsejaba
                    # arreglar el criterio cuando lo roto era el fichero de etiquetas. Lo encontro
                    # una auditoria independiente el 31/07/2026, y era la incoherencia mas grave
                    # del repositorio: la tesis entera de esta herramienta es fallar cerrado.
                    raise ValueError(
                        "etiqueta ilegible en %s, banco %s: %r no es un valor valido. "
                        "Los validos son true/si/yes, false/no y agregador. Una etiqueta que no "
                        "se entiende no se convierte en 'false': se para, porque de ahi sale la "
                        "verdad con la que se puntua el detector."
                        % (path, clave, valor or "(vacio)"))
    return etiquetas


def puntuar(resultado, agregadores, etiquetas):
    """Compara el detector con las etiquetas.

    Devuelve (falsos_pos, falsos_neg, mal_clasificados_agregador, acuerdos).
      falso POSITIVO del hallazgo = lo senala como carente y SI tiene control negativo.
      falso NEGATIVO = lo da por bueno y NO lo tiene.
    """
    fp, fn, mal_agr, ok = [], [], [], 0
    for ruta, verdad in etiquetas.items():
        if ruta not in resultado and ruta not in agregadores:
            continue
        if verdad == "agregador":
            if ruta in agregadores:
                ok += 1
            else:
                mal_agr.append(ruta)
            continue
        if ruta in agregadores:
            mal_agr.append(ruta)          # lo llama agregador y tiene casos propios
            continue
        detectado = bool(resultado[ruta])
        if detectado == (verdad == "true"):
            ok += 1
        elif verdad == "true":
            fp.append(ruta)
        else:
            fn.append(ruta)
    return fp, fn, mal_agr, ok


def _informe(resultado, agregadores, excluidos, excluir, listar):
    sin = sorted(r for r, s in resultado.items() if not s)
    con = sorted(r for r, s in resultado.items() if s)

    print("=" * 78)
    print("BANCOS SIN CONTROL NEGATIVO")
    print("=" * 78)
    # Los tres numeros, siempre. Dar el primero solo hace que parezca mas firme de lo que es.
    print("  bancos con casos propios .. %d" % len(resultado))
    print("  agregadores ............... %d  (lanzan otros bancos; no tienen casos que juzgar)"
          % len(agregadores))
    print("  excluidos a proposito ..... %d  %s"
          % (len(excluidos),
             "(--excluir %s)" % " ".join(excluir) if excluir else "(no se ha pasado --excluir)"))
    print("  criterio del universo ..... versionado en git + nombre test_*/run_tests*/*_test")
    print()
    print("  con control negativo ...... %d" % len(con))
    print("  SIN control negativo ...... %d" % len(sin))

    reparto = {}
    for senales in resultado.values():
        for s in senales:
            reparto[s] = reparto.get(s, 0) + 1
    if reparto:
        print("  senal que dispara ......... "
              + " | ".join("%s %d" % (k, reparto[k]) for k in _ORDEN if k in reparto))

    if listar:
        print("\n  -- SIN control negativo (revisar a mano antes de creerselo) --")
        for r in sin:
            print("     %s" % r)
        print("\n  -- con control negativo, y por que --")
        for r in con:
            print("     %-58s %s" % (r, ",".join(resultado[r])))
    return sin


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Cuenta los bancos de pruebas que solo comprueban que lo bueno pasa.")
    ap.add_argument("--raiz", metavar="RUTA",
                    help="el arbol a medir; por defecto, la raiz git del directorio actual")
    ap.add_argument("--etiquetas", metavar="FICHERO", default=ETIQUETAS,
                    help="la verdad de referencia con la que se puntua el detector")
    ap.add_argument("--excluir", metavar="SUBCADENA", action="append", default=[],
                    help="deja fuera las rutas que contengan esta subcadena (repetible)")
    ap.add_argument("--listar", action="store_true", help="imprime cada banco con su veredicto")
    ap.add_argument("--etiquetar", action="store_true",
                    help="plantilla YAML de los bancos que aun no tienen etiqueta")
    args = ap.parse_args(argv)

    raiz = args.raiz or raiz_git()
    if not raiz:
        print("ERROR: no hay ninguna raiz de git desde aqui, asi que no hay universo.")
        print("       Pasa --raiz RUTA con el arbol que quieres medir.")
        return 3

    resultado, agregadores, excluidos = analizar(raiz, tuple(args.excluir))
    if not resultado:
        # Cero bancos no es "cero problemas", es que el descubrimiento no funciono.
        print("ERROR: el descubrimiento no encontro ningun banco en %s" % raiz)
        print("       Sin universo no hay veredicto: decir '0 sin control negativo' aqui")
        print("       seria el falso verde de manual.")
        return 3

    etiquetas = leer_etiquetas(args.etiquetas)
    sin = _informe(resultado, agregadores, excluidos, args.excluir, args.listar)

    if args.etiquetar:
        print("\n  -- sin etiquetar (pegar en el fichero de etiquetas) --")
        for r in sorted(resultado):
            if r not in etiquetas:
                print("  - banco: %s" % r)
                print("    tiene_control_negativo:   # true | false")
                print("    evidencia: \"\"")
        return 2 if not etiquetas else 0

    print("\n" + "-" * 78)
    if not etiquetas:
        print("  SIN VERDAD DE REFERENCIA: no hay etiquetas con las que medir el detector.")
        print("  El recuento de arriba es una aproximacion sin puntuar. No se actua sobre el.")
        print("  Etiqueta con --etiquetar antes de darle peso a la cifra.")
        return 2

    fp, fn, mal_agr, ok = puntuar(resultado, agregadores, etiquetas)
    total = ok + len(fp) + len(fn) + len(mal_agr)
    print("  EL DETECTOR CONTRA LAS ETIQUETAS  (%d etiquetadas de %d bancos)"
          % (len(etiquetas), len(resultado) + len(agregadores)))
    print("    concuerda ............... %d de %d" % (ok, total))
    for r in fp:
        print("    [FALSO POSITIVO] lo senala y SI tiene control negativo: %s" % r)
    for r in fn:
        print("    [FALSO NEGATIVO] lo deja pasar y NO lo tiene:           %s" % r)
    for r in mal_agr:
        print("    [AGREGADOR MAL CLASIFICADO]                             %s" % r)

    if fp or fn or mal_agr:
        print("\n  >> El detector DISCREPA de las etiquetas. Se arregla el criterio, no la")
        print("     etiqueta: adaptar la verdad de referencia al instrumento es lo unico")
        print("     que esta prohibido de raiz.")
        return 1

    print("\n  >> El detector concuerda con todas las etiquetas.")
    print("     Bancos sin control negativo hoy: %d de %d." % (len(sin), len(resultado)))
    print("     La cifra se REPORTA y no tumba nada: en el arbol donde nacio bajo de 112 a")
    print("     ~10 en cinco pasadas, o sea que actuar sobre ella sin anclarla sale caro.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
