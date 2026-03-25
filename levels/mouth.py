import pygame
import random
from levels.level_base import BaseLevel


class MouthObstacle(pygame.sprite.Sprite):
    def __init__(self, x, sprite):
        super().__init__()
        self.image = sprite
        self.rect = pygame.Rect(x, 320, 40, 40)
        self.speed = 4


    def update(self):
        self.rect.x -= self.speed


    def is_off_screen(self):
        return self.rect.x < -40


    def reset_position(self, new_x):
        self.rect.x = new_x


class MouthObstacleManager:
    def __init__(self, obstacle_sprites):
        self.obstacles = pygame.sprite.Group()
        self.obstacle_sprites = obstacle_sprites
        self.speed = 4
        self.min_distance = 300
        self.dodged_count = 0
        self.initialize_obstacles()


    def initialize_obstacles(self):
        positions = [600, 900, 1200]
        for i, pos in enumerate(positions):
            obstacle = MouthObstacle(pos, self.obstacle_sprites[i])
            self.obstacles.add(obstacle)


    def update(self, player_rect):
        self.obstacles.update()
        for obstacle in self.obstacles:
            if obstacle.is_off_screen():
                new_pos = self.get_valid_position()
                obstacle.reset_position(new_pos)
                self.dodged_count += 1
            elif player_rect.colliderect(obstacle.rect):
                return True
        return False


    def get_valid_position(self):
        for _ in range(20):
            new_pos = random.randint(940, 1140)
            valid = True
            for obstacle in self.obstacles:
                if abs(new_pos - obstacle.rect.x) < self.min_distance:
                    valid = False
                    break
            if valid:
                return new_pos
        return random.randint(940, 1140)


    def draw(self, screen):
        self.obstacles.draw(screen)


    def reset(self):
        positions = [600, 900, 1200]
        for i, obstacle in enumerate(self.obstacles):
            obstacle.reset_position(positions[i])
        self.dodged_count = 0


    def clear_obstacles(self):
        self.obstacles.empty()
        self.dodged_count = 0  


class MouthLevel(BaseLevel):
    def __init__(self, config, obstacle_sprites, jump_sound=None):
        super().__init__(config, obstacle_sprites, jump_sound)
        self.obstacle_manager = MouthObstacleManager(obstacle_sprites)
   
 

