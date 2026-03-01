"""Controller: Input processing + Mode management"""
import pygame
import config as cfg

"""Game controller, manages input and modes"""
class Controller:

    def __init__(self):
        self.mode = cfg.MODE_AI_PLAY
        self.player_direction = cfg.DIR_NONE
        self.quit_requested = False
        self.training_speed_index = 0
        self.training_speed = cfg.TRAINING_SPEED_OPTIONS[0]
        self.save_requested = False
        self.load_requested = False
        self.reset_requested = False
        self.pause_requested = False

        self.buttons = {}

    def process_events(self, events):
        self.save_requested = False
        self.load_requested = False
        self.reset_requested = False
        self.pause_requested = False

        for event in events:
            if event.type == pygame.QUIT:
                self.quit_requested = True
                return

            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)


    """Handling the buttons"""
    def _handle_keydown(self, key):
        if key in (pygame.K_a, pygame.K_1, pygame.K_KP1):
            self.mode = cfg.MODE_AI_PLAY
        elif key in (pygame.K_t, pygame.K_2, pygame.K_KP2):
            self.mode = cfg.MODE_AI_TRAIN

        # Function key
        elif key == pygame.K_SPACE:
            self.pause_requested = True
        elif key in (pygame.K_s, pygame.K_3):
            self.save_requested = True
        elif key in (pygame.K_l, pygame.K_4):
            self.load_requested = True
        elif key in (pygame.K_r, pygame.K_5):
            self.reset_requested = True
        elif key == pygame.K_ESCAPE:
            self.quit_requested = True
        elif key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            self._increase_speed()
        elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self._decrease_speed()

    """Handling mouse clicks"""
    def _handle_click(self, pos):
        for name, rect in self.buttons.items():
            if rect.collidepoint(pos):
                if name == 'ai_play':
                    self.mode = cfg.MODE_AI_PLAY
                elif name == 'ai_train':
                    self.mode = cfg.MODE_AI_TRAIN
                elif name == 'reset':
                    self.reset_requested = True
                elif name == 'save':
                    self.save_requested = True
                elif name == 'load':
                    self.load_requested = True
                elif name == 'pause':
                    self.pause_requested = True
                elif name == 'speed_up':
                    self._increase_speed()
                elif name == 'speed_down':
                    self._decrease_speed()
                break

    def _increase_speed(self):
        if self.training_speed_index < len(cfg.TRAINING_SPEED_OPTIONS) - 1:
            self.training_speed_index += 1
            self.training_speed = cfg.TRAINING_SPEED_OPTIONS[self.training_speed_index]

    def _decrease_speed(self):
        if self.training_speed_index > 0:
            self.training_speed_index -= 1
            self.training_speed = cfg.TRAINING_SPEED_OPTIONS[self.training_speed_index]


    def consume_direction(self):
        d = self.player_direction
        return d