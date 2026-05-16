# bot_vs_bot_gui.py

import pygame
import sys
import chess
import chess.pgn
from mcts import MCTS
from minimax import Minimax
import threading
import random
import time

# Initialize Pygame
pygame.init()
screen_size = 480  # 60 pixels per square * 8 squares
screen = pygame.display.set_mode((screen_size, screen_size))
pygame.display.set_caption('Chess Bot vs Bot')

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE_COLOR = (240, 217, 181)
DARK_SQUARE_COLOR = (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 68)

# Define fonts
try:
    font_path = 'FreeSerif.ttf'  # Replace with the actual path if necessary
    font = pygame.font.Font(font_path, 48)
except FileNotFoundError:
    font = pygame.font.SysFont('DejaVu Sans', 48)

# Piece to Unicode mapping
piece_unicode = {
    'P': u'\u2659',
    'N': u'\u2658',
    'B': u'\u2657',
    'R': u'\u2656',
    'Q': u'\u2655',
    'K': u'\u2654',
    'p': u'\u265F',
    'n': u'\u265E',
    'b': u'\u265D',
    'r': u'\u265C',
    'q': u'\u265B',
    'k': u'\u265A',
}

def play_bots(engine1, engine2, engine1_name, engine2_name, time_limit_ms):
    board = chess.Board()
    game = chess.pgn.Game()
    node = game

    # Randomize who plays white
    is_engine1_white = random.choice([True, False])

    engine_white = engine1 if is_engine1_white else engine2
    engine_white_name = engine1_name if is_engine1_white else engine2_name
    engine_black = engine2 if is_engine1_white else engine1
    engine_black_name = engine2_name if is_engine1_white else engine1_name

    print(f"{engine_white_name} is White.")
    print(f"{engine_black_name} is Black.\n")

    # Game loop variables
    running = True
    last_move = None
    game_over = False
    result = None

    # Flags to manage engine thinking
    engine_state = {
        engine_white_name: {
            'thinking': False,
            'move': None
        },
        engine_black_name: {
            'thinking': False,
            'move': None
        }
    }

    # Function to calculate engine move
    def calculate_engine_move(engine, board_copy, engine_name, is_white):
        try:
            print(f"{engine_name} is thinking...")
            best_move = engine.find_best_move(board_copy, is_white)
            if not best_move:
                print(f"{engine_name} did not find a move. Choosing a random legal move.")
                best_move = random.choice(list(board_copy.legal_moves))
            engine_state[engine_name]['move'] = best_move
            engine_state[engine_name]['thinking'] = False
            print(f"{engine_name} played: {best_move}\n")
        except Exception as e:
            print(f"An error occurred with {engine_name}: {e}")
            engine_state[engine_name]['thinking'] = False

    # Start the first engine's move if it's its turn
    current_engine = engine_white if board.turn == chess.WHITE else engine_black
    current_engine_name = engine_white_name if board.turn == chess.WHITE else engine_black_name
    is_white = board.turn == chess.WHITE

    engine_state[current_engine_name]['thinking'] = True
    threading.Thread(target=calculate_engine_move, args=(current_engine, board.copy(), current_engine_name, is_white)).start()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

        # Check if any engine has completed its move
        for engine_name in [engine_white_name, engine_black_name]:
            if engine_state[engine_name]['move'] is not None:
                move = engine_state[engine_name]['move']
                if move in board.legal_moves:
                    board.push(move)
                    node = node.add_variation(move)
                    last_move = move
                else:
                    print(f"Engine {engine_name} attempted an illegal move: {move}")
                    running = False
                    game_over = True
                    result = "Illegal Move"
                    break

                engine_state[engine_name]['move'] = None

                # Check for game over
                if board.is_game_over():
                    game_over = True
                    result = board.result()
                    print("Game over!")
                    print(f"Result: {result}\n")
                    break

                # Switch to the next engine
                next_engine = engine_black if engine_name == engine_white_name else engine_white
                next_engine_name = engine_black_name if engine_name == engine_white_name else engine_white_name
                next_is_white = board.turn == chess.WHITE

                if not board.is_game_over():
                    engine_state[next_engine_name]['thinking'] = True
                    threading.Thread(target=calculate_engine_move, args=(next_engine, board.copy(), next_engine_name, next_is_white)).start()

        # Draw the board
        for row in range(8):
            for col in range(8):
                square = chess.square(col, row)
                x = col * (screen_size // 8)
                y = (7 - row) * (screen_size // 8)
                rect = pygame.Rect(x, y, screen_size // 8, screen_size // 8)

                # Determine square color
                if (row + col) % 2 == 0:
                    square_color = LIGHT_SQUARE_COLOR
                else:
                    square_color = DARK_SQUARE_COLOR

                pygame.draw.rect(screen, square_color, rect)

                # Highlight the last move
                if last_move and (square == last_move.from_square or square == last_move.to_square):
                    pygame.draw.rect(screen, HIGHLIGHT_COLOR, rect)

                # Draw the pieces
                piece = board.piece_at(square)
                if piece:
                    piece_symbol = piece.symbol()
                    piece_unicode_char = piece_unicode[piece_symbol]
                    text_color = WHITE if piece.color == chess.WHITE else BLACK
                    text_surface = font.render(piece_unicode_char, True, text_color)
                    text_rect = text_surface.get_rect(center=rect.center)
                    screen.blit(text_surface, text_rect)

        pygame.display.flip()

        # If game is over, stop making moves but keep the window open
        if game_over:
            # Optionally, display the result on the screen
            result_text = f"Game Over: {result}"
            text_surface = pygame.font.SysFont('DejaVu Sans', 24).render(result_text, True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(screen_size//2, screen_size//2))
            screen.blit(text_surface, text_rect)
            pygame.display.flip()
            time.sleep(3)  # Wait for 3 seconds before allowing window to remain open
            # Remove the break statement to keep the window open
            # Instead, you can set game_over to True and stop processing engine moves
            # Allow the loop to continue until the user closes the window

    # Save the game as PGN
    with open("bot_vs_bot_game.pgn", "w") as pgn_file:
        exporter = chess.pgn.FileExporter(pgn_file)
        game.accept(exporter)

    print("The game has been saved as 'bot_vs_bot_game.pgn'.")

if __name__ == '__main__':
    time_limit_ms = int(input("Enter the time limit for each engine per move in milliseconds (e.g., 5000): "))

    # Initialize engines
    mcts_engine = MCTS(time_limit_ms)
    minimax_engine = Minimax(time_limit_ms)

    # Run the match between MCTS and Minimax
    play_bots(mcts_engine, minimax_engine, "MCTS", "Minimax", time_limit_ms)
