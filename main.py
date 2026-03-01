"""Pac-Man Game - Main Program"""
import sys
import pygame
import config as cfg
from game_engine import GameEngine
from q_learning_agent import QLearningAgent
from renderer import Renderer
from controller import Controller

"""Main Class of Pac-Man Game"""
class PacManGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man Q-Learning")
        self.clock = pygame.time.Clock()

        self.engine = GameEngine()
        self.agent = QLearningAgent()
        self.renderer = Renderer(self.screen)
        self.controller = Controller()

        self.running = True
        self.max_steps_per_episode = 500  # avoid stuck

    def run(self):
        """Main Loop"""
        while self.running:
            dt = self.clock.tick(cfg.FPS) / 1000.0
            dt = min(dt, 0.05)  # 防止大跳帧

            self.controller.buttons = self.renderer.buttons

            # deal with events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    self.agent.plot_learning_curve()  # call drawing function
            self.controller.process_events(events)


            # check if quit
            if self.controller.quit_requested:
                self.running = False
                break

            # pause
            if self.controller.pause_requested:
                if not self.engine.game_over and not self.engine.game_won:
                    self.engine.paused = not self.engine.paused

            # save/load Q-Table
            if self.controller.save_requested:
                path = self.agent.save()
                print(f"[INFO] Q-table saved to {path}")

            if self.controller.load_requested:
                if self.agent.load():
                    print("[INFO] Q-table loaded successfully")
                else:
                    print("[WARN] No Q-table file found")

            # reset
            if self.controller.reset_requested:
                self.engine.reset()

            # update with mode
            mode = self.controller.mode
            if mode == cfg.MODE_AI_PLAY:
                self._update_ai_play(dt)
            elif mode == cfg.MODE_AI_TRAIN:
                self._update_ai_train(dt)

            # rendering
            ai_stats = self.agent.get_stats()
            ai_stats['state_key'] = self.agent.current_state_key
            self.renderer.render(
                self.engine, mode, ai_stats,
                self.controller.training_speed, dt
            )

        pygame.quit()
        sys.exit()

    """AI play mode"""
    def _update_ai_play(self, dt):
        if self.engine.game_over or self.engine.game_won or self.engine.paused:
            return

        self.engine.move_timer += dt
        if self.engine.move_timer >= self.engine.move_interval:
            self.engine.move_timer = 0.0

            state_info = self.engine.get_state_for_ai()
            state_key = self.agent.extract_state(state_info)

            # with low epsilon in AI mode
            old_eps = self.agent.epsilon
            self.agent.epsilon = 0.02  # greedy
            action = self.agent.choose_action(
                state_key, self.engine.game_map, self.engine.pacman.pos
            )
            self.agent.epsilon = old_eps

            # act and get reward
            reward, done, info = self.engine.step(action)

            # record the last action and reward
            self.agent.last_action = action
            self.agent.last_reward = reward

            # check win or lose
            if len(self.engine.pellets) == 0 and len(self.engine.power_pellets) == 0:
                self.engine.game_won = True
            if self.engine.lives <= 0:
                self.engine.game_over = True

            self.engine.pacman.anim_frame = (self.engine.pacman.anim_frame + 1) % 6

    """AI training mode"""
    def _update_ai_train(self, dt):
        speed = self.controller.training_speed

        for _ in range(speed):
            if self.engine.game_over or self.engine.game_won:
                # end the round, record and reset
                self.agent.on_episode_end(
                    self.engine.score,
                    self.engine.game_won
                )
                self.engine.reset()

                if self.agent.episode_count % cfg.CHECKPOINT_INTERVAL == 0:
                    self.agent.save()
                    print(f"[TRAIN] Episode {self.agent.episode_count} | "
                          f"Avg Reward: {self.agent.get_stats()['avg_reward']:.1f} | "
                          f"Win Rate: {self.agent.get_stats()['win_rate']:.1f}% | "
                          f"Epsilon: {self.agent.epsilon:.4f}")
                continue

            # get current state
            state_info = self.engine.get_state_for_ai()
            state_key = self.agent.extract_state(state_info)

            # choose action
            action = self.agent.choose_action(
                state_key, self.engine.game_map, self.engine.pacman.pos
            )

            # perform action
            reward, done, info = self.engine.step(action)

            self.agent.last_action = action
            self.agent.last_reward = reward

            # get new state
            new_state_info = self.engine.get_state_for_ai()
            new_state_key = self.agent.extract_state(new_state_info)

            # updata Q value
            self.agent.update(state_key, action, reward, new_state_key, done)

            # avoid stuck
            if self.agent.current_episode_steps >= self.max_steps_per_episode:
                self.engine.game_over = True


def main():
    game = PacManGame()
    game.run()


if __name__ == "__main__":
    main()