# Especificación: detector de bancos sin control negativo

> Se escribió antes del código y se aceptó antes de escribirlo. Va en el repositorio porque los
> criterios de aceptación son lo que hace comprobable el resto: sin ellos, «el detector funciona»
> es una opinión.

## El problema que resuelve

Un banco de pruebas que solo comprueba que lo bueno pasa da verde con el código bueno y con el
roto. Saber cuántos hay así es útil. La primera vez que se intentó salió mal de una forma que
conviene no repetir, y de ahí sale todo lo demás de este documento.

| versión | qué añadió al criterio | bancos sin brazo negativo |
|---|---|---:|
| v1 | la marca explícita | 112 de 131 |
| v2 | `assertNot*`, `assertFalse`, `assertRaises` | 77 |
| v3 | esperar cero, lista vacía, nombres `_no_` y `_sin_` | 48 |
| v4 | el helper propio que envuelve la aserción | 31 |
| a mano | 3 revisados, 2 tenían brazo negativo | ~10 |

Cada afinado daba menos. **Ninguna versión estaba mal programada: cada una medía un objeto
distinto.** Un número que solo baja conforme se mira mejor no ha convergido en ninguna parada
anterior, y en las tres primeras se habría actuado sobre él. Además el script de aquel día no
quedó en disco, así que volver a preguntar la cifra obligaba a repetir la investigación entera.

**De ahí los dos requisitos que ordenan todo lo demás:** el contador vive en disco, y el criterio
se puntúa contra una verdad de referencia en vez de juzgarse por el tamaño de su resultado.

## Población: siempre los tres números

El informe declara **tres** cifras y nunca una: lo que hay, lo que ha decidido dejar fuera, y con
qué criterio. Decir «131 bancos» sin lo demás es lo que hace que una cifra parezca más firme de lo
que es.

Y ese ejemplo no está elegido al azar. El 131 de la fila v1 de la tabla de arriba y el 131 de este
universo declarado se escriben igual y cuentan objetos distintos: en la primera pasada los
agregadores iban dentro del recuento y la exclusión de copias no existía. Dos cifras iguales sobre
el mismo árbol, con dos poblaciones detrás, es la forma más barata de fabricar una serie que
parece continua.

- **Universo:** ficheros versionados en git (`git ls-files`) cuyo nombre encaja con `test_*.py`,
  `run_tests*.py` o `*_test.py`.
- **Fuera a propósito:** lo que no está versionado (carpetas de trabajo, `__pycache__`, copias) y
  lo que se declare con `--excluir`, pensado para las copias de un repositorio que ya se mide en
  su origen.
- **Criterio:** el nombre y no el contenido. Un banco que no se llame así no entra. Es un suelo
  declarado y no un descuido.

## Señales: qué cuenta como brazo negativo

Cada banco se clasifica y **el informe dice qué señal disparó**, no solo el veredicto. Sin eso, la
cifra vuelve a ser un contador sin su objeto y nadie puede comprobarla.

| señal | qué reconoce |
|---|---|
| `MARCA` | la marca explícita: `_CN_`, «control negativo», «CN1» |
| `ASSERT_NEG` | `assertNot*`, `assertFalse`, `assertRaises`, `pytest.raises`, `assert not` |
| `ESPERA_CERO` | comparar contra `0`, `[]`, `{}`, `None`, `False`, `is False`, `not in`: negativo por significado |
| `NOMBRE_NEG` | nombres de caso con `_no_`, `_sin_`, `rechaza`, `bloquea`, `falla`, `invalido` |
| `ETIQUETA_NEG` | la etiqueta del caso declara el brazo negativo, o afirma el veredicto malo |

Un banco tiene brazo negativo si dispara **al menos una**. La lista es ampliable; lo que no es
ampliable sin pagar el precio es añadir una señal y quedarse con el número nuevo sin puntuarlo.

## La verdad de referencia es la pieza nueva

El fichero de etiquetas guarda bancos etiquetados **a mano**, cada uno con:

    - banco: ruta/relativa/run_tests_x.py
      tiene_control_negativo: true | false | agregador
      evidencia: "la línea o el nombre de caso que lo demuestra"
      etiquetado_el: 2026-07-30

Con eso, una versión nueva del criterio se puntúa: **falsos positivos** (bancos que el detector
señala y las etiquetas dicen que sí tienen brazo negativo) y **falsos negativos** (los que deja
pasar y no lo tienen). Un criterio que baja el recuento total **subiendo** los falsos negativos es
peor, aunque el titular sea más bonito.

`agregador` es un tercer valor y no un sí ni un no: son ficheros que se llaman como un banco y no
tienen un solo caso propio, porque descubren otros y los lanzan. Contarlos entre los carentes es
el mismo error de objeto que costó dos de las cifras de la tabla de arriba.

## Criterios de aceptación

1. **CA1 · el universo se declara.** El informe imprime los tres números: encontrados, excluidos
   y el criterio de exclusión.
2. **CA2 · cada señalado trae su motivo.** Con `--listar`, cada banco sin brazo negativo sale con
   su ruta; cada banco con brazo negativo sale con la señal que disparó.
3. **CA3 · el detector se mide contra las etiquetas** y publica su acuerdo con ellas. Sin
   etiquetas, lo dice y no finge una puntuación.
4. **CA4 · el código de salida habla del INSTRUMENTO y no del repositorio.** `0` concuerda con
   todas las etiquetas, `1` discrepa de alguna, `2` no hay etiquetas con las que medirse. El
   recuento de bancos se **reporta** y no tumba nada: actuar sobre una cifra que no ha convergido
   es justo el error que este detector existe para no repetir.
5. **CA5 · sin universo, no hay veredicto.** Si el descubrimiento devuelve cero bancos, o si no
   hay ninguna raíz de git desde donde se lanza, sale con `3` en vez de decir «0 bancos sin brazo
   negativo», que es el falso verde de manual.
6. **CA6 · determinista y sin red.** Ni modelo de lenguaje ni consultas externas. Dos ejecuciones
   seguidas sobre el mismo árbol dan el mismo resultado.

## La regla de parada evita repetir el fallo

**Una señal nueva entra solo cuando un caso ETIQUETADO la exige, y se declara qué caso.** No
cuando se le ocurre a alguien que podría existir, y desde luego no porque baje el recuento.

Las tres que entraron al etiquetar a mano, con el caso que las exigió:

| señal nueva | el caso etiquetado que la exigió |
|---|---|
| `is False` dentro de `ESPERA_CERO` | un banco con cinco `check(permitir is False, "BLOQUEA…")` |
| `not in` dentro de `ESPERA_CERO` | un banco con `check("F" not in filas, …)` |
| `ETIQUETA_NEG` | un banco cuya tabla de casos dice «NO toca un mensaje que ya está limpio», y otro que afirma el veredicto `NO_CONFIA` |

Y la comprobación que hace honesto el conjunto: **los once bancos que la señal nueva rescata están
los once en la lista etiquetada a mano.** No rescata ni uno sin verificar.

## Lo que la cifra NO autoriza a decir

Dos límites, dichos antes de que alguien cite el número:

1. **Las etiquetas negativas son pocas.** Con tres casos de «no lo tiene» no se puede afirmar una
   tasa de falsos negativos: el detector podría estar dando por bueno a bancos que no lo son y las
   etiquetas no lo verían. Lo que sí está medido es que su parte nueva no rescata nada sin
   verificar.
2. **Tener una aserción negativa no es discriminar.** Un banco puede llevar `assertFalse` y seguir
   pasando con el código roto. Eso lo dice mutar el código, no leerlo.

## Lo que este detector no hace

- **No arregla bancos.** No escribe en ninguno ni propone parches.
- **No dice si un banco es bueno.** Para eso está mutar el código y ver si el banco cae, que es
  otro instrumento y otro coste.
- **No cuenta lo que git no publica.** Un banco del árbol de trabajo que nadie ha añadido queda
  fuera, y es un suelo declarado.
