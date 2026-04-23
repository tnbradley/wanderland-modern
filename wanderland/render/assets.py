"""Asset loading and caching."""
from pathlib import Path
from typing import Dict, Optional

import pygame


class AssetLoader:
    """Loads and caches game assets."""
    
    def __init__(self, asset_dir: Path = Path("assets")) -> None:
        self._dir = asset_dir
        self._cache: Dict[str, pygame.Surface] = {}
    
    def load_image(self, path: str) -> Optional[pygame.Surface]:
        """Load an image, using cache if available."""
        if path in self._cache:
            return self._cache[path]
        
        try:
            full_path = self._dir / path if not path.startswith("assets") else Path(path)
            surface = pygame.image.load(str(full_path)).convert_alpha()
            self._cache[path] = surface
            return surface
        except (pygame.error, FileNotFoundError):
            return None
    
    def get(self, path: str) -> Optional[pygame.Surface]:
        """Alias for load_image."""
        return self.load_image(path)
    
    def load_tiles(self) -> Dict[int, pygame.Surface]:
        """Load all overworld tile images."""
        from wanderland.config import TileType
        tiles = {}
        mapping = {
            TileType.SAND: "overworld/sand_fantasy.png",
            TileType.GRASS: "overworld/grass-fantasy.png",
            TileType.FOREST: "overworld/trees_fantasy.png",
            TileType.MOUNTAINS: "overworld/mountains_fantasy.png",
            TileType.HIGH_MOUNTAINS: "overworld/high_mountains_fantasy.png",
            TileType.WATER: "overworld/water_fantasy.png",
            TileType.CAVE: "overworld/cave_fantasy.png",
            TileType.CASTLE: "overworld/castle_fantasy.png",
            TileType.TOWN: "overworld/town_fantasy.png",
        }
        for tile_type, path in mapping.items():
            surface = self.load_image(path)
            if surface:
                tiles[tile_type] = surface
        return tiles
    
    def load_local_tiles(self) -> Dict[int, pygame.Surface]:
        """Load local tile images."""
        from wanderland.config import TileType
        tiles = {}
        mapping = {
            TileType.SAND: "local/sand_fantasy.png",
            TileType.GRASS: "local/grass-fantasy.png",
            TileType.FOREST: "local/tree_small.png",
            TileType.MOUNTAINS: "local/mountains_fantasy.png",
            TileType.HIGH_MOUNTAINS: "local/high_mountains_fantasy.png",
            TileType.WATER: "local/water_fantasy.png",
            TileType.CAVE: "local/cave_fantasy.png",
            TileType.CASTLE: "local/castle_fantasy.png",
            TileType.TOWN: "local/town_fantasy.png",
        }
        for tile_type, path in mapping.items():
            surface = self.load_image(path)
            if surface:
                tiles[tile_type] = surface
        return tiles
    
    def load_ui(self) -> Dict[str, pygame.Surface]:
        """Load UI assets."""
        ui = {}
        assets = {
            "menu": "menu_small.png",
            "inv_square": "inv_square.png",
            "inv_selector": "inv_selector.png",
            "healthbar": "healthbar.png",
            "mp_bar": "mp_bar.png",
            "bg": "map.png",
        }
        for key, path in assets.items():
            surface = self.load_image(path)
            if surface:
                ui[key] = surface
        return ui
    
    def load_player_sprites(self) -> Dict[str, pygame.Surface]:
        """Load player character sprites."""
        sprites = {}
        mapping = {
            "down": "naked.png",
            "up": "naked_up.png",
            "left": "naked_left.png",
            "right": "naked_right.png",
        }
        for direction, path in mapping.items():
            surface = self.load_image(path)
            if surface:
                sprites[direction] = surface
        return sprites
