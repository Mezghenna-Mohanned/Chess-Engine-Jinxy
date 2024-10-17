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

def generate_pawn_moves(self, piece, from_square, attacks_only=False):
    moves = []
    direction = 8 if piece.isupper() else -8
    start_rank = 1 if piece.isupper() else 6
    enemy_pieces = self.occupied_black if piece.isupper() else self.occupied_white
    own_pieces = self.occupied_white if piece.isupper() else self.occupied_black
    promotion_rank = 7 if piece.isupper() else 0

    for capture_direction in [-1, 1]:
        to_square = from_square + direction + capture_direction
        if 0 <= to_square < 64 and abs((from_square % 8) - (to_square % 8)) == 1:
            if (enemy_pieces & (1 << to_square)) or (self.en_passant_target == to_square):
                captured_piece = self.get_piece_at_square(to_square) if (enemy_pieces & (1 << to_square)) else ('p' if piece.isupper() else 'P')
                if to_square // 8 == promotion_rank:
                    for promotion_piece in ['Q', 'R', 'B', 'N']:
                        prom_piece = promotion_piece if piece.isupper() else promotion_piece.lower()
                        moves.append(Move(piece, from_square, to_square, captured_piece, promoted_piece=prom_piece))
                else:
                    moves.append(Move(piece, from_square, to_square, captured_piece))
            elif attacks_only:
                moves.append(Move(piece, from_square, to_square))

    if attacks_only:
        return moves

    to_square = from_square + direction
    if 0 <= to_square < 64 and not (self.occupied & (1 << to_square)):
        if to_square // 8 == promotion_rank:
            for promotion_piece in ['Q', 'R', 'B', 'N']:
                prom_piece = promotion_piece if piece.isupper() else promotion_piece.lower()
                moves.append(Move(piece, from_square, to_square, promoted_piece=prom_piece))
        else:
            moves.append(Move(piece, from_square, to_square))
        if from_square // 8 == start_rank:
            to_square2 = from_square + 2 * direction
            if not (self.occupied & (1 << to_square2)):
                moves.append(Move(piece, from_square, to_square2))

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
