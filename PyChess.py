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

    for move in board.legal_moves:
        target_square = move.to_square
        target_piece = board.piece_at(target_square)

        if target_piece and target_piece.color == chess.BLACK:
            evaluation += piece_values[target_piece.piece_type]

        if board.is_attacked_by(chess.BLACK, move.from_square):
            evaluation -= piece_values[board.piece_at(move.from_square).piece_type] * 0.5

    return evaluation

def get_ai_move(board):
    best_move = None
    best_value = -float('inf')

    for move in board.legal_moves:
        board.push(move)
        move_value = evaluate_board(board)
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
        ai_move = get_ai_move(board)
        board.push(ai_move)

    print_board(board)
    print("Game over!")
    print("Result:", board.result())

if __name__ == "__main__":
    main()
