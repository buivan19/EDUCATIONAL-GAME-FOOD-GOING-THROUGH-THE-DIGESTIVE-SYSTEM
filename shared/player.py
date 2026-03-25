import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, ground_level, size=60):  # Changed parameter name to be clearer
        super().__init__()
       
        try:
            self.image = pygame.image.load("asset/player.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (size, size))
        except:
            print("Could not load player image, using placeholder")
            self.image = pygame.Surface((size, size))
            self.image.fill((255, 0, 0))  # Red color to make it visible
       
        # Position so bottom touches ground_level
        self.rect = pygame.Rect(x, ground_level - size, size, size)
        self.y_change = 0
        self.gravity = 2
        self.size = size


    def update(self, ground_level):
        if self.y_change > 0 or self.rect.y < ground_level - self.size:
            self.rect.y -= self.y_change
            self.y_change -= self.gravity


        # When player hits the ground
        if self.rect.y >= ground_level - self.size:
            self.rect.y = ground_level - self.size
            if self.y_change < 0:
                self.y_change = 0


    def jump(self):
        if self.y_change == 0:
            self.y_change = 35


    def reset(self, x, ground_level):
        self.rect.topleft = (x, ground_level - self.size)
        self.y_change = 0

