import chess
import time
import random
from functools import lru_cache
from evaluate import evaluate

class TranspositionEntry:
    def __init__(self, eval_score, depth, node_type):
        self.eval = eval_score
        self.depth = depth
        self.flag = node_type  # 'EXACT', 'LOWERBOUND', 'UPPERBOUND'

class Minimax:
    def __init__(self, time_limit_ms):
        self.time_limit_ms = time_limit_ms
        self.start_time = None
        self.ZOBRIST_TABLE = [[random.getrandbits(64) for _ in range(12)] for _ in range(64)]
        self.TRANSPOSITION_TABLE = {}
        self.current_hash = 0  # Will be initialized with the board's hash
        self.time_limit = 0

    def initialize_hash(self, board):
        """Compute the initial Zobrist hash of the board."""
        h = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                piece_index = self.get_piece_index(piece)
                h ^= self.ZOBRIST_TABLE[square][piece_index]
        self.current_hash = h

    def get_piece_index(self, piece):
        """Map a piece to an index between 0 and 11."""
        piece_type = piece.piece_type - 1  # Piece types are 1-6
        color_offset = 0 if piece.color == chess.WHITE else 6
        return piece_type + color_offset

    def update_hash(self, move, board):
        """Update the Zobrist hash incrementally when a move is made or undone."""
        piece_moved = board.piece_at(move.from_square)
        piece_moved_index = self.get_piece_index(piece_moved)
        self.current_hash ^= self.ZOBRIST_TABLE[move.from_square][piece_moved_index]
        self.current_hash ^= self.ZOBRIST_TABLE[move.to_square][piece_moved_index]

        # Handle captures
        if board.is_capture(move):
            if board.is_en_passant(move):
                captured_square = chess.square(
                    chess.square_file(move.to_square), chess.square_rank(move.from_square)
                )
            else:
                captured_square = move.to_square
            captured_piece = board.piece_at(captured_square)
            if captured_piece:
                captured_index = self.get_piece_index(captured_piece)
                self.current_hash ^= self.ZOBRIST_TABLE[captured_square][captured_index]

        # Handle promotions
        if move.promotion:
            # Remove the pawn at to_square
            pawn_piece = chess.Piece(chess.PAWN, piece_moved.color)
            pawn_index = self.get_piece_index(pawn_piece)
            self.current_hash ^= self.ZOBRIST_TABLE[move.to_square][pawn_index]
            # Add the promoted piece
            promoted_piece = chess.Piece(move.promotion, piece_moved.color)
            promoted_index = self.get_piece_index(promoted_piece)
            self.current_hash ^= self.ZOBRIST_TABLE[move.to_square][promoted_index]

        # Handle castling
        if board.is_castling(move):
            if move.to_square == chess.G1:
                # Short castling for White
                self._update_castling_hash(chess.H1, chess.F1, chess.ROOK, chess.WHITE)
            elif move.to_square == chess.C1:
                # Long castling for White
                self._update_castling_hash(chess.A1, chess.D1, chess.ROOK, chess.WHITE)
            elif move.to_square == chess.G8:
                # Short castling for Black
                self._update_castling_hash(chess.H8, chess.F8, chess.ROOK, chess.BLACK)
            elif move.to_square == chess.C8:
                # Long castling for Black
                self._update_castling_hash(chess.A8, chess.D8, chess.ROOK, chess.BLACK)

    def _update_castling_hash(self, from_square, to_square, piece_type, color):
        """Update the hash for castling moves."""
        rook_index = self.get_piece_index(chess.Piece(piece_type, color))
        self.current_hash ^= self.ZOBRIST_TABLE[from_square][rook_index]
        self.current_hash ^= self.ZOBRIST_TABLE[to_square][rook_index]

    def order_moves(self, board, moves=None):
        """Order moves using MVV-LVA, checks, promotions, and history heuristic."""
        def move_priority(move):
            priority = 0
            # Captures (MVV-LVA)
            if board.is_capture(move):
                attacker_value = self.get_piece_value(board.piece_at(move.from_square).piece_type)
                if board.is_en_passant(move):
                    victim_value = self.get_piece_value(chess.PAWN)
                else:
                    victim_value = self.get_piece_value(board.piece_at(move.to_square).piece_type)
                priority += 10_000 + victim_value - attacker_value
            # Promotions
            if move.promotion:
                priority += 8_000 + self.get_piece_value(move.promotion)
            # Checks
            if board.gives_check(move):
                priority += 5_000
            # Central control
            if move.to_square in [chess.D4, chess.E4, chess.D5, chess.E5]:
                priority += 1_000
            # Additional heuristics can be added here
            return priority

        if moves is None:
            moves = list(board.legal_moves)
        moves.sort(key=move_priority, reverse=True)
        return moves

    def get_piece_value(self, piece_type):
        """Get the material value of a piece type."""
        PIECE_VALUES = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0  # King value is set to 0 for move ordering purposes
        }
        return PIECE_VALUES.get(piece_type, 0)

    @lru_cache(maxsize=100000)
    def evaluate_board(self, board_fen, is_engine_white):
        """Evaluate the board using the provided evaluate function and cache the result."""
        board = chess.Board(board_fen)
        score = evaluate(board)
        # Adjust score based on engine's color
        if not is_engine_white:
            score = -score  # Invert score if engine is Black
        return score

    def quiescence_search(self, board, alpha, beta, is_maximizing, is_engine_white):
        """Perform quiescence search to evaluate quiet positions."""
        if time.time() - self.start_time >= self.time_limit:
            return self.evaluate_board(board.fen(), is_engine_white)

        stand_pat = self.evaluate_board(board.fen(), is_engine_white)

        if is_maximizing:
            if stand_pat >= beta:
                return beta
            if stand_pat > alpha:
                alpha = stand_pat
        else:
            if stand_pat <= alpha:
                return alpha
            if stand_pat < beta:
                beta = stand_pat

        moves = [move for move in board.legal_moves if board.is_capture(move) or move.promotion or board.gives_check(move)]
        moves = self.order_moves(board, moves)

        for move in moves:
            self.update_hash(move, board)
            board.push(move)
            score = self.quiescence_search(board, alpha, beta, not is_maximizing, is_engine_white)
            board.pop()
            self.update_hash(move, board)

            if is_maximizing:
                if score > alpha:
                    alpha = score
                if alpha >= beta:
                    break
            else:
                if score < beta:
                    beta = score
                if beta <= alpha:
                    break

        return alpha if is_maximizing else beta

    def _minimax_helper(self, depth, board, alpha, beta, is_maximizing, is_engine_white):
        """The recursive minimax function with alpha-beta pruning and transposition table."""
        if time.time() - self.start_time >= self.time_limit:
            return self.evaluate_board(board.fen(), is_engine_white)

        # Check for draw by threefold repetition or fifty-move rule
        if board.can_claim_threefold_repetition() or board.can_claim_fifty_moves():
            return 0  # Draw

        alpha_original = alpha
        entry = self.TRANSPOSITION_TABLE.get(self.current_hash)

        if entry and entry.depth >= depth:
            if entry.flag == 'EXACT':
                return entry.eval
            elif entry.flag == 'LOWERBOUND':
                alpha = max(alpha, entry.eval)
            elif entry.flag == 'UPPERBOUND':
                beta = min(beta, entry.eval)
            if alpha >= beta:
                return entry.eval

        if depth <= 0 or board.is_game_over():
            eval_score = self.quiescence_search(board, alpha, beta, is_maximizing, is_engine_white)
            return eval_score

        best_eval = -float('inf') if is_maximizing else float('inf')
        moves = self.order_moves(board)

        for move in moves:
            self.update_hash(move, board)
            board.push(move)
            eval = self._minimax_helper(depth - 1, board, alpha, beta, not is_maximizing, is_engine_white)
            board.pop()
            self.update_hash(move, board)

            if is_maximizing:
                if eval > best_eval:
                    best_eval = eval
                alpha = max(alpha, best_eval)
                if alpha >= beta:
                    break
            else:
                if eval < best_eval:
                    best_eval = eval
                beta = min(beta, best_eval)
                if beta <= alpha:
                    break

        # Store the result in the transposition table
        if best_eval <= alpha_original:
            flag = 'UPPERBOUND'
        elif best_eval >= beta:
            flag = 'LOWERBOUND'
        else:
            flag = 'EXACT'

        self.TRANSPOSITION_TABLE[self.current_hash] = TranspositionEntry(best_eval, depth, flag)
        return best_eval

    def iterative_deepening(self, board, is_engine_white):
        """Perform iterative deepening to find the best move within the time limit."""
        self.start_time = time.time()
        self.time_limit = self.time_limit_ms / 1000
        self.initialize_hash(board)
        best_move = None
        depth = 1

        while True:
            if time.time() - self.start_time >= self.time_limit:
                break
            new_best_move = None
            is_maximizing = board.turn == is_engine_white
            best_eval = -float('inf') if is_maximizing else float('inf')
            moves = self.order_moves(board)

            for move in moves:
                if time.time() - self.start_time >= self.time_limit:
                    break
                self.update_hash(move, board)
                board.push(move)
                eval = self._minimax_helper(depth - 1, board, -float('inf'), float('inf'), not is_maximizing, is_engine_white)
                board.pop()
                self.update_hash(move, board)

                if is_maximizing:
                    if eval > best_eval:
                        best_eval = eval
                        new_best_move = move
                else:
                    if eval < best_eval:
                        best_eval = eval
                        new_best_move = move

            if new_best_move is not None:
                best_move = new_best_move
            else:
                break

            depth += 1

        return best_move

    def find_best_move(self, board, is_engine_white):
        self.start_time = time.time()
        self.time_limit = self.time_limit_ms / 1000
        self.initialize_hash(board)
        best_move = None
        depth = 1

        # Start with the first legal move as a fallback in case time runs out
        legal_moves = list(board.legal_moves)
        if legal_moves:
            best_move = legal_moves[0]

        while time.time() - self.start_time < self.time_limit:
            new_best_move = None
            is_maximizing = board.turn == is_engine_white
            best_eval = -float('inf') if is_maximizing else float('inf')
            moves = self.order_moves(board)

            for move in moves:
                if time.time() - self.start_time >= self.time_limit:
                    # Return the best move found so far if time runs out
                    return best_move

                self.update_hash(move, board)
                board.push(move)
                eval = self._minimax_helper(depth - 1, board, -float('inf'), float('inf'), not is_maximizing, is_engine_white)
                board.pop()
                self.update_hash(move, board)

                if is_maximizing and eval > best_eval:
                    best_eval = eval
                    new_best_move = move
                elif not is_maximizing and eval < best_eval:
                    best_eval = eval
                    new_best_move = move

            if new_best_move is not None:
                best_move = new_best_move

            depth += 1  # Increase depth for the next iteration if there's time left

        return best_move
