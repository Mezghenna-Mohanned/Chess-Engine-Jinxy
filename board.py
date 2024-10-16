from constants import INITIAL_POSITIONS
from evaluation import evaluate

class Board:
    def __init__(self):
        self.bitboards = INITIAL_POSITIONS.copy()
        self.white_to_move = True
        self.castling_rights = {'K': True, 'Q': True, 'k': True, 'q': True}
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.move_history = []
        self.update_occupied()

    def update_occupied(self):
        self.occupied_white = 0
        self.occupied_black = 0
        for piece, bitboard in self.bitboards.items():
            if piece.isupper():
                self.occupied_white |= bitboard
            else:
                self.occupied_black |= bitboard
        self.occupied = self.occupied_white | self.occupied_black

    def make_move(self, move):
        state = {
            'bitboards': self.bitboards.copy(),
            'white_to_move': self.white_to_move,
            'castling_rights': self.castling_rights.copy(),
            'en_passant_target': self.en_passant_target,
            'halfmove_clock': self.halfmove_clock,
            'fullmove_number': self.fullmove_number,
        }
        self.move_history.append(state)

        piece = move.piece
        from_square = move.from_square
        to_square = move.to_square
        promotion = move.promotion

        self.en_passant_target = None

        if piece.upper() == 'P' or self.is_square_occupied_by_opponent(to_square):
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        self.bitboards[piece] &= ~(1 << from_square)

        captured_piece = None
        for p, bb in self.bitboards.items():
            if bb & (1 << to_square):
                self.bitboards[p] &= ~(1 << to_square)
                captured_piece = p
                break

        if piece.upper() == 'P':
            if to_square == self.en_passant_target:
                ep_capture_square = to_square + (-8 if piece.isupper() else 8)
                for p, bb in self.bitboards.items():
                    if bb & (1 << ep_capture_square):
                        self.bitboards[p] &= ~(1 << ep_capture_square)
                        captured_piece = p
                        break

        if promotion:
            promoted_piece = promotion
            self.bitboards[promoted_piece] |= (1 << to_square)
        else:
            self.bitboards[piece] |= (1 << to_square)

        if piece.upper() == 'P' and abs(to_square - from_square) == 16:
            self.en_passant_target = from_square + (8 if piece.isupper() else -8)

        self.update_castling_rights(piece, from_square, to_square)

        if not self.white_to_move:
            self.fullmove_number += 1

        self.white_to_move = not self.white_to_move

        self.update_occupied()

    def undo_move(self, move):
        if not self.move_history:
            return

        state = self.move_history.pop()
        self.bitboards = state['bitboards']
        self.white_to_move = state['white_to_move']
        self.castling_rights = state['castling_rights']
        self.en_passant_target = state['en_passant_target']
        self.halfmove_clock = state['halfmove_clock']
        self.fullmove_number = state['fullmove_number']

        self.update_occupied()

    def update_castling_rights(self, piece, from_square, to_square):
        if piece == 'K':
            self.castling_rights['K'] = False
            self.castling_rights['Q'] = False
        elif piece == 'k':
            self.castling_rights['k'] = False
            self.castling_rights['q'] = False
        elif piece == 'R':
            if from_square == 0:
                self.castling_rights['Q'] = False
            elif from_square == 7:
                self.castling_rights['K'] = False
        elif piece == 'r':
            if from_square == 56:
                self.castling_rights['q'] = False
            elif from_square == 63:
                self.castling_rights['k'] = False

        if self.is_square_occupied_by_opponent(to_square):
            if to_square == 0:
                self.castling_rights['Q'] = False
            elif to_square == 7:
                self.castling_rights['K'] = False
            elif to_square == 56:
                self.castling_rights['q'] = False
            elif to_square == 63:
                self.castling_rights['k'] = False

    def is_square_occupied_by_opponent(self, square):
        if self.white_to_move:
            return bool(self.occupied_black & (1 << square))
        else:
            return bool(self.occupied_white & (1 << square))

    def is_game_over(self):
        if self.is_checkmate():
            return True
        if self.is_stalemate():
            return True
        return False

    def is_checkmate(self):
        if not self.is_in_check():
            return False
        legal_moves = self.generate_legal_moves()
        return len(legal_moves) == 0

    def is_stalemate(self):
        if self.is_in_check():
            return False
        legal_moves = self.generate_legal_moves()
        return len(legal_moves) == 0

    def is_in_check(self):
        king_square = self.find_king_square(self.white_to_move)
        if king_square is None:
            return False
        return self.is_square_attacked(king_square, not self.white_to_move)

    def find_king_square(self, white):
        king_piece = 'K' if white else 'k'
        king_bitboard = self.bitboards.get(king_piece, 0)
        if king_bitboard:
            return (king_bitboard & -king_bitboard).bit_length() - 1
        return None

    def is_square_attacked(self, square, by_white):
        attacking_moves = []
        if by_white:
            for piece in 'PNBRQK':
                bitboard = self.bitboards.get(piece, 0)
                while bitboard:
                    from_square = (bitboard & -bitboard).bit_length() - 1
                    moves = self.generate_piece_moves(piece, from_square, attacks_only=True)
                    attacking_moves.extend(moves)
                    bitboard &= bitboard - 1
        else:
            for piece in 'pnbrqk':
                bitboard = self.bitboards.get(piece, 0)
                while bitboard:
                    from_square = (bitboard & -bitboard).bit_length() - 1
                    moves = self.generate_piece_moves(piece, from_square, attacks_only=True)
                    attacking_moves.extend(moves)
                    bitboard &= bitboard - 1
        for move in attacking_moves:
            if move.to_square == square:
                return True
        return False

    def generate_piece_moves(self, piece, from_square, attacks_only=False):
        moves = []
        if piece.upper() == 'P':
            moves.extend(self._generate_pawn_moves(piece, from_square, attacks_only))
        elif piece.upper() == 'N':
            moves.extend(self._generate_knight_moves(piece, from_square, attacks_only))
        elif piece.upper() == 'B':
            moves.extend(self._generate_bishop_moves(piece, from_square, attacks_only))
        elif piece.upper() == 'R':
            moves.extend(self._generate_rook_moves(piece, from_square, attacks_only))
        elif piece.upper() == 'Q':
            moves.extend(self._generate_queen_moves(piece, from_square, attacks_only))
        elif piece.upper() == 'K':
            moves.extend(self._generate_king_moves(piece, from_square, attacks_only))
        return moves

    def generate_legal_moves(self):
        legal_moves = []
        all_moves = []
        if self.white_to_move:
            for piece in 'PNBRQK':
                bitboard = self.bitboards.get(piece, 0)
                while bitboard:
                    from_square = (bitboard & -bitboard).bit_length() - 1
                    moves = self.generate_piece_moves(piece, from_square)
                    all_moves.extend(moves)
                    bitboard &= bitboard - 1
        else:
            for piece in 'pnbrqk':
                bitboard = self.bitboards.get(piece, 0)
                while bitboard:
                    from_square = (bitboard & -bitboard).bit_length() - 1
                    moves = self.generate_piece_moves(piece, from_square)
                    all_moves.extend(moves)
                    bitboard &= bitboard - 1

        for move in all_moves:
            self.make_move(move)
            if not self.is_in_check():
                legal_moves.append(move)
            self.undo_move(move)

        return legal_moves

    def _generate_pawn_moves(self, piece, from_square, attacks_only=False):
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
                    if to_square // 8 == promotion_rank:
                        for promotion_piece in ['Q', 'R', 'B', 'N']:
                            prom_piece = promotion_piece if piece.isupper() else promotion_piece.lower()
                            moves.append(Move(piece, from_square, to_square, promotion=prom_piece))
                    else:
                        moves.append(Move(piece, from_square, to_square))
                elif attacks_only:
                    moves.append(Move(piece, from_square, to_square))

        if attacks_only:
            return moves

        to_square = from_square + direction
        if 0 <= to_square < 64 and not (self.occupied & (1 << to_square)):
            if to_square // 8 == promotion_rank:
                for promotion_piece in ['Q', 'R', 'B', 'N']:
                    prom_piece = promotion_piece if piece.isupper() else promotion_piece.lower()
                    moves.append(Move(piece, from_square, to_square, promotion=prom_piece))
            else:
                moves.append(Move(piece, from_square, to_square))
            if from_square // 8 == start_rank:
                to_square2 = from_square + 2 * direction
                if not (self.occupied & (1 << to_square2)) and not (self.occupied & (1 << to_square)):
                    moves.append(Move(piece, from_square, to_square2))

        return moves

    def _generate_knight_moves(self, piece, from_square, attacks_only=False):
        moves = []
        knight_moves = [17, 15, 10, 6, -6, -10, -15, -17]
        own_pieces = self.occupied_white if piece.isupper() else self.occupied_black

        for move_offset in knight_moves:
            to_square = from_square + move_offset
            if 0 <= to_square < 64:
                if abs((from_square % 8) - (to_square % 8)) in [1, 2]:
                    if not (own_pieces & (1 << to_square)):
                        moves.append(Move(piece, from_square, to_square))
        return moves

    def _generate_bishop_moves(self, piece, from_square, attacks_only=False):
        moves = []
        own_pieces = self.occupied_white if piece.isupper() else self.occupied_black
        directions = [9, 7, -7, -9]

        for direction in directions:
            to_square = from_square
            while True:
                to_square += direction
                if 0 <= to_square < 64 and abs((to_square % 8) - (from_square % 8)) == abs((to_square // 8) - (from_square // 8)):
                    if own_pieces & (1 << to_square):
                        if attacks_only:
                            moves.append(Move(piece, from_square, to_square))
                        break
                    moves.append(Move(piece, from_square, to_square))
                    if self.occupied & (1 << to_square):
                        break
                else:
                    break
        return moves

    def _generate_rook_moves(self, piece, from_square, attacks_only=False):
        moves = []
        own_pieces = self.occupied_white if piece.isupper() else self.occupied_black
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
                    if self.occupied & (1 << to_square):
                        break
                else:
                    break
        return moves

    def _generate_queen_moves(self, piece, from_square, attacks_only=False):
        moves = []
        moves.extend(self._generate_bishop_moves(piece, from_square, attacks_only))
        moves.extend(self._generate_rook_moves(piece, from_square, attacks_only))
        return moves

    def _generate_king_moves(self, piece, from_square, attacks_only=False):
        moves = []
        king_moves = [8, -8, 1, -1, 9, -9, 7, -7]
        own_pieces = self.occupied_white if piece.isupper() else self.occupied_black

        for move_offset in king_moves:
            to_square = from_square + move_offset
            if 0 <= to_square < 64:
                if abs((from_square % 8) - (to_square % 8)) <= 1:
                    if not (own_pieces & (1 << to_square)):
                        moves.append(Move(piece, from_square, to_square))
        return moves

    def get_piece_at_square(self, square):
        for piece, bitboard in self.bitboards.items():
            if bitboard & (1 << square):
                return piece
        return None
    
    def is_capture_move(self, move):
        target_piece = self.get_piece_at_square(move.to_square)
        if target_piece is not None:
            return target_piece.isupper() != move.piece.isupper()
        return False

    def generate_capture_moves(self):
        capture_moves = []
        all_moves = self.generate_legal_moves()
        for move in all_moves:
            if self.is_capture_move(move):
                capture_moves.append(move)
        return capture_moves

    def get_piece_value(self, piece):
            piece_values = {
                'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
                'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000
            }
            return piece_values.get(piece, 0)


    def evaluate(self):
        return evaluate(self)

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
    rank = square // 8 + 1
    file = square % 8
    return f"{files[file]}{rank}"
