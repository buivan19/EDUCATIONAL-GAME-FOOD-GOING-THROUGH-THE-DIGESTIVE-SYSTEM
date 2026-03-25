import pygame
import random
import math
from levels.level_base import BaseLevel


class IntestineObstacle(pygame.sprite.Sprite):
    def __init__(self, x, sprite, kind, manager):
        super().__init__()
        self.base_sprite = sprite
        self.kind = kind  
        self.manager = manager
        self.osc_phase = random.uniform(0, math.pi)
        self.osc_amplitude = random.randint(24, 40)
        self.osc_speed = random.uniform(0.12, 0.20)
        self.image = self.base_sprite.copy()
        self.rect = pygame.Rect(x, 340, 40, 40)
        self._apply_kind_shape(reset_x=False)


    def _apply_kind_shape(self, reset_x=True):
        x = self.rect.x
        w, h = 40, 40
        y = 340


        if self.kind == "flying":
            y = 340 - 120
            self.image = self.base_sprite.copy()
        elif self.kind == "moving":
            self.image = self.base_sprite.copy()
        elif self.kind == "fast":
            self.image = self.base_sprite.copy()
        elif self.kind == "microvilli":
            self.image = self.base_sprite.copy()
        else:
            self.image = self.base_sprite.copy()


        self.rect = pygame.Rect(x, y, w, self.image.get_height())


    def update(self):
        speed = self.manager.get_current_speed()
        if self.kind == "fast":
            speed *= 1.6
        self.rect.x -= int(speed)
        if self.kind == "flying":
            self.osc_phase += self.osc_speed
            base_y = 340 - 120
            self.rect.y = base_y + int(self.osc_amplitude * math.sin(self.osc_phase))
        elif self.kind == "moving":
            self.osc_phase += self.osc_speed
            base_y = 340 - 50
            self.rect.y = base_y + int(50 * math.sin(self.osc_phase))


    def is_off_screen(self):
        return self.rect.x < -60


    def reset_position(self, new_x, new_kind=None):
        self.rect.x = new_x
        if new_kind is not None:
            self.kind = new_kind
            self._apply_kind_shape(reset_x=True)
        self.osc_phase = random.uniform(0, math.pi)


class IntestineObstacleManager:
    def __init__(self, obstacle_sprites):
        self.obstacles = pygame.sprite.Group()
        self.obstacle_sprites = obstacle_sprites
        self.base_speed = 6  
        self.min_distance = 220
        self.dodged_count = 0
        self.kinds = ["ground", "microvilli", "flying", "moving", "fast"]
        self._init_obstacles()


    def _init_obstacles(self):
        positions = [600, 850, 1100, 1350]
        for i, pos in enumerate(positions):
            kind_pool = self.kinds if i > 0 else ["ground", "microvilli"]
            kind = random.choice(kind_pool)
            sprite = self.obstacle_sprites[i % len(self.obstacle_sprites)]
            self.obstacles.add(IntestineObstacle(pos, sprite, kind, self))


    def get_current_speed(self):
        return min(self.base_speed + 1.0 * (self.dodged_count // 3), 16)


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
        progress = min(self.dodged_count / 15.0, 1.0)
        if r < 0.30 + 0.25 * progress:
            return "fast"
        if r < 0.60 + 0.20 * progress:
            return "moving"
        if r < 0.80 + 0.15 * progress:
            return "flying"
        if r < 0.90:  
            return "microvilli"
       
        return "ground"


    def _get_valid_spawn_x(self):
        dynamic_min = max(150, int(self.min_distance - min(self.dodged_count * 4, 140)))  
        for _ in range(24):
            new_x = random.randint(900, 1200)  
            if all(abs(new_x - o.rect.x) >= dynamic_min for o in self.obstacles):
                if random.random() < 0.35:
                    return new_x - random.randint(40, 100)  
                return new_x
        return random.randint(900, 1100)  


    def draw(self, screen):
        self.obstacles.draw(screen)


    def reset(self):
        positions = [600, 850, 1100, 1350]
        obstacles_list = list(self.obstacles)
        for i, obstacle in enumerate(obstacles_list):
            if i < len(positions):
                kind_pool = self.kinds if i > 0 else ["ground", "microvilli"]
                obstacle.reset_position(positions[i], new_kind=random.choice(kind_pool))
        self.dodged_count = 0


    def clear_obstacles(self):
        self.obstacles.empty()
        self.dodged_count = 0


class IntestinesLevel(BaseLevel):
    def __init__(self, config, obstacle_sprites, jump_sound=None):
        super().__init__(config, obstacle_sprites, jump_sound)
        self.obstacle_manager = IntestineObstacleManager(obstacle_sprites)


   

