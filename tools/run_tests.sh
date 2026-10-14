#!/bin/sh
# Pruebas automáticas del prototipo: un bot recorre los 4 niveles (incluido el jefe) y verifica
# que se pueden completar. Requiere Godot 4.3 en la variable GODOT (o en el PATH como "godot").
# Uso:  GODOT=/ruta/a/godot sh tools/run_tests.sh
GODOT=${GODOT:-godot}
cd "$(dirname "$0")/.." || exit 1
$GODOT --headless --path . --import > /dev/null 2>&1
echo "== Prueba 1: geometría de los niveles (sin enemigos) =="
$GODOT --headless --fixed-fps 60 --path . scenes/level.tscn -- --autotest --no-enemies --level=0 | grep "\[TEST\]"
echo "== Prueba 2: recorrido completo con enemigos y jefe =="
$GODOT --headless --fixed-fps 60 --path . scenes/level.tscn -- --autotest --level=0 | grep "\[TEST\]"
