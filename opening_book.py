import chess.pgn
from collections import defaultdict

def load_opening_book_from_pgn(pgn_file_path):
    opening_book = defaultdict(list)
    with open(pgn_file_path, 'r', encoding='utf-8') as pgn:
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            board = game.board()
            for move in game.mainline_moves():
                fen = board.fen()
                opening_book[fen].append(move)
                board.push(move)
    return opening_book
