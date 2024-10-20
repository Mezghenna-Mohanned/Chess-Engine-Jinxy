import json
from board import Board, Move
from minimax import find_best_move
from display import display_board
from utils import algebraic_to_square
import random

def load_opening_tree(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

class ChessEngine:
    def __init__(self, opening_tree):
        self.opening_tree = opening_tree
        self.current_node = self.opening_tree

    def update_current_node(self, move_str):
        """
        Update the current node of the opening tree based on the move made by the player.
        """
        print(f"Updating current node with move: {move_str}")
        if self.current_node and move_str in self.current_node:
            if "next" in self.current_node[move_str]:
                print(f"Move {move_str} found in opening book, moving to next node.")
                self.current_node = self.current_node[move_str]["next"]
                return True
            else:
                print(f"Move {move_str} found but no further moves in the book.")
                self.current_node = None
                return False
        else:
            print(f"Move {move_str} not found in opening book.")
            self.current_node = None
            return False


    def find_best_move(self, board, max_depth):

        if self.current_node and "responses" in self.current_node:
            response_move = random.choice(self.current_node["responses"])
            print(f"AI selects move from opening book: {response_move}")
            if response_move in self.current_node["next"]:
                print(f"Moving to next node in the opening book after move: {response_move}")
                self.current_node = self.current_node["next"][response_move]["next"]
            return parse_move(response_move, board)
        else:
            print("Out of opening book. Using minimax algorithm.")
            return find_best_move(board, max_depth)


def parse_move(move_str, board):
    """
    Parse a move string (like 'd2d4') and return a Move object.
    """
    if len(move_str) < 4 or len(move_str) > 5:
        print("Invalid move format.")
        return None

    from_square = algebraic_to_square(move_str[0:2])
    to_square = algebraic_to_square(move_str[2:4])

    if from_square is None or to_square is None:
        print("Invalid move coordinates.")
        return None

    piece = board.get_piece_at_square(from_square)
    if piece is None:
        print("No piece at the specified position.")
        return None

    captured_piece = board.get_piece_at_square(to_square) if board.is_square_occupied_by_opponent(to_square) else None
    return Move(piece, from_square, to_square, captured_piece)

def main():
    json_file_path = r"C:\Users\firefly\Desktop\Chess\pgns\chess_opening_tree.json"
    opening_tree = load_opening_tree(json_file_path)
    engine = ChessEngine(opening_tree)
    board = Board()

    while not board.is_game_over():
        display_board(board)
        
        if board.white_to_move:

            user_input = input("Your move: ").strip()
            move = parse_move(user_input, board)
            if move and move in board.generate_legal_moves():
                in_opening_book = engine.update_current_node(user_input)
                if in_opening_book:
                    board.make_move(move)
                else:
                    print("Out of opening book. Proceeding with player's move.")
                    board.make_move(move)
            else:
                print("Illegal move.")

        else:
            print("AI's turn (Black). Thinking...")
            if engine.current_node and "responses" in engine.current_node:
                ai_move_str = random.choice(engine.current_node["responses"])
                ai_move = parse_move(ai_move_str, board)

                if ai_move and ai_move in board.generate_legal_moves():
                    print(f"AI selects move from opening book: {ai_move_str}")
                    engine.update_current_node(ai_move_str)
                    board.make_move(ai_move)
                else:
                    print("AI move from opening book is illegal or not found. Switching to minimax.")
                    ai_move = engine.find_best_move(board, 3)
                    if ai_move:
                        board.make_move(ai_move)
                        ai_move_str = f"{ai_move.from_square}{ai_move.to_square}"
                        print(f"AI plays using minimax: {ai_move_str}")
                    else:
                        print("AI could not find a valid move.")
            else:
                print("Out of opening book. Using minimax algorithm.")
                ai_move = engine.find_best_move(board, 3)
                if ai_move:
                    board.make_move(ai_move)
                    ai_move_str = f"{ai_move.from_square}{ai_move.to_square}"
                    print(f"AI plays using minimax: {ai_move_str}")
                else:
                    print("AI could not find a valid move.")

    print("Game over.")
    display_board(board)
    if board.is_checkmate():
        winner = "Black" if not board.white_to_move else "White"
        print(f"Checkmate! {winner} wins.")
    else:
        print("Draw.")


if __name__ == "__main__":
    main()
