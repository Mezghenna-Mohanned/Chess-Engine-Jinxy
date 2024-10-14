import chess
import random

# Piece values for evaluation
piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

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

def evaluate_board(board):
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value
    return score

def minimax(board, depth, alpha, beta, is_maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

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
    best_move = None
    best_value = -float('inf')

    legal_moves = list(board.legal_moves)
    random.shuffle(legal_moves)

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
