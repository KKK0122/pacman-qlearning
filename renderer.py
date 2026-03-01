"""UI renderer: Game board + Information panel + Clickable buttons"""
import math
import pygame
import config as cfg


# Button color
COLOR_BTN_BG = (50, 50, 70)
COLOR_BTN_HOVER = (70, 70, 100)
COLOR_BTN_ACTIVE = (90, 90, 140)
COLOR_BTN_BORDER = (100, 100, 140)
COLOR_BTN_TEXT = (220, 220, 220)

"""render"""
class Renderer:

    def __init__(self, screen):
        self.screen = screen
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.font_tiny = None
        self._init_fonts()
        self.power_pellet_timer = 0.0
        self.buttons = {}

    def _init_fonts(self):
        pygame.font.init()
        self.font_large = pygame.font.SysFont('consolas', 32, bold=True)
        self.font_medium = pygame.font.SysFont('consolas', 22)
        self.font_small = pygame.font.SysFont('consolas', 18)
        self.font_tiny = pygame.font.SysFont('consolas', 14)
        self.font_btn = pygame.font.SysFont('consolas', 16, bold=True)

    def render(self, engine, mode, ai_stats=None, training_speed=1, dt=0.016):
        self.buttons = {}
        self.screen.fill(cfg.COLOR_BLACK)

        # game board
        self._render_game_board(engine)

        # information board
        self._render_info_panel(engine, mode, ai_stats, training_speed)

        # Bottom control bar
        self._render_control_bar(mode)

        # Game over / Victory
        if engine.game_over:
            self._render_overlay("GAME OVER", cfg.COLOR_RED)
        elif engine.game_won:
            self._render_overlay("YOU WIN!", cfg.COLOR_GREEN)
        elif engine.paused:
            self._render_overlay("PAUSED", cfg.COLOR_YELLOW)

        pygame.display.flip()

    # ============ Button Drawing Tool ============

    """Draw a clickable button, the return button Rect"""
    def _draw_button(self, x, y, w, h, text, btn_name, is_active=False):
        rect = pygame.Rect(x, y, w, h)
        self.buttons[btn_name] = rect

        # Detect mouse hover
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)

        # Background color
        if is_active:
            bg = COLOR_BTN_ACTIVE
        elif hovered:
            bg = COLOR_BTN_HOVER
        else:
            bg = COLOR_BTN_BG

        pygame.draw.rect(self.screen, bg, rect, border_radius=4)
        pygame.draw.rect(self.screen, COLOR_BTN_BORDER, rect, 1, border_radius=4)

        text_surf = self.font_btn.render(text, True,
                                         cfg.COLOR_YELLOW if is_active else COLOR_BTN_TEXT)
        tx = x + (w - text_surf.get_width()) // 2
        ty = y + (h - text_surf.get_height()) // 2
        self.screen.blit(text_surf, (tx, ty))

        return rect

    # ============ Game board rendering ============

    """Render the game board"""
    def _render_game_board(self, engine):
        gm = engine.game_map
        ox = cfg.BOARD_OFFSET_X
        oy = cfg.BOARD_OFFSET_Y
        cs = cfg.CELL_SIZE

        # Game board background
        board_rect = pygame.Rect(0, 0, cfg.GAME_BOARD_WIDTH, cfg.GAME_BOARD_HEIGHT)
        pygame.draw.rect(self.screen, cfg.COLOR_DARK_BLUE, board_rect)

        # Render the walls
        for y in range(gm.rows):
            for x in range(gm.cols):
                tile = gm.grid[y][x]
                sx = ox + x * cs
                sy = oy + y * cs

                if tile == cfg.TILE_WALL:
                    self._render_wall(sx, sy, cs, gm, x, y)
                elif tile == cfg.TILE_GHOST_DOOR:
                    gate_rect = pygame.Rect(sx + 2, sy + cs // 2 - 2, cs - 4, 4)
                    pygame.draw.rect(self.screen, cfg.COLOR_PINK, gate_rect)

        # Render the beans
        for (px, py) in engine.pellets:
            sx = ox + px * cs + cs // 2
            sy = oy + py * cs + cs // 2
            pygame.draw.circle(self.screen, cfg.COLOR_PELLET, (sx, sy), 3)


        # Render the ghost
        for ghost in engine.ghosts:
            self._render_ghost(ghost, ox, oy, cs)

        # Render the Pac-Man character
        self._render_pacman(engine.pacman, ox, oy, cs)

    """Render the walls"""
    def _render_wall(self, sx, sy, cs, gm, gx, gy):
        rect = pygame.Rect(sx + 1, sy + 1, cs - 2, cs - 2)
        pygame.draw.rect(self.screen, cfg.COLOR_WALL_FILL, rect)
        pygame.draw.rect(self.screen, cfg.COLOR_WALL_EDGE, rect, 1)

    def _render_pacman(self, pacman, ox, oy, cs):
        cx = ox + pacman.x * cs + cs // 2
        cy = oy + pacman.y * cs + cs // 2
        radius = cs // 2 - 3

        dir_angles = {
            cfg.DIR_RIGHT: 0,
            cfg.DIR_UP: 90,
            cfg.DIR_LEFT: 180,
            cfg.DIR_DOWN: 270,
            cfg.DIR_NONE: 0,
        }
        base_angle = dir_angles.get(pacman.direction, 0)

        start_angle = math.radians(base_angle)
        end_angle = math.radians(base_angle + 360)

        points = [(cx, cy)]
        num_segments = 30
        for i in range(num_segments + 1):
            angle = start_angle + (end_angle - start_angle) * i / num_segments
            px = cx + radius * math.cos(angle)
            py = cy - radius * math.sin(angle)
            points.append((px, py))
        points.append((cx, cy))

        if len(points) >= 3:
            pygame.draw.polygon(self.screen, cfg.COLOR_YELLOW, points)


    """Render the ghost"""
    def _render_ghost(self, ghost, ox, oy, cs):
        cx = ox + ghost.x * cs + cs // 2
        cy = oy + ghost.y * cs + cs // 2
        radius = cs // 2 - 3
        color = ghost.color

        pygame.draw.circle(self.screen, color, (cx, cy - 2), radius)
        body_rect = pygame.Rect(cx - radius, cy - 2, radius * 2, radius)
        pygame.draw.rect(self.screen, color, body_rect)


    # ============ Information panel rendering ============

    """Render the right information panel"""
    def _render_info_panel(self, engine, mode, ai_stats, training_speed):
        panel_x = cfg.GAME_BOARD_WIDTH
        panel_rect = pygame.Rect(panel_x, 0, cfg.INFO_PANEL_WIDTH, cfg.SCREEN_HEIGHT - cfg.CONTROL_BAR_HEIGHT)
        pygame.draw.rect(self.screen, cfg.COLOR_PANEL_BG, panel_rect)
        pygame.draw.line(self.screen, cfg.COLOR_PANEL_SECTION,
                         (panel_x, 0), (panel_x, cfg.SCREEN_HEIGHT), 2)

        x = panel_x + 20
        y = 20

        # === title ===
        title = self.font_large.render("PAC-MAN", True, cfg.COLOR_YELLOW)
        self.screen.blit(title, (x, y))
        subtitle = self.font_tiny.render("Q-Learning AI", True, cfg.COLOR_PANEL_TEXT)
        self.screen.blit(subtitle, (x + 180, y + 10))
        y += 50

        # === game information ===
        y = self._render_section_header(x, y, "GAME INFO")

        # score
        score_text = self.font_medium.render(f"Score: {engine.score}", True, cfg.COLOR_WHITE)
        self.screen.blit(score_text, (x, y))
        y += 30

        # life
        lives_text = self.font_medium.render("Lives: ", True, cfg.COLOR_WHITE)
        self.screen.blit(lives_text, (x, y))
        for i in range(engine.lives):
            heart_x = x + 80 + i * 25
            pygame.draw.circle(self.screen, cfg.COLOR_YELLOW, (heart_x, y + 12), 8)
        y += 30

        # level
        level_text = self.font_medium.render(f"Level: {engine.level}", True, cfg.COLOR_WHITE)
        self.screen.blit(level_text, (x, y))
        y += 30

        # The remaining quantity of beans
        pellets_left = len(engine.pellets) + len(engine.power_pellets)
        pellet_text = self.font_small.render(f"Pellets Left: {pellets_left}", True, cfg.COLOR_PANEL_TEXT)
        self.screen.blit(pellet_text, (x, y))
        y += 22


        # === Mode Switch Button ===
        y = self._render_section_header(x, y, "MODE SELECT")
        btn_w = 108
        btn_h = 30
        gap = 8
        self._draw_button(x + btn_w + gap, y, btn_w, btn_h, "1: AI Play",
                          'ai_play', mode == cfg.MODE_AI_PLAY)
        self._draw_button(x + (btn_w + gap) * 2, y, btn_w, btn_h, "2: Train",
                          'ai_train', mode == cfg.MODE_AI_TRAIN)
        y += btn_h + 12

        # === Control button ===
        ctrl_btn_w = 78
        ctrl_btn_h = 28
        self._draw_button(x, y, ctrl_btn_w, ctrl_btn_h, "Reset(R)", 'reset')
        self._draw_button(x + ctrl_btn_w + gap, y, ctrl_btn_w, ctrl_btn_h,
                          "Pause", 'pause')
        self._draw_button(x + (ctrl_btn_w + gap) * 2, y, ctrl_btn_w, ctrl_btn_h,
                          "Save(S)", 'save')
        self._draw_button(x + (ctrl_btn_w + gap) * 3, y, ctrl_btn_w, ctrl_btn_h,
                          "Load(L)", 'load')
        y += ctrl_btn_h + 8

        if mode == cfg.MODE_AI_TRAIN:
            speed_label = self.font_small.render(f"Speed: x{training_speed}", True, cfg.COLOR_PANEL_TEXT)
            self.screen.blit(speed_label, (x, y + 2))
            spd_btn_w = 36
            spd_btn_h = 26
            self._draw_button(x + 140, y, spd_btn_w, spd_btn_h, "-", 'speed_down')
            self._draw_button(x + 140 + spd_btn_w + 6, y, spd_btn_w, spd_btn_h, "+", 'speed_up')
            y += spd_btn_h + 8
        y += 10

        # === AI Statistics ===
        if ai_stats and mode in (cfg.MODE_AI_PLAY, cfg.MODE_AI_TRAIN):
            y = self._render_section_header(x, y, "AI STATISTICS")

            stats_items = [
                ("Episode", f"{ai_stats.get('episode', 0)}"),
                ("Epsilon", f"{ai_stats.get('epsilon', 0):.4f}"),
                ("Avg Reward", f"{ai_stats.get('avg_reward', 0):.1f}"),
                ("Win Rate", f"{ai_stats.get('win_rate', 0):.1f}%"),
                ("Q-Table", f"{ai_stats.get('q_table_size', 0)} states"),
            ]

            y += 10
            if ai_stats and 'last_action' in ai_stats and ai_stats['last_action'] is not None:
                dir_names = {0: "UP", 1: "DOWN", 2: "LEFT", 3: "RIGHT"}
                last_act = ai_stats['last_action']
                last_act_name = dir_names.get(last_act, str(last_act))
                last_rew = ai_stats.get('last_reward')
                act_text = self.font_small.render(f"Last Action: {last_act_name}", True, cfg.COLOR_PANEL_TEXT)
                self.screen.blit(act_text, (x, y))
                y += 22
                if last_rew is not None:
                    rew_text = self.font_small.render(f"Last Reward: {last_rew:+.1f}", True, cfg.COLOR_PANEL_TEXT)
                else:
                    rew_text = self.font_small.render("Last Reward: N/A", True, cfg.COLOR_PANEL_TEXT)
                self.screen.blit(rew_text, (x, y))
                y += 22
            for label, value in stats_items:
                text = self.font_small.render(f"{label}: {value}", True, cfg.COLOR_PANEL_TEXT)
                self.screen.blit(text, (x, y))
                y += 22
            y += 10


        # === Current state characteristics ===
        if ai_stats and mode in (cfg.MODE_AI_PLAY, cfg.MODE_AI_TRAIN):
            y = self._render_section_header(x, y, "STATE FEATURES")
            if hasattr(ai_stats, 'get'):
                state_key = ai_stats.get('state_key', None)
                if state_key:
                    feature_names = [
                        "Ghost Dir", "Ghost Dist", "Ghost2 Dist",
                        "Power", "Pellet Dir", "Front Wall",
                        "Left Wall", "Right Wall"
                    ]
                    for i, (name, val) in enumerate(zip(feature_names, state_key)):
                        text = self.font_tiny.render(f"{name}: {val}", True, cfg.COLOR_GRAY)
                        self.screen.blit(text, (x, y))
                        y += 16


    """Render Partition Title"""
    def _render_section_header(self, x, y, title):
        line_y = y + 2
        pygame.draw.line(self.screen, cfg.COLOR_PANEL_SECTION,
                         (x, line_y), (x + cfg.INFO_PANEL_WIDTH - 40, line_y), 1)
        y += 8
        header = self.font_small.render(title, True, cfg.COLOR_PANEL_HIGHLIGHT)
        self.screen.blit(header, (x, y))
        y += 28
        return y

    # ============ Bottom control bar ============

    """Render bottom control prompt"""
    def _render_control_bar(self, mode):
        bar_y = cfg.SCREEN_HEIGHT - cfg.CONTROL_BAR_HEIGHT
        bar_rect = pygame.Rect(0, bar_y, cfg.SCREEN_WIDTH, cfg.CONTROL_BAR_HEIGHT)
        pygame.draw.rect(self.screen, cfg.COLOR_PANEL_BG, bar_rect)
        pygame.draw.line(self.screen, cfg.COLOR_PANEL_SECTION,
                         (0, bar_y), (cfg.SCREEN_WIDTH, bar_y), 1)

        controls = [
            "Arrows: Move",
            "SPACE: Pause",
            "1: AI Play",
            "2: Train",
            "+/-: Speed",
            "R: Reset",
            "ESC: Quit",
        ]
        text = "  |  ".join(controls)
        rendered = self.font_tiny.render(text, True, cfg.COLOR_GRAY)
        tx = (cfg.SCREEN_WIDTH - rendered.get_width()) // 2
        ty = bar_y + (cfg.CONTROL_BAR_HEIGHT - rendered.get_height()) // 2
        self.screen.blit(rendered, (tx, ty))

    # ============ Coating layer ============

    def _render_overlay(self, text, color):
        overlay = pygame.Surface((cfg.GAME_BOARD_WIDTH, cfg.GAME_BOARD_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        rendered = self.font_large.render(text, True, color)
        tx = (cfg.GAME_BOARD_WIDTH - rendered.get_width()) // 2
        ty = cfg.GAME_BOARD_HEIGHT // 2 - 30
        self.screen.blit(rendered, (tx, ty))

        hint = self.font_small.render("Press R to restart | SPACE to resume", True, cfg.COLOR_WHITE)
        hx = (cfg.GAME_BOARD_WIDTH - hint.get_width()) // 2
        self.screen.blit(hint, (hx, ty + 50))