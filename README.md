# Pac-Man Q-Learning

A Pac-Man game AI powered by Q-learning. The agent learns to collect pellets and avoid ghosts in a maze, eventually achieving a 100% win rate.

## Quick Start

### Installation
```bash
git clone https://github.com/yourusername/PacMan-Qlearning.git
cd PacMan-Qlearning
pip install pygame matplotlib
python main.py



Controls
1 – AI Play mode

2 – Train mode

S / L – Save / Load Q-table

P – Plot learning curve

R – Reset game

SPACE – Pause / Resume

ESC – Quit

+ / - – Adjust training speed (in Train mode)




Project Structure

main.py – Entry point

game_engine.py – Core game logic

entities.py – Pac-Man and Ghost classes

game_map.py – Map loading and utilities

q_learning_agent.py – Q-learning algorithm

renderer.py – UI rendering

controller.py – Input handling

config.py – Configuration file





Algorithm Overview

State space: 7 discrete features (nearest ghost direction/distance, second ghost distance, nearest pellet direction, front/left/right walls)

Action space: Up, down, left, right

Reward function: +10 for pellet, -500 for death, +1000 for win, -1 per step, -5 for hitting wall, shaping rewards +2/+5

Hyperparameters: α=0.1, γ=0.9, ε start=1.0, decay=0.995, min=0.01