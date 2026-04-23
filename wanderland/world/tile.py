"""Tile types and classes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

from wanderland.config import TileType


@dataclass
class Tile:
    """Base tile class."""
    x: int
    y: int
    tile_type: int = TileType.GRASS
    blocks_path: bool = False
    chunk: Tuple[int, int] = (0, 0)
    image_path: Optional[str] = None
    hp: int = 0
    
    def set_tile(self, tile_type: int) -> None:
        self.tile_type = tile_type
    
    def set_image(self, path: Optional[str] = None) -> None:
        if path is not None:
            self.image_path = path
        else:
            self.image_path = self._default_image()
    
    def _default_image(self) -> Optional[str]:
        mapping = {
            TileType.SAND: "assets/overworld/sand_fantasy.png",
            TileType.GRASS: "assets/overworld/grass-fantasy.png",
            TileType.FOREST: "assets/overworld/trees_fantasy.png",
            TileType.MOUNTAINS: "assets/overworld/mountains_fantasy.png",
            TileType.HIGH_MOUNTAINS: "assets/overworld/high_mountains_fantasy.png",
            TileType.WATER: "assets/overworld/water_fantasy.png",
            TileType.CAVE: "assets/overworld/cave_fantasy.png",
            TileType.CASTLE: "assets/overworld/castle_fantasy.png",
            TileType.TOWN: "assets/overworld/town_fantasy.png",
        }
        return mapping.get(self.tile_type)
    
    def set_hp(self, hp: int) -> None:
        self.hp = hp
    
    def set_chunk(self, chunk: Tuple[int, int]) -> None:
        self.chunk = chunk


@dataclass  
class OverworldTile(Tile):
    """Overworld tile - coarse view."""
    pass


@dataclass
class LocalTile(Tile):
    """Local tile - zoomed in view."""
    pass
