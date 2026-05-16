import chess
import time
import random
import math
from evaluate import evaluate

class MCTSNode:
    def __init__(self, board, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.untried_moves = list(board.legal_moves)
        self.is_terminal = board.is_game_over()

        if parent is None:
            self.player = None  # Root node has no player
        else:
            # Player who made the move to reach this node
            self.player = not board.turn

class MCTS:
    def __init__(self, time_limit_ms):
        self.time_limit_ms = time_limit_ms
        self.start_time = None
        self.root_player = None
        self.Cp = 1.414  # Exploration parameter
        self.transposition_table = {}  # Initialize transposition table
        self.transposition_table_max_size = 100000  # Limit size of transposition table

    def find_best_move(self, board, is_engine_white):
        self.start_time = time.time()
        self.root_player = chess.WHITE if is_engine_white else chess.BLACK
        time_limit = self.time_limit_ms / 1000.0
        root_node = MCTSNode(board.copy())
        simulations = 0

        while time.time() - self.start_time < time_limit:
            node = self._select(root_node)
            value = self._simulate(node)
            self._backpropagate(node, value)
            simulations += 1

        # print(f"Simulations: {simulations}")

        if root_node.children:
            best_child = max(root_node.children, key=lambda c: c.visits)
            return best_child.move
        else:
            return random.choice(list(board.legal_moves))

    def _select(self, node):
        while not node.is_terminal:
            if node.untried_moves:
                return self._expand(node)
            else:
                node = self._uct_select(node)
        return node

    def _expand(self, node):
        move = node.untried_moves.pop()
        new_board = node.board.copy()
        new_board.push(move)
        child_node = MCTSNode(new_board, parent=node, move=move)
        node.children.append(child_node)
        return child_node

    def _simulate(self, node):
        board = node.board.copy()
        depth = 0
        max_depth = 10  # Reduced depth to speed up simulations

        while not board.is_game_over() and depth < max_depth:
            moves = list(board.legal_moves)
            if not moves:
                break
            move = self._select_simulation_move(board, moves)
            board.push(move)
            depth += 1

        # Use transposition table with board hash or FEN
        # Option 1: Use hash(board)
        # board_key = hash(board)

        # Option 2: Use board.fen()
        board_key = board.fen()

        if board_key in self.transposition_table:
            eval_value = self.transposition_table[board_key]
        else:
            eval_value = evaluate(board)
            if len(self.transposition_table) > self.transposition_table_max_size:
                self.transposition_table.clear()  # Limit transposition table size
            self.transposition_table[board_key] = eval_value

        eval_value = self._adjust_eval_for_player(eval_value)
        return eval_value

    def _backpropagate(self, node, value):
        while node is not None:
            node.visits += 1
            if node.player == self.root_player:
                node.value += value
            else:
                node.value -= value
            node = node.parent

    def _uct_select(self, node):
        log_parent_visits = math.log(node.visits + 1)

        def uct_value(child):
            if child.visits == 0:
                return float('inf')
            avg_value = child.value / child.visits
            # Adjust avg_value based on the player's perspective
            if child.player != self.root_player:
                avg_value = -avg_value
            exploration = self.Cp * math.sqrt(log_parent_visits / child.visits)
            return avg_value + exploration

        return max(node.children, key=uct_value)

    def _select_simulation_move(self, board, moves):
        # Simplified Heuristics: Prefer captures and promotions
        capturing_moves = []
        promotion_moves = []
        other_moves = []

        for move in moves:
            if board.is_capture(move):
                capturing_moves.append(move)
            elif move.promotion:
                promotion_moves.append(move)
            else:
                other_moves.append(move)

        if capturing_moves:
            return random.choice(capturing_moves)
        elif promotion_moves:
            return random.choice(promotion_moves)
        else:
            return random.choice(other_moves)

    def _adjust_eval_for_player(self, eval_value):
        if self.root_player == chess.BLACK:
            eval_value = -eval_value
        return eval_value
