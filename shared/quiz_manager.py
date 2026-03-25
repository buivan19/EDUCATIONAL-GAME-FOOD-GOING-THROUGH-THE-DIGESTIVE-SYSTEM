import pygame


class QuizManager:
    def __init__(self, all_questions, width, height, correct_sound=None, wrong_sound=None):  
        self.all_questions = all_questions
        self.current_level_questions = []
        self.current_question = 0
        self.selected_answer = -1
        self.score = 0
        self.active = False
        self.quiz_completed = False
        self.font = pygame.font.Font("asset/font/font1.ttf", 16)
        self.large_font = pygame.font.Font("asset/font/font1.ttf", 18)
        self.small_font = pygame.font.Font("asset/font/font1.ttf", 24)
        self.one_font = pygame.font.Font("asset/font/font1.ttf", 14)


        self.correct_sound = correct_sound
        self.wrong_sound = wrong_sound


        self.button_width = 600  # make buttons wider
        self.button_height = 70  # Make buttons taller by increasing this
       
        self.button_image = pygame.image.load("asset/UI/quiz_option.png")
        self.button_image = pygame.transform.scale(self.button_image, (self.button_width, self.button_height))


        self.screen_width = width
        self.screen_height = height


        self.quiz_backgrounds = {
            1: pygame.image.load("asset/background/quiz1.png"),
            2: pygame.image.load("asset/background/quiz2.png"),
            3: pygame.image.load("asset/background/quiz3.png")
        }
        for level, bg in self.quiz_backgrounds.items():
            self.quiz_backgrounds[level] = pygame.transform.scale(bg, (900,600))
       
        self.current_level = 1


    def set_level_questions(self, level_questions, level_num=1):
        self.current_level_questions = level_questions
        self.current_question = 0
        self.selected_answer = -1
        self.score = 0
        self.quiz_completed = False
        self.current_level = level_num


    def draw_quiz(self, screen, width, height):
        if self.current_level in self.quiz_backgrounds:
            screen.blit(self.quiz_backgrounds[self.current_level], (0, 0))
        else:
            screen.fill((0, 0, 0))


        if self.current_level == 1:
            text_color = (255, 150, 150)
        elif self.current_level == 2:
            text_color = (165, 42, 42)
        elif self.current_level == 3:
            text_color = (0, 0, 128)
       
        # Show progress
        progress_text = self.small_font.render(f"Question {self.current_question + 1} of {len(self.current_level_questions)}", True, text_color)
        screen.blit(progress_text, (width // 2 - progress_text.get_width() // 2, 40))
       
        q = self.current_level_questions[self.current_question]
        question_text = self.large_font.render(q["question"], True, text_color)
        screen.blit(question_text, (width // 2 - question_text.get_width() // 2, 100))


        start_y = 180
        spacing = 75
        for i, option in enumerate(q["options"]):
            option_text = self.font.render(f"{i + 1}. {option}", True, (255, 255, 255))
            y_pos = start_y + i * spacing
            button_surface = self.button_image.copy()


            if self.selected_answer != -1:
                if i == self.selected_answer:
                    button_surface.fill((0, 225, 0) if self.selected_answer == q["correct"] else (255, 0, 0), special_flags=pygame.BLEND_MULT)
                elif i == q["correct"]:
                    button_surface.fill((0, 225, 0), special_flags=pygame.BLEND_MULT)


            option_rect = pygame.Rect(width // 2 - self.button_width // 2, y_pos, self.button_width, self.button_height)
            screen.blit(button_surface, option_rect)
            text_y = y_pos + (self.button_height - option_text.get_height()) // 2
            screen.blit(option_text, (width // 2 - option_text.get_width() // 2, text_y))


        if self.selected_answer != -1:
            if self.selected_answer == q["correct"]:
                feedback_text = self.font.render("Correct! Press any key to continue", True, (0, 225, 0))
            else:
                correct_answer = q["options"][q["correct"]]
                feedback_text = self.one_font.render(f"Wrong! Correct answer: {correct_answer}. Press any key to continue", True, (255, 0, 0))
            screen.blit(feedback_text, (width // 2 - feedback_text.get_width() // 2, 550))
        else:
            instruction_text = self.small_font.render("PRESS 1,2,3,4 TO ANSWER", True, text_color)
            screen.blit(instruction_text, (width // 2 - instruction_text.get_width() // 2, 550))


    def handle_answer(self, key):
        if self.selected_answer == -1:
            if key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                self.selected_answer = key - pygame.K_1
                is_correct = self.selected_answer == self.current_level_questions[self.current_question]["correct"]
               
                if is_correct:
                    self.score += 1
                    if self.correct_sound:
                        self.correct_sound.play()
                else:
                    if self.wrong_sound:
                        self.wrong_sound.play()
               
                return False  
        else:
            self.current_question += 1
            self.selected_answer = -1
           
            if self.current_question >= len(self.current_level_questions):
                self.quiz_completed = True
                self.active = False
                return True  
        return False  


    def get_quiz_result(self):
        """Returns whether player passed the quiz (3/5 correct)"""
        total_questions = len(self.current_level_questions)
        return self.score >= (total_questions * 3) // 5  # At least 3/5 correct


    def reset(self):
        self.current_question = 0
        self.selected_answer = -1
        self.score = 0
        self.active = False
        self.quiz_completed = False

