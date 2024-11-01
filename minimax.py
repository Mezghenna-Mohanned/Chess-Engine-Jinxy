from evaluation import evaluate
from multiprocessing import Pool, cpu_count
import time
import sys

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

    capture_moves = board.generate_capture_moves()
    capture_moves = order_moves(capture_moves)

    for move in capture_moves:
        board.make_move(move)
        score = -quiescence_search(board, -beta, -alpha, -color)
        board.undo_move(move)
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha

def negamax(board, depth, alpha, beta, color, start_time, time_limit):
    alpha_orig = alpha
    if time.time() - start_time > time_limit:
        raise TimeoutError("Search timed out")

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
        try:
            eval = -negamax(board, depth - 1, -beta, -alpha, -color, start_time, time_limit)
        except TimeoutError:
            board.undo_move(move)
            raise
        board.undo_move(move)
        if eval > max_eval:
            max_eval = eval
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

def find_best_move(board, max_depth, time_limit=5.0):
    """
    Finds the best move using iterative deepening and Negamax with alpha-beta pruning.
    Args:
        board (Board): Current board state.
        max_depth (int): Maximum search depth.
        time_limit (float): Time limit in seconds for the search.
    Returns:
        Move or None: The best move found within the time limit.
    """
    best_move = None
    best_eval = float('-inf')
    color = 1 if board.white_to_move else -1
    legal_moves = board.generate_legal_moves()
    if not legal_moves:
        return None

    moves = order_moves(legal_moves)

    start_time = time.time()

    try:
        for depth in range(1, max_depth + 1):
            current_best_eval = float('-inf')
            current_best_move = None
            for move in moves:
                board.make_move(move)
                try:
                    eval = -negamax(board, depth - 1, float('-inf'), float('inf'), -color, start_time, time_limit)
                except TimeoutError:
                    board.undo_move(move)
                    raise
                board.undo_move(move)
                if eval > current_best_eval:
                    current_best_eval = eval
                    current_best_move = move
            if current_best_move:
                best_eval = current_best_eval
                best_move = current_best_move
            if abs(best_eval) > 10000:
                break
            if best_move:
                moves = [best_move] + [m for m in moves if m != best_move]
    except TimeoutError:
        print("Search timed out. Returning the best move found so far.")
        return best_move

    return best_move

def order_moves(moves):
    """
    Orders moves to improve the efficiency of alpha-beta pruning.
    Prioritizes captures, promotions, and checks.
    Args:
        moves (list of Move): List of possible moves.
    Returns:
        list of Move: Ordered list of moves.
    """
    def move_ordering(move):
        score = 0
        if move.is_castling:
            score += 1000
        if move.promoted_piece:
            score += 900
        if move.captured_piece:
            piece_values = {
                'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
                'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000
            }
            score += piece_values.get(move.captured_piece, 0)
        return score

    moves_sorted = sorted(moves, key=move_ordering, reverse=True)
    return moves_sorted

def get_piece_value(piece):
    piece_values = {
        'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
        'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000
    }
    return piece_values.get(piece, 0)
