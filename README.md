# Wanderland

A modernized port of Wanderland 0.03_2 — a 2D procedural exploration/survival game.

## About

Wanderland generates a random world using Voronoi diagrams and Simplex noise, then lets you explore it at two zoom levels: an overworld view for travel and local maps for detailed interaction. Chop trees, craft items, and wander.

## Requirements

- Python 3.8+
- pygame
- numpy
- Pillow
- opensimplex

## Install

```bash
pip install pygame numpy Pillow opensimplex
```

## Run

```bash
python main.py
```

## Controls

- **WASD** — Move
- **E** — Toggle inventory
- **Enter** — Toggle local/overworld view
- **F11** — Fullscreen
- **P** — Debug/craft test
- **Mouse** — Drag items in toolbar/inventory
- **Scroll** — Change selected toolbar slot
- **Escape** — Quit

## Project Structure

```
wanderland/
  config.py       — Game constants and configuration
  core/
    game.py       — Main game loop and state management
  entities/
    player.py     — Player, inventory, movement
    item.py       — Item definitions and registry
    crafting.py   — Crafting recipes
  render/
    renderer.py   — Drawing and UI
    assets.py     — Asset loading and caching
  world/
    generator.py  — Procedural world generation
    tile.py       — Tile types
    voronoi.py    — Voronoi diagram generator
```

## Original

This is a modernized version of Wanderland 0.03_2, originally written in Python/pygame in 2018.
