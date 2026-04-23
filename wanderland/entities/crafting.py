"""Crafting system."""
from typing import Dict, List, Tuple, Optional

from wanderland.entities.item import Item, REGISTRY

RecipeResult = Tuple[str, int]


class CraftingSystem:
    """Handles recipes and crafting."""
    
    def __init__(self) -> None:
        self._recipes: Dict[str, RecipeResult] = {}
    
    def add_recipe(self, ingredients: List[str], output: str, count: int = 1) -> None:
        """Register a crafting recipe."""
        key = "/".join(sorted(ingredients)) + "/"
        self._recipes[key] = (output, count)
    
    def craft(self, ingredients: List[Item]) -> Optional[RecipeResult]:
        """Try to craft with given ingredients. Returns (item_name, count) or None."""
        names = []
        for item in ingredients:
            if item.name:
                for _ in range(item.count):
                    names.append(item.name)
        
        key = "/".join(sorted(names)) + "/"
        return self._recipes.get(key)
    
    def get_recipe_names(self) -> List[str]:
        """Get all registered recipe output names."""
        return [r[0] for r in self._recipes.values()]


# Global crafting system
CRAFTING = CraftingSystem()
CRAFTING.add_recipe(["Log"], "Wood Block", 8)
CRAFTING.add_recipe(["Log", "Log", "Log", "Wood Block", "Wood Block", "Wood Block", "Wood Block"], "Workbench", 1)
