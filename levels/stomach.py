import pygame
import random
import math
from levels.level_base import BaseLevel


class StomachObstacle(pygame.sprite.Sprite):
    def __init__(self, x, sprite, kind, manager):
        super().__init__()
        self.base_sprite = sprite
        self.kind = kind
        self.manager = manager
        self.osc_phase = random.uniform(0, math.pi)
        self.osc_amplitude = random.randint(18, 32)
        self.osc_speed = random.uniform(0.08, 0.14)
        self.image = self.base_sprite.copy()
        self.rect = pygame.Rect(x, 320, 40, 40)
        self._apply_kind_shape()


    def _apply_kind_shape(self):
        w, h = 40, 40
        y = 320


        # The 'tall' configuration code has been removed.
        if self.kind == "flying":
            y = 320 - 120
            self.image = self.base_sprite.copy()
        elif self.kind == "moving":
            y = 350 - 30
            self.image = self.base_sprite.copy()
        elif self.kind == "fast":
            self.image = self.base_sprite.copy()
        else:
            self.image = self.base_sprite.copy()


        self.rect = pygame.Rect(self.rect.x, y, w, self.image.get_height())


    def update(self):
        speed = self.manager.get_current_speed()
        if self.kind == "fast":
            speed *= 1.35
        self.rect.x -= int(speed)


        if self.kind == "flying":
            self.osc_phase += self.osc_speed
            base_y = 320 - 120
            self.rect.y = base_y + int(self.osc_amplitude * math.sin(self.osc_phase))
        elif self.kind == "moving":
            self.osc_phase += self.osc_speed
            base_y = 320 - 30
            self.rect.y = base_y + int(30 * math.sin(self.osc_phase))


    def is_off_screen(self):
        return self.rect.x < -60


    def reset_position(self, new_x, new_kind=None):
        self.rect.x = new_x
        if new_kind is not None:
            self.kind = new_kind
            self._apply_kind_shape()
        self.osc_phase = random.uniform(0, math.pi)


class StomachObstacleManager:
    def __init__(self, obstacle_sprites):
        self.obstacles = pygame.sprite.Group()
        self.obstacle_sprites = obstacle_sprites
        self.base_speed = 4
        self.min_distance = 300
        self.dodged_count = 0
        # Removed "tall" from the list of kinds
        self.kinds = ["ground", "flying", "moving", "fast"]
        self._init_obstacles()


    def _init_obstacles(self):
        positions = [600, 900, 1200]
        for i, pos in enumerate(positions):
            kind = random.choice(self.kinds if i > 0 else ["ground"])  # Original was ["ground", "tall"]
            sprite = self.obstacle_sprites[i % len(self.obstacle_sprites)]
            self.obstacles.add(StomachObstacle(pos, sprite, kind, self))


    def get_current_speed(self):
        return min(self.base_speed + 0.8 * (self.dodged_count // 5), 12)


    def update(self, player_rect):
        self.obstacles.update()
        for obstacle in self.obstacles:
            if obstacle.is_off_screen():
                new_x = self._get_valid_spawn_x()
                new_kind = self._pick_next_kind()
                obstacle.reset_position(new_x, new_kind)
                self.dodged_count += 1
            elif player_rect.colliderect(obstacle.rect):
                return True
        return False


    def _pick_next_kind(self):
        r = random.random()
        progress = min(self.dodged_count / 20.0, 1.0)
        if r < 0.20 + 0.30 * progress:
            return "fast"
        if r < 0.45 + 0.25 * progress:
            return "moving"
        if r < 0.70 + 0.20 * progress:
            return "flying"
        return "ground"


    def _get_valid_spawn_x(self):
        min_distance = 240
        for _ in range(20):
            new_x = random.randint(900, 1100)
            valid = True
        for obstacle in self.obstacles:
                if abs(new_x - obstacle.rect.x) < min_distance:
                    valid = False
                    break
        if valid:
                if random.random() < 0.3:
                    return new_x - random.randint(10, 30)
                return new_x
       
        return random.randint(940, 1140)


    def draw(self, screen):
        self.obstacles.draw(screen)


    def reset(self):
        positions = [600, 900, 1200]
        for i, obstacle in enumerate(self.obstacles):
            obstacle.reset_position(positions[i], new_kind=random.choice(self.kinds))
        self.dodged_count = 0


    def clear_obstacles(self):
        self.obstacles.empty()
        self.dodged_count = 0


class StomachLevel(BaseLevel):
    def __init__(self, config, obstacle_sprites, jump_sound=None):
        super().__init__(config, obstacle_sprites, jump_sound)
        self.obstacle_manager = StomachObstacleManager(obstacle_sprites)


   

