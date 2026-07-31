# detector-control-negativo

**Tu suite de pruebas está verde. La pregunta que nadie hace es si esa suite sabría ponerse roja.
Un banco que solo comprueba que lo bueno pasa aprueba igual al código bueno y al roto. Esta
herramienta cuenta cuántos hay así en un repositorio, dice cuáles y por qué. Y se puntúa a sí
misma contra un conjunto etiquetado a mano antes de opinar de nadie.**

![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)
![sin dependencias](https://img.shields.io/badge/dependencias-ninguna-brightgreen)
![38 casos](https://img.shields.io/badge/banco-38%20casos-brightgreen)
![mutación 6/6](https://img.shields.io/badge/mutaci%C3%B3n-6%2F6-brightgreen)
![licencia MIT](https://img.shields.io/badge/licencia-MIT-lightgrey)

Esto es lo que devuelve, sobre el árbol de este mismo repositorio y sin preparar nada:

```
python skills/detector-control-negativo/verificar_control_negativo.py --etiquetas ejemplo/etiquetas_ejemplo.yaml --listar
```

```
==============================================================================
BANCOS SIN CONTROL NEGATIVO
==============================================================================
  bancos con casos propios .. 8
  agregadores ............... 1  (lanzan otros bancos; no tienen casos que juzgar)
  excluidos a proposito ..... 0  (no se ha pasado --excluir)
  criterio del universo ..... versionado en git + nombre test_*/run_tests*/*_test

  con control negativo ...... 6
  SIN control negativo ...... 2
  senal que dispara ......... MARCA 2 | ASSERT_NEG 2 | ESPERA_CERO 2 | NOMBRE_NEG 3 | ETIQUETA_NEG 2

  -- SIN control negativo (revisar a mano antes de creerselo) --
     ejemplo/bancos/test_prosa_con_no_y_sin.py
     ejemplo/bancos/test_solo_positivo.py

  -- con control negativo, y por que --
     ejemplo/bancos/test_assert_negativo.py                     ASSERT_NEG,NOMBRE_NEG
     ejemplo/bancos/test_espera_cero.py                         ESPERA_CERO
     ejemplo/bancos/test_marca_cn.py                            MARCA
     ejemplo/bancos/test_nombre_negativo_aislado.py             NOMBRE_NEG
     ejemplo/bancos/test_veredicto_malo.py                      ETIQUETA_NEG
     skills/detector-control-negativo/test_detector_control_negativo.py MARCA,ASSERT_NEG,ESPERA_CERO,NOMBRE_NEG,ETIQUETA_NEG

------------------------------------------------------------------------------
  EL DETECTOR CONTRA LAS ETIQUETAS  (9 etiquetadas de 9 bancos)
    concuerda ............... 9 de 9

  >> El detector concuerda con todas las etiquetas.
     Bancos sin control negativo hoy: 2 de 8.
     La cifra se REPORTA y no tumba nada: en el arbol donde nacio bajo de 112 a
     ~10 en cinco pasadas, o sea que actuar sobre ella sin anclarla sale caro.
```

Ese bloque son las 32 líneas que imprime el comando, sin quitar ninguna. Las dos últimas las dice el
propio programa en cada ejecución, para que la advertencia no dependa de que alguien se acuerde de
escribirla. Recortarlas al pegar la salida deja el recuento con más autoridad de la que tiene.

**Los ocho bancos de `ejemplo/bancos/` están plantados a propósito, uno a uno, con su etiqueta al
lado.** Dos sin brazo negativo, que son los dos que el informe señala; cinco con brazo negativo,
uno por cada señal; y un agregador, para el tercer valor de la etiqueta. El noveno banco del
universo es el de la propia herramienta. Ese «2 de 8» describe un árbol de juguete, construido para
que cada veredicto se pueda comprobar leyendo el fichero. De la calidad de los tests de nadie no
dice nada.

Son el material que el detector MIDE, así que varias de esas fixtures invocan símbolos que no
existen a propósito y se caerían si alguien las ejecutara como pruebas. Se llaman `test_*.py` porque
el criterio del detector es el nombre del fichero, y renombrarlas las sacaría de su propia medición.
La exclusión vive en `conftest.py`: hoy `python -m pytest -q` sobre este repositorio recoge las 38
pruebas del banco del detector y sale verde sin tocar una sola fixture.

[Español](#español) · [English](#english)

---

## Español

### El problema

Una suite verde demuestra que el código pasa sus casos. No demuestra que la suite sepa separar el
código bueno del roto.

Esa es otra pregunta.

El caso más común es un banco que comprueba solo el camino bueno: se le pasa una entrada
correcta, se comprueba que sale el resultado correcto y ahí acaba. Ese banco da verde. Y sigue
dando verde cuando alguien rompe la validación de entrada, porque nadie le pregunta nunca qué
hace con una entrada mala. En la jerga es un banco sin **control negativo**: le falta el caso que
afirma lo que la herramienta debe rechazar, bloquear, dejar vacío o marcar como inválido.

Contar cuántos bancos están en ese estado parece un ejercicio de una tarde. Lo intentamos y salió
así:

| versión del criterio | qué añadió | bancos sin control negativo |
|---|---|---:|
| v1 | la marca explícita del proyecto | 112 de 131 |
| v2 | `assertNot*`, `assertFalse`, `assertRaises` | 77 |
| v3 | esperar cero, lista vacía, nombres `_no_` y `_sin_` | 48 |
| v4 | el helper propio que envuelve la aserción | 31 |
| revisión a mano | 3 casos abiertos, 2 tenían control negativo | ~10 |
| criterio de hoy, puntuado contra 30 etiquetas | el instrumento de este repositorio | 3 de 131 |

**La última fila es una parada más de la serie y no su conclusión. Por eso está aquí abajo y no en
la portada.** Se midió el 30/07/2026 a las 15:04 sobre ese mismo árbol privado, en su commit
`e86c67d`, con este comando:

```bash
python skills/detector-control-negativo/verificar_control_negativo.py \
  --raiz <la raiz de ese arbol privado> \
  --excluir /candidato_repo/ \
  --etiquetas etiquetas_control_negativo.yaml
```

Los tres bancos son `Aplicaciones/05_capa_confianza_rag/suite_aceptacion/test_c11_determinismo.py`,
`evals/run_tests_contrato_skills.py` y
`pipeline/eval_suite/evaluador/test_clasificador_motivo.py`. Van con la cifra porque un 3 a secas
no se puede auditar.

Tres cosas que hay que saber para leer esa fila, ninguna de ellas un detalle:

1. **Ese comando no lo puede teclear quien lea esto.** El árbol es privado y no viaja en el
   repositorio. Lo que se publica es el método en vez de un resultado comprobable desde fuera.
2. **Sin `--excluir /candidato_repo/` el mismo comando sobre el mismo árbol devuelve 134 y no
   131.** En el árbol privado esa exclusión es una constante dentro del script y sale sola; el
   instrumento que se publica la pide por bandera. Una exclusión que se sobreentiende cambia el
   denominador sin dejar rastro.
3. **Los dos «131» de la tabla no son el mismo objeto.** El de la fila v1 es el universo sin
   separar: aquel día los agregadores iban dentro y la exclusión no existía. El de la última fila
   son 131 bancos con casos propios **más** 5 agregadores **más** 3 excluidos. Y el denominador se
   movió ese mismo día: entraron tres bancos al árbol a las 12:34, a las 13:02 y a las 14:18.

**Ninguna versión estaba mal programada.** Cada afinado medía un objeto distinto y cada uno daba
menos que el anterior. Una cifra que solo baja conforme se mira mejor no ha convergido en ninguna
parada anterior: en las tres primeras se habría actuado sobre ella, y la primera habría declarado
un problema diez veces mayor que el real. Encima, el script de aquel día no quedó en disco, así
que volver a preguntar la cifra obligaba a repetir la investigación entera.

De ahí salen los dos requisitos que ordenan esta herramienta: **el contador vive en disco**, y
**el criterio se puntúa contra una verdad de referencia** en vez de juzgarse por el tamaño de su
resultado.

### La pieza que la diferencia de un contador cualquiera

Un fichero de etiquetas escrito a mano, abriendo cada banco, con tres campos por entrada:

```yaml
  - banco: ejemplo/bancos/test_veredicto_malo.py
    tiene_control_negativo: true
    evidencia: "assertEqual(estado_de(fuente_caducada()), \"NO_CONFIA\"): afirma el veredicto malo"
    etiquetado_el: 2026-07-30
```

Con eso, una versión nueva del criterio **ya no se juzga por dar un número más pequeño**: se
puntúa. Se cuentan los falsos positivos (los que señala y sí tenían control negativo) y los
falsos negativos (los que da por buenos y no lo tienen). Un criterio que baja el titular subiendo
los falsos negativos es peor, aunque el titular quede mejor.

Y la etiqueta se escribe **antes** de afinar el criterio, a propósito. Al revés, la etiqueta se
acomoda al instrumento y la medición deja de valer.

`tiene_control_negativo` tiene un tercer valor, `agregador`. No es un adorno: hay ficheros que
se llaman como un banco y no tienen un solo caso propio, porque descubren otros y los lanzan.
Contarlos entre los carentes es contar el objeto equivocado. En la primera pasada cinco de los
veinticuatro señalados eran justo eso.

### Por eso el código de salida no habla del repositorio

| salida | qué significa |
|---|---|
| `0` | el detector concuerda con todas las etiquetas |
| `1` | discrepa de alguna: hay un falso positivo o un falso negativo |
| `2` | no hay etiquetas con las que medirse, así que no se puntúa |
| `3` | no hay universo: ninguna raíz de git, o cero bancos encontrados |

**El recuento de bancos se reporta y no tumba nada.** Es la consecuencia directa de la tabla de
arriba: actuar sobre una cifra que no ha convergido es el error que esta herramienta existe para
no repetir. Quien quiera un umbral que bloquee, lo pone él y sabiendo lo que hace.

Y el `3` es igual de deliberado. Fuera de un repositorio de git no hay universo, y decir «0
bancos sin control negativo» ahí sería el falso verde de manual: el mensaje más tranquilizador
posible producido por no haber mirado nada.

### Por qué cada señal es estrecha

| señal | qué reconoce |
|---|---|
| `MARCA` | la marca explícita: `_CN_`, «control negativo», «CN1» |
| `ASSERT_NEG` | `assertNot*`, `assertFalse`, `assertRaises`, `pytest.raises`, `assert not` |
| `ESPERA_CERO` | esperar `0`, `[]`, `{}`, `None`, `False`, `is False`, `not in` |
| `NOMBRE_NEG` | nombres de caso con `_no_`, `_sin_`, `rechaza`, `bloquea`, `falla`, `invalido` |
| `ETIQUETA_NEG` | la etiqueta del caso declara el brazo negativo, o afirma el veredicto malo |

Basta una para que el banco cuente como cubierto.

Dos precauciones que costaron tiempo y viven dentro del código:

**`ESPERA_CERO` mira la forma de la condición y no el nombre de la función que la envuelve.** Un
proyecto con su propio helper (`check(...)`) no tiene un solo `assertFalse` en todo el árbol, y
sin esta señal sus bancos salían como carentes. Fue uno de los dos falsos positivos que destapó
la revisión a mano.

**Las señales de texto se buscan donde toca y no en cualquier cadena.** La primera versión
miraba «no» y «sin» dentro de todo el fichero y **disparaba en 129 bancos de 129**. Una señal que
marca al 100 % de la población no separa nada: solo baja el recuento, que es como se fabrica una
cifra que parece mejor y mide peor. Se cazó porque el informe imprime el reparto por señal; con
el total a secas habría pasado por buena.

### La historia honesta: cuatro mutaciones antes de publicar

Antes de preparar este repositorio se le pasaron **cuatro mutaciones al propio detector**, cada
una verificada mordida a mordida **antes** de mirar qué decía el banco. Es lo contrario de
presumir de suite verde: se rompe el código a mano y se mira si alguien se queja.

- Dos mordieron limpio. Al romper el reconocimiento de agregadores (el fallo que en la primera
  pasada confundió 5 de 24) cayó el caso que compara el detector con las etiquetas y cayó
  señalando con nombre y apellido el banco mal clasificado.
- Dos no rompieron nada. Ahí estaba el agujero. Al borrar el literal `_CN_` del
  reconocimiento de la marca y al borrar los nombres `_no_` y `_sin_` de la señal de nombre,
  **no cayó ni un test**. Cada una de esas dos formas dependía en exclusiva de un único banco del
  árbol medido. Ninguno de esos dos bancos estaba en el fichero de etiquetas. Un banco de 24
  casos, verde, con dos líneas del criterio que cualquiera podía borrar mañana sin que nadie se
  enterase. La señal de nombre no es un detalle: es la que más peso tiene en el recuento.

Se cerró antes de tocar el repositorio, con **dos casos nuevos que aíslan cada una de las dos
formas** de cualquier otra señal que pudiera taparlas.

El banco pasó de 24 a 26 casos.

Los cuatro que faltan hasta 30 los añadió el empaquetado. Los dos últimos, hasta los 32 de hoy,
entraron al vigilar el censo de fixtures y la restauración del mutador. Cada uno cubre una pieza
que en el árbol privado no existía o estaba clavada dentro del script: que los bancos plantados a
propósito se cacen, que ningún banco de este repositorio se quede sin etiqueta, que la raíz de git
no se invente cuando no hay ninguna y que la exclusión declarada saque las rutas y las cuente
aparte. El comando de verificación de más abajo los enumera al ejecutarse.

### Lo que la mutación 6 de 6 no vio

El día de publicar había tres verdes. El banco en 32. La mutación en 6 de 6. El acuerdo con las
etiquetas en 9 de 9. Se le pidió entonces a un auditor externo que buscara con material que **no
estaba en el banco**. Encontró dos defectos y ninguno de los tres verdes podía verlos.

- La señal de nombre casaba por subcadena. `test_protocolo_de_arranque` disparaba `NOMBRE_NEG`
  porque «protocolo» contiene «roto». `test_invalidate_cache_refreshes`, porque «invalidate»
  contiene «invalid». La señal que más pesa en el recuento daba por cubierto lo que no lo estaba.
  Es el falso negativo, la dirección cara.
- El lector de etiquetas fallaba abierto. Cualquier valor que no reconociera pasaba a `false` en
  silencio. La plantilla que imprime `--etiquetar` sin rellenar, por ejemplo. O la palabra
  `verdadero`. La verdad de referencia se envenenaba sola, y encima el programa aconsejaba arreglar
  el criterio. Es el consejo contrario. En una herramienta cuya tesis es fallar cerrado, esa era la
  incoherencia más cara.

**Por qué no los cazó nada de lo anterior:** la mutación solo vigila las líneas que ya existen. El
acuerdo se mide contra un árbol de juguete, sin un solo nombre adversarial y sin una etiqueta mal
escrita. Un arnés hereda el punto ciego del corpus que lo alimenta. Los seis casos que cierran las
dos grietas llevan `NoSeCazaPorSubcadena` y `EtiquetaIlegibleNoSeConvierteEnFalso` en el nombre de
su clase. Cada uno trae su control al lado, para que el arreglo no pueda ser dejar de mirar.

Eso obliga a decir algo incómodo de la propia herramienta: **este detector cuenta qué bancos
tienen un brazo negativo, y tener un brazo negativo no es discriminar.** Un banco puede llevar
`assertFalse` y seguir pasando con el código roto. Lo que separa un banco de un adorno es mutar
el código y por eso la mutación viaja dentro del paquete:

```
python skills/detector-control-negativo/mutar.py
```

**Seis sabotajes. Hoy se cazan los seis.** No hay que creérselo: el comando lo hace delante de
quien lo lance y deja el fichero medido restaurado al terminar y también si el proceso muere a
mitad, porque la copia intacta vive en disco y no en la memoria del programa.

Y el mutador **falla cerrado**, que es la parte que más fácil se hace mal. Si el ancla de un
sabotaje ya no aparece en el fichero (porque alguien renombró una constante), esa mutación no se
aplica, y un mutador ingenuo la contaría como cazada sin haber cambiado una coma. Aquí eso sale
con ERROR y tumba la ejecución entera: un arnés que aprueba sin haber mordido no avala nada. Se
comprobó en las dos direcciones, con un ancla inventada a mano.

### Qué se puede comprobar desde fuera

**Esta página no te afirma ninguna cifra sobre el árbol privado.** El motivo no es que salga mal.
Es que no la puedes comprobar: ese árbol no viaja en el repositorio y no hay comando que teclear
para volver a medirlo. La última
pasada está en la tabla del principio, con su comando, su fecha, su hora, su commit y los tres
bancos con nombre y apellido, en la fila que la deja donde le toca: dentro de una serie que baja en
cada afinado.

Lo que sí puedes ejecutar es el ejemplo del principio, sobre este mismo repositorio y sin preparar
nada. Da **9 etiquetas de 9 bancos, concordancia 9 de 9 y salida `0`**. El «SIN control negativo
2 de 8» que sale ahí describe el árbol de juguete de `ejemplo/bancos/`, plantado banco a banco.

De la pasada sobre el árbol privado hay una sola cosa que este repositorio defiende, una
propiedad del instrumento y no del árbol: **el detector concordó con las 30 etiquetas escritas a
mano, 30 de 30**, sin un falso positivo ni un falso negativo. Eso se mide contra un objeto que no
se mueve, mientras el recuento se mide contra un árbol al que ese día le entraron tres bancos. Es
la diferencia entre las dos cifras y es toda la tesis de la herramienta.

Y dos límites que hay que decir antes de que alguien cite el número de la tabla:

1. **Las etiquetas negativas son pocas.** Tres casos de «no lo tiene» no permiten afirmar una tasa
   de falsos negativos. Lo que sí está medido es que la parte nueva del criterio no rescata ni un
   banco sin que una etiqueta lo respalde.
2. **El universo es lo que git publica y el criterio es el nombre.** Un banco del árbol de
   trabajo que nadie ha añadido queda fuera. Un banco que no se llame `test_*.py`,
   `run_tests*.py` o `*_test.py` tampoco entra. Son dos suelos declarados.

### Instalación

Para leer esta página no hace falta instalar nada: el instrumento viaja dentro y el comando del
principio lo ejecuta tal cual. Para usarlo a diario dentro de Claude Code, el paquete instalable
y sus instrucciones de desinstalación viven en
**[jleonceo/skill-detector-control-negativo](https://github.com/jleonceo/skill-detector-control-negativo)**.

En tu propio repositorio, sin instalar nada:

```bash
git clone https://github.com/jleonceo/detector-control-negativo
cd tu-repositorio
python ../detector-control-negativo/skills/detector-control-negativo/verificar_control_negativo.py --etiquetar
```

La primera ejecución sale con `2` y está bien que lo haga: todavía no hay etiquetas y sin ellas
el recuento es una aproximación sin puntuar. El camino es `--etiquetar`, abrir a mano los ficheros
que salgan y escribir la etiqueta con su evidencia.

Ese rato es el trabajo. No hay atajo: medir un banco obliga a leerlo.

| Opción | Para qué |
|---|---|
| `--raiz RUTA` | el árbol a medir; por defecto, la raíz git del directorio actual |
| `--etiquetas FICHERO` | la verdad de referencia con la que se puntúa el detector |
| `--excluir SUBCADENA` | deja fuera las rutas que la contengan; repetible y se cuentan aparte |
| `--listar` | cada banco con su veredicto y cada veredicto con la señal que lo disparó |
| `--etiquetar` | plantilla YAML de los bancos que aún no tienen etiqueta |

La raíz se le pregunta a git (`git rev-parse --show-toplevel`) en vez de deducirla contando
carpetas desde el script. Instalado como plugin, el script vive en la caché de Claude Code, lejos
de cualquier repositorio, y contar carpetas habría medido el árbol equivocado sin decir una
palabra.

### Verificación

```bash
python skills/detector-control-negativo/test_detector_control_negativo.py   # 38 casos
python skills/detector-control-negativo/mutar.py                           # 6 sabotajes
```

**38 casos. Siete de ellos son controles negativos marcados `CN`.** En un banco cuyo objeto es
cazar bancos sin control negativo, no tenerlos sería la ironía más cara del repositorio. El que
más vale es `test_cn1_prosa_con_no_y_sin_no_dispara`: comprueba que la señal de texto **no**
dispara sobre prosa llena de «no» y «sin», que es exactamente cómo la primera versión acabó
marcando 129 bancos de 129.

El banco mide dos objetos distintos a propósito. Los casos de fixture prueban el criterio con
texto escrito a mano, para que el veredicto correcto sea evidente al leerlo. Los casos sobre el
árbol lo prueban contra este repositorio de verdad y exigen el censo de etiquetas **en las dos
direcciones**: ninguna etiqueta puede apuntar a un fichero que ya no existe, y ningún banco puede
quedarse sin etiquetar. Sin la segunda, alguien añade un banco, no lo etiqueta, y la puntuación
sigue saliendo perfecta sobre los que ya estaban: un instrumento midiéndose contra una muestra
que encoge.

Un detalle pequeño que dice mucho de la herramienta: el guardián que compara este repositorio con
su gemelo se llama `guardian_gemelo.py` y no `test_gemelo.py`. El criterio del detector es el
nombre del fichero, así que llamarlo `test_*` lo metía en su propio universo como si fuera un
banco con casos que juzgar. Contaminar la medición con el instrumento es la clase de error que
este repositorio persigue.

### Requisitos

Python 3.9 o superior, biblioteca estándar, sin red y sin nada que instalar. En macOS y en casi
todo Linux el intérprete se llama `python3`, no `python`: los comandos de esta página van con
`python` porque se escribieron en Windows.

Esa frase habla del **instrumento**. Conviene apurarla porque el repositorio no cumple lo mismo
que él. `verificar_control_negativo.py` y `mutar.py` no abren un socket: lo que necesitan se lo
preguntan a `git` en local. El que sí sale a la red es `guardian_gemelo.py`, que consulta
`api.github.com` para comparar este repositorio con su gemelo, y por eso trae una vía local con
`GEMELO_LOCAL` para poder ejercitarlo sin ella. No forma parte de la skill ni de la medición.

Ese 3.9 está **declarado y todavía no certificado**. En local se ha ejecutado con Python 3.10, 3.13
y 3.14, las tres sobre Windows, pero en ninguna versión por debajo de 3.10, que es la que importaba.
Un repaso del código no encontró sintaxis ni biblioteca por encima de 3.9,
pero eso encuentra incompatibilidades y no certifica compatibilidad. Lo que la certifica es la
matriz de CI (3.9, 3.11 y 3.13 sobre Windows, Linux y macOS) dando verde, y hasta el primer push
no lo ha dado. Cuando lo dé, esta nota se corrige y no se borra.

### Piezas hermanas

- **[skill-detector-control-negativo](https://github.com/jleonceo/skill-detector-control-negativo)**:
  el mismo instrumento empaquetado como skill instalable de Claude Code, con su ejemplo dentro.
- **[adherencia-reglas](https://github.com/jleonceo/adherencia-reglas)**: cuenta qué fracción de
  las reglas que escribes para tu agente se cumple de verdad. Mismo patrón, otro objeto: allí se
  mide una norma, aquí se mide un banco.
- **[guardianes-verificados-ia](https://github.com/jleonceo/guardianes-verificados-ia)**: quién
  vigila a los guardianes. Un detector que encuentra el problema y no devuelve el código de salida
  que bloquea no protege nada.

---

## English

> **Read this first: the tool speaks Spanish, and this page does not change that.** Every line it
> prints, the five signal names (`MARCA`, `ASSERT_NEG`, `ESPERA_CERO`, `NOMBRE_NEG`,
> `ETIQUETA_NEG`), the five flags and the three YAML keys (`banco`,
> `tiene_control_negativo`, `evidencia`) are Spanish. The label value `agregador` means
> «aggregator». This page is the reference for that vocabulary, and not a localised program.

### The problem

A green suite proves the code passes its own cases. It does not prove the suite can tell working
code from broken code.

That is a different question.

The commonest case is a bench that only checks the happy path: feed it a valid input, assert the
correct result, done. That bench is green. It stays green after somebody breaks input validation,
because nobody ever asks it what happens with a bad input. The missing piece is the **negative
control**: the case that asserts what the tool must reject, block, leave empty or flag as
invalid.

Counting how many benches are in that state looks like an afternoon's work. Here is how it went:

| criterion version | what it added | benches with no negative control |
|---|---|---:|
| v1 | the project's explicit marker | 112 of 131 |
| v2 | `assertNot*`, `assertFalse`, `assertRaises` | 77 |
| v3 | expecting zero, an empty list, `_no_` and `_sin_` case names | 48 |
| v4 | the project's own assertion helper | 31 |
| by hand | 3 opened, 2 did have a negative control | ~10 |
| today's criterion, scored against 30 labels | this repository's instrument | 3 of 131 |

**That last row is one more stop on the series, not its conclusion, which is why it lives here and
not at the top of the page.** It was measured on 30/07/2026 at 15:04 over that same private tree, at
its commit `e86c67d`, with this command:

```bash
python skills/detector-control-negativo/verificar_control_negativo.py \
  --raiz <the root of that private tree> \
  --excluir /candidato_repo/ \
  --etiquetas etiquetas_control_negativo.yaml
```

The three benches are
`Aplicaciones/05_capa_confianza_rag/suite_aceptacion/test_c11_determinismo.py`,
`evals/run_tests_contrato_skills.py` and
`pipeline/eval_suite/evaluador/test_clasificador_motivo.py`. They travel with the figure because a
bare 3 cannot be audited.

Three things you need in order to read that row, and none of them is a detail:

1. **You cannot type that command.** The tree is private and does not travel in the repository.
   What gets published is the method rather than a result checkable from outside.
2. **Without `--excluir /candidato_repo/` the same command over the same tree returns 134 and not
   131.** In the private tree that exclusion is a constant inside the script and applies by itself;
   the instrument that gets published asks for it by flag. An exclusion taken for granted moves the
   denominator without leaving a trace.
3. **The two «131» in the table are not the same object.** The one in row v1 is the undifferentiated
   universe: aggregators went inside it that day and the exclusion did not exist. The one in the last
   row is 131 benches with cases of their own **plus** 5 aggregators **plus** 3 excluded. And the
   denominator moved that very day: three benches entered the tree at 12:34, at 13:02 and at 14:18.

**No version was miscoded.** Each refinement measured a different object, and each returned less
than the one before. A figure that only falls as you look harder has not converged at any earlier
stop: the first three would have been acted upon, and the first one declared a problem ten times
bigger than the real one. On top of that, the script from that day was never saved, so asking the
question again meant redoing the whole investigation.

Hence the two requirements that shape this tool: **the counter lives on disk**, and **the
criterion is scored against a reference truth** instead of being judged by the size of its own
result.

### The part that makes it more than a counter

A label file written by hand, opening every bench, three fields per entry:

```yaml
  - banco: ejemplo/bancos/test_veredicto_malo.py     # bench
    tiene_control_negativo: true                     # has a negative control
    evidencia: "assertEqual(estado_de(fuente_caducada()), \"NO_CONFIA\")"
    etiquetado_el: 2026-07-30                        # labelled on
```

With that, a new version of the criterion **stops being judged by returning a smaller number**
and gets scored instead: false positives (flagged, but they did have a negative control) and
false negatives (waved through, and they did not). A criterion that lowers the headline by
raising false negatives is worse, however much better the headline reads.

And the label is written **before** the criterion is tuned, deliberately. The other way round,
the label accommodates the instrument and the measurement stops meaning anything.

`tiene_control_negativo` takes a third value, `agregador`. It is not decoration: some files
are named like a bench and hold no case of their own, because they discover other benches and
launch them. Counting those among the uncovered counts the wrong object, and in the first pass
five of the twenty-four flagged files were exactly that.

### Which is why the exit code does not talk about the repository

| exit | meaning |
|---|---|
| `0` | the detector agrees with every label |
| `1` | it disagrees with one: there is a false positive or a false negative |
| `2` | there are no labels to be scored against, so no score is invented |
| `3` | no universe: no git root, or zero benches discovered |

**The bench count is reported and gates nothing.** That follows straight from the table above:
acting on a figure that has not converged is the very mistake this tool exists to avoid. Anyone
who wants a blocking threshold sets it themselves, knowing what they are doing.

The `3` is just as deliberate. Outside a git repository there is no universe, and saying «0
benches without a negative control» there would be the textbook false green: the most reassuring
message available, produced by having looked at nothing.

### Why each signal is narrow

| signal | what it recognises |
|---|---|
| `MARCA` | the explicit marker: `_CN_`, «control negativo», «CN1» |
| `ASSERT_NEG` | `assertNot*`, `assertFalse`, `assertRaises`, `pytest.raises`, `assert not` |
| `ESPERA_CERO` | expecting `0`, `[]`, `{}`, `None`, `False`, `is False`, `not in` |
| `NOMBRE_NEG` | case names with `_no_`, `_sin_`, `rechaza`, `bloquea`, `falla`, `invalido` |
| `ETIQUETA_NEG` | the case label declares the negative arm, or asserts the bad verdict |

One is enough for the bench to count as covered.

Two precautions that cost time and live inside the code:

**`ESPERA_CERO` looks at the shape of the condition, not at the name of the function wrapping
it.** A project with its own helper (`check(...)`) has no `assertFalse` anywhere in the tree, and
without this signal its benches came out as uncovered. That was one of the two false positives
the manual review exposed.

**Text signals are looked for where they belong and not inside any string.** The first version
looked for «no» and «sin» across the whole file and **fired on 129 benches out of 129**. A signal
that marks 100 % of the population separates nothing: it only lowers the count, which is how you
manufacture a figure that looks better and measures worse. It was caught because the report
prints the per-signal breakdown; with the bare total it would have passed for good.

### The honest story: four mutations before publishing

Before this repository was prepared, **four mutations were run against the detector itself**, each
one verified to bite **before** looking at what the bench said. This is the opposite of boasting
about a green suite: you break the code by hand and see whether anybody complains.

- Two bit cleanly. Breaking aggregator recognition (the fault that misfiled 5 of 24 in the
  first pass) brought down the case that compares the detector against the labels. It fell naming
  the misfiled bench.
- Two broke nothing. That was the hole. Deleting the `_CN_` literal from marker
  recognition, and deleting the `_no_` and `_sin_` names from the name signal, **took down not one
  test**. Each of those two forms depended exclusively on a single bench in the measured tree.
  Neither of those benches was in the label file. A 24-case bench, green, and two lines of the
  criterion anyone could delete tomorrow with nobody noticing. The name signal is not a detail:
  it is the one carrying most weight in the count.

It was closed before touching this repository, with **two new cases that isolate each of the two
forms** from any other signal that could mask them.

The bench went from 24 to 26 cases.

The four more up to 30 were added by the packaging. The next two, up to 32, came in while watching
the fixture census and the mutator's restore. Each covers a piece that in the private tree either
did not exist or sat nailed inside the script: the deliberately planted benches getting caught, no
bench of this repository going unlabelled, the git root never invented where there is none, the
declared exclusion dropping the paths to count them apart. The verification command further down
lists them as it runs.

### What the 6-out-of-6 mutation did not see

On publication day there were three greens. The bench at 32. Mutation at 6 of 6. Label agreement at
9 of 9. An outside auditor was then asked to look with material that was **not in the bench**. It
found two defects, and none of the three greens could see either.

- The name signal matched on substrings. `test_protocolo_de_arranque` fired `NOMBRE_NEG` because
  the Spanish «protocolo» contains «roto» (broken). `test_invalidate_cache_refreshes`, because
  «invalidate» contains «invalid». The signal that weighs most in the count was marking as covered
  what was not. That is the false negative, the expensive direction.
- The label reader failed open. Any value it did not recognise silently became `false`. The
  template `--etiquetar` prints when left unfilled, for one. Or the Spanish word `verdadero`. The
  reference truth poisoned itself, and the program then advised fixing the criterion. That is the
  opposite advice. In a tool whose whole thesis is failing closed, that was the costliest
  contradiction.

**Why nothing above caught them:** mutation only guards lines that already exist. Agreement is
measured against a toy tree, without a single adversarial name and without a single malformed label.
A harness inherits the blind spot of the corpus that feeds it. The six cases closing both gaps carry
`NoSeCazaPorSubcadena` and `EtiquetaIlegibleNoSeConvierteEnFalso` in their class names. Each brings
its control alongside, so the fix cannot be to stop looking.

Which forces an uncomfortable admission about the tool itself: **this detector counts which
benches have a negative arm, and having a negative arm is not the same as discriminating.** A
bench can carry `assertFalse` and still pass with broken code. What separates a bench from an
ornament is mutation, which is why mutation ships inside the package:

```
python skills/detector-control-negativo/mutar.py
```

**Six sabotages, and today all six are caught.** No need to take that on trust: the command does
it in front of you, and it restores the measured file when it finishes and also if the process is
killed halfway, because the intact copy lives on disk and not in the program's memory.

And the mutator **fails closed**, which is the part most easily got wrong. If a sabotage's anchor
no longer appears in the file (because someone renamed a constant), that mutation is not applied,
and a naive mutator would count it as caught without having changed a comma. Here that comes out
as ERROR and brings down the whole run: a harness that passes without having bitten vouches for
nothing. It was checked in both directions, with an anchor invented by hand.

### What can be checked from outside

**This page asserts no figure about the private tree.** The reason is not that the figure came out
wrong. It is that you cannot check it: that tree does not travel in the repository and there is no
command to type to measure it again. The last pass sits in the table at the top, with its command,
its date, its hour, its commit and the three benches named one by one, in the row that puts it where
it belongs: inside a series that falls with every refinement.

What you can run is the example at the top, over this very repository and with nothing to prepare.
It gives **9 labels over 9 benches, agreement 9 of 9 and exit `0`**, and the «SIN control negativo 2
de 8» printed there describes the toy tree in `ejemplo/bancos/`, planted bench by bench. Two with no
negative arm, which are the two the report flags; five with one, one per signal; and one aggregator,
for the label's third value. The ninth bench of that universe is the tool's own.

Those fixtures are the material the detector MEASURES, so several of them call symbols that do not
exist on purpose and would fail if anybody ran them as tests. They are named `test_*.py` because the
detector's criterion is the filename, and renaming them would drop them out of their own
measurement. The exclusion lives in `conftest.py`: today `python -m pytest -q` over this repository
collects 38 tests, all 38 from the detector's own bench, and comes out green without touching a
single fixture.

Of the pass over the private tree this repository stands behind one thing only. It is a property of
the instrument rather than of the tree: **the detector agreed with all 30
hand-written labels, 30 of 30**, with no false positive and no false negative. That is measured
against an object which does not move, while the count is measured against a tree that took in three
benches that same day. That is the difference between the two figures. It is also the whole thesis
of the tool.

And two limits worth stating before anybody quotes the figure in the table:

1. **There are few negative labels.** Three «it does not have one» cases do not support a false
   negative rate. What is measured is that the new part of the criterion rescues no bench without
   a label backing it.
2. **The universe is what git publishes, and the criterion is the filename.** A bench in the
   working tree that nobody added stays out. A bench not named `test_*.py`, `run_tests*.py` or
   `*_test.py` never enters. Two declared floors.

### Install

Nothing needs installing to read this page: the instrument travels inside and the command at the
top runs as it is. To use it day to day inside Claude Code, the installable package and its
uninstall instructions live at
**[jleonceo/skill-detector-control-negativo](https://github.com/jleonceo/skill-detector-control-negativo)**.

On your own repository, with nothing installed:

```bash
git clone https://github.com/jleonceo/detector-control-negativo
cd your-repository
python ../detector-control-negativo/skills/detector-control-negativo/verificar_control_negativo.py --etiquetar
```

The first run exits with `2`, and rightly so: there are no labels yet, and without them the count
is an unscored approximation. The path is `--etiquetar`, opening by hand whatever it lists, and
writing the label with its evidence.

That sitting is the work. There is no shortcut: measuring a bench means reading it.

| Option | What for |
|---|---|
| `--raiz PATH` | the tree to measure; by default, the git root of the current directory |
| `--etiquetas FILE` | the reference truth the detector is scored against |
| `--excluir SUBSTRING` | drops paths containing it; repeatable, and counted separately |
| `--listar` | every bench with its verdict, and every verdict with the signal that fired |
| `--etiquetar` | a YAML template for the benches that have no label yet |

The root is asked of git (`git rev-parse --show-toplevel`) rather than deduced by counting
folders up from the script. Installed as a plugin, the script lives in Claude Code's cache, far
from any repository, and counting folders would have measured the wrong tree without saying a
word.

### Verification

```bash
python skills/detector-control-negativo/test_detector_control_negativo.py   # 38 cases
python skills/detector-control-negativo/mutar.py                           # 6 sabotages
```

**38 cases, seven of them negative controls marked `CN`.** In a bench whose whole purpose is
catching benches without negative controls, having none would be the most expensive irony in the
repository. The one that matters most is `test_cn1_prosa_con_no_y_sin_no_dispara`: it checks that
the text signal does **not** fire on prose full of «no» and «sin», which is exactly how the first
version ended up marking 129 benches out of 129.

The bench measures two different objects on purpose. The fixture cases test the criterion against
text written by hand, so the correct verdict is obvious on reading. The tree cases test it against
this repository for real, and they demand the label census **in both directions**: no label may
point at a file that no longer exists, and no bench may go unlabelled. Without the second one,
somebody adds a bench, does not label it, and the score keeps coming out perfect over the ones
already there: an instrument measuring itself against a shrinking sample.

One small detail that says a lot about the tool: the guard comparing this repository with its twin
is called `guardian_gemelo.py` and not `test_gemelo.py`. The detector's criterion is the filename,
so calling it `test_*` dropped it into its own universe as though it were a bench with cases to
judge. Contaminating the measurement with the instrument is the kind of mistake this repository is
about.

### Requirements

Python 3.9 or newer, standard library, no network and nothing to install. On macOS and most Linux
the interpreter is `python3`, not `python`: the commands on this page say `python` because they
were written on Windows.

That sentence describes the **instrument**. It is worth tightening, because the repository does not
meet the same claim. `verificar_control_negativo.py` and `mutar.py` open no socket: what they
need they ask of local `git`. The one that does go out is `guardian_gemelo.py`, which queries
`api.github.com` to compare this repository against its twin, and which therefore ships a local
route through `GEMELO_LOCAL` so it can be exercised without the network. It is part of neither the
skill nor the measurement.

That 3.9 is **declared and not yet certified**. Locally it has been run with Python 3.10, 3.13 and
3.14, all three on Windows, and on nothing below 3.10, which is the version that mattered.
A read-through found no syntax or library above 3.9, but that finds incompatibilities and
does not certify compatibility. What certifies it is the CI matrix (3.9, 3.11 and 3.13 across
Windows, Linux and macOS) going green, and until the first push it has not. When it does, this note
gets corrected and not deleted.

### Sibling repositories

- **[skill-detector-control-negativo](https://github.com/jleonceo/skill-detector-control-negativo)**:
  the same instrument packaged as an installable Claude Code skill, example included.
- **[adherencia-reglas](https://github.com/jleonceo/adherencia-reglas)**: counts what fraction of
  the rules you wrote for your agent actually gets followed. Same pattern, different object: there
  a rule is measured, here a bench.
- **[guardianes-verificados-ia](https://github.com/jleonceo/guardianes-verificados-ia)**: who
  guards the guards. A detector that finds the problem and fails to return the exit code that
  blocks protects nothing.

---

## Licencia / License

MIT. Ver [LICENSE](LICENSE).
