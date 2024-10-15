import chess

piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

POSITIONAL_VALUES = {
    chess.PAWN: [
        0, 0, 0, 0, 0, 0, 0, 0,  # 8th rank
        5, 5, 5, 5, 5, 5, 5, 5,  # 7th rank
        1, 1, 2, 3, 3, 2, 1, 1,  # 6th rank
        1, 1, 2, 3, 3, 2, 1, 1,  # 5th rank
        1, 1, 2, 3, 3, 2, 1, 1,  # 4th rank
        1, 1, 2, 3, 3, 2, 1, 1,  # 3rd rank
        5, 5, 5, 5, 5, 5, 5, 5,  # 2nd rank
        0, 0, 0, 0, 0, 0, 0, 0   # 1st rank
    ],
    chess.KNIGHT: [
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20, 0, 0, 0, 0, -20, -40,
        -30, 0, 10, 15, 15, 10, 0, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 0, 10, 15, 15, 10, 0, -30,
        -40, -20, 0, 0, 0, 0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50,
    ],
    chess.BISHOP: [
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 5, 10, 15, 15, 10, 5, -10,
        -10, 5, 10, 15, 15, 10, 5, -10,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -20, -10, -10, -10, -10, -10, -10, -20,
    ],
    chess.ROOK: [
        0, 0, 0, 5, 5, 0, 0, 0,
        0, 0, 0, 5, 5, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 5, 5, 5, 5, 5, 5, 5,
        0, 0, 0, 0, 0, 0, 0, 0,
    ],
    chess.QUEEN: [
        -20, -10, -10, -5, -5, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 5, 5, 5, 0, -10,
        -5, 0, 5, 5, 5, 5, 0, -5,
        0, 0, 5, 5, 5, 5, 0, 0,
        -10, 0, 5, 0, 0, 0, 0, -10,
        -10, -10, 0, -5, -5, -10, -10, -10,
        -20, -10, -10, -20, -20, -10, -10, -20,
    ],
    chess.KING: [
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
        20, 20, 0, 0, 0, 0, 20, 20,
        20, 30, 10, 0, 0, 10, 30, 20,
        0, 0, 0, 0, 0, 0, 0, 0,
    ]
}

def evaluate_board(board):
    """Evaluate the board position using piece values and positional values."""
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            value = piece_values[piece.piece_type]
            positional_value = POSITIONAL_VALUES[piece.piece_type][square]
            score += (value + positional_value) if piece.color == chess.WHITE else -(value + positional_value)
    return score

def quiescence(board, alpha, beta):
    """Quiescence search to avoid horizon effect."""
    stand_pat = evaluate_board(board)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    for move in board.legal_moves:
        if board.is_capture(move):
            board.push(move)
            score = -quiescence(board, -beta, -alpha)
            board.pop()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

    return alpha

def minimax(board, depth, alpha, beta, is_maximizing_player):
    """Minimax algorithm with alpha-beta pruning."""
    if depth == 0 or board.is_game_over():
        return quiescence(board, alpha, beta)

    legal_moves = list(board.legal_moves)

    if is_maximizing_player:
        max_eval = -float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(board, depth):
    """Determine the best move for the AI."""
    best_move = None
    best_value = -float('inf')

    for move in board.legal_moves:
        board.push(move)
        move_value = minimax(board, depth - 1, -float('inf'), float('inf'), False)
        board.pop()

        if move_value > best_value:
            best_value = move_value
            best_move = move

    return best_move
