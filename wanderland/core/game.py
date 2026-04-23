"""Game state and main loop."""
from typing import List, Optional, Tuple

import pygame

from wanderland.config import CONFIG, TileType
from wanderland.entities.crafting import CRAFTING
from wanderland.entities.item import REGISTRY
from wanderland.entities.player import Player
from wanderland.render.assets import AssetLoader
from wanderland.render.renderer import Renderer
from wanderland.world.generator import WorldGenerator
from wanderland.world.tile import Tile


class GameState:
    """Main game state manager."""
    
    def __init__(self) -> None:
        try:
            pygame.mixer.pre_init(44100, 16, 2, 4096)
        except (NotImplementedError, AttributeError):
            pass
        pygame.init()
        
        self.screen = pygame.display.set_mode((CONFIG.width, CONFIG.height), pygame.DOUBLEBUF)
        pygame.display.set_caption("Wanderland")
        
        self.assets = AssetLoader()
        self.renderer = Renderer(self.screen, self.assets)
        self.clock = pygame.time.Clock()
        
        self.player: Optional[Player] = None
        self.generator: Optional[WorldGenerator] = None
        self.game_map: List[List[Tile]] = []
        self.running = False
        self.menu_open = False
        self.dragging_toolbar = -1
        self.dragging_inv = -1
    
    def run(self) -> None:
        """Main entry point."""
        self._show_title()
        self._initialize_game()
        self._game_loop()
    
    def _show_title(self) -> None:
        """Show title screen until player starts."""
        while True:
            if self.renderer.draw_title_screen():
                break
            self.clock.tick(CONFIG.fps)
    
    def _initialize_game(self) -> None:
        """Initialize world and player."""
        self.renderer.draw_loading("Generating World...")
        
        self.generator = WorldGenerator()
        self.generator.generate()
        
        start_chunk = self.generator.find_starting_chunk()
        start_x = start_chunk[0] * CONFIG.map_width * CONFIG.cell_width + 15 * CONFIG.cell_width
        start_y = start_chunk[1] * CONFIG.map_height * CONFIG.cell_height + 15 * CONFIG.cell_height
        
        self.player = Player((start_x, start_y))
        self.player.current_chunk = start_chunk
        
        self.renderer.draw_loading("Loading Chunks...")
        self.game_map = self.generator.load_surrounding_chunks(self.player)
        self.player.tile_neighbors = self.generator.get_neighbors(
            self.player.grid_x, self.player.grid_y, self.player.current_chunk
        )
        
        # Play placeholder audio
        try:
            if hasattr(pygame, 'mixer') and hasattr(pygame.mixer, 'music'):
                pygame.mixer.music.load("assets/audio/placeholder.wav")
                pygame.mixer.music.play()
        except (pygame.error, AttributeError, NotImplementedError):
            pass
    
    def _game_loop(self) -> None:
        """Main game loop."""
        self.running = True
        
        while self.running:
            self.clock.tick(CONFIG.fps)
            self._handle_input()
            self._update()
            self._render()
        
        pygame.quit()
    
    def _handle_input(self) -> None:
        """Process input events."""
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F11:
                    self._toggle_fullscreen()
                elif event.key == pygame.K_e:
                    self.menu_open = not self.menu_open
                elif event.key == pygame.K_RETURN:
                    self._toggle_local_mode()
                elif event.key == pygame.K_p:
                    self._debug_actions()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouse_up(event)
        
        # Continuous key input (movement)
        keys = pygame.key.get_pressed()
        self._handle_movement(keys)
    
    def _handle_movement(self, keys) -> None:
        """Handle WASD movement."""
        if not self.player:
            return
        
        dx, dy = 0, 0
        direction = self.player.sprite_name
        
        if keys[pygame.K_w]:
            dy = -CONFIG.cell_height
            direction = "up"
        elif keys[pygame.K_s]:
            dy = CONFIG.cell_height
            direction = "down"
        elif keys[pygame.K_a]:
            dx = -CONFIG.cell_width
            direction = "left"
        elif keys[pygame.K_d]:
            dx = CONFIG.cell_width
            direction = "right"
        
        if dx != 0 or dy != 0:
            self.player.set_sprite(direction)
            
            # Check collision
            target_x = self.player.grid_x + dx // CONFIG.cell_width
            target_y = self.player.grid_y + dy // CONFIG.cell_height
            
            if (0 <= target_x < len(self.game_map) and 
                0 <= target_y < len(self.game_map[0]) and
                not self.game_map[target_x][target_y].blocks_path):
                
                self.player.move(dx, dy)
                self._update_chunk_position()
    
    def _update_chunk_position(self) -> None:
        """Update chunk when player crosses boundaries."""
        if not self.player or not self.generator:
            return
        
        grid_x = self.player.grid_x
        grid_y = self.player.grid_y
        
        # Check for chunk boundary crossing
        chunk_changed = False
        cx, cy = self.player.current_chunk
        
        if grid_x < 32:
            cx -= 1
            chunk_changed = True
        elif grid_x >= 64:
            cx += 1
            chunk_changed = True
        
        if grid_y < 32:
            cy -= 1
            chunk_changed = True
        elif grid_y >= 64:
            cy += 1
            chunk_changed = True
        
        if chunk_changed:
            self.player.current_chunk = (cx, cy)
            self.game_map = self.generator.load_surrounding_chunks(self.player)
            self.player.update_camera(
                self.player.x if not self.player.is_local else self.player.x_local,
                self.player.y if not self.player.is_local else self.player.y_local
            )
        
        # Update neighbors
        self.player.tile_neighbors = self.generator.get_neighbors(
            self.player.grid_x, self.player.grid_y, self.player.current_chunk
        )
    
    def _toggle_local_mode(self) -> None:
        """Toggle between overworld and local view."""
        if not self.player:
            return
        
        self.player.toggle_local()
        
        if self.player.is_local:
            # Generate local map for current tile
            pass  # TODO: Implement local map generation
        else:
            self.game_map = self.generator.load_surrounding_chunks(self.player)
    
    def _handle_mouse_down(self, event) -> None:
        """Handle mouse button press."""
        if not self.player:
            return
        
        mx, my = pygame.mouse.get_pos()
        px, py = self.player.get_current_position()
        
        # Check toolbar
        for i in range(self.player.toolbar_size):
            tx = px - self.player.camera_x - 96 + (i * 32)
            ty = py - self.player.camera_y + 256
            if ty <= my <= ty + 32 and tx <= mx <= tx + 32:
                if self.player.toolbar[i].item_id != 0:
                    self.dragging_toolbar = i
                return
        
        # Check inventory
        if self.menu_open:
            for i in range(len(self.player.inventory)):
                col = i % 10
                row = i // 10
                ix = px - self.player.camera_x - 80 + (col * 32)
                iy = py - self.player.camera_y + 80 + (row * 32)
                if iy <= my <= iy + 32 and ix <= mx <= ix + 32:
                    if self.player.inventory[i].item_id != 0:
                        self.dragging_inv = i
                    return
    
    def _handle_mouse_up(self, event) -> None:
        """Handle mouse button release."""
        if not self.player:
            return
        
        mx, my = pygame.mouse.get_pos()
        px, py = self.player.get_current_position()
        
        # Toolbar drop
        if self.dragging_toolbar >= 0:
            for i in range(self.player.toolbar_size):
                tx = px - self.player.camera_x - 96 + (i * 32)
                ty = py - self.player.camera_y + 256
                if ty <= my <= ty + 32 and tx <= mx <= tx + 32:
                    self.player.toolbar.swap(self.dragging_toolbar, i)
                    break
            self.dragging_toolbar = -1
        
        # Inventory drop
        if self.dragging_inv >= 0:
            for i in range(len(self.player.inventory)):
                col = i % 10
                row = i // 10
                ix = px - self.player.camera_x - 80 + (col * 32)
                iy = py - self.player.camera_y + 80 + (row * 32)
                if iy <= my <= iy + 32 and ix <= mx <= ix + 32:
                    self.player.inventory.swap(self.dragging_inv, i)
                    break
            self.dragging_inv = -1
        
        # Scroll wheel
        if event.button == 4:  # Scroll up
            self.player.select_slot(self.player.selected_slot - 1)
        elif event.button == 5:  # Scroll down
            self.player.select_slot(self.player.selected_slot + 1)
    
    def _debug_actions(self) -> None:
        """Debug/test actions."""
        if not self.player:
            return
        
        # Damage test
        self.player.health_percent = max(0, self.player.health_percent - 0.05)
        
        # Crafting test
        log = REGISTRY.find("Log")
        block = REGISTRY.find("Wood Block")
        if log and block:
            ingredients = [REGISTRY.clone("Log") for _ in range(3)]
            ingredients.extend([REGISTRY.clone("Wood Block") for _ in range(4)])
            result = CRAFTING.craft(ingredients)
            if result:
                print(f"Crafted: {result[0]} x{result[1]}")
    
    def _update(self) -> None:
        """Update game state."""
        pass
    
    def _render(self) -> None:
        """Render frame."""
        self.renderer.clear()
        
        if self.game_map and self.player:
            self.renderer.draw_map(self.game_map, self.player)
            self.renderer.draw_player(self.player)
            self.renderer.draw_ui(self.player, self.menu_open)
        
        self.renderer.present()
    
    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen."""
        # Handled by renderer
        pass
