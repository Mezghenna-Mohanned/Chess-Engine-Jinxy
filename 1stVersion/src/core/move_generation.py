from src.core.constants import KNIGHT_MOVES, KING_MOVES , FILE_A , FILE_H
from collections import namedtuple
from src.core.board import Move

Move = namedtuple('Move', ['piece', 'from_square', 'to_square', 'promotion'])

def generate_legal_moves(board):
    moves = []
    if board.white_to_move:
        own_pieces = board.occupied_white
        enemy_pieces = board.occupied_black
        is_white = True
    else:
        own_pieces = board.occupied_black
        enemy_pieces = board.occupied_white
        is_white = False

    moves.extend(generate_all_pawn_moves(board, own_pieces, enemy_pieces, is_white))
    moves.extend(generate_all_knight_moves(board, own_pieces, is_white))
    moves.extend(generate_all_bishop_moves(board, own_pieces, is_white))
    moves.extend(generate_all_rook_moves(board, own_pieces, is_white))
    moves.extend(generate_all_queen_moves(board, own_pieces, is_white))
    moves.extend(generate_all_king_moves(board, own_pieces, is_white))

    return moves

def generate_all_pawn_moves(board, own_pieces, enemy_pieces, is_white):
    moves = []
    pawn_piece = 'P' if is_white else 'p'
    direction = 8 if is_white else -8
    start_rank = 1 if is_white else 6
    promotion_rank = 7 if is_white else 0
    pawn_bitboard = board.bitboards.get(pawn_piece, 0)
    empty_squares = ~(board.occupied_white | board.occupied_black)

    # Single moves
    if is_white:
        single_moves = (pawn_bitboard << 8) & empty_squares
    else:
        single_moves = (pawn_bitboard >> 8) & empty_squares

    # Promotions
    promotion_moves = single_moves & (0xFF << (promotion_rank * 8))
    single_moves ^= promotion_moves

    # Add single pawn moves
    while single_moves:
        to_square = (single_moves & -single_moves).bit_length() - 1
        from_square = to_square - direction
        moves.append(Move(pawn_piece, from_square, to_square, None))
        single_moves &= single_moves - 1

    # Add promotions
    while promotion_moves:
        to_square = (promotion_moves & -promotion_moves).bit_length() - 1
        from_square = to_square - direction
        for promotion_piece in ['Q', 'R', 'B', 'N']:
            prom_piece = promotion_piece if is_white else promotion_piece.lower()
            moves.append(Move(pawn_piece, from_square, to_square, prom_piece))
        promotion_moves &= promotion_moves - 1

    # Double moves
    if is_white:
        double_moves = ((pawn_bitboard & (0xFF << (start_rank * 8))) << 16) & empty_squares & (empty_squares << 8)
    else:
        double_moves = ((pawn_bitboard & (0xFF << (start_rank * 8))) >> 16) & empty_squares & (empty_squares >> 8)

    while double_moves:
        to_square = (double_moves & -double_moves).bit_length() - 1
        from_square = to_square - 2 * direction
        moves.append(Move(pawn_piece, from_square, to_square, None))
        double_moves &= double_moves - 1

    # Captures
    if is_white:
        left_captures = (pawn_bitboard << 7) & enemy_pieces & ~FILE_H
        right_captures = (pawn_bitboard << 9) & enemy_pieces & ~FILE_A
    else:
        left_captures = (pawn_bitboard >> 9) & enemy_pieces & ~FILE_H
        right_captures = (pawn_bitboard >> 7) & enemy_pieces & ~FILE_A

    capture_moves = left_captures | right_captures
    promotion_captures = capture_moves & (0xFF << (promotion_rank * 8))
    capture_moves ^= promotion_captures

    while capture_moves:
        to_square = (capture_moves & -capture_moves).bit_length() - 1
        from_square = to_square - (direction - 1) if (left_captures & (1 << to_square)) else to_square - (direction + 1)
        moves.append(Move(pawn_piece, from_square, to_square, None))
        capture_moves &= capture_moves - 1

    while promotion_captures:
        to_square = (promotion_captures & -promotion_captures).bit_length() - 1
        from_square = to_square - (direction - 1) if (left_captures & (1 << to_square)) else to_square - (direction + 1)
        for promotion_piece in ['Q', 'R', 'B', 'N']:
            prom_piece = promotion_piece if is_white else promotion_piece.lower()
            moves.append(Move(pawn_piece, from_square, to_square, prom_piece))
        promotion_captures &= promotion_captures - 1

    # En passant captures
    if board.en_passant_target is not None:
        ep_square = board.en_passant_target
        if is_white:
            ep_pawns = pawn_bitboard & ((1 << (ep_square - 9)) | (1 << (ep_square - 7)))
        else:
            ep_pawns = pawn_bitboard & ((1 << (ep_square + 7)) | (1 << (ep_square + 9)))
        while ep_pawns:
            from_square = (ep_pawns & -ep_pawns).bit_length() - 1
            moves.append(Move(pawn_piece, from_square, ep_square, None))
            ep_pawns &= ep_pawns - 1

    return moves

def generate_all_knight_moves(board, own_pieces, is_white):
    moves = []
    knight_piece = 'N' if is_white else 'n'
    knight_bitboard = board.bitboards.get(knight_piece, 0)
    enemy_pieces = board.occupied_black if is_white else board.occupied_white
    empty_squares = ~(board.occupied_white | board.occupied_black)

    while knight_bitboard:
        from_square = (knight_bitboard & -knight_bitboard).bit_length() - 1
        knight_attacks = KNIGHT_MOVES[from_square] & ~own_pieces
        while knight_attacks:
            to_square = (knight_attacks & -knight_attacks).bit_length() - 1
            moves.append(Move(knight_piece, from_square, to_square, None))
            knight_attacks &= knight_attacks - 1
        knight_bitboard &= knight_bitboard - 1
    return moves

def generate_all_bishop_moves(board, own_pieces, is_white):
    moves = []
    bishop_piece = 'B' if is_white else 'b'
    bishop_bitboard = board.bitboards.get(bishop_piece, 0)
    while bishop_bitboard:
        from_square = (bishop_bitboard & -bishop_bitboard).bit_length() - 1
        attacks = generate_sliding_attacks(from_square, board.occupied, 'bishop') & ~own_pieces
        while attacks:
            to_square = (attacks & -attacks).bit_length() - 1
            moves.append(Move(bishop_piece, from_square, to_square, None))
            attacks &= attacks - 1
        bishop_bitboard &= bishop_bitboard - 1
    return moves

def generate_all_rook_moves(board, own_pieces, is_white):
    moves = []
    rook_piece = 'R' if is_white else 'r'
    rook_bitboard = board.bitboards.get(rook_piece, 0)
    while rook_bitboard:
        from_square = (rook_bitboard & -rook_bitboard).bit_length() - 1
        attacks = generate_sliding_attacks(from_square, board.occupied, 'rook') & ~own_pieces
        while attacks:
            to_square = (attacks & -attacks).bit_length() - 1
            moves.append(Move(rook_piece, from_square, to_square, None))
            attacks &= attacks - 1
        rook_bitboard &= rook_bitboard - 1
    return moves

def generate_all_queen_moves(board, own_pieces, is_white):
    moves = []
    queen_piece = 'Q' if is_white else 'q'
    queen_bitboard = board.bitboards.get(queen_piece, 0)
    while queen_bitboard:
        from_square = (queen_bitboard & -queen_bitboard).bit_length() - 1
        attacks = generate_sliding_attacks(from_square, board.occupied, 'queen') & ~own_pieces
        while attacks:
            to_square = (attacks & -attacks).bit_length() - 1
            moves.append(Move(queen_piece, from_square, to_square, None))
            attacks &= attacks - 1
        queen_bitboard &= queen_bitboard - 1
    return moves

def generate_all_king_moves(board, own_pieces, is_white):
    moves = []
    king_piece = 'K' if is_white else 'k'
    king_bitboard = board.bitboards.get(king_piece, 0)
    enemy_attacks = board.get_all_enemy_attacks(not is_white)
    while king_bitboard:
        from_square = (king_bitboard & -king_bitboard).bit_length() - 1
        king_attacks = KING_MOVES[from_square] & ~own_pieces & ~enemy_attacks
        while king_attacks:
            to_square = (king_attacks & -king_attacks).bit_length() - 1
            moves.append(Move(king_piece, from_square, to_square))
            king_attacks &= king_attacks - 1
        king_bitboard &= king_bitboard - 1

    # Castling moves
    if is_white:
        if board.can_castle_kingside_white():
            moves.append(Move('K', 4, 6, is_castling=True))
        if board.can_castle_queenside_white():
            moves.append(Move('K', 4, 2, is_castling=True))
    else:
        if board.can_castle_kingside_black():
            moves.append(Move('k', 60, 62, is_castling=True))
        if board.can_castle_queenside_black():
            moves.append(Move('k', 60, 58, is_castling=True))
    return moves


def get_all_enemy_attacks(self, by_white):
    attacks = 0
    enemy_pieces = 'PNBRQK' if by_white else 'pnbrqk'
    for piece in enemy_pieces:
        bitboard = self.bitboards.get(piece, 0)
        while bitboard:
            from_square = (bitboard & -bitboard).bit_length() - 1
            piece_attacks = self.generate_piece_moves(piece, from_square, attacks_only=True)
            for move in piece_attacks:
                attacks |= (1 << move.to_square)
            bitboard &= bitboard - 1
    return attacks


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

