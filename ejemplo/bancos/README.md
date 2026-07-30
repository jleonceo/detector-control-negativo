# Esto es el corpus que mide la herramienta

Los ficheros de aquí se llaman `test_*.py` y ninguno es una prueba de este repositorio. Son el
material que el detector mide: siete bancos plantados a mano, cinco con brazo negativo (uno por
cada señal del criterio) y dos sin él, más un agregador para el tercer valor de la etiqueta. Invocan símbolos que no existen (`calcular`, `motor`, `estado_de`) porque imitan al banco
de otro proyecto, que es lo que el detector se encuentra ahí fuera. Ejecutarlos no tiene sentido.
El veredicto de cada uno está escrito a mano en `ejemplo/etiquetas_ejemplo.yaml`, que es la vara con
la que se puntúa el detector.

## Por qué llevan un nombre que parece de prueba

El universo del detector se define por el NOMBRE del fichero. Ese suelo está declarado: entra lo
versionado en git que se llame `test_*.py`, `run_tests*.py` o `*_test.py`. Un corpus con otros
nombres se queda fuera de la medición, así que el ejemplo dejaría de demostrar el criterio que está
enseñando. Se midió antes de decidirlo. Renombrando los siete, el ejemplo baja de ocho bancos a
uno y acaba publicando que aquí no hay ninguno sin control negativo, con código de salida cero. Ese
es el falso verde que este repositorio persigue.

## Qué se hizo entonces con pytest

Pytest reclama dos de esas tres formas de nombre, así que recogía este corpus y lo ejecutaba. El
`conftest.py` de la raíz lo declara fuera del descubrimiento, con el motivo entero escrito dentro.
El flujo de CI comprueba las dos mitades: que `python -m pytest -q` sale verde en un clon recién
hecho, y que sale verde **por no haber recogido nada de aquí**.

Si algún día hace falta un banco de verdad para el ejemplo, va en otra carpeta. Lo que vive aquí se
lee y se mide.

## Cómo se ve lo que hace el detector con cada uno

```
python skills/detector-control-negativo/verificar_control_negativo.py \
  --etiquetas ejemplo/etiquetas_ejemplo.yaml --listar
```

La lista dice, de cada fichero, si tiene brazo negativo y **qué señal** lo delata. Los dos que salen
señalados están plantados para eso. `test_solo_positivo.py` solo pregunta por el valor bueno.
`test_prosa_con_no_y_sin.py` está lleno de «no» y de «sin» en la prosa sin comprobar ni una entrada
mala, que es la trampa en la que cayó la primera versión del criterio.
