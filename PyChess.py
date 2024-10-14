import chess
import random

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
    current_fen = board.board_fen()
    for fen in opening_fens:
        if fen.startswith(current_fen):
            return fen
    return None

def play_game_with_openings(pgn_file, epd_file1, epd_file2):
    board = chess.Board()
    opening_fens = load_opening_fens(pgn_file) + load_opening_fens_from_epd(epd_file1) + load_opening_fens_from_epd(epd_file2)
    
    print("Starting with a standard chess position:")
    print(board)

    while not board.is_game_over():
        print(board)
        if board.turn == chess.WHITE:
            user_move = input("Your turn (White): Enter your move: ")
            try:
                move = chess.Move.from_uci(user_move)
                if move in board.legal_moves:
                    board.push(move)
                else:
                    print("Illegal move, try again.")
                    continue
            except:
                print("Invalid move format, try again.")
                continue
        else:
            print("AI's turn (Black):")
            matching_opening_fen = find_opening_match(board, opening_fens)
            if matching_opening_fen:
                print(f"AI found a matching opening position: {matching_opening_fen}")
                board.set_fen(matching_opening_fen)
            else:
                print("No matching opening found. Proceeding with regular AI move.")
                move = ai_move(board, depth=3)
                board.push(move)

    print(board)
    print("Game over!")
    result = board.result()
    print(f"Result: {result}")

if __name__ == "__main__":
    pgn_file = r"C:\Users\firefly\Documents\chessOp\TwoMoves_v1.pgn"
    epd_file1 = r"C:\Users\firefly\Documents\chessOp\dFRC_openings.epd"
    epd_file2 = r"C:\Users\firefly\Documents\chessOp\popularpos_lichess.epd"
    play_game_with_openings(pgn_file, epd_file1, epd_file2)
