import pygame


class FadeTransition:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.fade_alpha = 0
        self.fade_speed = 5
        self.fade_state = "none"  # "none", "fade_out", "fade_in", "fade_black"
        self.fade_target_state = None
        self.fade_callback = None  # Optional callback function
        self.fade_surface = pygame.Surface((width, height))
        self.fade_surface.fill((0, 0, 0))
       
    def start_fade_out(self, target_state=None, callback=None):
        """Start fading out to black"""
        self.fade_state = "fade_out"
        self.fade_target_state = target_state
        self.fade_callback = callback
        self.fade_alpha = 0
       
    def start_fade_in(self, callback=None):
        """Start fading in from black"""
        self.fade_state = "fade_in"
        self.fade_callback = callback
        self.fade_alpha = 255
       
    def update(self):
        """Update fade animation - returns True if state changed"""
        state_changed = False
       
        if self.fade_state == "fade_out":
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fade_state = "fade_black"
                state_changed = True
                # Execute callback if provided
                if self.fade_callback:
                    self.fade_callback()
                   
        elif self.fade_state == "fade_in":
            self.fade_alpha -= self.fade_speed
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fade_state = "none"
                state_changed = True
                # Execute callback if provided
                if self.fade_callback:
                    self.fade_callback()
                   
        return state_changed
       
    def draw(self, screen):
        """Draw the fade overlay if active"""
        if self.fade_state != "none":
            self.fade_surface.set_alpha(self.fade_alpha)
            screen.blit(self.fade_surface, (0, 0))
           
    def is_active(self):
        """Check if a fade transition is currently active"""
        return self.fade_state != "none"
       
    def set_speed(self, speed):
        """Set the fade speed"""
        self.fade_speed = speed
       
    def reset(self):
        """Reset the fade system"""
        self.fade_alpha = 0
        self.fade_state = "none"
        self.fade_target_state = None
        self.fade_callback = None

