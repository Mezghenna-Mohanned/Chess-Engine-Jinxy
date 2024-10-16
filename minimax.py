from evaluation import evaluate

transposition_table = {}

def quiescence_search(board, alpha, beta):
    stand_pat = evaluate(board)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    moves = board.generate_capture_moves()
    moves = order_moves(moves, board)
    for move in moves:
        board.make_move(move)
        score = -quiescence_search(board, -beta, -alpha)
        board.undo_move(move)
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha

def minimax(board, depth, alpha, beta, maximizing_player):
    board_hash = board.zobrist_hash()
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
        return quiescence_search(board, alpha, beta)

    if board.is_game_over():
        return evaluate(board)

    moves = board.generate_legal_moves()
    moves = order_moves(moves, board)
    if not moves:
        return evaluate(board)

    if maximizing_player:
        max_eval = float('-inf')
        for move in moves:
            board.make_move(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.undo_move(move)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        flag = 'exact'
        if max_eval <= alpha:
            flag = 'upperbound'
        elif max_eval >= beta:
            flag = 'lowerbound'
        transposition_table[board_hash] = {'value': max_eval, 'depth': depth, 'flag': flag}
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            board.make_move(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.undo_move(move)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        flag = 'exact'
        if min_eval <= alpha:
            flag = 'upperbound'
        elif min_eval >= beta:
            flag = 'lowerbound'
        transposition_table[board_hash] = {'value': min_eval, 'depth': depth, 'flag': flag}
        return min_eval

def find_best_move(board, max_depth):
    best_move = None
    best_eval = float('-inf') if board.white_to_move else float('inf')
    for depth in range(1, max_depth + 1):
        moves = board.generate_legal_moves()
        moves = order_moves(moves, board)
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

def order_moves(moves, board):
    captures = []
    quiet_moves = []
    for move in moves:
        if board.is_capture_move(move):
            captures.append(move)
        else:
            quiet_moves.append(move)
    captures.sort(key=lambda move: mvv_lva_score(move, board), reverse=True)
    return captures + quiet_moves

def mvv_lva_score(move, board):
    victim_piece = board.get_piece_at_square(move.to_square)
    attacker_piece = move.piece
    victim_value = board.get_piece_value(victim_piece)
    attacker_value = board.get_piece_value(attacker_piece)
    return victim_value * 10 - attacker_value
