"""Q-Learning Agent: State Extraction, Q-value Update, Training Management"""
import os
import pickle
import random
from collections import defaultdict, deque
import config as cfg
import matplotlib.pyplot as plt

"""Q-Learning agent"""
class QLearningAgent:

    # Q-table：{state_key: {action: q_value}}
    def __init__(self):
        self.q_table = defaultdict(lambda: {a: 0.0 for a in range(4)})
        self.lr = cfg.LEARNING_RATE
        self.gamma = cfg.DISCOUNT_FACTOR
        self.epsilon = cfg.EPSILON_START
        self.epsilon_min = cfg.EPSILON_MIN
        self.epsilon_decay = cfg.EPSILON_DECAY
        self.last_reward = None

        self.episode_count = 0
        self.episode_rewards = []
        self.episode_scores = []
        self.episode_steps = []
        self.win_count = 0
        self.recent_rewards = deque(maxlen=100)
        self.recent_wins = deque(maxlen=100)

        self.current_episode_reward = 0
        self.current_episode_steps = 0

        self.current_state_key = None
        self.current_q_values = {a: 0.0 for a in range(4)}
        self.last_action = cfg.DIR_NONE

    def extract_state(self, game_state):
        """Extract features from the game state and return the state key"
        7-dimensional features:
        1. Direction of the most recent ghost
        2. Distance level of the most recent ghost
        3. Distance level of the second closest ghost
        4. Direction of the nearest bean
        5. Presence of a wall in front
        6. Presence of a wall on the left
        7. Presence of a wall on the right """
        pacman_pos = game_state['pacman_pos']
        pacman_dir = game_state['pacman_dir']
        ghost_positions = game_state['ghost_positions']
        ghost_states = game_state['ghost_states']
        pellets = game_state['pellets']
        game_map = game_state['game_map']
        px, py = pacman_pos

        # --- Feature 1&2 ---
        active_ghost_dists = []
        for i, gpos in enumerate(ghost_positions):
            dist = game_map.manhattan_distance(pacman_pos, gpos)
            active_ghost_dists.append((dist, gpos))
        active_ghost_dists.sort(key=lambda x: x[0])

        if active_ghost_dists:
            nearest_dist, nearest_pos = active_ghost_dists[0]
            nearest_ghost_dir = self._get_relative_direction(pacman_pos, nearest_pos)
            nearest_ghost_dist_level = self._discretize_distance(nearest_dist)
        else:
            nearest_ghost_dir = 4
            nearest_ghost_dist_level = 3

        # --- Feature 3 ---
        if len(active_ghost_dists) > 1:
            second_dist = active_ghost_dists[1][0]
            second_ghost_dist_level = self._discretize_distance(second_dist)
        else:
            second_ghost_dist_level = 3

        # --- Feature 5  ---
        all_pellets = list(pellets)
        other_pellets = [p for p in all_pellets if p != pacman_pos]
        if other_pellets:
            nearest_pellet = min(
                other_pellets,
                key=lambda p: game_map.manhattan_distance(pacman_pos, p)
            )
            pellet_dir = self._get_relative_direction(pacman_pos, nearest_pellet)
        else:
            pellet_dir = 0

        # --- Feature 6-8 ---
        if pacman_dir == cfg.DIR_NONE:
            pacman_dir = cfg.DIR_RIGHT

        front_wall = self._check_wall(px, py, pacman_dir, game_map)
        left_dir = self._rotate_left(pacman_dir)
        left_wall = self._check_wall(px, py, left_dir, game_map)
        right_dir = self._rotate_right(pacman_dir)
        right_wall = self._check_wall(px, py, right_dir, game_map)

        state_key = (
            nearest_ghost_dir,
            nearest_ghost_dist_level,
            second_ghost_dist_level,
            pellet_dir,
            front_wall,
            left_wall,
            right_wall,
        )

        self.current_state_key = state_key
        return state_key

    """ε-greedy Strategy selection action"""
    def choose_action(self, state_key, game_map=None, pacman_pos=None):
        if random.random() < self.epsilon:
            if game_map and pacman_pos:
                valid = game_map.get_valid_moves(pacman_pos[0], pacman_pos[1])
                if valid:
                    action = random.choice(valid)
                else:
                    action = random.randint(0, 3)
            else:
                action = random.randint(0, 3)
        else:
            q_vals = self.q_table[state_key]
            if game_map and pacman_pos:
                valid = game_map.get_valid_moves(pacman_pos[0], pacman_pos[1])
                if valid:
                    action = max(valid, key=lambda a: q_vals[a])
                else:
                    action = max(q_vals, key=q_vals.get)
            else:
                action = max(q_vals, key=q_vals.get)

        self.last_action = action
        self.current_q_values = dict(self.q_table[state_key])
        return action

    """Obtain the optimal action (without random exploration)"""
    def get_best_action(self, state_key):
        q_vals = self.q_table[state_key]
        return max(q_vals, key=q_vals.get)

    """update Q-value"""
    def update(self, state, action, reward, next_state, done):
        current_q = self.q_table[state][action]
        if done:
            target = reward
        else:
            max_next_q = max(self.q_table[next_state].values())
            target = reward + self.gamma * max_next_q

        self.q_table[state][action] = current_q + self.lr * (target - current_q)

        self.current_episode_reward += reward
        self.current_episode_steps += 1

    """Attenuation exploration rate"""
    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def on_episode_end(self, score, won):
        self.episode_count += 1
        self.episode_rewards.append(self.current_episode_reward)
        self.episode_scores.append(score)
        self.episode_steps.append(self.current_episode_steps)
        self.recent_rewards.append(self.current_episode_reward)
        if won:
            self.win_count += 1
            self.recent_wins.append(1)
        else:
            self.recent_wins.append(0)

        self.decay_epsilon()

        self.current_episode_reward = 0
        self.current_episode_steps = 0

    """Obtain training statistics"""
    def get_stats(self):
        avg_reward = sum(self.recent_rewards) / max(1, len(self.recent_rewards))
        win_rate = sum(self.recent_wins) / max(1, len(self.recent_wins)) * 100
        return {
            'episode': self.episode_count,
            'total_reward': self.current_episode_reward,
            'avg_reward': avg_reward,
            'win_rate': win_rate,
            'epsilon': self.epsilon,
            'q_table_size': len(self.q_table),
            'current_q_values': self.current_q_values,
            'last_action': self.last_action,
            'last_reward': self.last_reward,
        }

    """Save the Q-table and training state"""
    def save(self, filepath=None):
        if filepath is None:
            os.makedirs(cfg.Q_TABLE_DIR, exist_ok=True)
            filepath = os.path.join(cfg.Q_TABLE_DIR, 'q_table.pkl')

        data = {
            'q_table': dict(self.q_table),
            'epsilon': self.epsilon,
            'episode_count': self.episode_count,
            'episode_rewards': self.episode_rewards,
            'episode_scores': self.episode_scores,
            'win_count': self.win_count,
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        return filepath

    """Load the Q-table and training state"""
    def load(self, filepath=None):
        if filepath is None:
            filepath = os.path.join(cfg.Q_TABLE_DIR, 'q_table.pkl')

        if not os.path.exists(filepath):
            return False

        with open(filepath, 'rb') as f:
            data = pickle.load(f)

        loaded_q = data.get('q_table', {})
        self.q_table = defaultdict(lambda: {a: 0.0 for a in range(4)})
        self.q_table.update(loaded_q)
        self.epsilon = data.get('epsilon', cfg.EPSILON_MIN)
        self.episode_count = data.get('episode_count', 0)
        self.episode_rewards = data.get('episode_rewards', [])
        self.episode_scores = data.get('episode_scores', [])
        self.win_count = data.get('win_count', 0)

        self.recent_rewards = deque(self.episode_rewards[-100:], maxlen=100)
        recent_wins_data = [1 if s > 0 else 0 for s in self.episode_scores[-100:]]
        self.recent_wins = deque(recent_wins_data, maxlen=100)

        return True

    # ============ Auxiliary Function ============

    @staticmethod
    def _get_relative_direction(from_pos, to_pos):
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        if dx == 0 and dy == 0:
            return 4
        if abs(dx) >= abs(dy):
            return cfg.DIR_RIGHT if dx > 0 else cfg.DIR_LEFT
        else:
            return cfg.DIR_DOWN if dy > 0 else cfg.DIR_UP

    @staticmethod
    def _discretize_distance(dist):
        """Discretize the distance into four levels"""
        if dist < 3:
            return 0  # VERY_CLOSE
        elif dist < 6:
            return 1  # CLOSE
        elif dist < 10:
            return 2  # FAR
        else:
            return 3  # SAFE

    @staticmethod
    def _check_wall(x, y, direction, game_map):
        """Check if there is a wall in a certain direction"""
        nx, ny = game_map.get_neighbor(x, y, direction)
        return 1 if game_map.is_wall(nx, ny) else 0

    @staticmethod
    def _rotate_left(direction):
        mapping = {
            cfg.DIR_UP: cfg.DIR_LEFT,
            cfg.DIR_LEFT: cfg.DIR_DOWN,
            cfg.DIR_DOWN: cfg.DIR_RIGHT,
            cfg.DIR_RIGHT: cfg.DIR_UP,
        }
        return mapping.get(direction, cfg.DIR_LEFT)

    @staticmethod
    def _rotate_right(direction):
        mapping = {
            cfg.DIR_UP: cfg.DIR_RIGHT,
            cfg.DIR_RIGHT: cfg.DIR_DOWN,
            cfg.DIR_DOWN: cfg.DIR_LEFT,
            cfg.DIR_LEFT: cfg.DIR_UP,
        }
        return mapping.get(direction, cfg.DIR_RIGHT)


    def plot_learning_curve(self, save_path='learning_curve.png'):
        """Draw the learning curve and save it"""
        episodes = range(1, len(self.episode_rewards) + 1)
        plt.figure(figsize=(10, 5))
        plt.plot(episodes, self.episode_rewards, label='Total Reward per Episode')
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.title('Q-Learning Training Progress')
        plt.legend()
        plt.grid(True)
        plt.savefig(save_path)
        plt.show()

        print(f"Learning curve saved to {save_path}")
