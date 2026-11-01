# EMBRA: Bosque de Brasas

Plataformas 2D en pixel art hecho con **Godot 4.3** (GDScript), basado en el GDD de la Fase 2.
Embra, una pequeña brasa separada de la fogata ancestral, debe cruzar cuatro zonas, recoger chispas,
esquivar a los Rondines y las zonas de fuego y humo, y llegar al altar para reavivar la fogata.

## Cómo jugar
| Acción | Teclas |
|---|---|
| Mover | Flechas izquierda / derecha (o A / D) |
| Saltar | ESPACIO |
| Pausa | ESC o P |
- Chispas: suman puntos. Rondín o fuego activo: pierdes una vida y parte del puntaje del nivel.
- Caer al vacío: pierdes una vida pero conservas el puntaje; reapareces en el último brasero.
- Cada nivel guarda tu mejor puntaje (menú > Mejores puntajes).

## Niveles
1. Bosque de Brasas (movimiento y salto) · 2. Cañón Humeante (fuego y humo) · 3. Ruinas de Carbón (enemigos + fuego) · 4. El Altar (todo junto)

## Estructura
- `scripts/` código del juego (todo comentado): `global.gd` (autoload), `player.gd`, `level.gd`, `rondin.gd`, `fire_zone.gd`, HUD, `bot.gd` (pruebas).
- `assets/` arte y audio originales generados con `tools/make_assets.py` y `tools/make_audio.py`.
- `tools/make_levels.py` genera los mapas ASCII (`scripts/level_data.gd`).
- `docs/` bitácora, biblia del videojuego, reporte de pruebas y plan de acción.

## Abrir y ejecutar
Instala Godot 4.3, abre `project.godot` y presiona F5. Para exportar: Proyecto > Exportar (hay presets para Windows, Linux y Web).

## Pruebas automáticas
`GODOT=/ruta/a/godot sh tools/run_tests.sh`

## Control de versiones
Cada etapa quedó en un commit (`git log --oneline`).

## Uso de IA

Durante el desarrollo usé IA (Claude) como herramienta de apoyo para depurar el código. El diseño del juego, sus mecánicas y su implementación son de mi autoría.

## Uso de IA

El proyecto se empezó en Unity y se migró a Godot. Como no conocía Godot, usé IA (Claude) como apoyo para depurar el código durante la migracion.
