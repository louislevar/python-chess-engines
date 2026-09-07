# Python Chess Engines

Custom chess engines built from scratch in Python using two different artificial intelligence search architectures:

* Minimax with Alpha-Beta Pruning
* Monte Carlo Tree Search (MCTS)

The project includes a graphical interface for human-vs-engine gameplay, configurable time controls, and automated engine-vs-engine gameplay.

## Features

* Complete chess game implementation
* Legal move generation
* Human-vs-engine GUI gameplay
* Engine-vs-engine gameplay
* Configurable time controls
* Minimax with Alpha-Beta Pruning
* Monte Carlo Tree Search (MCTS)
* Positional evaluation heuristics
* Piece-square table evaluation
* Automated PGN game logging

## Technologies

* Python
* Pygame
* Artificial Intelligence Search Algorithms

## Engine Architectures

### Minimax with Alpha-Beta Pruning

The Minimax engine uses deterministic adversarial search to evaluate possible game states and select the strongest move.

Alpha-Beta Pruning reduces the number of positions that need to be evaluated by eliminating branches that cannot influence the final decision.

### Monte Carlo Tree Search

The MCTS engine uses probabilistic tree search to evaluate moves through repeated simulations.

The algorithm balances exploration of less-visited moves with exploitation of moves that have demonstrated stronger results.

## GUI Gameplay

The graphical interface allows users to:

* Play against either engine
* Select the engine's colour
* Configure time controls
* Observe engine decisions in real time

## Repository Structure

```text
Chess/                  Core chess logic and board representation
mcts.py                 Monte Carlo Tree Search engine
minimax.py              Minimax engine with Alpha-Beta Pruning
evaluate.py             Position evaluation heuristics
usermatchGUI.py         GUI gameplay interface
botmatch.py             Engine-vs-engine gameplay
requirements.txt        Python dependencies
```

## Setup

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/louislevar/python-chess-engines.git
cd python-chess-engines
```

Create and activate a virtual environment:

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Run

Start a human-vs-engine game:

```bash
python usermatchGUI.py
```

Run an engine-vs-engine match:

```bash
python botmatch.py
```

## Screenshots

<img width="2102" height="1010" alt="Chess Engine GUI" src="https://github.com/user-attachments/assets/9d739413-8be6-4523-b1fd-3c869841758d" />
