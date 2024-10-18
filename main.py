import json
from board import Board
from minimax import find_best_move
from display import display_board
from board import Move
from evaluation import evaluate
from utils import algebraic_to_square
import random

def load_opening_tree(json_path):
    """
    Load the opening tree from a JSON file.
    """
    with open(json_path, 'r') as f:
        return json.load(f)

def square_to_algebraic(square):
    """
    Converts a square index (0-63) into algebraic notation (e.g., 0 -> 'a1').
    """
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    rank = (square // 8) + 1
    file = square % 8
    return f"{files[file]}{rank}"

def move_to_uci(move):
    """
    Converts a Move object or a dict into UCI string format.
    """
    if isinstance(move, dict):
        # Ensure 'from_square' and 'to_square' exist
        if 'from_square' not in move or 'to_square' not in move:
            raise KeyError("Move dict must contain 'from_square' and 'to_square'")
        from_square = square_to_algebraic(move['from_square'])
        to_square = square_to_algebraic(move['to_square'])
        promoted_piece = move.get('promoted_piece', '')
        return f"{from_square}{to_square}{promoted_piece}"
    elif isinstance(move, Move):
        from_square = square_to_algebraic(move.from_square)
        to_square = square_to_algebraic(move.to_square)
        uci_move = f"{from_square}{to_square}"
        if move.promoted_piece:
            uci_move += move.promoted_piece.lower()
        return uci_move
    else:
        raise TypeError("move_to_uci expects a Move object or a dict")

class ChessEngine:
    def __init__(self, opening_book):
        self.opening_book = opening_book
        self.current_node = opening_book  # Start at the root of the opening book

    def find_best_move(self, board, max_depth):
        """
        Determines the best move using the opening book or minimax algorithm.
        Returns a UCI string representing the move.
        """
        last_move = board.get_last_move()
        if last_move:
            try:
                last_move_str = move_to_uci(last_move)
            except (TypeError, KeyError) as e:
                print(f"Warning: Failed to convert last move to UCI - {e}")
                last_move_str = None

            if last_move_str and last_move_str in self.current_node:
                self.current_node = self.current_node[last_move_str]["next"]
            else:
                self.current_node = None  # Move not in opening book

        if self.current_node and "responses" in self.current_node:
            book_moves = self.current_node["responses"]
            if book_moves:
                selected_move = random.choice(book_moves)
                print(f"AI selects move from opening book: {selected_move}")  # Debugging
                # Update current_node to the next node based on selected_move
                if selected_move in self.current_node["next"]:
                    self.current_node = self.current_node["next"][selected_move]["next"]
                else:
                    self.current_node = None  # No further moves in opening book
                return selected_move

        # Fallback to minimax if no opening book moves are available
        print("No opening book moves available. Using minimax algorithm.")  # Debugging
        move_obj = find_best_move(board, max_depth)
        selected_move = move_to_uci(move_obj)
        print(f"AI selects move from minimax: {selected_move}")  # Debugging
        self.current_node = None  # Reset opening book traversal
        return selected_move

def parse_move(move_str, board):
    """
    Parses a UCI move string and returns a Move object.
    Returns None if the move is invalid.
    """
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

def main():
    # Path to your JSON opening book with UCI notation
    json_file_path = r"C:\Users\firefly\Desktop\Chess\pgns\chess_opening_tree.json"
    opening_book = load_opening_tree(json_file_path)
    engine = ChessEngine(opening_book)

    board = Board()

    while not board.is_game_over():
        display_board(board)

        if board.white_to_move:
            print("Your turn (White). Enter your move in UCI format (e.g., e2e4):")
            move = None
            while move is None:
                user_input = input("Your move: ").strip().lower()
                move = parse_move(user_input, board)
                if move is None:
                    print("Invalid move format. Please try again.")
                else:
                    legal_moves = board.generate_legal_moves()
                    # Convert legal moves to UCI strings for comparison
                    legal_moves_uci = [move_to_uci(m) for m in legal_moves]
                    if user_input not in legal_moves_uci:
                        print("Illegal move. Please try again.")
                        move = None
            board.make_move(move)

        else:
            print("AI's turn (Black). Thinking...")
            ai_move_str = engine.find_best_move(board, 3)
            print(f"AI plays: {ai_move_str}")
            move = parse_move(ai_move_str, board)
            if move is None:
                print("AI attempted an invalid move. Exiting game.")
                break
            board.make_move(move)

    print("Game over.")
    display_board(board)
    if board.is_checkmate():
        winner = "Black" if not board.white_to_move else "White"
        print(f"Checkmate! {winner} wins.")
    else:
        print("Draw.")

if __name__ == "__main__":
    main()
