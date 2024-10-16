from board import Board
from minimax import find_best_move
from display import display_board
from user_input import get_user_move

def main():
    board = Board()
    while not board.is_game_over():
        display_board(board)
        if board.white_to_move:
            print("Your turn (White). Enter your move in UCI format (e.g., e2e4):")
            move = None
            while move is None:
                user_input = input("Your move: ")
                move = get_user_move(board, user_input)
                if move is None:
                    print("Invalid move. Please try again.")
            board.make_move(move)
        else:
            print("AI's turn (Black). Thinking...")
            move = find_best_move(board, 3)
            print(f"AI plays: {move}")
            board.make_move(move)
    print("Game over.")
    display_board(board)
    if board.is_checkmate():
        winner = "Black" if board.white_to_move else "White"
        print(f"Checkmate! {winner} wins.")
    else:
        print("Draw.")

if __name__ == "__main__":
    main()
