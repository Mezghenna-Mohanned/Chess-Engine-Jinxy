from constants import PIECE_VALUES, POSITIONAL_VALUES

def evaluate(board):
    score = 0
    for piece, bitboard in board.bitboards.items():
        piece_value = PIECE_VALUES[piece]
        while bitboard:
            square = bitboard.bit_length() - 1
            positional_value = 0
            if piece.upper() in POSITIONAL_VALUES:
                positional_value = POSITIONAL_VALUES[piece.upper()][square]
                if piece.islower():
                    positional_value = -positional_value
            score += piece_value + positional_value
            bitboard &= bitboard - 1
    return score
