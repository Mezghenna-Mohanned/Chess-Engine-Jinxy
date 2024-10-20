from board import Board
from minimax import find_best_move
from display import display_board
from board import Move
from evaluation import evaluate
from opening_book import load_opening_book_from_pgn
from utils import algebraic_to_square
import random

def main():
    pgn_file_path = r"C:\Users\firefly\Desktop\Chess\pgns\wrchessmast24.pgn"
    opening_book = load_opening_book_from_pgn(pgn_file_path)
    engine = ChessEngine(opening_book)

    board = Board()
    
    while not board.is_game_over():
        display_board(board)
        
        if board.white_to_move:
            print("Your turn (White). Enter your move in UCI format (e.g., e2e4):")
            move = None
            while move is None:
                user_input = input("Your move: ")
                move = parse_move(user_input, board)
                if move is None:
                    print("Invalid move. Please try again.")
                else:
                    legal_moves = board.generate_legal_moves()
                    if move not in legal_moves:
                        print("Illegal move. Please try again.")
                        move = None
            board.make_move(move)
        
        else:
            print("AI's turn (Black). Thinking...")
            move = engine.find_best_move(board, 3)
            print(f"AI plays: {move}")
            board.make_move(move)
    
    print("Game over.")
    display_board(board)
    if board.is_checkmate():
        winner = "Black" if not board.white_to_move else "White"
        print(f"Checkmate! {winner} wins.")
    else:
        print("Draw.")

class ChessEngine:
    def __init__(self, opening_book):
        self.opening_book = opening_book

    def find_best_move(self, board, max_depth):
        fen = board.fen()
        if fen in self.opening_book:
            book_moves = self.opening_book[fen]
            if book_moves:
                return random.choice(book_moves)
            
        return find_best_move(board, max_depth)

def parse_move(move_str, board):
    if len(move_str) < 4 or len(move_str) > 5:
        return None

    from_square = algebraic_to_square(move_str[0:2])
    to_square = algebraic_to_square(move_str[2:4])

    if from_square is None or to_square is None:
        return None

    piece = board.get_piece_at_square(from_square)
    if piece is None:
        return None

    captured_piece = None
    if board.is_square_occupied_by_opponent(to_square):
        captured_piece = board.get_piece_at_square(to_square)

    promoted_piece = None
    if len(move_str) == 5:
        promotion_char = move_str[4]
        if promotion_char.upper() in ['Q', 'R', 'B', 'N']:
            promoted_piece = promotion_char.upper() if piece.isupper() else promotion_char.lower()
        else:
            return None

    is_en_passant = False
    if piece.upper() == 'P' and to_square == board.en_passant_target:
        is_en_passant = True
        captured_piece = 'p' if piece.isupper() else 'P'

    is_castling = False
    if piece.upper() == 'K' and abs(from_square - to_square) == 2:
        is_castling = True

    move = Move(piece, from_square, to_square, captured_piece, promoted_piece, is_en_passant, is_castling)
    return move

if __name__ == "__main__":
    main()