from constants import FILE_MASKS, RANK_MASKS

def generate_legal_moves(board):
    moves = []
    if board.white_to_move:
        for piece in 'PNBRQK':
            bitboard = board.bitboards[piece]
            while bitboard:
                from_square = (bitboard & -bitboard).bit_length() - 1
                moves.extend(generate_piece_moves(board, piece, from_square))
                bitboard &= bitboard - 1
    else:
        for piece in 'pnbrqk':
            bitboard = board.bitboards[piece]
            while bitboard:
                from_square = (bitboard & -bitboard).bit_length() - 1
                moves.extend(generate_piece_moves(board, piece, from_square))
                bitboard &= bitboard - 1
    return moves

def generate_piece_moves(board, piece, from_square, attacks_only=False):
    moves = []
    if piece.upper() == 'P':
        moves.extend(generate_pawn_moves(board, piece, from_square, attacks_only))
    elif piece.upper() == 'N':
        moves.extend(generate_knight_moves(board, piece, from_square, attacks_only))
    elif piece.upper() == 'B':
        moves.extend(generate_bishop_moves(board, piece, from_square, attacks_only))
    elif piece.upper() == 'R':
        moves.extend(generate_rook_moves(board, piece, from_square, attacks_only))
    elif piece.upper() == 'Q':
        moves.extend(generate_queen_moves(board, piece, from_square, attacks_only))
    elif piece.upper() == 'K':
        moves.extend(generate_king_moves(board, piece, from_square, attacks_only))
    return moves

def generate_pawn_moves(board, piece, from_square, attacks_only=False):
    moves = []
    direction = 8 if piece.isupper() else -8
    start_rank = 1 if piece.isupper() else 6
    enemy_pieces = board.occupied_black if piece.isupper() else board.occupied_white
    own_pieces = board.occupied_white if piece.isupper() else board.occupied_black
    promotion_rank = 7 if piece.isupper() else 0


    for capture_direction in [-1, 1]:
        to_square = from_square + direction + capture_direction
        if 0 <= to_square < 64 and abs((from_square % 8) - (to_square % 8)) == 1:
            if (enemy_pieces & (1 << to_square)) or (attacks_only and not (board.occupied & (1 << to_square))):
                if to_square // 8 == promotion_rank:
                    for promotion_piece in ['Q', 'R', 'B', 'N']:
                        prom_piece = promotion_piece if piece.isupper() else promotion_piece.lower()
                        moves.append(Move(piece, from_square, to_square, promotion=prom_piece))
                else:
                    moves.append(Move(piece, from_square, to_square))
            if board.en_passant_target == to_square:
                moves.append(Move(piece, from_square, to_square))

    if attacks_only:
        return moves

    to_square = from_square + direction
    if 0 <= to_square < 64 and not (board.occupied & (1 << to_square)):
        if to_square // 8 == promotion_rank:
            for promotion_piece in ['Q', 'R', 'B', 'N']:
                prom_piece = promotion_piece if piece.isupper() else promotion_piece.lower()
                moves.append(Move(piece, from_square, to_square, promotion=prom_piece))
        else:
            moves.append(Move(piece, from_square, to_square))
        if from_square // 8 == start_rank:
            to_square2 = from_square + 2 * direction
            if not (board.occupied & (1 << to_square2)) and not (board.occupied & (1 << to_square)):
                moves.append(Move(piece, from_square, to_square2))

    return moves

def generate_knight_moves(board, piece, from_square, attacks_only=False):
    moves = []
    knight_moves = [17, 15, 10, 6, -6, -10, -15, -17]
    own_pieces = board.occupied_white if piece.isupper() else board.occupied_black

    for move in knight_moves:
        to_square = from_square + move
        if 0 <= to_square < 64:
            if abs((from_square % 8) - (to_square % 8)) in [1, 2]:
                if not (own_pieces & (1 << to_square)):
                    moves.append(Move(piece, from_square, to_square))
    return moves

def generate_bishop_moves(board, piece, from_square, attacks_only=False):
    moves = []
    own_pieces = board.occupied_white if piece.isupper() else board.occupied_black
    enemy_pieces = board.occupied_black if piece.isupper() else board.occupied_white

    directions = [9, 7, -7, -9]
    for direction in directions:
        to_square = from_square
        while True:
            to_square += direction
            if 0 <= to_square < 64 and abs((from_square % 8) - (to_square % 8)) == abs((from_square // 8) - (to_square // 8)):
                if own_pieces & (1 << to_square):
                    if attacks_only:
                        moves.append(Move(piece, from_square, to_square))
                    break
                moves.append(Move(piece, from_square, to_square))
                if board.occupied & (1 << to_square):
                    break
            else:
                break
    return moves

def generate_rook_moves(board, piece, from_square, attacks_only=False):
    moves = []
    own_pieces = board.occupied_white if piece.isupper() else board.occupied_black
    enemy_pieces = board.occupied_black if piece.isupper() else board.occupied_white

    directions = [8, -8, 1, -1]
    for direction in directions:
        to_square = from_square
        while True:
            to_square += direction
            if 0 <= to_square < 64:
                if direction in [1, -1] and (from_square // 8 != to_square // 8):
                    break
                if own_pieces & (1 << to_square):
                    if attacks_only:
                        moves.append(Move(piece, from_square, to_square))
                    break
                moves.append(Move(piece, from_square, to_square))
                if board.occupied & (1 << to_square):
                    break
            else:
                break
    return moves

def generate_queen_moves(board, piece, from_square, attacks_only=False):
    moves = []
    # Queen moves are a combination of rook and bishop moves
    moves.extend(generate_bishop_moves(board, piece, from_square, attacks_only))
    moves.extend(generate_rook_moves(board, piece, from_square, attacks_only))
    return moves

def generate_king_moves(board, piece, from_square, attacks_only=False):
    moves = []
    king_moves = [8, -8, 1, -1, 9, -9, 7, -7]
    own_pieces = board.occupied_white if piece.isupper() else board.occupied_black

    for move in king_moves:
        to_square = from_square + move
        if 0 <= to_square < 64:
            if abs((from_square % 8) - (to_square % 8)) <= 1:
                if not (own_pieces & (1 << to_square)):
                    moves.append(Move(piece, from_square, to_square))
    return moves

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
