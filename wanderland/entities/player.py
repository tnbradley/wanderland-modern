"""Player entity."""
from __future__ import annotations

from typing import List, Optional, Tuple

from wanderland.config import CONFIG
from wanderland.entities.item import Item, REGISTRY
from wanderland.world.tile import Tile


class Inventory:
    """Player inventory."""
    
    def __init__(self, size: int = 40) -> None:
        self._slots: List[Item] = [REGISTRY.get(0) for _ in range(size)]
        self._size = size
    
    @property
    def slots(self) -> List[Item]:
        return self._slots
    
    def add(self, item: Item) -> bool:
        """Add item to inventory. Returns True if successful."""
        # Try stacking first
        if item.is_stackable:
            for i, slot in enumerate(self._slots):
                if slot.item_id == item.item_id:
                    self._slots[i].count += item.count
                    return True
        
        # Find empty slot
        for i, slot in enumerate(self._slots):
            if slot.item_id == 0:
                import copy
                self._slots[i] = copy.copy(item)
                return True
        return False
    
    def swap(self, i: int, j: int) -> None:
        self._slots[i], self._slots[j] = self._slots[j], self._slots[i]
    
    def __getitem__(self, idx: int) -> Item:
        return self._slots[idx]
    
    def __len__(self) -> int:
        return self._size


class Player:
    """Player character."""
    
    def __init__(self, start_pos: Tuple[int, int]) -> None:
        self.x, self.y = start_pos
        self.x_local, self.y_local = start_pos
        self._sprite = "down"
        self.camera_x = self.x - CONFIG.width // 2
        self.camera_y = self.y - CONFIG.height // 2
        self.current_chunk: Tuple[int, int] = (23, 13)
        self.local_chunk: Tuple[int, int] = (6, 8)
        
        self.toolbar_size = 7
        self.inventory_size = 40
        self.inventory = Inventory(self.inventory_size)
        self.toolbar = Inventory(self.toolbar_size)
        
        self.selected_slot = 0  # 0-indexed
        self.is_local = False
        self.health_percent = 1.0
        self.mp_percent = 1.0
        self.level = 1
        
        # Tile neighbors (3x3 grid)
        self.tile_neighbors: List[List[Tile]] = []
        self.local_tile_neighbors: List[List[Tile]] = []
        
        self._add_starting_items()
    
    def _add_starting_items(self) -> None:
        axe = REGISTRY.find("Axe")
        if axe:
            self.toolbar.add(axe)
    
    @property
    def sprite_name(self) -> str:
        return self._sprite
    
    def set_sprite(self, direction: str) -> None:
        self._sprite = direction
    
    @property
    def grid_x(self) -> int:
        return self.x // CONFIG.cell_width
    
    @property
    def grid_y(self) -> int:
        return self.y // CONFIG.cell_height
    
    @property
    def local_grid_x(self) -> int:
        return self.x_local // CONFIG.cell_width
    
    @property
    def local_grid_y(self) -> int:
        return self.y_local // CONFIG.cell_height
    
    def move(self, dx: int, dy: int) -> None:
        if self.is_local:
            self.x_local += dx
            self.y_local += dy
            self.camera_x += dx
            self.camera_y += dy
        else:
            self.x += dx
            self.y += dy
            self.camera_x += dx
            self.camera_y += dy
    
    def update_camera(self, x: int, y: int) -> None:
        self.camera_x = x - CONFIG.width // 2
        self.camera_y = y - CONFIG.height // 2
    
    def toggle_local(self) -> None:
        self.is_local = not self.is_local
        if self.is_local:
            self.x_local = self.x
            self.y_local = self.y
            self.update_camera(self.x_local, self.y_local)
        else:
            self.update_camera(self.x, self.y)
    
    def select_slot(self, slot: int) -> None:
        self.selected_slot = max(0, min(slot, self.toolbar_size - 1))
    
    def get_current_position(self) -> Tuple[int, int]:
        if self.is_local:
            return (self.x_local, self.y_local)
        return (self.x, self.y)
