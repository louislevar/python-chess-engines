# usermatchGUI.py

import pygame
import sys
import chess
import chess.pgn
from mcts import MCTS
from minimax import Minimax  # Ensure Minimax is properly imported
import threading

def play_against_engine(engine, time_limit_ms, color):
    # Initialize Pygame
    pygame.init()
    screen_size = 480  # 60 pixels per square * 8 squares
    screen = pygame.display.set_mode((screen_size, screen_size))
    pygame.display.set_caption('Chess')

    # Define colors
    WHITE_COLOR = (255, 255, 255)
    BLACK_COLOR = (0, 0, 0)
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

    board = chess.Board()
    game = chess.pgn.Game()
    node = game

    # Determine player and engine colors based on user input
    if color.lower() == 'w':
        user_color = chess.WHITE
        is_engine_white = False
    else:
        user_color = chess.BLACK
        is_engine_white = True

    print(f"You are playing as {'White' if user_color == chess.WHITE else 'Black'}.")

    # Game loop variables
    running = True
    selected_square = None
    engine_state = {
        'thinking': False,
        'move': None
    }

    # Function to calculate the engine's move
    def calculate_engine_move():
        try:
            print("Engine is thinking...")
            best_move = engine.find_best_move(board.copy(), is_engine_white)
            if best_move is None:
                print("Engine could not find a valid move.")
                engine_state['thinking'] = False
                return
            engine_state['move'] = best_move
            engine_state['thinking'] = False
            print("Engine move:", best_move)
        except Exception as e:
            print("An error occurred during engine calculation:", e)
            engine_state['thinking'] = False

    # Start the engine's move if it's the engine's turn
    if board.turn == is_engine_white and not board.is_game_over():
        engine_state['thinking'] = True
        threading.Thread(target=calculate_engine_move).start()

    said = False
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if board.turn == user_color and not board.is_game_over():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    col = x // (screen_size // 8)
                    row = 7 - (y // (screen_size // 8))
                    square = chess.square(col, row)

                    if selected_square is None:
                        # Select a piece
                        if board.piece_at(square) and board.piece_at(square).color == user_color:
                            selected_square = square
                    else:
                        # Attempt to make a move
                        move = chess.Move(from_square=selected_square, to_square=square)
                        if move in board.legal_moves:
                            board.push(move)
                            node = node.add_variation(move)
                            selected_square = None

                            # Check if the game is over after the user's move
                            if board.is_game_over() and not said:
                                print("Game over!")
                                print(f"Result: {board.result()}")
                                said = True
                                break

                            # After user's move, start the engine's move calculation
                            if not engine_state['thinking'] and not board.is_game_over():
                                engine_state['thinking'] = True
                                threading.Thread(target=calculate_engine_move).start()
                        else:
                            # Check for promotions
                            if board.piece_at(selected_square) and board.piece_at(selected_square).piece_type == chess.PAWN and (chess.square_rank(square) == 0 or chess.square_rank(square) == 7):
                                promotion = chess.QUEEN  # Default to Queen promotion
                                move = chess.Move(from_square=selected_square, to_square=square, promotion=promotion)
                                if move in board.legal_moves:
                                    board.push(move)
                                    node = node.add_variation(move)
                                    selected_square = None

                                    # Check if the game is over after the user's move
                                    if board.is_game_over():
                                        print("Game over!")
                                        print(f"Result: {board.result()}")
                                        running = False  # Stop the game loop
                                        break

                                    # After user's move, start the engine's move calculation
                                    if not engine_state['thinking'] and not board.is_game_over():
                                        engine_state['thinking'] = True
                                        threading.Thread(target=calculate_engine_move).start()
                                else:
                                    print("Illegal move. Please try again.")
                                selected_square = None
                            else:
                                print("Illegal move. Please try again.")
                                selected_square = None

        # If the engine has calculated its move, apply it
        if engine_state['move'] is not None:
            board.push(engine_state['move'])
            node = node.add_variation(engine_state['move'])
            engine_state['move'] = None

            # Check if the game is over after the engine's move
            if board.is_game_over():
                print("Game over!")
                print(f"Result: {board.result()}")
                running = False  # Stop the game loop
                break

            # Start engine's move if needed (due to promotion)
            if board.turn == is_engine_white and not board.is_game_over():
                engine_state['thinking'] = True
                threading.Thread(target=calculate_engine_move).start()

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

                # Highlight selected square
                if selected_square == square:
                    pygame.draw.rect(screen, HIGHLIGHT_COLOR, rect)
                else:
                    pygame.draw.rect(screen, square_color, rect)

                # Draw the pieces
                piece = board.piece_at(square)
                if piece:
                    piece_symbol = piece.symbol()
                    piece_unicode_char = piece_unicode[piece_symbol]
                    text_color = WHITE_COLOR if piece.color == chess.WHITE else BLACK_COLOR
                    text_surface = font.render(piece_unicode_char, True, text_color)
                    text_rect = text_surface.get_rect(center=rect.center)
                    screen.blit(text_surface, text_rect)

        pygame.display.flip()

        if board.is_game_over():
            print("Game over!")
            print(f"Result: {board.result()}")

    # Save the game as PGN
    with open("user_vs_bot_game.pgn", "w") as pgn_file:
        pgn_file.write(str(game))

    print("The game has been saved as 'user_vs_bot_game.pgn'.")

if __name__ == '__main__':
    # Prompt the user for game settings
    try:
        time_limit_ms = int(input("Enter the time limit for the engine per move in milliseconds (e.g., 5000): "))
    except ValueError:
        print("Invalid input. Using default time limit of 1000 ms.")
        time_limit_ms = 1000

    engine_choice = input("Do you want to play against MCTS or Minimax? (mcts/minimax): ").strip().lower()
    if engine_choice not in ["mcts", "minimax"]:
        print("Invalid engine choice. Defaulting to MCTS.")
        engine_choice = "mcts"

    color = input("Choose your color (w/b): ").strip().lower()
    if color not in ["w", "b"]:
        print("Invalid color choice. Defaulting to White (w).")
        color = "w"

    # Initialize the selected engine
    if engine_choice == "mcts":
        engine = MCTS(time_limit_ms)
    else:
        engine = Minimax(time_limit_ms)  # Use Minimax engine if chosen

    # Start the game
    play_against_engine(engine, time_limit_ms, color)
