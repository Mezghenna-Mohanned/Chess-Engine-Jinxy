from src.core.move_generation import Move, generate_legal_moves
from src.utils.utils import algebraic_to_square

def get_user_move(board, user_input):
    if len(user_input) != 4:
        return None
    from_square = algebraic_to_square(user_input[:2])
    to_square = algebraic_to_square(user_input[2:])
    if from_square is None or to_square is None:
        return None
    piece = board.get_piece_at_square(from_square)
    if piece is None or not piece.isupper():
        return None
    move = Move(piece, from_square, to_square)
    legal_moves = board.generate_legal_moves()
    if move in legal_moves:
        return move
    return None
