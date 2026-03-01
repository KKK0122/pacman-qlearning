"""游戏引擎：状态管理、碰撞检测、游戏逻辑"""
import config as cfg
from game_map import GameMap
from entities import Pacman, Ghost, create_ghosts


class GameEngine:
    """游戏引擎"""

    def __init__(self):
        self.game_map = GameMap()
        self.game_map.load()
        self.pacman = None
        self.ghosts = []
        self.pellets = set()
        self.power_pellets = set()
        self.score = 0
        self.lives = cfg.PACMAN_LIVES
        self.level = 1
        self.power_mode = False
        self.power_timer = 0.0
        self.game_over = False
        self.game_won = False
        self.paused = False
        self.phase_timer = 0.0  # 幽灵阶段计时
        self.ghost_phase = cfg.GHOST_SCATTER  # 全局幽灵阶段
        # self.ghosts_eaten_combo = 0  # 连续吃幽灵倍数
        self.step_events = []  # 本步事件列表
        self.move_timer = 0.0
        self.move_interval = 0.15  # 吃豆人移动间隔
        self.reset()

    def reset(self):
        """重置游戏状态"""
        # 重新加载地图以恢复豆子
        self.game_map.load()
        sx, sy = self.game_map.pacman_spawn
        self.pacman = Pacman(sx, sy)
        self.ghosts = create_ghosts(self.game_map)
        self.pellets = set(self.game_map.pellet_positions)
        # self.power_pellets = set(self.game_map.power_pellet_positions)
        self.score = 0
        self.lives = cfg.PACMAN_LIVES
        # self.power_mode = False
        # self.power_timer = 0.0
        self.game_over = False
        self.game_won = False
        self.phase_timer = 0.0
        self.ghost_phase = cfg.GHOST_SCATTER
        # self.ghosts_eaten_combo = 0
        self.step_events = []
        self.move_timer = 0.0

    def reset_positions(self):
        """只重置位置，不重置分数和豆子"""
        self.pacman.reset()
        for ghost in self.ghosts:
            ghost.reset()
        self.power_mode = False
        self.power_timer = 0.0
        # self.ghosts_eaten_combo = 0

    def step(self, action, dt=None):
        """执行一步游戏逻辑（用于Q-Learning）

        Args:
            action: 方向 (DIR_UP/DOWN/LEFT/RIGHT)
            dt: 时间步长（None则使用固定步长）

        Returns:
            (reward, done, info)
        """
        if dt is None:
            dt = self.move_interval

        self.step_events = []
        reward = cfg.REWARD_MOVE  # 基础移动惩罚

        if self.game_over or self.game_won:
            return (0, True, {'events': self.step_events})

        old_pos = self.pacman.pos
        old_pellet_count = len(self.pellets) + len(self.power_pellets)

        # 1. 设置吃豆人方向并移动
        self.pacman.direction = action
        nx, ny = self.game_map.get_neighbor(self.pacman.x, self.pacman.y, action)
        if self.game_map.is_walkable(nx, ny):
            self.pacman.x = nx
            self.pacman.y = ny
        else:
            reward += cfg.REWARD_HIT_WALL  # 撞墙惩罚

        # 2. 碰撞检测：豆子
        reward += self._check_pellet_collision()

        # 3. 更新幽灵阶段
        self._update_ghost_phase(dt)

        # 4. 更新能量模式
        # if self.power_mode:
        #     self.power_timer -= dt
        #     if self.power_timer <= 0:
        #         self.power_mode = False
        #         self.ghosts_eaten_combo = 0

        # 5. 移动幽灵
        for ghost in self.ghosts:
            ghost.update(self.game_map, self.pacman, self.ghosts, dt, self.phase_timer)

        # 6. 碰撞检测：幽灵
        ghost_reward = self._check_ghost_collision()
        reward += ghost_reward

        # 7. 引导性奖励
        reward += self._calculate_shaping_reward(old_pos)

        # 8. 检查胜负
        if len(self.pellets) == 0 and len(self.power_pellets) == 0:
            self.game_won = True
            reward += cfg.REWARD_WIN
            self.step_events.append('win')

        if self.lives <= 0:
            self.game_over = True

        done = self.game_over or self.game_won
        info = {
            'events': self.step_events,
            'score': self.score,
            'lives': self.lives,
            'pellets_left': len(self.pellets) + len(self.power_pellets),
        }
        return (reward, done, info)

    # def update_manual(self, dt):
    #     """手动模式更新（基于帧率的平滑移动）"""
    #     if self.paused or self.game_over or self.game_won:
    #         return
    #
    #     self.step_events = []
    #
    #     # 吃豆人移动计时
    #     self.move_timer += dt
    #     if self.move_timer >= self.move_interval:
    #         self.move_timer = 0.0
    #
    #         # 尝试切换方向
    #         if self.pacman.next_direction != cfg.DIR_NONE:
    #             nnx, nny = self.game_map.get_neighbor(
    #                 self.pacman.x, self.pacman.y, self.pacman.next_direction
    #             )
    #             if self.game_map.is_walkable(nnx, nny):
    #                 self.pacman.direction = self.pacman.next_direction
    #                 self.pacman.next_direction = cfg.DIR_NONE
    #
    #         # 移动吃豆人
    #         if self.pacman.direction != cfg.DIR_NONE:
    #             nx, ny = self.game_map.get_neighbor(
    #                 self.pacman.x, self.pacman.y, self.pacman.direction
    #             )
    #             if self.game_map.is_walkable(nx, ny):
    #                 self.pacman.x = nx
    #                 self.pacman.y = ny
    #
    #         # 碰撞检测：豆子
    #         self._check_pellet_collision()
    #
    #     # 更新幽灵阶段
    #     self._update_ghost_phase(dt)
    #
    #     # 更新能量模式
    #     if self.power_mode:
    #         self.power_timer -= dt
    #         if self.power_timer <= 0:
    #             self.power_mode = False
    #             self.ghosts_eaten_combo = 0
    #
    #     # 移动幽灵
    #     for ghost in self.ghosts:
    #         ghost.update(self.game_map, self.pacman, self.ghosts, dt, self.phase_timer)
    #
    #     # 碰撞检测：幽灵
    #     self._check_ghost_collision()
    #
    #     # 检查胜利
    #     if len(self.pellets) == 0 and len(self.power_pellets) == 0:
    #         self.game_won = True
    #
    #     if self.lives <= 0:
    #         self.game_over = True
    #
    #     # 更新吃豆人动画
    #     self.pacman.anim_timer += dt
    #     if self.pacman.anim_timer >= self.pacman.anim_speed:
    #         self.pacman.anim_timer = 0.0
    #         self.pacman.anim_frame = (self.pacman.anim_frame + 1) % 6

    def _check_pellet_collision(self):
        """检测豆子碰撞，返回奖励"""
        reward = 0
        pos = self.pacman.pos

        if pos in self.pellets:
            self.pellets.remove(pos)
            self.score += cfg.SCORE_PELLET
            reward += cfg.REWARD_PELLET
            self.step_events.append('pellet')

        # if pos in self.power_pellets:
        #     self.power_pellets.remove(pos)
        #     self.score += cfg.SCORE_POWER_PELLET
        #     reward += cfg.REWARD_POWER_PELLET
        #     self.power_mode = True
        #     self.power_timer = cfg.POWER_MODE_DURATION
        #     self.ghosts_eaten_combo = 0
        #     self.step_events.append('power_pellet')
        #     # 让所有幽灵进入惊吓状态
        #     for ghost in self.ghosts:
        #         ghost.set_frightened(cfg.POWER_MODE_DURATION)

        return reward

    def _check_ghost_collision(self):
        """检测幽灵碰撞，返回奖励"""
        reward = 0
        for ghost in self.ghosts:
            # if ghost.is_dead:
            #     continue
            if ghost.pos == self.pacman.pos:
                # if ghost.is_frightened:
                #     # 吃掉幽灵
                #     self.ghosts_eaten_combo += 1
                #     ghost_score = cfg.SCORE_GHOST * self.ghosts_eaten_combo
                #     self.score += ghost_score
                #     reward += cfg.REWARD_EAT_GHOST
                #     ghost_home = self.game_map.ghost_door if self.game_map.ghost_door else ghost.pos
                #     ghost.die(ghost_home)
                #     self.step_events.append('eat_ghost')
                # else:
                    # 被幽灵抓住
                    # self.lives -= 1
                    # reward += cfg.REWARD_DEATH
                    # self.step_events.append('death')
                    # if self.lives > 0:
                    #     self.reset_positions()
                    # break
                # 这是上面else之后的内容调整了缩进
                self.lives -= 1
                reward += cfg.REWARD_DEATH
                self.step_events.append('death')
                if self.lives > 0:
                    self.reset_positions()
                break
        return reward

    def _update_ghost_phase(self, dt):
        """更新幽灵全局阶段"""
        self.phase_timer += dt
        if self.ghost_phase == cfg.GHOST_SCATTER:
            if self.phase_timer >= cfg.GHOST_SCATTER_DURATION:
                self.ghost_phase = cfg.GHOST_CHASE
                self.phase_timer = 0.0
                for ghost in self.ghosts:
                    # if ghost.state not in (cfg.GHOST_FRIGHTENED, cfg.GHOST_DEAD):
                    #     ghost.state = cfg.GHOST_CHASE
                    # # if下面一行调整缩进
                    ghost.state = cfg.GHOST_CHASE
        elif self.ghost_phase == cfg.GHOST_CHASE:
            if self.phase_timer >= cfg.GHOST_CHASE_DURATION:
                self.ghost_phase = cfg.GHOST_SCATTER
                self.phase_timer = 0.0
                for ghost in self.ghosts:
                    # if ghost.state not in (cfg.GHOST_FRIGHTENED, cfg.GHOST_DEAD):
                    #     ghost.state = cfg.GHOST_SCATTER
                    # if下面一行调整缩进
                    ghost.state = cfg.GHOST_SCATTER

    def _calculate_shaping_reward(self, old_pos):
        """计算引导性奖励"""
        reward = 0
        new_pos = self.pacman.pos

        # 朝最近豆子移动的奖励
        all_pellets = list(self.pellets | self.power_pellets)
        if all_pellets:
            old_min_dist = min(
                self.game_map.manhattan_distance(old_pos, p) for p in all_pellets
            )
            new_min_dist = min(
                self.game_map.manhattan_distance(new_pos, p) for p in all_pellets
            )
            if new_min_dist < old_min_dist:
                reward += cfg.REWARD_TOWARD_PELLET

        # 远离最近幽灵的奖励（非能量模式）
        # if not self.power_mode:
        #     active_ghosts = [g for g in self.ghosts if not g.is_dead]
        #     if active_ghosts:
        #         old_min_ghost = min(
        #             self.game_map.manhattan_distance(old_pos, g.pos) for g in active_ghosts
        #         )
        #         new_min_ghost = min(
        #             self.game_map.manhattan_distance(new_pos, g.pos) for g in active_ghosts
        #         )
        #         if new_min_ghost > old_min_ghost and old_min_ghost < 5:
        #             reward += cfg.REWARD_AWAY_FROM_GHOST

        # if下一行开始，调整缩进，这部分代码的第一行代码[]里有删减
        active_ghosts = [g for g in self.ghosts]
        if active_ghosts:
            old_min_ghost = min(
                self.game_map.manhattan_distance(old_pos, g.pos) for g in active_ghosts
            )
            new_min_ghost = min(
                self.game_map.manhattan_distance(new_pos, g.pos) for g in active_ghosts
            )
            if new_min_ghost > old_min_ghost and old_min_ghost < 5:
                reward += cfg.REWARD_AWAY_FROM_GHOST

        return reward

    def get_state_for_ai(self):
        """返回AI所需的游戏状态信息"""
        return {
            'pacman_pos': self.pacman.pos,
            'pacman_dir': self.pacman.direction,
            'ghost_positions': [g.pos for g in self.ghosts],
            'ghost_states': [g.state for g in self.ghosts],
            'pellets': self.pellets,
            # 'power_pellets': self.power_pellets,
            # 'power_mode': self.power_mode,
            'score': self.score,
            'lives': self.lives,
            'game_map': self.game_map,
        }