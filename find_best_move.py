import chess
from Ai.minimax import minimax
from Ai.alpha_beta import alpha_beta

def find_best_move(board, depth, use_alpha_beta=True):
    """Find the best move for the AI using Minimax or Alpha-Beta pruning."""
    if use_alpha_beta:
        best_eval = float('-inf')
        best_move = None
        for move in board.legal_moves:
            board.push(move)
            move_eval = alpha_beta(board, depth - 1, float('-inf'), float('inf'), False)
            board.pop()
            if move_eval > best_eval:
                best_eval = move_eval
                best_move = move
    else:
        best_eval = float('-inf')
        best_move = None
        for move in board.legal_moves:
            board.push(move)
            move_eval = minimax(board, depth - 1, False)
            board.pop()
            if move_eval > best_eval:
                best_eval = move_eval
                best_move = move
                
    return best_move
