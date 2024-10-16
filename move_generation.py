from constants import (
    FILE_A, FILE_H, RANK_1, RANK_4, RANK_5, RANK_8,
    KNIGHT_MOVES, KING_MOVES, RANK_MASKS, FILE_MASKS
)

def generate_legal_moves(board):
    moves = []
    if board.white_to_move:
        own_pieces = board.occupied_white
        enemy_pieces = board.occupied_black
        pawn_piece = 'P'
        pieces = 'PNBRQK'
    else:
        own_pieces = board.occupied_black
        enemy_pieces = board.occupied_white
        pawn_piece = 'p'
        pieces = 'pnbrqk'

    pawn_moves = generate_pawn_moves(board, pawn_piece)
    moves.extend(pawn_moves)

    for piece in pieces:
        if piece.upper() != 'P':
            bitboard = board.bitboards.get(piece, 0)
            while bitboard:
                from_square = (bitboard & -bitboard).bit_length() - 1
                piece_moves = generate_piece_moves(board, piece, from_square)
                moves.extend(piece_moves)
                bitboard &= bitboard - 1
    return moves

def generate_piece_moves(board, piece, from_square):
    if piece.upper() == 'N':
        return generate_knight_moves(board, piece, from_square)
    elif piece.upper() == 'B':
        return generate_bishop_moves(board, piece, from_square)
    elif piece.upper() == 'R':
        return generate_rook_moves(board, piece, from_square)
    elif piece.upper() == 'Q':
        return generate_queen_moves(board, piece, from_square)
    elif piece.upper() == 'K':
        return generate_king_moves(board, piece, from_square)
    else:
        return []

def generate_pawn_moves(board, pawn_piece):
    moves = []
    is_white = pawn_piece.isupper()
    pawns = board.bitboards.get(pawn_piece, 0)
    empty_squares = ~board.occupied & 0xFFFFFFFFFFFFFFFF

    if is_white:
        one_step = (pawns << 8) & empty_squares
        promotion_moves = one_step & RANK_MASKS[7]
        one_step &= ~RANK_MASKS[7]
        two_step = ((pawns & RANK_MASKS[1]) << 16) & empty_squares & (empty_squares << 8)
        captures_left = (pawns << 7) & board.occupied_black & ~FILE_MASKS[7]
        captures_right = (pawns << 9) & board.occupied_black & ~FILE_MASKS[0]
        en_passant_left = (pawns << 7) & (1 << board.en_passant_target) if board.en_passant_target else 0
        en_passant_right = (pawns << 9) & (1 << board.en_passant_target) if board.en_passant_target else 0
    else:
        one_step = (pawns >> 8) & empty_squares
        promotion_moves = one_step & RANK_MASKS[0]
        one_step &= ~RANK_MASKS[0]
        two_step = ((pawns & RANK_MASKS[6]) >> 16) & empty_squares & (empty_squares >> 8)
        captures_left = (pawns >> 9) & board.occupied_white & ~FILE_MASKS[0]
        captures_right = (pawns >> 7) & board.occupied_white & ~FILE_MASKS[7]
        en_passant_left = (pawns >> 9) & (1 << board.en_passant_target) if board.en_passant_target else 0
        en_passant_right = (pawns >> 7) & (1 << board.en_passant_target) if board.en_passant_target else 0

    moves.extend(create_pawn_moves(pawn_piece, one_step, 8, is_double=False, promotion=False))
    moves.extend(create_pawn_moves(pawn_piece, two_step, 16, is_double=True, promotion=False))
    moves.extend(create_pawn_captures(pawn_piece, captures_left, 7, promotion=False))
    moves.extend(create_pawn_captures(pawn_piece, captures_right, 9, promotion=False))
    moves.extend(create_pawn_moves(pawn_piece, promotion_moves, 8, is_double=False, promotion=True))
    moves.extend(create_pawn_captures(pawn_piece, captures_left & RANK_MASKS[7 if is_white else 0], 7, promotion=True))
    moves.extend(create_pawn_captures(pawn_piece, captures_right & RANK_MASKS[7 if is_white else 0], 9, promotion=True))
    moves.extend(create_pawn_captures(pawn_piece, en_passant_left, 7, en_passant=True))
    moves.extend(create_pawn_captures(pawn_piece, en_passant_right, 9, en_passant=True))

    return moves

def create_pawn_moves(pawn_piece, bitboard, shift, is_double=False, promotion=False):
    moves = []
    is_white = pawn_piece.isupper()
    while bitboard:
        to_square = (bitboard & -bitboard).bit_length() - 1
        from_square = to_square - shift if is_white else to_square + shift
        if promotion:
            for promotion_piece in ['Q', 'R', 'B', 'N']:
                prom_piece = promotion_piece if is_white else promotion_piece.lower()
                moves.append(Move(pawn_piece, from_square, to_square, promotion=prom_piece))
        else:
            moves.append(Move(pawn_piece, from_square, to_square))
        bitboard &= bitboard - 1
    return moves

def create_pawn_captures(pawn_piece, bitboard, shift, promotion=False, en_passant=False):
    moves = []
    is_white = pawn_piece.isupper()
    while bitboard:
        to_square = (bitboard & -bitboard).bit_length() - 1
        from_square = to_square - shift if is_white else to_square + shift
        if promotion:
            for promotion_piece in ['Q', 'R', 'B', 'N']:
                prom_piece = promotion_piece if is_white else promotion_piece.lower()
                moves.append(Move(pawn_piece, from_square, to_square, promotion=prom_piece))
        elif en_passant:
            moves.append(Move(pawn_piece, from_square, to_square))
        else:
            moves.append(Move(pawn_piece, from_square, to_square))
        bitboard &= bitboard - 1
    return moves

def generate_knight_moves(board, piece, from_square):
    moves = []
    own_pieces = board.occupied_white if piece.isupper() else board.occupied_black
    knight_attacks = KNIGHT_MOVES[from_square] & ~own_pieces
    while knight_attacks:
        to_square = (knight_attacks & -knight_attacks).bit_length() - 1
        moves.append(Move(piece, from_square, to_square))
        knight_attacks &= knight_attacks - 1
    return moves

def generate_bishop_moves(board, piece, from_square):
    moves = []
    own_pieces = board.occupied_white if piece.isupper() else board.occupied_black
    attacks = generate_sliding_attacks(from_square, board.occupied, 'bishop') & ~own_pieces
    while attacks:
        to_square = (attacks & -attacks).bit_length() - 1
        moves.append(Move(piece, from_square, to_square))
        attacks &= attacks - 1
    return moves

def generate_rook_moves(board, piece, from_square):
    moves = []
    own_pieces = board.occupied_white if piece.isupper() else board.occupied_black
    attacks = generate_sliding_attacks(from_square, board.occupied, 'rook') & ~own_pieces
    while attacks:
        to_square = (attacks & -attacks).bit_length() - 1
        moves.append(Move(piece, from_square, to_square))
        attacks &= attacks - 1
    return moves

def generate_queen_moves(board, piece, from_square):
    moves = []
    own_pieces = board.occupied_white if piece.isupper() else board.occupied_black
    attacks = generate_sliding_attacks(from_square, board.occupied, 'queen') & ~own_pieces
    while attacks:
        to_square = (attacks & -attacks).bit_length() - 1
        moves.append(Move(piece, from_square, to_square))
        attacks &= attacks - 1
    return moves

def generate_king_moves(board, piece, from_square):
    moves = []
    own_pieces = board.occupied_white if piece.isupper() else board.occupied_black
    king_attacks = KING_MOVES[from_square] & ~own_pieces
    while king_attacks:
        to_square = (king_attacks & -king_attacks).bit_length() - 1
        moves.append(Move(piece, from_square, to_square))
        king_attacks &= king_attacks - 1
    return moves

def generate_sliding_attacks(square, occupied, piece_type):
    attacks = 0
    for direction in SLIDING_DIRECTIONS[piece_type]:
        sq = square
        while True:
            sq = SQUARES[sq]['neighbors'].get(direction)
            if sq is None:
                break
            attacks |= 1 << sq
            if occupied & (1 << sq):
                break
    return attacks

SQUARES = [{'neighbors': {}} for _ in range(64)]
DIRECTIONS = ['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW']
SLIDING_DIRECTIONS = {
    'rook': ['N', 'S', 'E', 'W'],
    'bishop': ['NE', 'NW', 'SE', 'SW'],
    'queen': DIRECTIONS
}

def initialize_squares():
    for square in range(64):
        rank = square // 8
        file = square % 8
        neighbors = {}
        if rank < 7:
            neighbors['N'] = square + 8
        if rank > 0:
            neighbors['S'] = square - 8
        if file < 7:
            neighbors['E'] = square + 1
        if file > 0:
            neighbors['W'] = square - 1
        if rank < 7 and file < 7:
            neighbors['NE'] = square + 9
        if rank < 7 and file > 0:
            neighbors['NW'] = square + 7
        if rank > 0 and file < 7:
            neighbors['SE'] = square - 7
        if rank > 0 and file > 0:
            neighbors['SW'] = square - 9
        SQUARES[square]['neighbors'] = neighbors

initialize_squares()

KNIGHT_MOVES = [0] * 64
KING_MOVES = [0] * 64

for square in range(64):
    rank = square // 8
    file = square % 8
    knight_offsets = [
        (2, 1), (1, 2), (-1, 2), (-2, 1),
        (-2, -1), (-1, -2), (1, -2), (2, -1)
    ]
    king_offsets = [
        (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]
    for dr, df in knight_offsets:
        r = rank + dr
        f = file + df
        if 0 <= r < 8 and 0 <= f < 8:
            KNIGHT_MOVES[square] |= 1 << (r * 8 + f)
    for dr, df in king_offsets:
        r = rank + dr
        f = file + df
        if 0 <= r < 8 and 0 <= f < 8:
            KING_MOVES[square] |= 1 << (r * 8 + f)

class Move:
    def __init__(self, piece, from_square, to_square, promotion=None):
        self.piece = piece
        self.from_square = from_square
        self.to_square = to_square
        self.promotion = promotion

    def __eq__(self, other):
        return (self.piece == other.piece and
                self.from_square == other.from_square and
                self.to_square == other.to_square and
                self.promotion == other.promotion)

    def __hash__(self):
        return hash((self.piece, self.from_square, self.to_square, self.promotion))

    def __repr__(self):
        move_str = f"{self.piece}{square_to_algebraic(self.from_square)}{square_to_algebraic(self.to_square)}"
        if self.promotion:
            move_str += f"={self.promotion}"
        return move_str

def square_to_algebraic(square):
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    rank = square // 8
    file = square % 8
    return f"{files[file]}{rank + 1}"
