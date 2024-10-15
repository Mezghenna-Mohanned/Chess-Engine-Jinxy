import chess

piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]

def load_opening_fens(pgn_file):
    fens = []
    with open(pgn_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('[FEN'):
                fen = line.split('"')[1]
                fens.append(fen)
    return fens

def load_opening_fens_from_epd(epd_file):
    fens = []
    with open(epd_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.strip():
                parts = line.split(';')
                fen = parts[0].strip()
                fens.append(fen)
    return fens

def is_protected(board, square):
    attackers = board.attackers(board.turn, square)
    return len(list(attackers)) > 0

def can_capture(board, square):
    attackers = board.attackers(not board.turn, square)
    return len(list(attackers)) > 0

def evaluate_board(board):
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            value = piece_values[piece.piece_type]

            if piece.color == chess.WHITE:
                score += value
                if is_protected(board, square):
                    score += 0.5
                if square in center_squares:
                    score += 0.5
                if can_capture(board, square):
                    score += value * 0.5

            else:
                score -= value
                if is_protected(board, square):
                    score -= 0.5
                if square in center_squares:
                    score -= 0.5
                if can_capture(board, square):
                    score -= value * 0.5
    return score

def quiescence_search(board, alpha, beta):
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
            if score > alpha:
                alpha = score
    return alpha

def minimax(board, depth, alpha, beta, is_maximizing_player):
    if depth == 0 or board.is_game_over():
        return quiescence_search(board, alpha, beta)

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

def ai_move(board, depth):
    if board.is_game_over():
        print("Game over!")
        return None

    best_move = None
    best_value = -float('inf')

    legal_moves = list(board.legal_moves)

    for move in legal_moves:
        board.push(move)
        board_value = minimax(board, depth - 1, -float('inf'), float('inf'), False)
        board.pop()

        if board_value > best_value:
            best_value = board_value
            best_move = move

    return best_move


def find_opening_match(board, opening_fens):
    current_fen = board.fen()
    for fen in opening_fens:
        if current_fen == fen:
            return fen
    return None
