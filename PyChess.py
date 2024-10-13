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

def print_board(board):
    print(board)

def get_player_move(board):
    while True:
        try:
            move = input("Enter your move (e.g., e2e4): ")
            if move == "exit":
                return None
            chess_move = chess.Move.from_uci(move)
            if chess_move in board.legal_moves:
                return chess_move
            else:
                print("Invalid move. Please try again.")
        except Exception as e:
            print(f"Error: {e}. Please enter a valid move.")

def evaluate_board(board):
    evaluation = 0
    for piece in chess.PIECE_TYPES:
        evaluation += len(board.pieces(piece, chess.WHITE)) * piece_values[piece]
        evaluation -= len(board.pieces(piece, chess.BLACK)) * piece_values[piece]

    return evaluation

def minimax_alpha_beta(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        max_eval = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax_alpha_beta(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax_alpha_beta(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def get_ai_move(board, depth=3):
    best_move = None
    best_value = -float('inf')
    alpha = -float('inf')
    beta = float('inf')

    for move in board.legal_moves:
        board.push(move)
        move_value = minimax_alpha_beta(board, depth - 1, alpha, beta, False)
        board.pop()

        if move_value > best_value:
            best_value = move_value
            best_move = move

    return best_move if best_move else random.choice(list(board.legal_moves))

def main():
    board = chess.Board()
    
    while not board.is_game_over():
        print_board(board)
        
        print("Your turn (White):")
        player_move = get_player_move(board)
        if player_move is None:
            print("Exiting the game.")
            break
        board.push(player_move)

        if board.is_game_over():
            break

        print("AI's turn (Black):")
        ai_move = get_ai_move(board, depth=3)
        board.push(ai_move)

    print_board(board)
    print("Game over!")
    print("Result:", board.result())

if __name__ == "__main__":
    main()
