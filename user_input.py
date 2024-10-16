from move_generation import Move, generate_legal_moves

def get_user_move(board, user_input):
    if len(user_input) != 4:
        return None
    from_square = algebraic_to_square(user_input[:2])
    to_square = algebraic_to_square(user_input[2:])
    if from_square is None or to_square is None:
        return None
    piece = board.get_piece_at_square(from_square)
    if piece is None or piece.islower():
        return None
    move = Move(piece, from_square, to_square)
    legal_moves = generate_legal_moves(board)
    if move in legal_moves:
        return move
    return None

def algebraic_to_square(algebraic):
    files = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
             'e': 4, 'f': 5, 'g': 6, 'h': 7}
    ranks = {'1': 0, '2': 1, '3': 2, '4': 3,
             '5': 4, '6': 5, '7': 6, '8': 7}
    if len(algebraic) != 2:
        return None
    file = files.get(algebraic[0].lower())
    rank = ranks.get(algebraic[1])
    if file is None or rank is None:
        return None
    return rank * 8 + file
