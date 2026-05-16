# Python Chess Engines

Custom chess engines built from scratch in Python using two different artificial intelligence search architectures:

- Minimax with Alpha-Beta Pruning
- Monte Carlo Tree Search (MCTS)

The project includes a graphical interface for human-vs-engine gameplay, configurable time constraints, and automated engine-vs-engine gameplay support.

## Features
- Complete chess game implementation
- Legal move generation
- Human-vs-engine GUI gameplay
- Engine-vs-engine gameplay
- Configurable time controls
- Minimax with Alpha-Beta Pruning
- Monte Carlo Tree Search (MCTS)
- Positional evaluation heuristics
- Piece-square table evaluation
- Automated PGN game logging

## Technologies
- Python
- Pygame
- Artificial Intelligence Search Algorithms

## Engine Architectures

### Minimax Engine
Implements deterministic adversarial search using Minimax with Alpha-Beta Pruning to reduce unnecessary branch exploration and improve search efficiency.

### Monte Carlo Tree Search Engine
Implements probabilistic search using Monte Carlo Tree Search (MCTS), balancing exploration and exploitation through repeated simulation-based evaluation.

## GUI Gameplay
The project includes a graphical interface allowing users to:
- Play against either engine
- Select engine colour
- Configure time constraints
- Observe real-time engine decisions

## Repository Structure
```txt
Chess/                  Core chess logic and board representation
mcts.py                 Monte Carlo Tree Search engine
minimax.py              Minimax engine with Alpha-Beta Pruning
evaluate.py             Position evaluation heuristics
usermatchGUI.py         GUI gameplay interface
botmatch.py             Engine-vs-engine gameplay
```
## Setup
Before running the project, extract `Chess.zip` into the project directory since it contains required engine dependencies and core chess logic.

## Screenshots
<img width="2102" height="1010" alt="Screenshot 2026-05-16 at 4 43 53 PM" src="https://github.com/user-attachments/assets/9d739413-8be6-4523-b1fd-3c869841758d" />

## Run
```bash
python3 human_vs_engine_gui.py
```

## Future Improvements
- Opening book integration
- Endgame tablebases
- Improved move ordering
- Stronger evaluation heuristics
- Multithreaded search
- Neural-network-assisted evaluation
