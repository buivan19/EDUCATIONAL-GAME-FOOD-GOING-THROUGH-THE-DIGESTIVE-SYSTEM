import pygame
from shared.player import Player


class BaseLevel:
    def __init__(self, config, obstacle_sprites, jump_sound=None):
        self.config = config
        self.obstacle_sprites = obstacle_sprites
        self.jump_sound = jump_sound
        self.player = Player(100, config["ground_level"])
        self.obstacle_manager = None  
        self.background = self._load_background()


    def handle_jump(self):
        self.player.jump()
        self._play_jump_sound()
       
    def _load_background(self):
        try:
            bg_full = pygame.image.load(self.config["background"])
            bg_full = pygame.transform.scale(bg_full, (self.config["width"], self.config["height"]))
            background_surface = pygame.Surface((self.config["width"], 440))
            background_surface.blit(bg_full, (0, 0), (0, 0, self.config["width"], 440))
            return background_surface
        except:
            background_surface = pygame.Surface((self.config["width"], 440))
            background_surface.fill((0, 0, 0))
            return background_surface
       
    def _play_jump_sound(self):
        """Helper method to play jump sound if available"""
        if self.jump_sound:
            self.jump_sound.play()


    def update(self):
        """Update game state - returns True if collision occurred"""
        self.player.update(self.config["ground_level"])
        collision = self.obstacle_manager.update(self.player.rect)
        return collision


    def draw(self, screen):
        """Draw level elements"""
        screen.blit(self.background, (0, 0))
        pygame.draw.rect(screen, self.config["ground_color"],
                        [0, self.config["ground_level"],
                        self.config["width"],
                        self.config["height"] - self.config["ground_level"]])
        screen.blit(self.player.image, self.player.rect)
        self.obstacle_manager.draw(screen)


    def reset(self):
        """Reset level to initial state"""
        self.player.reset(100, self.config["ground_level"])
        self.obstacle_manager.reset()


    def get_dodged_count(self):
        """Get number of obstacles dodged"""
        return self.obstacle_manager.dodged_count

