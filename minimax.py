from evaluation import evaluate
from multiprocessing import Pool, cpu_count
import time

TT_SIZE = 1000000
transposition_table = {}

def quiescence_search(board, alpha, beta, color):
    original_white_to_move = board.white_to_move

    stand_pat = color * evaluate(board)

    board.white_to_move = original_white_to_move

    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    moves = board.generate_capture_moves()
    moves = order_moves(moves)

    for move in moves:
        board.make_move(move)
        score = -quiescence_search(board, -beta, -alpha, -color)
        board.undo_move(move)
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha

def negamax(board, depth, alpha, beta, color):
    alpha_orig = alpha

    board_hash = board.zobrist_hash
    tt_entry = transposition_table.get(board_hash)
    if tt_entry and tt_entry['depth'] >= depth:
        if tt_entry['flag'] == 'exact':
            return tt_entry['value']
        elif tt_entry['flag'] == 'lowerbound':
            alpha = max(alpha, tt_entry['value'])
        elif tt_entry['flag'] == 'upperbound':
            beta = min(beta, tt_entry['value'])
        if alpha >= beta:
            return tt_entry['value']

    if depth == 0 or board.is_game_over():
        original_white_to_move = board.white_to_move

        value = quiescence_search(board, alpha, beta, color)

        board.white_to_move = original_white_to_move

        return value

    max_eval = float('-inf')
    moves = board.generate_legal_moves()
    if not moves:
        return color * evaluate(board)

    moves = order_moves(moves)

    for move in moves:
        board.make_move(move)
        eval = -negamax(board, depth - 1, -beta, -alpha, -color)
        board.undo_move(move)
        max_eval = max(max_eval, eval)
        alpha = max(alpha, eval)
        if alpha >= beta:
            break

    flag = 'exact'
    if max_eval <= alpha_orig:
        flag = 'upperbound'
    elif max_eval >= beta:
        flag = 'lowerbound'

    if len(transposition_table) > TT_SIZE:
        transposition_table.pop(next(iter(transposition_table)))
    transposition_table[board_hash] = {'value': max_eval, 'depth': depth, 'flag': flag}

    return max_eval

def find_best_move(board, max_depth):
    best_move = None
    best_eval = float('-inf')
    color = 1 if board.white_to_move else -1
    moves = board.generate_legal_moves()
    if not moves:
        return None
    moves = order_moves(moves)

    for depth in range(1, max_depth + 1):
        current_best_eval = float('-inf')
        current_best_move = None
        for move in moves:
            board.make_move(move)
            eval = -negamax(board, depth - 1, float('-inf'), float('inf'), -color)
            board.undo_move(move)
            if eval > current_best_eval:
                current_best_eval = eval
                current_best_move = move
        best_eval = current_best_eval
        best_move = current_best_move
        moves.sort(key=lambda m: move_ordering_score(board, m), reverse=True)
    return best_move

def order_moves(moves):
    moves.sort(key=lambda move: move_ordering_score(None, move), reverse=True)
    return moves

def move_ordering_score(board, move):
    score = 0
    if move.captured_piece:
        score += 10 * get_piece_value(move.captured_piece) - get_piece_value(move.piece)
    if move.promoted_piece:
        score += get_piece_value(move.promoted_piece)
    return score

def get_piece_value(piece):
    piece_values = {
        'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
        'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000
    }
    return piece_values.get(piece, 0)
