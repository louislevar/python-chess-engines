import chess

# Piece-square tables (from White's perspective)
pawn_table = [
     0,   5,  10,  15,  15,  10,   5,   0,
     5,  10,  15,  20,  20,  15,  10,   5,
     5,  10,  15,  20,  20,  15,  10,   5,
     5,  10,  15,  20,  20,  15,  10,   5,
     0,   5,  10,  15,  15,  10,   5,   0,
     5,   0,   0,  -5,  -5,   0,   0,   5,
     5,  10,  10, -10, -10,  10,  10,   5,
     0,   0,   0,   0,   0,   0,   0,   0
]

knight_table = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,   0,   0,   0,   0, -20, -40,
    -30,   0,  10,  15,  15,  10,   0, -30,
    -30,   5,  15,  20,  20,  15,   5, -30,
    -30,   0,  15,  20,  20,  15,   0, -30,
    -30,   5,  10,  15,  15,  10,   5, -30,
    -40, -20,   0,   5,   5,   0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

bishop_table = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,   5,   0,   0,   0,   0,   5, -10,
    -10,  10,  10,  10,  10,  10,  10, -10,
    -10,   0,  10,  10,  10,  10,   0, -10,
    -10,   5,   5,  10,  10,   5,   5, -10,
    -10,   0,   5,   5,   5,   5,   0, -10,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]

rook_table = [
     0,   0,   5,  10,  10,   5,   0,   0,
     0,   5,   5,  10,  10,   5,   5,   0,
     0,   0,   5,  10,  10,   5,   0,   0,
     0,   0,   5,  10,  10,   5,   0,   0,
     0,   0,   5,  10,  10,   5,   0,   0,
     0,   0,   5,  10,  10,   5,   0,   0,
     0,   0,   5,  10,  10,   5,   0,   0,
     0,   0,   5,  10,  10,   5,   0,   0
]

queen_table = [
    -20, -10, -10,  -5,  -5, -10, -10, -20,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -10,   0,   5,   5,   5,   5,   0, -10,
     -5,   0,   5,   5,   5,   5,   0,  -5,
      0,   0,   5,   5,   5,   5,   0,  -5,
    -10,   5,   5,   5,   5,   5,   0, -10,
    -10,   0,   5,   0,   0,   0,   0, -10,
    -20, -10, -10,  -5,  -5, -10, -10, -20
]

king_table_middlegame = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
     20,  20,   0,   0,   0,   0,  20,  20,
     20,  30,  10,   0,   0,  10,  30,  20
]

king_table_endgame = [
    -50, -40, -30, -20, -20, -30, -40, -50,
    -30, -20, -10,   0,   0, -10, -20, -30,
    -30, -10,  20,  30,  30,  20, -10, -30,
    -30, -10,  30,  40,  40,  30, -10, -30,
    -30, -10,  30,  40,  40,  30, -10, -30,
    -30, -10,  20,  30,  30,  20, -10, -30,
    -30, -30,   0,   0,   0,   0, -30, -30,
    -50, -30, -30, -30, -30, -30, -30, -50
]

# Piece values (excluding the king's material value)
piece_values = {
    chess.PAWN:   100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK:   500,
    chess.QUEEN:  900,
    chess.KING:     0  # Exclude king's material value
}

def get_piece_square_table(piece_type, endgame=False):
    if piece_type == chess.PAWN:
        return pawn_table
    elif piece_type == chess.KNIGHT:
        return knight_table
    elif piece_type == chess.BISHOP:
        return bishop_table
    elif piece_type == chess.ROOK:
        return rook_table
    elif piece_type == chess.QUEEN:
        return queen_table
    elif piece_type == chess.KING:
        return king_table_endgame if endgame else king_table_middlegame
    return None

def get_piece_value(piece_type):
    return piece_values.get(piece_type, 0)

def is_endgame(board):
    """Determine if the game is in the endgame phase."""
    # Consider endgame when both sides have no queens or when
    # one side has a queen and both sides have minor pieces
    total_material = sum(
        get_piece_value(piece.piece_type)
        for piece in board.piece_map().values()
    )
    # Adjust threshold as needed
    return total_material <= 2000

def evaluate(board):
    """Evaluate the board position with material and positional factors."""
    if board.is_checkmate():
        # The side to move is checkmated
        return -10000 if board.turn == chess.WHITE else 10000
    elif board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return 0  # Draw

    score = 0
    endgame = is_endgame(board)

    # Material balance and piece-square table evaluation combined
    for square, piece in board.piece_map().items():
        value = get_piece_value(piece.piece_type)
        pst = get_piece_square_table(piece.piece_type, endgame)
        square_value = 0
        if pst:
            if piece.color == chess.WHITE:
                square_value = pst[square]
            else:
                square_value = pst[chess.square_mirror(square)]
        if piece.color == chess.WHITE:
            score += value + square_value
        else:
            score -= value + square_value

    # Normalize score
    normalization_factor = 10000.0  # Adjusted normalization factor
    normalized_score = score / normalization_factor
    normalized_score = max(min(normalized_score, 1), -1)  # Clamp to [-1, 1]

    return normalized_score