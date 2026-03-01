"""Load and Manager the Map Data"""
from collections import deque
import config as cfg


"""Game Map Management Class"""
class GameMap:

    def __init__(self):
        self.grid = []
        self.rows = 0
        self.cols = 0
        self.pacman_spawn = (0, 0)
        self.ghost_spawns = []
        self.ghost_door = None
        self.pellet_positions = []
        self.power_pellet_positions = []

    """Load the map"""
    def load(self, filepath=None):
        if filepath is None:
            filepath = cfg.MAP_FILE
        with open(filepath, 'r') as f:
            lines = f.readlines()

        self.grid = []
        max_cols = 0
        for line in lines:
            row = list(line.rstrip('\n'))
            if len(row) > max_cols:
                max_cols = len(row)
            self.grid.append(row)

        for i in range(len(self.grid)):
            while len(self.grid[i]) < max_cols:
                self.grid[i].append(' ')

        self.rows = len(self.grid)
        self.cols = max_cols
        self._parse_map()

    """Analyze the positions of map elements"""
    def _parse_map(self):
        self.pellet_positions = []
        self.power_pellet_positions = []
        self.ghost_spawns = []
        self.ghost_door = None

        for y in range(self.rows):
            for x in range(self.cols):
                tile = self.grid[y][x]
                if tile == cfg.TILE_PACMAN_SPAWN:
                    self.pacman_spawn = (x, y)
                    self.grid[y][x] = cfg.TILE_OPEN
                elif tile == cfg.TILE_GHOST_SPAWN:
                    self.ghost_spawns.append((x, y))
                    self.grid[y][x] = cfg.TILE_EMPTY
                elif tile == cfg.TILE_GHOST_DOOR:
                    self.ghost_door = (x, y)
                    self.grid[y][x] = cfg.TILE_GHOST_DOOR
                elif tile == cfg.TILE_PATH:
                    self.pellet_positions.append((x, y))

        if len(self.ghost_spawns) < 2 and self.ghost_door:
            gx, gy = self.ghost_door
            for dx, dy in [(0, 1), (1, 1), (-1, 1), (0, 2)]:
                pos = (gx + dx, gy + dy)
                if pos not in self.ghost_spawns and self.is_inside(pos[0], pos[1]):
                    self.ghost_spawns.append(pos)
                    if len(self.ghost_spawns) >= 2:
                        break


    """Check if the coordinates are within the map's range"""
    def is_inside(self, x, y):
        return 0 <= x < self.cols and 0 <= y < self.rows

    def is_wall(self, x, y):
        if not self.is_inside(x, y):
            return True
        return self.grid[y][x] == cfg.TILE_WALL

    def is_walkable(self, x, y, is_ghost=False):
        if not self.is_inside(x, y):
            return False
        tile = self.grid[y][x]
        if tile == cfg.TILE_WALL:
            return False
        if tile == cfg.TILE_EMPTY:
            return is_ghost
        if tile == cfg.TILE_GHOST_DOOR:
            return is_ghost
        return True

    """Get the list of valid movement directions for a certain position"""
    def get_valid_moves(self, x, y, is_ghost=False):
        moves = []
        for direction, (dx, dy) in cfg.DIRECTION_VECTORS.items():
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny, is_ghost):
                moves.append(direction)
        return moves

    "Obtain the adjacent position in a certain direction"
    def get_neighbor(self, x, y, direction):
        if direction in cfg.DIRECTION_VECTORS:
            dx, dy = cfg.DIRECTION_VECTORS[direction]
            return (x + dx, y + dy)
        return (x, y)

    "Calculate the Manhattan distance"
    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])