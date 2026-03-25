import pygame
from levels.mouth import MouthLevel
from levels.stomach import StomachLevel
from levels.intestines import IntestinesLevel
from shared.quiz_manager import QuizManager
from shared.transition import FadeTransition


WIDTH, HEIGHT = 900, 600
GROUND_LEVEL = 400


LEVEL_CONFIG = {
    1: {"name": "MOUTH", "class": MouthLevel, "background": "asset/background/1.png",
        "obstacles_to_win": 10, "obstacle_paths": ["asset/obstacles/tooth.png", "asset/obstacles/food.png", "asset/obstacles/saliva.png"]},
    2: {"name": "STOMACH", "class": StomachLevel, "background": "asset/background/2.png",
        "obstacles_to_win": 12, "obstacle_paths": ["asset/obstacles/acid.png", "asset/obstacles/enzyme.png"]},
    3: {"name": "INTESTINES", "class": IntestinesLevel, "background": "asset/background/3.png",
        "obstacles_to_win": 15, "obstacle_size": (50, 50), "ground_color": (139, 69, 19),
        "obstacle_paths": ["asset/obstacles/bile.png", "asset/obstacles/microvilli.png", "asset/obstacles/enzyme2.png", "asset/obstacles/bacteria.png"]}
}


QUESTIONS = {
    1: [{"question": "What is the main function of the mouth?", "options": ["Breathing only", "Eating and speaking", "Pumping blood", "Seeing and hearing"], "correct": 1},
        {"question": "What organ in the mouth helps you taste food?", "options": ["Teeth", "Tongue", "Lips", "Gums"], "correct": 1},
        {"question": "What liquid is made in the mouth to help digest food?", "options": ["Water", "Saliva", "Blood", "Oil"], "correct": 1},
        {"question": "What should you use to clean your teeth every day?", "options": ["Comb", "Soap", "Toothbrush", "Towel"], "correct": 2},
        {"question": "How many sets of teeth do humans have in their lifetime?", "options": ["One", "Two", "Three", "Four"], "correct": 1}],
    2: [{"question": "What is the main function of the stomach?", "options": ["Digesting food", "Transporting food to stomach", "Absorbing nutrients", "Producing enzymes"], "correct": 1},
        {"question": "How does food move through the stomach?", "options": ["Gravity only", "Peristalsis", "Pumping action", "Muscle spasms"], "correct": 1},
        {"question": "How long is the average adult stomach?", "options": ["10-12 inches", "5-7 inches", "15-18 inches", "20-25 inches"], "correct": 0},
        {"question": "What prevents food from going into the windpipe?", "options": ["Tongue", "Epiglottis", "Uvula", "Vocal cords"], "correct": 1},
        {"question": "What is the medical term for difficulty swallowing?", "options": ["Dysphagia", "Dyspepsia", "Aphagia", "Odynophagia"], "correct": 0}],
    3: [{"question": "What is the main function of the intestine?", "options": ["Pump blood", "Absorb nutrients and water", "Produce hormones", "Filter air"], "correct": 1},
        {"question": "What are the two main parts of the intestine?", "options": ["Small intestine and large intestine", "Liver and stomach", "Pancreas and gallbladder", "Heart and lungs"], "correct": 0},
        {"question": "Which part of the intestine absorbs most nutrients?", "options": ["Large intestine", "Small intestine", "Rectum", "Appendix"], "correct": 1},
        {"question": "What helps move food through the intestines?", "options": ["Digestion", "Peristalsis", "Breathing", "Filtration"], "correct": 1},
        {"question": "Where does the intestine connect to the stomach?", "options": ["Esophagus", "Duodenum", "Colon", "Rectum"], "correct": 1}]
}


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Food adventure")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("asset/font/font1.ttf", 30)
        self.small_font = pygame.font.Font("asset/font/font1.ttf", 20)
        self.one_font = pygame.font.Font("asset/font/font1.ttf", 18)
        self.two_font = pygame.font.Font("asset/font/font1.ttf", 45)


        self.is_muted = False
        self.is_music_muted = False
        self._init_audio()
        self._init_ui()
       
        self.fade_transition = FadeTransition(WIDTH, HEIGHT)
        self.fade_transition.set_speed(3)
        self._load_intro_images()


        self.current_level = 1
        self.levels = self._build_level_configs()
        self.current_level_instance = self._load_level(self.current_level)
        self.quiz_manager = QuizManager(QUESTIONS, WIDTH, HEIGHT, self.correct_answer_sound, self.wrong_answer_sound)
        self.quiz_manager.set_level_questions(QUESTIONS[self.current_level])
       
        self.walk_timer = 0
        self.walk_duration = 80
        self.start_x = 100
        self.end_x = WIDTH - 40
        self.state = "start"
        self.previous_state = "start"
        self.quiz_passed = False
        self.quiz_triggered_by = "completion"
        self.current_intro_image = 0


    def _init_audio(self):
        sound_map = {
            'jump': ('asset/audio/jump.wav', 0.2), 'death': ('asset/audio/death.mp3', 0.6),
            'walk': ('asset/audio/victory_walk.mp3', 0.4), 'quiz_won': ('asset/audio/quiz_win.mp3', 0.5),
            'quiz_lose': ('asset/audio/quiz_lose.mp3', 0.5), 'correct_answer': ('asset/audio/correct.wav', 0.2),
            'wrong_answer': ('asset/audio/wrong.mp3', 0.2), 'intro_music': ('asset/audio/intro_music1.mp3', 0.6),
            'intro_music2': ('asset/audio/intro_music2.mp3', 0.6), 'level1_music': ('asset/audio/level1_music.mp3', 0.4),
            'level2_music': ('asset/audio/level2_music.mp3', 0.4), 'level3_music': ('asset/audio/level3_music.mp3', 0.4),
            'final_victory': ('asset/audio/victory.mp3', 0.8), 'button': ('asset/audio/button.mp3', 0.5)
        }
        for name, (path, vol) in sound_map.items():
            try:
                sound = pygame.mixer.Sound(path)
                sound.set_volume(vol)
                setattr(self, f'{name}_sound', sound)
                setattr(self, f'{name}_base_volume', vol)
            except:
                setattr(self, f'{name}_sound', None)


    def _init_ui(self):
        btn_size = 40
        self.sfx_button_rect = pygame.Rect(WIDTH - btn_size - 10, 10, btn_size, btn_size)
        self.music_button_rect = pygame.Rect(self.sfx_button_rect.left - btn_size - 10, 10, btn_size, btn_size)
        self.sfx_image = self._load_ui_image("asset/UI/sound.png", (btn_size, btn_size), (100, 100, 255, 150))
        self.music_image = self._load_ui_image("asset/UI/music.png", (btn_size, btn_size), (100, 100, 255, 150))
        self.start_background = self._load_ui_image("asset/background/start_screen.png", (WIDTH, HEIGHT), (0, 0, 0), False)
        self.final_background = self._load_ui_image("asset/background/final.png", (WIDTH, HEIGHT), (0, 0, 0), False)
        self.start_button_image = self._load_ui_image("asset/UI/start.png", (200, 80), (0, 150, 0))
        self.start_button_rect = self.start_button_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))
        pause_w, pause_h = 250, 80
        self.resume_button_rect = pygame.Rect(0, 0, pause_w, pause_h)
        self.resume_button_rect.center = (WIDTH // 2 - 140, HEIGHT // 2 + 50)
        self.exit_button_rect = pygame.Rect(0, 0, pause_w, pause_h)
        self.exit_button_rect.center = (WIDTH // 2 + 140, HEIGHT // 2 + 50)
        self.resume_image = self._load_ui_image("asset/UI/resume.png", (pause_w, pause_h), (0, 255, 0))
        self.exit_image = self._load_ui_image("asset/UI/exit.png", (pause_w, pause_h), (255, 0, 0))


    def _build_level_configs(self):
        defaults = {"ground_color": (128, 0, 32), "ground_level": GROUND_LEVEL, "width": WIDTH, "height": HEIGHT, "obstacle_size": (60, 60)}
        return {k: {**defaults, **v} for k, v in LEVEL_CONFIG.items()}


    def _load_ui_image(self, path, size, fallback_color, convert=True):
        try:
            img = pygame.image.load(path).convert_alpha() if convert else pygame.image.load(path)
            return pygame.transform.scale(img, size)
        except:
            surf = pygame.Surface(size, pygame.SRCALPHA if len(fallback_color) == 4 else 0)
            surf.fill(fallback_color)
            return surf


    def _load_intro_images(self):
        self.intro_images = {}
        try:
            self.intro_images[1] = [pygame.transform.scale(pygame.image.load(f"asset/intro/1{i}.png"), (WIDTH, HEIGHT)) for i in range(1, 7)]
            self.intro_images[2] = [pygame.transform.scale(pygame.image.load(f"asset/intro/2{i}.png"), (WIDTH, HEIGHT)) for i in range(1, 9)]
        except Exception as e:
            print(f"Could not load intro images: {e}")
        self.intro_images.setdefault(1, [])
        self.intro_images.setdefault(2, [])
        self.intro_images.setdefault(3, [])


    def _get_intro_music_sound(self):
        if self.current_level == 1:
            return getattr(self, "intro_music_sound", None)
        elif self.current_level == 2:
            return getattr(self, "intro_music2_sound", None)
        return getattr(self, "intro_music_sound", None)


    def _stop_all_intro_music(self):
        for attr in ["intro_music_sound", "intro_music2_sound"]:
            sound = getattr(self, attr, None)
            if sound:
                sound.stop()


    def _set_master_volume(self):
        sfx_scale = 0.0 if self.is_muted else 1.0
        music_scale = 0.0 if self.is_music_muted else 1.0
        sfx_sounds = ['jump', 'death', 'walk', 'quiz_won', 'quiz_lose', 'correct_answer', 'wrong_answer', 'final_victory', 'button']
        music_sounds = ['intro_music', 'intro_music2', 'level1_music', 'level2_music', 'level3_music']
        for name in sfx_sounds:
            sound = getattr(self, f'{name}_sound', None)
            if sound:
                sound.set_volume(sfx_scale * getattr(self, f'{name}_base_volume', 0.5))
        for name in music_sounds:
            sound = getattr(self, f'{name}_sound', None)
            if sound:
                sound.set_volume(music_scale * getattr(self, f'{name}_base_volume', 0.4))


    def _draw_volume_button(self, screen, rect, image, is_muted):
        mouse_pos = pygame.mouse.get_pos()
        scale = 1.1 if rect.collidepoint(mouse_pos) else 1.0
        scaled_img = pygame.transform.scale(image, (int(rect.width * scale), int(rect.height * scale)))
        scaled_rect = scaled_img.get_rect(center=rect.center)
        if is_muted:
            temp = scaled_img.copy()
            pygame.draw.line(temp, (255, 0, 0), (0, 0), (temp.get_width(), temp.get_height()), 4)
            pygame.draw.line(temp, (255, 0, 0), (temp.get_width(), 0), (0, temp.get_height()), 4)
            screen.blit(temp, scaled_rect)
        else:
            screen.blit(scaled_img, scaled_rect)
        pygame.draw.rect(screen, (255, 255, 255), scaled_rect, 1)


    def _load_level(self, level_num):
        config = self.levels[level_num]
        sprites = [pygame.transform.scale(pygame.image.load(p).convert_alpha(), config["obstacle_size"]) for p in config["obstacle_paths"]]
        return config["class"](config, sprites, self.jump_sound)


    def _advance_to_next_level(self):
        self.current_level += 1
        if self.current_level in self.levels:
            if self.intro_images.get(self.current_level):
                self.current_intro_image = 0
                self.fade_transition.start_fade_out("level_intro")
            else:
                self.current_level_instance = self._load_level(self.current_level)
                self.quiz_manager.set_level_questions(QUESTIONS[self.current_level], self.current_level)
                self.state = "level_start"
        else:
            self.state = "end"


    def _start_run(self):
        self.current_level_instance = self._load_level(self.current_level)
        self.quiz_manager.set_level_questions(QUESTIONS[self.current_level], self.current_level)
        self.quiz_manager.reset()
        self.walk_timer = 0
        self.state = "level_start"


    def _clear_obstacles(self):
        mgr = self.current_level_instance.obstacle_manager
        if hasattr(mgr, 'clear_obstacles'):
            mgr.clear_obstacles()
        elif hasattr(mgr, 'obstacles'):
            mgr.obstacles.empty()
            if hasattr(mgr, 'dodged_count'):
                mgr.dodged_count = 0


    def _handle_quiz_completion(self):
        self.quiz_passed = self.quiz_manager.get_quiz_result()
        self.state = "quiz_result"
        sound = self.quiz_won_sound if self.quiz_passed else self.quiz_lose_sound
        if sound:
            sound.play()


    def _stop_level_music(self):
        music = getattr(self, f'level{self.current_level}_music_sound', None)
        if music:
            music.stop()


    def _play_level_music(self):
        music = getattr(self, f'level{self.current_level}_music_sound', None)
        if music:
            music.play(-1)


    def _draw_pause_menu(self):
        if self.previous_state == "level_intro":
            if self.current_level in self.intro_images and self.current_intro_image < len(self.intro_images[self.current_level]):
                self.screen.blit(self.intro_images[self.current_level][self.current_intro_image], (0, 0))
            else:
                self.screen.fill((0, 0, 0))
        elif self.previous_state == "quiz":
            self.quiz_manager.draw_quiz(self.screen, WIDTH, HEIGHT)
        else:
            self.current_level_instance.draw(self.screen)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        pause_text = self.two_font.render("PAUSED", True, (255, 255, 255))
        self.screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 150))
        mouse_pos = pygame.mouse.get_pos()
        for img, rect in [(self.resume_image, self.resume_button_rect), (self.exit_image, self.exit_button_rect)]:
            scale = 1.1 if rect.collidepoint(mouse_pos) else 1.0
            scaled = pygame.transform.scale(img, (int(rect.width * scale), int(rect.height * scale)))
            self.screen.blit(scaled, scaled.get_rect(center=rect.center))
        self._draw_volume_button(self.screen, self.sfx_button_rect, self.sfx_image, self.is_muted)
        self._draw_volume_button(self.screen, self.music_button_rect, self.music_image, self.is_music_muted)


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.state == "paused":
                    return True
                if event.key == pygame.K_p and self.state in ["playing", "walking", "level_start", "level_intro", "quiz"]:
                    self.previous_state = self.state
                    self.state = "paused"
                    if self.previous_state == "playing":
                        self._stop_level_music()
                    return True
                if self.state == "end" and event.key == pygame.K_SPACE:
                    self.fade_transition.start_fade_out("final_victory_sequence")
                elif self.state == "final_victory" and event.key == pygame.K_SPACE:
                    self.state = "start"
                    self.current_level = 1
                    self.current_level_instance = self._load_level(1)
                    self.quiz_manager.set_level_questions(QUESTIONS[1], 1)
                elif self.state == "quiz" and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    if self.quiz_manager.handle_answer(event.key):
                        self._handle_quiz_completion()
                elif self.state == "level_intro" and event.key == pygame.K_SPACE and not self.fade_transition.is_active():
                    self.fade_transition.start_fade_out()
                elif self.state == "quiz_result" and event.key == pygame.K_SPACE:
                    self._advance_to_next_level() if self.quiz_passed else self._start_run()
                elif event.key == pygame.K_SPACE:
                    if self.state == "playing":
                        self.current_level_instance.handle_jump()
                    elif self.state == "level_start":
                        self.state = "playing"
                        self._play_level_music()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.sfx_button_rect.collidepoint(pos) and self.state in ["start", "paused"]:
                    if self.button_sound: self.button_sound.play()
                    self.is_muted = not self.is_muted
                    self._set_master_volume()
                elif self.music_button_rect.collidepoint(pos) and self.state in ["start", "paused"]:
                    if self.button_sound: self.button_sound.play()
                    self.is_music_muted = not self.is_music_muted
                    self._set_master_volume()
                elif self.state == "start" and self.start_button_rect.collidepoint(pos):
                    if self.button_sound: self.button_sound.play()
                    self.current_intro_image = 0
                    self.fade_transition.start_fade_out("level_intro")
                elif self.state == "paused":
                    if self.resume_button_rect.collidepoint(pos):
                        if self.button_sound: self.button_sound.play()
                        if self.previous_state == "playing": self._play_level_music()
                        self.state = self.previous_state
                    elif self.exit_button_rect.collidepoint(pos):
                        if self.button_sound: self.button_sound.play()
                        self.state = "start"
                        self.current_level = 1
                        self.current_level_instance = self._load_level(1)
                        self.quiz_manager.set_level_questions(QUESTIONS[1], 1)
                        self.quiz_manager.reset()
                        self._stop_all_intro_music()
                        self._stop_level_music()
        return True


    def update(self):
        if self.fade_transition.is_active():
            if self.fade_transition.update():
                if self.fade_transition.fade_state == "fade_black":
                    if self.fade_transition.fade_target_state == "level_intro":
                        self.state = "level_intro"
                        self.current_level_instance = self._load_level(self.current_level)
                        self.quiz_manager.set_level_questions(QUESTIONS[self.current_level], self.current_level)
                        self.fade_transition.start_fade_in()
                        intro_sound = self._get_intro_music_sound()
                        if intro_sound:
                            intro_sound.play(-1)
                    elif self.fade_transition.fade_target_state == "final_victory_sequence":
                        self.state = "final_victory"
                        if self.final_victory_sound: self.final_victory_sound.play()
                        self.fade_transition.start_fade_in()
                    elif self.state == "level_intro":
                        self.current_intro_image += 1
                        if self.current_intro_image >= len(self.intro_images.get(self.current_level, [])):
                            self._start_run()
                            self.fade_transition.start_fade_in()
                            self._stop_all_intro_music()
                        else:
                            self.fade_transition.start_fade_in()
        if self.state == "playing":
            if self.current_level_instance.update():
                self.quiz_triggered_by = "collision"
                self.quiz_manager.reset()
                self.quiz_manager.active = True
                self.state = "quiz"
                self._stop_level_music()
                if self.death_sound: self.death_sound.play()
            elif self.current_level_instance.get_dodged_count() >= self.levels[self.current_level]["obstacles_to_win"]:
                self.quiz_triggered_by = "completion"
                self.walk_timer = self.walk_duration
                self._clear_obstacles()
                self.state = "walking"
                self._stop_level_music()
                if self.walk_sound: self.walk_sound.play()
        elif self.state == "walking":
            self.walk_timer -= 1
            progress = 1 - (self.walk_timer / self.walk_duration)
            self.current_level_instance.player.rect.x = self.start_x + (self.end_x - self.start_x) * progress
            self.current_level_instance.player.rect.y = self.levels[self.current_level]["ground_level"] - 60
            self.current_level_instance.player.y_change = 0
            if self.walk_timer == 0:
                if self.walk_sound: self.walk_sound.stop()
                self.quiz_manager.reset()
                self.quiz_manager.active = True
                self.state = "quiz"
        self.fade_transition.update()


    def draw(self):
        if self.state == "start":
            self.screen.blit(self.start_background, (0, 0))
            mouse_pos = pygame.mouse.get_pos()
            if self.start_button_rect.collidepoint(mouse_pos):
                scaled = pygame.transform.scale(self.start_button_image, (220, 88))
                self.screen.blit(scaled, scaled.get_rect(center=self.start_button_rect.center))
            else:
                self.screen.blit(self.start_button_image, self.start_button_rect)
            self._draw_volume_button(self.screen, self.sfx_button_rect, self.sfx_image, self.is_muted)
            self._draw_volume_button(self.screen, self.music_button_rect, self.music_image, self.is_music_muted)
        elif self.state == "level_intro":
            if self.current_level in self.intro_images and self.current_intro_image < len(self.intro_images[self.current_level]):
                self.screen.blit(self.intro_images[self.current_level][self.current_intro_image], (0, 0))
                if not self.fade_transition.is_active():
                    text = self.one_font.render("Press SPACE to continue", True, (255, 255, 255))
                    self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 40))
        elif self.state == "end":
            self.screen.fill((0, 0, 0))
            text = self.font.render("YAY! YOU COMPLETED ALL THE LEVELS!", True, (255, 255, 255))
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
            if not self.fade_transition.is_active():
                inst = self.small_font.render("Press SPACE to continue", True, (255, 255, 255))
                self.screen.blit(inst, (WIDTH//2 - inst.get_width()//2, HEIGHT//2 + 60))
        elif self.state == "final_victory":
            self.screen.blit(self.final_background, (0, 0))
            text = self.small_font.render("Press SPACE to return to Start Screen", True, (255, 255, 255))
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 40))
        elif self.state == "quiz":
            self.quiz_manager.draw_quiz(self.screen, WIDTH, HEIGHT)
        elif self.state == "quiz_result":
            self.screen.fill((0, 0, 0))
            color = (0, 225, 0) if self.quiz_passed else (255, 0, 0)
            msg = "Congratulations! You passed!" if self.quiz_passed else "Try again! You need 3/5 correct."
            msg_text = self.font.render(msg, True, color)
            score_text = self.font.render(f"Your score: {self.quiz_manager.score}/5", True, (255, 255, 255))
            action = "move on to next level" if self.quiz_passed else "restart the level"
            inst = self.small_font.render(f"Press SPACE to {action}", True, (255, 255, 255))
            self.screen.blit(msg_text, (WIDTH//2 - msg_text.get_width()//2, HEIGHT//2 - 60))
            self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
            self.screen.blit(inst, (WIDTH//2 - inst.get_width()//2, HEIGHT//2 + 60))
        elif self.state == "paused":
            self._draw_pause_menu()
        else:
            self.current_level_instance.draw(self.screen)
            if self.state == "level_start":
                level_text = self.two_font.render(f"LEVEL {self.current_level}: {self.levels[self.current_level]['name']}", True, (255, 255, 255))
                self.screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 - 50))
                start_text = self.font.render("PRESS SPACE TO START", True, (255, 255, 255))
                self.screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2 + 20))
            elif self.state == "playing":
                level_text = self.two_font.render(f"LEVEL {self.current_level}: {self.levels[self.current_level]['name']}", True, (255, 255, 255))
                self.screen.blit(level_text, (20, 500))
                progress_text = self.one_font.render(f"Progress: {self.current_level_instance.get_dodged_count()}/{self.levels[self.current_level]['obstacles_to_win']}", True, (255, 255, 255))
                self.screen.blit(progress_text, (10, 20))
            elif self.state == "walking":
                text = self.font.render("LEVEL COMPLETE!", True, (0, 225, 0))
                self.screen.blit(text, (WIDTH//2 - text.get_width()//2, 60))
        self.fade_transition.draw(self.screen)


    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    Game().run()

