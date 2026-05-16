import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# Initialize dictionaries to store parsed data for averaging
time_data = defaultdict(list)

# Read and parse data from file
with open("experiment_results.txt", "r") as file:
    for line in file:
        # Extract time constraint and result
        match = re.search(r'MCTS vs Minimax at (\d+) ms per move: (\S+)', line)
        if match:
            time_ms = int(match.group(1))             # Time constraint in ms
            if time_ms > 3000:                        # Exclude data after 3000 ms
                continue
            result = match.group(2)                   # Result (e.g., "1-0", "0-1")
            
            # Append parsed data to the dictionaries
            time_data[time_ms].append(result)

# Calculate average win rates at each time constraint
time_constraints = sorted(time_data.keys())
avg_minimax_win_rates = []
avg_mcts_win_rates = []

for time_ms in time_constraints:
    results = time_data[time_ms]
    total_games = len(results)

    # Count results
    minimax_wins = results.count("1-0")
    mcts_wins = results.count("0-1")

    avg_minimax_win_rates.append(minimax_wins / total_games)
    avg_mcts_win_rates.append(mcts_wins / total_games)

# Polynomial fits (2nd degree) for win rates
minimax_poly = np.polyfit(time_constraints, avg_minimax_win_rates, 2)
mcts_poly = np.polyfit(time_constraints, avg_mcts_win_rates, 2)

minimax_poly_eq = np.poly1d(minimax_poly)
mcts_poly_eq = np.poly1d(mcts_poly)

# Calculate variance and standard deviation
minimax_variance = np.var(avg_minimax_win_rates)
mcts_variance = np.var(avg_mcts_win_rates)
minimax_std_dev = np.std(avg_minimax_win_rates)
mcts_std_dev = np.std(avg_mcts_win_rates)

# Plotting the average win rates with polynomial fits
plt.figure(figsize=(10, 6))
plt.scatter(time_constraints, avg_minimax_win_rates, color='blue', label="Minimax Win Rate")
plt.plot(time_constraints, minimax_poly_eq(time_constraints), 'b-', label="Minimax Polynomial Fit")
plt.scatter(time_constraints, avg_mcts_win_rates, color='red', label="MCTS Win Rate")
plt.plot(time_constraints, mcts_poly_eq(time_constraints), 'r-', label="MCTS Polynomial Fit")
plt.xlabel("Time Constraints (ms)")
plt.ylabel("Win Rates")
plt.title("Win Rates for Minimax and MCTS Engines Across Time Constraints")
plt.legend()
plt.grid(True)
plt.show()

# Output polynomial formulas, variance, and standard deviation
print("Polynomial formula for Minimax win rate:", minimax_poly_eq)
print("Polynomial formula for MCTS win rate:", mcts_poly_eq)
print("\nMinimax variance:", minimax_variance)
print("Minimax standard deviation:", minimax_std_dev)
print("\nMCTS variance:", mcts_variance)
print("MCTS standard deviation:", mcts_std_dev)
