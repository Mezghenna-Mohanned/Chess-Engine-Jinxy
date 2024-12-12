from src.Ai.evaluation import evaluate
import time

TT_SIZE = 1000000
transposition_table = {}

def quiescence_search(board, alpha, beta, color, depth=0, max_depth=4):
    """
    Performs a quiescence search to evaluate positions with potential captures.
    """
    stand_pat = color * evaluate(board)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    if depth >= max_depth:
        return stand_pat

    capture_moves = board.generate_capture_moves()
    capture_moves = order_moves(board, capture_moves)

    for move in capture_moves:
        board.make_move(move)
        score = -quiescence_search(board, -beta, -alpha, -color, depth + 1, max_depth)
        board.undo_move(move)
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha

def negamax(board, depth, alpha, beta, color, start_time, time_limit):
    """
    Implements the Negamax algorithm with alpha-beta pruning and transposition tables.
    """
    if time.time() - start_time > time_limit:
        raise TimeoutError("Search timed out")

    board_hash = board.zobrist_hash
    alpha_orig = alpha

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

    if depth == 0:
        return quiescence_search(board, alpha, beta, color)

    moves = board.generate_legal_moves()
    if not moves:
        if board.is_in_check():
            return -100000 + board.fullmove_number  # Checkmate
        else:
            return 0  # Stalemate

    moves = order_moves(board, moves)

    max_eval = float('-inf')
    best_move = None
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
            best_move = move
        alpha = max(alpha, eval)
        if alpha >= beta:
            break

    flag = 'exact'
    if max_eval <= alpha_orig:
        flag = 'upperbound'
    elif max_eval >= beta:
        flag = 'lowerbound'

    if len(transposition_table) > TT_SIZE:
        transposition_table.clear()
    transposition_table[board_hash] = {'value': max_eval, 'depth': depth, 'flag': flag, 'best_move': best_move}

    return max_eval

def find_best_move(board, max_depth, time_limit=5.0):
    """
    Finds the best move using iterative deepening and Negamax with alpha-beta pruning.
    """
    best_move = None
    color = 1 if board.white_to_move else -1
    moves = board.generate_legal_moves()
    if not moves:
        return None

    moves = order_moves(board, moves)
    start_time = time.time()

    try:
        for depth in range(1, max_depth + 1):
            current_best_eval = float('-inf')
            current_best_move = None
            alpha = float('-inf')
            beta = float('inf')
            for move in moves:
                board.make_move(move)
                try:
                    eval = -negamax(board, depth - 1, -beta, -alpha, -color, start_time, time_limit)
                except TimeoutError:
                    board.undo_move(move)
                    raise
                board.undo_move(move)
                if eval > current_best_eval:
                    current_best_eval = eval
                    current_best_move = move
                alpha = max(alpha, eval)
            if current_best_move:
                best_move = current_best_move
            if time.time() - start_time > time_limit:
                break
            moves = [best_move] + [m for m in moves if m != best_move]
    except TimeoutError:
        pass

    return best_move

def order_moves(board, moves):
    """
    Orders moves to improve the efficiency of alpha-beta pruning.
    Prioritizes captures, promotions, checks, and tactical motifs.
    """
    def move_ordering(move):
        score = 0
        if move.is_capture:
            captured_value = get_piece_value(move.captured_piece)
            attacker_value = get_piece_value(move.piece)
            score += 10 * (captured_value - attacker_value)
        if move.promotion:
            score += 900
        if board.is_check_move(move):
            score += 50
        if move.is_castling:
            score += 30
        return score

    return sorted(moves, key=move_ordering, reverse=True)

def get_piece_value(piece):
    """
    Returns the value of a piece for move ordering.
    """
    piece_values = {
        'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
        'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000
    }
    return piece_values.get(piece, 0)
