import chess
import random
import numpy as np

piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]

transposition_table = {}

def evaluate_board(board):
    """Evaluate the board position using advanced piece values and heuristics."""
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            value = piece_values[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value
            if piece.piece_type == chess.PAWN:
                score += 10 if piece.color == chess.WHITE else -10
            if square in center_squares:
                score += 5 if piece.color == chess.WHITE else -5
    return score

def quiescence_search(board, alpha, beta):
    """Use quiescence search to avoid horizon effects in tactical positions."""
    stand_pat = evaluate_board(board)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    for move in board.legal_moves:
        if board.is_capture(move):
            board.push(move)
            score = -quiescence_search(board, -beta, -alpha)
            board.pop()
            if score >= beta:
                return beta
            alpha = max(alpha, score)
    return alpha

def minimax(board, depth, alpha, beta, is_maximizing_player):
    """Minimax algorithm with Alpha-Beta pruning."""
    if board.fen() in transposition_table:
        return transposition_table[board.fen()]

    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if is_maximizing_player:
        max_eval = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        transposition_table[board.fen()] = max_eval
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        transposition_table[board.fen()] = min_eval
        return min_eval

def find_best_move(board, depth):
    """Find the best move for the AI using the enhanced Minimax algorithm."""
    best_move = None
    best_value = -float('inf')
    
    for move in board.legal_moves:
        board.push(move)
        board_value = minimax(board, depth - 1, -float('inf'), float('inf'), False)
        board.pop()

        if board_value > best_value:
            best_value = board_value
            best_move = move

    return best_move
