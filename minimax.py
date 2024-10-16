from move_generation import generate_legal_moves
from evaluation import evaluate

def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate(board)

    if maximizing_player:
        max_eval = float('-inf')
        moves = board.generate_legal_moves()
        for move in moves:
            board.make_move(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.undo_move(move)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        moves = board.generate_legal_moves()
        for move in moves:
            board.make_move(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.undo_move(move)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(board, depth):
    best_eval = float('-inf') if board.white_to_move else float('inf')
    best_move = None
    moves = board.generate_legal_moves()
    for move in moves:
        board.make_move(move)
        eval = minimax(board, depth - 1, float('-inf'), float('inf'), not board.white_to_move)
        board.undo_move(move)
        if board.white_to_move and eval > best_eval:
            best_eval = eval
            best_move = move
        elif not board.white_to_move and eval < best_eval:
            best_eval = eval
            best_move = move
    return best_move
