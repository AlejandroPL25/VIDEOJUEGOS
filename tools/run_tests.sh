#!/bin/sh
# Pruebas automáticas del prototipo: un bot recorre los 4 niveles hasta el altar y verifica que se
# pueden completar (el bot es invulnerable: se prueba la geometría, no la dificultad).
# Requiere Godot 4.3 en la variable GODOT (o en el PATH como "godot").
# Uso:  GODOT=/ruta/a/godot sh tools/run_tests.sh
GODOT=${GODOT:-godot}
cd "$(dirname "$0")/.." || exit 1
$GODOT --headless --path . --import > /dev/null 2>&1
echo "== Prueba: recorrido completo de los 4 niveles =="
$GODOT --headless --fixed-fps 60 --path . scenes/level.tscn -- --autotest --level=0 | grep "\[TEST\]"
