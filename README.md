# Embra: La Llama Eterna

Plataformas 2D en pixel art hecho con **Godot 4.3** (GDScript). Embra, la última brasa de la aldea de Cenizal,
debe cruzar cuatro zonas, recoger chispas y reavivar la Hoguera Eterna.

## Cómo jugar
| Acción | Teclado |
|---|---|
| Mover | A / D o flechas |
| Saltar | ESPACIO (mantén presionado para saltar más alto) |
| Bola de fuego | X |
| Pausa | ESC o P |
Pisa a los enemigos para vencerlos o quémalos con fuego. Los braseros guardan tu avance.

## Estructura del proyecto
- `scripts/` código del juego (todo comentado): `global.gd` (autoload), `player.gd`, `level.gd`, enemigos, jefe, HUD, `bot.gd` (pruebas).
- `scenes/` escenas mínimas (el nivel se construye por código a partir de los mapas).
- `assets/sprites`, `assets/audio` arte y audio originales, generados con `tools/make_assets.py` y `tools/make_audio.py`.
- `tools/make_levels.py` genera `scripts/level_data.gd` (mapas ASCII de los 4 niveles).
- `docs/` bitácora, biblia del videojuego, reporte y plan de acción.

## Abrir y ejecutar
1. Instala Godot 4.3 (https://godotengine.org) y abre `project.godot`.
2. Presiona F5 para jugar.
3. Exportar: Proyecto > Exportar (ya hay presets para Windows, Linux y Web).

## Pruebas automáticas
`GODOT=/ruta/a/godot sh tools/run_tests.sh` ejecuta un bot que completa los 4 niveles (incluida la pelea contra el jefe).

## Control de versiones
Cada etapa del desarrollo quedó en un commit (`git log --oneline`).
