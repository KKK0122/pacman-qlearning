"""Global configuration"""
import os

# ============ UI display settings ============
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 850
GAME_BOARD_WIDTH = 800
GAME_BOARD_HEIGHT = 800
INFO_PANEL_WIDTH = 400
CONTROL_BAR_HEIGHT = 50
FPS = 60

# ============ Grid settings ============
GRID_COLS = 15
GRID_ROWS = 15
CELL_SIZE = min(GAME_BOARD_WIDTH // GRID_COLS, GAME_BOARD_HEIGHT // GRID_ROWS)  # = 53
BOARD_OFFSET_X = (GAME_BOARD_WIDTH - GRID_COLS * CELL_SIZE) // 2
BOARD_OFFSET_Y = (GAME_BOARD_HEIGHT - GRID_ROWS * CELL_SIZE) // 2

# ============ Game settings ============
PACMAN_LIVES = 3
POWER_MODE_DURATION = 8.0  # s
GHOST_SCATTER_DURATION = 7.0  # s
GHOST_CHASE_DURATION = 20.0  # s
GHOST_RANDOM_FACTOR = 0.2

# ============ Directions ============
DIR_UP = 0
DIR_DOWN = 1
DIR_LEFT = 2
DIR_RIGHT = 3
DIR_NONE = -1

DIRECTION_VECTORS = {
    DIR_UP: (0, -1),
    DIR_DOWN: (0, 1),
    DIR_LEFT: (-1, 0),
    DIR_RIGHT: (1, 0),
}

OPPOSITE_DIRECTION = {
    DIR_UP: DIR_DOWN,
    DIR_DOWN: DIR_UP,
    DIR_LEFT: DIR_RIGHT,
    DIR_RIGHT: DIR_LEFT,
}

# ============ Map elements ============
TILE_WALL = '#'
TILE_PATH = '.'
TILE_EMPTY = ' '
TILE_GHOST_DOOR = 'G'
TILE_PACMAN_SPAWN = 'S'
TILE_GHOST_SPAWN = 'X'
TILE_OPEN = '-'  # Open Passage (Walkable)

# ============ color ============
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_BLUE = (33, 33, 222)
COLOR_DARK_BLUE = (0, 0, 40)
COLOR_RED = (255, 0, 0)
COLOR_PINK = (255, 184, 255)
COLOR_CYAN = (0, 255, 255)
COLOR_ORANGE = (255, 184, 82)
COLOR_PANEL_BG = (20, 20, 30)
COLOR_PANEL_TEXT = (200, 200, 200)
COLOR_PANEL_HIGHLIGHT = (255, 255, 100)
COLOR_PANEL_SECTION = (60, 60, 80)
COLOR_GREEN = (0, 200, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_WALL_FILL = (33, 33, 150)
COLOR_WALL_EDGE = (60, 60, 220)
COLOR_PELLET = (255, 183, 174)

GHOST_COLORS = {
    'blinky': COLOR_RED,
    'pinky': COLOR_PINK,
}

# ============ Q-Learning Parameters ============
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9
EPSILON_START = 1.0
EPSILON_MIN = 0.01
EPSILON_DECAY = 0.995

# ============ rewards ============
REWARD_MOVE = -1
REWARD_PELLET = 10
REWARD_DEATH = -500
REWARD_WIN = 1000
REWARD_TOWARD_PELLET = 2
REWARD_AWAY_FROM_GHOST = 5
REWARD_HIT_WALL = -5

# ============ training setting ============
TRAINING_EPISODES = 1000
CHECKPOINT_INTERVAL = 100
TRAINING_SPEED_OPTIONS = [1, 2, 5, 10, 50]

# ============ mode ============
MODE_AI_PLAY = 'AI_PLAY'
MODE_AI_TRAIN = 'AI_TRAIN'

# ============ ghost state ============
GHOST_CHASE = 'chase'
GHOST_SCATTER = 'scatter'

# ============ path ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_FILE = os.path.join(BASE_DIR, 'data', 'classic_map.txt')
Q_TABLE_DIR = os.path.join(BASE_DIR, 'data', 'q_tables')

# ============ score ============
SCORE_PELLET = 10
SCORE_POWER_PELLET = 50
SCORE_GHOST = 200