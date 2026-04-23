"""Game configuration and constants."""
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import pygame

# Colors
WHITE: Tuple[int, int, int] = (255, 255, 255)
BLACK: Tuple[int, int, int] = (0, 0, 0)
GREY: Tuple[int, int, int] = (100, 100, 100)
BG_COLOR: str = "#0058f8"

# Nintendo-ish palette
MT_TOP: Tuple[int, int, int] = (252, 252, 252)
MT_COLOR: Tuple[int, int, int] = (124, 124, 124)
GRASS_COLOR: Tuple[int, int, int] = (0, 184, 0)
TREES_COLOR: Tuple[int, int, int] = (0, 88, 0)
SAND_COLOR: Tuple[int, int, int] = (248, 216, 120)
DIRT_COLOR: Tuple[int, int, int] = (172, 124, 0)
SHALLOWS_COLOR: Tuple[int, int, int] = (0, 120, 248)

# Tile type IDs
class TileType:
    SAND = 0
    GRASS = 1
    FOREST = 2
    MOUNTAINS = 3
    HIGH_MOUNTAINS = 4
    WATER = 5
    CAVE = 6
    CASTLE = 7
    TOWN = 8


@dataclass(frozen=True)
class GameConfig:
    """Immutable game configuration."""
    width: int = 960
    height: int = 640
    cell_width: int = 32
    cell_height: int = 32
    map_width: int = 32
    map_height: int = 32
    fps: int = 60
    fullscreen: bool = False
    asset_dir: Path = Path("assets")
    
    @property
    def cell_size(self) -> Tuple[int, int]:
        return (self.cell_width, self.cell_height)
    
    @property
    def view_distance(self) -> int:
        """Tiles visible in each direction from player."""
        return 16


# Default instance
CONFIG = GameConfig()
