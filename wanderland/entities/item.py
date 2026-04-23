"""Item and inventory system."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Item:
    """Game item."""
    name: Optional[str] = None
    image_path: Optional[str] = None
    item_id: int = 0
    is_equipment: bool = False
    is_consumable: bool = False
    is_stackable: bool = False
    count: int = 1
    description: str = ""


class ItemRegistry:
    """Central item database."""
    
    def __init__(self) -> None:
        self._items: List[Item] = []
        self._empty = Item()  # item_id=0 means empty
        self._items.append(self._empty)
        self._by_name: dict[str, int] = {}
    
    def register(self, name: str, image: str, equipment: bool = False,
                 consumable: bool = False, stackable: bool = False,
                 description: str = "") -> Item:
        item_id = len(self._items)
        item = Item(
            name=name,
            image_path=image,
            item_id=item_id,
            is_equipment=equipment,
            is_consumable=consumable,
            is_stackable=stackable,
            description=description
        )
        self._items.append(item)
        self._by_name[name] = item_id
        return item
    
    def get(self, item_id: int) -> Item:
        return self._items[item_id]
    
    def find(self, name: str) -> Optional[Item]:
        item_id = self._by_name.get(name)
        if item_id is not None:
            return self.get(item_id)
        return None
    
    def clone(self, name: str) -> Optional[Item]:
        """Get a fresh copy of an item."""
        original = self.find(name)
        if original is None:
            return None
        import copy
        return copy.copy(original)


# Global registry
REGISTRY = ItemRegistry()

# Register game items
REGISTRY.register("Stone Axe", "assets/items/axe_stone.png", equipment=True)
REGISTRY.register("Axe", "assets/items/axe.png", equipment=True)
REGISTRY.register("Branch", "assets/items/branch.png", equipment=True)
REGISTRY.register("Fibers", "assets/items/fibers.png", consumable=True, stackable=True)
REGISTRY.register("Sword", "assets/items/sword1.png", equipment=True)
REGISTRY.register("Berries", "assets/items/berries.png", consumable=True, stackable=True)
REGISTRY.register("Log", "assets/items/log.png", stackable=True, description="A big ole log...")
REGISTRY.register("Wood Block", "assets/items/wood_blocks.png", stackable=True, description="Little ole wood blocks")
REGISTRY.register("Workbench", "assets/items/workbench.png", stackable=True, description="A Workbench")
