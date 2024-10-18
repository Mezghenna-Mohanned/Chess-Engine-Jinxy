import cProfile
import pstats
from minimax import find_best_move
from board import Board
from display import display_board

def automated_game():
    board = Board()
    display_board(board)
    while not board.is_game_over():
        if board.white_to_move:
            move = find_best_move(board, 3)
        else:
            move = find_best_move(board, 3)
        board.make_move(move)
        display_board(board)
    print("Game over.")

def profile_main():
    profiler = cProfile.Profile()
    try:
        profiler.enable()
        automated_game()
    except KeyboardInterrupt:
        print("\nProfiling interrupted by user.")
    finally:
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.print_stats(20)

if __name__ == "__main__":
    profile_main()
