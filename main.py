import json
from board import Board
from display import display_board
from board import Move
from utils import algebraic_to_square
import random
from minimax import find_best_move

def square_to_algebraic(square):
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    rank = square // 8 + 1
    file = square % 8
    return f"{files[file]}{rank}"

def parse_move_string(move_str, board):
    """
    Parses a move string in UCI format and returns a Move object.
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

class ChessEngine:
    def __init__(self, move_tree):
        self.move_tree = move_tree

    def get_ai_move(self, board, current_node, use_move_tree=True, max_depth=3):
        """
        Selects the AI's move based on the current node in the move tree.
        If no predefined move is found, falls back to the Minimax algorithm.
        """
        if use_move_tree and current_node:
            possible_moves = list(current_node.keys())
            if possible_moves:
                selected_move = random.choice(possible_moves)
                return selected_move

        print("Falling back to Minimax algorithm for move selection.")
        best_move = find_best_move(board, max_depth)
        if best_move:
            move_str = square_to_algebraic(best_move.from_square) + square_to_algebraic(best_move.to_square)
            if best_move.promoted_piece:
                move_str += f"={best_move.promoted_piece}"
            return move_str.lower()
        else:
            return None

def main():
    move_tree_path = r"C:\Users\firefly\Desktop\Chess\pgns\chess_opening_tree2.json"

    try:
        with open(move_tree_path, 'r') as f:
            move_tree = json.load(f)
    except FileNotFoundError:
        print(f"Move tree file not found at {move_tree_path}. Please ensure the file exists.")
        return

    engine = ChessEngine(move_tree)

    board = Board()
    current_node = move_tree
    use_move_tree = True

    while not board.is_game_over():
        display_board(board)

        if board.white_to_move:
            print("Your turn (White). Enter your move in UCI format (e.g., e2e4):")
            move = None
            while move is None:
                user_input = input("Your move: ")
                move = parse_move_string(user_input, board)
                if move is None:
                    print("Invalid move format. Please try again.")
                    continue

                move_uci = user_input.lower()
                if use_move_tree and move_uci not in current_node:
                    print("Move not found in the move tree. Switching to Minimax for future moves.")
                    use_move_tree = False
                elif use_move_tree:
                    if move_uci in current_node:
                        pass
                    else:
                        print("Move not found in the move tree. AI cannot respond.")
                        move = None
                        continue

                legal_moves = board.generate_legal_moves()
                if move not in legal_moves:
                    print("Illegal move. Please try again.")
                    move = None
                    continue

            board.make_move(move)

            if use_move_tree and move_uci in current_node:
                current_node = current_node[move_uci]
            else:
                current_node = {}
        else:
            print("AI's turn (Black). Thinking...")
            ai_move = engine.get_ai_move(board, current_node, use_move_tree=use_move_tree, max_depth=3)
            if ai_move:
                print(f"AI plays: {ai_move}")
                move_obj = parse_move_string(ai_move, board)
                if move_obj is not None:
                    board.make_move(move_obj)

                    ai_move_uci = ai_move.lower()
                    if use_move_tree and ai_move_uci in current_node:
                        current_node = current_node[ai_move_uci]
                    else:
                        current_node = {}
                else:
                    print("AI selected an invalid move.")
                    break
            else:
                print("AI has no predefined response.")
                break

    print("Game over.")
    display_board(board)
    if board.is_checkmate():
        winner = "Black" if not board.white_to_move else "White"
        print(f"Checkmate! {winner} wins.")
    else:
        print("Draw.")

if __name__ == "__main__":
    main()
