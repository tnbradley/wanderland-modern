"""Game renderer."""
from typing import Dict, List, Optional, Tuple

import pygame

from wanderland.config import CONFIG, TileType
from wanderland.entities.player import Player
from wanderland.render.assets import AssetLoader
from wanderland.world.tile import Tile


class Renderer:
    """Handles all game rendering."""
    
    def __init__(self, screen: pygame.Surface, assets: AssetLoader) -> None:
        self.screen = screen
        self.assets = assets
        self.tiles = assets.load_tiles()
        self.local_tiles = assets.load_local_tiles()
        self.ui = assets.load_ui()
        self.player_sprites = assets.load_player_sprites()
        self.font_large = pygame.font.SysFont("Plantin", 90)
        self.font_medium = pygame.font.SysFont("Plantin", 40)
        self.font_small = pygame.font.SysFont("Plantin", 20)
    
    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        self.screen.fill(color)
    
    def draw_map(self, game_map: List[List[Tile]], player: Player) -> None:
        """Draw the visible map tiles."""
        px, py = player.get_current_position()
        view = CONFIG.view_distance
        
        if player.is_local:
            grid_x, grid_y = player.local_grid_x, player.local_grid_y
        else:
            grid_x, grid_y = player.grid_x, player.grid_y
        
        for x in range(grid_x - view, grid_x + view):
            for y in range(grid_y - view, grid_y + view):
                if 0 <= x < len(game_map) and 0 <= y < len(game_map[0]):
                    tile = game_map[x][y]
                    tile_image = self._get_tile_image(tile, player.is_local)
                    if tile_image:
                        draw_x = x * CONFIG.cell_width - player.camera_x
                        draw_y = y * CONFIG.cell_height - player.camera_y
                        self.screen.blit(tile_image, (draw_x, draw_y))
    
    def _get_tile_image(self, tile: Tile, is_local: bool) -> Optional[pygame.Surface]:
        """Get the appropriate image for a tile."""
        if is_local:
            tiles = self.local_tiles
        else:
            tiles = self.tiles
        
        # Check for custom image first
        if tile.image_path:
            custom = self.assets.get(tile.image_path)
            if custom:
                return custom
        
        return tiles.get(tile.tile_type)
    
    def draw_player(self, player: Player) -> None:
        """Draw the player character."""
        px, py = player.get_current_position()
        sprite = self.player_sprites.get(player.sprite_name)
        if sprite:
            self.screen.blit(sprite, (px - player.camera_x, py - player.camera_y))
    
    def draw_ui(self, player: Player, menu_open: bool = False) -> None:
        """Draw UI elements."""
        px, py = player.get_current_position()
        
        # Health and MP bars
        healthbar = self.ui.get("healthbar")
        mp_bar = self.ui.get("mp_bar")
        
        if healthbar:
            self.screen.blit(healthbar, (px - player.camera_x - 432, py - player.camera_y + 256))
        if mp_bar:
            self.screen.blit(mp_bar, (px - player.camera_x - 264, py - player.camera_y + 256))
        
        # Health fill
        bar_width = int(120 * player.health_percent)
        if bar_width > 0:
            pygame.draw.rect(
                self.screen, (239, 58, 12),
                (px - player.camera_x - 429, py - player.camera_y + 268, bar_width, 16)
            )
        
        # MP fill
        mp_width = int(120 * player.mp_percent)
        if mp_width > 0:
            pygame.draw.rect(
                self.screen, (95, 205, 228),
                (px - player.camera_x - 261, py - player.camera_y + 268, mp_width, 16)
            )
        
        # Toolbar
        inv_square = self.ui.get("inv_square")
        inv_selector = self.ui.get("inv_selector")
        
        if inv_square:
            for i in range(player.toolbar_size):
                x = px - player.camera_x - 96 + (i * 32)
                y = py - player.camera_y + 256
                self.screen.blit(inv_square, (x, y))
                
                item = player.toolbar[i]
                if item.item_id != 0 and item.image_path:
                    item_img = self.assets.get(item.image_path)
                    if item_img:
                        self.screen.blit(item_img, (x, y))
        
        if inv_selector:
            sel_x = px - player.camera_x - 128 + (player.selected_slot * 32)
            sel_y = py - player.camera_y + 256
            self.screen.blit(inv_selector, (sel_x, sel_y))
        
        # Inventory menu
        if menu_open:
            menu = self.ui.get("menu")
            if menu:
                self.screen.blit(menu, (px - player.camera_x - 112, py - player.camera_y - 112))
            
            for i in range(len(player.inventory)):
                item = player.inventory[i]
                if item.item_id != 0 and item.image_path:
                    item_img = self.assets.get(item.image_path)
                    if item_img:
                        col = i % 10
                        row = i // 10
                        ix = px - player.camera_x - 80 + (col * 32)
                        iy = py - player.camera_y + 80 + (row * 32)
                        self.screen.blit(item_img, (ix, iy))
    
    def draw_title_screen(self) -> bool:
        """Draw title screen. Returns True if player clicked start."""
        bg = self.ui.get("bg")
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill((0, 0, 0))
        
        title = self.font_large.render("Wanderland", True, (255, 0, 0))
        start = self.font_medium.render("New Game", True, (255, 0, 0))
        
        title_x = CONFIG.width // 2 - title.get_width() // 2
        start_x = CONFIG.width // 2 - start.get_width() // 2
        
        self.screen.blit(title, (title_x, 100))
        self.screen.blit(start, (start_x, 200))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                start_rect = start.get_rect(topleft=(start_x, 200))
                if start_rect.collidepoint(mx, my):
                    return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_F11:
                    self._toggle_fullscreen()
        
        return False
    
    def draw_loading(self, text: str) -> None:
        """Draw loading screen."""
        bg = self.ui.get("bg")
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill((0, 0, 0))
        
        label = self.font_medium.render(text, True, (255, 0, 0))
        self.screen.blit(label, (CONFIG.width // 2 - label.get_width() // 2, 100))
        pygame.display.flip()
    
    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        global _fullscreen
        _fullscreen = not getattr(self, '_fullscreen', False)
        if _fullscreen:
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)
        else:
            pygame.display.set_mode((CONFIG.width, CONFIG.height), pygame.DOUBLEBUF)
    
    def present(self) -> None:
        """Update display."""
        pygame.display.flip()
