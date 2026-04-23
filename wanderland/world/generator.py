"""World generation using Voronoi + Simplex noise."""
from __future__ import annotations

import math
import os
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageFilter

try:
    import opensimplex
except ImportError:
    opensimplex = None

from wanderland.config import CONFIG, TileType, BG_COLOR, MT_TOP, MT_COLOR, GRASS_COLOR, TREES_COLOR, SAND_COLOR, SHALLOWS_COLOR
from wanderland.world.tile import OverworldTile, LocalTile


class WorldGenerator:
    """Procedural world generator."""
    
    def __init__(self, seed: Optional[int] = None) -> None:
        self.seed = seed or random.randint(0, 10000)
        self.simplex = opensimplex.OpenSimplex(seed=self.seed) if opensimplex else None
        self.rand_size = random.randint(5000, 10000)
        self.rand_points = random.randint(4000, self.rand_size)
        self.chunks: List[List[List[List[OverworldTile]]]] = []
        self.local_chunks: Dict[str, List[List[List[List[LocalTile]]]]] = {}
        self.map_image: Optional[Image.Image] = None
        self._blocks_dir = Path("assets/blocks")
    
    def generate(self) -> None:
        """Generate the world map."""
        self._generate_voronoi()
        self._process_map()
        self._create_blocks()
        self.chunks = self._create_chunks()
    
    def _generate_voronoi(self) -> None:
        """Generate Voronoi diagram."""
        # Simple voronoi implementation
        from wanderland.world.voronoi import generate_voronoi
        generate_voronoi(self.rand_points, self.rand_size, self.rand_size)
    
    def _process_map(self) -> None:
        """Process the voronoi map with noise."""
        im = Image.open("assets/voronoi_map.png")
        im = im.filter(ImageFilter.SMOOTH).filter(ImageFilter.BLUR).filter(ImageFilter.SHARPEN)
        im = im.convert('RGBA')
        width, height = im.size
        
        # Create background
        bg = Image.new('RGBA', (width, height), color=BG_COLOR)
        bg.save("assets/background.png")
        
        px = im.load()
        radius = int(0.25 * width)
        inner_radius = int(0.20 * width)
        
        for y in range(height):
            for x in range(width):
                if px[x, y][1] == 128:  # Green pixel
                    water_set = self._check_water_edge(px, x, y, width, height)
                    
                    if self.simplex:
                        value = self.simplex.noise2d(x / 6, y / 6)
                        shore_value = self.simplex.noise2d(x / 8, y / 8)
                    else:
                        value = random.uniform(-1, 1)
                        shore_value = random.uniform(-1, 1)
                    
                    distance = math.sqrt((x - width // 2) ** 2 + (y - 0) ** 2)
                    
                    if distance < radius:
                        if distance > inner_radius:
                            rgb = TREES_COLOR if random.randint(0, 15) == 3 else MT_TOP
                        else:
                            rgb = MT_TOP
                    elif value > 0.8:
                        rgb = MT_TOP
                    elif value > 0.5:
                        cave_chance = random.randint(0, 100)
                        castle_chance = random.randint(0, 260)
                        if cave_chance == 42:
                            rgb = (2, 2, 2)
                        elif castle_chance == 42:
                            rgb = (196, 0, 0)
                        else:
                            rgb = MT_COLOR
                    elif value > -0.2:
                        grass_chance = random.randint(0, 5)
                        village_chance = random.randint(0, 400)
                        if grass_chance == 4:
                            rgb = GRASS_COLOR
                        elif village_chance == 42:
                            rgb = (75, 0, 137)
                        else:
                            rgb = TREES_COLOR
                    elif value > -0.65:
                        tree_chance = random.randint(0, 5)
                        village_chance = random.randint(0, 400)
                        if village_chance == 42:
                            rgb = (75, 0, 137)
                        elif tree_chance == 4:
                            rgb = TREES_COLOR
                        else:
                            rgb = GRASS_COLOR
                    elif value > -0.75:
                        rgb = SAND_COLOR
                    else:
                        rgb = (0, 88, 248)
                    
                    if water_set:
                        village_chance = random.randint(0, 200)
                        if shore_value > 0.3:
                            rgb = (255, 255, 255, 0)
                        elif -0.1 < shore_value < 0.3:
                            rgb = SHALLOWS_COLOR if village_chance != 42 else (75, 0, 137)
                        elif -0.5 < shore_value < -0.2:
                            rgb = SAND_COLOR if village_chance != 42 else (75, 0, 137)
                        elif shore_value < -0.7:
                            rgb = SAND_COLOR
                    
                    px[x, y] = rgb
        
        self.map_image = Image.alpha_composite(Image.open("assets/background.png"), im)
        self.map_image.save("assets/map.png")
    
    def _check_water_edge(self, px, x: int, y: int, w: int, h: int) -> bool:
        """Check if pixel is at water edge."""
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                if px[nx, ny] == (255, 255, 255, 0):
                    return True
        return False
    
    def _create_blocks(self) -> None:
        """Slice map into 32x32 blocks."""
        self._blocks_dir.mkdir(exist_ok=True)
        w, h = self.map_image.size
        
        for x in range(1, w // 32):
            for y in range(1, h // 32):
                left = 32 * (x - 1)
                top = 32 * (y - 1)
                right = 32 * x
                bottom = 32 * y
                block = self.map_image.crop((left, top, right, bottom))
                block.save(self._blocks_dir / f"block{x}_{y}.png", 'png')
    
    def _create_chunks(self) -> List:
        """Create chunk grid from blocks."""
        block_count = len(list(self._blocks_dir.glob("*.png")))
        w, h = self.map_image.size
        chunks: List[List[List[List[OverworldTile]]]] = []
        
        for x in range(0, w // 32 - 1):
            chunks.append([])
            for y in range(0, h // 32 - 1):
                filename = self._blocks_dir / f"block{x+1}_{y+1}.png"
                im = Image.open(filename)
                chunks[x].append(self._create_tile_map(im, (x, y)))
        
        return chunks
    
    def _create_tile_map(self, im: Image.Image, chunk: Tuple[int, int]) -> List[List[OverworldTile]]:
        """Convert image to tile grid."""
        px = im.load()
        tiles: List[List[OverworldTile]] = []
        
        for x in range(CONFIG.map_width):
            tiles.append([])
            for y in range(CONFIG.map_height):
                tile = OverworldTile(x, y, TileType.WATER, True, chunk)
                
                r, g, b = px[x, y][:3]
                if r == 248:  # Sand
                    tile.set_tile(TileType.SAND)
                    tile.blocks_path = False
                elif g == 184:  # Grass
                    tile.set_tile(TileType.GRASS)
                    tile.blocks_path = False
                elif g == 88 and b == 0:  # Trees
                    tile.set_tile(TileType.FOREST)
                    tile.blocks_path = False
                elif g == 124:  # Mountains
                    tile.set_tile(TileType.MOUNTAINS)
                    tile.blocks_path = False
                elif r == 252:  # High mountains
                    tile.set_tile(TileType.HIGH_MOUNTAINS)
                    tile.blocks_path = False
                elif r == 2 or g == 2 or b == 2:  # Cave
                    tile.set_tile(TileType.CAVE)
                    tile.blocks_path = False
                elif r == 196:  # Castle
                    tile.set_tile(TileType.CASTLE)
                    tile.blocks_path = False
                elif r == 75:  # Town
                    tile.set_tile(TileType.TOWN)
                    tile.blocks_path = False
                
                tile.set_image()
                tiles[x].append(tile)
        
        return tiles
    
    def get_chunk(self, x: int, y: int) -> Optional[List[List[OverworldTile]]]:
        """Get chunk at coordinates."""
        if 0 <= x < len(self.chunks) and 0 <= y < len(self.chunks[0]):
            return self.chunks[x][y]
        return None
    
    def get_neighbors(self, x: int, y: int, chunk: Tuple[int, int], 
                      use_local: bool = False) -> List[List[Tile]]:
        """Get 3x3 neighbor grid."""
        cx, cy = chunk
        neighbors: List[List[Tile]] = []
        
        for j in range(y - 1, y + 2):
            row: List[Tile] = []
            for i in range(x - 1, x + 2):
                ni, nj = i, j
                nc_x, nc_y = cx, cy
                
                if j < 0:
                    nc_y -= 1
                    nj = CONFIG.map_height - 1
                elif j >= CONFIG.map_height:
                    nc_y += 1
                    nj = 0
                
                if i < 0:
                    nc_x -= 1
                    ni = CONFIG.map_width - 1
                elif i >= CONFIG.map_width:
                    nc_x += 1
                    ni = 0
                
                if use_local:
                    # Local chunk lookup would go here
                    row.append(OverworldTile(ni, nj, TileType.GRASS, False, (nc_x, nc_y)))
                else:
                    chunk_data = self.get_chunk(nc_x, nc_y)
                    if chunk_data:
                        row.append(chunk_data[ni][nj])
                    else:
                        row.append(OverworldTile(ni, nj, TileType.WATER, True, (nc_x, nc_y)))
            
            neighbors.append(row)
        
        return neighbors
    
    def load_surrounding_chunks(self, player) -> List[List[OverworldTile]]:
        """Load 3x3 chunk grid around player."""
        cx, cy = player.current_chunk
        size = CONFIG.map_height * 3
        result: List[List[OverworldTile]] = []
        
        for _ in range(size):
            result.append([OverworldTile(0, 0, TileType.WATER, True) for _ in range(size)])
        
        for j_idx, j in enumerate(range(cy - 1, cy + 2)):
            for i_idx, i in enumerate(range(cx - 1, cx + 2)):
                chunk = self.get_chunk(i, j)
                if not chunk:
                    continue
                
                for y in range(CONFIG.map_height):
                    for x in range(CONFIG.map_width):
                        c_x = x + i_idx * CONFIG.map_width
                        c_y = y + j_idx * CONFIG.map_height
                        result[c_x][c_y] = chunk[x][y]
        
        return result
    
    def find_starting_chunk(self) -> Tuple[int, int]:
        """Find a suitable starting location."""
        start_weight = 22
        for i, row in enumerate(self.chunks):
            if i > start_weight:
                for j, chunk in enumerate(row):
                    center = chunk[15][15]
                    if center.tile_type in (TileType.GRASS, TileType.FOREST):
                        return (i, j)
        return (len(self.chunks) // 2, len(self.chunks[0]) // 2)
