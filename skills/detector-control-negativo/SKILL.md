---
name: detector-control-negativo
description: >
  Cuenta cuántos bancos de pruebas de un repositorio comprueban solo que lo bueno pasa, y por
  eso darían verde igual con el código roto. Se activa al preguntar si los tests discriminan,
  si una suite verde demuestra algo, al revisar la calidad de un banco de pruebas, al auditar
  la cobertura de una suite heredada, o antes de presumir de tests en un README. Trae su propio
  instrumento determinista, anclado a un fichero de etiquetas escrito a mano, y su código de
  salida habla de la precisión del detector y no del estado del repositorio. NO arregla bancos
  y NO afirma que un banco discrimine de verdad: eso lo dice mutar el código, que es otro
  instrumento y otro coste.
license: MIT
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/verificar_control_negativo.py *)
compatibility: >
  Cualquier repositorio con git, porque el universo se pregunta a `git ls-files`. Python 3.9 o
  superior, biblioteca estándar, sin red y sin nada que instalar. Solo lectura: no escribe en
  ningún banco ni propone parches.
metadata:
  version: "1.0"
  validated_with: claude-opus-5
  validation_date: "2026-07-30"
---

# detector-control-negativo: los tests que aprueban al culpable

> **Principio rector.** Un banco que solo comprueba que lo bueno pasa da verde con el código
> bueno y con el roto. Saber cuántos hay así es útil; medirlo mal sale caro. En el árbol donde
> nació esta herramienta, el primer intento dio 112 bancos sin brazo negativo, luego 77, luego
> 48, luego 31, y una revisión a mano de tres casos encontró dos falsos positivos, o sea que la
> cifra de verdad rondaba los diez. **Ninguna versión estaba mal programada: cada afinado del
> criterio medía un objeto distinto.** Una cifra que solo baja conforme se mira mejor no ha
> convergido en ninguna parada anterior, y en las tres primeras se habría actuado sobre ella.

## Lo primero, y no es el recuento

**El código de salida habla del INSTRUMENTO, no del repositorio.** Esto se dice antes que
cualquier número porque es lo que cambia la forma de usar la herramienta:

| salida | qué significa |
|---|---|
| `0` | el detector concuerda con todas las etiquetas |
| `1` | discrepa de alguna: hay un falso positivo o un falso negativo |
| `2` | no hay etiquetas con las que medirse, así que no se puntúa |
| `3` | no hay universo: ninguna raíz de git, o el descubrimiento no encontró un solo banco |

El recuento de bancos se **reporta** y no tumba nada. Actuar sobre una cifra que no ha
convergido es exactamente el error que esta herramienta existe para no repetir.

## Cómo se usa

```bash
python ${CLAUDE_SKILL_DIR}/verificar_control_negativo.py --raiz .
python ${CLAUDE_SKILL_DIR}/verificar_control_negativo.py --raiz . --listar
python ${CLAUDE_SKILL_DIR}/verificar_control_negativo.py --raiz . --etiquetar
```

| Opción | Para qué |
|---|---|
| `--raiz RUTA` | el árbol a medir; por defecto, la raíz git del directorio actual |
| `--etiquetas FICHERO` | la verdad de referencia con la que se puntúa el detector |
| `--excluir SUBCADENA` | deja fuera las rutas que la contengan; repetible, y se cuentan aparte |
| `--listar` | cada banco con su veredicto, y cada veredicto con la señal que lo disparó |
| `--etiquetar` | plantilla YAML de los bancos que aún no tienen etiqueta |

**La primera ejecución en un repositorio nuevo sale con 2**, y está bien que sea así: todavía no
hay etiquetas, y sin ellas el recuento es una aproximación sin puntuar. El camino es
`--etiquetar`, abrir a mano los ficheros que salgan, y escribir la etiqueta con su evidencia.

## El orden del trabajo, que es lo que evita repetir el fallo

1. **Ejecutar y mirar los tres números**, nunca solo el primero: bancos con casos propios,
   agregadores y excluidos, con el criterio del universo declarado. Decir «131 bancos» sin lo
   demás hace que la cifra parezca más firme de lo que es.
2. **Ejecutar con `--listar`** y abrir tres o cuatro de los señalados. Si el criterio se
   equivoca, se ve aquí y no en la portada de un informe.
3. **Etiquetar a mano** antes de tocar el criterio. El fichero de etiquetas lleva por banco su
   veredicto, la línea que lo demuestra y la fecha.
4. **Una señal nueva entra solo cuando un caso ETIQUETADO la exige, y se declara qué caso.** No
   cuando a alguien se le ocurre que podría existir, y desde luego no porque baje el recuento.
5. **Si el detector discrepa de las etiquetas, se arregla el criterio.** Acomodar la verdad de
   referencia al instrumento es lo único que está prohibido de raíz.

## Las señales, y por qué cada una es estrecha

| señal | qué reconoce |
|---|---|
| `MARCA` | la marca explícita del proyecto: `_CN_`, «control negativo», «CN1» |
| `ASSERT_NEG` | `assertNot*`, `assertFalse`, `assertRaises`, `pytest.raises`, `assert not` |
| `ESPERA_CERO` | esperar cero, vacío, `None`, `False`, `is False`, `not in`: negativo por significado |
| `NOMBRE_NEG` | nombres de caso con `_no_`, `_sin_`, `rechaza`, `bloquea`, `falla`, `invalido` |
| `ETIQUETA_NEG` | la etiqueta del caso declara el brazo negativo, o afirma el veredicto malo |

Un banco tiene brazo negativo si dispara **al menos una**. Dos precauciones que costaron
tiempo y están dentro del código:

- **`ESPERA_CERO` mira la forma de la condición y no el nombre de la función que la envuelve.**
  Un proyecto con su propio helper (`check(...)`) no tiene `assertFalse` en ninguna línea, y sin
  esta señal sus bancos pasaban por carentes. Fue uno de los dos falsos positivos.
- **`NOMBRE_NEG` y `ETIQUETA_NEG` se buscan donde toca y no en cualquier cadena.** La primera
  versión miraba «no» y «sin» dentro de todo el texto y disparaba en 129 bancos de 129. Una
  señal que marca al 100 % de la población no separa nada, solo baja el recuento. Se cazó porque
  el informe imprime el reparto por señal; con el total a secas habría pasado por buena.

## Lo que esta skill NO hace

- **No arregla bancos.** No escribe en ninguno ni propone parches.
- **No dice si un banco es bueno.** Tener una aserción negativa no prueba que discrimine: un
  banco puede llevar `assertFalse` y seguir pasando con el código roto. Eso lo dice mutar el
  código y ver si el banco cae.
- **No cuenta lo que git no publica.** El universo sale de `git ls-files`, así que un banco del
  árbol de trabajo que nadie ha añadido queda fuera, y es un suelo declarado.
- **No entra por el nombre de un fichero que no parezca un banco.** El criterio es
  `test_*.py`, `run_tests*.py` o `*_test.py`. Otro esquema de nombres necesita otro criterio.

## El método completo

Las cifras medidas sobre un árbol real, el fichero de etiquetas, las cuatro mutaciones que se
le pasaron al propio detector y el banco que creció por dos de ellas están en el repositorio de
la herramienta: **https://github.com/jleonceo/detector-control-negativo**
