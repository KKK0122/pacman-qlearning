"""Game entities: Pac-Man, Ghosts, Beans"""
import random
from collections import deque
import config as cfg


"""pac-man"""
class Pacman:

    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.direction = cfg.DIR_NONE
        self.next_direction = cfg.DIR_NONE
        self.anim_frame = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.08

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.direction = cfg.DIR_NONE
        self.next_direction = cfg.DIR_NONE

    """Set the next expected direction"""
    def set_direction(self, direction):
        self.next_direction = direction

    """update location"""
    def update(self, game_map, dt):
        if self.next_direction != cfg.DIR_NONE:
            nx, ny = game_map.get_neighbor(self.x, self.y, self.next_direction)
            if game_map.is_walkable(nx, ny):
                self.direction = self.next_direction
                self.next_direction = cfg.DIR_NONE

        # Move in the current direction
        if self.direction != cfg.DIR_NONE:
            nx, ny = game_map.get_neighbor(self.x, self.y, self.direction)
            if game_map.is_walkable(nx, ny):
                self.x = nx
                self.y = ny

        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % 6

    @property
    def pos(self):
        return (self.x, self.y)


"""ghost"""
class Ghost:

    def __init__(self, x, y, name, color):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.name = name
        self.color = color
        self.state = cfg.GHOST_SCATTER
        self.direction = cfg.DIR_UP
        self.scatter_target = (0, 0)  # Move away from the target corner
        self.move_timer = 0.0
        self.move_interval = 0.22  # Movement interval (seconds), slower than Pac-Man

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.state = cfg.GHOST_SCATTER
        self.direction = cfg.DIR_UP

    """Update the position and status of the ghost"""
    def update(self, game_map, pacman, all_ghosts, dt, phase_timer):
        self.move_timer += dt
        if self.move_timer < self.move_interval:
            return
        self.move_timer = 0.0

        if self.state == cfg.GHOST_SCATTER:
            target = self.scatter_target
        else:
            target = self._get_chase_target(pacman, all_ghosts, game_map)

        if random.random() < cfg.GHOST_RANDOM_FACTOR:
            self._move_random(game_map)
        else:
            self._move_toward(target, game_map)

    """Obtain the pursuit target based on the type of ghost"""
    def _get_chase_target(self, pacman, all_ghosts, game_map):
        px, py = pacman.x, pacman.y

        if self.name == 'blinky':
            return (px, py)
        elif self.name == 'pinky':
            if pacman.direction in cfg.DIRECTION_VECTORS:
                dx, dy = cfg.DIRECTION_VECTORS[pacman.direction]
                tx = max(0, min(game_map.cols - 1, px + dx * 4))
                ty = max(0, min(game_map.rows - 1, py + dy * 4))
                return (tx, ty)
            return (px, py)
        elif self.name == 'inky':
            blinky = None
            for g in all_ghosts:
                if g.name == 'blinky':
                    blinky = g
                    break
            if blinky:
                if pacman.direction in cfg.DIRECTION_VECTORS:
                    dx, dy = cfg.DIRECTION_VECTORS[pacman.direction]
                    pivot_x = px + dx * 2
                    pivot_y = py + dy * 2
                    tx = 2 * pivot_x - blinky.x
                    ty = 2 * pivot_y - blinky.y
                    tx = max(0, min(game_map.cols - 1, tx))
                    ty = max(0, min(game_map.rows - 1, ty))
                    return (tx, ty)
            return (px, py)
        else:
            dist = abs(self.x - px) + abs(self.y - py)
            if dist > 8:
                return (px, py)
            else:
                return self.scatter_target

    """Move towards the target"""
    def _move_toward(self, target, game_map):
        if target is None:
            self._move_random(game_map)
            return

        valid_moves = game_map.get_valid_moves(self.x, self.y, is_ghost=True)
        if not valid_moves:
            return

        opposite = cfg.OPPOSITE_DIRECTION.get(self.direction)
        if len(valid_moves) > 1 and opposite in valid_moves:
            valid_moves.remove(opposite)

        best_dir = valid_moves[0]
        best_dist = float('inf')
        for d in valid_moves:
            nx, ny = game_map.get_neighbor(self.x, self.y, d)
            dist = abs(nx - target[0]) + abs(ny - target[1])
            if dist < best_dist:
                best_dist = dist
                best_dir = d

        nx, ny = game_map.get_neighbor(self.x, self.y, best_dir)
        self.x = nx
        self.y = ny
        self.direction = best_dir

    """Random Movement"""
    def _move_random(self, game_map):
        valid_moves = game_map.get_valid_moves(self.x, self.y, is_ghost=True)
        if not valid_moves:
            return

        opposite = cfg.OPPOSITE_DIRECTION.get(self.direction)
        if len(valid_moves) > 1 and opposite in valid_moves:
            valid_moves.remove(opposite)

        direction = random.choice(valid_moves)
        nx, ny = game_map.get_neighbor(self.x, self.y, direction)
        self.x = nx
        self.y = ny
        self.direction = direction

    @property
    def pos(self):
        return (self.x, self.y)


"""Create two ghosts"""
def create_ghosts(game_map):
    ghost_configs = [
        ('blinky', cfg.GHOST_COLORS['blinky']),
        ('pinky', cfg.GHOST_COLORS['pinky']),
    ]


    scatter_targets = [
        (game_map.cols - 2, 1),
        (1, 1),
    ]

    ghosts = []
    spawns = game_map.ghost_spawns[:2]
    while len(spawns) < 2:
        spawns.append(spawns[0] if spawns else (game_map.cols // 2, game_map.rows // 2))

    for i, (name, color) in enumerate(ghost_configs):
        sx, sy = spawns[i]
        ghost = Ghost(sx, sy, name, color)
        ghost.scatter_target = scatter_targets[i]
        ghosts.append(ghost)

    return ghosts